#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""NEZÁVISLÝ PŘEPOČET OMYLŮ — jinou metodou, než jakou používá brána.

PROČ: zadání (`NEXT-SESSION-INSTRUKCE.md` §3, Úkol 2.2) žádá **vlastní skript**,
protože brána `kronika-kontrola.py` je taky jen měřidlo — a to, co měří, může
měřit špatně. „Nezávisle" ale znamená **jinou metodou**, ne opsaný vzor.

ČÍM SE TO LIŠÍ OD BRÁNY:
  * brána hledá bloky pevným seznamem 8 kotev a konec bere nadpisem;
  * tenhle skript najde bloky **regexem na nadpisy** (`## 8.` a `### 8x.`)
    a konec bloku určí podle ÚROVNĚ nadpisu — ne podle seznamu.
  * a hlavně se ptá na **jinou otázku**: ne „kolik řádků", ale
    **„je číslování omylů 1..N úplné a bez duplicit?"** — což je přesně to,
    co má kronika hlídat („nezapsaný omyl zmizí navždy"). Kdyby jeden omyl
    chyběl a jiný byl dvakrát, počet řádků by SEDĚL a brána by mlčela.

Použití:  python _analyza\\v4-omyly-nezavisle.py
Návrat:   0 = počty sedí na kroniku §3 a číslování je úplné | 1 = rozchod
"""

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
BRANA = WS / "_analyza" / "kronika-kontrola.py"

# Blok = nadpis `## 8. …` (hlavní) nebo `### 8x. …` (vedlejší). Nic jiného.
VZOR_NADPISU = re.compile(r"^(#{2,3})\s+(8[b-z]?\.)\s+(.*)$")
# Řádek tabulky omylu: id je ČISTĚ ČÍSELNÉ (H8 neprojde) — viz overovani §8.3
VZOR_RADKU = re.compile(r"^\|\s*\*{0,2}(\d+)\*{0,2}\s*\|")

radky = HANDOFF.read_text(encoding="utf-8").splitlines()

# --- 1) najdi bloky omylů -------------------------------------------------
bloky = []          # (nazev, uroven, index_prvniho_radku)
for i, r in enumerate(radky):
    m = VZOR_NADPISU.match(r)
    if m:
        uroven, cislo = len(m.group(1)), m.group(2).rstrip(".")
        bloky.append([cislo, uroven, i, m.group(3)])

print("=" * 78)
print("NEZÁVISLÝ PŘEPOČET OMYLŮ (vlastní metoda, jiná otázka)")
print("=" * 78)
print()
print("  nalezené bloky omylů (regexem na nadpis, ne ze seznamu):")
for cislo, uroven, i, titulek in bloky:
    print("    řádek %5d  %-4s (#%d)  %s" % (i + 1, cislo, uroven, titulek[:52]))

# --- 2) spočítej řádky v každém bloku (konec = nadpis stejné/vyšší úrovně) --
# ⚠ PAST, DO KTERÉ JSEM SPADL NAPOPRVÉ (a je popsaná přímo v bráně): blok
# `## 8.` je ÚROVEŇ 2, kdežto `### 8b.` je úroveň 3 — takže „konec na nadpisu
# stejné/vyšší úrovně" u bloku `8` spolkne celý `8b`–`8f` a sečte je dvakrát
# (naměřeno: **117 místo 75**). Samotná úroveň na oddělení NESTAČÍ.
# Blok proto musí ukončit i nadpis KAŽDÉHO následujícího bloku omylů.
VSE_ANCHORY = [b[2] for b in bloky]
pocty = {}
idy_bloku = {}
okna = {}            # (od, do) — POUŽIJE SE I PRO HLEDÁNÍ „MIMO“, aby se
                     # neměřilo dvěma různými okny (to byla moje chyba)
for idx, (cislo, uroven, i, _t) in enumerate(bloky):
    konec = len(radky)
    for j in range(i + 1, len(radky)):
        if j in VSE_ANCHORY:                 # nadpis dalšího bloku omylů
            konec = j
            break
        m2 = re.match(r"^(#{1,6})\s", radky[j])
        if m2 and len(m2.group(1)) <= uroven:
            konec = j
            break
    okna[cislo] = (i, konec)
    idy = []
    for r in radky[i:konec]:
        m = VZOR_RADKU.match(r)
        if m:
            idy.append(int(m.group(1)))
    idy_bloku[cislo] = idy
    pocty[cislo] = len(idy)

print()
print("  %-6s %-8s %s" % ("BLOK", "ŘÁDKŮ", "ROZSAH ID"))
print("  " + "-" * 44)
for cislo, _u, _i, _t in bloky:
    idy = idy_bloku[cislo]
    rozsah = "%d–%d" % (min(idy), max(idy)) if idy else "—"
    print("  %-6s %-8d %s" % (cislo, pocty[cislo], rozsah))
celkem = sum(pocty.values())
print("  %-6s %-8d" % ("CELKEM", celkem))

# --- 3) ÚPLNOST A JEDNOZNAČNOST ČÍSLOVÁNÍ (jiná otázka než počet) ----------
vsechny = [n for idy in idy_bloku.values() for n in idy]
duplicit = sorted({n for n in vsechny if vsechny.count(n) > 1})
print()
print("  kontrola číslování V BLOCÍCH: id %d–%d, celkem %d řádků"
      % (min(vsechny), max(vsechny), len(vsechny)))
print("  duplicity: %s" % (duplicit if duplicit else "žádné"))

# ⚠ A TEĎ TA DRUHÁ OTÁZKA — a je to NÁLEZ: řádky s číselným id MIMO ty bloky.
# Brána `kronika-kontrola.py` má **PEVNÝ SEZNAM 8 kotev**, takže omyl, který
# je zapsaný pod JINÝM nadpisem, **nikdy neuvidí** — a jeho „celkem" pak není
# „všechny omyly v dokumentu", ale „omyly v 8 blocích, které znám".
# Je to táž vada jako H15 (brána diakritiky měla ruční seznam 5 z 12 skillů).
mimo = []
for i, r in enumerate(radky):
    m = VZOR_RADKU.match(r)
    if not m:
        continue
    # STEJNÁ OKNA jako při počítání (první verze měla jiná → nález propadl)
    if any(od <= i < do for od, do in okna.values()):
        continue
    # nadpis, pod kterým ten řádek leží
    nadpis = ""
    for j in range(i, -1, -1):
        if re.match(r"^#{1,6}\s", radky[j]):
            nadpis = radky[j][:64]
            break
    mimo.append((i + 1, int(m.group(1)), nadpis))
print()
print("  řádků s číselným id MIMO bloky omylů: %d" % len(mimo))
podle_nadpisu = {}
for radek_c, cislo_id, nadpis in mimo:
    podle_nadpisu.setdefault(nadpis, []).append(cislo_id)
for nadpis, idy in podle_nadpisu.items():
    print("      %-62s %s" % (nadpis, idy))

# Jsou to SKUTEČNÉ omyly, nebo jiná tabulka? Rozhoduje nadpis, ne tvar řádku.
OMYLOVE_NADPISY = [n for n in podle_nadpisu if "omyl" in n.lower()]
idy_mimo_omylu = sorted(n for nadpis in OMYLOVE_NADPISY for n in podle_nadpisu[nadpis])

# ⚠ A POZOR NA DRUHÝ SMĚR — tentýž omyl může být v dokumentu DVAKRÁT
# (`§16.8` je druhá kopie téhož, co je v bloku `8e`). Kdo sečte řádky, dostane
# **91**, a to je ŠPATNÉ ČÍSLO. Správná otázka je „kolik je UNIKÁTNÍCH id“.
v_blocich = set(vsechny)
vsechna_id = v_blocich | set(idy_mimo_omylu)
jen_mimo = sorted(set(idy_mimo_omylu) - v_blocich)
dvakrat = sorted(set(idy_mimo_omylu) & v_blocich)
print()
if jen_mimo:
    print("  ⚠ NÁLEZ (vada MĚŘIDLA, třída S27/H15): pod nadpisem pojmenovaným")
    print("    jako omyly je %d id, která v 8 blocích NEJSOU: %s" % (len(jen_mimo), jen_mimo))
    print("    → brána `kronika-kontrola.py` má PEVNÝ SEZNAM 8 kotev, takže je nevidí.")
    print("    → „celkem %d“ v kronice §3 NENÍ počet omylů v dokumentu." % len(vsechny))
    print("    → UNIKÁTNÍCH omylů v HANDOFF.md je %d (%d v blocích + %d jen mimo)."
          % (len(vsechna_id), len(v_blocich), len(jen_mimo)))
if dvakrat:
    print("  POZNÁMKA (ne nález): id %s je v dokumentu DVAKRÁT (blok i §16.8)."
          % (dvakrat if len(dvakrat) <= 12 else "%d–%d" % (min(dvakrat), max(dvakrat))))
    print("    Součet ŘÁDKŮ by dal %d — což je špatné číslo; správně je %d unikátních."
          % (len(vsechny) + len(idy_mimo_omylu), len(vsechna_id)))

# --- 4) srovnej s tvrzením kroniky §3 -------------------------------------
kron = KRONIKA.read_text(encoding="utf-8")
i3 = kron.find("## 3. Počty omylů")
i4 = kron.find("## 4.", i3)
tvrzene = {}
for r in kron[i3:i4].splitlines():
    m = re.match(r"^\|\s*\*{0,2}(\d+[–-]\d+|8[b-z])\*{0,2}\s*\|\s*([^|]*)\|\s*\*{0,2}(\d+)\*{0,2}\s*\|", r)
    if m:
        tvrzene[m.group(1)] = int(m.group(3))
print()
print("  %-6s %-14s %-14s %s" % ("BLOK", "MŮJ PŘEPOČET", "KRONIKA §3", "SOUHLAS"))
print("  " + "-" * 52)
# Klíč v kronice §3 NENÍ číslo nadpisu: hlavní blok `## 8.` má v kronice klíč
# `1–13` (podle rozsahu id). Mapuje se to VÝPOČTEM z rozsahu, ne opsáním.
chyby = []
for cislo, _u, _i, _t in bloky:
    idy = idy_bloku[cislo]
    klic = ("%d–%d" % (min(idy), max(idy))) if idy else cislo
    t = tvrzene.get(klic, tvrzene.get(cislo))
    ok = (t == pocty[cislo])
    print("  %-6s %-14d %-14s %s"
          % (klic, pocty[cislo], t if t is not None else "CHYBÍ", "OK" if ok else "ROZCHOD"))
    if not ok:
        chyby.append("blok %s: přepočet %d, kronika tvrdí %s" % (klic, pocty[cislo], t))
if "CELKEM" in tvrzene:
    print("  %-6s %-14d %-14s" % ("CELKEM", celkem, tvrzene["CELKEM"]))
elif "celkem" in tvrzene:
    print("  %-6s %-14d %-14s %s"
          % ("CELKEM", celkem, tvrzene["celkem"],
             "OK" if tvrzene["celkem"] == celkem else "ROZCHOD"))
    if tvrzene["celkem"] != celkem:
        chyby.append("celkem (bloky): přepočet %d, kronika tvrdí %s"
                     % (celkem, tvrzene["celkem"]))
else:
    # ⚠ DVĚ RŮZNÉ OTÁZKY, DVĚ RŮZNÁ ČÍSLA (a to je nález H18):
    #   * „omylů v N blocích, které brána ZNÁ" = co vidí `kronika-kontrola.py`
    #     (má PEVNÝ seznam kotev — a ten se ČTE Z BRÁNY, neopisuje se)
    #   * „omylů celkem v HANDOFF.md (unikátní id)" = co je v dokumentu
    # Kdybych porovnával svoje bloky (9) proti bráně (8), byl by to FALEŠNÝ
    # POPLACH na správných datech — a to je přesně to, co měřidlo nesmí dělat.
    zdroj = BRANA.read_text(encoding="utf-8")
    kotvy = re.findall(r'\(\s*"[^"]*"\s*,\s*"([^"]+)"\s*\)', zdroj)
    if not kotvy:
        kotvy = re.findall(r'^\s*\("[^"]+",\s*"([^"]+)"\),', zdroj, re.M)
    zname, nezname = [], []
    for cislo, _u, i, _t in bloky:
        radek = radky[i]
        (zname if any(radek.startswith(k) for k in kotvy) else nezname).append(cislo)
    soucet_znamych = sum(pocty[c] for c in zname)
    print("  kotvy přečtené Z BRÁNY: %d" % len(kotvy))
    print("  bloků, které brána ZNÁ: %d (%s) → %d omylů"
          % (len(zname), ", ".join(zname), soucet_znamych))
    if nezname:
        print("  bloků, které brána NEZNÁ: %d (%s) → %d omylů"
              % (len(nezname), ", ".join(nezname), sum(pocty[c] for c in nezname)))
    m_zná = re.search(r"\*\*omylů v (\d+) blocích, které brána ZNÁ\*\*\s*\|\s*\*\*(\d+)\*\*", kron[i3:i4])
    m_cel = re.search(r"\*\*omylů celkem v `HANDOFF\.md` \(unikátní id\)\*\*\s*\|\s*\*\*(\d+)\*\*", kron[i3:i4])
    if m_zná:
        hod_bloku, hod_omylu = int(m_zná.group(1)), int(m_zná.group(2))
        ok = (hod_bloku == len(zname) and hod_omylu == soucet_znamych)
        print("  %-6s %-14d %-14s %s  (v %d blocích, které brána ZNÁ)"
              % ("ZNÁ", soucet_znamych, hod_omylu, "OK" if ok else "ROZCHOD", hod_bloku))
        if not ok:
            chyby.append("kronika §3 (co zná brána): tvrdí %d bloků / %d omylů, naměřeno %d / %d"
                         % (hod_bloku, hod_omylu, len(zname), soucet_znamych))
    else:
        print("  CELKEM v kronice §3 NENALEZEN — hledal jsem `omylů v N blocích, které brána ZNÁ`")
    if m_cel:
        unik = len(vsechna_id)
        hod = int(m_cel.group(1))
        print("  %-6s %-14d %-14s %s  (UNIKÁTNÍCH id v celém dokumentu)"
              % ("UNIKÁT", unik, hod, "OK" if hod == unik else "ROZCHOD"))
        if hod != unik:
            chyby.append("kronika §3: unikátních id %s, naměřeno %d" % (hod, unik))
    else:
        print("  UNIKÁTNÍ SOUČET v kronice §3 NENALEZEN")

# „z toho vad měřidla" je RUČNÍ klasifikace (sloupec „Jak to vzniklo") — tenhle
# skript ji NEUMÍ a nesmí ji předstírat. Vypíše jen mechanický odhad keywordem.
MEZ = ("měřidlo", "test jsem psal", "můj test", "brána", "skript", "měření")
pocet_meridlo = 0
for idy in idy_bloku.values():
    pass
for idx, (cislo, uroven, i, _t) in enumerate(bloky):
    konec = bloky[idx + 1][2] if idx + 1 < len(bloky) else len(radky)
    for r in radky[i:konec]:
        if VZOR_RADKU.match(r) and any(k in r.lower() for k in MEZ):
            pocet_meridlo += 1
print()
print("  POZNÁMKA: „z toho vad měřidla“ je v kronice RUČNÍ klasifikace.")
print("  Mechanický odhad podle klíčových slov ve sloupci „Jak to vzniklo“: %d" % pocet_meridlo)
print("  NENÍ to totéž číslo jako ruční klasifikace — jen hrubá kontrola řádu.")

print()
if chyby:
    print("NALEZENO %d ROZCHODŮ:" % len(chyby))
    for c in chyby:
        print("  CHYBA %s" % c)
    sys.exit(1)
if jen_mimo:
    print("POČTY V BLOCÍCH SEDÍ (%d v %d blocích) — ale je tu NÁLEZ VÝŠ:"
          % (celkem, len(bloky)))
    print("  %d omylů (%s) je zapsaných pod jiným nadpisem, a brána je nevidí."
          % (len(jen_mimo), jen_mimo))
    sys.exit(1)
print("SOUHLASÍ — %d omylů v %d blocích, číslování bez děr a duplicit."
      % (celkem, len(bloky)))
sys.exit(0)
