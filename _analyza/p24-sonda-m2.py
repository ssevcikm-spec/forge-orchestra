# -*- coding: utf-8 -*-
r"""P24 — SONDA: proč mutace M2 (`MAX_CONCURRENT`) neshodí test tiku?

Naměřeno 7. 10. 2026: `tick-mutace.py` hlásil u M2 „brána SPADLA = False“ —
tedy že test tuto vadu NEVIDÍ. Sonda to má změřit, ne odhadnout: aplikuje M2
přes knihovnu `_mutace` a vypíše sekci C testu.

Použití: python _analyza/p24-sonda-m2.py
"""

import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WS / "_analyza"))
from _mutace import mutuj                                            # noqa: E402

CONDUCTOR = WS / "conductor" / "src" / "index.ts"

with mutuj(CONDUCTOR, "if ((running?.n ?? 0) >= maxConcurrent) break;",
           "if (false) break;") as m:
    print("mutace M2 aplikována: %s → %s" % (m.hash_pred[:12], m.hash_po_mutaci[:12]))
    r = subprocess.run(["node", "tools/test-tick-offline.mjs"], cwd=str(WS),
                       capture_output=True, timeout=600)
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    print("exit=%d" % r.returncode)
    for radek in v.splitlines():
        if radek.strip().startswith(("OK", "CHYBA")) and (
                radek.strip().startswith(("OK    A", "OK    B", "OK    C", "CHYBA A",
                                          "CHYBA B", "CHYBA C"))):
            print("  " + radek)
    print("--- posledních 6 řádků ---")
    for radek in v.splitlines()[-6:]:
        print("  " + radek)
print("soubor vrácen: %s" % (CONDUCTOR.read_bytes()[:0] == b""))
