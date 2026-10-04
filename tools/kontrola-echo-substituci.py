#!/usr/bin/env python3
import pathlib as _pl

# P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni skriptu.
# `tools/` je primo v koreni repa, takze _PARENT = root repa.
_PARENT = _pl.Path(__file__).resolve().parents[1]
r"""Najde v `run:` blocích workflowů echo, které bash NEBEZPEČNĚ vyhodnotí.

PROČ TO EXISTUJE
----------------
Bash bere uvnitř dvojitých uvozovek **zpětný apostrof** i **`$(`** jako
substituci. Když je v `echo "..."` text, který má jen vypadat jako kód,
bash se ho pokusí **spustit** — a do logu se místo skutečné chyby vysypou
`var: command not found` a `syntax error near unexpected token`.

Naměřeno 1. 10. 2026 (běh #241, granule `ui.hud`): skutečná příčina selhání
(`ALIGN_LEFT` neexistuje v Godotu 4) se v tom šumu ztratila. Ladění pak
vypadá jako vada brány, i když šlo o chybu modelu.

CO JE VADA A CO NE (tohle rozlišení je celý smysl nástroje)
-----------------------------------------------------------
První verze tohohle skriptu hlásila KAŽDÝ zpětný apostrof v `echo` — a to
byl falešný poplach:

  BEZPEČNÉ (nehlásit):
    echo "text \`kód\`"        – escapovaný apostrof; v shellu je to literál
                                 (v YAML se `\`` používá právě proto)
    echo "hotovo ($(wc -l))"   – záměrná substituce, výsledek se vloží

  VADA (hlásit):
    echo "text `kód`"          – NEescapovaný apostrof; bash kód SPUSTÍ

Nástroj proto escapované apostrofy přeskočí a `$(` jen vypíše k posouzení.
Pravidlo: **falešný poplach nutí „opravovat" správný kód** (viz `AGENTS.md`),
takže nástroj, který nerozlišuje, je horší než žádný.

DŮKAZ, KTERÝ MÁM — a co jsem NAOPAK NEDOKÁZAL (přiznat je důležitější)
----------------------------------------------------------------------
  + V běhu #241 se v logu objevilo `...sh: line 39: var: command not found`
    a `syntax error near unexpected token '('` s textem `var x := load(...)`
    a `var x := uzel.neco()` — což je PŘESNĚ text, který byl v TIP echách
    `agent.yml`. Skutečná příčina selhání (`ALIGN_LEFT` neexistuje v Godotu 4)
    se v tom šumu ztratila; musel jsem ji dolovat ručně.   [NAMĚŘENO]
  - Že to způsobily PRÁVĚ ty zpětné apostrofy, a ne něco jiného v témž kroku
    (např. `git status --porcelain` s mezerou ve jménu souboru), jsem
    NEDOKÁZAL. Mechanismus jsem nereprodukoval — `echo "\`text\`"` sám
    o sobě v bash syntax error nevyhodí.  [SILNÁ INDICIE, NE DŮKAZ]

Oprava (odstranit apostrofy z TIP ech) je správná tak jako tak: text, který
má jen vypadat jako kód, nemá co dělat v `echo` se substitucí. Kdyby se šum
v logu objevil znovu, hledej i jinde — podezřelé je každé místo, kde se do
shellu dostane jméno souboru nebo výstup nástroje.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WF = [
    pathlib.Path(_PARENT / 'repo' / '.github' / 'workflows'),
    pathlib.Path(_PARENT / 'uo-shadows' / '.github' / 'workflows'),
]

# Neescapovaný zpětný apostrof: není před ním liché množství zpětných lomítek.
NEESCAPOVANY = re.compile(r"(?<!\\)(?:\\\\)*`")
SUBSHELL = re.compile(r"\$\(")

vad = 0
k_posouzeni = 0
for slozka in WF:
    for soubor in sorted(slozka.glob("*.yml")):
        try:
            radky = soubor.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        in_run = False
        odsazeni_run = 0
        for i, radek in enumerate(radky, 1):
            if re.match(r"^\s*run:\s*\|", radek):
                in_run = True
                odsazeni_run = len(radek) - len(radek.lstrip())
                continue
            if in_run:
                if radek.strip() and (len(radek) - len(radek.lstrip())) <= odsazeni_run:
                    in_run = False
                    continue
                st = radek.strip()
                if not st.startswith("echo"):
                    continue
                if NEESCAPOVANY.search(st):
                    vad += 1
                    print(f"VADA  {soubor.name}:{i}  (NEescapovaný apostrof – bash ten kód SPUSTÍ)")
                    print(f"        {st[:110]}")
                elif SUBSHELL.search(st):
                    k_posouzeni += 1
                    print(f"?     {soubor.name}:{i}  ($( v echo – obvykle záměr, zkontroluj)")
                    print(f"        {st[:110]}")

print()
if vad:
    print(f"VÝSLEDEK: {vad} VAD (neescapovaný apostrof), {k_posouzeni} k posouzení")
    sys.exit(1)
print(f"VÝSLEDEK: 0 vad, {k_posouzeni} echo s $( k posouzení (obvykle záměr)")
sys.exit(0)
