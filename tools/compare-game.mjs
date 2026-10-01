// Porovna lokalni hru s repem ssevcikm-spec/uo-shadows na GitHubu.
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, relative } from 'node:path';

const PAT = readFileSync('C:/Users/Ssevc/Local-Deepseek/orchestra/.secrets/github_pat.txt', 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'forge-check' };
const REPO = 'ssevcikm-spec/uo-shadows';
const LOKAL = 'C:/Users/Ssevc/Local-Deepseek/games/uo-shadows';

const api = async (p) => {
  const r = await fetch(`https://api.github.com${p}`, { headers: H });
  return { status: r.status, body: r.ok ? await r.json() : (await r.text()).slice(0, 200) };
};

// 1) metadata repa
const repo = await api(`/repos/${REPO}`);
console.log(`repo: ${REPO}  private=${repo.body.private}  pushed=${repo.body.pushed_at}`);
console.log(`default branch: ${repo.body.default_branch}`);

// 2) strom repa (jednim dotazem, rekurzivne)
const br = await api(`/repos/${REPO}/git/trees/${repo.body.default_branch}?recursive=1`);
if (br.status !== 200) { console.log(`strom: HTTP ${br.status} ${br.body}`); process.exit(1); }
const soubory = br.body.tree.filter((x) => x.type === 'blob').map((x) => x.path);
console.log(`souboru v repu: ${soubory.length}${br.body.truncated ? ' (zkraceny vypis!)' : ''}`);

// 3) klicove soubory: jsou v repu?
const klicove = [
  '.forge/roadmap.json', '.forge/pick-provider.mjs', '.forge/providers.json',
  '.forge/node/worker.mjs', '.forge/node/provider-choice.mjs',
  '.github/workflows/agent.yml', '.github/workflows/ci.yml',
  'CONVENTIONS.md', 'docs/ARCHITEKTURA.md', 'forge.json',
  'project.godot', 'main.tscn', 'sprites.json',
];
console.log('\nklicove soubory:');
for (const k of klicove) {
  console.log(`  ${soubory.includes(k) ? 'JE   ' : 'CHYBI'} ${k}`);
}

// 4) soubory jen lokalne (mimo .git/.godot)
const lokalni = [];
(function walk(d) {
  for (const e of readdirSync(d, { withFileTypes: true })) {
    if (e.name === '.git' || e.name === '.godot') continue;
    const p = join(d, e.name);
    if (e.isDirectory()) walk(p);
    else lokalni.push(relative(LOKAL, p).split('\\').join('/'));
  }
})(LOKAL);
const vRepuSet = new Set(soubory);
const jenLokalne = lokalni.filter((f) => !vRepuSet.has(f));
console.log(`\nlokalnich souboru: ${lokalni.length}, z toho jen lokalne: ${jenLokalne.length}`);
for (const f of jenLokalne.slice(0, 40)) console.log(`  + ${f}`);

// 5) roadmapa v repu vs lokalni
const rmRepo = await api(`/repos/${REPO}/contents/.forge/roadmap.json`);
if (rmRepo.status === 200) {
  const txt = Buffer.from(rmRepo.body.content, 'base64').toString('utf8');
  try {
    const g = JSON.parse(txt).grains || [];
    console.log(`\nroadmapa v REPU: PLATNA, granul ${g.length}`);
  } catch (e) {
    console.log(`\nroadmapa v REPU: ROZBITA (${e.message.slice(0, 80)})`);
  }
}
const tLok = readFileSync(join(LOKAL, '.forge/roadmap.json'), 'utf8');
console.log(`roadmapa LOKALNE: ${(() => { try { return 'PLATNA, granul ' + JSON.parse(tLok).grains.length; } catch (e) { return 'ROZBITA'; } })()}`);
