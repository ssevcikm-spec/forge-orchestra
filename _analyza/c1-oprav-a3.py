#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Úkol C1 — `_analyza\\a3-kontrola.mjs`: sekce D čte `/tasks`, což NENÍ endpoint.

CO BYLO NAMĚŘENO (plánovací session, 2. 10. 2026):
  `GET /tasks` vrací **HTTP 200** a **rozcestník služby**
  (`{"service":"forge-conductor","endpoints":[...]}`) — žádné úloze.
  Nástroj z něj čte `tasks || []`, takže dostane **vždy prázdné pole**
  a u každé granule vypíše „(žádná úloha)". Podle toho výstupu se přitom
  rozhodovalo (a `HANDOFF.md` §14.2 z toho udělal nepravdivý závěr).

CO DĚLÁ TENHLE PATCH:
  sekce D se přepíše tak, aby úlohy braly z **`/queue`** (kde opravdu jsou)
  a mapovaly je na granule přes **`/roadmap`** (`item_id -> task_id`).
  Když úloha není, musí to být **NAMĚŘENÁ NULA** s rozlišeným důvodem:
  chybí `task_id` v roadmape / `task_id` není v `/queue` — ne tiché „(žádná
  úloha)". A když `/queue` nevrátí parsovatelný seznam, nástroj to hlásí
  jako CHYBU (dosud by mlčel).

Použití:
    python _analyza\\c1-oprav-a3.py            # zapíše
    python _analyza\\c1-oprav-a3.py --zpet     # vrátí zpět
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ANALYZA = Path(__file__).resolve().parent
CIL = ANALYZA / "a3-kontrola.mjs"
ZALOHA = ANALYZA / "c1-a3-kontrola-puvodni.mjs"

# ---------------------------------------------------------------- starý blok --
STARY = """console.log('\\n════ D. D1: STAVY ÚLOH NOVÝCH GRANULÍ ════');
// D1 je zdroj pravdy o tom, co conductor OPRAVDU udělal (nejen co si myslí cache).
const tasks = await cond('/tasks');
const seznam = Array.isArray(tasks) ? tasks : (tasks.tasks || []);
for (const g of zajimave) {
  const t = seznam.filter((x) => String(x.item_id || '').includes(g));
  if (!t.length) { console.log(`  ${g.padEnd(22)} (žádná úloha)`); continue; }
  for (const u of t.slice(-3)) console.log(`  ${g.padEnd(22)} id=${u.id} stav=${u.status} pokusů=${u.attempts} run=${String(u.run_key || '').slice(0, 12)}`);
}
"""

# ---------------------------------------------------------------- nový blok ---
NOVY = """console.log('\\n════ D. D1: STAVY ÚLOH NOVÝCH GRANULÍ ════');
// D1 je zdroj pravdy o tom, co conductor OPRAVDU udělal (nejen co si myslí cache).
//
// ⚠ POZOR — `/tasks` NENÍ ENDPOINT (naměřeno 2. 10. 2026). Vrací HTTP 200
// a ROZCESTNÍK SLUŽBY: `{"service":"forge-conductor","endpoints":[...]}`.
// Původní verze z něj četla `tasks || []`, takže dostala VŽDY prázdné pole
// a u každé granule vypsala „(žádná úloha)" — a vypadalo to jako naměřený
// stav. Úlohy jsou v `/queue`; na granule se mapují přes `/roadmap`
// (`item_id`, `status`, `task_id`), protože `/queue` `item_id` NEOBSAHUJE.
const rq = await cond('/queue');
const fronta = Array.isArray(rq) ? rq : (rq.tasks || []);
const frontaOk = Array.isArray(fronta) && fronta.length > 0;
const rmap = new Map();
for (const row of r) rmap.set(String(row.item_id || '').replace('uo-shadows/', ''), row);
console.log(`  /queue vrátil ${fronta.length} úloh, /roadmap ${r.length} řádků`);
if (!frontaOk) {
  // Nula a nezměřeno nejsou úspěch: musí to být vidět (AGENTS.md).
  console.log(`  CHYBA /queue nevrátil parsovatelný seznam úloh: ${JSON.stringify(rq).slice(0, 200)}`);
  chyb++;
}
for (const g of zajimave) {
  const row = rmap.get(g);
  if (!row) { console.log(`  ${g.padEnd(22)} v /roadmap NENÍ (granule ještě není založená)`); continue; }
  const tid = row.task_id;
  if (tid === null || tid === undefined) {
    console.log(`  ${g.padEnd(22)} roadmap=${row.status}  task_id=null (úloha se ještě nezaložila)`);
    continue;
  }
  const u = fronta.find((x) => Number(x.id) === Number(tid));
  if (!u) {
    console.log(`  ${g.padEnd(22)} roadmap=${row.status}  task_id=${tid} — v /queue NENÍ (fronta ${fronta.length} úloh)`);
    continue;
  }
  console.log(`  ${g.padEnd(22)} roadmap=${row.status}  úloha #${u.id} stav=${u.status} pokusů=${u.attempts}`);
}
"""


def main() -> int:
    zpet = "--zpet" in sys.argv
    if not CIL.exists():
        print("CHYBA: %s neexistuje" % CIL)
        return 2

    text = CIL.read_text(encoding="utf-8")

    if zpet:
        if not ZALOHA.exists():
            print("CHYBA: záloha %s neexistuje" % ZALOHA)
            return 2
        puvodni = ZALOHA.read_text(encoding="utf-8")
        CIL.write_bytes(puvodni.encode("utf-8"))
        assert CIL.read_text(encoding="utf-8") == puvodni
        print("OK: vráceno ze zálohy (%d znaků)" % len(puvodni))
        return 0

    if NOVY in text:
        print("OK: oprava už v souboru je")
        return 0

    pocet = text.count(STARY)
    if pocet != 1:
        print("CHYBA: starý blok nalezen %d× — očekávám 1×." % pocet)
        return 2

    # záloha PŘED zápisem (kopií, ne spoléháním na git)
    if not ZALOHA.exists():
        ZALOHA.write_bytes(text.encode("utf-8"))
        print("záloha: %s" % ZALOHA.name)

    novy = text.replace(STARY, NOVY, 1)
    assert novy != text, "MUTACE NEPROBĚHLA"
    CIL.write_bytes(novy.encode("utf-8"))

    z5 = CIL.read_text(encoding="utf-8")
    assert z5 == novy, "zapsaný obsah nesedí"
    assert "cond('/tasks')" not in z5, "staré volání /tasks v souboru zůstalo"
    assert "cond('/queue')" in z5, "nové volání /queue se nevložilo"
    print("OK: %s přepsán (%d → %d znaků)" % (CIL, len(text), len(z5)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
