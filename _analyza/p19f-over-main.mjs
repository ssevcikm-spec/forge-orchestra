// P19f — finální ověření: co je ŽIVĚ na GitHubu `main` v obou repech.
//
// PROČ SOUBOREM: `node -e` s `require()` **a** top-level `await` spadne na
// `ERR_AMBIGUOUS_MODULE_SYNTAX` (naměřeno 2× v téhle session, omyl 69b).
// V `.mjs` souboru je `import` + top-level `await` v pořádku.
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'p19f' };

const LOKALNI = {
  'ssevcikm-spec/forge-orchestra': '889a7e2',
  'ssevcikm-spec/uo-shadows': 'c40bdd5',
};

console.log('════ ŽIVÝ STAV NA GITHUBU — `main` obou repů ════');
let vse = true;
for (const repo of Object.keys(LOKALNI)) {
  const j = await (await fetch(`https://api.github.com/repos/${repo}/commits/main`, { headers: H })).json();
  const sha = (j.sha || '').slice(0, 9);
  const ok = sha.startsWith(LOKALNI[repo]);
  if (!ok) vse = false;
  console.log(`  ${ok ? 'OK  ' : 'CHYBA'} ${repo}`);
  console.log(`        main = ${sha}  (lokálně ${LOKALNI[repo]})`);
  console.log(`        ${(j.commit?.message || '').split('\n')[0].slice(0, 70)}`);
}

console.log('\n════ POSLEDNÍ BĚHY (ověření, že CI na tom commitu proběhl) ════');
for (const repo of Object.keys(LOKALNI)) {
  const j = await (await fetch(`https://api.github.com/repos/${repo}/actions/runs?per_page=3`, { headers: H })).json();
  console.log(`  --- ${repo} ---`);
  for (const r of j.workflow_runs || []) {
    console.log(`     #${String(r.run_number).padEnd(4)} ${String(r.name).slice(0, 34).padEnd(34)} `
      + `${r.status}/${r.conclusion || '-'}  head:${r.head_sha.slice(0, 9)}`);
  }
}
console.log(`\nVÝSLEDEK: ${vse ? 'oba repy mají na main to, co je lokálně' : 'NĚCO NESEDÍ'}`);
process.exit(vse ? 0 : 1);
