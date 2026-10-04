# -*- coding: utf-8 -*-
r"""Doplní nález **H13** do tabulky §18.11 v `HANDOFF.md`.

PROČ: `kronika-kontrola.py` má pravidlo, že **každý nález z kroniky §2 musí být
zmíněný v `HANDOFF.md`** (odkud vzešel). H13 jsem zapsal jen do kroniky →
kontrola správně spadla: *„nález H13 je v kronice, ale v HANDOFF.md není"*.
**To je brána, která funguje** — kdyby mlčela, nález by žil jen na jednom místě.

Použití:  python _analyza\s19d-dopln-h13.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
ZAPIS = "--zapis" in sys.argv

H13 = (WS / "_analyza" / "s19c-h13.md").read_text(encoding="utf-8").strip()
assert H13.startswith("| **H13** |"), "H13 nemá správný tvar"
assert H13.count("\n") == 0, "H13 musí být JEDEN řádek tabulky"
# V HANDOFFu má tabulka §18.11 jiné sloupce než v kronice: # | Nález | Naměřeno | Proč to je nález
H13_HANDOFF = H13.replace(
    "| **otevřeno** — číslo v repu je **zastaralé měření** (táž třída jako N1) | akční session (§18.17) |",
    "| `providers.json` u Groqu: *„jeden běh spálí ~6k“* vs. **naměřeno ~14,4 tisíce** — 2,4× víc | **Číslo v repu je zastaralé měření**, ne lež (táž třída jako **N1**). Kdo se podle něj rozhoduje, rozhoduje se o jiném systému — a odhad „~33 běhů/den“ je nadsazený |")

text = HANDOFF.read_text(encoding="utf-8")
KOTVA = "| **H12** |"
pocet = text.count(KOTVA)
print("HANDOFF.md: kotva H12 → %dx (očekáváno 1)" % pocet)
assert pocet == 1, "kotva H12 není právě 1×"
assert "| **H13** |" not in text, "H13 už v souboru je"

i = text.find(KOTVA)
konec = text.find("\n", i)
assert konec > i, "řádek H12 nemá konec"
novy = text[:konec + 1] + H13_HANDOFF + "\n" + text[konec + 1:]
assert novy.count("| **H13** |") == 1, "H13 není právě 1×"
assert novy.count(KOTVA) == 1, "H12 se ztratil nebo zdvojil"
assert novy.startswith(text[:8192]), "PŘEDCHOZÍ OBSAH SE ZMĚNIL"

print("  H13 se vloží za H12 do tabulky §18.11")
print("  `%s`" % H13_HANDOFF[:100])

if ZAPIS:
    HANDOFF.write_bytes(novy.encode("utf-8"))
    print()
    print("  ZAPSÁNO: %d -> %d B"
          % (len(text.encode("utf-8")), len(novy.encode("utf-8"))))
else:
    print()
    print("  (dry-run — spusť s --zapis)")
