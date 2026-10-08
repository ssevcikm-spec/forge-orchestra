# -*- coding: utf-8 -*-
r"""P27 — výměna SHA v zadání (ASCII token → ASCII token, bezpečné pro kotvy).

Používá se po commitu: hlavička zadání musí tvrdit **živý** HEAD, a ten se
commitem posune. Nahrazuje se VŠUDE v `NEXT-SESSION-INSTRUKCE.md` (hlavička,
kotva, seznam commitů, stavový řádek) a ověřuje se počet výskytů.

Použití: python _analyza/p27-vymen-sha.py <stary_sha> <novy_sha>
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
Z = WS / "NEXT-SESSION-INSTRUKCE.md"

if len(sys.argv) < 3:
    print("použití: p27-vymen-sha.py <stary> <novy>")
    sys.exit(2)
stary, novy = sys.argv[1], sys.argv[2]

t = Z.read_text(encoding="utf-8")
n = t.count(stary)
print("  výskytů %s: %d" % (stary, n))
if n == 0:
    print("  (nic k výměně — zadání už živý sha má)")
    sys.exit(0 if novy in t else 1)
t2 = t.replace(stary, novy)
Z.write_bytes(t2.encode("utf-8"))
t3 = Z.read_text(encoding="utf-8")
print("  po výměně: %s=%d, %s=%d" % (stary, t3.count(stary), novy, t3.count(novy)))
print("  LF a bez BOM:", t3.count("\r\n") == 0 and not t3.startswith("\ufeff"))
sys.exit(0 if (t3.count(stary) == 0 and t3.count(novy) >= n) else 1)
