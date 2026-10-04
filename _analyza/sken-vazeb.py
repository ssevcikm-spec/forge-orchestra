# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sken vazeb orchestra a hry na okoli workspace.

Read-only. Hleda:
  1) absolutni cesty na Local-Deepseek
  2) vylez o uroven vys (..\..\), odkazy na sourozenecke slozky
  3) zminky o okolnich projektech (ollama, litellm, router, dsh-consolidation...)
  4) pocet souboru a radku, aby bylo videt, jaka cast byla prohledana

NEPOUZIVA Select-String (tise preskakuje) ani grep tool (tise preskakuje
skryte slozky) - chodi po filesystemu sam a cte bajty.
"""
import os
import re
import sys
from collections import Counter, defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = _STANICE
CIL = {
    "orchestra": os.path.join(ROOT, "orchestra"),
    "hra": os.path.join(ROOT, "games", "uo-shadows"),
}

# co neprohledavat (cizi kod / binarky)
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".godot", "venv", ".venv",
    "dist", "build", ".wrangler", ".npm-cache", ".mypy_cache",
}
SKIP_EXT = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".svg", ".ttf", ".otf",
    ".woff", ".woff2", ".zip", ".gz", ".7z", ".exe", ".dll", ".so", ".dylib",
    ".pdf", ".mp3", ".ogg", ".wav", ".import", ".pyc", ".bin", ".wasm",
    ".patch", ".log", ".pdb", ".lib", ".obj", ".a", ".node", ".map",
}
TEXT_EXT = {
    ".py", ".mjs", ".js", ".cjs", ".ts", ".json", ".yml", ".yaml", ".toml",
    ".md", ".ps1", ".cmd", ".bat", ".sh", ".gd", ".tscn", ".godot", ".cfg",
    ".txt", ".env", ".gitignore", ".sql", ".html", ".css", ".svg",
}

VZORY = [
    ("ABS_CESTA", re.compile(r"[Cc]:[\\/]+Users[\\/]+Ssevc[\\/]+Local-Deepseek[\\/]+([A-Za-z0-9_.\-]+)")),
    ("ABS_CESTA_LOOSE", re.compile(r"Local-Deepseek")),
    ("VYLEZ_2", re.compile(r"\.\.[\\/]\.\.[\\/]")),
    ("VYLEZ_3", re.compile(r"\.\.[\\/]\.\.[\\/]\.\.[\\/]")),
    ("SOUSED", re.compile(r"\b(ollama|litellm|dsh-consolidation|dsh-usage-visual|_retired|_analyza|session-handoff|obrazky|research|wrangler)\b", re.I)),
    ("GAMES_REL", re.compile(r"(^|[\\/\"'\s])games[\\/]", re.I)),
]


def zjisti_okoli(cesta):
    """Vrati (koren, zdroj_okolí) - prvni slozka pod ROOT."""
    rel = os.path.relpath(cesta, ROOT)
    if rel.startswith(".."):
        return None
    return rel.split(os.sep)[0]


def skenuj(nazev, zaklad):
    nalezy = defaultdict(list)
    dokumenty = {}   # soubor -> okoli
    pocet_souboru = 0
    pocet_vyloucenych = 0
    celkem_radku = 0
    podle_okoli = Counter()

    for dirpath, dirnames, filenames in os.walk(zaklad):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            cesta = os.path.join(dirpath, fn)
            ext = os.path.splitext(fn)[1].lower()
            if ext in SKIP_EXT:
                pocet_vyloucenych += 1
                continue
            # ber i soubory bez pripony, pokud jsou textove podle nazvu
            if ext and ext not in TEXT_EXT and fn not in ("Dockerfile", "Makefile"):
                if ext not in (".jsonl", ".mjs", ".py"):
                    pocet_vyloucenych += 1
                    continue
            try:
                with open(cesta, "rb") as f:
                    raw = f.read()
            except OSError:
                pocet_vyloucenych += 1
                continue
            if b"\x00" in raw[:4096]:
                pocet_vyloucenych += 1
                continue
            pocet_souboru += 1
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("cp1252", errors="replace")
            radky = text.splitlines()
            celkem_radku += len(radky)
            okoli = zjisti_okoli(cesta)
            dokumenty[cesta] = okoli
            for i, radek in enumerate(radky, 1):
                for jmeno, rx in VZORY:
                    m = rx.search(radek)
                    if m:
                        nalezy[jmeno].append((cesta, i, radek.strip()[:190]))
                        if jmeno == "ABS_CESTA" and m.group(1):
                            podle_okoli[m.group(1)] += 1
    return {
        "nalezy": nalezy,
        "dokumenty": dokumenty,
        "pocet_souboru": pocet_souboru,
        "pocet_vyloucenych": pocet_vyloucenych,
        "celkem_radku": celkem_radku,
        "podle_okoli": podle_okoli,
    }


def main():
    print("=" * 78)
    print("SKEN VAZEB: orchestra a hra -> okoli workspace")
    print("=" * 78)

    vsechny_okoli = Counter()
    for nazev, zaklad in CIL.items():
        if not os.path.isdir(zaklad):
            print(f"\n!! {nazev}: {zaklad} NEEXISTUJE")
            continue
        print(f"\n{'#' * 78}\n# {nazev.upper()}  ({zaklad})\n{'#' * 78}")
        v = skenuj(nazev, zaklad)
        print(f"prohledano souboru: {v['pocet_souboru']}  ({v['celkem_radku']} radku), "
              f"preskoceno (binarky/cizi): {v['pocet_vyloucenych']}")

        # okoli, do ktereho soubory sahaji
        okoli = Counter(o for o in v["dokumenty"].values() if o)
        print(f"rozlozeni souboru podle okoli workspace: {dict(okoli.most_common(12))}")
        vsechny_okoli.update(okoli)

        for jmeno in ("ABS_CESTA", "ABS_CESTA_LOOSE", "VYLEZ_2", "VYLEZ_3", "SOUSED", "GAMES_REL"):
            n = v["nalezy"].get(jmeno, [])
            print(f"\n--- {jmeno}: {len(n)} vyskytu ---")
            if jmeno == "ABS_CESTA":
                print(f"    cilove slozky: {dict(v['podle_okoli'].most_common(20))}")
            for cesta, i, radek in n[:25]:
                rel = os.path.relpath(cesta, ROOT)
                print(f"    {rel}:{i}: {radek}")
            if len(n) > 25:
                print(f"    ... a dalsich {len(n) - 25}")

    print("\n" + "=" * 78)
    print("SOUHRN: rozlozeni prohledanych souboru podle okoli")
    print("=" * 78)
    for k, val in vsechny_okoli.most_common():
        print(f"  {val:6d}  {k}")


if __name__ == "__main__":
    main()
