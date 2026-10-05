// P16/F — je NASZENÍ na správném commitu? (tři kroky; HTTP 200 není důkaz)
//
// Krok 1 (push dorazil) se měří `git ls-remote` v PowerShellu — tady se dělají
// kroky 2 a 3 a ověření PŘÍČINY:
//   2) build běžel na SPRÁVNÉM commitu (head_sha + conclusion),
//      a když neběžel: anotace check-runu (log NEEXISTUJE — `404 BlobNotFound`),
//   3) server posílá NOVÝ artefakt (`last-modified` souboru `index.png`),
//   + stav GitHubu (`githubstatus.com`) — „neproběhlo (prostředí)" je TŘETÍ stav.
//
// Síť jde přes Node `fetch` (TLS z PowerShellu na téhle stanici nefunguje).
// Nic se nepushuje, nic se nemění.

const REPO = 'ssevcikm-spec/uo-shadows';
const ORCH = 'ssevcikm-spec/forge-orchestra';
const SHA_OCEKAVANY = '44dd45446ed1ce4a418902eb4e81c50a8c2d5694';
const PUSH_UTC = Date.parse('2026-10-05T20:39:00Z');
const API = 'https://api.github.com';

// PAT ze souboru se secretem (skill `orchestra`: „Na GitHub jen přes PAT ze
// souboru se secretem — nikdy ho nevypisuj ani nepiš do historie příkazů").
// Bez něj vrací neautentizované API `403` (limit) a měření by tvrdilo, že běh
// NEEXISTUJE — což je falešný nález (`overovani` §9.4).
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
const WS = dirname(dirname(fileURLToPath(import.meta.url)));
let PAT = '';
try {
  PAT = readFileSync(join(WS, '.secrets', 'github_pat.txt'), 'utf8').trim();
} catch { /* bez PAT se jede neautentizovaně */ }
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
console.log('P16/F — nasazení na správném commitu (tři kroky)');
console.log('='.repeat(78));

// ── krok 2: build na SPRÁVNÉM commitu ─────────────────────────────────────
console.log('\n--- 2) běžel build na `44dd454`? ------------------------------------');
const runs = await getJson(`${API}/repos/${REPO}/actions/runs?per_page=30`);
zk(runs.status === 200, 'API běhů odpovídá', `HTTP ${runs.status}`);
const vsechny = runs.data?.workflow_runs ?? [];
const naCommitu = vsechny.filter((r) => r.head_sha === SHA_OCEKAVANY);
console.log(`  běhů na commitu 44dd454: ${naCommitu.length}`);
for (const r of naCommitu) {
  console.log(`      #${r.run_number} ${r.name}  ${r.status}/${r.conclusion}  `
    + `event=${r.event}  created=${r.created_at}`);
}
const release = naCommitu.filter((r) => r.path.includes('release.yml'));
zk(release.length > 0, 'na commitu je běh `release.yml`', `${release.length}`);
const posledni = release.sort((a, b) => b.run_number - a.run_number)[0];
if (posledni) {
  console.log(`  poslední release.yml: #${posledni.run_number} `
    + `${posledni.status}/${posledni.conclusion} attempt=${posledni.run_attempt}`);
}

// ── joby a PŘÍČINA (anotace, ne log) ──────────────────────────────────────
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
console.log(`  anotací celkem: ${anotace.length}`);
for (const a of anotace.slice(0, 8)) console.log(`      ${a.slice(0, 150)}`);
const neacquired = anotace.some((a) => /not acquired by Runner/i.test(a));
zk(neacquired, 'anotace říká „The job was not acquired by Runner of type hosted…“ '
  + '→ job NEDOSTAL runner (prostředí, ne kód)', `${anotace.length} anotací`);

// log jobu — musí být NEDOSTUPNÝ (důkaz, že se nic nespustilo)
console.log('\n--- 2c) existuje log toho běhu? (má být 404) ----------------------');
if (posledni) {
  const r = await fetch(`${API}/repos/${REPO}/actions/runs/${posledni.id}/logs`,
    { redirect: 'manual' });
  console.log(`      GET /actions/runs/${posledni.id}/logs → HTTP ${r.status}`);
  zk(r.status !== 200, 'log NENÍ k dispozici (nic se nespustilo) — důvod je '
    + 'v ANOTACI, ne v logu', `HTTP ${r.status}`);
}

// ── krok 3: server posílá NOVÝ artefakt? ─────────────────────────────────
console.log('\n--- 3) posílá server NOVÝ artefakt? (HTTP 200 není důkaz) ---------');
const head = await fetch('https://ssevcikm-spec.github.io/uo-shadows/index.png',
  { method: 'HEAD' });
const lm = head.headers.get('last-modified');
const lmTs = lm ? Date.parse(lm) : NaN;
console.log(`      status=${head.status}  last-modified=${lm}`);
console.log(`      push byl ${new Date(PUSH_UTC).toISOString()}`);
zk(head.status === 200, 'artefakt odpovídá (HTTP 200) — to samo NIC nedokazuje');
zk(Number.isFinite(lmTs) && lmTs > PUSH_UTC,
  'artefakt je NOVĚJŠÍ než push (krok 3 „Jak ověřit nasazení“)',
  lm ? new Date(lmTs).toISOString() : '—');
if (Number.isFinite(lmTs) && lmTs <= PUSH_UTC) {
  console.log(`      ⚠ STARÝ artefakt: ${(PUSH_UTC - lmTs) / 3600000} h před pushem`
    + ' → web se NEPŘENASADIL');
}

// ── třetí stav: prostředí ────────────────────────────────────────────────
console.log('\n--- 4) stav GitHubu (třetí stav: neproběhlo — prostředí) -----------');
const comp = await getJson('https://www.githubstatus.com/api/v2/components.json');
const actions = comp.data?.components?.find((c) => c.name === 'Actions');
console.log(`      Actions: ${actions?.status ?? '?'}`);
const inc = await getJson('https://www.githubstatus.com/api/v2/incidents/unresolved.json');
for (const i of inc.data?.incidents ?? []) {
  console.log(`      incident "${i.name}" [${i.status}] od ${i.created_at}`);
  console.log(`         ${(i.incident_updates?.[0]?.body ?? '').slice(0, 130)}`);
}
zk(!!actions, 'stav Actions je čitelný', actions?.status ?? '—');

// ── souhrn ───────────────────────────────────────────────────────────────
const chyb = vysledky.filter((x) => !x.ok).length;
console.log('\n' + '='.repeat(78));
console.log(`VÝSLEDEK: ${vysledky.length} kontrol, ${chyb} chyb`);
for (const x of vysledky.filter((y) => !y.ok)) console.log(`   CHYBA ${x.popis}`);
console.log('='.repeat(78));
