// Hloubkova analyza orchestra - detail tasku, ktere prekrocily MAX_ATTEMPTS=5.
// Spusteni: node _analyza/hl-strop.mjs
import { readFileSync, writeFileSync } from 'node:fs'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim()
const GH = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'hl-analyza' }
const REPO = 'ssevcikm-spec/uo-shadows'

async function gh(p) {
  for (let i = 0; i < 3; i++) {
    const r = await fetch('https://api.github.com' + p, { headers: GH })
    if (r.status === 403 || r.status === 429) { await new Promise((s) => setTimeout(s, 2500)); continue }
    return r.json()
  }
  throw new Error('rate limit')
}

const data = JSON.parse(readFileSync(`${WS}/_analyza/hl-vytizeni.json`, 'utf8'))
const runs = data.agentRuns.map((r) => ({ ...r, t: Date.parse(r.created), u: Date.parse(r.updated) }))
const byTask = new Map()
for (const r of runs) {
  const m = String(r.name || '').match(/^Forge #(\d+)/)
  if (!m) continue
  const id = Number(m[1])
  if (!byTask.has(id)) byTask.set(id, [])
  byTask.get(id).push(r)
}

// tasky, ktere maji vic behu, nez je MAX_ATTEMPTS (5)
const podezrele = [...byTask.entries()].filter(([, v]) => v.length > 5).sort((a, b) => a[1][0].t - b[1][0].t)
console.log(`# MAX_ATTEMPTS v kodu = 5 (wrangler.toml:55). Tasku s VIC nez 5 behy: ${podezrele.length}`)
const iso = (ms) => new Date(ms).toISOString().slice(0, 19).replace('T', ' ')

for (const [id, v] of podezrele.slice(0, 6)) {
  v.sort((a, b) => a.t - b.t)
  console.log(`\n===== task #${id}: ${v.length} behu =====`)
  // detail prvniho behu: inputs workflowu (payload) a joby
  for (const r of v) {
    const d = await gh(`/repos/${REPO}/actions/runs/${r.id ?? ''}`)
    const rn = r.n ?? r.run_number
    // run_number je v datech; id potrebujeme - dohledame pres seznam
    console.log(`   #${rn}  ${iso(r.t)} → ${iso(r.u)}  ${r.conclusion}  (${((r.u - r.t) / 60000).toFixed(1)} min)`)
  }
}

// ---- detail behu: ziskej id a inputs (payload) pro vybrane tasky ----
console.log(`\n# ===== DETAIL: zadani a prubeh prvniho a posledniho behu =====`)
let all = []
for (let page = 1; page <= 3; page++) {
  const j = await gh(`/repos/${REPO}/actions/workflows/agent.yml/runs?per_page=100&page=${page}`)
  const l = j.workflow_runs || []
  all = all.concat(l)
  if (l.length < 100) break
}
const detail = new Map(all.map((r) => [r.run_number, r]))
const ukazkove = [podezrele[0], podezrele[podezrele.length - 1]].filter(Boolean)
for (const [id, v] of ukazkove) {
  v.sort((a, b) => a.t - b.t)
  const first = detail.get(v[0].n)
  console.log(`\n--- task #${id}, beh #${v[0].n} (prvni) ---`)
  console.log(`   name: ${first?.name}`)
  console.log(`   event: ${first?.event}  attempt: ${first?.run_attempt}  head: ${first?.head_branch}`)
  const jobs = await gh(`/repos/${REPO}/actions/runs/${first?.id}/jobs?per_page=50`)
  const job = (jobs.jobs || [])[0]
  if (job) {
    console.log(`   job: ${job.name} → ${job.conclusion}`)
    for (const s of job.steps || []) console.log(`      ${s.number}. ${s.name} → ${s.conclusion}`)
  }
}

// ---- kolik behu ma stejny payload? (dispatch s jinym pokusem = stejny task) ----
console.log(`\n# ===== ROZDELENI: pocet behu na ulohu =====`)
const dist = {}
for (const [, v] of byTask) dist[v.length] = (dist[v.length] || 0) + 1
console.log(JSON.stringify(dist))
const nad5 = [...byTask.values()].filter((v) => v.length > 5)
console.log(`# behu v tasich s >5 behy: ${nad5.reduce((s, v) => s + v.length, 0)} z ${runs.length} = ${(100 * nad5.reduce((s, v) => s + v.length, 0) / runs.length).toFixed(0)} %`)
console.log(`# prumerny pocet behu na ulohu: ${(runs.length / byTask.size).toFixed(2)}`)
