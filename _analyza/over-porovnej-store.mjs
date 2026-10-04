// Porovna REALNE soubory (ne junctiony) mezi novym store a karantenou.
// Cil: zjistit, zda migrace o neco prisla, a zda smycka v attachments
// ukazuje na skutecna data, nebo je prazdna uz od zacatku.
import { lstatSync, readdirSync, readlinkSync } from 'node:fs'
import { join, relative } from 'node:path'

function rozbor(root) {
  const soubory = new Set()
  const junctiony = []
  const prazdne = []
  let dirs = 0

  function walk(dir, h = 0) {
    if (h > 8) return
    let es
    try { es = readdirSync(dir, { withFileTypes: true }) } catch { return }
    let pocetDeti = 0
    for (const e of es) {
      const p = join(dir, e.name)
      let st
      try { st = lstatSync(p) } catch { continue }
      pocetDeti++
      const rel = relative(root, p)
      if (st.isSymbolicLink()) {
        let cil = null
        try { cil = readlinkSync(p) } catch { /* ignore */ }
        junctiony.push({ rel, cil })
      } else if (st.isDirectory()) {
        dirs++
        walk(p, h + 1)
      } else {
        soubory.add(rel)
      }
    }
    if (pocetDeti === 0) prazdne.push(relative(root, dir))
  }
  walk(root)
  return { soubory, junctiony, prazdne, dirs }
}

const T = 'E:\\DeepSeekHarness-data'
const Q = 'E:\\DSH-quarantine\\20261001-144747\\DSH_data'

const a = rozbor(T)
const b = rozbor(Q)

console.log('=== REALNE SOUBORY (bez junctionu) ===')
console.log(`  novy store : ${a.soubory.size} souboru, ${a.junctiony.length} junctionu, ${a.dirs} adresaru`)
console.log(`  karantena  : ${b.soubory.size} souboru, ${b.junctiony.length} junctionu, ${b.dirs} adresaru`)

console.log()
console.log('=== CO JE V KARANTENE A NENI V NOVEM STORE (ztrata?) ===')
const chybi = [...b.soubory].filter((x) => !a.soubory.has(x))
console.log(`  chybi: ${chybi.length}`)
for (const c of chybi.slice(0, 20)) console.log(`     ${c}`)

console.log()
console.log('=== CO JE V NOVEM STORE A NENI V KARANTENE (navic) ===')
const navic = [...a.soubory].filter((x) => !b.soubory.has(x))
console.log(`  navic: ${navic.length}`)
for (const c of navic.slice(0, 20)) console.log(`     ${c}`)

console.log()
console.log('=== ATTACHMENTS: kde jsou REALNA data? ===')
for (const [nazev, r] of [['novy store', a], ['karantena', b]]) {
  const att = [...r.soubory].filter((x) => x.startsWith('attachments'))
  console.log(`  ${nazev}: ${att.length} realnych souboru v attachments`)
  for (const x of att.slice(0, 12)) console.log(`     ${x}`)
}

console.log()
console.log('=== PRZADNE ADRESARE V attachments (novy store) ===')
const pa = a.prazdne.filter((x) => x.startsWith('attachments'))
console.log(`  ${pa.length} prazdnych`)
for (const x of pa.slice(0, 12)) console.log(`     ${x}`)
