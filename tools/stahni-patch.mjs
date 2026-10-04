import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Stahne artefakt agent.patch z behu a vypise .gd soubory v nem.
// Pouziti: node orchestra\tools\stahni-patch.mjs <runId>
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };
const RUN = process.argv[2];

const gh = async (p) => { const r = await fetch(`https://api.github.com${p}`, { headers: H }); return r.ok ? r.json() : { chyba: r.status }; };
const jobs = await gh(`/repos/${REPO}/actions/runs/${RUN}/jobs`);
const job = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
const arts = await gh(`/repos/${REPO}/actions/runs/${RUN}/artifacts`);
const art = (arts.artifacts || []).find((a) => a.name.startsWith('agent-patch'));
if (!art) { console.log('artefakt nenalezen'); process.exit(1); }
console.log(`artefakt: ${art.name}  ${art.size_in_bytes} B`);

const zip = await fetch(`https://api.github.com/repos/${REPO}/actions/artifacts/${art.id}/zip`, { headers: H });
const buf = Buffer.from(await zip.arrayBuffer());
mkdirSync(`${ORCH}/.tmp`, { recursive: true });
const cesta = `${ORCH}/.tmp/patch-${RUN}.zip`;
writeFileSync(cesta, buf);
console.log(`ulozene: ${cesta} (${buf.length} B)`);
