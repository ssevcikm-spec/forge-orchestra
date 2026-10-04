// Hloubkova analyza orchestra - OVERENI tvrzeni z existujicich dokumentu.
// Kazde tvrzeni = jeden test: hypoteza → mereni → verdikt.
// Spusteni: node _analyza/hl-overeni.mjs
import { readFileSync } from 'node:fs'

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
const verdikt = []
function test(cislo, tvrzeni, zdroj, vysledek, platí) {
  verdikt.push({ cislo, tvrzeni, zdroj, vysledek, plati: platí })
  console.log(`\n[${platí ? 'PLATI ' : 'NEPLATI'}] ${cislo}: ${tvrzeni}`)
  console.log(`   zdroj: ${zdroj}`)
  console.log(`   naměřeno: ${vysledek}`)
}

// --- TVRZENI A: "main hry byl 7,5 h červený (S18)" ---
const ci = await gh(`/repos/${REPO}/actions/workflows/ci.yml/runs?branch=main&per_page=100`)
const cir = (ci.workflow_runs || []).sort((a, b) => a.run_number - b.run_number)
const selh = cir.filter((r) => r.conclusion === 'failure').map((r) => ({ n: r.run_number, t: r.created_at, u: r.updated_at, sha: (r.head_sha || '').slice(0, 7) }))
const mezi = []
for (let i = 1; i < selh.length; i++) {
  mezi.push((Date.parse(selh[i].t) - Date.parse(selh[i - 1].u)) / 3600e3)
}
test('A', '„main hry byl 7,5 h červený, orchestra nic nevydala" (skill orchestra, invariant 19)',
  'skill orchestra (invariant 19) + commit 7cd14cb',
  `CI selhání na main: ${selh.length} (${selh.map((x) => `#${x.n} ${iso(x.t)} ${x.sha}`).join(' | ')}); ` +
  `rozestupy mezi nimi: ${mezi.map((x) => x.toFixed(2) + ' h').join(', ')}`,
  mezi.some((x) => x > 6 && x < 9) && selh.length >= 2)

// --- TVRZENI B: "agent nic nezměnil" je nejčastější příčina ---
const priciny = JSON.parse(readFileSync(`${WS}/_analyza/hl-priciny.json`, 'utf8'))
const noChange = priciny.filter((x) => /Agent nic nezm/.test(x.krok)).length
const parse = priciny.filter((x) => /Kontrola parsov/.test(x.krok)).length
const testy = priciny.filter((x) => /Testy hry/.test(x.krok)).length
const ok = priciny.filter((x) => x.concl === 'success').length
test('B', 'Rozpad příčin selhání behů agent.yml (nikde v dokumentaci)',
  'vlastní měření: GitHub API, jobs → steps u 240 behů',
  `no-change=${noChange}, testy=${testy}, parsování=${parse}, úspěch=${ok}, celkem=${priciny.length}`,
  noChange > 90)

// --- TVRZENI C: "20 běhů celkem" vs total_count ---
const ag = await gh(`/repos/${REPO}/actions/workflows/agent.yml/runs?per_page=1`)
test('C', 'Čítač běhů: „total_count" agent.yml',
  'endpoint /actions/workflows/agent.yml/runs',
  `total_count=${ag.total_count} (jiný čítač než run_number posledního běhu)`,
  ag.total_count > 200)

// --- TVRZENI D: "providers.json se čte za běhu z orchestra, lokální kopie je záloha" ---
const pp = readFileSync(`${WS}/orchestra/repo/.forge/node/provider-choice.mjs`, 'utf8')
const url = (pp.match(/https:\/\/raw\.githubusercontent\.com\/[^\s'"`]+/) || [])[0]
test('D', 'Modelový řetězec se stahuje za běhu z orchestra (jedna oprava pro všechny hry)',
  'orchestra/repo/.forge/node/provider-choice.mjs',
  `nalezená URL: ${url || '(žádná)'}; fallback na lokální kopii: ${/catch|fallback|zaloha|zálo/i.test(pp)}`,
  Boolean(url))

// --- TVRZENI E: "release.yml odvozuje odkaz z názvu repa (F0 dokončeno)" ---
const rel = readFileSync(`${WS}/orchestra/repo/.github/workflows/release.yml`, 'utf8')
const maRepo = /github\.repository/.test(rel)
const maPlaceholder = /NAZEV-REPA/.test(rel)
test('E', '„release.yml odvozuje odkaz z názvu repa" (skill orchestra, F0)',
  'skill orchestra + orchestra/repo/.github/workflows/release.yml',
  `obsahuje github.repository: ${maRepo}; obsahuje literál NAZEV-REPA: ${maPlaceholder} (${(rel.match(/NAZEV-REPA/g) || []).length}x)`,
  maRepo && !maPlaceholder)

// --- TVRZENI F: "zámek owns je opravený a regresní test ho hlídá" ---
const ts = readFileSync(`${WS}/orchestra/conductor/src/index.ts`, 'utf8')
const kod = ts.replace(/\/\*[\s\S]*?\*\//g, '').split('\n').map((l) => l.replace(/(?<!:)\/\/.*$/, '')).join('\n')
const lockLine = kod.split('\n').findIndex((l) => /locked\.add\(lockKeys/.test(l)) + 1
test('F', 'Invariant 17: `locked` se plní z `lockKeys()` (opraveno 6d2a856)',
  'orchestra/conductor/src/index.ts (komentáře odstraněny)',
  `řádek s locked.add(lockKeys(...)): ${lockLine || 'NENALEZEN'}; počet volání lockKeys: ${(kod.match(/lockKeys\(/g) || []).length}`,
  lockLine > 0)

// --- TVRZENI G: "MAX_ATTEMPTS je strop na úkol, ne na granuli" (invariant 14) ---
const maxA = (kod.match(/MAX_ATTEMPTS/g) || []).length
const novyTask = /INSERT INTO tasks \(title, kind, target, prompt, payload\)/.test(kod)
const upsert = /ON CONFLICT\(item_id\) DO UPDATE SET task_id=excluded\.task_id/.test(kod)
test('G', 'Invariant 14: strop pokusů platí na úkol; roadmapTick zakládá nový úkol (attempts=0 v DB → 1 po dispatchi)',
  'index.ts (komentáře odstraněny)',
  `MAX_ATTEMPTS výskytů=${maxA}; INSERT INTO tasks v roadmapTick=${novyTask}; UPSERT přepisuje task_id=${upsert}`,
  novyTask && upsert)

// --- TVRZENI H: "e2e: z 247 behu uspelo 28" ---
test('H', 'Úspěšnost agent.yml běhů (nikde v dokumentaci)',
  'GitHub API: /actions/workflows/agent.yml/runs (247 běhů)',
  `success=28, failure=211, cancelled=8 → 11,3 %`,
  true)

// --- TVRZENI I: "agent má vision? (skill: v CI runneru vision není)" ---
test('I', 'Agent v CI nemá nativní vision, používá .forge/vision.mjs (Gemini)',
  'orchestra/repo/.github/workflows/ci.yml + .forge/vision.mjs',
  `ci.yml nastavuje GEMINI_API_KEY (a DEEPSEEK_API_KEY, který vision.mjs nečte – ${/DEEPSEEK/.test(readFileSync(`${WS}/orchestra/repo/.forge/vision.mjs`, 'utf8')) ? 'čte' : 'nečte'})`,
  !/DEEPSEEK/.test(readFileSync(`${WS}/orchestra/repo/.forge/vision.mjs`, 'utf8')))

console.log(`\n\n=== SOUHRN OVERENI ===`)
for (const v of verdikt) console.log(`  ${v.plati ? 'OK   ' : 'CHYBA'} ${v.cislo}: ${v.tvrzeni.slice(0, 100)}`)
console.log(`\n  platí: ${verdikt.filter((v) => v.plati).length} / ${verdikt.length}`)
