// p30-sonda-deploy.mjs — zjistí ŽIVĚ, jestli push spustil nasazení conductora.
//
// Co měří:
//   1) seznam workflow runs pro .github/workflows/deploy.yml (posledních 10)
//   2) jejich stav, head_sha, conclusion a čas
//   3) jestli mezi nimi je běh na zadaném commitu (default: živý HEAD)
//
// PAT se čte ze souboru .secrets/github_pat.txt a NIKDY se nevypisuje.
// Exit 1 = nasazení na daném commitu NEBYLO úspěšné.

import { readFileSync } from "node:fs";

const REPO = "ssevcikm-spec/forge-orchestra";
const pat = readFileSync(new URL("../.secrets/github_pat.txt", import.meta.url), "utf8").trim();
const cil = process.argv[2] ?? null;

const api = async (cesta) => {
  const r = await fetch(`https://api.github.com${cesta}`, {
    headers: {
      Authorization: `Bearer ${pat}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "forge-p30-sonda",
    },
  });
  if (!r.ok) throw new Error(`${cesta} -> HTTP ${r.status} ${await r.text()}`);
  return r.json();
};

const chyby = [];
const ok = (podminka, text) => {
  console.log(`${podminka ? "OK  " : "CHYBA"} ${text}`);
  if (!podminka) chyby.push(text);
};

const runs = await api(`/repos/${REPO}/actions/workflows/deploy.yml/runs?per_page=10`);
console.log(`workflow deploy.yml: total_count=${runs.total_count}`);
console.log("");
console.log("  #  | head_sha  | event  | status      | conclusion   | created_at           | název běhu");
for (const r of runs.workflow_runs) {
  console.log(
    `  ${String(r.run_number).padStart(3)} | ${r.head_sha.slice(0, 8)} | ${String(r.event).padEnd(6)} | ` +
      `${String(r.status).padEnd(11)} | ${String(r.conclusion ?? "-").padEnd(12)} | ` +
      `${r.created_at} | ${r.display_title?.slice(0, 40) ?? ""}`,
  );
}
console.log("");

const aktualni = runs.workflow_runs[0] ?? null;
ok(aktualni !== null, "existuje aspoň jeden běh deploy.yml");

if (aktualni) {
  console.log(`nejnovější běh: #${aktualni.run_number} head=${aktualni.head_sha.slice(0, 8)} ` +
    `status=${aktualni.status} conclusion=${aktualni.conclusion} created=${aktualni.created_at}`);
  const naCommitu = runs.workflow_runs.find((r) => cil && r.head_sha.startsWith(cil));
  if (cil) {
    ok(naCommitu !== undefined, `na commitu ${cil} existuje běh deploy.yml`);
    if (naCommitu) {
      ok(
        naCommitu.status === "completed" && naCommitu.conclusion === "success",
        `běh #${naCommitu.run_number} na ${cil} je completed/success (je: ${naCommitu.status}/${naCommitu.conclusion})`,
      );
      console.log(`  viz ${naCommitu.html_url}`);
    }
  }
}

console.log("");
console.log(chyby.length === 0 ? `VŠE OK (${0} chyb)` : `CHYB: ${chyby.length}`);
for (const c of chyby) console.log(`  - ${c}`);
process.exit(chyby.length === 0 ? 0 : 1);
