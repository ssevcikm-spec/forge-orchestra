// Ověří, které z doporučení ANALYZA-ARCHITEKTURY-ORCHESTRA.md (§5.1 L1-L17,
// §5.2 ST1-ST10) jsou k 1. 10. 2026 večer HOTOVÉ, které NE, a čím to bylo
// naměřeno. Bez sítě. Výstup je tabulka pro zápis do dokumentu.
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';

const W = process.cwd();
const je = (p) => fs.existsSync(`${W}/${p}`);
const grep = (p, re) => {
  if (!je(p)) return null;
  const t = fs.readFileSync(`${W}/${p}`, 'utf8');
  return (t.match(re) || []).length;
};
const git = (args) => {
  try {
    return execFileSync('git', args, { cwd: W, encoding: 'utf8' }).trim();
  } catch (e) {
    return 'CHYBA: ' + (e.message || '').split('\n')[0];
  }
};

const vysledky = [];
const zapis = (id, hotovo, dukaz) => vysledky.push({ id, hotovo, dukaz });

// ---- L1: validate-all.mjs exit code + spravna kopie
{
  const nastavujeExit = grep('orchestra/tools/validate-all.mjs', /process\.exitCode/);
  const pouzivaStarou = grep('orchestra/tools/validate-all.mjs', /kontrola-schematu/);
  const staraExistuje = je('orchestra/tools/kontrola-schematu.py');
  zapis(
    'L1',
    nastavujeExit > 0 && pouzivaStarou === 0,
    `process.exitCode: ${nastavujeExit === 0 ? 'NENÍ' : nastavujeExit + 'x'}; ` +
      `validate-all volá kontrola-schematu.py: ${pouzivaStarou}x; ` +
      `starý soubor existuje: ${staraExistuje}`,
  );
}

// ---- L2: smazat stary kontrola-schematu.py + oprav-check-schema-*
{
  const stare = ['orchestra/tools/kontrola-schematu.py'];
  const zbyle = stare.filter(je);
  const oprav = fs
    .readdirSync(`${W}/orchestra/tools`)
    .filter((f) => /^oprav-check-schema/.test(f));
  zapis('L2', zbyle.length === 0 && oprav.length === 0, `kontrola-schematu.py: ${zbyle.length}; oprav-check-schema*: ${oprav.length}`);
}

// ---- L3: sablona v gitu
{
  const forge = git(['-C', 'orchestra', 'ls-files', 'repo/.forge']).split('\n').filter(Boolean).length;
  const fq = grep('orchestra/repo/.github/workflows/release.yml', /forge-quest/g);
  zapis('L3', forge >= 21 && fq === 0, `git ls-files repo/.forge = ${forge} (plán chtěl 21); release.yml 'forge-quest' = ${fq}x`);
}

// ---- L4: prazdna roadmapa sablony
{
  const d = JSON.parse(fs.readFileSync(`${W}/orchestra/repo/.forge/roadmap.json`, 'utf8'));
  zapis('L4', (d.grains || []).length === 0, `grains = ${(d.grains || []).length}`);
}

// ---- L5: .env v gitignore hry
{
  let v = 'nešlo ověřit';
  let hotovo = false;
  try {
    execFileSync('git', ['-C', 'games/uo-shadows', 'check-ignore', '.forge/node/.env'], { encoding: 'utf8' });
    v = 'check-ignore VRACÍ CESTU → ignorováno';
    hotovo = true;
  } catch {
    v = 'check-ignore NIC → NENÍ ignorováno';
  }
  zapis('L5', hotovo, v);
}

// ---- L7: komentare o MAX_ATTEMPTS v conductoru
{
  const mrtvy = grep('orchestra/conductor/src/index.ts', /mrtvý kód/g);
  zapis('L7', mrtvy === 0, `komentářů tvrdících „mrtvý kód": ${mrtvy}x (:31, :233)`);
}

// ---- L9: spec.json mezi chranenymi soubory
{
  const g = grep('orchestra/repo/.github/workflows/agent.yml', /spec\.json/g);
  const g2 = grep('games/uo-shadows/.github/workflows/agent.yml', /spec\.json/g);
  zapis('L9', g > 0 && g2 > 0, `agent.yml šablona: ${g}x 'spec.json'; hra: ${g2}x`);
}

// ---- L10: test-local.ps1 $Game vs $Project
{
  const g = grep('orchestra/tools/test-local.ps1', /\$Game\b/g);
  zapis('L10', g === 0, `výskytů $Game: ${g}x (má být 0, parametr je $Project)`);
}

// ---- L16: test-cooldown / test-eskalace
{
  const ma = (p) => grep(p, /sys\.exit/g) > 0;
  zapis(
    'L16',
    !je('orchestra/tools/test-cooldown.py') || ma('orchestra/tools/test-cooldown.py'),
    `test-cooldown.py sys.exit: ${grep('orchestra/tools/test-cooldown.py', /sys\.exit/g)}x, assert: ${grep('orchestra/tools/test-cooldown.py', /\bassert\b/g)}x`,
  );
}

// ---- ST1: prepisy.json
zapis('ST1', je('orchestra/prepisy.json'), `orchestra/prepisy.json existuje: ${je('orchestra/prepisy.json')}`);
// ---- ST2: forge.config.json
zapis('ST2', je('orchestra/repo/forge.config.json'), `forge.config.json v šabloně: ${je('orchestra/repo/forge.config.json')}`);
// ---- ST4: test agent.yml
{
  const t = grep('orchestra/tools/test-ci-workflow.mjs', /agent\.yml/g);
  zapis('ST4', t > 0, `test-ci-workflow.mjs zmiňuje agent.yml: ${t}x`);
}
// ---- ST6: onboarding jako test
zapis('ST6', je('orchestra/tools/test-onboarding.py') || je('orchestra/tools/test-onboarding.mjs'), `test onboardingu existuje: ${je('orchestra/tools/test-onboarding.py') || je('orchestra/tools/test-onboarding.mjs')}`);

console.log('| # | Stav | Naměřeno |');
console.log('|---|---|---|');
for (const v of vysledky) {
  console.log(`| **${v.id}** | ${v.hotovo ? '✅ HOTOVO' : '❌ CHYBÍ'} | ${v.dukaz} |`);
}
const hotovo = vysledky.filter((v) => v.hotovo).length;
console.log(`\nHotovo: ${hotovo} z ${vysledky.length} kontrolovaných doporučení.`);
