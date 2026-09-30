// Ověří dostupnost poskytovatelů a změní, jak velký výstup zvládnou.
//
// Odpovídá na otázku „nemají velké modely problém s dávkou tokenů?" přímo:
// pošle modelu stejné zadání jako agent a změří, kolik tokenů vrátí a jestli
// dodrží formát SEARCH/REPLACE.
import { readFileSync } from 'node:fs';

const SECRETS = 'C:/Users/Ssevc/Local-Deepseek/orchestra/.secrets';
const klic = (soubor) => {
  try { return readFileSync(`${SECRETS}/${soubor}`, 'utf8').replace(/^\uFEFF/, '').trim(); }
  catch { return ''; }
};

const POSKYTOVATELE = [
  { name: 'groq', baseUrl: 'https://api.groq.com/openai/v1', key: klic('groq_key.txt'),
    models: ['openai/gpt-oss-120b', 'openai/gpt-oss-20b'], strong: ['openai/gpt-oss-120b'] },
  { name: 'openrouter', baseUrl: 'https://openrouter.ai/api/v1', key: klic('openrouter_key.txt'),
    models: ['qwen/qwen3.8-27b:free', 'google/gemma-4-31b-it:free'], strong: [] },
];

// Stejné zadání, jaké dostává agent u malé granule (core.skills).
const ZADANI = `Vytvoř soubor scripts/skills.gd s tímto obsahem a nic jiného neřeš:

extends Node

var dovednosti: Dictionary = {
    "tezba": 0,
    "drevorubectvi": 0,
    "kovarstvi": 0,
    "boj_na_blizko": 0
}

func add(skill: String, n: int) -> void:
    dovednosti[skill] = clamp(dovednosti[skill] + n, 0, 100)

func hodnota(skill: String) -> int:
    return dovednosti[skill]

Odpověz POUZE blokem SEARCH/REPLACE pro nový soubor (prázdná sekce SEARCH).`;

async function zmer(poskytovatel, model) {
  const ctrl = new AbortController();
  const cas = setTimeout(() => ctrl.abort(), 120000);
  const t0 = Date.now();
  try {
    const res = await fetch(`${poskytovatel.baseUrl}/chat/completions`, {
      method: 'POST',
      signal: ctrl.signal,
      headers: {
        Authorization: `Bearer ${poskytovatel.key}`,
        'content-type': 'application/json',
        'HTTP-Referer': 'https://github.com/',
        'X-Title': 'forge-mereni',
      },
      body: JSON.stringify({
        model,
        messages: [{ role: 'user', content: ZADANI }],
        max_tokens: 2000,
      }),
    });
    const ms = Date.now() - t0;
    const text = await res.text();
    if (!res.ok) return { ok: false, ms, chyba: `HTTP ${res.status}: ${text.slice(0, 140)}` };
    const d = JSON.parse(text);
    const obsah = d.choices?.[0]?.message?.content ?? '';
    const reasoning = d.choices?.[0]?.message?.reasoning_content ?? d.choices?.[0]?.message?.reasoning ?? '';
    const u = d.usage || {};
    return {
      ok: true, ms,
      vstup: u.prompt_tokens, vystup: u.completion_tokens,
      delka: obsah.length, reasoningDelka: String(reasoning).length,
      maSearchReplace: /<<<<<<< SEARCH/.test(obsah) && />>>>>>> REPLACE/.test(obsah),
      konec: obsah.slice(0, 90).replace(/\n/g, ' ⏎ '),
    };
  } catch (e) {
    return { ok: false, ms: Date.now() - t0, chyba: String(e).slice(0, 140) };
  } finally {
    clearTimeout(cas);
  }
}

for (const p of POSKYTOVATELE) {
  console.log(`\n=== ${p.name} ===`);
  if (!p.key) { console.log('  (klíč není v .secrets – přeskakuji)'); continue; }
  console.log(`  klíč: ${p.key.slice(0, 6)}… (${p.key.length} znaků)`);
  for (const m of p.models) {
    const silny = p.strong.includes(m) ? ' [STRONG]' : '';
    const r = await zmer(p, m);
    if (!r.ok) { console.log(`  ✗ ${m}${silny}: ${r.chyba}`); continue; }
    console.log(`  ✓ ${m}${silny}`);
    console.log(`      ${r.ms} ms | vstup ${r.vstup} tok | výstup ${r.vystup} tok | `
      + `text ${r.delka} zn | reasoning ${r.reasoningDelka} zn`);
    console.log(`      SEARCH/REPLACE formát: ${r.maSearchReplace ? 'DODRŽEN' : 'CHYBÍ'}`);
    console.log(`      začátek: ${r.konec}`);
  }
}
