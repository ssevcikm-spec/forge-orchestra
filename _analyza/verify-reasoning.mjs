// Verify: does DSH actually replay reasoning_content back into the request?
import { readFileSync, readdirSync, realpathSync } from 'node:fs'
import { join } from 'node:path'
import { zstdDecompressSync } from 'node:zlib'

const MAGIC = Buffer.from([0x28, 0xb5, 0x2f, 0xfd])
function dec(buf) {
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

const seen = new Set()
const home = process.env.DSH_HOME ?? ''
const files = [...findLogs(join(home, 'sessions'), seen)]

// Look for any record that carries a full request body, and check for reasoning replay.
let found = 0
const shapes = new Map()
for (const f of files) {
  if (found > 6) break
  let txt; try { txt = dec(readFileSync(f)) } catch { continue }
  for (const line of txt.split('\n')) {
    if (!line.trim()) continue
    let o; try { o = JSON.parse(line) } catch { continue }
    if (!/^request\//.test(o.type ?? '')) continue
    const s = JSON.stringify(o)
    shapes.set(o.type, (shapes.get(o.type) ?? 0) + 1)
    if (found < 3 && o.type === 'request/header') {
      console.log('--- request/header keys:', Object.keys(o.data ?? o).join(', '))
      const d = o.data ?? o
      console.log(JSON.stringify(d).slice(0, 1200))
      console.log()
      found++
    }
    if (found < 6 && s.includes('reasoning')) {
      const idx = s.indexOf('reasoning')
      console.log(`[${o.type}] reasoning mentioned: ...${s.slice(Math.max(0, idx - 120), idx + 240)}...`)
      console.log()
      found++
    }
  }
}
console.log('request record types seen:', [...shapes.entries()])

// Independent proof: if reasoning were NOT replayed, DeepSeek returns HTTP 400.
// Scan logs for error records.
let errs = 0
const errSamples = []
for (const f of files) {
  let txt; try { txt = dec(readFileSync(f)) } catch { continue }
  for (const line of txt.split('\n')) {
    if (!line.includes('400') && !line.toLowerCase().includes('reasoning_content')) continue
    let o; try { o = JSON.parse(line) } catch { continue }
    const s = JSON.stringify(o)
    if (s.includes('reasoning_content') || /"status"\s*:\s*400/.test(s)) {
      errs++
      if (errSamples.length < 3) errSamples.push(s.slice(0, 400))
    }
  }
}
console.log(`\nrecords mentioning reasoning_content or HTTP 400: ${errs}`)
for (const e of errSamples) console.log('  ' + e)
