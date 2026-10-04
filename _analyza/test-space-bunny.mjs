// Živý test modelu stealth/space-bunny-alpha přes OpenRouter.
// Klíč se čte z DSH credential storu a NIKDY se nevypisuje.
// Použití: node _analyza\test-space-bunny.mjs
import fs from 'node:fs';

const CRED = 'C:/Users/Ssevc/.dsh/.credentials.yaml';
const raw = fs.readFileSync(CRED, 'utf8');
let key = null;
for (const line of raw.split(/\r?\n/)) {
  const m = /^\s{2}([A-Z0-9_]+):\s*(\S+)\s*$/.exec(line);
  if (m && m[1] === 'OPENROUTER_API_KEY') { key = m[2]; break; }
}
if (!key) { console.error('CHYBA: OPENROUTER_API_KEY v credential storu nenalezen'); process.exit(1); }
console.log('klic nacten: delka', key.length, 'prefix', key.slice(0, 7) + '...');

const body = {
  model: 'stealth/space-bunny-alpha',
  stream: true,
  messages: [{ role: 'user', content: "How many r's are in the word 'strawberry'?" }],
  reasoning: { effort: 'low' },
};

const t0 = Date.now();
const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${key}`,
  },
  body: JSON.stringify(body),
});
console.log('HTTP', res.status, res.headers.get('content-type'), `${Date.now() - t0} ms`);
if (!res.ok) { console.log(await res.text()); process.exit(1); }

const reader = res.body.getReader();
const dec = new TextDecoder();
let buf = '', text = '', reasoning = '', usage = null, chunks = 0, model = null;
for (;;) {
  const { value, done } = await reader.read();
  if (done) break;
  buf += dec.decode(value, { stream: true });
  let i;
  while ((i = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, i).trim();
    buf = buf.slice(i + 1);
    if (!line.startsWith('data:')) continue;
    const payload = line.slice(5).trim();
    if (payload === '[DONE]') continue;
    let j; try { j = JSON.parse(payload); } catch { continue; }
    chunks++;
    model ??= j.model;
    const d = j.choices?.[0]?.delta ?? {};
    if (d.content) text += d.content;
    if (d.reasoning) reasoning += d.reasoning;
    if (j.usage) usage = j.usage;
  }
}
console.log('model na wire:', model);
console.log('SSE chunku:', chunks);
console.log('reasoning znaku:', reasoning.length, '| text znaku:', text.length);
console.log('text:', JSON.stringify(text.slice(0, 200)));
console.log('usage:', JSON.stringify(usage));
console.log('reasoning tokens:', usage?.completion_tokens_details?.reasoning_tokens);
