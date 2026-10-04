// What precedes a cache-bust? Measure the idle gap and the preceding record type.
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
function tsOf(o) {
  for (const v of [o.time, o.ts, o.timestamp, o.data?.time, o.data?.ts]) {
    if (typeof v === 'number' && v > 1e11) return v
    if (typeof v === 'string') { const t = Date.parse(v); if (!Number.isNaN(t)) return t }
  }
  return null
}

const seen = new Set()
const home = process.env.DSH_HOME ?? ''
const files = [...findLogs(join(home, 'sessions'), seen)]

const gaps = []          // seconds between previous request and the busting request
const prevTypes = new Map()
const busts = []
const gapBuckets = { '<1 min': 0, '1-10 min': 0, '10-60 min': 0, '1-6 h': 0, '>6 h': 0, 'unknown': 0 }

for (const f of files) {
  let txt; try { txt = dec(readFileSync(f)) } catch { continue }
  const sname = f.replace(/^.*sessions\\/, '').replace(/\\session.*$/, '')
  let lastReqTime = null
  let lastType = null
  for (const line of txt.split('\n')) {
    if (!line.trim()) continue
    let o; try { o = JSON.parse(line) } catch { continue }
    const t = tsOf(o)
    if (o.type === 'assistant/message' && o.data?.usage) {
      const miss = o.data.usage.inputTokens ?? 0
      const hit = o.data.usage.cacheReadTokens ?? 0
      if (miss > 100000) {
        const gap = (t !== null && lastReqTime !== null) ? (t - lastReqTime) / 1000 : null
        gaps.push(gap)
        prevTypes.set(lastType ?? '?', (prevTypes.get(lastType ?? '?') ?? 0) + 1)
        busts.push({ sname, miss, hit, gap, prevType: lastType, ctx: miss + hit })
        if (gap === null) gapBuckets['unknown']++
        else if (gap < 60) gapBuckets['<1 min']++
        else if (gap < 600) gapBuckets['1-10 min']++
        else if (gap < 3600) gapBuckets['10-60 min']++
        else if (gap < 21600) gapBuckets['1-6 h']++
        else gapBuckets['>6 h']++
      }
      lastReqTime = t ?? lastReqTime
    }
    if (t !== null) lastType = o.type
  }
}

const fmt = (n) => Math.round(n).toLocaleString('en-US')
const known = gaps.filter((g) => g !== null)
console.log('='.repeat(74))
console.log('WHAT CAUSES CACHE-BUSTS?  (61 events with miss > 100k)')
console.log('='.repeat(74))
console.log(`events: ${busts.length}   median idle gap before bust: ${known.length ? (known.sort((a, b) => a - b)[Math.floor(known.length / 2)]).toFixed(0) + ' s' : 'n/a'}`)
console.log()
console.log('IDLE GAP BEFORE THE BUSTING REQUEST')
for (const [k, v] of Object.entries(gapBuckets)) if (v) console.log(`  ${k.padEnd(10)} ${String(v).padStart(3)}  ${'#'.repeat(v)}`)
console.log()
console.log('IMMEDIATELY PRECEDING RECORD TYPE')
for (const [k, v] of [...prevTypes.entries()].sort((a, b) => b[1] - a[1])) console.log(`  ${String(v).padStart(3)} x  ${k}`)
console.log()
console.log('TOP 12 BUSTS')
for (const b of busts.sort((a, b2) => b2.miss - a.miss).slice(0, 12)) {
  const g = b.gap === null ? 'n/a' : b.gap > 3600 ? (b.gap / 3600).toFixed(1) + ' h' : b.gap > 60 ? (b.gap / 60).toFixed(1) + ' min' : b.gap.toFixed(0) + ' s'
  console.log(`  miss ${fmt(b.miss).padStart(10)}  ctx ${fmt(b.ctx).padStart(10)}  idle before ${g.padStart(8)}  prev: ${b.prevType}  ${b.sname}`)
}
console.log()
const longIdle = busts.filter((b) => b.gap !== null && b.gap > 1800)
console.log(`busts preceded by >30 min idle (cache likely expired): ${longIdle.length}`)
console.log(`  tokens re-billed by those: ${fmt(longIdle.reduce((a, b) => a + b.miss, 0))}`)
const shortIdle = busts.filter((b) => b.gap !== null && b.gap < 1800)
console.log(`busts with an active session (<30 min idle): ${shortIdle.length}`)
console.log(`  tokens re-billed by those: ${fmt(shortIdle.reduce((a, b) => a + b.miss, 0))}`)
