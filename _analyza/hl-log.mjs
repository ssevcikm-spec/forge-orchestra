// Hloubkova analyza orchestra - co RIKA log selhaneho behu u brany "Kontrola parsovani".
// Spusteni: node _analyza/hl-log.mjs [run_number]
import { readFileSync, writeFileSync } from 'node:fs'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim()
const GH = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'hl-analyza' }
const REPO = 'ssevcikm-spec/uo-shadows'
const CISLO = Number(process.argv[2] || 243)

async function gh(p, raw = false) {
  for (let i = 0; i < 4; i++) {
    const r = await fetch('https://api.github.com' + p, { headers: raw ? { ...GH, Accept: 'application/vnd.github.raw' } : GH })
    if (r.status === 403 || r.status === 429) { await new Promise((s) => setTimeout(s, 4000)); continue }
    return raw ? { status: r.status, text: await r.text() } : { status: r.status, j: await r.json() }
  }
  throw new Error('rl')
}

const all = await gh(`/repos/${REPO}/actions/workflows/agent.yml/runs?per_page=100`)
const run = (all.j.workflow_runs || []).find((r) => r.run_number === CISLO)
if (!run) { console.log('beh nenalezen'); process.exit(1) }
console.log(`# beh #${run.run_number} ${run.conclusion} ${run.created_at} name=${run.name}`)

const jobs = await gh(`/repos/${REPO}/actions/runs/${run.id}/jobs?per_page=50`)
const job = (jobs.j.jobs || [])[0]
const log = await gh(`/repos/${REPO}/actions/jobs/${job.id}/logs`, true)
const t = log.text || ''
writeFileSync(`${WS}/_analyza/tmp-log-${CISLO}.txt`, t)
console.log(`# log: ${t.length} znaku → _analyza/tmp-log-${CISLO}.txt`)

// --- hledej klicove udalosti ---
function useky(re, popis, max = 4) {
  const out = []
  const lines = t.split('\n')
  for (let i = 0; i < lines.length; i++) {
    if (re.test(lines[i])) out.push(lines.slice(Math.max(0, i - 1), Math.min(lines.length, i + 6)).join('\n'))
    if (out.length >= max) break
  }
  if (!out.length) { console.log(`\n### ${popis}: NENALEZENO`); return }
  console.log(`\n### ${popis} (${out.length} ukazek)`)
  for (const u of out) console.log(u.split('\n').map((l) => '   ' + l.slice(0, 150)).join('\n'))
}

useky(/Kontrola parsování|parse|Parser|PARSE/i, 'PARSE GATE')
useky(/Vyber bezplatn|pick-provider|FORGE_PROVIDER|FORGE_MODEL|vybran/i, 'VYBER POSKYTOVATELE')
useky(/aider|Aider|litellm|LiteLLM/i, 'AIDER / LITELLM', 3)
useky(/429|rate.?limit|quota|Too Many/i, 'RATE LIMIT', 2)
useky(/Testy hry|\[test\]|selhani|FAIL/i, 'TESTY', 2)
useky(/Report|report\.mjs|conductor/i, 'REPORT', 2)

// --- kolik radku a co obsahuje kazda sekce ---
console.log(`\n### VELIKOST LOGU`)
console.log(`   radku: ${t.split('\n').length}`)
const sec = {}
for (const l of t.split('\n')) {
  const m = l.match(/^(\d{4}-\d\d-\d\dT[\d:.]+Z)\s(.*)$/)
  if (m) {
    const klic = m[2].slice(0, 20)
    sec[klic] = (sec[klic] || 0) + 1
  }
}
