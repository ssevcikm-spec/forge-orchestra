#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""KROK B1 — `naposledy_selhalo` místo `updated_at` (vada S12).

CO JE VADA (naměřeno 2. 10. 2026, `orchestra\\tools\\test-cooldown.py`):
  Cooldown guard v `roadmapTick` se ptá na `roadmap.updated_at`:
  `const ts = r.tupd || r.rupd`, kde `rupd = roadmap.updated_at`. Jenže tenhle
  sloupec se přepisuje při KAŽDÉ změně řádku — mimo jiné při VZNIKU granule
  (`INSERT … status='queued', updated_at=datetime('now')`). Nová granule tedy
  vypadá jako „právě selhala" a **3 h se nevydá**.

  Naměřeno, jak to vidí test: scénář „NOVÁ granule (vznikla teď, neselhal)"
  → má se vydat=True, vydá se=False → VADA.

CO B1 DĚLÁ:
  1. `conductor/schema.sql` (i kopie v `repo/`): přidá `naposledy_selhalo`.
  2. `conductor/src/index.ts`: self-migrace přidá sloupec do živé D1, cesty,
     které zapisují SELHÁNÍ, ho nastaví — a cooldown guard se ptá NA NĚJ.

  `updated_at` se NEPŘESTÁVÁ plnit: pořád nese „poslední změna řádku" a jiné
  kontroly ho čtou. Mění se jen to, na co se ptá cooldown.

POZOR — DVĚ KOPIE `schema.sql`: `orchestra/conductor/schema.sql`
a `orchestra/repo/.forge/…`? Ne: kopie je `orchestra/repo/…` bez schematu.
  Šablona `orchestra/repo/` schema.sql NEMÁ, proto se mění jen jedna kopie
  a ověřuje se to na konci (sondu najde `kontrola-driftu`).

Použití:
    python _analyza\\f1-b1-conductor.py
    python _analyza\\f1-b1-conductor.py --zpet
"""

import hashlib
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(__file__).resolve().parent.parent
ORCH = WS / "orchestra"
SCHEMA = ORCH / "conductor" / "schema.sql"
INDEX = ORCH / "conductor" / "src" / "index.ts"

# ────────────────────────────────────────────────────────────── SCHEMA ──────
SCHEMA_STARY = """  updated_at  TEXT NOT NULL DEFAULT (datetime('now'))  -- poslední změna (cooldown retry)
);"""

SCHEMA_NOVY = """  updated_at  TEXT NOT NULL DEFAULT (datetime('now')),  -- poslední změna řádku
  -- KDY NAPOSLEDY SELHALA (B1, 2. 10. 2026). Do té doby se cooldown ptal na
  -- `updated_at`, což je ale i čas VZNIKU řádku — nová granule proto vypadala
  -- jako „právě selhala" a RETRY_HOURS se na ni vztáhl (vada S12). NULL =
  -- ještě neselhala.
  naposledy_selhalo TEXT
);"""

SCHEMA_MIGRACE_STARY = """-- Migrace starých tabulek: roadmap.updated_at přibyl kvůli cooldownu
-- opakovaných pokusů selhaných granulí (RETRY_HOURS).
-- ALTER TABLE roadmap ADD COLUMN updated_at TEXT NOT NULL DEFAULT (datetime('now'));"""

SCHEMA_MIGRACE_NOVY = """-- Migrace starých tabulek: roadmap.updated_at přibyl kvůli cooldownu
-- opakovaných pokusů selhaných granulí (RETRY_HOURS).
-- ALTER TABLE roadmap ADD COLUMN updated_at TEXT NOT NULL DEFAULT (datetime('now'));
-- B1 (2. 10. 2026): cooldown se ptá na `naposledy_selhalo`, ne na `updated_at`.
-- ALTER TABLE roadmap ADD COLUMN naposledy_selhalo TEXT;"""

# ──────────────────────────────────────────────────────────────── INDEX ─────
MIGRACE_STARY = """  await env.DB.prepare("ALTER TABLE roadmap ADD COLUMN updated_at TEXT")
    .run().catch((e) => console.log("roadmap.updated_at: " + String(e).slice(0, 100)));
  await env.DB.prepare("UPDATE roadmap SET updated_at = created_at WHERE updated_at IS NULL")
    .run().catch(() => undefined);"""

MIGRACE_NOVY = """  await env.DB.prepare("ALTER TABLE roadmap ADD COLUMN updated_at TEXT")
    .run().catch((e) => console.log("roadmap.updated_at: " + String(e).slice(0, 100)));
  await env.DB.prepare("UPDATE roadmap SET updated_at = created_at WHERE updated_at IS NULL")
    .run().catch(() => undefined);
  // B1 (2. 10. 2026): cooldown se ptá na `naposledy_selhalo`, ne na `updated_at`.
  // Sloupec se přidává stejnou idempotentní cestou; `NULL` znamená „ještě
  // neselhala", takže čerstvá granule NENÍ v cooldownu (vada S12).
  await env.DB.prepare("ALTER TABLE roadmap ADD COLUMN naposledy_selhalo TEXT")
    .run().catch((e) => console.log("roadmap.naposledy_selhalo: " + String(e).slice(0, 100)));"""

SELECT_STARY = """    `SELECT r.item_id, r.task_id, r.status AS rstatus, r.updated_at AS rupd,
            t.status AS tstatus, t.updated_at AS tupd
       FROM roadmap r LEFT JOIN tasks t ON t.id = r.task_id`,"""

SELECT_NOVY = """    `SELECT r.item_id, r.task_id, r.status AS rstatus, r.updated_at AS rupd,
            r.naposledy_selhalo AS rfail,
            t.status AS tstatus, t.updated_at AS tupd
       FROM roadmap r LEFT JOIN tasks t ON t.id = r.task_id`,"""

GUARD_STARY = """    const ts = r.tupd || r.rupd || null;
    const stale = !ts
      || (Date.now() - Date.parse(String(ts).replace(" ", "T") + "Z") > retryH * 3600e3);
    if (!stale) blocked.add(r.item_id);"""

GUARD_NOVY = """    // B1 (2. 10. 2026): rozhoduje `naposledy_selhalo`, NE `updated_at`.
    // `updated_at` je i čas VZNIKU řádku, takže nová granule vypadala jako
    // „právě selhala" a RETRY_HOURS se na ni vztáhl, i když nikdy neselhala
    // (vada S12, naměřeno `tools/test-cooldown.py`). `tupd` zůstává jako
    // záložní cesta pro řádky, u kterých sloupec ještě není vyplněný.
    const ts = r.rfail || r.tupd || null;
    const stale = !ts
      || (Date.now() - Date.parse(String(ts).replace(" ", "T") + "Z") > retryH * 3600e3);
    if (!stale) blocked.add(r.item_id);"""

TYP_STARY = """    rupd: string | null;"""

TYP_NOVY = """    rupd: string | null;
    rfail: string | null;"""

# Zápis selhání: VŠECHNA místa, kde se selhání zapisuje do roadmapy.
# POZOR — jsou DVĚ a musí je opravit obojí:
#   * `pollRuns` (řádek ~431) zapisuje při KAŽDÉM selhání ('queued'/'failed'),
#   * `/report` (řádek ~1445) jen u POSLEDNÍHO pokusu ('failed').
# Kdyby se opravilo jen jedno, cooldown by se v tom druhém případě nevynutil.
FAIL1_STARY = """      await env.DB.prepare(
        `UPDATE roadmap SET status = ?, updated_at = datetime('now') WHERE task_id = ?`,
      ).bind(nextStatus === "failed" ? "failed" : "queued", row.task_id).run().catch(() => undefined);"""

FAIL1_NOVY = """      // B1: tohle je SELHÁNÍ — proto se plní `naposledy_selhalo` (z něj čte
      // cooldown). `updated_at` se plní dál, ale cooldown ho už nečte.
      await env.DB.prepare(
        `UPDATE roadmap SET status = ?, updated_at = datetime('now'),
           naposledy_selhalo = datetime('now') WHERE task_id = ?`,
      ).bind(nextStatus === "failed" ? "failed" : "queued", row.task_id).run().catch(() => undefined);"""

FAIL2_STARY = """        if (nextStatus === "failed") {
          await env.DB.prepare(
            "UPDATE roadmap SET status='failed', updated_at=datetime('now') WHERE task_id=?",
          ).bind(run.task_id).run().catch(() => undefined);
        }"""

FAIL2_NOVY = """        // B1: `naposledy_selhalo` se plní při KAŽDÉM selhání, ne jen u
        // posledního pokusu — cooldown se ptá na něj, takže kdyby tu chybělo,
        // granule by se po opakovatelném selhání vydala okamžitě.
        if (nextStatus === "failed") {
          await env.DB.prepare(
            `UPDATE roadmap SET status='failed', updated_at=datetime('now'),
               naposledy_selhalo = datetime('now') WHERE task_id=?`,
          ).bind(run.task_id).run().catch(() => undefined);
        } else {
          await env.DB.prepare(
            `UPDATE roadmap SET naposledy_selhalo = datetime('now') WHERE task_id=?`,
          ).bind(run.task_id).run().catch(() => undefined);
        }"""

# DRUHÝ GUARD TÉHOŽ COOLDOWNU: dispatch smyčka (řádek ~907) se ptá
# `rm.updated_at > datetime('now', ?)`. Je to TÁŽ vada S12 — nová granule má
# `updated_at` z doby vzniku, takže se do cooldownu chytí taky.
GUARD2_STARY = """    const readyAll = await env.DB.prepare(
      `SELECT * FROM tasks WHERE status='ready' AND target='cloud'
         AND NOT EXISTS (
           SELECT 1 FROM roadmap rm
            WHERE rm.task_id = tasks.id
              AND rm.updated_at > datetime('now', ?)
         )
        ORDER BY id LIMIT 25`,
    ).bind(`-${retryH} hours`).all<Task>();"""

GUARD2_NOVY = """    const readyAll = await env.DB.prepare(
      `SELECT * FROM tasks WHERE status='ready' AND target='cloud'
         AND NOT EXISTS (
           SELECT 1 FROM roadmap rm
            WHERE rm.task_id = tasks.id
              AND rm.naposledy_selhalo > datetime('now', ?)
         )
        ORDER BY id LIMIT 25`,
    ).bind(`-${retryH} hours`).all<Task>();"""

KOMENT_GUARD_STARY = """    // Rozhoduje proto VÝHRADNĚ čas poslední změny řádku, který failure zapisuje
    // v obou případech. Řádek se nemaže, takže je to spolehlivý nositel
    // cooldownu; dispatch smyčka se ptá jen na úlohy, které už jsou `ready`."""

KOMENT_GUARD_NOVY = """    // B1 (2. 10. 2026): rozhoduje `naposledy_selhalo`, ne `updated_at`.
    // Původní úvaha („čas poslední změny řádku je spolehlivý nositel cooldownu")
    // platila jen do chvíle, než se do téhož sloupce začal psát i VZNIK granule:
    // `INSERT … status='queued', updated_at=datetime('now')`. Od té chvíle byla
    // nová granule v cooldownu, i když nikdy neselhala (vada S12).
    // Dispatch smyčka se ptá jen na úlohy, které už jsou `ready`."""


def zmen(text: str, stary: str, novy: str, popis: str) -> str:
    pocet = text.count(stary)
    if pocet != 1:
        print("CHYBA: %s — nalezeno %d×, očekávám 1×" % (popis, pocet))
        sys.exit(2)
    novy_text = text.replace(stary, novy, 1)
    assert novy_text != text, "MUTACE NEPROBĚHLA: %s" % popis
    return novy_text


def main() -> int:
    zpet = "--zpet" in sys.argv
    zalohy = {SCHEMA: SCHEMA.with_suffix(".sql.b1zaloha"),
              INDEX: INDEX.with_suffix(".ts.b1zaloha")}

    if zpet:
        for cil, zal in zalohy.items():
            if not zal.is_file():
                print("CHYBA: záloha %s není" % zal)
                return 2
            cil.write_bytes(zal.read_bytes())
            print("vráceno: %s" % cil.name)
        return 0

    schema = SCHEMA.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")

    if "naposledy_selhalo" in schema and "naposledy_selhalo" in index:
        print("OK: B1 už v obou souborech je")
        return 0

    # zálohy kopií (ne spoléháním na git — soubor může mít necommitnuté změny)
    for cil, zal in zalohy.items():
        if not zal.is_file():
            zal.write_bytes(cil.read_bytes())
            print("záloha: %s" % zal.name)

    schema2 = zmen(schema, SCHEMA_STARY, SCHEMA_NOVY, "schema: sloupec")
    schema2 = zmen(schema2, SCHEMA_MIGRACE_STARY, SCHEMA_MIGRACE_NOVY,
                   "schema: komentář s migrací")

    index2 = zmen(index, TYP_STARY, TYP_NOVY, "index: typ řádku rfail")
    index2 = zmen(index2, MIGRACE_STARY, MIGRACE_NOVY, "index: self-migrace sloupce")
    index2 = zmen(index2, SELECT_STARY, SELECT_NOVY, "index: SELECT rfail")
    index2 = zmen(index2, GUARD_STARY, GUARD_NOVY, "index: cooldown guard (roadmapTick)")
    index2 = zmen(index2, GUARD2_STARY, GUARD2_NOVY, "index: cooldown guard (dispatch)")
    index2 = zmen(index2, KOMENT_GUARD_STARY, KOMENT_GUARD_NOVY, "index: komentář guardu")
    index2 = zmen(index2, FAIL1_STARY, FAIL1_NOVY, "index: zápis selhání (pollRuns)")
    index2 = zmen(index2, FAIL2_STARY, FAIL2_NOVY, "index: zápis selhání (/report)")

    SCHEMA.write_bytes(schema2.encode("utf-8"))
    INDEX.write_bytes(index2.encode("utf-8"))

    # OVĚŘ Z DISKU, že změny jsou skutečně tam
    s5 = SCHEMA.read_text(encoding="utf-8")
    i5 = INDEX.read_text(encoding="utf-8")
    assert s5 == schema2 and i5 == index2, "zapsaný obsah nesedí"
    for kontr, kde in ((s5, "schema"), (i5, "index")):
        if "naposledy_selhalo" not in kontr:
            print("CHYBA: %s — naposledy_selhalo se nezapsalo" % kde)
            return 2
    if "r.rfail || r.tupd" not in i5:
        print("CHYBA: guard nečte rfail")
        return 2
    if "rm.naposledy_selhalo > datetime" not in i5:
        print("CHYBA: dispatch guard nečte naposledy_selhalo")
        return 2
    if i5.count("naposledy_selhalo = datetime('now')") != 3:
        print("CHYBA: zápisů selhání je %d, očekávám 3 (pollRuns, /report, /report-else)"
              % i5.count("naposledy_selhalo = datetime('now')"))
        return 2
    if "rm.updated_at > datetime('now', ?)" in i5:
        print("CHYBA: v dispatch guardu zůstalo `rm.updated_at` — vada S12 by zůstala")
        return 2

    print("OK: schema.sql  %d → %d znaků" % (len(schema), len(s5)))
    print("OK: index.ts    %d → %d znaků" % (len(index), len(i5)))
    print("   sha256 schema: %s" % hashlib.sha256(s5.encode("utf-8")).hexdigest()[:16])
    print("   sha256 index:  %s" % hashlib.sha256(i5.encode("utf-8")).hexdigest()[:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
