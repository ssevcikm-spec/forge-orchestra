// p36-pat-sonda.mjs — jen ZJIŠTĚNÍ, které secrety v repech existují a kdy byly
// naposledy změněny. Hodnoty se NIKDY nevypisují (API je ani nevrací).
//
// Proč: 14 z 29 selhaných běhů agenta spadlo v jobu „Otevři pull request“ na
// `fatal: could not read Username for 'https://github.com'` — to je podpis
// chybějícího/neplatného tokenu, ne chyby kódu. `FORGE_PAT` je secret, který
// PR job používá (`token: ${{ secrets.FORGE_PAT }}`).
//
// Použití: node _analyza/p36-pat-sonda.mjs

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, "_analyza", "p36-pat-sonda-vystup.txt");
const PAT = readFileSync(join(WS, ".secrets", "github_pat.txt"), "utf8").trim();

const radky = [];
const zapis = (x = "") => { radky.push(x); console.log(x); };

const api = async (cesta) => {
  const r = await fetch(`https://api.github.com${cesta}`, {
    headers: {
      Authorization: `Bearer ${PAT}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "forge-p36-sonda",
    },
  });
  const text = await r.text();
  if (!r.ok) return { chyba: `HTTP ${r.status}: ${text.slice(0, 200)}` };
  return JSON.parse(text);
};

// ── platnost LOKÁLNÍHO PAT (hlavička, kterou GitHub u fine-grained tokenů posílá)
{
  const r = await fetch("https://api.github.com/user", {
    headers: {
      Authorization: `Bearer ${PAT}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "forge-p36-sonda",
    },
  });
  const j = await r.json();
  zapis("## LOKÁLNÍ PAT (soubor .secrets/github_pat.txt — hodnota se nevypisuje)");
  zapis(`  HTTP ${r.status} · login=${j.login ?? "?"}`);
  zapis(`  github-authentication-token-expiration: ${r.headers.get("github-authentication-token-expiration") ?? "(hlavička není — token bez expirace, nebo klasický PAT)"}`);
  zapis(`  x-oauth-scopes: ${r.headers.get("x-oauth-scopes") ?? "(žádné — fine-grained)"}`);
  zapis("");
}

for (const repo of ["ssevcikm-spec/forge-orchestra", "ssevcikm-spec/uo-shadows"]) {
  zapis(`## ${repo}`);
  const s = await api(`/repos/${repo}/actions/secrets`);
  if (s.chyba) {
    zapis(`  (secrety nejde vypsat: ${s.chyba})`);
  } else {
    zapis(`  celkem secretů: ${s.total_count}`);
    for (const x of s.secrets || []) {
      zapis(`    ${x.name.padEnd(28)} změněn ${x.updated_at}`);
    }
  }
  zapis("");
}

// Kdy naposledy uspěl běh agenta v repu hry — a co dělaly běhy mezi tím
const hra = "ssevcikm-spec/uo-shadows";
const behy = await api(`/repos/${hra}/actions/workflows/agent.yml/runs?per_page=100&page=1`);
if (!behy.chyba) {
  zapis(`## agent.yml v ${hra} — posledních 100 běhů podle výsledku`);
  const podle = new Map();
  for (const r of behy.workflow_runs) podle.set(r.conclusion ?? r.status, (podle.get(r.conclusion ?? r.status) || 0) + 1);
  for (const [k, n] of [...podle.entries()].sort((a, b) => b[1] - a[1])) zapis(`  ${String(n).padStart(3)}×  ${k}`);
  const posledniUspesny = behy.workflow_runs.find((r) => r.conclusion === "success");
  zapis(`  poslední ÚSPĚŠNÝ v této stovce: ${posledniUspesny ? `#${posledniUspesny.run_number} ${posledniUspesny.created_at}` : "(ŽÁDNÝ)"}`);
}

writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
console.log(`\n[zapsano] ${OUT} (${radky.join("\n").length} znaku)`);
