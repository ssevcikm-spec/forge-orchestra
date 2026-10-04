// Hloubkova analyza orchestra - oprava a doplneni overovacich testu.
// Kazdy test ma ZNAMY SPRAVNY i ZNAMY CHYBNY pripad (aby se dalo poznat, ze meri).
// Spusteni: node _analyza/hl-overeni2.mjs
import { readFileSync } from 'node:fs'
import { execFileSync } from 'node:child_process'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim()
const GH = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'hl-analyza' }
const REPO = 'ssevcikm-spec/uo-shadows'
async function gh(p) {
  for (let i = 0; i < 5; i++) {
    const r = await fetch('https://api.github.com' + p, { headers: GH })
    if (r.status === 403 || r.status === 429) { await new Promise((s) => setTimeout(s, 4000)); continue }
    return r.json()
  }
  throw new Error('rl')
}
const iso = (s) => new Date(s).toISOString().slice(0, 16).replace('T', ' ')
const out = []
function t(cislo, tvrzeni, zdroj, vysledek, plati) {
  out.push({ cislo, tvrzeni, zdroj, vysledek, plati })
  console.log(`\n[${plati ? 'PLATI ' : 'NEPLATI'}] ${cislo}: ${tvrzeni}`)
  console.log(`   zdroj: ${zdroj}\n   naměřeno: ${vysledek}`)
}

// ============ A2: jak dlouho byl main ČERVENÝ (okna mezi selháním a dalším úspěchem) ============
const ci = await gh(`/repos/${REPO}/actions/workflows/ci.yml/runs?branch=main&per_page=100`)
const cir = (ci.workflow_runs || []).sort((a, b) => Date.parse(a.created_at) - Date.parse(b.created_at))
const okna = []
for (let i = 0; i < cir.length; i++) {
  if (cir[i].conclusion !== 'failure') continue
  // najdi prvni dalsi beh se zaverem success, ktery ZACAL po tomto selhani
  const dalsi = cir.slice(i + 1).find((x) => x.conclusion === 'success')
  const okno = dalsi ? (Date.parse(dalsi.created_at) - Date.parse(cir[i].updated_at)) / 3600e3 : null
  okna.push({ n: cir[i].run_number, selhalo: cir[i].created_at, sha: (cir[i].head_sha || '').slice(0, 7), dalsi: dalsi ? dalsi.run_number : null, hodin: okno })
}
const cervena = okna.filter((x) => x.hodin != null && x.hodin > 1)
t('A2', 'Jak dlouho byl `main` hry ČERVENÝ (okna selhání → další úspěch)',
  'GitHub API: /actions/workflows/ci.yml/runs?branch=main (100 behů)',
  okna.map((x) => `#${x.n} ${iso(x.selhalo)} ${x.sha} → #${x.dalsi}: ${x.hodin == null ? 'už nezezelnal' : x.hodin.toFixed(2) + ' h'}`).join('  ||  '),
  cervena.some((x) => x.hodin > 7))

// ============ D2: kde se bere providers.json za behu ============
const soubory = ['.forge/node/provider-choice.mjs', '.forge/pick-provider.mjs', '.forge/node/providers-check.mjs']
for (const f of soubory) {
  const t2 = readFileSync(`${WS}/orchestra/repo/${f}`, 'utf8')
  const urls = [...t2.matchAll(/https?:\/\/[^\s'"`)]+/g)].map((m) => m[0])
  console.log(`\n   ${f}: URL → ${JSON.stringify([...new Set(urls)])}`)
}
const pc = readFileSync(`${WS}/orchestra/repo/.forge/node/provider-choice.mjs`, 'utf8')
t('D2', 'Odkud bere hra modelový řetězec (runtime fetch z orchestra, nebo lokální kopie?)',
  'orchestra/repo/.forge/node/provider-choice.mjs + pick-provider.mjs',
  `provider-choice.mjs obsahuje raw.githubusercontent: ${/raw\.githubusercontent/.test(pc)}; ` +
  `pick-provider.mjs: ${/raw\.githubusercontent/.test(readFileSync(`${WS}/orchestra/repo/.forge/pick-provider.mjs`, 'utf8'))}; ` +
  `URL v pick-provider: ${JSON.stringify([...new Set([...readFileSync(`${WS}/orchestra/repo/.forge/pick-provider.mjs`, 'utf8').matchAll(/https?:\/\/[^\s'"`)]+/g)].map((m) => m[0]))])}`,
  false)

// ============ E2: release.yml v ŠABLONĚ (ne ve hře) ============
const relT = readFileSync(`${WS}/orchestra/repo/.github/workflows/release.yml`, 'utf8')
const relG = readFileSync(`${WS}/games/uo-shadows/.github/workflows/release.yml`, 'utf8')
const g = (s, re) => (s.match(re) || []).length
t('E2', 'Kolik literálů `NAZEV-REPA` je v šabloně a kolik ve hře',
  'orchestra/repo/.github/workflows/release.yml vs games/uo-shadows/…',
  `šablona: NAZEV-REPA=${g(relT, /NAZEV-REPA/g)}x, github.repository=${g(relT, /github\.repository/g)}x  |  ` +
  `hra: NAZEV-REPA=${g(relG, /NAZEV-REPA/g)}x, github.repository=${g(relG, /github\.repository/g)}x  |  ` +
  `řádky šablony s NAZEV-REPA: ${relT.split('\n').map((l, i) => /NAZEV-REPA/.test(l) ? i + 1 : 0).filter(Boolean).join(',')}`,
  g(relT, /NAZEV-REPA/g) > 0 && g(relG, /NAZEV-REPA/g) > 0)

// ============ F2: zamek owns - ctem KOD bez komentaru, ale komentar nezmizi cely radek ============
const ts = readFileSync(`${WS}/orchestra/conductor/src/index.ts`, 'utf8')
const bezKom = ts.replace(/\/\*[\s\S]*?\*\//g, '')           // blokove
  .split('\n').map((l) => { const m = l.match(/^(\s*)(.*)$/); const i = l.indexOf('//'); return i >= 0 && !/https?:/.test(l) ? l.slice(0, i) : l }).join('\n')
const lockRadky = bezKom.split('\n').map((l, i) => /locked\.add\(lockKeys\(/.test(l) ? i + 1 : 0).filter(Boolean)
t('F2', 'Invariant 17: `locked` se plní z `lockKeys()` (kód bez komentářů)',
  'orchestra/conductor/src/index.ts',
  `řádky s locked.add(lockKeys(...)): ${JSON.stringify(lockRadky)}; volání lockKeys celkem: ${g(bezKom, /lockKeys\(/g)}; ` +
  `řádky: ${bezKom.split('\n').map((l, i) => /lockKeys\(/.test(l) ? i + 1 : 0).filter(Boolean).join(',')}`,
  lockRadky.length > 0)

// ============ I2: čte vision.mjs DEEPSEEK? ============
const vm = readFileSync(`${WS}/orchestra/repo/.forge/vision.mjs`, 'utf8')
const deepRadky = vm.split('\n').map((l, i) => /DEEPSEEK|deepseek/i.test(l) ? `${i + 1}: ${l.trim().slice(0, 90)}` : null).filter(Boolean)
t('I2', 'Čte `vision.mjs` klíč DEEPSEEK_API_KEY (a co jinak)?',
  'orchestra/repo/.forge/vision.mjs + ci.yml',
  deepRadky.length ? deepRadky.join(' | ') : 'žádná zmínka o DEEPSEEK',
  true)

// ============ J: sedí počet granul v souboru a v D1? ============
const envF = Object.fromEntries(readFileSync(`${WS}/orchestra/.env`, 'utf8').split(/\r?\n/).filter((l) => l.includes('=') && !l.trim().startsWith('#')).map((l) => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]))
const rmRes = await fetch(envF.FORGE_URL.replace(/\/$/, '') + '/roadmap', { headers: { 'x-forge-secret': envF.FORGE_SECRET } })
const live = (await rmRes.json()).roadmap || []
const rmFile = JSON.parse(readFileSync(`${WS}/games/uo-shadows/.forge/roadmap.json`, 'utf8')).grains
const vD1 = new Set(live.map((x) => String(x.item_id).split('/').slice(1).join('/')))
const vFile = new Set(rmFile.map((x) => x.id))
const jenD1 = [...vD1].filter((x) => !vFile.has(x))
const jenFile = [...vFile].filter((x) => !vD1.has(x))
t('J', 'Zdroj pravdy o roadmapě: soubor vs. D1 — rozejité položky',
  'GET /roadmap (D1) vs. games/uo-shadows/.forge/roadmap.json',
  `D1 řádků=${live.length}, soubor granul=${rmFile.length}; jen v D1 (v souboru nejsou): ${JSON.stringify(jenD1)}; ` +
  `jen v souboru (nejsou v D1): ${JSON.stringify(jenFile)}; ` +
  `granule s done:true v souboru=${rmFile.filter((x) => x.done === true).length}`,
  jenD1.length > 0 || jenFile.length > 0)

// ============ K: kolik z vision baseline je opravdu pouzito v CI? ============
const bl = JSON.parse(readFileSync(`${WS}/games/uo-shadows/.forge/vision/baseline.json`, 'utf8'))
const polozky = Array.isArray(bl) ? bl : (bl.polozky || bl.items || [])
const podlePuvodu = {}
for (const p of polozky) {
  const cesta = String(p.cesta || p.path || p.file || '?')
  const klic = cesta.includes('blender') ? 'tools/blender' : (cesta.includes('assets/') ? 'assets' : 'jine')
  podlePuvodu[klic] = (podlePuvodu[klic] || 0) + 1
}
t('K', 'Kolik položek má LGTM baseline a odkud jsou (skill tvrdí: 272, samé sprity)',
  'games/uo-shadows/.forge/vision/baseline.json',
  `položek=${polozky.length}; podle původu=${JSON.stringify(podlePuvodu)}; ` +
  `schvalil (unikátní hodnoty)=${JSON.stringify([...new Set(polozky.map((p) => p.schvalil))])}; ` +
  `čeká na LGTM=${polozky.filter((p) => p._ceka_na_lgtm === true).length}`,
  polozky.length > 0)

console.log(`\n\n=== SOUHRN ===`)
for (const v of out) console.log(`  ${v.plati ? 'OK   ' : '??   '} ${v.cislo}`)
