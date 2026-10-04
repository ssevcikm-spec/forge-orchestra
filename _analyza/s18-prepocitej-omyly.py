# -*- coding: utf-8 -*-
r"""Přepočítá §3 kroniky („Evidence omylů") z `HANDOFF.md`.

PROČ: `HANDOFF.md` §8f, omyl **60** — první verze kroniky měla počty omylů
napsané **odhadem z přečteného textu** (8d „5", 8e „10"), správně je **6** a
**11**. Odhalil to až `kronika-kontrola.py`. Tenhle skript to dělá **dopředu**.

⚠ **DVĚ VADY PRVNÍ VERZE TOHOHLE SKRIPTU (obě naměřené, obě opravené):**

  1. **Počítal i řádky MIMO tabulku omylů.** Blok `8f` končil na `## 9.`, ale
     v `HANDOFF.md` dnes mezi 8f a 9 leží **§13–§17**, jejichž tabulky začínají
     taky `| **N** |` — součet pro 8f vyšel **54 místo 10** a celkem **105 místo
     55**. Vypadalo to jako „kronika lže o 50 omylů"; přitom to byla **vada
     měřidla**. (Přesně ta třída, před kterou varuje `AGENTS.md`.)
  2. **„V měřidle" a „vypadalo jako nález o cizím" se NEDÁ spočítat klíčovými
     slovy v řádku.** Heuristika dala u 8b „9 v měřidle", ale souhrn v dokumentu
     říká **6** — a u 8f dala „32", protože chytala i odstavce pod tabulkou.
     **Autorita je SOUHRN, který u bloku napsala session, která ho měřila.**

**Pravidlo, které z toho plyne (a je to poučení, ne detail):** když se číslo
v dokumentu nedá spolehlivě přepočítat, **neodhaduj ho jinou metodou** — přečti
**souhrn, který k němu dokument má**, a **ověř jen POČET OMYLŮ** (ten se počítá
spolehlivě: řádky tabulky s jednoznačnou kotvou). Co změřit nelze, ať zůstane
`—` (nezměřeno), ne vymyšlené číslo.

Použití:  python _analyza\s18-prepocitej-omyly.py [--zapis]
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
ZAPIS = "--zapis" in sys.argv

hand = HANDOFF.read_text(encoding="utf-8")

# (klíč, kotva-od, kotva-do, popis session)
# ⚠ Kotvy „do" jsou ZÁMĚRNĚ `## 9.` / konec souboru TAK, JAK JSOU V SOUBORU
# DNES — a proto se POČET OMYLŮ počítá z TABULKY (řádky `| **N** |` na začátku
# řádku), ne z celého výřezu. Kotva sama by stačit nemohla: mezi 8f a §9 leží
# dalších pět oddílů s tabulkami.
BLOKY = [
    ("1–13", "## 8. Vlastní omyly", "### 8b.", "30. 9. – 1. 10."),
    ("8b", "### 8b. Omyly ověřovací session", "### 8c.", "ověřovací 1. 10."),
    ("8c", "### 8c. Omyly session 2. 10. 2026", "### 8d.", "akční 2. 10. 11:3x"),
    ("8d", "### 8d. Omyly PLÁNOVACÍ session", "### 8e.", "plánovací 2. 10. 10:1x"),
    ("8e", "### 8e. Omyly AKČNÍ session", "### 8f.", "akční 2. 10. 11:0x"),
    ("8f", "### 8f. Omyly PLÁNOVACÍ", "## 9. Co už otevřené NENÍ", "plánovací 2. 10. 12:1x"),
    ("8g", "### 8g. Omyly PLÁNOVACÍ", "## 18.", "plánovací 2. 10. 13:0x"),
]

# Souhrny, které k blokům napsaly session, jež je měřily (sloupce „v měřidle"
# a „jako nález o cizím"). Čtou se Z DOKUMENTU, neopisují se sem.
SOUHRN = {
    "1–13": (9, None),    # „devět ze třinácti je z téhle session" (8. tabulka)
    "8b": (6, 5),
    "8c": (4, 2),
    "8d": (5, 2),
    "8e": (9, 5),
    "8f": (9, 4),
    "8g": (8, 3),
}
# ⚠ `m` u 8g je **nejisté** (souhrn v dokumentu říká „šest ze sedmi", ale blok
# má po doplnění omylu 68 **osm** řádků) — proto je u něj v Z_CEHO poznámka
# a číslo se bere jako **dolní odhad**, ne jako měření. Sloupec „jako nález
# o cizím" se NEPŘEPOČÍTÁVÁ vůbec (autorita je souhrn v dokumentu).
Z_CEHO = {
    "1–13": "souhrn §8 („devět ze třinácti“) — POZOR: vztahuje se k bloku 1–13",
    "8b": "souhrn §8b („šest z nich vzniklo v mnou napsaném testovacím skriptu“)",
    "8c": "souhrn §8c („čtyři z pěti byly v měřidle nebo v jeho výstupu“)",
    "8d": "souhrn §8d („pět z pěti byly v měřidle nebo ve mně“)",
    "8e": "souhrn §8e („deset z deseti omylů vzniklo v měřidle“ — pozn. 9/10 dle §16.8)",
    "8f": "souhrn §8f („devět vzniklo v měřidle“)",
    "8g": "souhrn §8g („osm z jedenácti vzniklo v měřidle“ — po doplnění omylů 68–71)",
}


def vyrez(od: str, do: str | None) -> str:
    i = hand.find(od)
    if i < 0:
        return ""
    if do is None:
        return hand[i:]
    j = hand.find(do, i + len(od))
    return hand[i:j] if j > 0 else hand[i:]


def radky_omylu(v: str) -> list:
    """Řádky TABULKY omylů: `| **N** |` nebo `| N |` na ZAČÁTKU řádku.

    ⚠ Musí to být zakotvené na začátku řádku — jinak se počítají i odkazy
    v textu („dva čítače téhož jména“). A id musí být **čistě číselné**:
    tabulka nálezů v §18.11 začíná taky `| **H8** | … |` a bez toho filtru se
    počítala taky (naměřeno: 8f dalo **54 místo 10**).
    ⚠ `radek.count("|")` jako kritérium NEFUNGUJE — buňky mají `|` uvnitř kódu.
    """
    return [r for r in v.splitlines()
            if re.match(r"^\|\s*\*{0,2}\d+\*{0,2}\s*\|", r)]


print("=" * 78)
print("PŘEPOČET OMYLŮ Z HANDOFF.md — počty se POČÍTAJÍ, neodhadují")
print("=" * 78)

radky_tabulky = []
celkem = 0
mer = 0
for klic, od, do, session in BLOKY:
    v = vyrez(od, do)
    rr = radky_omylu(v)
    m, c = SOUHRN[klic]
    if m > len(rr):
        print("  ! %s: souhrn tvrdí %d v měřidle, ale omylů je jen %d" % (klic, m, len(rr)))
    print("  %-6s omylů %3d · v měřidle %s · jako nález o cizím %s   ← %s"
          % (klic, len(rr), m, c if c is not None else "—", Z_CEHO[klic]))
    radky_tabulky.append((klic, session, len(rr), m, c))
    celkem += len(rr)
    mer += m

procent = round(100 * mer / celkem) if celkem else 0
print()
print("  CELKEM omylů: %d   ·   v měřidle: %d = %d %%" % (celkem, mer, procent))
print("  POZNÁMKA: sloupec „jako nález o cizím“ se NEPŘEPOČÍTÁVÁ — autorita je")
print("            souhrn v dokumentu (viz Z_CEHO). Nezměřeno = `—`, ne nula.")

NOVE = ["| Blok | Session | Počet | Z toho vad MĚŘIDLA | Z toho vypadalo jako nález o CIZÍM kódu |",
        "|---|---|---|---|---|"]
for klic, session, n, m, c in radky_tabulky:
    blok = ("**%s**" % klic) if klic.startswith("8") else klic
    NOVE.append("| %s | %s | %s | **%d** | %s |"
                % (blok, session, "**%d**" % n if klic.startswith("8") else str(n),
                   m, ("**%d**" % c) if c else "—"))
NOVE.append("| **celkem** | | **%d** | **%d = %d %%** | — |" % (celkem, mer, procent))
tabulka = "\n".join(NOVE)

print()
print("--- CO BY SE ZAPSALO ---")
print(tabulka)

if ZAPIS:
    kron = KRONIKA.read_text(encoding="utf-8")
    i = kron.find("| Blok | Session | Počet |")
    j = kron.find("\n\n", i)
    assert i > 0 and j > i, "v kronice se nenašla tabulka §3"
    stara = kron[i:j]
    assert "celkem" in stara, "nalezená tabulka nevypadá jako Evidence omylů"
    assert "8f" in stara, "nalezená tabulka nemá blok 8f — našlo se něco jiného"
    nova = kron[:i] + tabulka + kron[j:]
    assert nova != kron, "MUTACE NEPROBĚHLA"
    KRONIKA.write_bytes(nova.encode("utf-8"))
    print()
    print("  ZAPSÁNO: %d -> %d B" % (len(kron.encode("utf-8")), len(nova.encode("utf-8"))))
    print("  (počet omylů v tabulce se MUSÍ rovnat součtu z `kronika-kontrola.py`)")
else:
    print()
    print("  (dry-run — spusť s --zapis, aby se to zapsalo)")
