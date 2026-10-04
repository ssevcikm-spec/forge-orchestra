// What fills the context? Measure tool RESULT sizes by tool name.
// Tool results are the bulk of conversation history; each one is re-read on
// every later request, so size here compounds.
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

const stats = new Map()   // tool -> {n, chars, sizes:[]}
const perSession = []

for (const f of files) {
  let txt; try { txt = dec(readFileSync(f)) } catch { continue }
  const sname = f.replace(/^.*sessions\\/, '').replace(/\\session.*$/, '')
  // pair tool/call -> tool/result by id
  const callById = new Map()
  let sessChars = 0, sessResults = 0
  for (const line of txt.split('\n')) {
    if (!line.trim()) continue
    let o; try { o = JSON.parse(line) } catch { continue }
    if (o.type === 'tool/call') {
      const id = o.data?.id ?? o.data?.callId ?? o.id
      const name = o.data?.name ?? o.data?.tool ?? '?'
      if (id) callById.set(id, name)
      continue
    }
    if (o.type !== 'tool/result') continue
    const id = o.data?.id ?? o.data?.callId ?? o.id
    const name = callById.get(id) ?? o.data?.name ?? '?'
    const s = JSON.stringify(o.data?.result ?? o.data?.content ?? o.data ?? '')
    const n = s.length
    const st = stats.get(name) ?? { n: 0, chars: 0, sizes: [] }
    st.n++; st.chars += n; if (st.sizes.length < 4000) st.sizes.push(n)
    stats.set(name, st)
    sessChars += n; sessResults++
  }
  if (sessResults) perSession.push({ sname, sessChars, sessResults })
}

const fmt = (n) => Math.round(n).toLocaleString('en-US')
function pct(arr, p) { const a = [...arr].sort((x, y) => x - y); return a[Math.floor(a.length * p)] ?? 0 }

const totalChars = [...stats.values()].reduce((a, b) => a + b.chars, 0)
console.log('='.repeat(96))
console.log('WHAT FILLS THE CONTEXT — tool result sizes (chars, JSON-encoded)')
console.log('='.repeat(96))
console.log(`${'tool'.padEnd(16)} ${'calls'.padStart(6)} ${'total chars'.padStart(13)} ${'% of all'.padStart(9)} ${'mean'.padStart(9)} ${'median'.padStart(8)} ${'p90'.padStart(9)} ${'max'.padStart(10)}`)
for (const [n, st] of [...stats.entries()].sort((a, b) => b[1].chars - a[1].chars)) {
  console.log(`${n.padEnd(16)} ${String(st.n).padStart(6)} ${fmt(st.chars).padStart(13)} ${(100 * st.chars / totalChars).toFixed(1).padStart(8)}% ${fmt(st.chars / st.n).padStart(9)} ${fmt(pct(st.sizes, 0.5)).padStart(8)} ${fmt(pct(st.sizes, 0.9)).padStart(9)} ${fmt(pct(st.sizes, 1)).padStart(10)}`)
}
console.log(`${'TOTAL'.padEnd(16)} ${String([...stats.values()].reduce((a, b) => a + b.n, 0)).padStart(6)} ${fmt(totalChars).padStart(13)}`)

console.log()
console.log('ROUGH TOKEN EQUIVALENT (chars / 3.6, mixed CZ/EN/code)')
console.log(`  total tool-result text ever produced : ~${fmt(totalChars / 3.6)} tokens`)
const big = [...stats.entries()].filter(([, s]) => s.chars > 0).sort((a, b) => b[1].chars - a[1].chars)
for (const [n, s] of big.slice(0, 6)) console.log(`  ${n.padEnd(16)} ~${fmt(s.chars / 3.6).padStart(12)} tokens`)

console.log()
console.log('BIGGEST SINGLE RESULTS (the ones that really hurt)')
const all = []
for (const [n, st] of stats) for (const sz of st.sizes) all.push({ n, sz })
all.sort((a, b) => b.sz - a.sz)
for (const r of all.slice(0, 12)) console.log(`  ${fmt(r.sz).padStart(10)} chars  ~${fmt(r.sz / 3.6).padStart(9)} tok   ${r.n}`)
console.log()
const over = (lim) => all.filter((r) => r.sz > lim)
for (const lim of [4000, 12000, 40000, 200000]) {
  const g = over(lim)
  console.log(`  results over ${fmt(lim).padStart(7)} chars: ${String(g.length).padStart(5)}  carrying ${fmt(g.reduce((a, b) => a + b.sz, 0)).padStart(12)} chars (~${fmt(g.reduce((a, b) => a + b.sz, 0) / 3.6)} tok)`)
}
