// Detail aktualnich behu: co model udelal, kde to skoncilo.
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };
const gh = async (p) => { const r = await fetch(`https://api.github.com${p}`, { headers: H }); return r.ok ? r.json() : { chyba: r.status }; };

const runs = await gh(`/repos/${REPO}/actions/runs?per_page=12`);
const aktualni = (runs.workflow_runs || []).filter((x) => /Forge #1(07|08|09|10)\b/.test(x.name || ''));
console.log(`aktuální běhy DAG: ${aktualni.length}\n`);

for (const x of aktualni.slice(0, 4)) {
  console.log('═'.repeat(90));
  console.log(`${x.name}   ${x.status}/${x.conclusion ?? '-'}   ${x.created_at}`);
  console.log('═'.repeat(90));
  const jobs = await gh(`/repos/${REPO}/actions/runs/${x.id}/jobs`);
  for (const j of jobs.jobs || []) {
    console.log(`job ${j.name}: ${j.status}/${j.conclusion ?? '-'}`);
    const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${j.id}/logs`, { headers: H });
    if (!lg.ok) { console.log(`  (bez logu: ${lg.status})`); continue; }
    const radky = (await lg.text()).split('\n');

    // hledej klicove momenty
    const vzory = [
      /FORGE_MODEL:|FORGE_PROVIDER:/,
      /Applied edit to|No changes|nochange|did not|No valid patches/i,
      /Cannot infer the type|Parse Error|SCRIPT ERROR|Nonexistent function/i,
      /\[test\] (OK|FAIL)/,
      /tvrdý limit|timeout/i,
      /::error::/,
      /aider skoncil/i,
      /Tokens:|Cost:/i,
    ];
    const vybrane = radky.filter((l) => vzory.some((v) => v.test(l)));
    // deduplikuj a zkrat
    const videne = new Set();
    for (const l of vybrane) {
      const c = l.replace(/^\S*Z\s?/, '').trim().slice(0, 158);
      if (videne.has(c)) continue;
      videne.add(c);
      if (videne.size > 26) break;
      console.log(`   | ${c}`);
    }
  }
  console.log();
}
