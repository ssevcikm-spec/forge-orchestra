// Decisive check: is request/header emitted on CHANGE, or per turn?
// Compare consecutive headers within a session.
import { readFileSync, readdirSync, realpathSync } from 'node:fs'
import { join } from 'node:path'
import { zstdDecompressSync } from 'node:zlib'
import { createHash } from 'node:crypto'

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

let hTotal = 0, hChangedConfig = 0, hChangedTools = 0, hChangedSystem = 0, hIdentical = 0
let cTotal = 0, cIdentical = 0, cChanged = 0
let turns = 0

for (const f of files) {
  let txt; try { txt = dec(readFileSync(f)) } catch { continue }
  let prevH = null, prevC = null
  for (const line of txt.split('\n')) {
    if (!line.trim()) continue
    let o; try { o = JSON.parse(line) } catch { continue }
    if (o.type === 'turn/start') { turns++; continue }
    if (o.type === 'request/header') {
      const h = o.data?.header
      const sig = JSON.stringify({ c: h?.config, t: h?.tools?.map((x) => x.name), s: h?.system })
      hTotal++
      if (prevH !== null) {
        if (sig === prevH.sig) hIdentical++
        else {
          if (JSON.stringify(h?.config) !== prevH.config) hChangedConfig++
          if (JSON.stringify(h?.tools?.map((x) => x.name)) !== prevH.tools) hChangedTools++
          if (h?.system !== prevH.system) hChangedSystem++
        }
      }
      prevH = { sig, config: JSON.stringify(h?.config), tools: JSON.stringify(h?.tools?.map((x) => x.name)), system: h?.system }
      continue
    }
    if (o.type === 'request/context') {
      cTotal++
      const sig = JSON.stringify(o.data).length + ':' + createHash('sha1').update(JSON.stringify(o.data)).digest('hex').slice(0, 12)
      if (prevC !== null) { if (sig === prevC) cIdentical++; else cChanged++ }
      prevC = sig
    }
  }
}

console.log('Is request/header emitted on CHANGE or per-TURN?')
console.log(`  turn/start records          : ${turns}`)
console.log(`  request/header records      : ${hTotal}`)
console.log(`  -> header is NOT per-turn (${hTotal} < ${turns})`)
console.log(`  consecutive headers IDENTICAL byte-for-byte: ${hIdentical}`)
console.log(`  consecutive headers DIFFERENT             : ${hChangedConfig + hChangedTools + hChangedSystem}`)
console.log(`     of those, config changed : ${hChangedConfig}`)
console.log(`     of those, tool set changed: ${hChangedTools}`)
console.log(`     of those, system changed : ${hChangedSystem}`)
console.log()
console.log(`  request/context records: ${cTotal}   identical-consecutive: ${cIdentical}   changed: ${cChanged}`)
