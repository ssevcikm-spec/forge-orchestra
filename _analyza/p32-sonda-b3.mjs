// p32-sonda-b3.mjs — ÚKOL B3: OVĚŘENÍ „B4" (bez aktivní hry se nedispatchuje) NA ŽIVÉ SLUŽBĚ.
//
// ⚠ TENHLE SKRIPT MĚNÍ STAV ŽIVÉ SLUŽBY: dočasně vypne aktivní hru
// (`POST /game/active {game_id, active:false}`) a v `finally` ji VŽDY zase zapne.
// Uživatel k tomu dal výslovné „ano" (B3 to vyžaduje — dočasně to zastaví orchestra).
//
// CO SE MĚŘÍ (a proč zrovna takhle):
//   1. PŘED:  /games (aktivní hra) · /health (games) · /tasks/cleanup {dry_run}
//   2. VYPNUTO: /health musí hlásit games=0; `POST /tick` musí říct
//      „žádná AKTIVNÍ hra → nedispatchuji (B4)" a spustit 0 úloh;
//      `/tasks/cleanup {dry_run}` musí vrátit 503 — což je ZÁROVEŇ živý důkaz
//      nálezu H128 (cleanup bere jen hry `active = 1`, takže s vypnutou hrou
//      neudělá nic — a doporučené pořadí v komentáři `index.ts:1558–1559`
//      je tím neproveditelné).
//   3. PO ZAPNUTÍ: /health zpět games≥1, tik bez hlášky B4, cleanup 200.
//
// Použití: node _analyza/p32-sonda-b3.mjs [jmeno-vystupu.txt]
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const out = process.argv[2] ?? "_analyza/p32-b3-vystup.txt";

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
const zapis = (x = "") => { radky.push(x); console.log(x); };
const uloz = () => writeFileSync(join(WS, out), radky.join("\n") + "\n", "utf8");

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
    return { status: r.status, ms: Date.now() - t0, body: b };
  } catch (e) {
    return { status: 0, ms: Date.now() - t0, chyba: String(e).slice(0, 200) };
  }
};

const her = (games) => (games || []).filter((g) => g.active === 1 || g.active === true);
const textTiku = (r) => (r.body && typeof r.body === "object"
  ? JSON.stringify(r.body) : String(r.body ?? ""));

zapis(`# P32 — sonda B3: ověření B4 na ŽIVÉ SLUŽBĚ — ${new Date().toISOString()}`);
zapis(`# URL=${URL}   (skript dočasně vypne aktivní hru a v finally ji zase zapne)`);

// ── 1) PŘED ────────────────────────────────────────────────────────────────
const g0 = await volat("GET", "/games");
const h0 = await volat("GET", "/health");
const c0 = await volat("POST", "/tasks/cleanup", { dry_run: true });
const aktivni = her(g0.body?.games);
zapis("");
zapis(`## PŘED — GET /games -> HTTP ${g0.status}, her celkem ${(g0.body?.games || []).length}, aktivních ${aktivni.length}`);
zapis(JSON.stringify(g0.body, null, 1));
zapis(`## PŘED — GET /health -> HTTP ${h0.status}`);
zapis(JSON.stringify(h0.body, null, 1));
zapis(`## PŘED — POST /tasks/cleanup {dry_run:true} -> HTTP ${c0.status}`);
zapis(JSON.stringify(c0.body, null, 1));

if (!aktivni.length) {
  zapis("");
  zapis("CHYBA: v registru není ŽÁDNÁ aktivní hra — není co vypnout; sonda končí (nic se nezměnilo).");
  uloz();
  process.exit(2);
}
const hra = aktivni[0];
zapis(`# vypínám hru: ${hra.game_id} (repo ${hra.repo}, roadmap_file ${hra.roadmap_file})`);

// ── 2) VYPNOUT + MĚŘIT + (VŽDY) ZAPNOUT ────────────────────────────────────
// ⚠ Proměnné MUSÍ být deklarované VNĚ `try` — `const` uvnitř bloku není
// vidět ve `finally` (naměřeno 9. 10. 2026: sonda spadla na `h1 is not defined`
// a doklad se neuložil, ačkoli měření i návrat stavu proběhly správně).
const vs = { obnoveno: false, hlaska_b4: false, tik_off: null, c_off: null };
const off = await volat("POST", "/game/active", { game_id: hra.game_id, active: false });
zapis("");
zapis(`## POST /game/active {game_id:"${hra.game_id}", active:false} -> HTTP ${off.status}  [MĚNÍ STAV]`);
zapis(JSON.stringify(off.body, null, 1));
let g1, h1, t1, c1, on, g2, h2, t2, c2;
try {
  g1 = await volat("GET", "/games");
  h1 = await volat("GET", "/health");
  t1 = await volat("POST", "/tick", {});
  c1 = await volat("POST", "/tasks/cleanup", { dry_run: true });
  zapis("");
  zapis(`## VYPNUTO — GET /health -> HTTP ${h1.status}`);
  zapis(JSON.stringify(h1.body, null, 1));
  zapis(`## VYPNUTO — GET /games: aktivních ${her(g1.body?.games).length}`);
  zapis(`## VYPNUTO — POST /tick -> HTTP ${t1.status}  [jinak MĚNÍ STAV; teď nesmí dispatchovat]`);
  zapis(textTiku(t1));
  zapis(`## VYPNUTO — POST /tasks/cleanup {dry_run:true} -> HTTP ${c1.status}`);
  zapis(JSON.stringify(c1.body, null, 1));
  vs.tik_off = t1;
  vs.c_off = c1;
  vs.hlaska_b4 = textTiku(t1).includes("nedispatchuji (B4)");
} finally {
  on = await volat("POST", "/game/active", { game_id: hra.game_id, active: true });
  g2 = await volat("GET", "/games");
  h2 = await volat("GET", "/health");
  t2 = await volat("POST", "/tick", {});
  c2 = await volat("POST", "/tasks/cleanup", { dry_run: true });
  zapis("");
  zapis(`## ZPĚT ZAPNUTO — POST /game/active {active:true} -> HTTP ${on.status}  [MĚNÍ STAV]`);
  zapis(JSON.stringify(on.body, null, 1));
  zapis(`## PO ZAPNUTÍ — GET /health -> HTTP ${h2.status}: games=${h2.body?.games}`);
  zapis(`## PO ZAPNUTÍ — GET /games: aktivních ${her(g2.body?.games).length}`);
  zapis(`## PO ZAPNUTÍ — POST /tick -> HTTP ${t2.status}`);
  zapis(textTiku(t2));
  zapis(`## PO ZAPNUTÍ — POST /tasks/cleanup {dry_run:true} -> HTTP ${c2.status}`);
  zapis(JSON.stringify(c2.body, null, 1));
  vs.obnoveno = on.status === 200 && her(g2.body?.games).length >= 1 && (h2.body?.games ?? 0) >= 1;
  vs.h1 = h1; vs.c1 = c1; vs.h2 = h2; vs.c2 = c2; vs.h0 = h0; vs.c0 = c0;
  vs.tik_on = t2; vs.on = on;
}

// ── 3) VYHODNOCENÍ ─────────────────────────────────────────────────────────
const kontroly = [
  ["PŘED: registr má ≥1 aktivní hru", aktivni.length >= 1],
  ["PŘED: /health hlásí games ≥ 1", (h0.body?.games ?? 0) >= 1],
  ["PŘED: cleanup {dry_run} → 200", c0.status === 200],
  ["VYPNUTO: /health hlásí games = 0 (B4 guard)", (vs.h1?.body?.games ?? -1) === 0],
  ["VYPNUTO: tik to ŘEKNE — „nedispatchuji (B4)\"", vs.hlaska_b4],
  ["VYPNUTO: tik nespustil žádnou úlohu", /spusteno:\s*0\s*úloh/.test(textTiku(vs.tik_off))],
  ["VYPNUTO: cleanup → 503 (H128: bere jen aktivní hry)", vs.c_off?.status === 503],
  ["PO ZAPNUTÍ: hra je zase aktivní", vs.obnoveno],
];
zapis("");
zapis("=".repeat(78));
zapis("VYHODNOCENÍ (každý bod je měřený, ne odhadnutý)");
zapis("=".repeat(78));
let chyb = 0;
for (const [popis, ok] of kontroly) {
  zapis(`  ${ok ? "OK   " : "CHYBA"} ${popis}`);
  if (!ok) chyb++;
}
zapis("");
zapis(`VÝSLEDEK: ${kontroly.length} kontrol, ${chyb} chyb`);
zapis(`STAV SLUŽBY: hra ${hra.game_id} = ${vs.obnoveno ? "AKTIVNÍ (obnoveno)" : "⚠ NEVRÁCENA DO PŮVODNÍHO STAVU"}`);
uloz();
console.log(`\n[zapsano] ${out}`);
process.exit(vs.obnoveno ? (chyb ? 1 : 0) : 2);
