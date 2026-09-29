#!/usr/bin/env node
// Ovládání orchestra z příkazové řádky: založení úkolu, fronta, stav, ruční tik.
//
// Použití:
//   node bin/task.mjs add "Nazev ukolu" "Zadani pro agenta" [code|assets|build]
//   node bin/task.mjs queue
//   node bin/task.mjs failed
//   node bin/task.mjs status
//   node bin/task.mjs tick
//
// Adresa a tajemství se berou z prostředí FORGE_URL / FORGE_SECRET, nebo
// ze souboru gameforge/orchestra/.env (řádky KEY=HODNOTA).
//
// Proč Node a ne curl/Invoke-RestMethod: PowerShell i curl na této stanici
// neumí navázat TLS spojení (schannel: SEC_E_NO_CREDENTIALS). Node umí.

import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const ENV_FILE = join(HERE, '..', '.env');

if (existsSync(ENV_FILE)) {
  for (const line of readFileSync(ENV_FILE, 'utf8').split('\n')) {
    const t = line.trim();
    if (!t || t.startsWith('#')) continue;
    const i = t.indexOf('=');
    if (i > 0 && !process.env[t.slice(0, i)]) {
      process.env[t.slice(0, i)] = t.slice(i + 1).trim();
    }
  }
}

const URL_BASE = (process.env.FORGE_URL || '').replace(/\/$/, '');
const SECRET = process.env.FORGE_SECRET || '';
const [cmd = 'status', ...args] = process.argv.slice(2);

if (!URL_BASE) {
  console.error('Chybí FORGE_URL. Nastav ho v prostředí nebo do gameforge/orchestra/.env');
  process.exit(2);
}

async function call(path, { method = 'GET', body } = {}) {
  const headers = { 'x-forge-secret': SECRET };
  if (body) headers['content-type'] = 'application/json';
  const res = await fetch(`${URL_BASE}${path}`, {
    method, headers, body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }
  return { status: res.status, data };
}

if (cmd === 'add') {
  // --target lan  → úkol pro domácí uzel (telefon/PC) místo GitHub Actions
  const ti = args.indexOf('--target');
  let target = 'cloud';
  if (ti >= 0) {
    target = args[ti + 1] || 'lan';
    args.splice(ti, 2);
  }

  // Pro domácí uzly je potřeba říct, CO má uzel udělat (payload.steps).
  // Krok = "shell:<prikaz>", "godot-import", "godot-test",
  //        "godot-export:<preset>:<cesta>", "python:<skript>", "make-dir:<slozka>"
  const opt = (flag) => {
    const i = args.indexOf(flag);
    if (i < 0) return null;
    const v = args[i + 1] || null;
    args.splice(i, 2);
    return v;
  };
  const steps = opt('--steps');
  const repo = opt('--repo');
  const name = opt('--name');
  const ref = opt('--ref');
  const artifacts = opt('--artifacts');

  const [title, prompt, kind = 'code'] = args;
  if (!title || !prompt) {
    console.error('Použití: node bin/task.mjs add "Nazev" "Zadani" [kind] [--target lan]');
    console.error('  Pro domácí uzel navíc: --repo <url> --name <slozka> --steps "godot-import;godot-test"');
    console.error('                        [--ref vetev] [--artifacts slozka]');
    process.exit(2);
  }

  const payload = {};
  if (repo) payload.repo = repo;
  if (name) payload.name = name;
  if (ref) payload.ref = ref;
  if (artifacts) payload.artifacts = artifacts;
  if (steps) payload.steps = steps.split(';').map((s) => s.trim()).filter(Boolean);

  const body = { title, prompt, kind, target };
  if (Object.keys(payload).length) body.payload = payload;
  const r = await call('/task', { method: 'POST', body });
  console.log(r.status, JSON.stringify(r.data, null, 2));
} else if (cmd === 'poll') {
  const r = await call('/poll', { method: 'POST' });
  console.log(r.status, JSON.stringify(r.data, null, 2));
} else if (cmd === 'workers') {
  const r = await call('/workers');
  console.table(r.data.workers || r.data);
} else if (cmd === 'queue') {
  const r = await call('/queue');
  console.table(r.data.tasks || r.data);
} else if (cmd === 'failed') {
  // Selhané úkoly + jejich běhy s log_tail (podklad pro forge replan)
  const r = await call('/failed');
  const tasks = (r.data.tasks || []).map((t) => ({
    id: t.id,
    title: (t.title || '').slice(0, 44),
    grain: (t.payload && t.payload.grain) || '',
    repo: (t.payload && t.payload.repo) || '',
    pokusu: t.attempts,
    behu: (t.runs || []).length,
  }));
  console.table(tasks);
  for (const t of (r.data.tasks || [])) {
    for (const run of t.runs || []) {
      if (run.log_tail) console.log(`#${t.id} ${run.run_key.slice(0, 8)}: ${(run.summary || '').slice(0, 80)}`);
    }
  }
} else if (cmd === 'status') {
  const r = await call('/status');
  console.table(r.data.runs || r.data);
} else if (cmd === 'tick') {
  const r = await call('/tick', { method: 'POST' });
  console.log(r.status, JSON.stringify(r.data, null, 2));
} else if (cmd === 'health') {
  const r = await call('/health');
  console.log(r.status, JSON.stringify(r.data, null, 2));
} else {
  console.error(`Neznámý příkaz '${cmd}'. Na výběr: add, queue, failed, status, workers, tick, poll, health`);
  process.exit(2);
}
