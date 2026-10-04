// Ověří čísla z HANDOFF.md §7 (tři verze vision.test.mjs) a §9.
// Počítá volání test( ve zdrojáku vs. skutečný výsledek — to je to, co se má měřit.
import fs from 'node:fs';

const soubory = [
  ['root', 'vision.test.mjs'],
  ['sablona', 'orchestra/repo/.forge/node/vision.test.mjs'],
  ['hra', 'games/uo-shadows/.forge/node/vision.test.mjs'],
];

console.log('=== Počty volání test( ve zdrojáku ===');
for (const [jmeno, p] of soubory) {
  if (!fs.existsSync(p)) {
    console.log(`${jmeno.padEnd(9)} ${p} -> NEEXISTUJE`);
    continue;
  }
  const t = fs.readFileSync(p, 'utf8');
  // test('...') nebo test("...") nebo await test(
  const volani = (t.match(/\btest\s*\(/g) || []).length;
  console.log(
    `${jmeno.padEnd(9)} ${String(fs.statSync(p).size).padStart(6)} B   test( = ${volani}   ${p}`,
  );
}

console.log('\n=== Hash vision.mjs (kód) — má být shodný ===');
for (const p of ['orchestra/repo/.forge/vision.mjs', 'games/uo-shadows/.forge/vision.mjs']) {
  const { createHash } = await import('node:crypto');
  const h = createHash('sha256').update(fs.readFileSync(p)).digest('hex');
  console.log(`  ${h}  ${p}`);
}

console.log('\n=== Je vision.test.mjs ve seznamu drift kontroly? ===');
const drift = fs.readFileSync('orchestra/tools/kontrola-driftu.mjs', 'utf8');
console.log('  zminen v kontrola-driftu.mjs:', drift.includes('vision.test.mjs'));
