/**
 * DEFINITIVE DSH cost & cache analysis.
 * Correct per-model classification (no /pro/i trap for gemini-3.1-pro-preview),
 * per-model prices, peak/off-peak, reasoning amplification, cache-bust causes.
 *
 * Off-peak prices, USD per 1M tokens:
 *   deepseek-flash   hit 0.003  miss 0.15  out 0.60
 *   deepseek-v4-pro  hit 0.022  miss 0.66  out 1.98
 *   gemini-*         not billed by DeepSeek -> excluded from DeepSeek spend
 *
 * Peak = 01:00-04:00 and 06:00-10:00 UTC Mon-Fri (CN holidays not modelled).
 */
import { readFileSync, readdirSync, realpathSync } from 'node:fs'
import { join } from 'node:path'
import { zstdDecompressSync } from 'node:zlib'

const MAGIC = Buffer.from([0x28, 0xb5, 0x2f, 0xfd])
const PRICES = {
  flash: { hit: 0.003, miss: 0.15, out: 0.60 },
  pro: { hit: 0.022, miss: 0.66, out: 1.98 },
}
const PEAK_MULT = 2

function classify(m) {
  if (!m) return 'unknown'
  const s = String(m).toLowerCase()
  if (s.includes('gemini')) return 'gemini'
  if (s.includes('deepseek') || s === 'deepseek') {
    if (s.includes('pro')) return 'pro'
    return 'flash'
  }
  if (s === 'assistant' || s === 'null') return 'unknown'
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
  const d = new Date(ms)
  const dow = d.getUTCDay()
  if (dow === 0 || dow === 6) return false
  const h = d.getUTCHours() + d.getUTCMinutes() / 60
  return (h >= 1 && h < 4) || (h >= 6 && h < 10)
}
function tsOf(o) {
  for (const v of [o.time, o.ts, o.timestamp, o.data?.time, o.data?.ts, o.data?.timestamp]) {
    if (typeof v === 'number' && v > 1e11) return v
    if (typeof v === 'string') { const t = Date.parse(v); if (!Number.isNaN(t)) return t }
  }
  return null
}

const seen = new Set()
const home = process.env.DSH_HOME ?? ''
const files = [...findLogs(join(home, 'sessions'), seen)]

const M = {
  flash: { req: 0, hit: 0, miss: 0, out: 0, reason: 0, cost: 0 },
  pro: { req: 0, hit: 0, miss: 0, out: 0, reason: 0, cost: 0 },
  gemini: { req: 0, hit: 0, miss: 0, out: 0, reason: 0, cost: 0 },
  other: { req: 0, hit: 0, miss: 0, out: 0, reason: 0, cost: 0 },
  unknown: { req: 0, hit: 0, miss: 0, out: 0, reason: 0, cost: 0 },
}
const T = { off: { hit: 0, miss: 0, out: 0, cost: 0, req: 0 }, peak: { hit: 0, miss: 0, out: 0, cost: 0, req: 0 } }
let switches = 0
let reasonReread = 0, reasonRereadCost = 0
const busts = []
const sessionAgg = []
let totalCostAll = 0

for (const f of files) {
  let txt; try { txt = dec(readFileSync(f)) } catch { continue }
  const sname = f.replace(/^.*sessions\\/, '').replace(/\\session.*$/, '')
  let cur = null
  let carriedReason = 0
  let sCost = 0, sReq = 0
  // deque of recent events to attribute a bust
  let lastSwitchAt = -1e18, lastCompactionAt = -1e18
  let sawCompaction = 0
  for (const line of txt.split('\n')) {
    if (!line.trim()) continue
    let o; try { o = JSON.parse(line) } catch { continue }
    const t = tsOf(o)

    if (o.type === 'request/header') {
      const m = o.data?.header?.config?.model
      if (m && m !== cur) { if (cur !== null) switches++; cur = m; lastSwitchAt = t ?? 0 }
      continue
    }
    if (o.type === 'compaction/summary') { carriedReason = 0; sawCompaction++; lastCompactionAt = t ?? 0; continue }
    if (o.type === 'compaction/prune') { continue }
    if (o.type !== 'assistant/message') continue
    const u = o.data?.usage
    if (!u) continue

    const k = classify(cur)
    const price = PRICES[k] ?? null
    const hit = u.cacheReadTokens ?? 0, miss = u.inputTokens ?? 0, out = u.outputTokens ?? 0, reason = u.reasoningTokens ?? 0
    const peak = t !== null && isPeak(t)
    const mult = peak ? PEAK_MULT : 1

    const b = { req: 1, hit, miss, out, reason, cost: 0 }
    if (price) b.cost = ((hit * price.hit + miss * price.miss + out * price.out) / 1e6) * mult
    const tgt = M[k]
    tgt.req += b.req; tgt.hit += hit; tgt.miss += miss; tgt.out += out; tgt.reason += reason; tgt.cost += b.cost
    if (price) {
      const bucket = peak ? T.peak : T.off
      bucket.req++; bucket.hit += hit; bucket.miss += miss; bucket.out += out; bucket.cost += b.cost
    }
    sCost += b.cost; sReq++

    // reasoning re-read amplification (flash only, to stay interpretable)
    if (k === 'flash') {
      const rr = Math.min(carriedReason, hit + miss)
      reasonReread += rr
      reasonRereadCost += rr * PRICES.flash.hit / 1e6 * mult
    }
    carriedReason += reason

    if (miss > 100000) {
      const cause = []
      if (t !== null && t - lastSwitchAt < 5000) cause.push('model-switch')
      if (t !== null && t - lastCompactionAt < 5000) cause.push('compaction')
      busts.push({ sname, miss, cause: cause.join('+') || 'other', model: cur })
    }
  }
  if (sReq) { sessionAgg.push({ sname, sCost, sReq, sawCompaction }); totalCostAll += sCost }
}

const fmt = (n) => Math.round(n).toLocaleString('en-US')
const usd = (n) => '$' + n.toFixed(3)

console.log('='.repeat(78))
console.log('DEFINITIVE DSH COST ANALYSIS — DeepSeek spend, off-peak base prices')
console.log('='.repeat(78))
const reqAll = Object.values(M).reduce((a, b) => a + b.req, 0)
console.log(`sessions ${sessionAgg.length}   requests ${fmt(reqAll)}   model switches in-session ${switches}`)
console.log()
console.log('BY MODEL')
for (const k of ['flash', 'pro', 'gemini', 'unknown', 'other']) {
  const b = M[k]
  if (!b.req) continue
  const pct = 100 * b.cost / Math.max(1e-9, M.flash.cost + M.pro.cost)
  console.log(`  ${k.padEnd(8)} req ${String(fmt(b.req)).padStart(6)} (${(100 * b.req / reqAll).toFixed(0).padStart(2)}%)  out ${fmt(b.out).padStart(10)}  reason ${(100 * b.reason / Math.max(1, b.out)).toFixed(0).padStart(3)}% of out  ${b.cost ? usd(b.cost).padStart(9) : '   n/a   '}  ${b.cost ? pct.toFixed(0) + '% of DeepSeek spend' : '(not billed by DeepSeek)'}`)
}
const dsSpend = M.flash.cost + M.pro.cost
console.log(`\n  DEEPSEEK SPEND (off-peak base, peak surcharge included): ${usd(dsSpend)}`)
console.log(`  if the SAME tokens had all run on Flash                : ${usd((M.flash.hit + M.pro.hit) * PRICES.flash.hit / 1e6 + (M.flash.miss + M.pro.miss) * PRICES.flash.miss / 1e6 + (M.flash.out + M.pro.out) * PRICES.flash.out / 1e6)}`)
console.log(`  -> model choice alone costs                             : ${usd(dsSpend - ((M.flash.hit + M.pro.hit) * PRICES.flash.hit / 1e6 + (M.flash.miss + M.pro.miss) * PRICES.flash.miss / 1e6 + (M.flash.out + M.pro.out) * PRICES.flash.out / 1e6))}`)
console.log()
console.log('PEAK / OFF-PEAK (DeepSeek only)')
console.log(`  off-peak req ${fmt(T.off.req).padStart(6)}  ${usd(T.off.cost)}`)
console.log(`  PEAK     req ${fmt(T.peak.req).padStart(6)}  ${usd(T.peak.cost)}  (half of that is the surcharge: ${usd(T.peak.cost / 2)})`)
console.log()
console.log('COST STRUCTURE (DeepSeek only, base prices, peak surcharge removed)')
const baseCost = T.off.cost + T.peak.cost / 2
const comp = {
  'cache-HIT input': (T.off.hit + T.peak.hit) * 0, // placeholder
}
function mixCost(b) { return null }
const hitTok = T.off.hit + T.peak.hit, missTok = T.off.miss + T.peak.miss, outTok = T.off.out + T.peak.out
const costs = {}
for (const k of ['flash', 'pro']) {
  const p = PRICES[k]
  costs[k] = { hit: M[k].hit * p.hit / 1e6, miss: M[k].miss * p.miss / 1e6, out: M[k].out * p.out / 1e6 }
}
const sumHit = costs.flash.hit + costs.pro.hit
const sumMiss = costs.flash.miss + costs.pro.miss
const sumOut = costs.flash.out + costs.pro.out
const base = sumHit + sumMiss + sumOut
console.log(`  cache-HIT input  ${usd(sumHit).padStart(9)}  ${(100 * sumHit / base).toFixed(1).padStart(5)} %`)
console.log(`  cache-MISS input ${usd(sumMiss).padStart(9)}  ${(100 * sumMiss / base).toFixed(1).padStart(5)} %`)
console.log(`  OUTPUT           ${usd(sumOut).padStart(9)}  ${(100 * sumOut / base).toFixed(1).padStart(5)} %`)
console.log(`  total base       ${usd(base).padStart(9)}`)
void hitTok; void missTok; void outTok; void baseCost; void comp; void mixCost
console.log()
console.log('CACHE-BUST EVENTS (miss > 100k)')
const byCause = new Map()
for (const b of busts) byCause.set(b.cause, (byCause.get(b.cause) ?? 0) + 1)
for (const [c, n] of [...byCause.entries()].sort((a, b) => b[1] - a[1])) console.log(`  ${String(n).padStart(3)} x  cause: ${c}`)
const bustTok = busts.reduce((a, b) => a + b.miss, 0)
console.log(`  ${busts.length} events, ${fmt(bustTok)} tokens billed at FULL price`)
console.log(`  cost at flash miss price   : ${usd(bustTok * PRICES.flash.miss / 1e6)}`)
console.log(`  same tokens as cache hits  : ${usd(bustTok * PRICES.flash.hit / 1e6)}`)
console.log(`  -> avoidable               : ${usd(bustTok * (PRICES.flash.miss - PRICES.flash.hit) / 1e6)}`)
console.log()
console.log('THINKING (reasoning) — flash sessions only')
console.log(`  reasoning output tokens          : ${fmt(M.flash.reason)}  = ${usd(M.flash.reason * PRICES.flash.out / 1e6)} as output`)
console.log(`  reasoning re-read from context   : ${fmt(reasonReread)} token-reads = ${usd(reasonRereadCost)}`)
console.log(`  amplifications per reasoning tok : ${(reasonReread / Math.max(1, M.flash.reason)).toFixed(1)}x`)
console.log(`  THINKING TOTAL                   : ${usd(M.flash.reason * PRICES.flash.out / 1e6 + reasonRereadCost)}  = ${(100 * (M.flash.reason * PRICES.flash.out / 1e6 + reasonRereadCost) / M.flash.cost).toFixed(1)} % of flash spend`)
console.log()
console.log('TOP 10 SESSIONS BY DeepSeek COST')
sessionAgg.sort((a, b) => b.sCost - a.sCost)
for (const s of sessionAgg.slice(0, 10)) console.log(`  ${usd(s.sCost).padStart(9)}  req ${String(s.sReq).padStart(5)}  comp ${s.sawCompaction}  ${s.sname}`)

// ---------------- TARGET STATE ----------------
console.log()
console.log('='.repeat(78))
console.log('TARGET STATE — cumulative effect of the levers, DeepSeek spend')
console.log('='.repeat(78))
const H = M.flash.hit + M.pro.hit
const S = M.flash.miss + M.pro.miss
const O = M.flash.out + M.pro.out
const RE = M.flash.reason + M.pro.reason
const bustTokAll = busts.reduce((a, b) => a + b.miss, 0)
const bustShare = bustTokAll / Math.max(1, S)   // share of miss tokens that are bursts

const p = PRICES.flash
const start = dsSpend
// L1: move everything to flash
const l1 = (H * p.hit + S * p.miss + O * p.out) / 1e6
// L2: + all off-peak (remove peak surcharge). Peak cost share measured above.
const peakSurcharge = T.peak.cost / 2   // half of peak cost is the surcharge, at mixed prices
const peakFrac = T.peak.cost / Math.max(1e-9, T.peak.cost + T.off.cost)
const l2 = l1 * (1 - peakFrac * 0.5)
// L3: + no cache-busts (bust miss tokens become hits)
const l3 = l2 - bustTokAll * (p.miss - p.hit) / 1e6 * (1 - peakFrac * 0.5)
// L4: + halve reasoning (half as output, and half as much polluting the context)
const reasonOutCost = RE * p.out / 1e6
const reasonCtxShare = H > 0 ? (reasonReread / (M.flash.hit + M.flash.miss)) : 0
const l4 = l3 - (reasonOutCost * 0.5) - (l3 * p.hit / (p.hit + p.miss + p.out) * reasonCtxShare * 0.5)

const row = (label, v, prev) => console.log(`  ${label.padEnd(46)} ${usd(v).padStart(9)}   ${prev ? 'saves ' + usd(prev - v) : ''}`)
row('BASELINE — what was actually spent', start, null)
row('L1  everything on deepseek-flash', l1, start)
row('L2  + all work off-peak', l2, l1)
row('L3  + no cache-busts', l3, l2)
row('L4  + reasoning effort lowered', l4, l3)
console.log()
console.log(`  tokens: hit ${fmt(H)}  miss ${fmt(S)}  out ${fmt(O)}  reasoning ${fmt(RE)}`)
console.log(`  peak surcharge actually paid: ${usd(peakSurcharge)}`)
console.log(`  TOTAL ACHIEVABLE REDUCTION: ${usd(start - l4)}  = ${(100 * (start - l4) / start).toFixed(0)} %`)
console.log()
console.log('  per-lever share of the reduction:')
const ls = [['model choice (pro -> flash)', start - l1], ['off-peak scheduling', l1 - l2], ['no cache-busts', l2 - l3], ['lower reasoning effort', l3 - l4]]
for (const [n, v] of ls) console.log(`    ${n.padEnd(32)} ${usd(v).padStart(8)}  ${(100 * v / (start - l4)).toFixed(0)} %`)
console.log()
console.log('  NOTE: off-peak share here is conservative — it assumes peak work keeps')
console.log('  the same token mix. Lever L4 is the least certain (see report caveats).')
