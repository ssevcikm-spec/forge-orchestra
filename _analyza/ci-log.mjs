// Stáhne logy CI pro dané head SHA (důkaz, že kontrola PROBĚHLA, ne že mlčela).
// Spuštění: node _analyza\ci-log.mjs
import { readFileSync, writeFileSync } from 'node:fs';

const WS = 'C:/Users/Ssevc/Local-Deepseek';
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim();
const REPO = 'ssevcikm-spec/uo-shadows';
const GH = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'dsh-ci-log' };

const HEADY = process.argv.slice(2).filter((a) => /^[0-9a-f]{7,40}$/.test(a)).map((s) => [s.slice(0, 10), s]);
if (HEADY.length === 0) {
  HEADY.push(['#28 save.gd', '9efbb0763fa7c2f3cf0c98de08029e20ae8c3018']);
  HEADY.push(['#29 hud.gd', '7c45e2d3dde1c03ffc6ce60fe18636d0d60b2b61']);
}

for (const [popis, sha] of HEADY) {
  const r = await fetch(`https://api.github.com/repos/${REPO}/actions/runs?head_sha=${sha}&per_page=5`, { headers: GH });
  const j = await r.json();
  const runs = j.workflow_runs ?? [];
  console.log(`${popis} (${sha.slice(0, 10)}) — běhů: ${runs.length}`);
  for (const run of runs) {
    console.log(`  ${run.name} #${run.run_number} id=${run.id} ${run.status}/${run.conclusion} event=${run.event}`);
    const lr = await fetch(`https://api.github.com/repos/${REPO}/actions/runs/${run.id}/logs`, { headers: GH });
    if (!lr.ok) {
      console.log(`    logy nejdou stáhnout: HTTP ${lr.status}`);
      continue;
    }
    const buf = Buffer.from(await lr.arrayBuffer());
    const out = `${WS}/_analyza/ci-${run.id}.zip`;
    writeFileSync(out, buf);
    console.log(`    logy → _analyza/ci-${run.id}.zip (${buf.length} B)`);
  }
}
