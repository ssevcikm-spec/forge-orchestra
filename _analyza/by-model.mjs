// Split cost by MODEL and by reasoningEffort, using request/header records.
import { readFileSync, readdirSync, realpathSync } from 'node:fs'
import { join } from 'node:path'
import { zstdDecompressSync } from 'node:zlib'

const MAGIC = Buffer.from([0x28, 0xb5, 0x2f, 0xfd])
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

// DeepSeek Flash vs V4-Pro, off-peak, USD/1M
const PRICES = {
  flash: { hit: 0.003, miss: 0.15, out: 0.60 },
  pro: { hit: 0.022, miss: 0.66, out: 1.98 },
}
function kind(m) {
  if (!m) return 'unknown'
  if (/pro/i.test(m)) return 'pro'
  if (/flash/i.test(m)) return 'flash'
  return 'other:' + m
}

const seen = new Set()
const home = process.env.DSH_HOME ?? ''
const files = [...findLogs(join(home, 'sessions'), seen)]

const byModel = new Map()     // modelKind -> {req, hit, miss, out, cost, sessions:Set}
const byEffort = new Map()
const perModelRequest = []    // {model, effort}
let mismatch = 0

for (const f of files) {
  let txt; try { txt = dec(readFileSync(f)) } catch { continue }
  let curModel = null, curEffort = null
  // request/header gives the config actually sent; assistant/message gives usage.
  // We carry the last-seen header forward.
  const sname = f.replace(/^.*sessions\\/, '').replace(/\\session.*$/, '')
  for (const line of txt.split('\n')) {
    if (!line.trim()) continue
    let o; try { o = JSON.parse(line) } catch { continue }
    if (o.type === 'request/header') {
      const c = o.data?.header?.config
      if (c) {
        curModel = c.model ?? curModel
        curEffort = c.reasoningEffort ?? curEffort
        perModelRequest.push({ model: curModel, effort: curEffort, session: sname })
      }
      continue
    }
    if (o.type !== 'assistant/message') continue
    const u = o.data?.usage
    if (!u) continue
    const k = kind(curModel)
    const b = byModel.get(k) ?? { req: 0, hit: 0, miss: 0, out: 0, cost: 0, sessions: new Set() }
    b.req++; b.hit += u.cacheReadTokens ?? 0; b.miss += u.inputTokens ?? 0; b.out += u.outputTokens ?? 0
    b.sessions.add(sname)
    const p = PRICES[k] ?? PRICES.flash
    b.cost += ((u.cacheReadTokens ?? 0) * p.hit + (u.inputTokens ?? 0) * p.miss + (u.outputTokens ?? 0) * p.out) / 1e6
    byModel.set(k, b)

    const e = curEffort ?? 'unknown'
    const be = byEffort.get(e) ?? { req: 0, out: 0, reason: 0, hit: 0, miss: 0, cost: 0 }
    be.req++; be.out += u.outputTokens ?? 0; be.reason += u.reasoningTokens ?? 0
    be.hit += u.cacheReadTokens ?? 0; be.miss += u.inputTokens ?? 0
    byEffort.set(e, be)
  }
}

const fmt = (n) => Math.round(n).toLocaleString('en-US')
const usd = (n) => '$' + n.toFixed(3)

console.log('='.repeat(78))
console.log('COST SPLIT BY MODEL  (off-peak prices; Flash vs V4-Pro)')
console.log('='.repeat(78))
let grand = 0
for (const [k, b] of [...byModel.entries()].sort((a, c) => c[1].cost - a[1].cost)) {
  grand += b.cost
  console.log(`  ${k.padEnd(10)} req ${String(b.req).padStart(6)}  sessions ${String(b.sessions.size).padStart(3)}  hit ${fmt(b.hit).padStart(14)}  miss ${fmt(b.miss).padStart(11)}  out ${fmt(b.out).padStart(10)}  ${usd(b.cost)}`)
}
console.log(`  ${'TOTAL'.padEnd(10)} ${' '.repeat(20)} ${' '.repeat(14)} ${' '.repeat(11)} ${' '.repeat(10)}  ${usd(grand)}`)
console.log()
console.log('COST SPLIT BY reasoningEffort (from request headers)')
for (const [e, b] of [...byEffort.entries()].sort((a, c) => c[1].cost - a[1].cost)) {
  console.log(`  effort=${e.padEnd(9)} req ${String(b.req).padStart(6)}  out ${fmt(b.out).padStart(10)}  reasoning ${fmt(b.reason).padStart(10)} (${(100 * b.reason / Math.max(1, b.out)).toFixed(0)}% of out)  ${usd(b.cost)}`)
}
console.log()
console.log('MODEL USED PER SESSION START (first header seen per session)')
const firstBySession = new Map()
for (const r of perModelRequest) if (!firstBySession.has(r.session)) firstBySession.set(r.session, r)
const tally = new Map()
for (const r of firstBySession.values()) {
  const k = `${r.model} / effort=${r.effort}`
  tally.set(k, (tally.get(k) ?? 0) + 1)
}
for (const [k, n] of [...tally.entries()].sort((a, b) => b[1] - a[1])) console.log(`  ${String(n).padStart(4)} x  ${k}`)
console.log(`\n(header records: ${perModelRequest.length}, sessions: ${firstBySession.size}, mismatches: ${mismatch})`)
