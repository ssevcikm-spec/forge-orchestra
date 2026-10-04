// Hloubkova analyza orchestra - Q1: OKNA NECINNOSTI a jejich pricina.
// Krizove overuje: mezery v behu agent.yml vs. selhani CI hry na main vs. stav fronty.
// Spusteni: node _analyza/hl-okna.mjs
import { readFileSync } from 'node:fs'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim()
const GH = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'hl-analyza' }
const REPO = 'ssevcikm-spec/uo-shadows'
const env = Object.fromEntries(
  readFileSync(`${WS}/orchestra/.env`, 'utf8').split(/\r?\n/)
    .filter((l) => l.includes('=') && !l.trim().startsWith('#'))
    .map((l) => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]),
)

async function gh(p) {
  const r = await fetch('https://api.github.com' + p, { headers: GH })
  return r.json()
}

// --- behy agent.yml (uz stazene v hl-vytizeni.json) ---
const data = JSON.parse(readFileSync(`${WS}/_analyza/hl-vytizeni.json`, 'utf8'))
const runs = data.agentRuns.map((r) => ({ ...r, t: Date.parse(r.created), u: Date.parse(r.updated) }))
  .sort((a, b) => a.t - b.t)

// --- behy CI na main (stav CILE) ---
let ci = []
for (let page = 1; page <= 3; page++) {
  const j = await gh(`/repos/${REPO}/actions/workflows/ci.yml/runs?branch=main&per_page=100&page=${page}`)
  const l = j.workflow_runs || []
  ci = ci.concat(l)
  if (l.length < 100) break
}
ci = ci.map((r) => ({ n: r.run_number, c: r.conclusion, t: Date.parse(r.created_at), u: Date.parse(r.updated_at), sha: (r.head_sha || '').slice(0, 7) }))
  .sort((a, b) => a.t - b.t)
const ciFail = ci.filter((x) => x.c === 'failure')
console.log(`# CI behu na main: ${ci.length} (${ci[0]?.t ? new Date(ci[0].t).toISOString() : '?'} .. ${ci[ci.length - 1]?.t ? new Date(ci[ci.length - 1].t).toISOString() : '?'})`)
console.log(`# CI failure: ${ciFail.length} → ${JSON.stringify(ciFail.map((x) => `#${x.n} ${new Date(x.t).toISOString().slice(0, 16)} ${x.sha}`))}`)

// --- casova osa: pro kazdou mezeru v behu agent.yml zjisti stav CI ---
const merged = []
for (const r of runs) {
  if (merged.length && r.t <= merged[merged.length - 1][1]) merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], r.u)
  else merged.push([r.t, r.u])
}
console.log(`\n== OKNA NECINNOSTI vs. stav CI na main ==`)
console.log(`(stav CI = posledni beh ci.yml na main, ktery v tu chvili DOBEHL; cerveny = 'main je rozbity')`)
const iso = (ms) => new Date(ms).toISOString().slice(0, 16).replace('T', ' ')
let sumGap = 0
for (let i = 1; i < merged.length; i++) {
  const from = merged[i - 1][1], to = merged[i][0]
  const h = (to - from) / 3600e3
  if (h < 0.5) continue
  sumGap += h
  // posledni DOKONCENY beh CI pred 'from'
  const last = ci.filter((x) => x.u <= from).pop()
  // stav CI v prubehu okna
  const during = ci.filter((x) => x.t >= from && x.t <= to)
  const cerveny = last && last.c === 'failure'
  console.log(`\n  ${iso(from)} → ${iso(to)}  = ${h.toFixed(2)} h`)
  console.log(`     stav CI na zacatku okna: ${last ? `#${last.n} ${last.c}` : 'zadny beh'}   → ${cerveny ? 'CILE BYLO CERVENE' : 'cil zeleny'}`)
  if (during.length) console.log(`     behu CI behem okna: ${during.map((x) => `#${x.n}:${x.c}`).join(' ')}`)
}
console.log(`\n# soucet vsech oken necinnosti (>0.5 h): ${sumGap.toFixed(2)} h`)
const span = (runs[runs.length - 1].u - runs[0].t) / 3600e3
console.log(`# okno celkem: ${span.toFixed(2)} h → necinnost ${(100 * sumGap / span).toFixed(1)} %`)

// --- co delal conductor: rutime stavy fronty pres /roadmap neni historie, takze
//     bereme merene pokusy z nazvu behu (task id) a hledame, kdy ktery task žil ---
const byTask = new Map()
for (const r of runs) {
  const m = String(r.name || '').match(/^Forge #(\d+)/)
  if (!m) continue
  const id = Number(m[1])
  if (!byTask.has(id)) byTask.set(id, [])
  byTask.get(id).push(r)
}
// --- rozpad na VLNY pokusu: task, ktery ma 5 pokusu, je jedna vlna; novy task
//     na touz granuli je vlna dalsi. Granuli poznáme jen z PR/nazvu, proto
//     ukazujeme casove hranice vln u tasku s >=4 pokusy. ---
console.log(`\n== VLNY POKUSU (tasky s >= 4 behy) ==`)
const vlny = [...byTask.entries()].filter(([, v]) => v.length >= 4).sort((a, b) => a[1][0].t - b[1][0].t)
for (const [id, v] of vlny) {
  const a = v[0].t, b = v[v.length - 1].u
  console.log(`  task #${id}: ${v.length} behu, ${iso(a)} → ${iso(b)} = ${((b - a) / 60000).toFixed(1)} min, vysledky: ${v.map((x) => x.conclusion).join(',')}`)
}
console.log(`# tasku celkem: ${byTask.size}, z toho s >=4 behy: ${vlny.length}`)
const totalRuns = runs.length
console.log(`# behu celkem: ${totalRuns}`)
const vsechnyVlny = [...byTask.entries()].filter(([, v]) => v.length >= 3)
console.log(`# tasku s >=3 behy: ${vsechnyVlny.length}; jejich behu: ${vsechnyVlny.reduce((s, [, v]) => s + v.length, 0)} (${(100 * vsechnyVlny.reduce((s, [, v]) => s + v.length, 0) / totalRuns).toFixed(0)} % vsech behu)`)
