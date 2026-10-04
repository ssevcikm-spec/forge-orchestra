// Ověření NASAZENÍ — třetí krok důkazu podle AGENTS.md:
// „server posílá NOVÝ build" (HTTP 200 nestačí, starý web odpovídá taky).
// Síť z PowerShellu nejde (schannel) → Node fetch.
const URLS = [
  'https://ssevcikm-spec.github.io/uo-shadows/index.png',
  'https://ssevcikm-spec.github.io/uo-shadows/index.html',
];

for (const u of URLS) {
  try {
    const r = await fetch(u, { method: 'HEAD' });
    console.log(`${r.status}  last-modified: ${r.headers.get('last-modified')}  ${u}`);
  } catch (e) {
    console.log(`CHYBA ${e.message}  ${u}`);
  }
}
// Push byl podle HANDOFF.md §21.8 v 14:43:10 UTC; build musí být POZDĚJI.
console.log('\nreferenční čas pushе (HANDOFF §21.8): 2026-10-02 14:43:10 UTC');
