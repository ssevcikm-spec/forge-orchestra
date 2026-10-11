// p37-cf-analytika.mjs — HISTORIE invokací conductora z Cloudflare Analytics (P37, prevzato z P34 s vlastnim vystupem - H166).
//
// PROČ: `wrangler tail` vidí jen ŽIVÉ eventy. Otázka „od kdy tik umírá na
// CPU limit" potřebuje HISTORII. Cloudflare GraphQL Analytics API ji dá
// (dataset `workersInvocationsAdaptive`, rozměr `datetime` + `status`).
//
// Token se ČTE z konfigurace wrangleru (`oauth_token`), NIKDY se nevypisuje.
// Použití: node _analyza/p37-cf-analytika.mjs [hodin-zpet]
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const CONFIG = 'C:\\Users\\Ssevc\\AppData\\Roaming\\xdg.config\\.wrangler\\config\\default.toml';
const ACC = 'b19df1f89d07d2cb5b516c95ee8919e1';
const SCRIPT = 'forge-conductor';
const hodin = Number(process.argv[2] || 48);

const cfg = readFileSync(CONFIG, 'utf8');
const m = cfg.match(/^\s*oauth_token\s*=\s*"([^"]+)"/m);
if (!m) { console.log('CHYBA: oauth_token v konfiguraci wrangleru nenalezen'); process.exit(2); }
const token = m[1];

const do_ = new Date();
const od = new Date(do_.getTime() - hodin * 3600 * 1000);

const dotaz = `
query Q($acc: String!, $script: String!, $od: Time!, $do: Time!) {
  viewer {
    accounts(filter: {accountTag: $acc}) {
      workersInvocationsAdaptive(limit: 10000, filter: {scriptName: $script, datetime_geq: $od, datetime_leq: $do}, orderBy: [datetime_ASC]) {
        dimensions { datetime status }
        sum { requests errors subrequests }
      }
    }
  }
}`;

const r = await fetch('https://api.cloudflare.com/client/v4/graphql', {
  method: 'POST',
  headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' },
  body: JSON.stringify({ query: dotaz, variables: { acc: ACC, script: SCRIPT, od: od.toISOString(), do: do_.toISOString() } }),
});
const j = await r.json();
const out = {
  mereno: do_.toISOString(), od: od.toISOString(), hodin,
  http_status: r.status,
  chyby: j.errors ?? null,
  radky: j?.data?.viewer?.accounts?.[0]?.workersInvocationsAdaptive ?? null,
};
writeFileSync(join(WS, '_analyza/p37-cf-analytika-vystup.txt'), JSON.stringify(out, null, 2) + '\n', 'utf8');
if (j.errors) { console.log('CHYBY:', JSON.stringify(j.errors).slice(0, 800)); }
const radky = out.radky || [];
console.log(`# radku: ${radky.length} (HTTP ${r.status})`);
const podle = new Map();
for (const x of radky) {
  const k = x.dimensions.status;
  const p = podle.get(k) || { requesty: 0, chyby: 0, hodin: new Set() };
  p.requesty += x.sum.requests; p.chyby += x.sum.errors; p.hodin.add(x.dimensions.datetime.slice(0, 13));
  podle.set(k, p);
}
for (const [k, v] of [...podle].sort((a, b) => b[1].requesty - a[1].requesty)) {
  console.log(`  ${k}: ${v.requesty} invokaci, ${v.chyby} chyb, v ${v.hodin.size} hodinovych oknech`);
}

// Tabulka po hodinach: kdy presne umiraly invokace na limit.
const hodiny = new Map();
for (const x of radky) {
  const h = x.dimensions.datetime.slice(0, 13);
  const p = hodiny.get(h) || { success: 0, exceededResources: 0, jine: 0 };
  if (x.dimensions.status === 'success') p.success += x.sum.requests;
  else if (x.dimensions.status === 'exceededResources') p.exceededResources += x.sum.requests;
  else p.jine += x.sum.requests;
  hodiny.set(h, p);
}
console.log('\n# hodina (UTC)          | success | exceededRes | jine | podil selhani');
for (const [h, p] of [...hodiny].sort()) {
  const celkem = p.success + p.exceededResources + p.jine;
  const podil = celkem ? Math.round((p.exceededResources / celkem) * 100) : 0;
  console.log(`  ${h} | ${String(p.success).padStart(7)} | ${String(p.exceededResources).padStart(11)} | ${String(p.jine).padStart(4)} | ${String(podil).padStart(3)} %`);
}
