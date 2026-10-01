// Detail behu: co brana zkontrolovala, co rekl aider, jake testy selhaly.
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };
const RUN = process.argv[2];

const jobs = await (await fetch(`https://api.github.com/repos/${REPO}/actions/runs/${RUN}/jobs`, { headers: H })).json();
const job = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
const radky = (await lg.text()).split('\n').map((l) => l.replace(/^\S*Z\s?/, '').replace(/\x1b\[[0-9;]*m/g, ''));

const sekce = (od, doo) => {
  const i = radky.findIndex((l) => od.test(l));
  if (i < 0) return [];
  const j = doo ? radky.findIndex((l, k) => k > i && doo.test(l)) : radky.length;
  return radky.slice(i, j < 0 ? i + 60 : j);
};

console.log('════ BRÁNA NA PARSOVÁNÍ ════');
for (const l of sekce(/Kontroluji parsování|Agent nezměnil žádný/, /##\[group\]Run set -o pipefail/)) {
  if (l.trim() && !/^\s*(shell:|env:|[A-Z_]+:)/.test(l)) console.log(`  ${l.trim().slice(0, 150)}`);
}

console.log('\n════ AIDER (co udělal) ════');
const vzory = /Model:|Tokens:|Applied edit|did not conform|No changes|nochange|error|Error/i;
const videne = new Set();
for (const l of sekce(/FORGE_PROMPT:/, /Kontroluji parsování|Testy hry/)) {
  const c = l.trim();
  if (!vzory.test(c) || c.length > 155) continue;
  if (videne.has(c)) continue;
  videne.add(c);
  if (videne.size > 14) break;
  console.log(`  ${c}`);
}

console.log('\n════ TESTY (co selhalo) ════');
for (const l of sekce(/##\[group\]Run set -o pipefail/, /Verdikt a vytvoření patche|##\[group\]Run git diff/)) {
  const c = l.trim();
  if (/\[test\]|SCRIPT ERROR|Parse Error|FAIL|selhání|tvrdý limit/i.test(c)) console.log(`  ${c.slice(0, 155)}`);
}
