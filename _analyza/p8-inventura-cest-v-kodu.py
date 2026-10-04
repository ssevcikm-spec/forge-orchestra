"""P8 — INVENTURA KONKRETNICH CEST V KODU (co presne se v obou repech odkazuje).

PROC: nahrazovat naslepo je hazard — v kazdem souboru muze byt cesta v jinem
tvaru (raw string, lomitka, JS literál) a nahrada muze rozbit syntaxi.
Nejdriv se zmeri, CO tam je, pak se navrhne nahrada.

Vystup: pro kazdou unikatni cestu pocet vyskytu + soubory.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CIL = [Path(r"E:\Workspaces\forge-orchestra"), Path(r"E:\Workspaces\uo-shadows")]
KOD_SUFFIX = {".py", ".mjs", ".js", ".ts", ".ps1", ".cmd", ".gd", ".sql"}

# cesta zacinajici na Local-Deepseek, vcetne vsech oddelovacu
VZOR = re.compile(
    r"""(?P<q>['"]|r['"])?"""
    r"""(?P<cesta>[A-Za-z]:[\\/]Users[\\/]Ssevc[\\/]Local-Deepseek"""
    r"""(?:[\\/][A-Za-z0-9_.\-]+)*)""",
)


def main() -> int:
    podle_cesty: dict[str, list[str]] = defaultdict(list)
    for zaklad in CIL:
        for p in sorted(zaklad.rglob("*")):
            if any(d in p.parts for d in (".git", "node_modules", ".godot",
                                          "__pycache__", ".wrangler")):
                continue
            if not p.is_file() or p.suffix.lower() not in KOD_SUFFIX:
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for m in VZOR.finditer(text):
                cesta = m.group("cesta")
                podle_cesty[cesta].append(str(p.relative_to(zaklad)))

    print(f"unikatnich cest: {len(podle_cesty)}")
    print(f"vyskytu celkem:  {sum(len(v) for v in podle_cesty.values())}")
    print()
    # normalizuj na lomitka pro seskupeni
    seskup: dict[str, list[str]] = defaultdict(list)
    for c, kde in podle_cesty.items():
        klic = c.replace("\\", "/")
        seskup[klic].extend(kde)
    print(f"po normalizaci oddelovacu: {len(seskup)}")
    print()
    for klic in sorted(seskup):
        kde = seskup[klic]
        print(f"{klic}")
        print(f"    {len(kde)}x, souboru: {len(set(kde))}")
        for s in sorted(set(kde))[:6]:
            print(f"        {s}")
        if len(set(kde)) > 6:
            print(f"        … +{len(set(kde)) - 6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
