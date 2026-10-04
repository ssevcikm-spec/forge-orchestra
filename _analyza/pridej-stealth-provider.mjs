// Vloží provider `openrouter-stealth` do profilu desktop a vygeneruje overlay,
// kterým se tentýž blok ověří headless během.
// Režimy: node pridej-stealth-provider.mjs vloz | overlay <cilovy-soubor>
import fs from 'node:fs';

const PROFIL = 'C:/Users/Ssevc/.dsh/profiles/desktop/cordis.patch.yml';
const KOTVA = '        apiKeyEnv: OPENROUTER_API_KEY';

const BLOK = [
  '      # Stealth model OpenRouteru — ověřeno headless během 4. 10. 2026',
  '      # (route openrouter-stealth, reasoningEffort high, SSE streaming).',
  '      # Je to VLASTNÍ route, ne další model v `openrouter` výš: katalog pi-ai',
  '      # ten model nezná a route `openrouter` míchá protokoly',
  '      # (anthropic-messages + openai-completions), takže by musela dostat',
  '      # api i baseURL — a to by změnilo i stávající modely. Takhle se nic nemění.',
  '      # Pozor: OpenRouter u modelu uvádí expiration_date 2026-10-05.',
  '      openrouter-stealth:',
  '        displayName: OpenRouter - Space Bunny (stealth)',
  '        apiKeyEnv: OPENROUTER_API_KEY',
  '        api: openai-completions',
  '        baseURL: https://openrouter.ai/api/v1',
  '        models:',
  '          - id: stealth/space-bunny-alpha',
  '            name: Space Bunny Alpha (stealth)',
  '            contextWindow: 1000000',
  '            maxTokens: 524288',
  '            input:',
  '              - text',
  '              - image',
  '            reasoningEfforts:',
  '              low: low',
  '              medium: medium',
  '              high: high',
  '              xhigh: xhigh',
  '              max: max',
];

const rezim = process.argv[2];

if (rezim === 'vloz') {
  const pred = fs.statSync(PROFIL);
  const raw = fs.readFileSync(PROFIL, 'utf8');
  if (raw.includes('openrouter-stealth:')) { console.log('už tam je — nic se nemění'); process.exit(0); }
  const idx = raw.lastIndexOf(KOTVA);
  if (idx < 0) { console.error('CHYBA: kotva nenalezena'); process.exit(1); }
  const eol = raw.includes('\r\n') ? '\r\n' : '\n';
  const konecRadku = raw.indexOf('\n', idx);
  if (konecRadku < 0) { console.error('CHYBA: kotva na posledním řádku'); process.exit(1); }
  const novy = raw.slice(0, konecRadku + 1) + BLOK.join(eol) + eol + raw.slice(konecRadku + 1);
  // soubor mohl být mezitím přepsán běžící aplikací → zkontroluj před zápisem
  const ted = fs.statSync(PROFIL);
  if (ted.mtimeMs !== pred.mtimeMs || ted.size !== pred.size) {
    console.error('CHYBA: soubor se během operace změnil (aplikace ho přepsala) — zkus znovu');
    process.exit(2);
  }
  fs.writeFileSync(PROFIL, novy, 'utf8');
  const zpet = fs.readFileSync(PROFIL, 'utf8');
  const kontroly = {
    'novy provider': zpet.includes('openrouter-stealth:'),
    'model': zpet.includes('stealth/space-bunny-alpha'),
    'puvodni google': zpet.includes('gemini-3.1-flash-lite-image'),
    'puvodni openrouter': zpet.includes('apiKeyEnv: OPENROUTER_API_KEY'),
    'jeden vyskyt noveho klice': (zpet.match(/openrouter-stealth:/g) ?? []).length === 1,
  };
  for (const [k, v] of Object.entries(kontroly)) console.log(`${v ? 'OK  ' : 'CHYBA'} ${k}`);
  const vse = Object.values(kontroly).every(Boolean);
  console.log(`zapsáno: ${novy.length} znaků, eol=${eol === '\r\n' ? 'CRLF' : 'LF'}`);
  process.exit(vse ? 0 : 1);
}

if (rezim === 'overlay') {
  const cil = process.argv[3];
  if (!cil) { console.error('chybí cílový soubor'); process.exit(1); }
  const eol = '\n';
  const radky = fs.readFileSync(PROFIL, 'utf8').split(/\r?\n/);
  const start = radky.findIndex((l) => l.startsWith('- id: llm-pi-ai'));
  if (start < 0) { console.error('CHYBA: řádek llm-pi-ai nenalezen'); process.exit(1); }
  let konec = radky.length;
  for (let i = start + 1; i < radky.length; i++) {
    if (radky[i].startsWith('# ') || radky[i].trim() === '') { konec = i; break; }
  }
  const row = radky.slice(start, konec);
  const out = [
    '# Overlay vygenerovaný z ŽIVÉHO profilu desktop — ověřuje přesně ten blok,',
    '# který je v cordis.patch.yml (config se u patche nahrazuje CELÝ).',
    ...row,
    '- id: agent-default-model',
    '  config:',
    '    provider: openrouter-stealth',
    '    model: stealth/space-bunny-alpha',
    '    reasoningEffort: high',
    '',
  ].join(eol);
  fs.writeFileSync(cil, out, 'utf8');
  console.log(`overlay zapsán: ${cil} (${out.split('\n').length} řádků, z profilu řádky ${start + 1}–${konec})`);
  process.exit(0);
}

console.error('pouzij: vloz | overlay <soubor>');
process.exit(2);
