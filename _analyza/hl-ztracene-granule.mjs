// Overuje: byly granule core.attributes a entity.item NĚKDY dispatchované?
// (mají PR, ale nemají řádek v D1 → jejich stav se ztratil)
// A existuje pro ne "zachranna cesta" párování PR podle názvu?
// Jen čtení. Spusteni: node _analyza/hl-ztracene-granule.mjs
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

const rm = JSON.parse(readFileSync(`${WS}/games/uo-shadows/.forge/roadmap.json`, 'utf8'))
const d1 = JSON.parse(readFileSync(`${WS}/_analyza/tmp-roadmap-d1.json`, 'utf8')).roadmap
const maRadku = new Set(d1.map((x) => String(x.item_id).split('/').slice(1).join('/')))

// vsechny PR v repu (strankovane) - hledame podle VETVE i podle NAZVU
let prs = []
for (let page = 1; page <= 3; page++) {
  const j = await gh(`/repos/${REPO}/pulls?state=all&per_page=100&page=${page}&sort=created&direction=desc`)
  if (!Array.isArray(j) || !j.length) break
  prs = prs.concat(j)
  if (j.length < 100) break
}
console.log(`# PR v repu (strankovano): ${prs.length}`)
const otevreneNeboZavrene = prs.length

// "zachranna cesta" v roadmapTick cte JEN poslednich 100 zavrenych PR
const zavrene = await gh(`/repos/${REPO}/pulls?state=closed&per_page=100&sort=updated&direction=desc`)
const titulkyZachrana = new Set(zavrene.filter((p) => p.merged_at)
  .map((p) => String(p.title).replace(/^Forge #\d+:\s*/, '')))
console.log(`# zavřených PR stažených pro záchranu: ${zavrene.length} (limit API), z toho sloučených ${zavrene.filter((p) => p.merged_at).length}`)
console.log(`# nejstarší z nich: PR #${Math.min(...zavrene.map((p) => p.number))}\n`)

console.log('granule             | D1 řádek | PR (podle větve)         | název v záchraně | verdikt')
for (const g of rm.grains) {
  const podleVetve = prs.filter((p) => String(p.head?.ref || '').match(new RegExp(`^forge/task-\\d+$`)) &&
    String(p.title).replace(/^Forge #\d+:\s*/, '') === g.title)
  const vZachrane = titulkyZachrana.has(g.title)
  const ma = maRadku.has(g.id)
  let verdikt = ''
  if (podleVetve.length && !ma) verdikt = '← PR existuje, ale D1 řádek NENÍ'
  else if (vZachrane && !ma && g.done !== true) verdikt = '← záchrana podle názvu by ho zachránila'
  else if (!ma && g.done !== true) verdikt = '← NIKDE: čeká na nové vydání'
  console.log(`  ${g.id.padEnd(18)} | ${String(ma ? 'ANO' : 'NE').padEnd(8)} | ${String(podleVetve.map((p) => `#${p.number}${p.merged_at ? '✓' : ''}`).join(',') || '-').padEnd(24)} | ${String(vZachrane).padEnd(16)} | ${verdikt}`)
}

console.log('\n# co je "zachranna cesta": roadmapTick páruje PR podle TITULKU granule')
console.log('#   (index.ts:502-503). Funguje jen pro PR v posledních 100 zavřených.')
console.log(`#   Dnes staženo zavřených PR: ${zavrene.length}; nejstarší #${Math.min(...zavrene.map((p) => p.number))}.`)
