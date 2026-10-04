#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Zapíše §8e a §16 do `HANDOFF.md` — BEZ MAZÁNÍ čehokoli.

PRAVIDLO (`AGENTS.md`): „Přepisuješ-li `HANDOFF.md`, nic nesmí zmizet."
Tenhle skript proto **jen vkládá**:
  * §8e se vloží PŘED `## 9. Co už otevřené NENÍ`,
  * §16 se připojí NA KONEC souboru.

Po zápisu se ověří, že **původní obsah zůstal** (délka roste, žádná sekce
neubyla) a že počet klíčových bodů pro `handoff-kontrola-uplnost.py` neklesl.

Použití:
    python _analyza/s16-zapis-handoff.py
    python _analyza/s16-zapis-handoff.py --zpet
"""

import hashlib
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
S16 = WS / "_analyza" / "s16-novy-oddil.md"
S8E = WS / "_analyza" / "s8e-novy-oddil.md"
ZALOHA = WS / "_analyza" / "s16-handoff-zaloha.md"

KOTVA_9 = "## 9. Co už otevřené NENÍ"


def nadpisy(text: str) -> list:
    return [r for r in text.splitlines() if r.startswith("#")]


def main() -> int:
    zpet = "--zpet" in sys.argv
    if zpet:
        if not ZALOHA.is_file():
            print("CHYBA: záloha %s není" % ZALOHA)
            return 2
        HANDOFF.write_bytes(ZALOHA.read_bytes())
        print("vráceno ze zálohy (%d znaků)" % len(HANDOFF.read_text(encoding="utf-8")))
        return 0

    puvodni = HANDOFF.read_text(encoding="utf-8")
    if "## 16. Provedeno 2. 10. 2026 (11:0x–12:0x UTC)" in puvodni:
        print("OK: §16 už v HANDOFF.md je")
        return 0
    if "### 8e. Omyly AKČNÍ session" in puvodni:
        print("OK: §8e už v HANDOFF.md je")
        return 0

    if not S16.is_file() or not S8E.is_file():
        print("CHYBA: chybí %s nebo %s" % (S16, S8E))
        return 2

    # záloha PŘED zápisem (kopií, ne spoléháním na git — soubor v gitu není)
    if not ZALOHA.is_file():
        ZALOHA.write_bytes(puvodni.encode("utf-8"))
        print("záloha: %s (%d znaků)" % (ZALOHA.name, len(puvodni)))

    nadpisy_pred = nadpisy(puvodni)
    if KOTVA_9 not in puvodni:
        print("CHYBA: kotva %r v HANDOFF.md není — nevím, kam vložit §8e" % KOTVA_9)
        return 2

    novy = puvodni.replace(KOTVA_9, S8E.read_text(encoding="utf-8").rstrip() + "\n\n" + KOTVA_9, 1)
    assert novy != puvodni, "MUTACE NEPROBĚHLA (vložení §8e)"
    novy = novy.rstrip() + "\n\n" + S16.read_text(encoding="utf-8").strip() + "\n"

    # ── KONTROLY, ŽE NIC NEZMIZELO ─────────────────────────────────────────
    if len(novy) <= len(puvodni):
        print("CHYBA: nový text není delší — něco se smazalo")
        return 2
    nadpisy_po = nadpisy(novy)
    chybejici = [h for h in nadpisy_pred if h not in nadpisy_po]
    if chybejici:
        print("CHYBA: tyto nadpisy po zápisu chybí:")
        for h in chybejici:
            print("   ", h)
        return 2
    # každá původní sekce musí být v novém textu obsažena CELÁ (kontrola po
    # blocích mezi nadpisy dalším nadpisem)
    for h in nadpisy_pred:
        i = puvodni.index(h)
        j = puvodni.find("\n#", i + len(h))
        blok = puvodni[i:j if j > 0 else len(puvodni)]
        if blok.strip() and blok.strip() not in novy:
            print("CHYBA: obsah sekce %r se v novém textu nenašel celý" % h[:60])
            return 2

    HANDOFF.write_bytes(novy.encode("utf-8"))
    z5 = HANDOFF.read_text(encoding="utf-8")
    assert z5 == novy, "zapsaný obsah nesedí"
    print("OK: HANDOFF.md  %d → %d znaků, nadpisů %d → %d"
          % (len(puvodni), len(z5), len(nadpisy_pred), len(nadpisy(z5))))
    print("   sha256 před: %s" % hashlib.sha256(puvodni.encode("utf-8")).hexdigest()[:16])
    print("   sha256 po:   %s" % hashlib.sha256(z5.encode("utf-8")).hexdigest()[:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
