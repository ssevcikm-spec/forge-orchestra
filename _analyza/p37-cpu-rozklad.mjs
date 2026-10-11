// p37-cpu-rozklad.mjs — KOLIK CPU STOJÍ TIK: rozklad podle skutečných odpovědí GitHubu.
//
// PROČ: živé měření (P37, 11. 10. 2026 17:0xZ) ukázalo, že cron tik umírá na
// `exceededCpu` (`cpuTime = 10`, free plán) — a to UŽ OD ~13:58Z, kdy naposledy
// doběhl (`last_cron`). Conductor se přitom od 09:42Z NENASAZOVAL, takže příčina
// není v kódu, ale v DATEch, která tik zpracovává.
//
// Tenhle skript volá TYTÉŽ endpointy jako `roadmapTick` (tick je volá každou
// minutu) a měří:
//   * velikost odpovědi v bajtech (to je to, co se parsuje),
//   * čas `JSON.parse` (Node = týž engine V8 jako Workers),
//   * čas odvozené práce (Set z 100 PR / ze stromu) — ta v tiku taky je.
// Měří se medián z N běhů (default 7), aby jedno zaškobrtnutí neměnilo verdikt.
//
// ⚠ JE TO MĚŘENÍ NÁKLADU, NE DŮKAZ PŘÍČINY: lokální V8 nemá D1 ani CPU účetnictví
// Cloudflare. Co skript dokazuje, je PODÍL jednotlivých odpovědí na rozpočtu —
// a to, že součet je nad 10 ms.
//
// PAT se čte ze .secrets/github_pat.txt a NIKDY se nevypisuje.
// Použití: node _analyza/p37-cpu-rozklad.mjs [N]
// Exit 0 = měřeno.

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, "_analyza", "p37-cpu-rozklad-vystup.txt");
const HRA = "ssevcikm-spec/uo-shadows";
const ROADMAP = ".forge/roadmap.json";
const PAT = readFileSync(join(WS, ".secrets", "github_pat.txt"), "utf8").trim();
const N = Number(process.argv[2] || 7);

const radky = [];
const zapis = (x = "") => { radky.push(x); console.log(x); };
const median = (a) => { const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };

// Endpointy TAK, JAK JE VOLÁ `roadmapTick` (conductor/src/index.ts).
const CESTY = [
  ["/pulls?state=closed&per_page=100&sort=updated&direction=desc", "100 zavřených PR (merged tituly)"],
  ["/git/trees/origin%2Fmain?recursive=1", "celý strom origin/main (A2, lazy)"],
  [`/contents/${ROADMAP}`, "roadmapa hry (base64)"],
  ["/pulls?state=open&per_page=30", "30 otevřených PR (lazy)"],
  ["/actions/runs?event=workflow_dispatch&per_page=50", "50 běhů (pollRuns, jen když něco běží)"],
];

const stahni = async (cesta) => {
  const r = await fetch(`https://api.github.com/repos/${HRA}${cesta}`, {
    headers: {
      Authorization: `Bearer ${PAT}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "forge-conductor",
    },
  });
  const text = await r.text();
  return { status: r.status, text, bajtu: Buffer.byteLength(text, "utf8") };
};

zapis(`# p37 — rozklad ceny tiku podle odpovědí GitHubu — ${new Date().toISOString()}`);
zapis(`# repo: ${HRA} · medián z ${N} běhů JSON.parse · rozpočet free plánu: 10 ms CPU`);

zapis("");
zapis("## VELIKOST ODPOVĚDÍ A CENA JSON.parse");
zapis("  endpoint                                     | HTTP |    bajtů | parse medián | parse max");
const vysledky = [];
for (const [cesta, popis] of CESTY) {
  let o;
  try { o = await stahni(cesta); } catch (e) {
    zapis(`  ${cesta.slice(0, 44).padEnd(45)} | CHYBA: ${String(e).slice(0, 60)}`);
    continue;
  }
  if (o.status !== 200) {
    zapis(`  ${cesta.slice(0, 44).padEnd(45)} | HTTP ${o.status} — NEMĚŘENO`);
    continue;
  }
  const casy = [];
  let naparsovano = null;
  for (let i = 0; i < N; i++) {
    const t0 = process.hrtime.bigint();
    naparsovano = JSON.parse(o.text);
    const t1 = process.hrtime.bigint();
    casy.push(Number(t1 - t0) / 1e6);
  }
  vysledky.push({ cesta, popis, bajtu: o.bajtu, parse_median_ms: median(casy), parse_max_ms: Math.max(...casy), naparsovano });
  zapis(`  ${cesta.slice(0, 44).padEnd(45)} | ${String(o.status).padStart(4)} | ${String(o.bajtu).padStart(8)} | ${median(casy).toFixed(2).padStart(10)} ms | ${Math.max(...casy).toFixed(2).padStart(7)} ms`);
}

// ── Odvozená práce: to, co tick z odpovědí staví ────────────────────────────
zapis("");
zapis("## ODVOZENÁ PRÁCE (to, co tick z odpovědí staví)");
let soucetParsu = 0;
for (const v of vysledky) {
  soucetParsu += v.parse_median_ms;
  if (v.cesta.startsWith("/pulls?state=closed")) {
    const casy = [];
    for (let i = 0; i < N; i++) {
      const t0 = process.hrtime.bigint();
      const titles = new Set();
      let merged = 0;
      for (const pr of v.naparsovano || []) {
        const m = String(pr.head?.ref || "").match(/^forge\/task-(\d+)$/);
        if (pr.merged_at) {
          if (m) merged++;
          const t = String(pr.title || "").replace(/^Forge #\d+:\s*/, "");
          if (t) titles.add(t);
        }
      }
      const t1 = process.hrtime.bigint();
      casy.push(Number(t1 - t0) / 1e6);
    }
    zapis(`  smyčka přes ${(v.naparsovano || []).length} zavřených PR (merged tituly): medián ${median(casy).toFixed(2)} ms`);
    zapis(`     → merged PR: ${(v.naparsovano || []).filter((p) => p.merged_at).length}, unikátních titulů: ${new Set((v.naparsovano || []).filter((p) => p.merged_at).map((p) => String(p.title || ""))).size}`);
  }
  if (v.cesta.startsWith("/git/trees")) {
    const strom = v.naparsovano?.tree || [];
    const casy = [];
    for (let i = 0; i < N; i++) {
      const t0 = process.hrtime.bigint();
      const s = new Set(strom.filter((e) => e?.type === "blob").map((e) => String(e.path)));
      const t1 = process.hrtime.bigint();
      casy.push(Number(t1 - t0) / 1e6);
    }
    zapis(`  stavba Set z ${strom.length} uzlů stromu (${strom.filter((e) => e?.type === "blob").length} blobů): medián ${median(casy).toFixed(2)} ms`);
  }
  if (v.cesta.startsWith("/contents/")) {
    const obsah = String(v.naparsovano?.content || "");
    const casy = [];
    for (let i = 0; i < N; i++) {
      const t0 = process.hrtime.bigint();
      const bin = atob(obsah.replace(/\n/g, ""));
      const bytes = new Uint8Array(bin.length);
      for (let j = 0; j < bin.length; j++) bytes[j] = bin.charCodeAt(j);
      JSON.parse(new TextDecoder().decode(bytes));
      const t1 = process.hrtime.bigint();
      casy.push(Number(t1 - t0) / 1e6);
    }
    zapis(`  dekódování base64 roadmapy (${obsah.length} znaků base64): medián ${median(casy).toFixed(2)} ms  [H165 opravená cesta]`);
  }
}

zapis("");
zapis("## SOUČET (jen JSON.parse odpovědí, které tik reálně stáhne)");
zapis(`  všechny měřené endpointy: ${soucetParsu.toFixed(2)} ms`);
const realne = vysledky.filter((v) => !v.cesta.startsWith("/actions/runs") && !v.cesta.startsWith("/pulls?state=open"));
zapis(`  bez lazy endpointů (pollRuns neběží — 0 running): ${realne.reduce((a, v) => a + v.parse_median_ms, 0).toFixed(2)} ms`);
zapis(`  rozpočet free plánu: 10 ms — a do něj patří I D1 dotazy, dekódování, Set a logika.`);

writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
console.log(`\n[zapsano] ${OUT}`);
process.exit(0);
