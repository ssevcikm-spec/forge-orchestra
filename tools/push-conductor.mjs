import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Nahraje zmenene soubory orchestra do GitHubu (obsah -> base64 -> PUT).
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const REPO = 'ssevcikm-spec/forge-orchestra';
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'push', 'X-GitHub-Api-Version': '2022-11-28' };

const SOUBORY = [
  { lokal: `${ORCH}/conductor/src/index.ts`, repo: 'conductor/src/index.ts' },
  { lokal: `${ORCH}/conductor/wrangler.toml`, repo: 'conductor/wrangler.toml' },
];

const api = async (p, init = {}) => {
  const r = await fetch(`https://api.github.com${p}`, { ...init, headers: { ...H, ...(init.headers || {}) } });
  const t = await r.text();
  return { status: r.status, body: t ? JSON.parse(t) : null };
};

for (const s of SOUBORY) {
  const obsah = readFileSync(s.lokal);
  const cur = await api(`/repos/${REPO}/contents/${s.repo}`);
  if (cur.status !== 200) { console.log(`CHYBA cteni ${s.repo}: ${cur.status}`); continue; }
  if (Buffer.from(cur.body.content, 'base64').equals(obsah)) { console.log(`beze zmeny: ${s.repo}`); continue; }
  const put = await api(`/repos/${REPO}/contents/${s.repo}`, {
    method: 'PUT',
    body: JSON.stringify({
      message: `conductor: strop pokusu + kratsi cooldown (${s.repo})\n\nBez stropu vznikala smycka: uloha spadla s vycerpanymi pokusy,\nstale-recovery ji vratila do fronty a dispatch pridal dalsi pokus -- beh\nzustal naverky running. Zavedeno MAX_ATTEMPTS (5, driv hardcoded 3) a\nRETRY_HOURS zkraceno z 6 na 3 h. Report navic respektuje terminalni stavy\n'blocked' a 'done'.`,
      content: obsah.toString('base64'),
      sha: cur.body.sha,
      branch: 'main',
    }),
  });
  console.log(put.status === 200 || put.status === 201 ? `OK ${s.repo} -> ${put.body.commit.sha.slice(0, 8)}` : `CHYBA ${s.repo}: ${put.status}`);
}
