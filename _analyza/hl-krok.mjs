// Hloubkova analyza orchestra - detail jednoho behu po KROCICH.
// Kazdy krok ma vlastni log; hledame, kde presne beh selhal a co brana rekla.
// Spusteni: node _analyza/hl-krok.mjs [run_number] [slovo v nazvu kroku]
import { readFileSync, writeFileSync } from 'node:fs'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim()
const GH = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'hl-analyza' }
const REPO = 'ssevcikm-spec/uo-shadows'
const CISLO = Number(process.argv[2] || 243)
const SLOVO = process.argv[3] || 'parsov'

async function gh(p, raw = false) {
  for (let i = 0; i < 4; i++) {
    const r = await fetch('https://api.github.com' + p, { headers: raw ? { ...GH, Accept: 'application/vnd.github.raw' } : GH })
    if (r.status === 403 || r.status === 429) { await new Promise((s) => setTimeout(s, 4000)); continue }
    if (raw) return { status: r.status, text: await r.text() }
    return { status: r.status, j: await r.json() }
  }
  throw new Error('rl')
}

const all = await gh(`/repos/${REPO}/actions/workflows/agent.yml/runs?per_page=100`)
const run = (all.j.workflow_runs || []).find((r) => r.run_number === CISLO)
const jobs = await gh(`/repos/${REPO}/actions/runs/${run.id}/jobs?per_page=50`)
const job = (jobs.j.jobs || [])[0]
console.log(`# beh #${run.run_number} ${run.conclusion}  ${run.name}`)
console.log(`# job ${job.id} ${job.name} ${job.conclusion}`)

for (const s of job.steps || []) {
  console.log(`   ${String(s.number).padStart(2)}. ${s.name} → ${s.conclusion}  (${s.started_at} .. ${s.completed_at})`)
}

const cil = (job.steps || []).find((s) => new RegExp(SLOVO, 'i').test(s.name))
if (!cil) { console.log(`# krok s '${SLOVO}' nenalezen`); process.exit(0) }

const log = await gh(`/repos/${REPO}/actions/jobs/${job.id}/logs`, true)
const t = log.text || ''
// rozdel log na bloky podle ##[group]
const idx = t.indexOf(`##[group]Run`)
console.log(`\n# hledam v logu jobu vsechny bloky; hledany krok: "${cil.name}"`)
const bloky = t.split(/\n(?=\d{4}-\d\d-\d\dT)/)
// najdi posledni vyskyt nazvu kroku
const pozice = []
for (let i = 0; i < bloky.length; i++) if (bloky[i].includes(cil.name)) pozice.push(i)
console.log(`# vyskytu nazvu kroku v logu: ${pozice.length}`)
if (pozice.length) {
  const start = pozice[pozice.length - 1]
  console.log(`\n===== LOG KROKU (od posledniho vyskytu) =====`)
  for (const l of bloky.slice(start, start + 80)) console.log('   ' + l.replace(/^\S+Z\s?/, '').slice(0, 170))
}

// jeste hledej klicova slova v celem logu
console.log(`\n===== KLICOVA SLOVA V CELEM LOGU =====`)
for (const re of [/CHYBA[^\n]{0,120}/g, /parse error[^\n]{0,100}/gi, /GDScript[^\n]{0,100}/g,
                  /SyntaxError[^\n]{0,100}/g, /::error[^\n]{0,120}/g, /selhal[^\n]{0,120}/gi,
                  /Expected[^\n]{0,100}/g, /Unexpected[^\n]{0,100}/g]) {
  const m = t.match(re)
  if (m) console.log(`   ${re.source}: ${m.length}x  napr. ${JSON.stringify(m.slice(0, 3).map((x) => x.slice(0, 130)))}`)
}
writeFileSync(`${WS}/_analyza/tmp-log-${CISLO}-${SLOVO}.txt`, t)
console.log(`\n# cely log: _analyza/tmp-log-${CISLO}-${SLOVO}.txt`)
