// Dry-run resetu roadmapy: co by se smazalo, než se to opravdu stane.
import { readFileSync } from 'node:fs';

const env = readFileSync('C:/Users/Ssevc/Local-Deepseek/orchestra/.env', 'utf8').replace(/^\uFEFF/, '');
const get = (k) => {
  for (const radek of env.split(/\r?\n/)) {
    if (radek.startsWith(k + '=')) return radek.slice(k.length + 1).trim();
  }
  return '';
};
const URL = get('FORGE_URL');
const SEC = get('FORGE_SECRET');

const posli = async (telo, popis) => {
  const r = await fetch(`${URL}/roadmap/reset`, {
    method: 'POST',
    headers: { 'x-forge-secret': SEC, 'content-type': 'application/json' },
    body: JSON.stringify(telo),
  });
  console.log(`--- ${popis} -> HTTP ${r.status} ---`);
  console.log(await r.text());
};

await posli({ game_id: 'uo-shadows', dry_run: true }, 'DRY-RUN (nic se nemění)');
