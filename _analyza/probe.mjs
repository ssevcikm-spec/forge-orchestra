// Probe: what usage fields are actually in DSH session logs?
import { readFileSync, readdirSync, statSync, realpathSync } from 'node:fs'
import { join } from 'node:path'
import { zstdDecompressSync } from 'node:zlib'

function* walk(dir, seen = new Set()) {
  let real
  try { real = realpathSync(dir) } catch { return }
  if (seen.has(real)) return
  seen.add(real)
  let entries
  try { entries = readdirSync(dir, { withFileTypes: true }) } catch { return }
  for (const e of entries) {
    const p = join(dir, e.name)
    if (e.isDirectory()) yield* walk(p, seen)
    else if (/^session(\.v\d+)?\.jsonl\.zstd$/.test(e.name)) yield p
  }
}

function decompressChain(buf) {
  // chained zstd frames: find magic 0x28 0xB5 0x2F 0xFD
  const magic = Buffer.from([0x28, 0xb5, 0x2f, 0xfd])
  const starts = []
  let idx = buf.indexOf(magic, 0)
  while (idx !== -1) { starts.push(idx); idx = buf.indexOf(magic, idx + 1) }
  if (!starts.length) return ''
  starts.push(buf.length)
  let out = ''
  for (let k = 0; k < starts.length - 1; k++) {
    try { out += zstdDecompressSync(buf.subarray(starts[k], starts[k + 1])).toString('utf8') } catch {}
  }
  return out
}

const roots = ['C:\\Users\\Ssevc\\.dsh\\sessions']
const files = []
for (const r of roots) for (const f of walk(r)) files.push(f)
console.log('files found:', files.length)

const keyCount = new Map()
const usageShapes = new Map()
let sampled = 0
const samples = []

for (const f of files) {
  if (sampled > 25) break
  let txt
  try { txt = decompressChain(readFileSync(f)) } catch { continue }
  if (!txt) continue
  sampled++
  for (const line of txt.split('\n')) {
    if (!line.trim()) continue
    let rec
    try { rec = JSON.parse(line) } catch { continue }
    const t = rec.type ?? rec.kind ?? rec.event ?? '?'
    keyCount.set(t, (keyCount.get(t) ?? 0) + 1)
    // hunt for usage-ish objects
    const stack = [rec]
    while (stack.length) {
      const o = stack.pop()
      if (!o || typeof o !== 'object') continue
      if (o.usage && typeof o.usage === 'object') {
        const shape = Object.keys(o.usage).sort().join(',')
        usageShapes.set(shape, (usageShapes.get(shape) ?? 0) + 1)
        if (samples.length < 4) samples.push({ file: f, type: t, usage: o.usage, model: o.model ?? o.modelId })
      }
      for (const v of Object.values(o)) if (v && typeof v === 'object') stack.push(v)
    }
  }
}

console.log('\n=== record types ===')
console.log([...keyCount.entries()].sort((a, b) => b[1] - a[1]).slice(0, 25))
console.log('\n=== usage shapes ===')
console.log([...usageShapes.entries()])
console.log('\n=== usage samples ===')
console.log(JSON.stringify(samples, null, 2))
