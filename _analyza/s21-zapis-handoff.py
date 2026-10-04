# -*- coding: utf-8 -*-
r"""Zapíše §21 (provedení) a §8h (vlastní omyly) do `HANDOFF.md`.

PROČ SKRIPTEM: `HANDOFF.md` má 3 169 řádků, nic se nesmí ztratit a oddíly
nejdou vložit „někam na konec" — **každý patří na SVÉ místo**:

  * **§8h** musí být **uvnitř** bloku omylů §8, tedy ZA posledním řádkem
    tabulky `8g` (omyl 71). Kdyby se přidal na konec souboru (jak to dělá
    `s18-zapis-handoff.py`), `kronika-kontrola.py` by ho **neměřil** — jeho
    kotva pro `8g` je `## 18. Ověření práce AKČNÍ session`, takže by tabulka
    zůstala mimo výřez. Naměřeno: přesně tímhle způsobem se do výřezu jednou
    dostala CIZÍ tabulka (omyl 67).
  * **§21** patří na **konec souboru** (je to nejnovější událost).

Pojistky (každá je naměřená past):
  1. každá kotva smí být v souboru jen JEDNOU (jinak se oddíl vloží dvakrát —
     omyl 68),
  2. vkládaný text se bere z `.md` souboru, ne z literálu (české uvozovky
     v Python literálu rozbily v projektu už mnoho skriptů),
  3. po zápisu se ověří, že **předchozí obsah je na začátku bajt na bajt
     stejný** a že každá kotva je v souboru právě 1×.

Použití:  python _analyza\s21-zapis-handoff.py [--zapis]
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
ZALOHA = WS / "_analyza" / "handoff-pred-s21.md"
ZAPIS = "--zapis" in sys.argv

OMYL_71 = "| **71** |"
KOTVA_8H = "### 8h. Omyly AKČNÍ session"
KOTVA_21 = "## 21. Provedeno 2. 10. 2026"

text = HANDOFF.read_text(encoding="utf-8")
oddil_8h = (WS / "_analyza" / "s21b-oddil-8h.md").read_text(encoding="utf-8").strip()
oddil_21 = (WS / "_analyza" / "s21-oddil.md").read_text(encoding="utf-8").strip()

# ── pojistka 1: dvojí vložení ───────────────────────────────────────────────
for jmeno, kotva in (("8h", KOTVA_8H), ("21", KOTVA_21)):
    pocet = text.count(kotva)
    if pocet:
        print("ODMÍTNUTO: kotva %r je v HANDOFF.md už %dx — oddíly se vkládají JEN JEDNOU."
              % (kotva, pocet))
        print("  Vrať soubor ze zálohy: %s" % ZALOHA)
        sys.exit(2)

# ── pojistka 2: vkládaný text má správný tvar ───────────────────────────────
assert oddil_8h.startswith("### 8h."), "text §8h nezačíná nadpisem: %r" % oddil_8h[:60]
assert oddil_21.startswith("## 21."), "text §21 nezačíná nadpisem: %r" % oddil_21[:60]
assert len(oddil_8h) > 3000, "§8h je podezřele krátký (%d B)" % len(oddil_8h)
assert len(oddil_21) > 5000, "§21 je podezřele krátký (%d B)" % len(oddil_21)
assert oddil_8h.count("\n") >= 10, "§8h nemá tabulku omylů (%d řádků)" % oddil_8h.count("\n")

# ── §8h: ZA poslední řádek omylu 71, ale PŘED uzavíracím odstavcem bloku 8g ──
# ⚠ PROČ NE HONA ZA TABULKOU (naměřeno 2. 10. 2026): blok 8g **není jen
# tabulka** — za ní následuje jeho **uzavírací odstavec** („Vzor z těch
# jedenácti…"). Kdyby se §8h vložil mezi tabulku a ten odstavec, **rozdělil by
# blok 8g** a `kronika-kontrola.py` by blok 8g přestal nacházet (**měřil by
# 19 omylů místo 11**). Správné místo je **za uzavíracím odstavcem**.
assert text.count(OMYL_71) == 1, "kotva omylu 71 není právě 1x (nalezeno %d)" % text.count(OMYL_71)
i71 = text.find(OMYL_71)
konec71 = text.find("\n", i71)
assert konec71 > i71, "řádek omylu 71 nemá konec"
# Ověření, že 71 je opravdu POSLEDNÍ omyl bloku: za ním už nesmí být řádek
# tabulky s VYŠŠÍM číslem omylu. (Pouhé „nesmí následovat žádný `| **N** |`"
# je špatné kritérium — naměřeno: za §8g jsou tabulky §17–§21 s vlastním
# číslováním od 1, takže by to hlásilo falešný poplach na správném souboru.)
zbytek = text[konec71:]
vyssi = [int(m.group(1)) for L in zbytek.splitlines()
         if (m := re.match(r"^\|\s*\*{0,2}(\d+)\*{0,2}\s*\|", L)) and int(m.group(1)) > 71]
assert not vyssi, "za omylem 71 je další omyl s vyšším číslem (%s) — vkládal bych doprostřed" % vyssi[:5]

# Konec bloku 8g = poslední řádek jeho uzavíracího odstavce (před `---`, za
# kterým začíná `## 18.`).
KONEC_8G = "> jim uvěří, nebo je „opraví\" špatně."
assert text.count(KONEC_8G) == 1, \
    "uzavírací odstavec bloku 8g se nenašel (%dx) — vkládal bych doprostřed bloku" % text.count(KONEC_8G)
i_konec = text.find(KONEC_8G) + len(KONEC_8G)
assert text.find(OMYL_71) < i_konec, "konec 8g je PŘED tabulkou — něco je špatně"

novy = text[:i_konec] + "\n\n" + oddil_8h + "\n" + text[i_konec:]

# ── §21: na KONEC souboru ───────────────────────────────────────────────────
novy2 = novy.rstrip("\n") + "\n\n---\n\n" + oddil_21 + "\n"

# ── pojistka 3: co se nesmí změnit ──────────────────────────────────────────
assert novy2.count(KOTVA_8H) == 1, "§8h není právě 1x"
assert novy2.count(KOTVA_21) == 1, "§21 není právě 1x"
assert novy2.count(OMYL_71) == 1, "omyl 71 se ztratil nebo zdvojil"
assert novy2.startswith(text[:100000]), "PŘEDCHOZÍ OBSAH SE ZMĚNIL (prvních 100 kB)"
assert len(novy2) > len(text), "soubor se nezvětšil"
# Poslední řádek omylu 8g musí zůstat PŘED §8h.
assert novy2.find(OMYL_71) < novy2.find(KOTVA_8H) < novy2.find(KOTVA_21), \
    "pořadí oddílů je špatné"

print("PŘED: %d B, %d řádků" % (len(text.encode("utf-8")), len(text.splitlines())))
print("PO:   %d B, %d řádků" % (len(novy2.encode("utf-8")), len(novy2.splitlines())))
print("  §8h vložen za omyl 71 (uvnitř bloku §8), §21 na konec souboru")
print("  omylů v §8h: %d" % len([1 for L in oddil_8h.splitlines()
                                if (m := re.match(r"^\|\s*\*{0,2}(\d+)\*{0,2}\s*\|", L))]))

if ZAPIS:
    ZALOHA.write_bytes(HANDOFF.read_bytes())
    print("  záloha: %s (%d B)" % (ZALOHA.name, ZALOHA.stat().st_size))
    HANDOFF.write_bytes(novy2.encode("utf-8"))
    # Ověření VÝSTUPU, ne návratové hodnoty (past overovani §7.3).
    zpet = HANDOFF.read_text(encoding="utf-8")
    assert zpet == novy2, "zapsaný obsah nesedí s tím, co jsem sestavil"
    print("  ZAPSÁNO a ověřeno čtením z disku.")
else:
    print("  (dry-run — spusť s --zapis)")
