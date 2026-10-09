# -*- coding: utf-8 -*-
r"""P29/B6 — MUTAČNÍ DŮKAZ OPRAVY: VRÁTÍ VADU A OVĚŘÍ, ŽE JEJÍ TESTY SPADNOU.

CO TO JE: důkaz, že nové kontroly `AE*` v `tools/test-tick-offline.mjs` nejsou
zelené nad ničím. Vrací se TŘI věci, každá zvlášť:

  * **M1** — uklizení osiřelých řádků cache (`DELETE FROM roadmap`) se vypne;
  * **M2** — pojmenování přeskočené granule na stropu (`STROP GRANULE`) se vypne;
  * **M3** — pojmenování úloh v cooldownu (`v cooldownu`) se vypne.

Každá mutace má DVĚ nohy: (a) zdravý strom → 0 chyb, (b) mutant → SPADNE
na kontrole, která tu věc měří. Mutace jde přes `_analyza/_mutace.py`, takže
se soubor VŽDY vrátí bajt na bajt a hash se ověří.

Použití: python _analyza\p29-b6-mutace.py
"""

import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
SRC = WS / "conductor" / "src" / "index.ts"
TEST = WS / "tools" / "test-tick-offline.mjs"
sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj  # noqa: E402

kontrol = 0
chyb = 0


def check(popis, zjisteno, ocekavano):
    global kontrol, chyb
    kontrol += 1
    if zjisteno == ocekavano:
        print("  OK    %s" % popis)
        return True
    chyb += 1
    print("  CHYBA %s\n        čekáno:   %r\n        naměřeno: %r"
          % (popis, ocekavano, zjisteno))
    return False


def tick_test():
    r = subprocess.run(["node", str(TEST)], cwd=str(WS), capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=1800)
    v = (r.stdout or "") + (r.stderr or "")
    cervene = [l.strip()[5:].strip() for l in v.splitlines()
               if l.strip().startswith("CHYBA")]
    return r.returncode, v, cervene


def zivy():
    kod, v, cervene = tick_test()
    check("KONTROLA: zdravý strom → test tiku projde (exit 0)", kod, 0)
    check("KONTROLA: a má víc kontrol než před opravou (>205)",
          int(v.split("VYSLEDEK:")[-1].split("kontrol")[0].strip()) > 205, True)
    return cervene


def mutace(popis, stary, novy, ocekavane):
    """Spustí mutaci a ověří, že SPADLY právě ty kontroly, které to měří."""
    print("\n--- %s ---" % popis)
    try:
        with mutuj(SRC, stary, novy) as m:
            check("%s: mutace se provedla (hash před != po)" % popis,
                  m.hash_pred != m.hash_po_mutaci, True)
            kod, v, cervene = tick_test()
        check("%s: mutant → test tiku SPADNE" % popis, kod != 0, True)
        for popis_kontroly in ocekavane:
            check("%s: spadla kontrola `%s`" % (popis, popis_kontroly),
                  any(popis_kontroly in c for c in cervene), True)
        check("%s: soubor je vrácen bajt na bajt" % popis,
              m.hash_po_navratu, m.hash_pred)
    except ValueError as e:
        check("%s: mutaci nešlo provést (%s)" % (popis, str(e)[:80]), True, False)


def main():
    print("=" * 88)
    print("P29/B6 — MUTAČNÍ DŮKAZ: tři vraty ve zdroji conductora, každá se dvěma nohami")
    print("=" * 88)
    zivy()

    # M1 — vypnout uklizení osiřelých řádků (tělo smyčky se nahradí `void`)
    mutace(
        "M1 (uklizení osiřelých řádků VYPNUTO)",
        """      const del = await env.DB.prepare("DELETE FROM roadmap WHERE item_id = ?")
        .bind(r.item_id).run().catch(() => undefined);
      smazanoOsirelych += del?.meta?.changes ?? 0;""",
        """      void r;  // P29/B6 mutace: uklizení VYPNUTO
      smazanoOsirelych += 0;""",
        ["AE: osiřelý řádek cache se SMAŽE", "AE: tik počet uklizených řádků VYPÍŠE"])

    # M2 — vypnout pojmenování stropu granule
    mutace(
        "M2 (pojmenování STROPU GRANULE VYPNUTO)",
        "        preskoceno.push(`#${t.id} STROP GRANULE `\n"
        "          + `${grainRunsMap?.get(grainKeyOf(t.payload) || \"\")}/${cap} `\n"
        "          + `(${grainKeyOf(t.payload)})`);",
        "        void cap;  // P29/B6 mutace: pojmenování stropu VYPNUTO",
        ["AE3: a tik strop POJMENUJE i s číslem"])

    # M3 — vypnout pojmenování cooldownu
    mutace(
        "M3 (pojmenování COOLDOWNU VYPNUTO)",
        "    if (ids.length) cooldownMsg = ` | v cooldownu ${ids.length} úloh: ${ids.join(\", \")}`;",
        "    void ids;  // P29/B6 mutace: pojmenování cooldownu VYPNUTO",
        ["AE4: tik vypíše, KOLIK úloh drží cooldown a které"])

    print("\n" + "=" * 88)
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    print("=" * 88)
    return 0 if chyb == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
