// Which agent preset did each session run, and is run_code really callable?
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
const seen = new Set()
const home = process.env.DSH_HOME ?? ''
const files = [...findLogs(join(home, 'sessions'), seen)]

const presetBySession = new Map()
const runCodeBySession = new Map()
const allToolNames = new Map()
const envMode = new Map()
let presetRecords = 0

for (const f of files) {
  let txt; try { txt = dec(readFileSync(f)) } catch { continue }
  const sname = f.replace(/^.*sessions\\/, '').replace(/\\session.*$/, '')
  for (const line of txt.split('\n')) {
    if (!line.trim()) continue
    let o; try { o = JSON.parse(line) } catch { continue }
    const t = String(o.type ?? '')
    if (t.startsWith('agent-preset')) {
      presetRecords++
      const p = o.data?.agentPreset ?? o.data?.preset ?? o.agentPreset
      if (p) presetBySession.set(sname, p)
      continue
    }
    if (t === 'request/header') {
      const tools = o.data?.header?.tools
      if (Array.isArray(tools)) {
        for (const tt of tools) allToolNames.set(tt.name, (allToolNames.get(tt.name) ?? 0) + 1)
      }
      continue
    }
    if (t === 'tool/call') {
      const n = o.data?.name ?? o.data?.tool ?? '?'
      if (n === 'run_code') runCodeBySession.set(sname, (runCodeBySession.get(sname) ?? 0) + 1)
    }
  }
}

console.log('agent-preset records found:', presetRecords)
console.log('\npreset per session (first seen):')
const tally = new Map()
for (const p of presetBySession.values()) tally.set(p, (tally.get(p) ?? 0) + 1)
for (const [p, n] of [...tally.entries()].sort((a, b) => b[1] - a[1])) console.log(`  ${String(n).padStart(3)} x  ${p}`)
if (!presetBySession.size) console.log('  (none — the record type may differ; see note)')

console.log(`\nsessions that CALLED run_code: ${runCodeBySession.size} of ${files.length}`)
for (const [s, n] of [...runCodeBySession.entries()].sort((a, b) => b[1] - a[1]).slice(0, 12)) {
  console.log(`  ${String(n).padStart(5)} calls  preset=${presetBySession.get(s) ?? '?'}  ${s}`)
}

console.log('\nTOOL NAMES seen in request headers (what the MODEL can actually call):')
for (const [n, c] of [...allToolNames.entries()].sort((a, b) => b[1] - a[1])) {
  console.log(`  ${String(c).padStart(6)} headers mention  ${n}`)
}
