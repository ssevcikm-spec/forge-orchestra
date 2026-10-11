// p36-cf-token-sonda.mjs — JEN ČTE: proč dnes Cloudflare Analytics vrací 401.
//
// Pozadí: při P36 běžel `p35-a-overeni.py --plne` (A3 zadání) a jeho noha A5
// naměřila u Cloudflare Analytics **HTTP 401 „Authentication error“ (kód 10000)**
// tam, kde P35 ve 10:43Z měřila **HTTP 200**. P35 tím spadl čítač z 74/0 na 73/0.
//
// Sonda zkouší DVA nezávislé zdroje přihlášení, které na stanici jsou:
//   1) `oauth_token` z konfigurace wrangleru (bere ho `p34-cf-analytika.mjs`)
//   2) `CLOUDFLARE_API_TOKEN` z `.secrets/cf-secrets.json` (bere ho deploy.yml)
// a u každého jen zapíše HTTP status a text chyby — NIKDY token.
//
// Použití: node _analyza/p36-cf-token-sonda.mjs

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, "_analyza", "p36-cf-token-vystup.txt");
const WRANGLER_CFG = "C:\\Users\\Ssevc\\AppData\\Roaming\\xdg.config\\.wrangler\\config\\default.toml";
const ACC = "b19df1f89d07d2cb5b516c95ee8919e1";
const SCRIPT = "forge-conductor";

const radky = [];
const zapis = (x = "") => { radky.push(x); console.log(x); };

const dotaz = `query Q($acc: String!, $script: String!) {
  viewer { accounts(filter: {accountTag: $acc}) {
    workersInvocationsAdaptive(limit: 2, filter: {scriptName: $script}) {
      dimensions { datetime status } sum { requests } } } } }`;

async function zkus(nazev, token) {
  if (!token) { zapis(`  ${nazev}: token NENALEZEN`); return null; }
  const r = await fetch("https://api.cloudflare.com/client/v4/graphql", {
    method: "POST",
    headers: { authorization: `Bearer ${token}`, "content-type": "application/json" },
    body: JSON.stringify({ query: dotaz, variables: { acc: ACC, script: SCRIPT } }),
  });
  const t = await r.text();
  let j = null;
  try { j = JSON.parse(t); } catch { /* necháme jako text */ }
  zapis(`  ${nazev}: HTTP ${r.status} · délka tokenu ${token.length}`);
  if (j?.errors) zapis(`    errors: ${JSON.stringify(j.errors).slice(0, 300)}`);
  if (r.status !== 200) zapis(`    tělo: ${t.slice(0, 300)}`);
  return r.status;
}

zapis(`# p36 — sonda CF tokenů — ${new Date().toISOString()}`);
zapis("");

let cfgToken = null;
try {
  const cfg = readFileSync(WRANGLER_CFG, "utf8");
  const m = cfg.match(/^\s*oauth_token\s*=\s*"([^"]+)"/m);
  cfgToken = m ? m[1] : null;
  const exp = cfg.match(/^\s*expiration_time\s*=\s*"([^"]+)"/m);
  const scopes = [...cfg.matchAll(/scopes\s*=\s*\[([^\]]*)\]/g)].map((x) => x[1]).join(" ");
  zapis(`## 1) wrangler oauth_token (${WRANGLER_CFG})`);
  zapis(`  expiration_time v konfiguraci: ${exp ? exp[1] : "(není)"}`);
  zapis(`  scopes v konfiguraci: ${scopes.replace(/\s+/g, " ").slice(0, 200) || "(žádné)"}`);
} catch (e) {
  zapis(`## 1) wrangler konfigurace se NEDÁ PŘEČÍST: ${String(e).slice(0, 120)}`);
}
const s1 = await zkus("oauth_token", cfgToken);
zapis("");

zapis("## 2) CLOUDFLARE_API_TOKEN z .secrets/cf-secrets.json");
let apiToken = null;
try {
  const j = JSON.parse(readFileSync(join(WS, ".secrets", "cf-secrets.json"), "utf8"));
  apiToken = j.CLOUDFLARE_API_TOKEN || j.api_token || null;
  zapis(`  klíče v souboru: ${Object.keys(j).join(", ")}`);
} catch (e) {
  zapis(`  soubor se NEDÁ PŘEČÍST: ${String(e).slice(0, 120)}`);
}
const s2 = await zkus("CLOUDFLARE_API_TOKEN", apiToken);
zapis("");

zapis("## ZÁVĚR (měřený, ne odhadnutý)");
zapis(`  oauth_token -> ${s1 ?? "NEMĚŘENO"} · CLOUDFLARE_API_TOKEN -> ${s2 ?? "NEMĚŘENO"}`);

writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
console.log(`\n[zapsano] ${OUT} (${radky.join("\n").length} znaku)`);
