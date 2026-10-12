// p40-d-graphql-sonda.mjs — MŮŽE `roadmapTick` číst merged PR LAČNĚJI?
//
// PROČ: `roadmapTick` stahuje `/pulls?state=closed&per_page=100` — naměřeno
// 599 722 B pro 36 PR (16,6 kB na PR, protože REST vrací i `base`/`head`/`_links`).
// `JSON.parse` toho balíku je 2,3–2,6 ms CPU a tik ho platí KAŽDOU MINUTU.
// Tik potřebuje z každého PR jen čtyři věci: `number`, `title`, `merged_at`,
// `headRefName` (na ně stojí párování `forge/task-N` a titulky granulí).
// GraphQL umí vrátit PRÁVĚ tyhle čtyři pole → payload má být o dva řády menší.
//
// CO MĚŘÍ: velikost odpovědi, cenu `JSON.parse` a to, jestli vrátí TOTÉŽ
// (množina merged task id + titulů) jako REST. Když ne, je odpověď „nejde to“.
//
// PAT se čte z `.secrets/github_pat.txt` a NIKDY se nevypisuje.
// Použití: node _analyza/p40-d-graphql-sonda.mjs
// Exit 0 = změřeno; 1 = GraphQL selhal (to je taky výsledek).

import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, '_analyza', 'p40-d-graphql-vystup.txt');
const PAT = readFileSync(join(WS, '.secrets', 'github_pat.txt'), 'utf8').trim();
const [OWNER, NAME] = ['ssevcikm-spec', 'uo-shadows'];

const radky = [];
const p = (x = '') => { radky.push(x); console.log(x); };
const ms = (ns) => Number(ns) / 1e6;
const med = (a) => { const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };

const HLAV = {
  Authorization: `Bearer ${PAT}`,
  Accept: 'application/vnd.github+json',
  'X-GitHub-Api-Version': '2022-11-28',
  'User-Agent': 'forge-conductor',
};

p(`# p40-d — GraphQL místo REST pro merged PR — ${new Date().toISOString()}`);
p(`# repo: ${OWNER}/${NAME} · tik platí tenhle fetch každou minutu`);
p('');

// ── 1) REST (dnešní cesta) ──────────────────────────────────────────────────
const restR = await fetch(`https://api.github.com/repos/${OWNER}/${NAME}/pulls?state=closed&per_page=100&sort=updated&direction=desc`, { headers: HLAV });
const restT = await restR.text();
const casyRest = [];
for (let i = 0; i < 11; i++) { const t = process.hrtime.bigint(); JSON.parse(restT); casyRest.push(ms(process.hrtime.bigint() - t)); }
const rest = JSON.parse(restT);
const restMerged = new Set();
const restTituly = new Set();
for (const pr of rest) {
  if (!pr.merged_at) continue;
  const m = String(pr.head?.ref || '').match(/^forge\/task-(\d+)$/);
  if (m) restMerged.add(Number(m[1]));
  const t = String(pr.title || '').replace(/^Forge #\d+:\s*/, '');
  if (t) restTituly.add(t);
}
p('## REST (dnešní cesta v `roadmapTick`)');
p(`   HTTP ${restR.status} · ${restT.length} B · PR celkem ${rest.length} · merged ${rest.filter((x) => x.merged_at).length}`);
p(`   JSON.parse: medián ${med(casyRest).toFixed(2)} ms (n=11)`);
p(`   merged task id: ${restMerged.size} · merged titulů: ${restTituly.size}`);
p('');

// ── 2) GraphQL (jen 4 pole) ────────────────────────────────────────────────
// `states: MERGED` + `orderBy: UPDATED_AT DESC` + `last: 100` = přesně to, co
// REST dává po filtrování `merged_at`, ale BEZ balastu.
const dotaz = `query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    pullRequests(states: MERGED, last: 100, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes { number title mergedAt headRefName }
    }
  }
}`;
const gqlR = await fetch('https://api.github.com/graphql', {
  method: 'POST',
  headers: { ...HLAV, 'content-type': 'application/json' },
  body: JSON.stringify({ query: dotaz, variables: { owner: OWNER, name: NAME } }),
});
const gqlT = await gqlR.text();
p('## GraphQL (jen number/title/mergedAt/headRefName)');
p(`   HTTP ${gqlR.status} · ${gqlT.length} B`);
let gql = null;
try { gql = JSON.parse(gqlT); } catch { /* */ }
if (!gql || gql.errors) {
  p(`   ✗ GraphQL selhalo: ${JSON.stringify(gql?.errors || gqlT.slice(0, 200)).slice(0, 400)}`);
  p('   → TODO NEPOUŽÍVAT (REST zůstává), ale je to měřený výsledek, ne dohad.');
  writeFileSync(OUT, radky.join('\n') + '\n', 'utf8');
  console.log(`\n[zapsano] ${OUT}`);
  process.exit(1);
}
const uzly = gql?.data?.repository?.pullRequests?.nodes || [];
const casyGql = [];
for (let i = 0; i < 11; i++) { const t = process.hrtime.bigint(); JSON.parse(gqlT); casyGql.push(ms(process.hrtime.bigint() - t)); }
const gqlMerged = new Set();
const gqlTituly = new Set();
for (const pr of uzly) {
  const m = String(pr.headRefName || '').match(/^forge\/task-(\d+)$/);
  if (m) gqlMerged.add(Number(m[1]));
  const t = String(pr.title || '').replace(/^Forge #\d+:\s*/, '');
  if (t) gqlTituly.add(t);
}
p(`   uzlů: ${uzly.length} · JSON.parse: medián ${med(casyGql).toFixed(2)} ms (n=11)`);
p(`   merged task id: ${gqlMerged.size} · merged titulů: ${gqlTituly.size}`);
p('');

// ── 3) SEDÍ TO NA SEBE? (jinak je zlevnění regrese) ────────────────────────
const chybiId = [...restMerged].filter((x) => !gqlMerged.has(x));
const chybiTitul = [...restTituly].filter((x) => !gqlTituly.has(x));
p('## SHODA REST vs GraphQL');
p(`   task id: REST ${restMerged.size} / GQL ${gqlMerged.size} · chybí v GQL: ${chybiId.length ? chybiId.join(', ') : 'žádné'}`);
p(`   tituly:  REST ${restTituly.size} / GQL ${gqlTituly.size} · chybí v GQL: ${chybiTitul.length ? chybiTitul.slice(0, 5).join(' | ') : 'žádné'}`);
p('');
p('## ÚSPORA');
p(`   payload: ${restT.length} B → ${gqlT.length} B  (${(100 * gqlT.length / restT.length).toFixed(1)} %)`);
p(`   JSON.parse: ${med(casyRest).toFixed(2)} ms → ${med(casyGql).toFixed(2)} ms  (úspora ${(med(casyRest) - med(casyGql)).toFixed(2)} ms na tik)`);
p(`   VOLÁNÍ: 1 na tik v obou případech (nezvyšuje počet round-tripů).`);
p(`   zdroj dat: REST ${restR.status} · GraphQL ${gqlR.status}`);

writeFileSync(OUT, radky.join('\n') + '\n', 'utf8');
console.log(`\n[zapsano] ${OUT}`);
process.exit(chybiId.length || chybiTitul.length ? 1 : 0);
