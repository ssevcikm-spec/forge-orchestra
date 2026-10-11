// p37-agent-behy.mjs — ŽIVĚ z GitHub API: které příčiny výpadku jsou DNES živé.
//
// Zadání P37 §2.2 (VÝPADEK): „Nejdřív ZMĚŘ, které ze čtyř příčin jsou dnes živé.“
// P36 to naměřila k 9. 10. 19:42Z (poslední běh) — tenhle skript měří TOTÉŽ
// znovu a navíc odděluje:
//   * běhy z POSLEDNÍ STOVKY (kontext P36) — pro srovnání čísel,
//   * běhy vytvořené PO <prah> (default 2026-10-09T20:00:00Z) — tj. co se dělo
//     PO posledním běhu, který P36 viděla. Když je seznam prázdný, orchestra
//     v tom okně NEVYTVOŘILA ANI JEDEN BĚH — a to je měření, ne dohad.
//
// PAT se čte ze .secrets/github_pat.txt a NIKDY se nevypisuje.
//
// Použití:
//   node _analyza/p37-agent-behy.mjs                     # seznam + stovka + klasifikace
//   node _analyza/p37-agent-behy.mjs --vsechny            # klasifikace VŠECH selhaných ze stovky
//   node _analyza/p37-agent-behy.mjs --od 2026-10-09T20:00:00Z
//   node _analyza/p37-agent-behy.mjs --logy               # navíc logy (1 zástupce za třídu)
//
// Exit 0 = měřeno (i když běhy selhaly); 1 = měření neproběhlo úplně (HTTP chyba).

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, "_analyza", "p37-agent-behy-vystup.txt");
const HRA = "ssevcikm-spec/uo-shadows";
const PAT = readFileSync(join(WS, ".secrets", "github_pat.txt"), "utf8").trim();
const CHCI_LOGY = process.argv.includes("--logy");

const iOd = process.argv.indexOf("--od");
const PRAH = iOd >= 0 ? process.argv[iOd + 1] : "2026-10-09T20:00:00Z";

const radky = [];
const zapis = (x = "") => { radky.push(x); console.log(x); };
const jenRadek = (s) => String(s ?? "").replace(/\s+/g, " ").trim();

const api = async (cesta, jakoText = false) => {
  const r = await fetch(`https://api.github.com${cesta}`, {
    headers: {
      Authorization: `Bearer ${PAT}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "forge-p37-sonda",
    },
  });
  if (!r.ok) throw new Error(`${cesta} -> HTTP ${r.status} ${(await r.text()).slice(0, 200)}`);
  return jakoText ? r.text() : r.json();
};

// Klasifikace jednoho běhu: job → selhaný krok (pojmenovaně).
const klasifikuj = async (beh) => {
  const joby = (await api(`/repos/${HRA}/actions/runs/${beh.id}/jobs`)).jobs || [];
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
  return trida;
};

zapis(`# p37 — běhy agenta v repu hry (${HRA}) — ${new Date().toISOString()}`);
zapis(`# práh pro „čerstvé běhy“ (--od): ${PRAH}`);

// ── 1) všechny běhy agent.yml ───────────────────────────────────────────────
const vsechny = [];
for (let strana = 1; strana <= 6; strana++) {
  const d = await api(`/repos/${HRA}/actions/workflows/agent.yml/runs?per_page=100&page=${strana}`);
  vsechny.push(...d.workflow_runs);
  if (d.workflow_runs.length < 100) break;
}

zapis("");
zapis(`## CELKEM BĚHŮ agent.yml VIDITELNÝCH PŘES API: ${vsechny.length}`);
zapis(`   nejnovější běh: #${vsechny[0]?.run_number} | ${vsechny[0]?.created_at} | ` +
  `${vsechny[0]?.conclusion ?? vsechny[0]?.status} | ${jenRadek(vsechny[0]?.display_title).slice(0, 70)}`);
zapis(`   nejstarší viditelný: #${vsechny.at(-1)?.run_number} | ${vsechny.at(-1)?.created_at}`);

zapis("");
zapis("## POSLEDNÍCH 20 BĚHŮ");
zapis("  #run | status    | conclusion | created_at           | název");
for (const r of vsechny.slice(0, 20)) {
  zapis(`  ${String(r.run_number).padStart(4)} | ${String(r.status).padEnd(9)} | ` +
    `${String(r.conclusion ?? "-").padEnd(10)} | ${r.created_at} | ${jenRadek(r.display_title).slice(0, 55)}`);
}

// ── 1b) poslední úspěch + výsledky stovky ──────────────────────────────────
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

// ── 2) ČERSTVÉ BĚHY: co se stalo PO prahu ──────────────────────────────────
const cerstve = vsechny.filter((r) => r.created_at > PRAH);
zapis("");
zapis(`## ČERSTVÉ BĚHY (created_at > ${PRAH}): ${cerstve.length}`);
if (!cerstve.length) {
  zapis("  ⚠ ŽÁDNÝ — orchestra v tom okně NEVYTVOŘILA ANI JEDEN BĚH agenta.");
  zapis("    To znamená: ani jedna ze čtyř příčin NEBĚŽELA, protože se nespustilo nic.");
} else {
  const tridyC = new Map();
  const chybyC = [];
  for (const beh of cerstve) {
    let t;
    try { t = await klasifikuj(beh); } catch (e) { chybyC.push(`${beh.id}: ${String(e).slice(0, 90)}`); continue; }
    tridyC.set(t, (tridyC.get(t) || 0) + 1);
    zapis(`  ${String(beh.run_number).padStart(4)} | ${beh.created_at} | ${beh.conclusion} | ${t}`);
  }
  zapis("");
  zapis("### SOUHRN ČERSTVÝCH");
  for (const [t, n] of [...tridyC.entries()].sort((a, b) => b[1] - a[1])) zapis(`  ${String(n).padStart(3)}×  ${t}`);
  if (chybyC.length) zapis(`!! ${chybyC.length} čerstvých běhů nešlo klasifikovat (NEÚPLNÉ)`);
}

// ── 3) klasifikace VŠECH selhaných z poslední stovky ───────────────────────
if (process.argv.includes("--vsechny")) {
  const selhane = poslednich100.filter((r) => r.conclusion && r.conclusion !== "success");
  zapis("");
  zapis(`## KLASIFIKACE VŠECH SELHANÝCH BĚHŮ Z POSLEDNÍ STOVKY (${selhane.length})`);
  const vsechnyTridy = new Map();
  const podleDne = new Map();
  const chyby2 = [];
  for (const beh of selhane) {
    let t;
    try { t = await klasifikuj(beh); } catch (e) { chyby2.push(`${beh.id}: ${String(e).slice(0, 90)}`); continue; }
    vsechnyTridy.set(t, (vsechnyTridy.get(t) || 0) + 1);
    const den = beh.created_at.slice(0, 10);
    if (!podleDne.has(den)) podleDne.set(den, new Map());
    const dm = podleDne.get(den);
    dm.set(t, (dm.get(t) || 0) + 1);
  }
  zapis("");
  zapis("### SOUHRN CELÉ STOVKY");
  for (const [t, n] of [...vsechnyTridy.entries()].sort((a, b) => b[1] - a[1])) zapis(`  ${String(n).padStart(3)}×  ${t}`);
  zapis("");
  zapis("### PODLE DNE");
  for (const [den, m] of [...podleDne.entries()].sort()) {
    zapis(`  ${den}: ` + [...m.entries()].map(([t, n]) => `${n}× ${t}`).join(" | "));
  }
  if (chyby2.length) zapis(`\n!! ${chyby2.length} běhů nešlo klasifikovat (NEÚPLNÉ měření)`);
}

// ── 4) logy: jeden zástupce za třídu z celé stovky ─────────────────────────
if (CHCI_LOGY) {
  zapis("");
  zapis("## LOGY — 1 ZÁSTUPCE ZA TŘÍDU (z poslední stovky)");
  const VZOR = /(error|Error|ERROR|fatal|FATAL|RateLimitError|exit code|nezměnil|neni|není|could not read|401|403|Bad credentials)/;
  const videne = new Set();
  for (const beh of poslednich100.slice(0, 60)) {
    if (beh.conclusion === "success") continue;
    let joby = [];
    try { joby = (await api(`/repos/${HRA}/actions/runs/${beh.id}/jobs`)).jobs || []; } catch { continue; }
    for (const j of joby) {
      if (j.conclusion === "success" || j.conclusion === "skipped") continue;
      const klic = `${j.name} → ${(j.steps || []).filter((s) => s.conclusion === "failure").map((s) => s.name).join(",")}`;
      if (videne.has(klic)) continue;
      videne.add(klic);
      zapis("");
      zapis(`### ${klic}   (běh #${beh.run_number}, ${beh.created_at})`);
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
      for (const l of zaj.slice(0, 30)) zapis(`    ${jenRadek(l).slice(0, 200)}`);
      zapis(`    --- POSLEDNÍCH 4 ŘÁDKY:`);
      for (const l of cist.slice(-4)) zapis(`    ${jenRadek(l).slice(0, 200)}`);
    }
  }
}

writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
console.log(`\n[zapsano] ${OUT} (${radky.join("\n").length} znaku)`);
process.exit(0);
