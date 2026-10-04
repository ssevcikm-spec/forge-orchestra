/**
 * Cost by PROJECT (session working directory) and by session shape.
 * Answers: which workstream burns the money, and does session length drive cost?
 *
 * Off-peak base prices, USD per 1M tokens:
 *   deepseek-flash  hit 0.003  miss 0.15  out 0.60
 *   deepseek-v4-pro hit 0.022  miss 0.66  out 1.98
 * Peak (01-04, 06-10 UTC Mon-Fri) = 2x.
 */
import { readFileSync, readdirSync, realpathSync } from 'node:fs'
import { join } from 'node:path'
import { zstdDecompressSync } from 'node:zlib'

const MAGIC = Buffer.from([0x28, 0xb5, 0x2f, 0xfd])
const PRICES = { flash: { hit: 0.003, miss: 0.15, out: 0.60 }, pro: { hit: 0.022, miss: 0.66, out: 1.98 } }

function classify(m) {
  if (!m) return 'unknown'
  const s = String(m).toLowerCase()
  if (s.includes('gemini')) return 'gemini'
  if (s.includes('pro')) return 'pro'
  if (s.includes('flash') || s.includes('deepseek')) return 'flash'
  return 'other'
}
function dec(buf) {
  const s = []; let i = buf.indexOf(MAGIC)
  while (i !== -1) { s.push(i); i = buf.indexOf(MAGIC, i + 4) }
  s.push(buf.length); let o = ''
  for (let k = 0; k < s.length - 1; k++) { try { o += zstdDecompressSync(buf.subarray(s[k], s[k + 1])).toString('utf8') } catch {} }
  return o
}
function* findLogs(dir, seen, depth = 0) {
  if (depth > 4) return
  let real; try { real = realpathSync(dir) } catch { return }
  if (seen.has(real)) return
  seen.add(real)
  let es; try { es = readdirSync(dir, { withFileTypes: true }) } catch { return }
  for (const e of es) {
    const p = join(dir, e.name)
    if (e.isDirectory()) yield* findLogs(p, seen, depth + 1)
    else if (/^session(\.v\d+)?\.jsonl\.zstd$/.test(e.name)) yield p
  }
}
function isPeak(ms) {
  const d = new Date(ms), dow = d.getUTCDay()
  if (dow === 0 || dow === 6) return false
  const h = d.getUTCHours() + d.getUTCMinutes() / 60
  return (h >= 1 && h < 4) || (h >= 6 && h < 10)
}
function tsOf(o) {
  for (const v of [o.time, o.ts, o.data?.time, o.data?.ts]) {
    if (typeof v === 'number' && v > 1e11) return v
    if (typeof v === 'string') { const t = Date.parse(v); if (!Number.isNaN(t)) return t }
  }
  return null
}

const seen = new Set()
const home = process.env.DSH_HOME ?? ''
const files = [...findLogs(join(home, 'sessions'), seen)]

const projects = new Map()
const sessions = []

for (const f of files) {
  let txt; try { txt = dec(readFileSync(f)) } catch { continue }
  const rel = f.replace(/^.*sessions\\/, '')
  const proj = rel.replace(/\\[^\\]*$/, '') || rel
  let cur = null
  let req = 0, hit = 0, miss = 0, out = 0, reason = 0, cost = 0, peakReq = 0
  let peakCtx = 0, compactions = 0, toolCalls = 0, userMsgs = 0, reasonOut = 0
  const tools = new Map()

  for (const line of txt.split('\n')) {
    if (!line.trim()) continue
    let o; try { o = JSON.parse(line) } catch { continue }
    if (o.type === 'request/header') {
      const m = o.data?.header?.config?.model
      if (m) cur = m
      continue
    }
    if (o.type === 'compaction/summary') { compactions++; continue }
    if (o.type === 'tool/call') {
      toolCalls++
      const n = o.data?.name ?? o.data?.tool ?? '?'
      tools.set(n, (tools.get(n) ?? 0) + 1)
      continue
    }
    if (o.type === 'user/message') { userMsgs++; continue }
    if (o.type !== 'assistant/message') continue
    const u = o.data?.usage
    if (!u) continue
    const k = classify(cur)
    const p = PRICES[k]
    const t = tsOf(o)
    const mult = t !== null && isPeak(t) ? 2 : 1
    const h = u.cacheReadTokens ?? 0, m = u.inputTokens ?? 0, ou = u.outputTokens ?? 0, r = u.reasoningTokens ?? 0
    req++; hit += h; miss += m; out += ou; reason += r; reasonOut += r
    if (t !== null && isPeak(t)) peakReq++
    const ctx = h + m
    if (ctx > peakCtx) peakCtx = ctx
    if (p) cost += ((h * p.hit + m * p.miss + ou * p.out) / 1e6) * mult
  }
  if (!req) continue
  const agg = projects.get(proj) ?? { proj, sessions: 0, req: 0, hit: 0, miss: 0, out: 0, reason: 0, cost: 0, peakReq: 0, compactions: 0, toolCalls: 0, userMsgs: 0, peakCtx: 0 }
  for (const [kk, vv] of [['sessions', 1], ['req', req], ['hit', hit], ['miss', miss], ['out', out], ['reason', reason], ['cost', cost], ['peakReq', peakReq], ['compactions', compactions], ['toolCalls', toolCalls], ['userMsgs', userMsgs]]) agg[kk] += vv
  agg.peakCtx = Math.max(agg.peakCtx, peakCtx)
  projects.set(proj, agg)
  sessions.push({ proj, req, cost, peakCtx, compactions, toolCalls, userMsgs, out, reason, hit, miss })
}

const fmt = (n) => Math.round(n).toLocaleString('en-US')
const usd = (n) => '$' + n.toFixed(2)

const list = [...projects.values()].sort((a, b) => b.cost - a.cost)
const totalCost = list.reduce((a, b) => a + b.cost, 0)
console.log('='.repeat(100))
console.log('COST BY PROJECT (session workspace directory)')
console.log('='.repeat(100))
console.log(`${'project'.padEnd(46)} ${'sess'.padStart(4)} ${'req'.padStart(6)} ${'cost'.padStart(9)} ${'%'.padStart(5)} ${'out'.padStart(10)} ${'reason%'.padStart(7)} ${'ctxPeak'.padStart(9)} ${'comp'.padStart(4)} ${'tools'.padStart(6)}`)
for (const p of list) {
  const name = p.proj.replace(/^--|--$/g, '').slice(0, 45)
  console.log(`${name.padEnd(46)} ${String(p.sessions).padStart(4)} ${String(p.req).padStart(6)} ${usd(p.cost).padStart(9)} ${(100 * p.cost / totalCost).toFixed(1).padStart(5)} ${fmt(p.out).padStart(10)} ${(100 * p.reason / Math.max(1, p.out)).toFixed(0).padStart(6)}% ${fmt(p.peakCtx).padStart(9)} ${String(p.compactions).padStart(4)} ${String(p.toolCalls).padStart(6)}`)
}
console.log(`${'TOTAL'.padEnd(46)} ${String(list.reduce((a, b) => a + b.sessions, 0)).padStart(4)} ${String(list.reduce((a, b) => a + b.req, 0)).padStart(6)} ${usd(totalCost).padStart(9)}`)

console.log()
console.log('='.repeat(100))
console.log('DOES SESSION LENGTH DRIVE COST?  (cost per request vs session peak context)')
console.log('='.repeat(100))
const buckets = [
  ['ctx peak < 200k', (s) => s.peakCtx < 200000],
  ['200k - 500k', (s) => s.peakCtx >= 200000 && s.peakCtx < 500000],
  ['500k - 700k', (s) => s.peakCtx >= 500000 && s.peakCtx < 700000],
  ['700k - 800k (saturated)', (s) => s.peakCtx >= 700000],
]
console.log(`${'bucket'.padEnd(26)} ${'sess'.padStart(4)} ${'req'.padStart(6)} ${'total'.padStart(9)} ${'per-req'.padStart(9)} ${'ctx/req'.padStart(10)}`)
for (const [label, fn] of buckets) {
  const g = sessions.filter(fn)
  if (!g.length) continue
  const c = g.reduce((a, b) => a + b.cost, 0)
  const r = g.reduce((a, b) => a + b.req, 0)
  const ctx = g.reduce((a, b) => a + b.hit + b.miss, 0) / Math.max(1, r)
  console.log(`${label.padEnd(26)} ${String(g.length).padStart(4)} ${String(r).padStart(6)} ${usd(c).padStart(9)} ${('$' + (c / r).toFixed(4)).padStart(9)} ${fmt(ctx).padStart(10)}`)
}
console.log()
console.log('Tools used most (all sessions):')
const toolTotals = new Map()
for (const line of []) void line
for (const f of files) {
  let txt; try { txt = dec(readFileSync(f)) } catch { continue }
  for (const l of txt.split('\n')) {
    if (!l.includes('"tool/call"')) continue
    let o; try { o = JSON.parse(l) } catch { continue }
    if (o.type !== 'tool/call') continue
    const n = o.data?.name ?? o.data?.tool ?? '?'
    toolTotals.set(n, (toolTotals.get(n) ?? 0) + 1)
  }
}
for (const [n, c] of [...toolTotals.entries()].sort((a, b) => b[1] - a[1]).slice(0, 14)) console.log(`  ${String(c).padStart(6)}  ${n}`)
