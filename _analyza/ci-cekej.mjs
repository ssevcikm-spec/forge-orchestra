// Počká na CI pro dané commity (polluje GitHub API). Nic nemění.
// Spuštění: node _analyza\ci-cekej.mjs <sha> [<sha> ...]
import { readFileSync } from 'node:fs';

const WS = 'C:/Users/Ssevc/Local-Deepseek';
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim();
const REPO = 'ssevcikm-spec/uo-shadows';
const GH = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'dsh-ci-cekej' };
const SHA = process.argv.slice(2).filter((a) => /^[0-9a-f]{7,40}$/.test(a));

const MAX = 40;        // 40 × 15 s = 10 minut
for (let kolo = 1; kolo <= MAX; kolo++) {
  let hotovo = 0;
  const radky = [];
  for (const sha of SHA) {
    const r = await fetch(`https://api.github.com/repos/${REPO}/actions/runs?head_sha=${sha}&per_page=5`, { headers: GH });
    const runs = (await r.json()).workflow_runs ?? [];
    const ci = runs.find((x) => x.name.startsWith('CI'));
    if (!ci) { radky.push(`  ${sha.slice(0, 10)}  (běh ještě není v API)`); continue; }
    radky.push(`  ${sha.slice(0, 10)}  ${ci.name} #${ci.run_number}  ${ci.status}/${ci.conclusion ?? '—'}`);
    if (ci.status === 'completed') hotovo++;
  }
  console.log(`[kolo ${kolo}] hotovo ${hotovo}/${SHA.length}`);
  for (const l of radky) console.log(l);
  if (hotovo === SHA.length) {
    const spatne = radky.filter((l) => !l.includes('/success'));
    console.log(spatne.length ? `VÝSLEDEK: NĚCO NEDOPADLO DOBŘE\n${spatne.join('\n')}` : 'VÝSLEDEK: všechny běhy completed/success');
    process.exit(spatne.length ? 1 : 0);
  }
  await new Promise((s) => setTimeout(s, 15000));
}
console.log('VÝSLEDEK: čas vypršel, běhy pořád nejsou hotové');
process.exit(2);
