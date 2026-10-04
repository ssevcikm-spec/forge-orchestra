// Hloubkova analyza orchestra - Q7: co dela agent, kdyz zadani nerozumi / narazi na
// chybejici smlouvu. Cte logy behu, ktere spadly na brane "Kontrola parsovani".
// Spusteni: node _analyza/hl-chyby.mjs [pocet_behu]
import { readFileSync, writeFileSync } from 'node:fs'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim()
const GH = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'hl-analyza' }
const REPO = 'ssevcikm-spec/uo-shadows'
const N = Number(process.argv[2] || 12)

async function gh(p, raw = false) {
  for (let i = 0; i < 5; i++) {
    const r = await fetch('https://api.github.com' + p, { headers: raw ? { ...GH, Accept: 'application/vnd.github.raw' } : GH })
    if (r.status === 403 || r.status === 429) { await new Promise((s) => setTimeout(s, 4000)); continue }
    if (raw) return { status: r.status, text: await r.text() }
    return { status: r.status, j: await r.json() }
  }
  throw new Error('rl')
}

const det = JSON.parse(readFileSync(`${WS}/_analyza/hl-priciny.json`, 'utf8'))
const parseFail = det.filter((d) => /Kontrola parsov/.test(d.krok)).map((d) => d.run)
const testFail = det.filter((d) => /Testy hry/.test(d.krok)).map((d) => d.run)
const noChange = det.filter((d) => /Agent nic nezm/.test(d.krok)).map((d) => d.run)
console.log(`# behu s chybou parsovani: ${parseFail.length} (${parseFail.join(',')})`)
console.log(`# behu s chybou testu:     ${testFail.length}`)
console.log(`# behu bez zmeny:          ${noChange.length}`)

const all = await gh(`/repos/${REPO}/actions/workflows/agent.yml/runs?per_page=100&page=1`)
const byNum = new Map((all.j.workflow_runs || []).map((r) => [r.run_number, r]))

function vytahni(t, pat, ctx = 2, max = 3) {
  const lines = t.split('\n').map((l) => l.replace(/^\S+Z\s?/, '').replace(/\u001b\[\d+m/g, ''))
  const out = []
  for (let i = 0; i < lines.length; i++) {
    if (pat.test(lines[i])) {
      out.push(lines.slice(i, Math.min(lines.length, i + ctx + 1)).join(' | ').slice(0, 240))
      if (out.length >= max) break
    }
  }
  return out
}

const vysledky = []
for (const cislo of parseFail.slice(0, N)) {
  const r = byNum.get(cislo)
  if (!r) continue
  const jobs = await gh(`/repos/${REPO}/actions/runs/${r.id}/jobs?per_page=50`)
  const job = (jobs.j.jobs || [])[0]
  const log = await gh(`/repos/${REPO}/actions/jobs/${job.id}/logs`, true)
  const t = log.text || ''
  const chyby = vytahni(t, /SCRIPT ERROR: Parse Error/, 2, 4)
  const stineni = vytahni(t, /stíní class_name|vnořená class/, 1, 2)
  const chybySoub = [...new Set([...t.matchAll(/::error file=([^\s:]+)/g)].map((m) => m[1]))]
  const model = (t.match(/FORGE_MODEL: (\S+)/) || [])[1]
  const prompt = (t.match(/FORGE_PROMPT: (.{0,160})/) || [])[1]
  const zmenil = /Applied edit to ([^\n]+)/.exec(t)
  const zmeneneSoubory = [...new Set([...t.matchAll(/Applied edit to (\S+)/g)].map((m) => m[1]))]
  const readDeps = [...new Set([...t.matchAll(/Added (\S+) to the chat \(read-only\)/g)].map((m) => m[1]))]
  const edituje = [...new Set([...t.matchAll(/Added (\S+) to the chat\./g)].map((m) => m[1]))]
  vysledky.push({ run: cislo, model, chyby, stineni, chybySoub, zmeneneSoubory, edituje, readDeps, prompt })
  console.log(`\n===== beh #${cislo} =====`)
  console.log(`   model (z logu): ${model}`)
  console.log(`   zadani: ${prompt}`)
  console.log(`   editoval: ${JSON.stringify(edituje)}`)
  console.log(`   četl (deps): ${JSON.stringify(readDeps)}`)
  console.log(`   zmenil: ${JSON.stringify(zmeneneSoubory)}`)
  for (const c of chyby) console.log(`   PARSE: ${c}`)
  for (const c of stineni) console.log(`   STINENI: ${c}`)
}

// souhrn typu chyb
const typy = {}
for (const v of vysledky) {
  for (const c of v.chyby) {
    const m = c.match(/Parse Error[:\s]*(.{0,60})/)
    if (m) { const k = m[1].replace(/["`].*$/, '').trim().slice(0, 50); typy[k] = (typy[k] || 0) + 1 }
  }
}
console.log(`\n=== TYPY CHYB PARSOVANI ===`)
for (const [k, v] of Object.entries(typy).sort((a, b) => b[1] - a[1])) console.log(`  ${v}x  ${k}`)
const chybSoubor = {}
for (const v of vysledky) for (const f of v.chybySoub) chybSoubor[f] = (chybSoubor[f] || 0) + 1
console.log(`\n=== SOUBORY, KTERE SE NEPARSOVALY ===`)
for (const [k, v] of Object.entries(chybSoubor).sort((a, b) => b[1] - a[1])) console.log(`  ${v}x  ${k}`)

// kolik z tech behu cetlo soubor, ktery byl potreba
console.log(`\n=== MELA GRANULE K DISPOZICI SVOJI ZAVISLOST? ===`)
for (const v of vysledky) {
  const hleda = [...v.chyby.join(' ').matchAll(/[A-Z][A-Za-z]+/g)].map((m) => m[0])
  console.log(`  #${v.run}: editoval=${v.edituje.join(',')} cetl=${v.readDeps.length} souboru; chyba zminuje: ${JSON.stringify([...new Set(hleda)].slice(0, 8))}`)
}
writeFileSync(`${WS}/_analyza/hl-chyby.json`, JSON.stringify(vysledky, null, 1))
console.log(`\n# data: _analyza/hl-chyby.json`)
