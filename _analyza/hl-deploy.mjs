// Hloubkova analyza orchestra - je NASZENY conductor stejny jako v gitu?
// A bezi cron? Meri: deploye conductora (deploy.yml) + hash zdroje v repu orchestra.
// Spusteni: node _analyza/hl-deploy.mjs
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim()
const GH = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'hl-analyza' }

async function gh(p, raw = false) {
  const r = await fetch('https://api.github.com' + p, {
    headers: raw ? { ...GH, Accept: 'application/vnd.github.raw' } : GH,
  })
  if (raw) return { status: r.status, text: await r.text() }
  return { status: r.status, j: await r.json() }
}

// --- posledni behy deploy.yml v repu orchestra ---
const dep = await gh('/repos/ssevcikm-spec/forge-orchestra/actions/workflows/deploy.yml/runs?per_page=10')
console.log(`# deploy.yml behu: total_count=${dep.j?.total_count}`)
for (const r of dep.j?.workflow_runs || []) {
  console.log(`   #${r.run_number} ${r.conclusion} ${r.created_at} head=${(r.head_sha || '').slice(0, 7)} event=${r.event}`)
}

// --- vsechny workflows v repu orchestra ---
const wfs = await gh('/repos/ssevcikm-spec/forge-orchestra/actions/workflows')
console.log(`\n# workflows v orchestra: ${(wfs.j?.workflows || []).map((w) => w.path).join(', ')}`)
for (const w of wfs.j?.workflows || []) {
  const rr = await gh(`/repos/ssevcikm-spec/forge-orchestra/actions/workflows/${w.id}/runs?per_page=3`)
  const l = rr.j?.workflow_runs || []
  console.log(`   ${w.path}: behu=${rr.j?.total_count} posledni=${l.map((x) => `#${x.run_number}:${x.conclusion}`).join(' ') || '(zadny)'}`)
}

// --- zdroj conductora v repu orchestra vs. lokalni ---
const remote = await gh('/repos/ssevcikm-spec/forge-orchestra/contents/conductor/src/index.ts', true)
const local = readFileSync(`${WS}/orchestra/conductor/src/index.ts`, 'utf8')
const h = (s) => createHash('sha256').update(s.replace(/\r\n/g, '\n')).digest('hex').slice(0, 16)
console.log(`\n# conductor/src/index.ts`)
console.log(`   v repu orchestra (main): ${remote.status} sha256=${remote.status === 200 ? h(remote.text) : '-'} bajtu=${remote.text.length}`)
console.log(`   lokalne:                            sha256=${h(local)} bajtu=${local.length}`)
console.log(`   ${remote.status === 200 && h(remote.text) === h(local) ? 'SHODNE' : 'ROZDILNE (pozor!)'}`)

// --- ostatni soubory conductora ---
for (const p of ['conductor/wrangler.toml', 'conductor/schema.sql']) {
  const rr = await gh(`/repos/ssevcikm-spec/forge-orchestra/contents/${p}`, true)
  const ll = readFileSync(`${WS}/orchestra/${p}`, 'utf8')
  console.log(`   ${p}: ${rr.status === 200 ? (h(rr.text) === h(ll) ? 'SHODNE' : 'ROZDILNE') : 'NENALEZENO'} (repo ${rr.text?.length} vs lokál ${ll.length})`)
}

// --- HEAD repa orchestra vs. lokalni HEAD ---
const commits = await gh('/repos/ssevcikm-spec/forge-orchestra/commits?per_page=5')
console.log(`\n# orchestra rep HEAD: ${commits.j?.[0]?.sha?.slice(0, 7)} "${commits.j?.[0]?.commit?.message?.slice(0, 60)}" ${commits.j?.[0]?.commit?.author?.date}`)
console.log(`   predchozi: ${(commits.j || []).slice(1, 5).map((c) => c.sha.slice(0, 7)).join(' ')}`)

// --- herni rep: HEAD a zda je lokalni klon na tomtez ---
const g = await gh('/repos/ssevcikm-spec/uo-shadows/commits?per_page=3')
console.log(`\n# hra rep HEAD: ${g.j?.[0]?.sha?.slice(0, 7)} "${g.j?.[0]?.commit?.message?.slice(0, 60)}" ${g.j?.[0]?.commit?.author?.date}`)

// --- ma orchestra branch protection / jine vetve? ---
const br = await gh('/repos/ssevcikm-spec/forge-orchestra/branches')
console.log(`\n# vetve orchestra: ${(br.j || []).map((b) => b.name).join(', ')}`)
const br2 = await gh('/repos/ssevcikm-spec/uo-shadows/branches?per_page=20')
console.log(`# vetve hry: ${(br2.j || []).map((b) => b.name).join(', ')}`)
