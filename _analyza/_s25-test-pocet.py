# -*- coding: utf-8 -*-
"""TEST PREDIKÁTU `je_pocet()` — bere funkci PŘÍMO ze zdroje nástroje.

Dvojice (text, očekáváno) pokrývá oba směry (`overovani` §3 bod 4):
  * tvary, které jsou POČET  → musí projít,
  * tvary, které počtu jen VYPADAJÍ → musí být odmítnuty.
"""
import os
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
z = (WS / "_analyza" / "audit2b-cisla-proti-zdroji.py").read_text(encoding="utf-8")
# ⚠ VÝŘEZ SE MUSÍ ZASTAVIT PŘED `BRANA_DIA = WS / …` — ta sahá na `WS`
# a `exec` by spadl na `NameError` (vlastní omyl testu, 2. 10. 2026).
# Začíná u `JINA_JEDNOTKA` (jednoznačné přiřazení) a končí u `je_pocet` +
# `SPOJENI`; `NENI_POCET` se do výřezu přidá zvlášť, protože v souboru stojí
# o pár set znaků dřív (u `CITACE`), ale patří k témuž predikátu.
i = z.index("    JINA_JEDNOTKA = re.compile")
j = i + z[i:].index("    # ⚠ DATUM JE NEJSILNĚJŠÍ")
_k = z[i:j]
if "    BRANA_DIA = WS" in _k:
    j = i + _k.index("    BRANA_DIA = WS")
_np = z.index("    NENI_POCET = re.compile")
blok = z[_np:z.index("\n", _np) + 1] + z[i:j]
# ⚠ POZOR: řádek níž NESMÍ `blok` PŘEPSAT holým `z[i:j]` — to byl vlastní
# omyl testu (výřez se tím ztratil a `exec` nenašel `NENI_POCET`).
blok = "\n".join(l[4:] if l.startswith("    ") else l for l in blok.splitlines())
ns = {"re": re, "os": os}
exec(blok, ns)
je_pocet = ns["je_pocet"]
SPOJENI = ns["SPOJENI"]
OCEKAVANA = ns["OCEKAVANA"]
NENI_POCET = ns["NENI_POCET"]

# ── DIAGNOSTIKA pro JEDEN případ (aby se nehádalo, co funkce vidí) ────────
if "--diagnostika" in sys.argv:
    _t = "12 kontrol, 0 chyb"
    _m = list(re.finditer(r"(\d+)\s+(?:kontrol(?!\w)|dokument)", _t))[-1]
    print("  DIAG: text=%r  match=%r  konec=%d" % (_t, _m.group(0), _m.end()))
    _zr = _t.rfind("\n", 0, _m.end()) + 1
    print("  DIAG: začátek řádku=%d · SPOJENI hledá v [%d, %d)" % (_zr, _zr, _m.end()))
    for _mm in SPOJENI.finditer(_t, _zr, _m.end()):
        print("  DIAG: SPOJENI našlo %r  [%d,%d)  jednotka=%r"
              % (_mm.group(0), _mm.start(), _mm.end(), _mm.group("jednotka")))
    for _jed in ("kontrol", "dokument"):
        print("  DIAG: je_pocet(očekávaná=%r) = %s"
              % (_jed, je_pocet(_t, _m.end(), _jed)))
    print("  DIAG: NENI_POCET.match(%r) = %s"
          % (_t[_m.end():], NENI_POCET.match(_t[_m.end():])))
    sys.exit(0)

VZOR = re.compile(r"(\d+)\s+(?:kontrol(?!\w)|dokument)")

# (text, očekávaný výsledek, proč, KTEROU veličinu měřím)
PRIPADY = [
    ("39 kontrol, 0 selhání", True, "čítač brány", "kontrol"),
    ("59 kontrol,   0 selhání", True, "víc mezer", "kontrol"),
    ('23 kontrol). Bez něj „0 nálezů" nic neznamená', True, "závorka", "kontrol"),
    ("57 dokumentů", True, "dokumentů = počet", "dokument"),
    ("8 dokument správně | Ne", True, "číslo+jednotka k sobě PATŘÍ", "dokument"),
    ("2 kontrolní vzorky", False, "`kontrolní` NENÍ čítač", "kontrol"),
    ("0 řádků", False, "vzor to ani nemá chytit", "kontrol"),
    ("64 kontrol, 0 selhání", True, "jiný čítač", "kontrol"),
    ("12 kontrol, 0 chyb", True, "jiný čítač", "kontrol"),
    # ⚠ Tohle je ta past z `HANDOFF.md:583`: na řádku je `8 dokument`, ale
    # číslo patří veličině, kterou v tu chvíli NEMĚŘÍM → musí se odmítnout.
    ("8 dokument správně", False, "měřím `kontrol`, ne `dokument`", "kontrol"),
]

print("=" * 92)
print("  TEST `je_pocet()` — 10 případů (7 kladných, 3 záporné)")
print("=" * 92)
chyby = 0
for text, ocekavane, proc, jednotka in PRIPADY:
    nalezy = list(VZOR.finditer(text))
    if not nalezy:
        # Text, který vzor vůbec nemá chytit: to je taky SPRÁVNĚ — ale jinak
        # než „predikát vrátil False". Rozlišit se to musí, jinak by test
        # procházel z nesprávného důvodu.
        verdikt = "OK (vzor nenašel — správně)" if not ocekavane else "CHYBA (vzor nenašel, měl!)"
        if ocekavane:
            chyby += 1
        print("  %-46r %s" % (text[:46], verdikt))
        continue
    got = je_pocet(text, nalezy[-1].end(), jednotka)
    ok = (got == ocekavane)
    if not ok:
        chyby += 1
    print("  %-44r %-12s je_pocet=%-5s očekáváno=%-5s %s"
          % (text[:44], "(" + jednotka + ")", got, ocekavane,
             "OK" if ok else "<<< CHYBA"))

print()
print("=" * 92)
print("  ZMĚŘENO: případů=%d, chyb=%d" % (len(PRIPADY), chyby))
sys.exit(1 if chyby else 0)
