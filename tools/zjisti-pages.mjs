import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Zjistí PRAVDU o herních repech a GitHub Pages – místo dohadů z dokumentace.
//
// PROČ: v `release.yml` je odkaz na `https://ssevcikm-spec.github.io/forge-quest/`,
// ale herní repo se jmenuje `uo-shadows`. Buď je odkaz mrtvý, nebo Pages visí
// na starém repu. Na uživatelskou otázku „odkud to vlastně běží" se nesmí
// odpovídat odhadem.
//
// TLS: používá se Node `fetch` (PowerShell na téhle stanici padá na schannelu).
// Použití: node orchestra/tools/zjisti-pages.mjs

import { readFileSync } from 'node:fs';

const PAT_CESTA = join(PARENT, '.secrets', 'github_pat.txt');
let PAT = '';
try {
  PAT = readFileSync(PAT_CESTA, 'utf8').trim();
} catch (e) {
  console.error(`CHYBA: PAT nejde přečíst (${PAT_CESTA}): ${e.message}`);
  process.exit(2);
}

const H = {
  Authorization: `Bearer ${PAT}`,
  Accept: 'application/vnd.github+json',
  'User-Agent': 'forge-pages-check',
};

async function api(cesta) {
  const r = await fetch(`https://api.github.com${cesta}`, { headers: H });
  if (r.status === 404) return { _status: 404 };
  if (!r.ok) return { _status: r.status, _text: (await r.text()).slice(0, 200) };
  return r.json();
}

// Uživatel (ne organizace) – podle orchestra/README.md je `ssevcikm-spec` uživatel.
console.log('=== Repozitáře uživatele ssevcikm-spec ===');
const repa = await api('/user/repos?per_page=100&sort=pushed');
if (Array.isArray(repa)) {
  for (const r of repa) {
    console.log(`  ${r.name.padEnd(24)} push: ${r.pushed_at}  private: ${r.private}  ` +
                `pages: ${r.has_pages ? 'ANO → ' + (r.homepage || '(bez homepage)') : 'ne'}`);
  }
} else {
  console.log(`  nepodařilo se načíst: ${JSON.stringify(repa)}`);
}

console.log('\n=== Hledám forge-quest a uo-shadows ===');
for (const nazev of ['forge-quest', 'uo-shadows', 'uo-sandbox']) {
  const r = await api(`/repos/ssevcikm-spec/${nazev}`);
  if (r._status === 404) {
    console.log(`  ${nazev.padEnd(14)} NEEXISTUJE (404)`);
    continue;
  }
  if (r._status) {
    console.log(`  ${nazev.padEnd(14)} chyba HTTP ${r._status}: ${r._text}`);
    continue;
  }
  console.log(`  ${nazev.padEnd(14)} existuje | default branch: ${r.default_branch} | ` +
              `pages: ${r.has_pages ? 'ANO' : 'ne'} | homepage: ${r.homepage || '(žádná)'}`);
}

console.log('\n=== GitHub Pages u uo-shadows (kde to skutečně běží) ===');
const pages = await api('/repos/ssevcikm-spec/uo-shadows/pages');
if (pages._status === 404) {
  console.log('  Pages NEEXISTUJE (404) – webová verze na Pages neběží');
} else if (pages._status) {
  console.log(`  chyba HTTP ${pages._status}: ${pages._text}`);
} else {
  console.log(`  URL:      ${pages.html_url}`);
  console.log(`  status:   ${pages.status}`);
  console.log(`  build:    ${pages.build_type}`);
  console.log(`  zdroj:    ${pages.source?.branch || '(actions)'} / ${pages.source?.path || '-'}`);
  console.log(`  cname:    ${pages.cname || '(žádná)'}`);
}

console.log('\n=== Poslední běh workflow "release.yml" (staví web) ===');
const runs = await api('/repos/ssevcikm-spec/uo-shadows/actions/workflows/release.yml/runs?per_page=5');
if (runs.workflow_runs) {
  for (const r of runs.workflow_runs) {
    console.log(`  #${r.run_number} ${r.status}/${r.conclusion || '-'} ` +
                `${r.created_at} head:${r.head_sha.slice(0, 7)} ${r.head_branch}`);
  }
  if (!runs.workflow_runs.length) console.log('  (žádné běhy)');
} else {
  console.log(`  nepodařilo se načíst: ${JSON.stringify(runs).slice(0, 200)}`);
}

console.log('\n=== Poslední commity na main (co je v gitu, tedy i na Pages) ===');
const commity = await api('/repos/ssevcikm-spec/uo-shadows/commits?per_page=5');
if (Array.isArray(commity)) {
  for (const c of commity) {
    console.log(`  ${c.sha.slice(0, 7)} ${c.commit.author.date} ${c.commit.message.split('\n')[0].slice(0, 60)}`);
  }
} else {
  console.log(`  nepodařilo se načíst: ${JSON.stringify(commity).slice(0, 200)}`);
}
