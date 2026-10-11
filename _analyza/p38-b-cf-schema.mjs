// p38-b-cf-schema.mjs — introspekce GraphQL typu pro invokace (P38).
// PROČ: `sum { cpuTime }` GraphQL odmítl ("unknown field cpuTime") — jak se pole
// doopravdy jmenuje, se NESMÍ hádat (skill overovani: metriku ověř na zdroji).
// Použití: node _analyza/p38-b-cf-schema.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const CONFIG = 'C:\\Users\\Ssevc\\AppData\\Roaming\\xdg.config\\.wrangler\\config\\default.toml';
const cfg = readFileSync(CONFIG, 'utf8');
const token = cfg.match(/^\s*oauth_token\s*=\s*"([^"]+)"/m)[1];

const dotaz = `query { __type(name: "WorkersInvocationsAdaptive") { name kind fields { name type { name kind ofType { name kind } } } } }`;
const r = await fetch('https://api.cloudflare.com/client/v4/graphql', {
  method: 'POST',
  headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' },
  body: JSON.stringify({ query: dotaz }),
});
const j = await r.json();
writeFileSync(join(WS, '_analyza/p38-b-cf-schema-vystup.txt'), JSON.stringify(j, null, 1) + '\n', 'utf8');
if (j.errors) { console.log('CHYBY:', JSON.stringify(j.errors).slice(0, 800)); process.exit(1); }
const t = j.data.__type;
if (!t) { console.log('typ WorkersInvocationsAdaptive nenalezen'); process.exit(1); }
console.log(`typ ${t.name} (${t.kind}) — pole:`);
for (const f of t.fields) {
  const typ = f.type.name || (f.type.ofType && `${f.type.kind}<${f.type.ofType.name}>`) || f.type.kind;
  console.log(`  ${f.name.padEnd(24)} ${typ}`);
}
