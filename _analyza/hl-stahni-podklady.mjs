// Stahne podklady pro srovnani `done` v roadmap.json (JEN CTENI, nic nemeni).
// Zapisuje do _analyza/tmp-roadmap-d1.json a tmp-pr.json.
// Node fetch - TLS z PowerShellu na teto stanici nefunguje a Python urllib
// dostal z Cloudflare 403 (namereno 1. 10. 2026).
// Spusteni: node _analyza/hl-stahni-podklady.mjs
import { readFileSync, writeFileSync } from 'node:fs'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const env = Object.fromEntries(
  readFileSync(`${WS}/orchestra/.env`, 'utf8').replace(/^\uFEFF/, '').split(/\r?\n/)
    .filter((l) => l.includes('=') && !l.trim().startsWith('#'))
    .map((l) => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]),
)
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim()

const r1 = await fetch(env.FORGE_URL.replace(/\/$/, '') + '/roadmap',
  { headers: { 'x-forge-secret': env.FORGE_SECRET } })
if (!r1.ok) throw new Error(`/roadmap → HTTP ${r1.status}`)
const d1 = await r1.json()
writeFileSync(`${WS}/_analyza/tmp-roadmap-d1.json`, JSON.stringify(d1, null, 1))
console.log(`# /roadmap: ${(d1.roadmap || []).length} řádků → _analyza/tmp-roadmap-d1.json`)

const r2 = await fetch('https://api.github.com/repos/ssevcikm-spec/uo-shadows/pulls'
  + '?state=closed&per_page=100&sort=updated&direction=desc',
  { headers: { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'hl-analyza' } })
if (!r2.ok) throw new Error(`/pulls → HTTP ${r2.status}`)
const prs = await r2.json()
writeFileSync(`${WS}/_analyza/tmp-pr.json`, JSON.stringify(prs, null, 1))
console.log(`# /pulls: ${prs.length} PR (sloučených ${prs.filter((p) => p.merged_at).length}) → _analyza/tmp-pr.json`)
