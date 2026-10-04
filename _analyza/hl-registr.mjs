// Hloubkova analyza orchestra - Q4: co udela orchestra, kdyz se registr her rozbije?
// BEZ ZASahu: pouziva se jen dry_run a cteni. Nic se nemeni.
// Spusteni: node _analyza/hl-registr.mjs
import { readFileSync } from 'node:fs'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const env = Object.fromEntries(
  readFileSync(`${WS}/orchestra/.env`, 'utf8').split(/\r?\n/)
    .filter((l) => l.includes('=') && !l.trim().startsWith('#'))
    .map((l) => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]),
)
const URLB = env.FORGE_URL.replace(/\/$/, '')
const H = { 'x-forge-secret': env.FORGE_SECRET, 'content-type': 'application/json' }

async function call(p, init = {}) {
  const r = await fetch(URLB + p, { headers: H, ...init })
  const t = await r.text()
  let j = null
  try { j = JSON.parse(t) } catch { /* */ }
  return { status: r.status, j, t }
}

console.log(`# mereno ${new Date().toISOString()}  (pouze cteni a dry_run)`)
const g = await call('/games')
console.log(`\n== registr her (GET /games) ==\n${JSON.stringify(g.j)}`)

// co je v kodu jako fallback
const ts = readFileSync(`${WS}/orchestra/conductor/src/index.ts`, 'utf8')
const i = ts.indexOf('async function listGames')
console.log(`\n== fallback v kódu (index.ts) ==`)
console.log(ts.slice(i, i + 520).split('\n').map((l) => '   ' + l).join('\n'))

// co by se stalo: dry_run u /tasks/cleanup (NEMAZE, jen pocita)
const c = await call('/tasks/cleanup', { method: 'POST', body: JSON.stringify({ dry_run: true }) })
console.log(`\n== POST /tasks/cleanup {dry_run:true} ==  HTTP ${c.status}`)
console.log(JSON.stringify(c.j, null, 1))

// dry_run u resetu
const r = await call('/roadmap/reset', { method: 'POST', body: JSON.stringify({ game_id: 'uo-shadows', dry_run: true }) })
console.log(`\n== POST /roadmap/reset {game_id, dry_run:true} ==  HTTP ${r.status}`)
console.log(JSON.stringify(r.j, null, 1))

// tick - jen cteni vysledku (POZOR: /tick JE zasah; proto se nevola)
console.log(`\n# POZN.: /tick jsem NEVOLAL – spustil by dispatch. Stav je videt z /health a /queue.`)
const h = await call('/health')
console.log(`# /health: ${JSON.stringify(h.j)}`)
