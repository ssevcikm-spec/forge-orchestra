// Overuje invariant: "co je v souboru roadmapy hotove, MUSI mit radek v D1".
// Kdyz radek chybi, zavislosti na tu granuli zustanou viset (roadmapTick dela
// jen UPDATE pres ON CONFLICT - ale pro 'done: true' dela UPSERT, takze se radek
// ZALOZI; otazka je, jestli se tak stalo u vsech).
// Jen cteni. Spusteni: node _analyza/hl-d1-rada.mjs
import { readFileSync } from 'node:fs'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const d1 = JSON.parse(readFileSync(`${WS}/_analyza/tmp-roadmap-d1.json`, 'utf8')).roadmap || []
const rm = JSON.parse(readFileSync(`${WS}/games/uo-shadows/.forge/roadmap.json`, 'utf8'))
const radky = new Map(d1.map((x) => [String(x.item_id).split('/').slice(1).join('/'), x]))

console.log(`# D1: ${d1.length} radku | soubor: ${rm.grains.length} granul`)
console.log('\nstav podle souboru a D1:')
console.log('  granule             | soubor done | D1 radek | D1 status | poznamka')
const chybi = []
for (const g of rm.grains) {
  const d = radky.get(g.id)
  const done = g.done === true
  let poz = ''
  if (done && !d) { poz = '← VADA: hotovo v souboru, ale v D1 NENI'; chybi.push(g.id) }
  else if (done && d && d.status !== 'done') poz = `← nesoulad: soubor done, D1 ${d.status}`
  else if (!done && d && d.status === 'done') poz = '← nesoulad: D1 done, soubor ne'
  console.log(`  ${g.id.padEnd(19)} | ${String(done).padEnd(11)} | ${String(d ? 'ANO' : 'NE').padEnd(8)} | ${String(d ? d.status : '-').padEnd(9)} | ${poz}`)
}

console.log(`\n# hotovych granul v souboru bez radku v D1: ${chybi.length} ${JSON.stringify(chybi)}`)

// a jeste: ktere zavislosti cekaji na granule bez radku v D1
console.log('\n# zavislosti na granulich bez radku v D1:')
let n = 0
for (const g of rm.grains) {
  for (const dep of (g.depends_on || [])) {
    if (!radky.has(dep)) {
      console.log(`   ${g.id} čeká na ${dep} – ${dep} nemá řádek v D1`)
      n++
    }
  }
}
console.log(`   celkem: ${n}`)
