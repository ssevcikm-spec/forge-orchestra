"""Změří konce řádků a BOM u originálů i u připravených záplat."""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CRLF = bytes([13, 10])
LF = bytes([10])
BOM = bytes([0xEF, 0xBB, 0xBF])

ROOTY = {
    "originál": pathlib.Path(r"C:\Users\Ssevc\.dsh\skills"),
    "záplata": pathlib.Path(r"_analyza\patch"),
}

for jmeno in ["game-developer", "dsh-prostredi"]:
    for popis, root in ROOTY.items():
        b = (root / jmeno / "SKILL.md").read_bytes()
        crlf = b.count(CRLF)
        lf = b.count(LF) - crlf
        print(
            f"{jmeno:16} {popis:9} CRLF={crlf:4}  LF-only={lf:4}  "
            f"BOM={b[:3] == BOM}  bajtů={len(b)}"
        )
