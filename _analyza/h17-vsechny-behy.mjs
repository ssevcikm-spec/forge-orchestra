// H17 — souhrn příčin u všech pěti selhaných běhů (#142–#146).
//
// PROČ: `HANDOFF.md` §16.7 předpovídalo, že #146 selhala na kontrole izo
// projekce (protože worker pracoval proti commitu BEZ opravy testu). Tenhle
// skript to vyvrací nebo potvrzuje z LOGU běhu — a to je jiná otázka než
// „jaký je stav úlohy" (to umí `/queue`).
//
// POZOR: český text se v tomhle souboru NESMÍ skládat přes PowerShell
// here-string — naměřeno 2. 10. 2026: `Set-Content` z něj udělal trojici
// znaků, kterou brána diakritiky hlásí jako vadu souboru. Znaky rozbitého
// kódování se proto popisují SLOVEM (viz AGENTS.md), ne doslovně.
//
// Použití:  node _analyza/h17-vsechny-behy.mjs
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'h17' };

const BEHY = [
  ['#146', 36999784822], ['#145', 36999780638], ['#144/new', 36999776851],
  ['#143/new', 36999773646], ['#142/new', 36999768712], ['#144/old', 36988977938],
];

// Hledaný text se sestavuje z kódových bodů, aby v souboru nebyl doslovně.
const ZMENA = 'Agent nezm' + String.fromCharCode(0x011b) + 'nil';

for (const [popis, id] of BEHY) {
  const jobs = await (await fetch(`https://api.github.com/repos/${REPO}/actions/runs/${id}/jobs`, { headers: H })).json();
  const job = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
  const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
  const txt = await lg.text();
  const tpm = txt.match(/tokens per minute \(TPM\): Limit\s+(\d+),\s*Requested\s+(\d+)/);
  const model = txt.match(/model `([^`]+)` in organization/);
  const sum = txt.match(/\[test\] (\d+) kontrol, (\d+) selh/);
  const zmena = txt.includes(ZMENA);
  // ⚠ POZOR: hledat jen `ZMENA` NESTAČÍ — tentýž řetězec je i v `echo`
  // kroku, který se vypisuje do logu (naměřeno: hlásilo „zmena=false: true"
  // i u běhů, které na ten krok vůbec nedošly). Rozhoduje `##[error]`.
  const zmenaChyba = new RegExp('##\\[error\\]' + ZMENA).test(txt);
  const parseErr = [...txt.matchAll(/Parse Error: ([^\n]{0,90})/g)].map((m) => m[1]);
  const parsovane = [...txt.matchAll(/Skript se neparsuje [–-] (scripts\/[a-z_]+\.gd)/g)].map((m) => m[1]);
  const krok = (job.steps || []).find((s) => s.conclusion === 'failure');
  console.log(`${popis.padEnd(10)} selhal-krok="${krok ? krok.name : '?'}"  test=${sum ? sum[0] : '-'}  agent-nezmenil:${zmenaChyba}`);
  console.log(`           model=${model ? model[1] : '-'}  TPM=${tpm ? `limit ${tpm[1]}, zadano ${tpm[2]}` : '-'}`);
  if (parsovane.length) console.log(`           NEPARSOVALO SE: ${[...new Set(parsovane)].join(', ')}`);
  if (parseErr.length) console.log(`           Parse Error: ${[...new Set(parseErr)].slice(0, 3).join(' | ')}`);
  void zmena;
}
