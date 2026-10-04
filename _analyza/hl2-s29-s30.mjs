// Druhé kolo — ověření S29/S30 proti SKUTEČNOSTI (git + GitHub API), ne proti D1.
// Spuštění: node _analyza\hl2-s29-s30.mjs
// PAT se nikdy nevypisuje.
import { readFileSync } from 'node:fs';

// POZOR (naměřeno 2. 10. 2026): sandbox `workspace-write` blokuje podprocesy
// s piped stdio → `execFileSync(git.cmd)` spadne na `EPERM: spawnSync cmd.exe`.
// Proto git NENÍ v tomhle skriptu: git se pouští z PowerShellu a výsledek
// se sem předává souborem `_analyza/hl2-git.json` (viz hl2-git.ps1).
const WS = 'C:/Users/Ssevc/Local-Deepseek';
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim();
const GH = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'hl2-analyza' };
const REPO = 'ssevcikm-spec/uo-shadows';

const gitData = JSON.parse(readFileSync(`${WS}/_analyza/hl2-git.json`, 'utf8'));
async function gh(p) {
  const r = await fetch('https://api.github.com' + p, { headers: GH });
  const t = await r.text();
  try { return { status: r.status, j: JSON.parse(t) }; } catch { return { status: r.status, j: null, t: t.slice(0, 200) }; }
}

console.log(`# Ověření S29/S30 proti skutečnosti — ${new Date().toISOString()}`);
console.log(`# repo: ${REPO}\n`);

// ---------- 1. Co je SKUTEČNĚ v origin/main ----------
console.log('## 1. Soubory v origin/main (skutečná práce v hlavní větvi)');
const seznam = gitData.originMainScripts;
console.log(`   .gd souborů v origin/main/scripts: ${seznam.length}`);
for (const s of seznam) console.log(`     ${s}`);
console.log(`   (v lokálním HEAD: ${gitData.localHeadScripts.length})`);
for (const s of gitData.localHeadScripts) {
  if (!seznam.includes(s)) console.log(`     [JEN LOKÁLNĚ] ${s}`);
}

// ---------- 2. PR: stav vs. sloučení ----------
console.log('\n## 2. Pull requesty — stav podle GitHub API');
const prs = [];
for (let page = 1; page <= 3; page++) {
  const r = await gh(`/repos/${REPO}/pulls?state=all&per_page=100&page=${page}&sort=created&direction=desc`);
  if (!Array.isArray(r.j) || r.j.length === 0) break;
  prs.push(...r.j);
  if (r.j.length < 100) break;
}
console.log(`   PR celkem (endpoint /pulls?state=all): ${prs.length}`);
const otevrene = prs.filter((p) => p.state === 'open');
const sloucene = prs.filter((p) => p.merged_at);
const zavreneBez = prs.filter((p) => p.state === 'closed' && !p.merged_at);
console.log(`   otevřené: ${otevrene.length} | sloučené: ${sloucene.length} | zavřené bez sloučení: ${zavreneBez.length}`);

console.log('\n   OTEVŘENÉ PR:');
for (const p of otevrene) {
  const d = await gh(`/repos/${REPO}/pulls/${p.number}`); // DETAIL — seznam vrací merged_by null!
  console.log(`     #${p.number} "${p.title}"`);
  console.log(`        head=${p.head.ref} base=${p.base.ref} +${p.additions}/-${p.deletions} mergeable_state=${d.j?.mergeable_state}`);
}

// ---------- 3. Poslední sloučené PR: číslo, titulek, merged_by ----------
console.log('\n## 3. Posledních 12 sloučených PR (merged_at + merged_by z DETAILU)');
const posledni = sloucene.sort((a, b) => new Date(b.merged_at) - new Date(a.merged_at)).slice(0, 12);
for (const p of posledni) {
  const d = await gh(`/repos/${REPO}/pulls/${p.number}`);
  console.log(`     #${p.number} merged=${p.merged_at} by=${d.j?.merged_by?.login ?? 'null'} | ${p.title}`);
}

// ---------- 4. Co tvrdí soubor roadmap.json vs. co je v main ----------
console.log('\n## 4. Granule, které soubor/D1 vedou jako hotové — je práce v main?');
const roadmap = JSON.parse(readFileSync(`${WS}/games/uo-shadows/.forge/roadmap.json`, 'utf8')).grains;
const hotoveVerejne = roadmap.filter((g) => g.done === true);
console.log(`   granul s done:true v souboru: ${hotoveVerejne.length}`);

// Zjisti "owns" z D1 tasků (payload) — co ta granule měla vytvořit
const env = Object.fromEntries(
  readFileSync(`${WS}/orchestra/.env`, 'utf8').split(/\r?\n/)
    .filter((l) => l.includes('=') && !l.trim().startsWith('#'))
    .map((l) => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]),
);
const q = await fetch(env.FORGE_URL.replace(/\/$/, '') + '/queue', { headers: { 'x-forge-secret': env.FORGE_SECRET } });
const queue = await q.json();
const tasky = new Map((queue.tasks ?? []).map((t) => [t.id, t]));

// title -> PR, párování podle TITULKU (to je ta záchranná cesta, S30)
const prPodleTitulku = new Map();
for (const p of prs) if (p.merged_at) prPodleTitulku.set(p.title.trim().toLowerCase(), p);

console.log('\n   granule | v main? | PR sloučené | jak to systém ví');
for (const g of hotoveVerejne) {
  console.log(`     ${String(g.id).padEnd(18)} done_note="${String(g.done_note ?? '').slice(0, 60)}"`);
}

// ---------- 5. Aktivní hra: co conductor TVRDÍ vs. co je v repu ----------
console.log('\n## 5. games.active vs. skutečnost');
const g = await fetch(env.FORGE_URL.replace(/\/$/, '') + '/games', { headers: { 'x-forge-secret': env.FORGE_SECRET } });
console.log('   /games:', JSON.stringify((await g.json()).games));
console.log('   (pole active=1 je jediné, co říká, která hra se vyvíjí — nikde se neporovnává s obsahem repa)');
