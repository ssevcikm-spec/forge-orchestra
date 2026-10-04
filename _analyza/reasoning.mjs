/**
 * How much do REASONING tokens really cost?
 *
 * With `tools` present, DeepSeek requires reasoning_content to be replayed into
 * the context on every later request. So a reasoning token is paid for:
 *   (a) once as output            @ $0.60 / 1M
 *   (b) again on every later request in the same session, as part of the
 *       cached prefix   @ $0.003 / 1M each time
 *
 * This script measures (a) and (b) exactly from the session logs.
 */
import { readFileSync, readdirSync, realpathSync } from 'node:fs'
import { join } from 'node:path'
import { zstdDecompressSync } from 'node:zlib'

const MAGIC = Buffer.from([0x28, 0xb5, 0x2f, 0xfd])
const P = { hit: 0.003, miss: 0.15, out: 0.60 }   // off-peak Flash

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

function* findLogs(dir, seen, depth = 0) {
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

const home = process.env.DSH_HOME ?? join(process.env.USERPROFILE ?? '', '.dsh')
const seen = new Set()
const files = [...findLogs(join(home, 'sessions'), seen)]

let totReasonOut = 0, totOutput = 0, totHit = 0, totMiss = 0
let reasonReread = 0        // tokens of reasoning re-read from cache on later requests
let reasonRereadCost = 0
let totalCost = 0
const perSession = []

for (const file of files) {
  let text
  try { text = decompressFrames(readFileSync(file)) } catch { continue }
  if (!text) continue
  let carriedReason = 0     // reasoning currently living in this session's context
  let sReasonOut = 0, sOut = 0, sHit = 0, sMiss = 0, sReread = 0, steps = 0
  for (const line of text.split('\n')) {
    if (!line.trim()) continue
    let o
    try { o = JSON.parse(line) } catch { continue }
    if (o.type !== 'assistant/message') continue
    const u = o.data?.usage
    if (!u) continue
    steps++
    const reason = u.reasoningTokens ?? 0
    const out = u.outputTokens ?? 0
    const hit = u.cacheReadTokens ?? 0
    const miss = u.inputTokens ?? 0

    // This request re-read `carriedReason` tokens of earlier reasoning from context.
    const reread = Math.min(carriedReason, hit + miss)
    reasonReread += reread
    reasonRereadCost += reread * P.hit / 1e6
    sReread += reread

    sReasonOut += reason; sOut += out; sHit += hit; sMiss += miss
    carriedReason += reason
    if (o.type === 'compaction/summary') carriedReason = 0
  }
  totReasonOut += sReasonOut; totOutput += sOut; totHit += sHit; totMiss += sMiss
  if (steps) {
    const c = (sHit * P.hit + sMiss * P.miss + sOut * P.out) / 1e6
    totalCost += c
    perSession.push({ file, steps, sReasonOut, sOut, sReread, c })
  }
}

const usd = (n) => '$' + n.toFixed(3)
const fmt = (n) => Math.round(n).toLocaleString('en-US')

const reasonOutCost = totReasonOut * P.out / 1e6
console.log('='.repeat(72))
console.log('COST OF THINKING (reasoning tokens), all sessions, off-peak prices')
console.log('='.repeat(72))
console.log(`requests                        : ${fmt(perSession.reduce((a, s) => a + s.steps, 0))}`)
console.log(`output tokens                   : ${fmt(totOutput)}`)
console.log(`  of which reasoning            : ${fmt(totReasonOut)}  (${(100 * totReasonOut / totOutput).toFixed(1)} %)`)
console.log()
console.log('(a) reasoning paid once as OUTPUT')
console.log(`    ${fmt(totReasonOut)} x $0.60/1M = ${usd(reasonOutCost)}`)
console.log()
console.log('(b) reasoning RE-READ from context on later requests')
console.log(`    ${fmt(reasonReread)} token-reads x $0.003/1M = ${usd(reasonRereadCost)}`)
console.log(`    (= ${(reasonReread / Math.max(1, totHit + totMiss) * 100).toFixed(1)} % of all input token-reads)`)
console.log()
const thinkingTotal = reasonOutCost + reasonRereadCost
console.log(`TOTAL attributable to thinking   : ${usd(thinkingTotal)}`)
console.log(`TOTAL bill (off-peak, all input) : ${usd(totalCost)}`)
console.log(`  -> thinking is ${(100 * thinkingTotal / totalCost).toFixed(1)} % of the entire bill`)
console.log()
console.log('CONTEXT POLLUTION')
console.log(`  median reasoning per request  : ${fmt(totReasonOut / perSession.reduce((a, s) => a + s.steps, 0))} tokens`)
console.log('  reasoning is appended to context forever, so it inflates every later request.')
console.log('  amplification factor (re-reads per 1 reasoning token produced):')
console.log(`    ${(reasonReread / Math.max(1, totReasonOut)).toFixed(1)}x`)
console.log()
console.log('TOP 8 SESSIONS BY REASONING RE-READ COST')
perSession.sort((a, b) => b.sReread - a.sReread)
for (const s of perSession.slice(0, 8)) {
  const name = s.file.replace(/^.*sessions\\/, '').replace(/\\session.*$/, '')
  console.log(`  reread ${fmt(s.sReread).padStart(12)} tok  (${usd(s.sReread * P.hit / 1e6)})  steps ${String(s.steps).padStart(5)}  reasonOut ${fmt(s.sReasonOut).padStart(9)}  ${name}`)
}
