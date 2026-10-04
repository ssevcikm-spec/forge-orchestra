// Vytvoří PR z větve na main (nic nesloučí, nic nemění jinde).
// Spuštění: node _analyza\pr-vytvor.mjs <head-ref> <title> <body-file>
import { readFileSync } from 'node:fs';

const WS = 'C:/Users/Ssevc/Local-Deepseek';
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim();
const REPO = 'ssevcikm-spec/uo-shadows';
const GH = {
  Authorization: `Bearer ${PAT}`,
  Accept: 'application/vnd.github+json',
  'User-Agent': 'dsh-pr-vytvor',
  'X-GitHub-Api-Version': '2022-11-28',
};

const [head, title, bodyFile] = process.argv.slice(2);
if (!head || !title) {
  console.log('použití: node _analyza\\pr-vytvor.mjs <head-ref> "<title>" <body-file>');
  process.exit(2);
}
const body = bodyFile ? readFileSync(bodyFile, 'utf8') : '';

const r = await fetch(`https://api.github.com/repos/${REPO}/pulls`, {
  method: 'POST',
  headers: GH,
  body: JSON.stringify({ title, head, base: 'main', body, draft: false }),
});
const t = await r.text();
const j = JSON.parse(t);
if (r.status !== 201) {
  console.log(`HTTP ${r.status}: ${t.slice(0, 400)}`);
  process.exit(1);
}
console.log(`PR #${j.number} vytvořen: ${j.html_url}`);
console.log(`  head=${j.head.ref} (${j.head.sha.slice(0, 10)}) base=${j.base.ref} mergeable_state=${j.mergeable_state}`);
