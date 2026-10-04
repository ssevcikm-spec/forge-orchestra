// H17 — podvrh conductora pro ověření měřidla C1 (`a3-kontrola.mjs`, sekce D).
//
// PROČ VLASTNÍ PODVRH: `c1-dukaz-selhani.py` podvrhuje tak, že PŘEPÍŠE soubor
// `a3-kontrola.mjs` a pak ho vrátí. Tady se nemění NIC v repu — spustí se
// lokální HTTP server, který odpovídá stejnými TVARY jako živý conductor,
// jen `/queue` vrátí to, co vracelo staré (vadné) měřidlo: rozcestník služby.
//
// Použití:  node _analyza/h17-podvrh-conductor.mjs <port>
import { readFileSync } from 'node:fs';
import { createServer } from 'node:http';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const env = Object.fromEntries(
  readFileSync(`${ORCH}/.env`, 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);

// ŽIVÝ conductor: co OPRAVDU odpovídá (tvary, ne hodnoty).
const zive = {};
for (const cesta of ['/health', '/roadmap', '/queue']) {
  const r = await fetch(`${env.FORGE_URL}${cesta}`, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
  zive[cesta] = r.ok ? await r.json() : { chyba: r.status };
}
const rq = zive['/queue'];
const fronta = Array.isArray(rq) ? rq : (rq.tasks || []);
console.log(`[podvrh] zive: /health ok=${zive['/health']?.ok} /roadmap radku=${(zive['/roadmap']?.roadmap || []).length} /queue uloh=${fronta.length}`);
console.log(`[podvrh] /queue prvni uloha: ${JSON.stringify(fronta[0] || null).slice(0, 160)}`);

// PODVRH: přesně to, co vracel neexistující endpoint `/tasks` — rozcestník.
const ROZCESTNIK = {
  service: 'forge-conductor',
  endpoints: ['/health', '/tick', '/report', '/queue', '/roadmap', '/game', '/tasks/cleanup'],
  poznamka: 'PODVRH pro H17: neexistujici endpoint /tasks vraci rozcestnik sluzby',
};

const port = Number(process.argv[2] || 8791);
const prichozi = [];
const server = createServer((req, res) => {
  const cesta = req.url.split('?')[0];
  prichozi.push(cesta);
  let telo;
  if (cesta === '/queue') telo = ROZCESTNIK;         // <<< VADNÝ TVAR
  else if (zive[cesta] !== undefined) telo = zive[cesta];
  else telo = { service: 'forge-conductor', endpoints: [] };
  console.log(`[podvrh] ${cesta} -> ${Array.isArray(telo) ? `pole(${telo.length})` : JSON.stringify(telo).slice(0, 90)}`);
  res.writeHead(200, { 'content-type': 'application/json' });
  res.end(JSON.stringify(telo));
});
server.listen(port, '127.0.0.1', () => console.log(`[podvrh] bezi na http://127.0.0.1:${port}`));

for (const sig of ['SIGINT', 'SIGTERM']) {
  process.on(sig, () => { console.log(`[podvrh] prijato ${sig}, koncim`); server.close(() => process.exit(0)); });
}
