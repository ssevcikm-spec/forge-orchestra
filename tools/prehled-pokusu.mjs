// Přehled běhů podle granule a modelu: kolik pokusů, jak rychle po sobě, kdo odpovídal.
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };

const taskInfo = JSON.parse(readFileSync(`${ORCH}/.tmp/tasky.json`, 'utf8').replace(/^\uFEFF/, ''));

const podle = new Map();
for (const x of taskInfo) {
  if (!podle.has(x.task)) podle.set(x.task, []);
  podle.get(x.task).push(x);
}

console.log('task | granule           | model | pokusu | prvni -> posledni     | rozestup');
console.log('-'.repeat(96));
for (const [task, seznam] of [...podle.entries()].sort((a, b) => Number(a[0]) - Number(b[0]))) {
  seznam.sort((a, b) => new Date(a.cas) - new Date(b.cas));
  const prvni = new Date(seznam[0].cas);
  const posledni = new Date(seznam[seznam.length - 1].cas);
  const rozestup = seznam.length > 1
    ? Math.round((posledni - prvni) / 60000) + ' min'
    : '-';
  console.log(
    String(task).padEnd(4), '|',
    String(seznam[0].grain || '?').padEnd(17), '|',
    String(seznam[0].model || '?').padEnd(5), '|',
    String(seznam.length).padEnd(6), '|',
    (prvni.toISOString().slice(11, 19) + ' -> ' + posledni.toISOString().slice(11, 19)).padEnd(21), '|',
    rozestup,
  );
}
