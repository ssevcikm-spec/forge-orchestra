// Ověřuje, jaké `contextWindow` DSH skutečně posílá — čte `request/context`
// z reálných session logů (a pro kontrolu i `request/header`).
//
// PROČ: `~\.dsh\skills\dsh-usage\report.mjs` má okno NATVRDO
// (`const PK = 800000`, ř. 184) a odvozuje z něj prahy 640k/800k.
// Když se změní model, předpoklad se musí přeměřit.
//
// Naměřeno 1. 10. 2026: deepseek-flash / deepseek-v4-flash / deepseek-v4-pro
// = 1 000 000; ale `deepseek-v4-flash-free` = 200 000 a `assistant` = 262 144.
// Na těch by prahy ležely NAD oknem a report by hlásil zelenou špatně.
//
// Spuštění:  node _analyza\over-okno.mjs   (z rootu workspace)
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

// model -> Set(contextWindow)
const okna = new Map()
let headeru = 0
for (const f of files) {
  let txt; try { txt = dec(readFileSync(f)) } catch { continue }
  for (const line of txt.split('\n')) {
    if (!line.trim()) continue
    let o; try { o = JSON.parse(line) } catch { continue }
    if (o.type !== 'request/header') continue
    headeru++
    const c = o.data?.header?.config ?? {}
    const win = o.data?.header?.contextWindow ?? c.contextWindow ?? null
    const key = String(c.model ?? '(bez modelu)')
    if (!okna.has(key)) okna.set(key, new Map())
    const m = okna.get(key)
    const k2 = String(win)
    m.set(k2, (m.get(k2) ?? 0) + 1)
  }
}

console.log('request/header záznamů:', headeru)
console.log('log souborů:', files.length)
console.log('\ncontextWindow podle modelu:')
for (const [model, m] of [...okna.entries()].sort()) {
  const casti = [...m.entries()].map(([w, n]) => `${w} (${n}x)`).join(', ')
  console.log(`  ${model.padEnd(28)} ${casti}`)
}

// Fallback: podívej se i do request/context, kde contextWindow podle schématu je
console.log('\n--- kontrola přes request/context ---')
const ctx = new Map()
for (const f of files) {
  let txt; try { txt = dec(readFileSync(f)) } catch { continue }
  for (const line of txt.split('\n')) {
    if (!line.trim()) continue
    let o; try { o = JSON.parse(line) } catch { continue }
    if (o.type !== 'request/context') continue
    const key = `${o.data?.model ?? '?'} | win=${o.data?.contextWindow ?? 'CHYBI'}`
    ctx.set(key, (ctx.get(key) ?? 0) + 1)
  }
}
if (ctx.size === 0) console.log('  (žádné request/context záznamy)')
for (const [k, n] of [...ctx.entries()].sort()) console.log(`  ${k}  ${n}x`)
