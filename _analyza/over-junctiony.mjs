// Overi junctiony tak, aby se NESLEDOVALA smycka (to je prave ta past).
// existsSync() i statSync() junctiony sleduji -> u smycky v attachments vraci
// ELOOP a vypada to jako rozbita junctiona. Spravne je cist Target pres
// readlink a existenci cile overit pres lstat (nesleduje link).
import { lstatSync, readdirSync, readlinkSync, lstatSync as lstat } from 'node:fs'
import { join } from 'node:path'

const T = 'E:\\DeepSeekHarness-data'

function junctiony(dir, out = [], hloubka = 0) {
  if (hloubka > 6) return out
  let es
  try { es = readdirSync(dir, { withFileTypes: true }) } catch { return out }
  for (const e of es) {
    const p = join(dir, e.name)
    let st
    try { st = lstatSync(p) } catch { continue }
    // POZOR: dirent.isSymbolicLink() vraci u junctionu true, ale lstat je jistejsi
    if (st.isSymbolicLink()) out.push(p)
    else if (e.isDirectory()) junctiony(p, out, hloubka + 1)
  }
  return out
}

// existence cile BEZ sledovani linku (lstat misto stat)
function cilExistuje(p) {
  try { lstat(p); return true } catch { return false }
}

const j = junctiony(T)
let ok = 0, spatne = 0, mimo = 0
console.log(`junctions: ${j.length}\n`)

for (const p of j) {
  const cil = readlinkSync(p)
  const existuje = cilExistuje(cil)
  const veStore = cil.startsWith(T)
  if (!veStore) mimo++
  if (existuje) ok++; else spatne++
  console.log(`  ${existuje ? 'OK    ' : 'ROZBITO'} ${p.slice(T.length + 1).slice(0, 50)}`)
  console.log(`           -> ${cil.replace(T, '<STORE>')}`)
}

console.log(`\nzivych: ${ok}   rozbitych: ${spatne}   mimo store: ${mimo}`)

// Kontrola SMYCKY zamerne: cile obou stran musi existovat jako lstat
console.log('\n--- smycka file-objects <-> files (lstat, nesleduje se) ---')
const a = join(T, 'attachments\\v1\\file-objects\\5b\\5bb58208e9ef1576d7a50258bd720422fa4e7bf0a6ce45d02487728e5fe2f6c7')
const b = readlinkSync(a)
console.log(`  file-objects\\5b\\... -> ${b.replace(T, '<STORE>')}`)
console.log(`     lstat cile: ${cilExistuje(b) ? 'EXISTUJE' : 'CHYBI'}`)
try {
  const s = lstatSync(b)
  console.log(`     typ: ${s.isDirectory() ? 'adresar' : s.size + ' B soubor'}`)
} catch (e) { console.log(`     lstat chyba: ${e.code}`) }
