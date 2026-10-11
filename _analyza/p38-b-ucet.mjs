// p38-b-ucet.mjs — NA JAKÉM PLÁNU conductor skutečně běží (P38).
//
// PROČ: `conductor/wrangler.toml` má v komentáři „free plán" a celý výklad
// výpadku (10 ms CPU) stojí na tom. Komentář ale NENÍ měření — a rozdíl je
// podstatný: `[limits] cpu_ms` je dokumentovaně podporovaný JEN pro Standard
// Usage Model (placený), takže na free plánu se limit zvednout NEDÁ.
// API to říká přímo: `usage_model` skriptu.
//
// Token se ČTE z konfigurace wrangleru (`oauth_token`), NIKDY se nevypisuje.
// Použití: node _analyza/p38-b-ucet.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const CONFIG = 'C:\\Users\\Ssevc\\AppData\\Roaming\\xdg.config\\.wrangler\\config\\default.toml';
const ACC = 'b19df1f89d07d2cb5b516c95ee8919e1';
const token = readFileSync(CONFIG, 'utf8').match(/^\s*oauth_token\s*=\s*"([^"]+)"/m)[1];

const radky = [];
const p = (x) => { radky.push(x); console.log(x); };
const api = async (cesta) => {
  const r = await fetch(`https://api.cloudflare.com/client/v4${cesta}`, {
    headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' },
  });
  return { status: r.status, json: await r.json().catch(() => null) };
};

p(`# p38-b — plán a usage model conductora — ${new Date().toISOString()}`);

const sk = await api(`/accounts/${ACC}/workers/scripts/forge-conductor`);
p('');
p(`## GET /workers/scripts/forge-conductor → HTTP ${sk.status}`);
if (sk.json?.result) {
  const r = sk.json.result;
  for (const k of ['id', 'etag', 'created_on', 'modified_on', 'usage_model', 'compatibility_date', 'handlers', 'last_deployed_from']) {
    if (k in r) p(`   ${k} = ${JSON.stringify(r[k])}`);
  }
  const dalsi = Object.keys(r).filter((k) => !['id', 'etag', 'created_on', 'modified_on', 'usage_model', 'compatibility_date', 'handlers', 'last_deployed_from'].includes(k));
  for (const k of dalsi) {
    const v = r[k];
    p(`   ${k} = ${typeof v === 'object' ? JSON.stringify(v).slice(0, 200) : v}`);
  }
} else {
  p(`   ${JSON.stringify(sk.json).slice(0, 400)}`);
}

const sub = await api(`/accounts/${ACC}/subscriptions`);
p('');
p(`## GET /accounts/${ACC}/subscriptions → HTTP ${sub.status}`);
const vysledky = sub.json?.result || [];
if (!vysledky.length) p(`   (žádné předplatné v odpovědi) ${sub.status === 200 ? '' : JSON.stringify(sub.json).slice(0, 300)}`);
for (const s of vysledky) {
  p(`   rate_plan.id = ${s.rate_plan?.id} · ${s.rate_plan?.public_name ?? ''}`);
  p(`     stav=${s.state} · price=${s.price} · currency=${s.currency} · freq=${s.frequency}`);
  p(`     aktuální_period_end=${s.current_period_end ?? '-'}`);
}

writeFileSync(join(WS, '_analyza/p38-b-ucet-vystup.txt'), radky.join('\n') + '\n', 'utf8');
console.log('\n[zapsano] _analyza/p38-b-ucet-vystup.txt');
