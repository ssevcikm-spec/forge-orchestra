// Hloubkova analyza orchestra - Q5: je sablona nezavisla na hre?
// Provede instalaci sablony do docasne slozky ve workspace (mimo oba repy)
// a zmeri, co v novem "repu" zustane odvozene z NUDY / z jine hry.
// Spusteni: node _analyza/hl-instal.mjs
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync, readdirSync, statSync } from 'node:fs'
import { join } from 'node:path'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const TPL = `${WS}/orchestra/repo`
const OUT = `${WS}/_analyza/tmp-nova-hra`

rmSync(OUT, { recursive: true, force: true })
mkdirSync(OUT, { recursive: true })

// replika toho, co dela install-into-repo.ps1 (Copy-Item repo\<from>\* <to> -Recurse)
// pro dvojice, ktere skript uvadi; zkopirujume .forge a .github a korenove soubory.
function copyRec(from, to) {
  mkdirSync(to, { recursive: true })
  for (const e of readdirSync(from, { withFileTypes: true })) {
    const f = join(from, e.name), t = join(to, e.name)
    if (e.isDirectory()) copyRec(f, t)
    else writeFileSync(t, readFileSync(f))
  }
}
copyRec(`${TPL}/.forge`, `${OUT}/.forge`)
copyRec(`${TPL}/.github`, `${OUT}/.github`)
for (const f of readdirSync(TPL)) {
  if (f === '.forge' || f === '.github') continue
  const s = statSync(join(TPL, f))
  if (s.isFile()) writeFileSync(join(OUT, f), readFileSync(join(TPL, f)))
}

const all = []
;(function w(d) {
  for (const e of readdirSync(d, { withFileTypes: true })) {
    const p = join(d, e.name)
    if (e.isDirectory()) w(p); else all.push(p)
  }
})(OUT)
console.log(`# instalace sablony do ${OUT.replace(WS + '/', '')}: souboru=${all.length}`)

// --- 1) zustaly v novem repu literalni placeholdery / odkazy na cizi hru? ---
const VZORY = [
  ['NAZEV-REPA', /NAZEV-REPA/g],
  ['uo-shadows', /uo-shadows/g],
  ['forge-quest', /forge-quest/g],
  ['ssevcikm-spec', /ssevcikm-spec/g],
  ['gameforge', /gameforge/i],
]
console.log(`\n== 1) CO ZUSTALO V NOVEM REPU (poctive zkopirovane) ==`)
for (const [nazev, re] of VZORY) {
  let souboru = 0, vyskytu = 0
  const kde = []
  for (const f of all) {
    const t = readFileSync(f, 'utf8')
    const m = t.match(re)
    if (m) { souboru++; vyskytu += m.length; kde.push(`${f.replace(OUT + '\\', '').replace(OUT + '/', '')}(${m.length})`) }
  }
  console.log(`   ${nazev.padEnd(14)} souboru=${souboru} vyskytu=${vyskytu}  ${kde.slice(0, 6).join(' ')}`)
}

// --- 2) absolutni cesty na tuto stanici ---
console.log(`\n== 2) ABSOLUTNI CESTY V NOVEM REPU ==`)
let abs = 0
for (const f of all) {
  const t = readFileSync(f, 'utf8')
  const m = t.match(/[A-Z]:[\\/]Users[\\/][^\s'")]+/g)
  if (m) { abs += m.length; console.log(`   ${f.replace(OUT + '\\', '')}: ${m.length}x napr. ${m[0].slice(0, 60)}`) }
}
console.log(`   celkem vyskytu absolutnich cest: ${abs}`)

// --- 3) co je v sablone MRTVE pro novou hru (odkazy na soubory, ktere v ni nejsou) ---
console.log(`\n== 3) SOUBORY, NA KTERE SE SABLONA ODKAZUJE ==`)
const jmena = new Set(all.map((f) => f.replace(OUT + '\\', '').replace(/\\/g, '/')))
const odkazy = new Map()
for (const f of all) {
  if (!/\.(mjs|py|yml|yaml|sh|ps1)$/.test(f)) continue
  const t = readFileSync(f, 'utf8')
  for (const m of t.matchAll(/['"`]([.\w/-]+\.(?:mjs|py|json|yml|yaml|sh|gd|tscn))['"`]/g)) {
    const c = m[1]
    if (c.startsWith('.')) continue
    if (!odkazy.has(c)) odkazy.set(c, new Set())
    odkazy.get(c).add(f.replace(OUT + '\\', '').replace(/\\/g, '/'))
  }
}
const chybi = [...odkazy.entries()].filter(([c]) => !jmena.has(c) && !jmena.has('node/' + c) && ![...jmena].some((x) => x.endsWith('/' + c)))
for (const [c, kde] of chybi.sort()) {
  console.log(`   CHYBI v novem repu: ${c}  (odkazuje ${[...kde].slice(0, 3).join(', ')})`)
}
console.log(`   celkem odkazu na neexistujici soubory: ${chybi.length}`)

// --- 4) roadmap.json: co v ni je po instalaci ---
const rm = JSON.parse(readFileSync(`${OUT}/.forge/roadmap.json`, 'utf8'))
console.log(`\n== 4) ROADMAP V NOVEM REPU == grains=${(rm.grains || []).length}`)

// --- 5) vision-profile.json: co v nem je po instalaci ---
const vp = JSON.parse(readFileSync(`${OUT}/.forge/vision-profile.json`, 'utf8'))
const real = Object.keys(vp).filter((k) => !k.startsWith('_'))
console.log(`== 5) VISION-PROFILE V NOVEM REPU ==`)
console.log(`   dokumentacnich klicu (_x): ${Object.keys(vp).filter((k) => k.startsWith('_')).length}`)
console.log(`   konfiguracnich klicu:      ${real.length} → ${real.join(', ')}`)
console.log(`   hra=${JSON.stringify(vp.hra)}  map={${Object.keys(vp.mapa || {}).join(',')}}`)

// --- 6) release.yml: odkaz na hru ---
const rel = readFileSync(`${OUT}/.github/workflows/release.yml`, 'utf8')
console.log(`\n== 6) release.yml V NOVEM REPU ==`)
for (const [i, l] of rel.split('\n').entries()) {
  if (/NAZEV-REPA|github\.repository|github\.io|echo/.test(l)) console.log(`   :${i + 1}  ${l.trim().slice(0, 140)}`)
}

// --- 7) .env soubory: co po instalaci chybi ---
console.log(`\n== 7) TAJEMSTVI A .env V NOVEM REPU ==`)
for (const p of ['.forge/node/.env', '.forge/provider.env', '.forge/provider.json', '.gitignore', '.gitattributes']) {
  const fp = join(OUT, p)
  console.log(`   ${p}: ${existsSync(fp) ? 'JE (' + readFileSync(fp).length + ' B)' : 'CHYBI'}`)
}
const gi = existsSync(join(OUT, '.gitignore')) ? readFileSync(join(OUT, '.gitignore'), 'utf8') : ''
console.log(`   .gitignore obsahuje .env: ${/\.env/.test(gi)}   provider.env: ${/provider\.env/.test(gi)}`)

console.log(`\n# vystup zustava v workspace: ${OUT.replace(WS + '/', '')} (da se smazat)`)
