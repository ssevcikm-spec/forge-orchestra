// p38-b-cf-pole.mjs — KTERÁ POLE GraphQL opravdu existují (P38).
//
// PROČ: `sum { cpuTime }` vrátil „unknown field cpuTime" — a hádat jméno pole
// je přesně to, co se nesmí (skill overovani: metriku ověř na zdroji). Introspekce
// `__type(name:"WorkersInvocationsAdaptive")` typ nenašla, takže se pole zjišťují
// dotazem: každý kandidát se zkusí SAMOSTATNĚ a zapíše se, jestli prošel.
//
// Použití: node _analyza/p38-b-cf-pole.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const CONFIG = 'C:\\Users\\Ssevc\\AppData\\Roaming\\xdg.config\\.wrangler\\config\\default.toml';
const token = readFileSync(CONFIG, 'utf8').match(/^\s*oauth_token\s*=\s*"([^"]+)"/m)[1];
const ACC = 'b19df1f89d07d2cb5b516c95ee8919e1';
const SCRIPT = 'forge-conductor';

// POZOR (naměřeno 19:38Z): `orderBy: [datetime_ASC]` vyžaduje, aby `datetime`
// BYL ve výběru — jinak GraphQL vrátí „cannot order by datetime: it is neither
// aggregated, nor a dimension" a kandidát vypadá jako neexistující pole.
// Proto každý kandidát nese `dimensions { datetime }` navíc.
const DIM = 'dimensions { datetime }';
const kandidati = [
  ['sum.requests', `${DIM} sum { requests }`],
  ['sum.cpuTime', `${DIM} sum { cpuTime }`],
  ['sum.cpuTimeUs', `${DIM} sum { cpuTimeUs }`],
  ['sum.wallTime', `${DIM} sum { wallTime }`],
  ['sum.duration', `${DIM} sum { duration }`],
  ['quantiles{cpuTimeP50,P99}', `${DIM} quantiles { cpuTimeP50 cpuTimeP99 }`],
  ['quantiles{cpuTimeP25,P75}', `${DIM} quantiles { cpuTimeP25 cpuTimeP75 }`],
  ['quantiles{cpuTimeP999}', `${DIM} quantiles { cpuTimeP999 }`],
  ['avg.cpuTime', `${DIM} avg { cpuTime }`],
  ['avg.cpuTimeUs', `${DIM} avg { cpuTimeUs }`],
  ['dimensions.status', `${DIM} dimensions { status }`],
  ['dimensions.scriptName', `${DIM} dimensions { scriptName }`],
  ['dimensions.outcome', `${DIM} dimensions { outcome }`],
  ['count', `${DIM} count`],
];

const radky = [];
const p = (x) => { radky.push(x); console.log(x); };
p(`# p38-b — která pole workersInvocationsAdaptive existují — ${new Date().toISOString()}`);

const do_ = new Date();
const od = new Date(do_.getTime() - 3 * 3600 * 1000);
const obal = (vnitrek) => `query Q($acc: String!, $script: String!, $od: Time!, $do: Time!) {
  viewer { accounts(filter: {accountTag: $acc}) {
    workersInvocationsAdaptive(limit: 5, filter: {scriptName: $script, datetime_geq: $od, datetime_leq: $do}, orderBy: [datetime_ASC]) { ${vnitrek} }
  } }
}`;

for (const [jmeno, vnitrek] of kandidati) {
  const r = await fetch('https://api.cloudflare.com/client/v4/graphql', {
    method: 'POST',
    headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' },
    body: JSON.stringify({ query: obal(vnitrek), variables: { acc: ACC, script: SCRIPT, od: od.toISOString(), do: do_.toISOString() } }),
  });
  const j = await r.json();
  if (j.errors) {
    p(`   ✗ ${jmeno.padEnd(26)} — ${String(j.errors[0]?.message).slice(0, 90)}`);
  } else {
    const ukazka = JSON.stringify(j?.data?.viewer?.accounts?.[0]?.workersInvocationsAdaptive?.[0] ?? null).slice(0, 120);
    p(`   ✓ ${jmeno.padEnd(26)} — OK, ukázka: ${ukazka}`);
  }
}

writeFileSync(join(WS, '_analyza/p38-b-cf-pole-vystup.txt'), radky.join('\n') + '\n', 'utf8');
console.log('\n[zapsano] _analyza/p38-b-cf-pole-vystup.txt');
