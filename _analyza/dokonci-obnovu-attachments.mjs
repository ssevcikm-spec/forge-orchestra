// Cilene dokonceni obnovy 14 souboru, ktere minule selhaly na EPERM.
// Overuje velikost i hash proti originalu v karantene.
import { lstatSync, readlinkSync, copyFileSync, rmSync, existsSync, mkdirSync, readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { join, dirname } from 'node:path'

const Q = 'E:\\DSH-quarantine\\20261001-144747\\DSH_data'
const T = 'E:\\DeepSeekHarness-data'

// Presne tech 14, ktere selhaly (z logu predchoziho behu)
const chybejici = [
  'attachments\\v1\\file-objects\\1d\\1d77e02e6b093b22a18e4244eb969f2f8371a7a6d102d03033f48ac5f39b5015',
  'attachments\\v1\\file-objects\\34\\349fc6f21b218c133b7db89c5873d7ff9710eb82c0ed473944f80e0f3a4da8c2',
  'attachments\\v1\\file-objects\\5b\\5bb58208e9ef1576d7a50258bd720422fa4e7bf0a6ce45d02487728e5fe2f6c7',
  'attachments\\v1\\file-objects\\62\\62a1ac305f58791db48b23b81ae3eb0000a685d2c8cf7f088e1c5a9cc1c2af45',
  'attachments\\v1\\file-objects\\ce\\ce6e1d783d942a04819c35118c1fc170f5b1dc60170486019f44459e918b3cb1',
  'attachments\\v1\\file-objects\\dd\\dd4c65cee560b374a758d72248b4f07d9e103c789ab40e4b2afea66a66c7068d',
  'attachments\\v1\\file-objects\\f4\\f4be818027e2477c553f37bbae7aa83edae2ae4294f90623110f698c741b7015',
  'attachments\\v1\\files\\1d\\1d77e02e6b093b22a18e4244eb969f2f8371a7a6d102d03033f48ac5f39b5015\\better-deepseek-20260917-115803.zip',
  'attachments\\v1\\files\\34\\349fc6f21b218c133b7db89c5873d7ff9710eb82c0ed473944f80e0f3a4da8c2\\docs-20260917-115459.zip',
  'attachments\\v1\\files\\5b\\5bb58208e9ef1576d7a50258bd720422fa4e7bf0a6ce45d02487728e5fe2f6c7\\SKILL.md',
  'attachments\\v1\\files\\62\\62a1ac305f58791db48b23b81ae3eb0000a685d2c8cf7f088e1c5a9cc1c2af45\\docs-20260917-115308.zip',
  'attachments\\v1\\files\\ce\\ce6e1d783d942a04819c35118c1fc170f5b1dc60170486019f44459e918b3cb1\\docs-20260917-115629.zip',
  'attachments\\v1\\files\\dd\\dd4c65cee560b374a758d72248b4f07d9e103c789ab40e4b2afea66a66c7068d\\docs-20260917-115415.zip',
  'attachments\\v1\\files\\f4\\f4be818027e2477c553f37bbae7aa83edae2ae4294f90623110f698c741b7015\\docs-20260917-115547.zip',
]

const sha = (p) => createHash('sha256').update(readFileSync(p)).digest('hex')

let ok = 0
const chyby = []
console.log('=== OBNOVA 14 SOUBORU ===')
for (const rel of chybejici) {
  const zdroj = join(Q, rel)
  const cil = join(T, rel)
  try {
    let st
    try { st = lstatSync(zdroj) } catch { throw new Error('zdroj v karantene neexistuje') }
    if (st.isSymbolicLink()) throw new Error('zdroj je junction, ne soubor')

    mkdirSync(dirname(cil), { recursive: true })
    if (existsSync(cil)) {
      const c = lstatSync(cil)
      rmSync(cil, { recursive: c.isDirectory() && !c.isSymbolicLink(), force: true })
    }
    copyFileSync(zdroj, cil)

    // Overeni velikosti I hashe
    const s2 = lstatSync(cil)
    if (s2.isSymbolicLink()) throw new Error('vysledek je junction!')
    if (s2.size !== st.size) throw new Error(`velikost ${s2.size} != ${st.size}`)
    const h1 = sha(zdroj), h2 = sha(cil)
    if (h1 !== h2) throw new Error('hash nesedi')

    ok++
    console.log(`  OK  ${String(s2.size).padStart(7)} B  sha=${h2.slice(0, 12)}..  ${rel.slice(20)}`)
  } catch (e) {
    chyby.push(`${rel}: ${e.message}`)
    console.log(`  CHYBA ${rel.slice(20)}: ${e.message}`)
  }
}

console.log()
console.log(`obnoveno: ${ok} z ${chybejici.length}`)
if (chyby.length) { console.log('CHYBY:'); chyby.forEach((c) => console.log('  ' + c)) }
process.exit(chyby.length ? 1 : 0)
