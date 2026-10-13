#!/usr/bin/env node
// K3/K4 — ODKUD BRÁT „DOKUMENT PŘED ROZDĚLENÍM NA SEKCE“.
//
// PROČ TO EXISTUJE (naměřeno 13. 10. 2026, hned po prvním commitu K3/K4):
// nástroje K3 srovnávají nové sekce s PŮVODNÍM `repo/CONVENTIONS.md`. Dokud
// byly změny jen v pracovním stromě, stačilo `git show HEAD:repo/CONVENTIONS.md`.
// Po commitu je ale v `HEAD` už ROZCESTNÍK — a nástroj tiše měří jiný dokument:
//   * brána rozdělení hlásila „0 bloků originálu, 14 chyb“ (index vs index),
//   * měření aiderem by jako „starý stav“ četlo rozcestník (836 t) místo
//     celého dokumentu (3 802 t) — a rozdíl A/B by zmizel.
// Proto se základ hledá DYNAMICKY: commit, který PŘIDAL první sekci
// (`repo/CONVENTIONS/01-typy.md`), a jeho rodič. Když rozdělení ještě
// neproběhlo, padá to zpátky na `HEAD`.
//
// Použití:
//   import { revizePredRozdelenim } from './_revize-konvenci.mjs';
//   const rev = revizePredRozdelenim();

import { spawnSync } from 'node:child_process';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ORCH = dirname(dirname(fileURLToPath(import.meta.url)));
export const PRVNI_SEKCE = 'repo/CONVENTIONS/01-typy.md';

export function revizePredRozdelenim() {
  const r = spawnSync('git', ['-C', ORCH, 'log', '--diff-filter=A', '--format=%H', '-1',
    '--', PRVNI_SEKCE], { encoding: 'utf8' });
  const sha = String(r.stdout || '').trim().split('\n').filter(Boolean)[0];
  return sha ? `${sha}^` : 'HEAD';
}

/** Text původního (nerozděleného) dokumentu z gitu. */
export function celyDokumentPredRozdelenim(spawn = spawnSync) {
  const r = spawn('git', ['-C', ORCH, 'show', `${revizePredRozdelenim()}:repo/CONVENTIONS.md`],
    { encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 });
  if (r.status !== 0) return null;
  return r.stdout;
}
