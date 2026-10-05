// P17/A — je hra NASAZENÁ? (tři kroky z `DSH_HOME\AGENTS.md`, „Jak ověřit nasazení")
//
// P16/F naměřila 5. 10. 2026 večer: běhy #117 a #78 na `44dd454` skončily
// `cancelled` s prázdným `runner_name` (anotace: „The job was not acquired by
// Runner of type hosted…"), GitHub Actions byl `major_outage`, a artefakt na
// Pages byl STARÝ (build #77). Úkol A téhle session je totéž PŘEMĚŘIT:
// buď je nasazeno (`last-modified` po pushi), nebo je to doložené výpadkem.
//
// Tenhle skript NIC nemění a NEPUSHuje — jen měří. Re-run běhů je samostatný
// krok (P17/A2), který se pouští teprve, když výpadek pominul.
//
// Síť jde přes Node `fetch` (TLS z PowerShellu na téhle stanici nefunguje).

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const REPO = 'ssevcikm-spec/uo-shadows';
const SHA_OCEKAVANY = '44dd45446ed1ce4a418902eb4e81c50a8c2d5694';
const PUSH_UTC = Date.parse('2026-10-05T20:39:00Z');
const API = 'https://api.github.com';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
let PAT = '';
try {
  PAT = readFileSync(join(WS, '.secrets', 'github_pat.txt'), 'utf8').trim();
} catch { /* bez PAT se jede neautentizovaně (limit 60/h, `403`) */ }
const HLAVICKY = {
  accept: 'application/vnd.github+json',
  ...(PAT ? { authorization: `Bearer ${PAT}` } : {}),
};

const vysledky = [];
function zk(ok, popis, detail = '') {
  vysledky.push({ ok, popis, detail });
  console.log(`  ${ok ? 'OK  ' : 'CHYBA'} ${popis}${detail ? `  [${detail}]` : ''}`);
}

async function getJson(url) {
  const r = await fetch(url, { headers: HLAVICKY });
  let data = null;
  try { data = await r.json(); } catch { /* 404 bez těla */ }
  if (r.status !== 200) {
    console.log(`      ! ${url.replace(API, '')} → HTTP ${r.status}`
      + `${data?.message ? ` — ${data.message}` : ''}`);
  }
  return { status: r.status, data: r.status === 200 ? data : null };
}

console.log('='.repeat(78));
console.log('P17/A — nasazení hry (tři kroky)');
console.log(`běženo: ${new Date().toISOString()}`);
console.log('='.repeat(78));

// ── krok 3 (nezávislý na GitHubu — měř PRVNÍ, ať je vidět i bez API) ──────
console.log('\n--- 3) posílá server NOVÝ artefakt? (HTTP 200 není důkaz) ---------');
let artefaktNovy = false;
try {
  const head = await fetch('https://ssevcikm-spec.github.io/uo-shadows/index.png',
    { method: 'HEAD' });
  const lm = head.headers.get('last-modified');
  const lmTs = lm ? Date.parse(lm) : NaN;
  console.log(`      status=${head.status}  last-modified=${lm}`);
  console.log(`      push byl ${new Date(PUSH_UTC).toISOString()}`);
  zk(head.status === 200, 'artefakt odpovídá (HTTP 200) — to samo NIC nedokazuje');
  artefaktNovy = Number.isFinite(lmTs) && lmTs > PUSH_UTC;
  zk(artefaktNovy, 'artefakt je NOVĚJŠÍ než push (krok 3)', lm ?? '—');
  if (Number.isFinite(lmTs) && lmTs <= PUSH_UTC) {
    console.log(`      ⚠ STARÝ artefakt: ${((PUSH_UTC - lmTs) / 3600000).toFixed(2)} h`
      + ' před pushem → web se NEPŘENASADIL');
  }
} catch (e) {
  zk(false, 'artefakt se podařilo změřit', e.message);
}

// ── krok 2: běžel build na SPRÁVNÉM commitu? ─────────────────────────────
console.log('\n--- 2) běžel build na `44dd454`? ------------------------------------');
const runs = await getJson(`${API}/repos/${REPO}/actions/runs?per_page=40`);
zk(runs.status === 200, 'API běhů odpovídá', `HTTP ${runs.status}`);
const vsechny = runs.data?.workflow_runs ?? [];
const naCommitu = vsechny.filter((r) => r.head_sha === SHA_OCEKAVANY);
console.log(`  běhů na commitu 44dd454: ${naCommitu.length}`
  + ` (z ${vsechny.length} posledních)`);
for (const r of naCommitu) {
  console.log(`      #${r.run_number} ${r.name}  ${r.status}/${r.conclusion}  `
    + `attempt=${r.run_attempt}  event=${r.event}  ${r.created_at}  id=${r.id}`);
}
const release = naCommitu.filter((r) => r.path.includes('release.yml'));
const ci = naCommitu.filter((r) => r.path.includes('ci.yml'));
zk(release.length > 0, 'na commitu je běh `release.yml`', `${release.length}`);
const posledni = release.sort((a, b) => b.run_number - a.run_number)[0];
const uspech = posledni && posledni.status === 'completed'
  && posledni.conclusion === 'success';
zk(uspech, 'release.yml na `44dd454` doběhl ÚSPĚŠNĚ',
  posledni ? `#${posledni.run_number} ${posledni.status}/${posledni.conclusion}` : '—');

// ── joby, runner a PŘÍČINA (anotace, ne log) ─────────────────────────────
console.log('\n--- 2b) joby, runner a PŘÍČINA (anotace check-runu) ----------------');
for (const r of naCommitu) {
  const jobs = await getJson(`${API}/repos/${REPO}/actions/runs/${r.id}/jobs`);
  for (const j of jobs.data?.jobs ?? []) {
    console.log(`      #${r.run_number} job "${j.name}": ${j.status}/${j.conclusion}`
      + `  runner="${j.runner_name ?? ''}"  ${j.started_at} → ${j.completed_at}`);
  }
}
const cr = await getJson(`${API}/repos/${REPO}/commits/${SHA_OCEKAVANY}/check-runs`);
zk(cr.status === 200, 'check-runs pro commit odpovídají', `HTTP ${cr.status}`);
const anotace = [];
for (const c of cr.data?.check_runs ?? []) {
  const a = await getJson(`${API}/repos/${REPO}/check-runs/${c.id}/annotations`);
  for (const x of a.data ?? []) anotace.push(`${c.name}: [${x.annotation_level}] ${x.message}`);
}
const failureAnotace = anotace.filter((a) => a.includes('[failure]'));
console.log(`  anotací celkem: ${anotace.length} (z toho failure: ${failureAnotace.length})`);
for (const a of failureAnotace.slice(0, 8)) console.log(`      ${a.slice(0, 170)}`);
const neacquired = failureAnotace.some((a) => /not acquired by Runner/i.test(a));
if (neacquired) {
  console.log('      → anotace říká „job NEDOSTAL runner" = PROSTŘEDÍ, ne kód');
}

// log jobu — P16 měřila 403, P15 hlásila 404 BlobNotFound; zapiš, které to je dnes
console.log('\n--- 2c) je log k dispozici? (ověř, které HTTP to je dnes) ----------');
if (posledni) {
  const r = await fetch(`${API}/repos/${REPO}/actions/runs/${posledni.id}/logs`,
    { redirect: 'manual', headers: HLAVICKY });
  console.log(`      GET /actions/runs/${posledni.id}/logs → HTTP ${r.status}`
    + `  location=${r.headers.get('location') ?? '—'}`);
  vysledky.push({
    ok: r.status !== 200,
    popis: 'log NENÍ k dispozici (nic se nespustilo)',
    detail: `HTTP ${r.status}`,
  });
}

// ── stav GitHubu ─────────────────────────────────────────────────────────
console.log('\n--- 4) stav GitHubu (třetí stav: neproběhlo — prostředí) -----------');
const comp = await getJson('https://www.githubstatus.com/api/v2/components.json');
const actions = comp.data?.components?.find((c) => c.name === 'Actions');
const pages = comp.data?.components?.find((c) => c.name === 'Pages');
console.log(`      Actions: ${actions?.status ?? '?'}   Pages: ${pages?.status ?? '?'}`);
const inc = await getJson('https://www.githubstatus.com/api/v2/incidents/unresolved.json');
const otevrene = inc.data?.incidents ?? [];
console.log(`      nevyřešených incidentů: ${otevrene.length}`);
for (const i of otevrene) {
  console.log(`      incident "${i.name}" [${i.status}] od ${i.created_at}`);
  console.log(`         ${(i.incident_updates?.[0]?.body ?? '').slice(0, 150)}`);
}
zk(!!actions, 'stav Actions je čitelný', actions?.status ?? '—');
const actionsOk = actions?.status === 'operational';

// ── souhrn a doporučení ──────────────────────────────────────────────────
const chyb = vysledky.filter((x) => !x.ok).length;
console.log('\n' + '='.repeat(78));
console.log(`VÝSLEDEK: ${vysledky.length} kontrol, ${chyb} chyb`);
for (const x of vysledky.filter((y) => !y.ok)) console.log(`   CHYBA ${x.popis}`);
console.log('-'.repeat(78));
console.log(`artefakt nový:            ${artefaktNovy}`);
console.log(`release.yml úspěšný:      ${uspech}`);
console.log(`job nedostal runner:      ${neacquired}`);
console.log(`Actions operational:      ${actionsOk} (${actions?.status ?? '?'})`);
const verdikt = artefaktNovy ? 'NASAZENO'
  : (actionsOk ? 'BLOKOVÁNO-NE?' : 'BLOKOVÁNO-VÝPADKEM');
console.log(`VERDIKT: ${verdikt}`);
console.log('='.repeat(78));

// strojově čitelný soubor (aby na něj šlo navázat, ne ho opisovat)
const out = {
  kdy: new Date().toISOString(),
  repo: REPO,
  sha: SHA_OCEKAVANY,
  push_utc: '2026-10-05T20:39:00Z',
  artefakt_novy: artefaktNovy,
  release_uspesny: !!uspech,
  job_nedostal_runner: neacquired,
  actions_status: actions?.status ?? null,
  pages_status: pages?.status ?? null,
  nevyresene_incidenty: otevrene.map((i) => ({ nazev: i.name, stav: i.status, od: i.created_at })),
  behy_na_commitu: naCommitu.map((r) => ({
    cislo: r.run_number, nazev: r.name, stav: r.status, vysledek: r.conclusion,
    pokus: r.run_attempt, id: r.id,
  })),
  kontroly: vysledky,
  verdikt,
};
const { writeFileSync } = await import('node:fs');
writeFileSync(join(WS, '_analyza', 'p17a-vysledky.json'),
  JSON.stringify(out, null, 2) + '\n', 'utf8');
console.log('zapsáno: _analyza/p17a-vysledky.json');
