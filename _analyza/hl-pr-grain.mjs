// Zjisti, ktere PR patri ktere granularni polozce (podle vetve forge/task-<id>).
// Vystup: task -> {pr, merged_at, title}. Jen cteni.
// Spusteni: node _analyza/hl-pr-grain.mjs
import { readFileSync, writeFileSync } from 'node:fs'

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

let prs = []
for (let page = 1; page <= 3; page++) {
  const j = await gh(`/repos/${REPO}/pulls?state=all&per_page=100&page=${page}&sort=created&direction=desc`)
  if (!Array.isArray(j) || !j.length) break
  prs = prs.concat(j)
  if (j.length < 100) break
}
const forge = prs.filter((p) => String(p.head?.ref || '').startsWith('forge/task-'))
console.log(`# forge PR celkem (strankovano): ${forge.length}, sloucenych: ${forge.filter((p) => p.merged_at).length}`)

// task_id z nazvu vetve
const podleTasku = new Map()
for (const p of forge) {
  const m = String(p.head.ref).match(/task-(\d+)/)
  if (!m) continue
  const id = Number(m[1])
  if (!podleTasku.has(id)) podleTasku.set(id, [])
  podleTasku.get(id).push({ pr: p.number, merged_at: p.merged_at, title: p.title, state: p.state })
}
console.log('\n# task -> PR (serazeno podle cisla PR)')
const vysledek = {}
for (const [id, seznam] of [...podleTasku.entries()].sort((a, b) => a[0] - b[0])) {
  const sloucene = seznam.filter((x) => x.merged_at)
  console.log(`  task #${String(id).padStart(3)} → ${seznam.map((x) => `PR #${x.pr}${x.merged_at ? ' (merged ' + x.merged_at.slice(0, 10) + ')' : ' (' + x.state + ')'}`).join(', ')}`)
  console.log(`              ${seznam[0].title.slice(0, 90)}`)
  vysledek[id] = seznam
}
writeFileSync(`${WS}/_analyza/hl-pr-grain.json`, JSON.stringify(vysledek, null, 1))
console.log(`\n# data: _analyza/hl-pr-grain.json`)

// --- a jeste: shoduji se NAZVY granul s nazvy sloucenych PR? (to je zachranna cesta) ---
const rm = JSON.parse(readFileSync(`${WS}/games/uo-shadows/.forge/roadmap.json`, 'utf8'))
const titulkyPR = new Set(forge.filter((p) => p.merged_at).map((p) => String(p.title).replace(/^Forge #\d+:\s*/, '')))
console.log(`\n# shoda nazvu granul s nazvy sloucenych PR (zachranna cesta v roadmapTick):`)
for (const g of rm.grains) {
  const shoda = titulkyPR.has(g.title)
  console.log(`  ${shoda ? 'SHODA ' : '      '} ${g.id.padEnd(18)} ${g.done === true ? '(done:true)' : ''}`)
}
