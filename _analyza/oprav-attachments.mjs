// OBNOVA 14 souboru v attachments, ktere jsem rozbil prebasovanim.
//
// CO SE STALO: puvodni `files\X\<jmeno>` BYLY REALNE SOUBORY (hardlinky na
// obsah v objects). Pri prebasovani jsem na ne zavolal mklink /J a prepsal
// je junctionami, ktere se navic zacyklily. Data zustala jen v karantene.
//
// POSTUP: z karanteny zjistit spravny tvar (co je realny soubor, co hardlink,
// co junction) a v novem store ho znovu postavit. Original v karantene
// NEMENIME - je to jedina zaloha.
import { readdirSync, lstatSync, readlinkSync, statSync, copyFileSync, rmSync, existsSync, mkdirSync } from 'node:fs'
import { join, dirname } from 'node:path'

const Q = 'E:\\DSH-quarantine\\20261001-144747\\DSH_data'
const T = 'E:\\DeepSeekHarness-data'
const ATT = 'attachments\\v1'

function projdi(dir, h = 0, out = []) {
  if (h > 6) return out
  let es; try { es = readdirSync(dir, { withFileTypes: true }) } catch { return out }
  for (const e of es) {
    const p = join(dir, e.name)
    let st; try { st = lstatSync(p) } catch { continue }
    out.push({ p, st, jmeno: e.name })
    if (e.isDirectory()) projdi(p, h + 1, out)
  }
  return out
}

console.log('=== 1. POPIS ORIGINALU V KARANTENE ===')
const q = projdi(join(Q, ATT))
const realne = q.filter((x) => x.st.isFile() && !x.st.isSymbolicLink())
console.log(`  polozek: ${q.length}, realnych souboru: ${realne.length}`)
for (const r of realne) {
  console.log(`  SOUBOR ${r.st.size} B  ${r.p.slice(Q.length + 1)}`)
}

console.log()
console.log('=== 2. OBNOVA V NOVEM STORE ===')
let obnoveno = 0
const chyby = []
for (const r of realne) {
  const rel = r.p.slice(Q.length + 1)
  const cil = join(T, rel)
  try {
    mkdirSync(dirname(cil), { recursive: true })
    // kdyz je na cili junction, odstranit (rmdir odstrani jen link)
    if (existsSync(cil)) {
      const st = lstatSync(cil)
      if (st.isSymbolicLink()) rmSync(cil, { recursive: false, force: true })
      else rmSync(cil, { force: true })
    }
    copyFileSync(r.p, cil)
    const over = lstatSync(cil)
    if (over.size !== r.st.size) throw new Error(`velikost nesedi: ${over.size} != ${r.st.size}`)
    obnoveno++
    console.log(`  OK  ${over.size} B  ${rel}`)
  } catch (e) {
    chyby.push(`${rel}: ${e.message}`)
    console.log(`  CHYBA ${rel}: ${e.message}`)
  }
}

console.log()
console.log('=== 3. ODSTRANENI ZACYCLENYCH JUNCTIONU ===')
let odstraneno = 0
function junctiony(dir, h = 0, out = []) {
  if (h > 6) return out
  let es; try { es = readdirSync(dir, { withFileTypes: true }) } catch { return out }
  for (const e of es) {
    const p = join(dir, e.name)
    let st; try { st = lstatSync(p) } catch { continue }
    if (st.isSymbolicLink()) out.push(p)
    else if (e.isDirectory()) junctiony(p, h + 1, out)
  }
  return out
}
for (const j of junctiony(join(T, ATT))) {
  let cil = null
  try { cil = readlinkSync(j) } catch { /* ignore */ }
  // zacyklena = jeji cil je zpet v attachments (file-objects <-> files)
  if (cil && cil.startsWith(join(T, ATT))) {
    try {
      rmSync(j, { recursive: false, force: true })
      odstraneno++
      console.log(`  odstranen: ${j.slice(T.length + 1)}`)
    } catch (e) { console.log(`  nepodarilo se odstranit ${j.slice(T.length + 1)}: ${e.message}`) }
  }
}

console.log()
console.log('=== 4. VYSLEDEK ===')
console.log(`  obnoveno souboru: ${obnoveno} z ${realne.length}`)
console.log(`  odstraneno zacyclenych junctionu: ${odstraneno}`)
if (chyby.length) { console.log('  CHYBY:'); chyby.forEach((c) => console.log('    ' + c)) }

// Overeni: precti obnoveny SKILL.md
const sk = join(T, ATT, 'files\\5b\\5bb58208e9ef1576d7a50258bd720422fa4e7bf0a6ce45d02487728e5fe2f6c7\\SKILL.md')
try {
  const s = statSync(sk)
  console.log(`\n  KONTROLA SKILL.md: ${s.size} B  ${s.size === 4500 ? 'OK' : 'NESPRAVNA VELIKOST'}`)
} catch (e) { console.log(`\n  KONTROLA SKILL.md selhala: ${e.code}`) }

process.exit(chyby.length === 0 && obnoveno === realne.length ? 0 : 1)
