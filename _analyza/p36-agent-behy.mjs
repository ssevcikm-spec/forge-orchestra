// p36-agent-behy.mjs — ŽIVĚ z GitHub API: proč selhaly běhy, které spálily granule.
//
// Zadání P36 §2.2: „Zjisti z D1/`/failed`/`/status`, proč tytéž granule selhaly
// 8×.“ D1 má u všech 24 běhů `summary = 'GitHub Actions: failure'` a `log_tail`
// PRÁZDNÝ — takže příčina v D1 NENÍ. Tenhle skript ji hledá tam, kde vznikla:
// v bězích workflow `agent.yml` v repu HRY (payload.repo = ssevcikm-spec/uo-shadows).
//
// PAT se čte ze souboru .secrets/github_pat.txt a NIKDY se nevypisuje.
//
// Použití:
//   node _analyza/p36-agent-behy.mjs            # seznam + KLASIFIKACE všech 29 běhů
//   node _analyza/p36-agent-behy.mjs --logy     # navíc logy (1 zástupce za třídu)
//
// Exit 0 = měřeno (i když běhy selhaly); 1 = měření neproběhlo (HTTP chyba).

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, "_analyza", "p36-agent-behy-vystup.txt");
const HRA = "ssevcikm-spec/uo-shadows";
const PAT = readFileSync(join(WS, ".secrets", "github_pat.txt"), "utf8").trim();
const CHCI_LOGY = process.argv.includes("--logy");

const radky = [];
const zapis = (x = "") => { radky.push(x); console.log(x); };
const jenRadek = (s) => String(s ?? "").replace(/\s+/g, " ").trim();

const api = async (cesta, jakoText = false) => {
  const r = await fetch(`https://api.github.com${cesta}`, {
    headers: {
      Authorization: `Bearer ${PAT}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "forge-p36-sonda",
    },
  });
  if (!r.ok) throw new Error(`${cesta} -> HTTP ${r.status} ${(await r.text()).slice(0, 200)}`);
  return jakoText ? r.text() : r.json();
};

zapis(`# p36 — běhy agenta v repu hry (${HRA}) — ${new Date().toISOString()}`);

// ── 1) běhy agent.yml ───────────────────────────────────────────────────────
const vsechny = [];
for (let strana = 1; strana <= 6; strana++) {
  const d = await api(`/repos/${HRA}/actions/workflows/agent.yml/runs?per_page=100&page=${strana}`);
  vsechny.push(...d.workflow_runs);
  if (d.workflow_runs.length < 100) break;
}

zapis("");
zapis(`## POSLEDNÍCH 20 BĚHŮ agent.yml (celkem ${vsechny.length})`);
zapis("  #run | status    | conclusion | created_at           | název");
for (const r of vsechny.slice(0, 20)) {
  zapis(`  ${String(r.run_number).padStart(4)} | ${String(r.status).padEnd(9)} | ` +
    `${String(r.conclusion ?? "-").padEnd(10)} | ${r.created_at} | ${jenRadek(r.display_title).slice(0, 55)}`);
}

// ── 1b) kdy naposledy agent USPOĚL (a jak vypadá posledních 100 běhů) ───────
const uspesne = await api(`/repos/${HRA}/actions/workflows/agent.yml/runs?status=success&per_page=10`);
zapis("");
zapis(`## POSLEDNÍ ÚSPĚŠNÉ BĚHY agent.yml (total_count=${uspesne.total_count})`);
if (!uspesne.workflow_runs.length) zapis("  (ŽÁDNÝ úspěšný běh v historii workflow)");
for (const r of uspesne.workflow_runs) {
  zapis(`  #${r.run_number} | ${r.created_at} | ${jenRadek(r.display_title).slice(0, 60)}`);
}
const poslednich100 = vsechny.slice(0, 100);
const podleVysledku = new Map();
for (const r of poslednich100) {
  const k = r.conclusion ?? r.status;
  podleVysledku.set(k, (podleVysledku.get(k) || 0) + 1);
}
zapis("");
zapis(`## VÝSLEDKY POSLEDNÍCH ${poslednich100.length} BĚHŮ (od ${poslednich100.at(-1)?.created_at} do ${poslednich100[0]?.created_at})`);
for (const [k, n] of [...podleVysledku.entries()].sort((a, b) => b[1] - a[1])) {
  zapis(`  ${String(n).padStart(3)}×  ${k}`);
}

// ── 2) běhy úloh #240–#246 (granule nad stropem) ────────────────────────────
const CIL = ["#240", "#241", "#242", "#243", "#244", "#245", "#246"];
const nalezy = vsechny
  .filter((r) => CIL.some((c) => (r.display_title || "").includes(c)))
  .sort((a, b) => a.created_at.localeCompare(b.created_at));

zapis("");
zapis(`## BĚHY ÚLOH ${CIL.join(", ")}: ${nalezy.length}`);

// ── 3) KLASIFIKACE: který job/krok selhal ───────────────────────────────────
zapis("");
zapis("## KLASIFIKACE (job + selhaný krok)");
const tridy = new Map();
const chybyMereni = [];
for (const beh of nalezy) {
  const uloha = (beh.display_title || "").match(/#\d+/)?.[0] ?? "?";
  let joby = [];
  try {
    joby = (await api(`/repos/${HRA}/actions/runs/${beh.id}/jobs`)).jobs || [];
  } catch (e) {
    chybyMereni.push(`${beh.id}: ${String(e).slice(0, 120)}`);
    zapis(`  ${String(beh.run_number).padStart(4)} ${uloha}  ?? NELZE ZJISTIT: ${String(e).slice(0, 100)}`);
    continue;
  }
  let trida = "NEZJIŠTĚNO";
  for (const j of joby) {
    for (const s of j.steps || []) {
      if (s.conclusion && s.conclusion !== "success" && s.conclusion !== "skipped") {
        trida = `${j.name} → ${s.number}. ${s.name}`;
      }
    }
    if (trida === "NEZJIŠTĚNO" && j.conclusion && j.conclusion !== "success" && j.conclusion !== "skipped") {
      trida = `${j.name} → (job ${j.conclusion})`;
    }
  }
  tridy.set(trida, (tridy.get(trida) || 0) + 1);
  zapis(`  ${String(beh.run_number).padStart(4)} ${uloha} | ${beh.created_at} | ${trida}`);
}

zapis("");
zapis("## SOUHRN PODLE TŘÍDY");
for (const [t, n] of [...tridy.entries()].sort((a, b) => b[1] - a[1])) {
  zapis(`  ${String(n).padStart(3)}×  ${t}`);
}
if (chybyMereni.length) {
  zapis("");
  zapis(`!! ${chybyMereni.length} běhů se NEPODAŘILO klasifikovat (měření je NEÚPLNÉ):`);
  for (const c of chybyMereni) zapis(`   ${c}`);
}

// ── 3b) (--vsechny) klasifikace VŠECH selhaných běhů z poslední stovky ──────
if (process.argv.includes("--vsechny")) {
  const selhane = vsechny.slice(0, 100).filter((r) => r.conclusion && r.conclusion !== "success");
  zapis("");
  zapis(`## KLASIFIKACE VŠECH SELHANÝCH BĚHŮ Z POSLEDNÍ STOVKY (${selhane.length})`);
  const vsechnyTridy = new Map();
  const podleDne = new Map();
  const chyby2 = [];
  for (const beh of selhane) {
    let joby = [];
    try {
      joby = (await api(`/repos/${HRA}/actions/runs/${beh.id}/jobs`)).jobs || [];
    } catch (e) { chyby2.push(`${beh.id}: ${String(e).slice(0, 90)}`); continue; }
    let trida = "NEZJIŠTĚNO";
    for (const j of joby) {
      for (const s of j.steps || []) {
        if (s.conclusion && s.conclusion !== "success" && s.conclusion !== "skipped") trida = `${j.name} → ${s.name}`;
      }
    }
    vsechnyTridy.set(trida, (vsechnyTridy.get(trida) || 0) + 1);
    const den = beh.created_at.slice(0, 10);
    if (!podleDne.has(den)) podleDne.set(den, new Map());
    const dm = podleDne.get(den);
    dm.set(trida, (dm.get(trida) || 0) + 1);
  }
  zapis("");
  zapis("### SOUHRN CELÉ STOVKY");
  for (const [t, n] of [...vsechnyTridy.entries()].sort((a, b) => b[1] - a[1])) {
    zapis(`  ${String(n).padStart(3)}×  ${t}`);
  }
  zapis("");
  zapis("### PODLE DNE");
  for (const [den, m] of [...podleDne.entries()].sort()) {
    zapis(`  ${den}: ` + [...m.entries()].map(([t, n]) => `${n}× ${t}`).join(" | "));
  }
  if (chyby2.length) zapis(`\n!! ${chyby2.length} běhů nešlo klasifikovat (NEÚPLNÉ měření)`);
}

// ── 4) logy: jeden zástupce za třídu ────────────────────────────────────────
if (CHCI_LOGY) {
  zapis("");
  zapis("## LOGY — 1 ZÁSTUPCE ZA TŘÍDU");
  const VZOR = /(error|Error|ERROR|fatal|FATAL|RateLimitError|exit code|nezměnil|neni|není)/;
  const videne = new Set();
  for (const beh of nalezy) {
    const joby = (await api(`/repos/${HRA}/actions/runs/${beh.id}/jobs`)).jobs || [];
    for (const j of joby) {
      if (j.conclusion === "success" || j.conclusion === "skipped") continue;
      const klic = `${j.name} → ${(j.steps || []).filter((s) => s.conclusion === "failure").map((s) => s.name).join(",")}`;
      if (videne.has(klic)) continue;
      videne.add(klic);
      zapis("");
      zapis(`### ${klic}   (běh #${beh.run_number}, úloha ${(beh.display_title || "").match(/#\d+/)?.[0]})`);
      zapis(`    ${beh.html_url}`);
      let log = "";
      try {
        log = await api(`/repos/${HRA}/actions/jobs/${j.id}/logs`, true);
      } catch (e) {
        zapis(`    (log nejde stáhnout: ${String(e).slice(0, 140)})`);
        continue;
      }
      const cist = log.replace(/\x1b\[[0-9;]*m/g, "").split(/\r?\n/);
      const zaj = cist.filter((l) => VZOR.test(l));
      zapis(`    (${cist.length} řádků, zajímavých ${zaj.length})`);
      for (const l of zaj.slice(0, 25)) zapis(`    ${jenRadek(l).slice(0, 200)}`);
      zapis(`    --- POSLEDNÍCH 4 ŘÁDKY:`);
      for (const l of cist.slice(-4)) zapis(`    ${jenRadek(l).slice(0, 200)}`);
    }
  }
}

writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
console.log(`\n[zapsano] ${OUT} (${radky.join("\n").length} znaku)`);
process.exit(chybyMereni.length ? 1 : 0);
