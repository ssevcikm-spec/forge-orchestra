// Hloubkova analyza orchestra - LGTM baseline: kolik polozek, odkud, kdo schvalil.
// Spusteni: node _analyza/hl-baseline.mjs
import { readFileSync } from 'node:fs'

const WS = 'C:/Users/Ssevc/Local-Deepseek'
const b = JSON.parse(readFileSync(`${WS}/games/uo-shadows/.forge/vision/baseline.json`, 'utf8'))
const pol = b.polozky || {}
const klice = Object.keys(pol)
console.log(`# baseline: verze=${b.verze} schvaleno=${b.schvaleno} prompt_verze=${b.prompt_verze}`)
console.log(`# _stav=${JSON.stringify(b._stav)}`)
console.log(`# _ceka_na_lgtm=${JSON.stringify(b._ceka_na_lgtm)}`)
console.log(`# ZMERENO: polozek=${klice.length}`)

const skupiny = {}
for (const k of klice) {
  const s = k.startsWith('tools/blender/') ? 'tools/blender/' : (k.split('/')[0] + '/' + (k.split('/')[1] || ''))
  skupiny[s] = (skupiny[s] || 0) + 1
}
console.log(`# podle slozky: ${JSON.stringify(skupiny, null, 1)}`)

const schvalil = {}
const ceka = []
for (const [k, v] of Object.entries(pol)) {
  schvalil[v.schvalil || '?'] = (schvalil[v.schvalil || '?'] || 0) + 1
  if (v.poznamka && /čeká na lidskou kontrolu/i.test(v.poznamka)) ceka.push(k)
}
console.log(`# schvalil: ${JSON.stringify(schvalil)}`)
console.log(`# polozek s poznamkou "čeká na lidskou kontrolu": ${ceka.length}`)
const casy = Object.values(pol).map((v) => v.schvaleno).filter(Boolean).sort()
console.log(`# casy schvaleni: ${casy[0]} .. ${casy[casy.length - 1]} (${new Set(Object.values(pol).map((v) => String(v.schvaleno).slice(0, 16))).size} ruznych minut)`)

// --- kolik z tech polozek je VUBEC pouzito v CI (snimek hry je mimo repo!) ---
console.log(`\n# Otazka: pouzije CI tuhle cache?`)
const base = readFileSync(`${WS}/orchestra/repo/.forge/baseline.py`, 'utf8')
const radky = base.split('\n')
const iMimo = radky.findIndex((l) => /mimo repo/.test(l))
console.log(`# baseline.py hleda obrazek v repu: ${/mimo repo/.test(base)} (řádek ${iMimo + 1})`)
for (let i = Math.max(0, iMimo - 12); i < iMimo + 4; i++) console.log(`   ${i + 1}| ${radky[i].slice(0, 130)}`)
const ci = readFileSync(`${WS}/orchestra/repo/.github/workflows/ci.yml`, 'utf8')
const snimek = ci.split('\n').map((l, i) => /write-movie|frames/.test(l) ? `${i + 1}: ${l.trim().slice(0, 100)}` : null).filter(Boolean)
console.log(`# kam pise CI snimek: ${JSON.stringify(snimek)}`)
