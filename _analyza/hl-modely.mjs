// Hloubkova analyza orchestra - Q3: kolik volani modelu orchestra spotrebuje
// a kde. Cte logy behu agent.yml a hleda radky o modelech, tokenech a casovani.
// Spusteni: node _analyza/hl-modely.mjs [pocet_behu]
import { readFileSync, writeFileSync } from 'node:fs'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim()
const GH = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'hl-analyza' }
const REPO = 'ssevcikm-spec/uo-shadows'
const N = Number(process.argv[2] || 20)

async function gh(p, raw = false) {
  for (let i = 0; i < 4; i++) {
    const r = await fetch('https://api.github.com' + p, { headers: raw ? { ...GH, Accept: 'application/vnd.github.raw' } : GH })
    if (r.status === 403 || r.status === 429) { await new Promise((s) => setTimeout(s, 4000)); continue }
    return raw ? { status: r.status, text: await r.text() } : { status: r.status, j: await r.json() }
  }
  throw new Error('rate limit ' + p)
}

// vyber behu: kombinace uspesnych a neuspesnych
const list = await gh(`/repos/${REPO}/actions/workflows/agent.yml/runs?per_page=100`)
const runs = (list.j.workflow_runs || []).filter((r) => r.conclusion === 'success' || r.conclusion === 'failure')
const vyber = []
// vezmi 8 uspesnych a 12 neuspesnych
for (const r of runs) {
  if (r.conclusion === 'success' && vyber.filter((x) => x.conclusion === 'success').length < 8) vyber.push(r)
  else if (r.conclusion === 'failure' && vyber.filter((x) => x.conclusion === 'failure').length < 12) vyber.push(r)
  if (vyber.length >= N) break
}
console.log(`# analyzuji ${vyber.length} behu agent.yml (${vyber.filter((r) => r.conclusion === 'success').length} success, ${vyber.filter((r) => r.conclusion === 'failure').length} failure)`)

const RE = {
  provider: /(?:poskytovatel|provider|model)[:=]\s*([\w./:-]+)/i,
  aiderModel: /(?:aider|litellm|using model|Main model)[^\n]{0,80}/i,
  tokens: /(?:tokens?|token)[^\n]{0,60}?([\d,]+)/i,
  cost: /(?:cost|cena)[^\n]{0,40}/i,
  rateLimit: /(429|rate.?limit|quota|exceeded)/i,
  timeAgent: /Spusť agenta|Run agent/i,
}

const souhrn = []
for (const r of vyber) {
  const jobs = await gh(`/repos/${REPO}/actions/runs/${r.id}/jobs?per_page=50`)
  const job = (jobs.j.jobs || [])[0]
  if (!job) continue
  // casy kroku
  const kroky = (job.steps || []).map((s) => ({ n: s.name, c: s.conclusion, a: s.started_at, b: s.completed_at }))
  const trvani = (s) => (s.a && s.b) ? (Date.parse(s.b) - Date.parse(s.a)) / 1000 : null
  const agentStep = kroky.find((s) => /Spusť agenta/.test(s.n))
  const vyberKroku = kroky.filter((s) => /Vyber bezplatného|Spusť agenta|Testy hry|Kontrola parsování|Verdikt/.test(s.n))
  // log jobu (jen cast) - hledej model a tokeny
  const log = await gh(`/repos/${REPO}/actions/jobs/${job.id}/logs`, true)
  const t = log.text || ''
  const modely = [...t.matchAll(/FORGE_MODEL=([^\s]+)/g)].map((m) => m[1])
  const prov = [...t.matchAll(/FORGE_PROVIDER=([^\s]+)/g)].map((m) => m[1])
  const litellm = [...t.matchAll(/LiteLLM completion\(\)[^\n]{0,120}/g)].map((m) => m[0]).slice(0, 3)
  const tok = [...t.matchAll(/Tokens:\s*([\d,]+)\s*sent,\s*([\d,]+)\s*received/gi)].map((m) => ({ sent: +m[1].replace(/,/g, ''), recv: +m[2].replace(/,/g, '') }))
  const rl = (t.match(/429|rate limit|quota/gi) || []).length
  const soubor = {
    run: r.run_number, concl: r.conclusion, name: (r.name || '').slice(0, 30),
    agent_s: agentStep ? trvani(agentStep) : null,
    kroky: vyberKroku.map((s) => `${s.n}=${s.c}${trvani(s) != null ? `(${trvani(s)}s)` : ''}`),
    modely: [...new Set(modely)], providery: [...new Set(prov)],
    litellm: litellm.slice(0, 1),
    tokeny: tok.reduce((a, x) => ({ sent: a.sent + x.sent, recv: a.recv + x.recv }), { sent: 0, recv: 0 }),
    tokeny_vyskytu: tok.length,
    rate_limit_radku: rl,
  }
  souhrn.push(soubor)
  console.log(`\n#${soubor.run} ${soubor.concl} ${soubor.name}`)
  console.log(`   agent krok: ${soubor.agent_s}s`)
  console.log(`   kroky: ${soubor.kroky.join('  ')}`)
  console.log(`   FORGE_PROVIDER=${JSON.stringify(soubor.providery)} FORGE_MODEL=${JSON.stringify(soubor.modely)}`)
  console.log(`   tokeny: sent=${soubor.tokeny.sent} recv=${soubor.tokeny.recv} (radku s tokeny: ${soubor.tokeny_vyskytu})`)
  console.log(`   radku s 429/quota: ${soubor.rate_limit_radku}`)
  if (soubor.litellm.length) console.log(`   ${soubor.litellm[0].slice(0, 110)}`)
}

const ok = souhrn.filter((s) => s.concl === 'success')
const bad = souhrn.filter((s) => s.concl === 'failure')
const avg = (a, f) => a.length ? (a.reduce((s, x) => s + (f(x) || 0), 0) / a.length) : 0
console.log(`\n=== SOUHRN ===`)
console.log(`  uspesne behy: ${ok.length}, prumerny krok agenta ${avg(ok, (s) => s.agent_s).toFixed(0)} s, tokeny sent=${avg(ok, (s) => s.tokeny.sent).toFixed(0)} recv=${avg(ok, (s) => s.tokeny.recv).toFixed(0)}`)
console.log(`  selhane behy: ${bad.length}, prumerny krok agenta ${avg(bad, (s) => s.agent_s).toFixed(0)} s, tokeny sent=${avg(bad, (s) => s.tokeny.sent).toFixed(0)} recv=${avg(bad, (s) => s.tokeny.recv).toFixed(0)}`)
const vsechnyProv = {}
for (const s of souhrn) for (const p of s.providery) vsechnyProv[p] = (vsechnyProv[p] || 0) + 1
console.log(`  poskytovatele napric behy: ${JSON.stringify(vsechnyProv)}`)
writeFileSync(`${WS}/_analyza/hl-modely.json`, JSON.stringify(souhrn, null, 1))
console.log(`# data: _analyza/hl-modely.json`)
