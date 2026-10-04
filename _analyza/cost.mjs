/**
 * DSH full-cost analysis: input (miss/hit) + OUTPUT + reasoning, plus time-of-day
 * (peak vs off-peak) split. Prices are DeepSeek Flash, USD per 1M tokens.
 *
 *   cache-hit input : 0.003 off-peak / 0.006 peak
 *   cache-miss input: 0.150 off-peak / 0.300 peak
 *   output          : 0.600 off-peak / 1.200 peak
 *
 * Peak = 01:00-04:00 and 06:00-10:00 UTC, Mon-Fri, excl. Chinese public holidays.
 * We do not model CN holidays (conservative: we may over-count peak).
 */
import { readFileSync, readdirSync, realpathSync } from 'node:fs'
import { join } from 'node:path'
import { zstdDecompressSync } from 'node:zlib'

const MAGIC = Buffer.from([0x28, 0xb5, 0x2f, 0xfd])
const PRICE = {
  off: { hit: 0.003, miss: 0.15, out: 0.6 },
  peak: { hit: 0.006, miss: 0.3, out: 1.2 },
}

function decompressFrames(buf) {
  const starts = []
  let i = buf.indexOf(MAGIC)
  while (i !== -1) { starts.push(i); i = buf.indexOf(MAGIC, i + 4) }
  starts.push(buf.length)
  let out = ''
  for (let k = 0; k < starts.length - 1; k++) {
    try { out += zstdDecompressSync(buf.subarray(starts[k], starts[k + 1])).toString('utf8') } catch {}
  }
  return out
}

function* findLogs(dir, seen = new Set(), depth = 0) {
  if (depth > 4) return
  let real
  try { real = realpathSync(dir) } catch { return }
  if (seen.has(real)) return
  seen.add(real)
  let entries
  try { entries = readdirSync(dir, { withFileTypes: true }) } catch { return }
  for (const e of entries) {
    const p = join(dir, e.name)
    if (e.isDirectory()) yield* findLogs(p, seen, depth + 1)
    else if (/^session(\.v\d+)?\.jsonl\.zstd$/.test(e.name)) yield p
  }
}

function tsOf(o) {
  const c = [o.ts, o.time, o.timestamp, o.at, o.createdAt,
    o.data?.ts, o.data?.time, o.data?.timestamp, o.data?.at, o.data?.createdAt]
  for (const v of c) {
    if (typeof v === 'number' && v > 1e11) return v
    if (typeof v === 'string') { const t = Date.parse(v); if (!Number.isNaN(t)) return t }
  }
  return null
}

function isPeak(ms) {
  const d = new Date(ms)
  const dow = d.getUTCDay()            // 0 = Sunday
  if (dow === 0 || dow === 6) return false
  const h = d.getUTCHours() + d.getUTCMinutes() / 60
  return (h >= 1 && h < 4) || (h >= 6 && h < 10)
}

const home = process.env.DSH_HOME ?? join(process.env.USERPROFILE ?? '', '.dsh')
const roots = [join(home, 'sessions')]

const totals = {
  req: 0, miss: 0, hit: 0, out: 0, reasoning: 0,
  peak: { req: 0, miss: 0, hit: 0, out: 0 },
  off: { req: 0, miss: 0, hit: 0, out: 0 },
  noTs: { req: 0, miss: 0, hit: 0, out: 0 },
}
const sessions = new Map()
const hourHist = new Array(24).fill(0).map(() => ({ req: 0, miss: 0, hit: 0, out: 0 }))
const dowHist = new Array(7).fill(0).map(() => ({ req: 0, cost: 0, miss: 0, hit: 0, out: 0 }))
let compactions = 0
let prunes = 0
const busts = []
const toolCost = new Map()   // tool name -> out tokens produced in that step (approx via tool/call names)

function cost(p, b) { return (b.hit * p.hit + b.miss * p.miss + b.out * p.out) / 1e6 }

// ONE shared seen-set across roots: C:\Users\Ssevc\.dsh is a junction to E:\DSH\data,
// so scanning both roots naively counts every session twice.
const seenDirs = new Set()
for (const root of roots) {
  for (const file of findLogs(root, seenDirs)) {
    let text
    try { text = decompressFrames(readFileSync(file)) } catch { continue }
    if (!text) continue
    const sess = { file, req: 0, miss: 0, hit: 0, out: 0, reasoning: 0, peak: 0, off: 0, compactions: 0, peakCtx: 0 }
    for (const line of text.split('\n')) {
      if (!line.trim()) continue
      let o
      try { o = JSON.parse(line) } catch { continue }
      if (o.type === 'compaction/summary') { compactions++; sess.compactions++; continue }
      if (o.type === 'compaction/prune') { prunes++; continue }
      if (o.type !== 'assistant/message') continue
      const u = o.data?.usage
      if (!u) continue
      const b = {
        miss: u.inputTokens ?? 0,
        hit: u.cacheReadTokens ?? 0,
        out: u.outputTokens ?? 0,
      }
      const reason = u.reasoningTokens ?? 0
      const ctx = b.miss + b.hit
      if (ctx > sess.peakCtx) sess.peakCtx = ctx

      totals.req++; totals.miss += b.miss; totals.hit += b.hit; totals.out += b.out; totals.reasoning += reason
      sess.req++; sess.miss += b.miss; sess.hit += b.hit; sess.out += b.out; sess.reasoning += reason

      const t = tsOf(o)
      const bucket = t === null ? totals.noTs : (isPeak(t) ? totals.peak : totals.off)
      bucket.req++; bucket.miss += b.miss; bucket.hit += b.hit; bucket.out += b.out
      if (t !== null) {
        if (isPeak(t)) sess.peak++; else sess.off++
        const d = new Date(t)
        const h = hourHist[d.getUTCHours()]; h.req++; h.miss += b.miss; h.hit += b.hit; h.out += b.out
        const w = dowHist[d.getUTCDay()]; w.req++; w.miss += b.miss; w.hit += b.hit; w.out += b.out
      }
      if (b.miss > 100000) busts.push({ seq: o.seq, miss: b.miss, ctx, sess: file, t })
    }
    if (sess.req) sessions.set(file, sess)
  }
}

const hitRatio = totals.hit / (totals.hit + totals.miss)
const actualCost = cost(PRICE.off, totals.off) + cost(PRICE.peak, totals.peak) + cost(PRICE.peak, totals.noTs)
const allOffCost = cost(PRICE.off, totals)
const allMissCostOff = (totals.hit + totals.miss) * PRICE.off.miss / 1e6 + totals.out * PRICE.off.out / 1e6
const inputOnlyOff = cost(PRICE.off, totals)
const inputCostOff = (totals.hit * PRICE.off.hit + totals.miss * PRICE.off.miss) / 1e6
const outputCostOff = totals.out * PRICE.off.out / 1e6

const fmt = (n) => n.toLocaleString('en-US')
const usd = (n) => '$' + n.toFixed(3)

console.log('='.repeat(72))
console.log('DSH FULL COST ANALYSIS  (DeepSeek Flash, all sessions on disk)')
console.log('='.repeat(72))
console.log(`sessions: ${sessions.size}   requests: ${fmt(totals.req)}`)
console.log()
console.log('TOKENS')
console.log(`  cache MISS (full price in) : ${fmt(totals.miss)}`)
console.log(`  cache HIT  (cheap in)      : ${fmt(totals.hit)}`)
console.log(`  OUTPUT                     : ${fmt(totals.out)}`)
console.log(`    of which reasoning       : ${fmt(totals.reasoning)}  (${(100 * totals.reasoning / Math.max(1, totals.out)).toFixed(1)} % of output)`)
console.log(`  cache hit ratio            : ${(100 * hitRatio).toFixed(2)} %`)
console.log()
console.log('COST (USD)')
console.log(`  input, off-peak prices     : ${usd(inputCostOff)}`)
console.log(`  output, off-peak prices    : ${usd(outputCostOff)}`)
console.log(`  TOTAL at off-peak prices   : ${usd(allOffCost)}`)
console.log(`  TOTAL at peak prices       : ${usd(cost(PRICE.peak, totals))}`)
console.log(`  TOTAL actual (time-aware)  : ${usd(actualCost)}`)
console.log(`  counterfactual all-miss    : ${usd(allMissCostOff)}   (no cache at all, off-peak)`)
console.log()
console.log('SHARE OF COST (off-peak prices)')
const hitCostOff = totals.hit * PRICE.off.hit / 1e6
const missCostOff = totals.miss * PRICE.off.miss / 1e6
console.log(`  cache-hit input : ${usd(hitCostOff)}  = ${(100 * hitCostOff / allOffCost).toFixed(1)} %`)
console.log(`  cache-miss input: ${usd(missCostOff)}  = ${(100 * missCostOff / allOffCost).toFixed(1)} %`)
console.log(`  OUTPUT          : ${usd(outputCostOff)}  = ${(100 * outputCostOff / allOffCost).toFixed(1)} %`)
void inputOnlyOff
console.log()
console.log(`OUTPUT TOKENS PER REQUEST: ${(totals.out / Math.max(1, totals.req)).toFixed(0)}`)
console.log()
console.log('PEAK vs OFF-PEAK (by request timestamp, UTC)')
console.log(`  off-peak req ${fmt(totals.off.req)}  cost ${usd(cost(PRICE.off, totals.off))}`)
console.log(`  PEAK     req ${fmt(totals.peak.req)}  cost ${usd(cost(PRICE.peak, totals.peak))}   <- would be ${usd(cost(PRICE.off, totals.peak))} off-peak`)
console.log(`  no-timestamp req ${fmt(totals.noTs.req)} (costed at peak, conservative)`)
console.log(`  SAVING if all peak work moved off-peak: ${usd(cost(PRICE.peak, totals.peak) - cost(PRICE.off, totals.peak))}`)
console.log()
console.log('BY UTC HOUR (cost at that hour\'s applicable rate)')
for (let h = 0; h < 24; h++) {
  const b = hourHist[h]
  if (!b.req) continue
  const p = (h >= 1 && h < 4) || (h >= 6 && h < 10) ? PRICE.peak : PRICE.off
  console.log(`  ${String(h).padStart(2, '0')}:00 UTC  req ${String(b.req).padStart(5)}  miss ${String(fmt(b.miss)).padStart(12)}  out ${String(fmt(b.out)).padStart(9)}  ${usd(cost(p, b))}`)
}
console.log()
console.log('BY UTC WEEKDAY')
const names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
for (let d = 0; d < 7; d++) {
  const b = dowHist[d]
  if (!b.req) continue
  console.log(`  ${names[d]}  req ${String(b.req).padStart(5)}  miss ${String(fmt(b.miss)).padStart(12)}  hit ${String(fmt(b.hit)).padStart(13)}  out ${String(fmt(b.out)).padStart(9)}`)
}
console.log()
console.log(`COMPACTIONS: ${compactions}   PRUNES: ${prunes}      CACHE-BUST (miss>100k): ${busts.length}`)
const bustTotal = busts.reduce((a, b) => a + b.miss, 0)
console.log(`  tokens re-billed at full price by those busts: ${fmt(bustTotal)}  = ${usd(bustTotal * PRICE.off.miss / 1e6)} off-peak / ${usd(bustTotal * PRICE.peak.miss / 1e6)} peak`)
console.log(`  if those had been cache hits instead        : ${usd(bustTotal * PRICE.off.hit / 1e6)} off-peak`)
console.log()
console.log('TOP 12 SESSIONS BY COST (off-peak prices)')
const ranked = [...sessions.values()]
  .map((s) => ({ ...s, c: cost(PRICE.off, s) }))
  .sort((a, b) => b.c - a.c)
  .slice(0, 12)
for (const s of ranked) {
  const name = s.file.replace(/^.*sessions\\/, '').replace(/\\session.*$/, '')
  console.log(`  ${usd(s.c).padStart(8)}  req ${String(s.req).padStart(5)}  ctxpeak ${String(fmt(s.peakCtx)).padStart(9)}  out ${String(fmt(s.out)).padStart(8)}  comp ${s.compactions}  ${name}`)
}
