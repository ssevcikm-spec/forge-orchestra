// NEJSILNEJSI OVERENI (jen cteni): u vsech content-addressed souboru overi,
// ze SHA256(obsah) == nazev souboru. To dokazuje integritu bez ohledu na to,
// co tvrdi migrace, karantena nebo jakekoli pocitadlo.
//
// Tyka se: attachments\v1\objects\<2znaky>\<64 hex>
//          attachments\v1\file-objects\<2znaky>\<64 hex>
//          attachments\v1\files\<2znaky>\<64 hex>\<jmeno>
import { readdirSync, lstatSync, readFileSync, readlinkSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { join } from 'node:path'

const T = 'E:\\DeepSeekHarness-data'
const HEX64 = /^[0-9a-f]{64}$/

const vysledky = { ok: 0, spatne: [], preskoceno: 0, junctiony: 0, prazdne: [] }

function zkontroluj(cesta, ocekavany) {
  let st
  try { st = lstatSync(cesta) } catch { return }
  if (st.isSymbolicLink()) {
    vysledky.junctiony++
    // junctionu overime tak, ze precteme jeji cil pres lstat (nesleduje link)
    let cil = null
    try { cil = readlinkSync(cesta) } catch { /* ignore */ }
    if (cil) {
      try { lstatSync(cil); vysledky.ok++ } catch { vysledky.spatne.push(`${cesta} -> cil CHYBI`) }
    }
    return
  }
  if (st.isDirectory()) {
    // slozka <hash>: hledej uvnitr soubor a over hash
    let es
    try { es = readdirSync(cesta) } catch { return }
    if (es.length === 0) { vysledky.prazdne.push(cesta.slice(T.length + 1)); return }
    for (const e of es) zkontroluj(join(cesta, e), ocekavany)
    return
  }
  // soubor
  if (!ocekavany) { vysledky.preskoceno++; return }
  try {
    const h = createHash('sha256').update(readFileSync(cesta)).digest('hex')
    if (h === ocekavany) vysledky.ok++
    else vysledky.spatne.push(`${cesta.slice(T.length + 1)}  hash=${h.slice(0, 16)}.. != nazev=${ocekavany.slice(0, 16)}..`)
  } catch (e) { vysledky.spatne.push(`${cesta.slice(T.length + 1)}  nelze precist: ${e.code}`) }
}

console.log('=== KONTROLA content-addressing (SHA256 vs nazev) ===')
for (const oblast of ['objects', 'file-objects', 'files']) {
  const zaklad = join(T, 'attachments', 'v1', oblast)
  let podadresare
  try { podadresare = readdirSync(zaklad, { withFileTypes: true }) } catch { continue }
  for (const p of podadresare) {
    if (!p.isDirectory()) continue
    const cesta = join(zaklad, p.name)
    for (const e of readdirSync(cesta)) {
      const cil = join(cesta, e)
      if (HEX64.test(e)) zkontroluj(cil, e)          // <64hex> -> soubor nebo slozka
      else if (e.length > 2) zkontroluj(cil, p.name.length === 64 ? p.name : null)
    }
  }
}

console.log()
console.log(`  OVERENO (hash == nazev) : ${vysledky.ok}`)
console.log(`  JUNCTIONY (cil overen)  : ${vysledky.junctiony}`)
console.log(`  PRAZDNE ADRESARE        : ${vysledky.prazdne.length}`)
console.log(`  PRESKOCENO (bez hashe)  : ${vysledky.preskoceno}`)
console.log(`  NESPRAVNYCH             : ${vysledky.spatne.length}`)
if (vysledky.spatne.length) {
  console.log()
  console.log('  --- NESPRAVNE ---')
  for (const s of vysledky.spatne) console.log(`    ${s}`)
}
if (vysledky.prazdne.length) {
  console.log()
  console.log('  --- PRAZDNE ADRESARE (ocekavane u content-addressed stromu) ---')
  for (const s of vysledky.prazdne.slice(0, 12)) console.log(`    ${s}`)
  if (vysledky.prazdne.length > 12) console.log(`    ... a dalsich ${vysledky.prazdne.length - 12}`)
}
console.log()
console.log(vysledky.spatne.length === 0 ? '=== INTEGRITA OK ===' : `=== ${vysledky.spatne.length} VAD ===`)
process.exit(vysledky.spatne.length === 0 ? 0 : 1)
