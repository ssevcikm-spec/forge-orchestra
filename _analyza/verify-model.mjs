// Verify model attribution: are the 4 "pro" sessions really pro, and how many
// usage records precede the first header (i.e. are unattributed)?
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

let totalUsage = 0, unattributed = 0, switches = 0
const proSessions = []

for (const f of files) {
  let txt; try { txt = dec(readFileSync(f)) } catch { continue }
  const sname = f.replace(/^.*sessions\\/, '').replace(/\\session.*$/, '')
  let cur = null
  const modelsSeen = []
  let usageHere = 0, unattribHere = 0, headers = 0
  for (const line of txt.split('\n')) {
    if (!line.trim()) continue
    let o; try { o = JSON.parse(line) } catch { continue }
    if (o.type === 'request/header') {
      headers++
      const m = o.data?.header?.config?.model
      if (m && m !== cur) {
        if (cur !== null) switches++
        cur = m
        modelsSeen.push(m)
      }
      continue
    }
    if (o.type !== 'assistant/message') continue
    if (!o.data?.usage) continue
    usageHere++; totalUsage++
    if (cur === null) { unattribHere++; unattributed++ }
  }
  const pro = modelsSeen.some((m) => /pro/i.test(m))
  if (pro) proSessions.push({ sname, modelsSeen, headers, usageHere, unattribHere })
}

console.log(`total assistant/message usage records : ${totalUsage}`)
console.log(`records before ANY header (unattributed): ${unattributed}  (${(100 * unattributed / totalUsage).toFixed(2)} %)`)
console.log(`model switches observed in-session     : ${switches}`)
console.log()
console.log('SESSIONS THAT USED A "PRO" MODEL:')
for (const s of proSessions) {
  console.log(`  ${s.sname}`)
  console.log(`     models seen: ${[...new Set(s.modelsSeen)].join(' -> ')}`)
  console.log(`     headers: ${s.headers}   usage records: ${s.usageHere}   unattributed: ${s.unattribHere}`)
}
