// p38-b-ucet2.mjs — pokus o PLNÝ obraz účtu (P38, když `/subscriptions` vrací 403).
// Postupuje se od nejkonkrétnějšího k nejobecnějšímu a KAŽDÝ endpoint se pojmenuje
// i s chybou — „nešlo to" musí být vidět, ne mlčet (nula není úspěch).
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const CONFIG = 'C:\\Users\\Ssevc\\AppData\\Roaming\\xdg.config\\.wrangler\\config\\default.toml';
const ACC = 'b19df1f89d07d2cb5b516c95ee8919e1';
const token = readFileSync(CONFIG, 'utf8').match(/^\s*oauth_token\s*=\s*"([^"]+)"/m)[1];

const cesty = [
  `/accounts/${ACC}/workers/services/forge-conductor`,
  `/accounts/${ACC}/workers/scripts`,
  `/accounts/${ACC}/workers/scripts/forge-conductor/settings`,
  `/accounts/${ACC}/workers/subdomain`,
  `/accounts/${ACC}`,
  `/accounts`,
  `/user/subscriptions`,
  `/user/tokens/verify`,
];

const radky = [];
const p = (x) => { radky.push(x); console.log(x); };
p(`# p38-b2 — obraz účtu Cloudflare — ${new Date().toISOString()}`);
for (const c of cesty) {
  const r = await fetch(`https://api.cloudflare.com/client/v4${c}`, {
    headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' },
  });
  const j = await r.json().catch(() => null);
  const uspech = j?.success;
  let zajimave = '';
  const res = j?.result;
  if (uspech && res) {
    if (Array.isArray(res)) {
      zajimave = `pole[${res.length}]: ` + JSON.stringify(res.slice(0, 3)).slice(0, 400);
    } else {
      // vytáhni jen pole, která o plánu/modelu něco říkají
      const klice = ['usage_model', 'name', 'id', 'plan', 'type', 'created_on', 'modified_on', 'settings', 'default_usage_model', 'compatibility_date'];
      const vyber = {};
      for (const k of klice) if (k in res) vyber[k] = res[k];
      zajimave = JSON.stringify(Object.keys(vyber).length ? vyber : res).slice(0, 500);
    }
  } else {
    zajimave = `errors: ${JSON.stringify(j?.errors ?? j).slice(0, 200)}`;
  }
  p(`   ${String(r.status).padStart(3)} ${c}`);
  p(`       ${zajimave}`);
}
writeFileSync(join(WS, '_analyza/p38-b-ucet2-vystup.txt'), radky.join('\n') + '\n', 'utf8');
console.log('\n[zapsano] _analyza/p38-b-ucet2-vystup.txt');
