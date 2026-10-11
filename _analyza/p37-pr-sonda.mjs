// p37-pr-sonda.mjs — PROČ TIK UMÍRÁ NA CPU: kolik zavřených PR se v tiku parsuje.
//
// `roadmapTick` volá na KAŽDÉM tiku (každou minutu):
//   /pulls?state=closed&per_page=100&sort=updated&direction=desc
// a odpověď je VELKÁ (P37 naměřila 599 722 B za 36 PR = 16,6 kB na PR, protože
// PR objekt nese i `head.repo`/`base.repo`). Cena roste s POČTEM zavřených PR.
//
// Tenhle skript měří:
//   * kolik PR je zavřených a jak jsou velcí/staří (kdy přibyly),
//   * celkový počet PR (open+closed) a čas posledních zavření/aktualizací,
//   * zda jde načíst strom `origin/main` OBĚMA tvary refu (`origin/main` vs `main`)
//     — kód volá `origin%2Fmain`, což je jméno LOKÁLNÍHO remote-tracking refu,
//     ne refu na GitHubu; když vrací 404, je ta větev MRTVÁ.
//
// Použití: node _analyza/p37-pr-sonda.mjs
// Exit 0 = měřeno.

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, "_analyza", "p37-pr-sonda-vystup.txt");
const HRA = "ssevcikm-spec/uo-shadows";
const PAT = readFileSync(join(WS, ".secrets", "github_pat.txt"), "utf8").trim();

const radky = [];
const zapis = (x = "") => { radky.push(x); console.log(x); };

const api = async (cesta) => {
  const r = await fetch(`https://api.github.com/repos/${HRA}${cesta}`, {
    headers: { Authorization: `Bearer ${PAT}`, Accept: "application/vnd.github+json", "User-Agent": "forge-p37-sonda" },
  });
  const text = await r.text();
  return { status: r.status, bajtu: Buffer.byteLength(text, "utf8"), json: r.ok ? JSON.parse(text) : null, text };
};

zapis(`# p37 — zavřené PR hry (${HRA}) — ${new Date().toISOString()}`);

// ── 1) to, co tik skutečně parsuje ─────────────────────────────────────────
const zavrene = await api("/pulls?state=closed&per_page=100&sort=updated&direction=desc");
zapis("");
zapis(`## /pulls?state=closed&per_page=100&sort=updated&direction=desc → HTTP ${zavrene.status}, ${zavrene.bajtu} B`);
if (zavrene.json) {
  const prs = zavrene.json;
  zapis(`   PR v odpovědi: ${prs.length}  → ${(zavrene.bajtu / Math.max(prs.length, 1)).toFixed(0)} B/PR`);
  zapis("");
  zapis("## KDY BYLY ZAVŘENÉ / NAPOSLEDY AKTUALIZOVANÉ (to rozhoduje o VELIKOSTI odpovědi)");
  const podleDne = new Map();
  for (const p of prs) {
    const den = String(p.closed_at || p.updated_at || "?").slice(0, 10);
    podleDne.set(den, (podleDne.get(den) || 0) + 1);
  }
  for (const [d, n] of [...podleDne.entries()].sort()) zapis(`   ${d}: ${n} PR`);
  zapis("");
  zapis("## POSLEDNÍCH 15 ZAVŘENÝCH (podle closed_at) — 'updated_at' ukazuje, co přibylo NAPOSLED");
  const podleClosed = prs.filter((p) => p.closed_at).sort((a, b) => String(b.closed_at).localeCompare(String(a.closed_at)));
  for (const p of podleClosed.slice(0, 15)) {
    zapis(`   #${String(p.number).padStart(3)} | closed ${p.closed_at} | updated ${p.updated_at} | merged ${p.merged_at ? "ANO" : "ne"} | ${String(p.title).slice(0, 60)}`);
  }
  zapis("");
  zapis("## POSLEDNÍCH 15 AKTUALIZOVANÝCH");
  const podleUpd = [...prs].sort((a, b) => String(b.updated_at).localeCompare(String(a.updated_at)));
  for (const p of podleUpd.slice(0, 15)) {
    zapis(`   #${String(p.number).padStart(3)} | updated ${p.updated_at} | closed ${p.closed_at ?? "-"} | merged ${p.merged_at ? "ANO" : "ne"} | ${String(p.title).slice(0, 55)}`);
  }
}

// ── 2) kolik PR existuje CELKEM (roste počet → roste cena tiku) ─────────────
const vsechny = await api("/pulls?state=all&per_page=1");
zapis("");
zapis(`## CELKEM PR (open+closed) — jen hlavička, bez těla`);
zapis(`   HTTP ${vsechny.status} (počet je v hlavičce, ne v těle — měřeno přes search API níž)`);
const hledani = await api("/pulls?state=closed&per_page=1&sort=created&direction=asc");
if (hledani.json) {
  zapis(`   nejstarší zavřený PR: #${hledani.json[0]?.number} (${hledani.json[0]?.created_at})`);
}

// ── 3) MRTVÁ VĚTEV? strom `origin/main` vs `main` ─────────────────────────
zapis("");
zapis("## STROM `origin/main` (kód volá `origin%2Fmain`) vs `main`");
for (const ref of ["origin%2Fmain", "main", "HEAD"]) {
  const t = await api(`/git/trees/${ref}?recursive=1`);
  let blobu = "?";
  if (t.json?.tree) blobu = t.json.tree.filter((e) => e.type === "blob").length;
  zapis(`   /git/trees/${ref.padEnd(14)} → HTTP ${t.status}, ${String(t.bajtu).padStart(9)} B, blobů: ${blobu}${t.status !== 200 ? "   ⚠ KÓD TADY DOSTANE `null` = NEVÍME" : ""}`);
}

writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
console.log(`\n[zapsano] ${OUT}`);
process.exit(0);
