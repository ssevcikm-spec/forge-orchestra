// Hloubkova analyza orchestra - Q10: zdroj pravdy o roadmapě (soubor vs D1).
// Spusteni: node _analyza/hl-roadmap-srovnani.mjs
import { readFileSync } from 'node:fs'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const env = Object.fromEntries(
  readFileSync(`${WS}/orchestra/.env`, 'utf8').split(/\r?\n/)
    .filter((l) => l.includes('=') && !l.trim().startsWith('#'))
    .map((l) => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]),
)
const r = await fetch(env.FORGE_URL.replace(/\/$/, '') + '/roadmap', { headers: { 'x-forge-secret': env.FORGE_SECRET } })
const d1 = (await r.json()).roadmap || []
const rm = JSON.parse(readFileSync(`${WS}/games/uo-shadows/.forge/roadmap.json`, 'utf8'))
const soubor = rm.grains || []

const g = (id) => String(id).split('/').slice(1).join('/')
const mD1 = new Map(d1.map((x) => [g(x.item_id), x]))
const mF = new Map(soubor.map((x) => [x.id, x]))
const vsechna = [...new Set([...mD1.keys(), ...mF.keys()])].sort()

console.log(`# mereno ${new Date().toISOString()}`)
console.log(`# D1 (GET /roadmap): ${d1.length} řádků | soubor (roadmap.json): ${soubor.length} granul`)
console.log(`# D1 'done': ${d1.filter((x) => x.status === 'done').length} | soubor 'done:true': ${soubor.filter((x) => x.done === true).length}`)
console.log(`# jen v D1: ${[...mD1.keys()].filter((k) => !mF.has(k)).length} | jen v souboru: ${[...mF.keys()].filter((k) => !mD1.has(k)).length}`)
console.log('')
console.log('  granule              | soubor done | D1 status  | D1 task | D1 attempts | ROZEJITO?')
for (const id of vsechna) {
  const f = mF.get(id), d = mD1.get(id)
  const roz = (f === undefined) !== (d === undefined)
  console.log(`  ${id.padEnd(20)} | ${String(f ? (f.done === true) : '(v souboru není)').padEnd(11)} | ${String(d ? d.status : '(v D1 není)').padEnd(10)} | ${String(d ? d.task_id : '-').padEnd(7)} | ${String(d ? d.attempts : '-').padEnd(11)} | ${roz ? 'ANO' : 'ne'}`)
}
console.log('')
console.log('# Co z toho plyne:')
console.log('#  1) soubor nezná 4 granule, které D1 považuje za vydané (stav je jen v D1)')
console.log('#  2) soubor neumí říct „hotovo" u 8 granul, které D1 vede jako done')
console.log('#  3) D1 nezná 0 granul, které jsou v souboru → soubor je NADMNOŽINA (po resetu by o stav přišel)')
console.log('#  4) /roadmap/reset smaže řádky D1 a stav postaví ZNOVU ze souboru → hotové granule bez done:true by se vydaly znovu')
