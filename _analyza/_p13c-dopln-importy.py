# -*- coding: utf-8 -*-
r"""P13c-b: opraví `join()`/`dirname()`/… volaná BEZ IMPORTU (nález H68).

CO SE NAMĚŘILO (plošný sken, ne dohad):
  V orchestra je **~50 souborů**, které volají `join(...)`, ale **nemají ho
  importovaný**. Modul proto spadne hned na prvním volání:

      ReferenceError: join is not defined

  Přesně to potkalo `tools/validate-all.mjs` (nález **H57**) a
  `tools/test-ci-workflow.mjs` (dvojče) — **obě brány spadly PŘED první
  kontrolou** a v přehledu to vypadalo jako „brána našla vadu".

  Vzniklo to zřejmě hromadnou opravou cest (P8) — přidalo se `join(...)`,
  ale import ne.

⚠ DVĚ PASTI, KTERÉ SKRIPT ZAVÍRÁ:
  1. **Falešný poplach na lokální definici.** První verze skenu hlásila 57
     souborů; většina si `function join(...)` **definuje sama**. Kdo to
     neodliší, „opravuje" správný kód (`overovani` §9.5).
  2. **Zápis musí projít parserem.** Po každé úpravě se soubor zkontroluje
     `node --check` (u `.ts` se přeskočí) — jinak by z „opravy" vznikla
     syntaktická vada, kterou u `.mjs` pozná až běh.

Použití: python _analyza\p13c-dopln-importy.py [--zapis]
Bez `--zapis` jen VYPÍŠE, co by udělal (dry-run).
"""

import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HRA = WS.parent / "uo-shadows"
GIT = WS / "tools" / "git.cmd"
ZAPIS = "--zapis" in sys.argv

FUNKCE = ("join", "dirname", "basename", "extname")
SUFFIXY = (".mjs", ".js", ".cjs", ".mts", ".cts", ".ts")


def volani(text: str, funkce: str) -> bool:
    """Holé volání `funkce(` — NE metoda `x.join(`.

    ⚠ PŘEDPONA `.` ROZHODUJE: `arr.join(',')` je metoda pole, ne volání volné
    funkce. První verze skenu to nerozlišovala a hlásila **57 souborů**, z toho
    většinu falešně (`conductor/src/index.ts` má 9× `Array.join` a `join()`
    z `node:path` nikdy nevolá). Falešný poplach nutí „opravovat" správný kód
    (`overovani` §9.5) — a hůř: přidal by import, který soubor nepotřebuje.
    """
    import re as _re
    return _re.search(rf"(?<![\w.$?]){funkce}\s*\(", text) is not None


def ma_import(text: str, funkce: str) -> bool:
    if re.search(rf"import\s*\{{[^}}]*\b{funkce}\b[^}}]*\}}", text):
        return True
    if re.search(rf"(?:const|let|var)\s*\{{[^}}]*\b{funkce}\b", text):
        return True
    if re.search(rf"(?:function|const|let|var)\s+{funkce}\b", text):
        return True
    return False


def dopln_import(text: str, chybejici: list[str]) -> str | None:
    """Doplní chybějící jména do existujícího importu z `node:path`."""
    m = re.search(r"import\s*\{([^}]*)\}\s*from\s*['\"]node:path['\"]", text)
    if not m:
        return None
    jmena = [x.strip() for x in m.group(1).split(",") if x.strip()]
    nova = jmena + [f for f in chybejici if f not in jmena]
    novy_import = "import { " + ", ".join(nova) + " } from 'node:path'"
    return text[:m.start()] + novy_import + text[m.end():]


def soubory():
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
            yield popis, koren, f, p


def main() -> int:
    opraveno, preskoceno, selhalo = [], [], []
    for popis, koren, f, p in soubory():
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        chybejici = [fn for fn in FUNKCE
                     if volani(text, fn) and not ma_import(text, fn)]
        if not chybejici:
            continue
        novy = dopln_import(text, chybejici)
        if novy is None:
            preskoceno.append((popis, f, chybejici, "není `import ... from 'node:path'`"))
            continue
        if novy == text:
            preskoceno.append((popis, f, chybejici, "náhrada nic nezměnila"))
            continue
        if not ZAPIS:
            print(f"  [dry-run] {popis}/{f}: doplnit {chybejici}")
            opraveno.append((popis, f, chybejici))
            continue
        p.write_text(novy, encoding="utf-8", newline="")
        zpet = p.read_text(encoding="utf-8")
        assert all(ma_import(zpet, fn) for fn in chybejici), f"{f}: import se nezapsal"
        # Syntaktická kontrola (u `.ts` ji `node --check` neumí).
        if p.suffix.lower() != ".ts":
            r = subprocess.run(["node", "--check", str(p)], capture_output=True)
            if r.returncode != 0:
                p.write_text(text, encoding="utf-8", newline="")
                selhalo.append((f, r.stderr.decode("utf-8", "replace")[:200]))
                continue
        opraveno.append((popis, f, chybejici))

    for popis, f, chybejici in opraveno:
        print(f"  {'OPRAVENO' if ZAPIS else 'K DOPLNĚNÍ'} {popis}/{f}: {chybejici}")
    for popis, f, chybejici, proc in preskoceno:
        print(f"  ? {popis}/{f}: {chybejici} — {proc}")
    for f, chyba in selhalo:
        print(f"  CHYBA {f}: po úpravě neprošel parserem, VRÁCENO:\n     {chyba}")

    print()
    print(f"VÝSLEDEK ({'zápis' if ZAPIS else 'dry-run'}): "
          f"{len(opraveno)} k doplnění, {len(preskoceno)} přeskočeno, {len(selhalo)} vráceno")
    return 1 if selhalo else 0


if __name__ == "__main__":
    sys.exit(main())
