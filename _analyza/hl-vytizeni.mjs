// Hloubkova analyza orchestra - Q1/Q2/Q3: vytizeni, uspesnost, ekonomie.
// Cte VSECHNY behy agent.yml (workflow_dispatch = orchestra) a pocita z nich.
// Spusteni: node _analyza/hl-vytizeni.mjs
import { readFileSync, writeFileSync } from 'node:fs'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim()
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'hl-analyza' }
const REPO = 'ssevcikm-spec/uo-shadows'

async function gh(p) {
  for (let i = 0; i < 3; i++) {
    const r = await fetch('https://api.github.com' + p, { headers: H })
    if (r.status === 403 || r.status === 429) { await new Promise((s) => setTimeout(s, 3000)); continue }
    const j = await r.json()
    return j
  }
  throw new Error('rate limit ' + p)
}

// --- vsechny behy agent.yml (workflow_dispatch) ---
let all = []
for (let page = 1; page <= 4; page++) {
  const j = await gh(`/repos/${REPO}/actions/workflows/agent.yml/runs?per_page=100&page=${page}`)
  const runs = j.workflow_runs || []
  all = all.concat(runs)
  if (runs.length < 100) break
}
all.sort((a, b) => a.run_number - b.run_number)
console.log(`# agent.yml behu stazeno: ${all.length}  (API total_count=${(await gh(`/repos/${REPO}/actions/workflows/agent.yml/runs?per_page=1`)).total_count})`)
console.log(`# casove rozpeti: ${all[0]?.created_at} .. ${all[all.length - 1]?.created_at}`)

// --- rozpad podle conclusion ---
const concl = {}
for (const r of all) concl[r.conclusion || r.status] = (concl[r.conclusion || r.status] || 0) + 1
console.log(`\n== conclusion vsech behu agent.yml ==\n   ${JSON.stringify(concl)}`)

// --- behy po dnech ---
const byDay = {}
for (const r of all) {
  const d = r.created_at.slice(0, 10)
  byDay[d] = byDay[d] || { n: 0, ok: 0 }
  byDay[d].n++
  if (r.conclusion === 'success') byDay[d].ok++
}
console.log(`\n== behy agent.yml po dnech (den: behu / uspesnych) ==`)
for (const d of Object.keys(byDay).sort()) console.log(`   ${d}: ${byDay[d].n} / ${byDay[d].ok}`)

// --- task id z nazvu behu: "Forge #140 [uuid]" ---
const parse = (name) => {
  const m = String(name || '').match(/^Forge #(\d+) \[([0-9a-f-]+)\]/)
  return m ? { task: Number(m[1]), key: m[2] } : null
}

// --- kolik behu na jeden task, a jak dlouho zil ---
const byTask = new Map()
for (const r of all) {
  const p = parse(r.name)
  if (!p) continue
  if (!byTask.has(p.task)) byTask.set(p.task, [])
  byTask.get(p.task).push(r)
}
const taskIds = [...byTask.keys()].sort((a, b) => a - b)
console.log(`\n== behu na ULOHU (task) ==  uloh=${taskIds.length}`)
const dist = {}
for (const t of taskIds) {
  const n = byTask.get(t).length
  dist[n] = (dist[n] || 0) + 1
}
console.log(`   rozdeleni (behu na ulohu: pocet uloh): ${JSON.stringify(dist)}`)

// --- doba behu a mezery mezi pokusy tehoz tasku ---
let durSum = 0, durN = 0, gapSum = 0, gapN = 0
const gaps = []
for (const t of taskIds) {
  const rs = byTask.get(t).sort((a, b) => Date.parse(a.created_at) - Date.parse(b.created_at))
  for (const r of rs) {
    if (r.updated_at && r.created_at) {
      const d = (Date.parse(r.updated_at) - Date.parse(r.created_at)) / 60000
      if (d > 0) { durSum += d; durN++ }
    }
  }
  for (let i = 1; i < rs.length; i++) {
    const g = (Date.parse(rs[i].created_at) - Date.parse(rs[i - 1].created_at)) / 60000
    gapSum += g; gapN++; gaps.push({ task: t, min: g, prev: rs[i - 1].conclusion })
  }
}
console.log(`   prumerna doba behu: ${(durSum / durN).toFixed(1)} min (n=${durN})`)
gaps.sort((a, b) => a.min - b.min)
console.log(`   mezera mezi pokusy tehoz tasku: min=${gaps[0]?.min.toFixed(1)} median=${gaps[Math.floor(gaps.length / 2)]?.min.toFixed(1)} max=${gaps[gaps.length - 1]?.min.toFixed(1)} (n=${gaps.length})`)
// rozdeleni mezer: kolik je < 60 min (tj. OBESEL se cooldown)
const pod60 = gaps.filter((g) => g.min < 60).length
const pod180 = gaps.filter((g) => g.min < 180).length
console.log(`   mezer < 60 min: ${pod60} (${(100 * pod60 / gaps.length).toFixed(0)} %)  < 180 min: ${pod180} (${(100 * pod180 / gaps.length).toFixed(0)} %)`)
console.log(`   priklady nejkratsich mezer: ${JSON.stringify(gaps.slice(0, 8).map((g) => ({ task: g.task, min: +g.min.toFixed(1), po: g.prev })))}`)

// --- vytizeni: kolik casu je orchestra VIDITELNE cinná ---
// Konzervativni definice: sjednoceni intervalu [created_at, updated_at] vsech behu.
const iv = all
  .map((r) => [Date.parse(r.created_at), Date.parse(r.updated_at || r.created_at)])
  .filter(([a, b]) => b > a)
  .sort((a, b) => a[0] - b[0])
const merged = []
for (const [a, b] of iv) {
  if (merged.length && a <= merged[merged.length - 1][1]) {
    merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], b)
  } else merged.push([a, b])
}
const busyMs = merged.reduce((s, [a, b]) => s + (b - a), 0)
const spanMs = Date.parse(all[all.length - 1].updated_at) - Date.parse(all[0].created_at)
console.log(`\n== VYTIZENI (Q1) ==`)
console.log(`   okno: ${all[0].created_at} .. ${all[all.length - 1].updated_at}  = ${(spanMs / 3600e3).toFixed(1)} h`)
console.log(`   cas, kdy bezel nektery beh agent.yml: ${(busyMs / 3600e3).toFixed(2)} h = ${(100 * busyMs / spanMs).toFixed(2)} % okna`)
console.log(`   pocet souvislych bloku behu: ${merged.length}`)
const blocks = merged.map(([a, b]) => ({
  od: new Date(a).toISOString().slice(0, 16).replace('T', ' '),
  do_: new Date(b).toISOString().slice(0, 16).replace('T', ' '),
  hodin: +(((b - a) / 3600e3).toFixed(2)),
}))
console.log(`   bloky (od..do, hodin): ${JSON.stringify(blocks)}`)

// --- mezery mezi bloky (kdy orchestra NEDELALA vubec) ---
console.log(`\n== OKNA NECINNOSTI (mezery mezi bloky) ==`)
for (let i = 1; i < merged.length; i++) {
  const g = (merged[i][0] - merged[i - 1][1]) / 3600e3
  if (g > 0.5) {
    console.log(`   ${new Date(merged[i - 1][1]).toISOString().slice(0, 16).replace('T', ' ')} → ${new Date(merged[i][0]).toISOString().slice(0, 16).replace('T', ' ')}  = ${g.toFixed(2)} h`)
  }
}

// --- ekonomie: kdyz beh uspeje, kolik behu to stalo ---
const okRuns = all.filter((r) => r.conclusion === 'success')
console.log(`\n== EKONOMIE (Q2/Q3) ==`)
console.log(`   uspesnych behu: ${okRuns.length} z ${all.length} = ${(100 * okRuns.length / all.length).toFixed(1)} %`)
console.log(`   tj. 1 uspesny beh na kazdych ${(all.length / okRuns.length).toFixed(2)} spustenych`)

// --- pull requesty: merge rate a cas do mergu ---
let prAll = []
for (let page = 1; page <= 3; page++) {
  const j = await gh(`/repos/${REPO}/pulls?state=all&per_page=100&page=${page}&sort=created&direction=desc`)
  if (!Array.isArray(j) || !j.length) break
  prAll = prAll.concat(j)
  if (j.length < 100) break
}
const forgePrs = prAll.filter((p) => String(p.head?.ref || '').startsWith('forge/task-'))
const mrg = forgePrs.filter((p) => p.merged_at)
console.log(`\n== PR orchestra ==  celkem forge PR (posledni strankovani)=${forgePrs.length} sloucenych=${mrg.length} (${(100 * mrg.length / Math.max(1, forgePrs.length)).toFixed(0)} %)`)
const tt = mrg.map((p) => (Date.parse(p.merged_at) - Date.parse(p.created_at)) / 60000).sort((a, b) => a - b)
if (tt.length) console.log(`   cas od PR k mergi (min): min=${tt[0].toFixed(1)} median=${tt[Math.floor(tt.length / 2)].toFixed(1)} max=${tt[tt.length - 1].toFixed(1)}`)
const openPrs = prAll.filter((p) => p.state === 'open')
console.log(`   otevrenych PR ted: ${openPrs.length} → ${JSON.stringify(openPrs.map((p) => p.title))}`)
const closedUnmerged = forgePrs.filter((p) => p.state === 'closed' && !p.merged_at)
console.log(`   zavrenych BEZ slouceni: ${closedUnmerged.length} → ${JSON.stringify(closedUnmerged.slice(0, 8).map((p) => p.title))}`)

// --- task id v nazvech vs. PR vetve: sedi? ---
const taskIdsInPrs = new Set(forgePrs.map((p) => Number(String(p.head.ref).match(/task-(\d+)/)?.[1])))
const taskIdsInRuns = new Set(taskIds)
const prBezBehu = [...taskIdsInPrs].filter((t) => !taskIdsInRuns.has(t))
const behyBezPr = [...taskIdsInRuns].filter((t) => !taskIdsInPrs.has(t))
console.log(`\n== vazba task id: PR vs behy ==`)
console.log(`   task id v PR: ${taskIdsInPrs.size}  v nazvech behu: ${taskIdsInRuns.size}`)
console.log(`   task v PR, ktery nema beh v agent.yml: ${JSON.stringify(prBezBehu.slice(0, 20))}`)
console.log(`   task s behem, ktery nema PR: ${JSON.stringify(behyBezPr.slice(0, 30))}`)

writeFileSync(`${WS}/_analyza/hl-vytizeni.json`, JSON.stringify({
  mereno: new Date().toISOString(),
  agentRuns: all.map((r) => ({ n: r.run_number, name: r.name, conclusion: r.conclusion, created: r.created_at, updated: r.updated_at, event: r.event })),
  blocks, concl, byDay,
}, null, 1))
console.log(`\n# surova data: _analyza/hl-vytizeni.json`)
