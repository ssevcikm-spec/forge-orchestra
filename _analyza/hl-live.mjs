// Hloubkova analyza orchestra - LIVE mereni conductora a GitHubu.
// Spusteni: node _analyza/hl-live.mjs
// Node fetch (TLS z PowerShellu nefunguje). PAT se nikdy nevypisuje.
import { readFileSync } from 'node:fs'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const env = Object.fromEntries(
  readFileSync(`${WS}/orchestra/.env`, 'utf8').split(/\r?\n/)
    .filter((l) => l.includes('=') && !l.trim().startsWith('#'))
    .map((l) => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]),
)
const URLB = env.FORGE_URL.replace(/\/$/, '')
const H = { 'x-forge-secret': env.FORGE_SECRET }
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim()
const GH = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'hl-analyza' }

const ts = new Date().toISOString()
console.log(`# mereno ${ts}  (node ${process.version})`)
console.log(`# conductor: ${URLB}`)

async function get(p, h = H) {
  const r = await fetch(URLB + p, { headers: h })
  const t = await r.text()
  let j = null
  try { j = JSON.parse(t) } catch { /* */ }
  return { status: r.status, j, t }
}

async function gh(p) {
  const r = await fetch('https://api.github.com' + p, { headers: GH })
  const t = await r.text()
  try { return { status: r.status, j: JSON.parse(t) } } catch { return { status: r.status, j: null, t } }
}

const out = {}

// ---------- conductor ----------
const health = await get('/health', {})
out.health = health.j
console.log(`\n== /health (VEREJNY, bez secretu) ==\n${JSON.stringify(health.j)}`)

for (const p of ['/games', '/roadmap', '/failed', '/queue', '/workers']) {
  const r = await get(p)
  out[p] = r.j
  if (p === '/games') console.log(`\n== /games ==\n${JSON.stringify(r.j, null, 1)}`)
  if (p === '/roadmap') {
    const rows = r.j?.roadmap || []
    const byStatus = {}
    const perGame = {}
    for (const row of rows) {
      byStatus[row.status] = (byStatus[row.status] || 0) + 1
      const g = String(row.item_id).split('/')[0]
      perGame[g] = (perGame[g] || 0) + 1
    }
    console.log(`\n== /roadmap == radku=${rows.length}`)
    console.log(`   podle status: ${JSON.stringify(byStatus)}`)
    console.log(`   podle hry:    ${JSON.stringify(perGame)}`)
    console.log(`   ukazka: ${JSON.stringify(rows.slice(0, 6))}`)
    const now = Date.now()
    const ages = rows.map((x) => (now - Date.parse(String(x.updated_at).replace(' ', 'T') + 'Z')) / 3600e3)
    ages.sort((a, b) => a - b)
    if (ages.length) {
      console.log(`   stari radku updated_at (h): min=${ages[0].toFixed(2)} median=${ages[Math.floor(ages.length / 2)].toFixed(2)} max=${ages[ages.length - 1].toFixed(2)}`)
    }
  }
  if (p === '/failed') {
    const t = r.j?.tasks || []
    console.log(`\n== /failed == uloh=${t.length}`)
    for (const x of t.slice(0, 10)) {
      console.log(`   #${x.id} ${x.status} attempts=${x.attempts} grain=${JSON.parse(x.payload || '{}').grain} behu=${(x.runs || []).length}`)
    }
  }
  if (p === '/queue') {
    const t = r.j?.tasks || []
    const byStatus = {}
    for (const x of t) byStatus[x.status] = (byStatus[x.status] || 0) + 1
    console.log(`\n== /queue == (LIMIT 50) uloh=${t.length} status=${JSON.stringify(byStatus)}`)
  }
  if (p === '/workers') {
    console.log(`\n== /workers ==\n${JSON.stringify(r.j?.workers, null, 1)}`)
  }
}

// ---------- GitHub: orchestrova repo ----------
console.log('\n############ GITHUB ############')
const repoGame = 'ssevcikm-spec/uo-shadows'
const rInfo = await gh(`/repos/${repoGame}`)
console.log(`\n== repo ${repoGame} ==  pushed_at=${rInfo.j?.pushed_at}  default=${rInfo.j?.default_branch}`)

// vsechny behy (vcetne cron) - pozor na citac: total_count je pocet vsech behu
const runs = await gh(`/repos/${repoGame}/actions/runs?per_page=100`)
console.log(`\n== actions/runs?per_page=100 ==  total_count=${runs.j?.total_count} (VSECHNY behy tohoto repa)`)
const list = runs.j?.workflow_runs || []
const byWf = {}
for (const r of list) byWf[r.name] = (byWf[r.name] || 0) + 1
console.log(`   poslednich 100 podle workflow: ${JSON.stringify(byWf)}`)

// agent.yml = behy orchestra (workflow_dispatch)
const agentRuns = await gh(`/repos/${repoGame}/actions/workflows/agent.yml/runs?per_page=100`)
console.log(`\n== agent.yml runs ==  total_count=${agentRuns.j?.total_count} (pocet behu agent.yml)`)
const ar = agentRuns.j?.workflow_runs || []
const concl = {}
for (const r of ar) concl[r.conclusion || r.status] = (concl[r.conclusion || r.status] || 0) + 1
console.log(`   poslednich ${ar.length} podle conclusion: ${JSON.stringify(concl)}`)
const dt = ar.map((r) => r.created_at).sort()
if (dt.length) console.log(`   casove rozpeti poslednich ${ar.length}: ${dt[0]} .. ${dt[dt.length - 1]}`)

// volani modelu: z logu poslednich behu vytahneme tokeny/model
console.log('\n== ekonomie: tokeny a model z poslednich behu ==')
const s = ar.slice(0, 12)
for (const r of s) {
  const jobs = await gh(`/repos/${repoGame}/actions/runs/${r.id}/jobs?per_page=50`)
  const jl = jobs.j?.jobs || []
  const total = jl.reduce((a, x) => a + (x.steps || []).length, 0)
  console.log(`   #${r.run_number} ${r.conclusion} ${r.created_at} steps=${total} name="${(r.name || '').slice(0, 40)}"`)
}

// pull requesty: kdo je sloucil (prirazeni = tvrzeni)
console.log('\n== PR: merged_by (kdo sloucil) ==')
const prs = await gh(`/repos/${repoGame}/pulls?state=closed&per_page=30&sort=updated&direction=desc`)
const merged = (prs.j || []).filter((p) => p.merged_at)
console.log(`   z poslednich ${(prs.j || []).length} zavrenych PR je sloucenych ${merged.length}`)
const byUser = {}
for (const p of merged) byUser[p.merged_by?.login || '?'] = (byUser[p.merged_by?.login || '?'] || 0) + 1
console.log(`   merged_by: ${JSON.stringify(byUser)}`)
const titles = merged.map((p) => p.title)
console.log(`   poslednich 5 sloucenych: ${JSON.stringify(titles.slice(0, 5))}`)

// CI hry na main
console.log('\n== CI hry na main (stav CILE) ==')
const ci = await gh(`/repos/${repoGame}/actions/workflows/ci.yml/runs?branch=main&per_page=20`)
const cir = ci.j?.workflow_runs || []
const ciconcl = {}
for (const r of cir) ciconcl[r.conclusion || r.status] = (ciconcl[r.conclusion || r.status] || 0) + 1
console.log(`   poslednich ${cir.length}: ${JSON.stringify(ciconcl)}`)
for (const r of cir.slice(0, 5)) console.log(`   #${r.run_number} ${r.conclusion} ${r.created_at} head=${(r.head_sha || '').slice(0, 7)}`)

// jak casto orchestra pracuje: kdy vznikaly behy agent.yml
console.log('\n== aktivita: behy agent.yml po hodinach (poslednich 100) ==')
const hours = {}
for (const r of ar) {
  const h = r.created_at.slice(0, 13)
  hours[h] = (hours[h] || 0) + 1
}
console.log('   ' + JSON.stringify(hours))

// release.yml
const rel = await gh(`/repos/${repoGame}/actions/workflows/release.yml/runs?per_page=5`)
console.log('\n== release.yml (poslednich 5) ==')
for (const r of (rel.j?.workflow_runs || [])) console.log(`   #${r.run_number} ${r.conclusion} ${r.created_at} head=${(r.head_sha || '').slice(0, 7)}`)
