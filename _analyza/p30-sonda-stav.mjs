// p30-sonda-stav.mjs — JEN ČTE živou službu a uloží odpovědi jako doklad (UTF-8 bajty).
//
// PROČ: 9. 10. 2026 se při měření ztratil výstup ručního tiku (PowerShell
// `Set-Content` neměl právo zápisu) — doklad se musí zapisovat v tom procesu,
// který ho získal. Tenhle skript proto sám ukládá odpovědi do souboru.
//
// Použití:
//   node _analyza/p30-sonda-stav.mjs <jmeno-vystupu.txt> [--tik]
// Bez `--tik` se NIC nemění (jen GET endpointy).
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const out = process.argv[2] ?? "_analyza/p30-stav-vystup.txt";
const chciTik = process.argv.includes("--tik");

const env = {};
for (const l of readFileSync(join(WS, ".env"), "utf8").replace(/^\uFEFF/, "").split(/\r?\n/)) {
  if (l.includes("=") && !l.trim().startsWith("#")) {
    const i = l.indexOf("=");
    env[l.slice(0, i).trim()] = l.slice(i + 1).trim();
  }
}
const URL = String(env.FORGE_URL || "").replace(/\/$/, "");
const H = { "x-forge-secret": env.FORGE_SECRET, "content-type": "application/json" };

const radky = [];
const zapis = (x) => { radky.push(x); console.log(x); };

const volat = async (metoda, cesta, telo) => {
  const t0 = Date.now();
  try {
    const r = await fetch(URL + cesta, {
      method: metoda, headers: H,
      body: telo === undefined ? undefined : JSON.stringify(telo),
    });
    const text = await r.text();
    let b;
    try { b = JSON.parse(text); } catch { b = text.slice(0, 600); }
    return { status: r.status, ms: Date.now() - t0, body: b, last_modified: r.headers.get("last-modified") };
  } catch (e) {
    return { status: 0, ms: Date.now() - t0, chyba: String(e).slice(0, 200) };
  }
};

zapis(`# p30 sonda stavu — ${new Date().toISOString()}`);
zapis(`# URL=${URL}  tik=${chciTik}`);

const gety = ["/health", "/status", "/roadmap", "/queue"];
for (const c of gety) {
  const r = await volat("GET", c);
  zapis("");
  zapis(`## GET ${c} -> HTTP ${r.status} (${r.ms} ms)`);
  zapis(JSON.stringify(r.body, null, 1));
}

const clean = await volat("POST", "/tasks/cleanup", { dry_run: true });
zapis("");
zapis("## POST /tasks/cleanup {dry_run:true} -> JEN CTE");
zapis(JSON.stringify(clean, null, 1));

if (chciTik) {
  const tik = await volat("POST", "/tick", {});
  zapis("");
  zapis(`## POST /tick -> HTTP ${tik.status} (${tik.ms} ms)  [MENI STAV: dispatchuje praci]`);
  zapis(JSON.stringify(tik, null, 1));
  const po = await volat("POST", "/tasks/cleanup", { dry_run: true });
  zapis("");
  zapis("## POST /tasks/cleanup {dry_run:true} PO TIKU");
  zapis(JSON.stringify(po, null, 1));
  const status2 = await volat("GET", "/status");
  zapis("");
  zapis("## GET /status PO TIKU");
  zapis(JSON.stringify(status2.body, null, 1));
}

const cesta = join(WS, out);
writeFileSync(cesta, radky.join("\n") + "\n", "utf8");
console.log(`\n[zapsano] ${out} (${radky.join("\n").length} znaku)`);
