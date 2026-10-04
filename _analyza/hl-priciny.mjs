// Hloubkova analyza orchestra - KDE presne selhava 100 behu orchestra (Q2/Q3).
// Sklada pricinu z kroků jobu: ktera brana spadla jako prvni.
// Spusteni: node _analyza/hl-priciny.mjs
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
  throw new Error('rl ' + p)
}

let runs = []
for (let page = 1; page <= 3; page++) {
  const j = await gh(`/repos/${REPO}/actions/workflows/agent.yml/runs?per_page=100&page=${page}`)
  const l = j.workflow_runs || []
  runs = runs.concat(l)
  if (l.length < 100) break
}
console.log(`# behu agent.yml: ${runs.length}`)

const priciny = {}
const detail = []
for (const r of runs) {
  const jobs = await gh(`/repos/${REPO}/actions/runs/${r.id}/jobs?per_page=50`)
  const job = (jobs.jobs || [])[0]
  if (!job) continue
  const steps = job.steps || []
  const selhal = steps.find((s) => s.conclusion === 'failure')
  const klic = selhal ? selhal.name : (r.conclusion === 'success' ? 'USPECH (zadny krok neselhal)' : `jiny: ${r.conclusion}`)
  priciny[klic] = (priciny[klic] || 0) + 1
  // cas v kroku agenta
  const ag = steps.find((s) => /Spusť agenta/.test(s.name))
  const trv = (ag && ag.started_at && ag.completed_at) ? (Date.parse(ag.completed_at) - Date.parse(ag.started_at)) / 1000 : null
  detail.push({ run: r.run_number, concl: r.conclusion, krok: klic, agent_s: trv,
                kroky_fail: steps.filter((s) => s.conclusion === 'failure').map((s) => s.name) })
}
console.log(`\n=== PRVNI SELHANY KROK (rozpad vsech behu) ===`)
for (const [k, v] of Object.entries(priciny).sort((a, b) => b[1] - a[1])) {
  console.log(`  ${String(v).padStart(3)}x  ${k}`)
}
const uspech = detail.filter((d) => d.concl === 'success')
const selh = detail.filter((d) => d.concl === 'failure')
const prum = (a) => a.length ? (a.reduce((s, x) => s + (x.agent_s || 0), 0) / a.length).toFixed(0) : '-'
console.log(`\n=== CAS V KROKU 'Spusť agenta' ===`)
console.log(`  uspesne behy (${uspech.length}): prumer ${prum(uspech)} s   median ${uspech.map((x) => x.agent_s || 0).sort((a, b) => a - b)[Math.floor(uspech.length / 2)]} s`)
console.log(`  selhane behy (${selh.length}): prumer ${prum(selh)} s   median ${selh.map((x) => x.agent_s || 0).sort((a, b) => a - b)[Math.floor(selh.length / 2)]} s`)
const kratke = selh.filter((x) => (x.agent_s || 0) < 30)
console.log(`  selhane behy s krokem agenta < 30 s (agent skoro nic neudelal): ${kratke.length} z ${selh.length} = ${(100 * kratke.length / Math.max(1, selh.length)).toFixed(0)} %`)
writeFileSync(`${WS}/_analyza/hl-priciny.json`, JSON.stringify(detail, null, 1))
console.log(`# data: _analyza/hl-priciny.json`)
