# -*- coding: utf-8 -*-
r"""P13c-b: najdi `.mjs`/`.js`/`.ts` soubory, které VOLAJÍ `join(...)`, ale NEIMPORTUJÍ ho.

PROČ TO EXISTUJE (nález **H57** a jeho **dvojče H68**):
  `tools/validate-all.mjs` spadl na `ReferenceError: join is not defined`
  (volal `join()`, ale v importu z `node:path` měl jen `dirname`). Totéž
  v `tools/test-ci-workflow.mjs` — a plošný sken pak našel **31 souborů**
  v orchestra se stejnou vadou.

  Všechny spadnou **PŘED první kontrolou**, takže se to čte jako „brána našla
  vadu" — a to je táž třída jako nález **H48** (brána, která vůbec neběžela,
  `overovani` §7.13). Rozdíl je jen v tom, že tady je příčina ve ZDROJÁKU.

⚠ DVĚ PASTI, KTERÉ SKEN ZAVÍRÁ (obě naměřené na sobě):

  1. **Metoda vs. volání.** `arr.join(',')` je metoda pole, ne volání volné
     funkce. První verze hledala `\\bjoin\\s*\\(` a hlásila **57 souborů**,
     z toho většinu falešně (`conductor/src/index.ts` má 9× `Array.join`,
     ale `join()` z `node:path` **nikdy nevolá**). Falešný poplach nutí
     „opravovat" správný kód (`overovani` §9.5).
  2. **`resolve` je dvojznačné.** `new Promise((resolve) => …)` je úplně jiné
     `resolve` než `path.resolve`. Sken ho proto **vůbec nehlídá** — radši
     přiznaná mez než falešný poplach.

Použití: python _analyza/hl-chybejici-importy.py
Návrat:  0 = každé volání má import | 1 = nález (vypíše soubor a funkci)
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
GIT = WS / "tools" / "git.cmd"
HRA = WS.parent / "uo-shadows"

# Jen jména, u kterých je „volání bez importu" JEDNOZNAČNĚ vada.
POTREBNE = {
    "join": "node:path",
    "dirname": "node:path",
    "basename": "node:path",
    "extname": "node:path",
    "fileURLToPath": "node:url",
}
SUFFIXY = (".mjs", ".js", ".cjs", ".mts", ".cts", ".ts")


def volani(text: str, funkce: str) -> bool:
    """Holé volání `funkce(` — NE metoda `x.join(` (předpona `.`/`?.`)."""
    return re.search(rf"(?<![\w.$?]){funkce}\s*\(", text) is not None


def ma_import(text: str, funkce: str) -> bool:
    if re.search(rf"import\s*\{{[^}}]*\b{funkce}\b[^}}]*\}}", text):
        return True
    if re.search(rf"(?:const|let|var)\s*\{{[^}}]*\b{funkce}\b", text):
        return True
    if re.search(rf"(?:function|const|let|var)\s+{funkce}\b", text):
        return True
    return False


def main() -> int:
    nalezy = []
    zkontrolovano = 0
    for koren, popis in ((WS, "orchestra"), (HRA, "hra")):
        if not koren.is_dir():
            continue
        r = subprocess.run([str(GIT), "-C", str(koren), "ls-files"],
                           capture_output=True, shell=True)
        for f in (r.stdout or b"").decode("utf-8", "replace").splitlines():
            p = koren / f
            if not p.is_file() or p.suffix.lower() not in SUFFIXY:
                continue
            if any(x in f for x in ("node_modules/", "_archiv/", "_scratch")):
                continue
            try:
                t = p.read_text(encoding="utf-8", errors="replace")
            except Exception:                                  # noqa: BLE001
                continue
            zkontrolovano += 1
            for funkce, modul in POTREBNE.items():
                if volani(t, funkce) and not ma_import(t, funkce):
                    nalezy.append((popis, f, funkce, modul))

    if not nalezy:
        print("OK: každé volání `join`/`dirname`/… má v souboru svůj import.")
        print(f"ZMĚŘENO: {zkontrolovano} souborů, 0 chybějících importů")
        return 0

    print("NÁLEZ: volání bez importu — modul spadne PŘED první kontrolou:")
    for popis, f, funkce, modul in nalezy:
        print(f"  [{popis}] {f}: `{funkce}()` chybí import z `{modul}`")
    print()
    print(f"ZMĚŘENO: {zkontrolovano} souborů, {len(nalezy)} chybějících importů")
    print("Náprava: python _analyza\\p13c-dopln-importy.py --zapis")
    return 1


if __name__ == "__main__":
    sys.exit(main())
