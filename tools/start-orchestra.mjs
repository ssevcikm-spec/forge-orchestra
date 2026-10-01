// Zapne workflow agent.yml v repu hry a aktivuje hru v orchestra.
import { readFileSync } from 'node:fs';

const PAT = readFileSync('C:/Users/Ssevc/Local-Deepseek/orchestra/.secrets/github_pat.txt', 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'forge-setup', 'X-GitHub-Api-Version': '2022-11-28' };
const REPO = 'ssevcikm-spec/uo-shadows';

const api = async (p, init = {}) => {
  const r = await fetch(`https://api.github.com${p}`, { ...init, headers: { ...H, ...(init.headers || {}) } });
  const t = await r.text();
  return { status: r.status, body: t ? JSON.parse(t) : null };
};

// 1) najdi agent.yml a zapni ho
const list = await api(`/repos/${REPO}/actions/workflows`);
const wf = list.body.workflows.find((w) => w.path.endsWith('/agent.yml'));
console.log(`workflow: ${wf.name} (id=${wf.id}), stav=${wf.state}`);

if (wf.state !== 'active') {
  const en = await api(`/repos/${REPO}/actions/workflows/${wf.id}/enable`, { method: 'PUT' });
  console.log(`enable -> HTTP ${en.status}`);
} else {
  console.log('už je aktivní');
}
const po = await api(`/repos/${REPO}/actions/workflows/${wf.id}`);
console.log(`stav po: ${po.body.state}`);

// 2) aktivuj hru v orchestra
const env = Object.fromEntries(
  readFileSync('C:/Users/Ssevc/Local-Deepseek/orchestra/.env', 'utf8')
    .split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);

const call = async (path, init = {}) => {
  const r = await fetch(`${env.FORGE_URL}${path}`, {
    ...init,
    headers: { 'x-forge-secret': env.FORGE_SECRET, 'content-type': 'application/json', ...(init.headers || {}) },
  });
  return { status: r.status, text: await r.text() };
};

console.log('\n--- orchestra: registrace a aktivace hry ---');
const reg = await call('/game', {
  method: 'POST',
  body: JSON.stringify({ game_id: 'uo-shadows', repo: REPO, roadmap_file: '.forge/roadmap.json' }),
});
console.log(`POST /game -> HTTP ${reg.status} ${reg.text}`);

const on = await call('/game/active', {
  method: 'POST',
  body: JSON.stringify({ game_id: 'uo-shadows', active: true }),
});
console.log(`POST /game/active {active:true} -> HTTP ${on.status} ${on.text}`);

const games = await call('/games');
console.log(`\n/games: ${games.text}`);
const health = await call('/health');
console.log(`/health: ${health.text}`);
