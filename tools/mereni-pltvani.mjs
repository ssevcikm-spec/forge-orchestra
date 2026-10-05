import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Zmeri pltvani kvotou: kolik behu spusti druhy provider a kolik to stoji.
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'mereni' };
const gh = async (p) => { const r = await fetch(`https://api.github.com${p}`, { headers: H }); return r.ok ? r.json() : { chyba: r.status }; };

const j = await gh(`/repos/${REPO}/actions/runs?per_page=40`);
const forge = (j.workflow_runs || []).filter((x) => /Forge #/.test(x.name || ''));

let sDvema = 0, sJednim = 0, tokenyCelkem = 0, tokenyDruhy = 0, rateLimitBehu = 0, maloTokenu = 0;
const detail = [];

for (const x of forge.slice(0, 16)) {
  const jobs = await gh(`/repos/${REPO}/actions/runs/${x.id}/jobs`);
  const job = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
  if (!job) continue;
  const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
  if (!lg.ok) continue;
  const t = (await lg.text()).replace(/\x1b\[[0-9;]*m/g, '');

  const providery = [...t.matchAll(/FORGE_PROVIDER:\s*(\S+)/g)].map((m) => m[1]);
  const unikatni = [...new Set(providery)];
  const sent = [...t.matchAll(/Tokens:\s*([\d.]+)k sent/g)].map((m) => parseFloat(m[1]));
  const received = [...t.matchAll(/Tokens:\s*[\d.]+k sent,\s*([\d.]+)\s*received/g)].map((m) => parseFloat(m[1]));
  const soucet = sent.reduce((a, b) => a + b, 0);
  const rateLimit = /RateLimitError|rate limit reached|exceeded your current quota/i.test(t);

  tokenyCelkem += soucet;
  if (unikatni.length > 1) {
    sDvema++;
    // druhá část = od druhého volání dál
    tokenyDruhy += sent.slice(1).reduce((a, b) => a + b, 0);
  } else sJednim++;
  if (rateLimit) rateLimitBehu++;
  const maxRecv = received.length ? Math.max(...received) : 0;
  if (maxRecv < 100) maloTokenu++;

  detail.push(`  ${x.name.slice(0, 22).padEnd(24)} ${unikatni.join('>').padEnd(18)} tok=${sent.join('+') || '-'}  odpoved=${received.join('+') || '-'}  ${rateLimit ? 'RATE-LIMIT' : ''}${maxRecv < 100 ? ' MALO-ODPOVEDI' : ''}`);
}

console.log('════ BEH PO BEHU ════');
for (const d of detail) console.log(d);

console.log('\n════ SOUHRN ════');
console.log(`  behů zkoumáno: ${detail.length}`);
console.log(`  s jedním providerem: ${sJednim}`);
console.log(`  s DVĚMA providery:   ${sDvema}`);
console.log(`  tokenů celkem:       ${Math.round(tokenyCelkem)}k`);
console.log(`  z toho na 2. pokus:  ${Math.round(tokenyDruhy)}k  (${Math.round(100 * tokenyDruhy / tokenyCelkem)} %)`);
console.log(`  běhů s rate-limit:   ${rateLimitBehu}`);
console.log(`  běhů s odpovědí <100 tokenů: ${maloTokenu}  <<< model nevrátil kód`);
console.log('\n════ DŮSLEDEK PRO PARALELIZACI ════');
console.log(`  Kdyby se pouštěly 2 modely paralelně, spotřeba na běh by vzrostla`);
console.log(`  z ~${Math.round(tokenyCelkem / Math.max(1, detail.length))}k na ~${Math.round(2 * tokenyCelkem / Math.max(1, detail.length))}k tokenů.`);
console.log(`  Groq má 200k/den → počet běhů na Groqu by klesl na polovinu.`);
