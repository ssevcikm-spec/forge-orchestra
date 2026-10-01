// Presna pricina selhani: vypis vsechny kroky jobu a klicove radky z verdiktu.
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };

const RUN = process.argv[2] || '36726987332';
const gh = async (p) => { const r = await fetch(`https://api.github.com${p}`, { headers: H }); return r.ok ? r.json() : { chyba: r.status }; };

const jobs = await gh(`/repos/${REPO}/actions/runs/${RUN}/jobs`);
for (const j of jobs.jobs || []) {
  console.log(`\njob: ${j.name}  ->  ${j.conclusion}`);
  for (const s of j.steps || []) {
    const znak = s.conclusion === 'success' ? 'ok' : s.conclusion === 'skipped' ? '--' : 'XX';
    console.log(`  ${znak} ${String(s.number).padStart(2)}. ${s.name}`);
  }
  const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${j.id}/logs`, { headers: H });
  if (!lg.ok) continue;
  const radky = (await lg.text()).split('\n');

  // najdi blok "Verdikt" a vse kolem nej
  let vBloku = false;
  const kontext = [];
  for (const l of radky) {
    const c = l.replace(/^\S*Z\s?/, '');
    if (/Verdikt|status=|ZMENA=|nochange|změnil|changed/i.test(c)) { vBloku = true; }
    if (vBloku) kontext.push(c.trimEnd());
    if (kontext.length > 60) break;
  }
  console.log('\n  --- blok verdiktu (prvnich 45 radku) ---');
  for (const l of kontext.slice(0, 45)) console.log(`   | ${l.slice(0, 170)}`);

  console.log('\n  --- vsechny ::error a ::notice ---');
  for (const l of radky) {
    const c = l.replace(/^\S*Z\s?/, '').trim();
    if (/::error|::notice|::warning/.test(c)) console.log(`   ! ${c.slice(0, 175)}`);
  }

  console.log('\n  --- poslednich 20 radku logu ---');
  for (const l of radky.slice(-20)) console.log(`   | ${l.replace(/^\S*Z\s?/, '').trim().slice(0, 165)}`);
}
