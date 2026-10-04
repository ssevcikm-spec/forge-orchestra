// P19b — počká na dokončení release.yml pro commit c40bdd5 a ověří TŘI kroky
// nasazení stránky (push → workflow na tom commitu → last-modified po pushi).
//
// PROČ VLASTNÍ: `zjisti-pages.mjs` vypíše i běh `in_progress` a kdo se podle
// něj rozhodne hned, přečte si „ještě ne" jako „hotovo" (a `last-modified`
// starý zůstane — naměřeno 2. 10. 2026: `last-modified 09:30:47` přesně půl
// hodiny po pushi ve 13:16).
//
// Použití:  node _analyza/p19b-cekej-pages.mjs [<sha>]
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'p19b' };
const gh = async (p) => {
  const r = await fetch(`https://api.github.com${p}`, { headers: H });
  return r.ok ? r.json() : { chyba: r.status };
};

const SHA = process.argv[2] || 'c40bdd5';
const REPO = 'ssevcikm-spec/uo-shadows';
const URL_PNG = 'https://ssevcikm-spec.github.io/uo-shadows/index.png';

console.log('════ ČEKÁM NA release.yml PRO COMMIT %s ════' % SHA);
let beh = null;
for (let kolo = 1; kolo <= 30; kolo++) {
  const runs = await gh(`/repos/${REPO}/actions/runs?head_sha=${SHA}&per_page=20`);
  const release = (runs.workflow_runs || []).find((r) => /Vydání hry/.test(r.name || ''));
  const ci = (runs.workflow_runs || []).find((r) => /^CI/.test(r.name || ''));
  const popis = `release=${release ? `#${release.run_number} ${release.status}/${release.conclusion || '-'}` : 'nenalezen'}`
    + `  ci=${ci ? `#${ci.run_number} ${ci.status}/${ci.conclusion || '-'}` : 'nenalezen'}`;
  console.log(`  [kolo ${String(kolo).padStart(2)}] ${popis}`);
  if (release && release.status === 'completed') { beh = release; break; }
  await new Promise((s) => setTimeout(s, 20000));
}

if (!beh) { console.log('\nCHYBA: release.yml se v limitu nedokončil'); process.exit(1); }

console.log('\n════ KROK 2: workflow NA TOM commitu ════');
console.log(`  release.yml #${beh.run_number} ${beh.status}/${beh.conclusion}`);
console.log(`  head_sha = ${beh.head_sha.slice(0, 9)}  (hledáno ${SHA.slice(0, 9)})`);
const ok2 = beh.conclusion === 'success' && beh.head_sha.startsWith(SHA);
console.log(`  ${ok2 ? 'OK  ' : 'CHYBA'} release.yml proběhl na TOM commitu a uspěl`);

console.log('\n════ KROK 3: last-modified PO pushi ════');
let lm = null;
for (let kolo = 1; kolo <= 20; kolo++) {
  const r = await fetch(URL_PNG, { method: 'HEAD' });
  lm = r.headers.get('last-modified');
  const stariMin = (Date.now() - Date.parse(lm)) / 60000;
  console.log(`  [kolo ${String(kolo).padStart(2)}] status=${r.status} last-modified=${lm}  (stáří ${stariMin.toFixed(1)} min)`);
  // Push byl v ~13:16 UTC; nový build poznáme podle toho, že je header MLADŠÍ
  // než 10 minut (starý build je z 09:30).
  if (stariMin < 10) break;
  await new Promise((s) => setTimeout(s, 20000));
}
const ok3 = lm && (Date.now() - Date.parse(lm)) / 60000 < 10;
console.log(`  ${ok3 ? 'OK  ' : 'CHYBA'} server posílá NOVÝ build (ne ten z 09:30)`);

console.log('\n════ VÝSLEDEK ════');
console.log(`  push dorazil        : OK (rev-list --count = 0)`);
console.log(`  workflow na commitu : ${ok2 ? 'OK' : 'CHYBA'}`);
console.log(`  nový build na serveru: ${ok3 ? 'OK' : 'CHYBA'}`);
process.exit(ok2 && ok3 ? 0 : 1);
