/**
 * Classify every session by TOPIC (from session/title) and aggregate cost.
 * Answers: what does GAME/ASSET work cost vs APP/CODE work vs research/meta?
 */
import { readFileSync, readdirSync, realpathSync } from 'node:fs'
import { join } from 'node:path'
import { zstdDecompressSync } from 'node:zlib'

const MAGIC = Buffer.from([0x28, 0xb5, 0x2f, 0xfd])
const PRICES = { flash: { hit: 0.003, miss: 0.15, out: 0.60 }, pro: { hit: 0.022, miss: 0.66, out: 1.98 } }
function classifyModel(m) {
  if (!m) return 'unknown'
  const s = String(m).toLowerCase()
  if (s.includes('gemini')) return 'gemini'
  if (s.includes('pro')) return 'pro'
  return 'flash'
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

// TOPIC rules — game/asset work vs app/code vs meta
const RULES = [
  ['GAME / ASSET', /game|hra|hru|hra|sprite|asset|blender|godot|uo-shadows|idle|tile|textur|postav|character|animac|map|level|orchestra|forge|comfyui|sdxl|imagegen|obraz/i],
  ['APP / CODE', /refactor|bug|test|api|server|typescript|python|component|deploy|build|fix|implement|migrat|script|tool|skill|plugin|patch|config|dsl|worker|ci\b/i],
  ['RESEARCH / META', /analýz|analy|research|report|rešerš|audit|measure|usage|token|cena|cost|dokument|readme|handoff|kontrol|review|ověř|verify|srovn|návrh/i],
]
function topicOf(title) {
  if (!title) return 'NO TITLE'
  for (const [name, re] of RULES) if (re.test(title)) return name
  return 'OTHER'
}

const seen = new Set()
const home = process.env.DSH_HOME ?? ''
const files = [...findLogs(join(home, 'sessions'), seen)]

const rows = []
for (const f of files) {
  let txt; try { txt = dec(readFileSync(f)) } catch { continue }
  const rel = f.replace(/^.*sessions\\/, '')
  const projSeg = rel.split('\\')[0] ?? '?'
  let cur = null, title = null
  let req = 0, hit = 0, miss = 0, out = 0, reason = 0, cost = 0, peakReq = 0, peakCtx = 0, comp = 0, tools = 0, reasonOut = 0
  const toolNames = new Map()
  for (const line of txt.split('\n')) {
    if (!line.trim()) continue
    let o; try { o = JSON.parse(line) } catch { continue }
    if (o.type === 'session/title') { title = o.data?.title ?? o.title ?? title; continue }
    if (o.type === 'request/header') { const m = o.data?.header?.config?.model; if (m) cur = m; continue }
    if (o.type === 'compaction/summary') { comp++; continue }
    if (o.type === 'tool/call') { tools++; const n = o.data?.name ?? '?'; toolNames.set(n, (toolNames.get(n) ?? 0) + 1); continue }
    if (o.type !== 'assistant/message') continue
    const u = o.data?.usage; if (!u) continue
    const k = classifyModel(cur), p = PRICES[k]
    const t = tsOf(o), mult = t !== null && isPeak(t) ? 2 : 1
    const h = u.cacheReadTokens ?? 0, m = u.inputTokens ?? 0, ou = u.outputTokens ?? 0, r = u.reasoningTokens ?? 0
    req++; hit += h; miss += m; out += ou; reason += r; reasonOut += r
    if (t !== null && isPeak(t)) peakReq++
    if (h + m > peakCtx) peakCtx = h + m
    if (p) cost += ((h * p.hit + m * p.miss + ou * p.out) / 1e6) * mult
  }
  if (!req) continue
  rows.push({ projSeg, title, topic: topicOf(title), req, hit, miss, out, reason, reasonOut, cost, peakReq, peakCtx, comp, tools, toolNames })
}

const fmt = (n) => Math.round(n).toLocaleString('en-US')
const usd = (n) => '$' + n.toFixed(2)
const total = rows.reduce((a, b) => a + b.cost, 0)

console.log('='.repeat(104))
console.log('COST BY TOPIC  (classified from session titles)')
console.log('='.repeat(104))
const byTopic = new Map()
for (const r of rows) {
  const a = byTopic.get(r.topic) ?? { sess: 0, req: 0, cost: 0, hit: 0, miss: 0, out: 0, reason: 0, peakReq: 0, comp: 0, tools: 0 }
  a.sess++; a.req += r.req; a.cost += r.cost; a.hit += r.hit; a.miss += r.miss; a.out += r.out
  a.reason += r.reason; a.peakReq += r.peakReq; a.comp += r.comp; a.tools += r.tools
  byTopic.set(r.topic, a)
}
console.log(`${'topic'.padEnd(18)} ${'sess'.padStart(4)} ${'req'.padStart(6)} ${'cost'.padStart(9)} ${'%'.padStart(5)} ${'per-req'.padStart(9)} ${'ctx/req'.padStart(9)} ${'out'.padStart(10)} ${'reason%'.padStart(7)} ${'tools'.padStart(6)} ${'pk%'.padStart(5)}`)
for (const [t, a] of [...byTopic.entries()].sort((x, y) => y[1].cost - x[1].cost)) {
  console.log(`${t.padEnd(18)} ${String(a.sess).padStart(4)} ${String(a.req).padStart(6)} ${usd(a.cost).padStart(9)} ${(100 * a.cost / total).toFixed(1).padStart(5)} ${('$' + (a.cost / a.req).toFixed(4)).padStart(9)} ${fmt((a.hit + a.miss) / a.req).padStart(9)} ${fmt(a.out).padStart(10)} ${(100 * a.reason / Math.max(1, a.out)).toFixed(0).padStart(6)}% ${String(a.tools).padStart(6)} ${(100 * a.peakReq / a.req).toFixed(0).padStart(4)}%`)
}
console.log(`${'TOTAL'.padEnd(18)} ${String(rows.length).padStart(4)} ${String(rows.reduce((a, b) => a + b.req, 0)).padStart(6)} ${usd(total).padStart(9)}`)

console.log()
console.log('='.repeat(104))
console.log('GAME / ASSET SESSIONS — detail')
console.log('='.repeat(104))
for (const r of rows.filter((x) => x.topic === 'GAME / ASSET').sort((a, b) => b.cost - a.cost)) {
  console.log(`  ${usd(r.cost).padStart(8)}  req ${String(r.req).padStart(5)}  ctxPeak ${fmt(r.peakCtx).padStart(9)}  out ${fmt(r.out).padStart(9)}  reason ${(100 * r.reason / Math.max(1, r.out)).toFixed(0).padStart(3)}%  tools ${String(r.tools).padStart(5)}  | ${(r.title ?? '(no title)').slice(0, 62)}`)
}

console.log()
console.log('='.repeat(104))
console.log('DOES SESSION LENGTH / CONTEXT SATURATION DRIVE COST?')
console.log('='.repeat(104))
const buckets = [
  ['ctx peak < 200k', (s) => s.peakCtx < 200000],
  ['200k-500k', (s) => s.peakCtx >= 200000 && s.peakCtx < 500000],
  ['500k-700k', (s) => s.peakCtx >= 500000 && s.peakCtx < 700000],
  ['700k-800k (saturated)', (s) => s.peakCtx >= 700000],
]
console.log(`${'bucket'.padEnd(24)} ${'sess'.padStart(4)} ${'req'.padStart(6)} ${'total'.padStart(9)} ${'per-req'.padStart(10)} ${'ctx/req'.padStart(9)}`)
for (const [label, fn] of buckets) {
  const g = rows.filter(fn); if (!g.length) continue
  const c = g.reduce((a, b) => a + b.cost, 0), rr = g.reduce((a, b) => a + b.req, 0)
  const ctx = g.reduce((a, b) => a + b.hit + b.miss, 0) / Math.max(1, rr)
  console.log(`${label.padEnd(24)} ${String(g.length).padStart(4)} ${String(rr).padStart(6)} ${usd(c).padStart(9)} ${('$' + (c / rr).toFixed(4)).padStart(10)} ${fmt(ctx).padStart(9)}`)
}

console.log()
console.log('TOOL CALL FREQUENCY (all sessions) — what actually consumes turns')
const T = new Map()
for (const r of rows) for (const [n, c] of r.toolNames) T.set(n, (T.get(n) ?? 0) + c)
const toolTotal = [...T.values()].reduce((a, b) => a + b, 0)
for (const [n, c] of [...T.entries()].sort((a, b) => b[1] - a[1]).slice(0, 16)) console.log(`  ${String(c).padStart(6)}  ${(100 * c / toolTotal).toFixed(1).padStart(5)}%  ${n}`)
