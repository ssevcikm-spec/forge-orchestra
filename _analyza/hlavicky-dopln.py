# -*- coding: utf-8 -*-
r"""OPATŘENÍ 7 — doplní hlavičku „Co tenhle dokument JE" živým dokumentům.

PROČ: `_analyza\audit1-inventar.py` naměřil **80 z 111** dokumentů bez hlavičky
a zadání `ZADANI-OPRAVA-MERIDEL.md` (Úkol 5a) žádá **≤ 20** — u **živých**
dokumentů v kořeni a v `_analyza`.

CO SE NEDOPLŇUJE (a proč):
  * **zálohy a pracovní kopie** (`_zaloha-*`, `*-pred-*`, `handoff-pred-*`,
    `_analyza\patch*`, `_analyza\*zaloha*`) — ty se mají poznat **jako zálohy**
    (nález **NA21**), ne tvářit se jako dokument;
  * **skilly** (`SKILL.md`) — u těch se hlavička nevyžaduje (`neni-clanek`);
  * **`_analyza` pracovní úryvky** (`_s25-*`, `_tmp-*`) — to jsou výstupy sond.

CO SE ZAPISUJE: přesně tvar, který hledá `HLAVICKA_VZORY` v inventáři
(`Co tenhle dokument JE`) + **druh** klíčovým slovem (`DEKLARACE`), aby
inventář nemusel hádat. Vkládá se **za první nadpis `# …`**, ne na začátek —
dokument musí pořád začínat svým názvem.

⚠ BEZPEČNOST: každý soubor se **zálohuje kopií do `_analyza\_hlavicky-zaloha\`**
(kořen workspace **není v gitu** — viz `AGENTS.md`), zapisuje se **bajty**
a po zápisu se ověří, že vzor v souboru **skutečně je**.

Použití:  $env:PYTHONIOENCODING='utf-8'; python _analyza\hlavicky-dopln.py [--zapsat]
          (bez `--zapsat` jen VYPÍŠE, co by udělal — suchý běh)
"""

import json
import pathlib
import re
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
INVENTAR = WS / "_analyza" / "audit-inventar.json"
ZALOHA = WS / "_analyza" / "_hlavicky-zaloha"
ZAPSAT = "--zapsat" in sys.argv

VZORY = [r"Co tenhle dokument JE", r"Co je tenhle soubor", r"Co tenhle soubor je",
         r"Co tenhle dokument je"]

# Co je dokument ZA (klíčové slovo pro `DEKLARACE` v inventáři).
# Bere se z NÁZVU souboru — je to odhad a v hlavičce se vypíše, takže se dá
# opravit; kdyby se to nechalo na „jiné", inventář by druh neurčil.
def druh_z_nazvu(jmeno: str) -> str:
    j = jmeno.upper()
    if j.startswith("ZADANI") or "ZADANI" in j:
        return "zadání"
    if j.startswith("PLAN") or j.startswith("PLAN-"):
        return "plán"
    if j.startswith("ANALYZA"):
        return "analýza"
    if j.startswith("IMPLEMENTACE"):
        return "záznam o provedení"
    if j.startswith("KRONIKA"):
        return "kronika"
    if j.startswith("HANDOFF"):
        return "stav"
    if "MERENI" in j or "SOUBEH" in j or "NALEZY" in j:
        return "záznam o provedení"
    if j.startswith("PROMPT"):
        return "postup"
    if "REJSTRIK" in j or "ROZCESTNIK" in j or "MOZNOSTI" in j:
        return "rejstřík"
    return "záznam o provedení"


def je_zaloha(cesta: pathlib.Path) -> bool:
    n = cesta.name.lower()
    return (n.startswith("_zaloha") or n.startswith("_tmp") or n.startswith("_s")
            or "-pred-" in n or n.startswith("handoff-pred")
            or "zaloha" in str(cesta.parent).lower()
            or "patch" in str(cesta.parent).lower())


def ma_hlavicku(text: str) -> bool:
    return any(re.search(v, text[:4000]) for v in VZORY)


def vloz_hlavicku(text: str, jmeno: str) -> str:
    druh = druh_z_nazvu(jmeno)
    blok = (
        "\n> **Co tenhle dokument JE:** %s. Hlavičku „Co tenhle dokument JE“\n"
        "> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání\n"
        "> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se\n"
        "> jeho druh hádat z názvu (nález **NA21**).\n" % druh
    )
    radky = text.splitlines(keepends=True)
    for i, l in enumerate(radky):
        if l.startswith("# "):
            return "".join(radky[:i + 1]) + blok + "".join(radky[i + 1:])
    return blok + text


def main() -> int:
    if not INVENTAR.is_file():
        print("CHYBA: %s není — spusť `python _analyza\\audit1-inventar.py`" % INVENTAR)
        return 1
    d = json.loads(INVENTAR.read_text(encoding="utf-8"))

    kandidati, preskoceno = [], []
    for z in d["dokumenty"]:
        cesta = WS / z["cesta"]
        if not cesta.is_file():
            continue
        if str(z.get("hlavicka", "")).startswith("ANO"):
            continue
        if je_zaloha(cesta):
            preskoceno.append((z["cesta"], "záloha / pracovní kopie"))
            continue
        if cesta.name == "SKILL.md":
            preskoceno.append((z["cesta"], "skill — hlavička se nevyžaduje"))
            continue
        kandidati.append(cesta)

    print("=" * 96)
    print("  DOPLNĚNÍ HLAVIČKY „Co tenhle dokument JE“ %s"
          % ("(ZÁPIS)" if ZAPSAT else "(SUCHÝ BĚH — nic se nezapisuje)"))
    print("=" * 96)
    print("  dokumentů bez hlavičky v inventáři: %d"
          % len([z for z in d["dokumenty"]
                 if str(z.get("hlavicka", "")).startswith("NE")]))
    print("  kandidátů k doplnění:               %d" % len(kandidati))
    print("  přeskočeno (zálohy/skilly):         %d" % len(preskoceno))
    print()

    zapsano, chyby = 0, []
    if ZAPSAT:
        ZALOHA.mkdir(parents=True, exist_ok=True)
    for cesta in kandidati:
        orig = cesta.read_bytes()
        text = orig.decode("utf-8")
        if ma_hlavicku(text):
            continue
        novy = vloz_hlavicku(text, cesta.name)
        if novy == text:
            chyby.append("%s: text se nezměnil" % cesta.name)
            continue
        print("  %-58s → %s" % (z["cesta"] if False else
                                str(cesta.relative_to(WS))[:58],
                                druh_z_nazvu(cesta.name)))
        if not ZAPSAT:
            continue
        # ⚠ ZÁLOHA KOPIÍ — kořen workspace NENÍ v gitu, `git checkout` není cesta zpět.
        shutil.copyfile(cesta, ZALOHA / cesta.name)
        cesta.write_bytes(novy.encode("utf-8"))
        over = cesta.read_text(encoding="utf-8")
        if not ma_hlavicku(over):
            chyby.append("%s: hlavička se do souboru NEDOSTALA" % cesta.name)
        else:
            zapsano += 1

    print()
    print("=" * 96)
    if ZAPSAT:
        print("  ZAPSÁNO: %d souborů · zálohy v %s"
              % (zapsano, ZALOHA.relative_to(WS)))
    if chyby:
        for c in chyby:
            print("  CHYBA: %s" % c)
        return 1
    if ZAPSAT:
        print("  Ověř: python _analyza\\audit1-inventar.py "
              "(hledej `bez hlavičky`)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
