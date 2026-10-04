#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""OVĚŘENÍ BRÁNY KRONIKY NA ŽIVÉM DOKUMENTU — má opravdu TŘI stavy?

PROČ: `HANDOFF.md` §21.4 tvrdí, že brána `kronika-kontrola.py` byla opravena
tak, že **chybějící blok se hlásí jako `NEZMĚŘENO`**, a ne jako „naměřená
nula". To je tvrzení o MĚŘIDLE — a to se musí ověřit spuštěním, ne čtením
(zadání `NEXT-SESSION-INSTRUKCE.md` §3, bod 1.5 a Úkol 3/H17).

CO SE MĚŘÍ (5 případů; každý mutuje KOPII, originál se nikdy nemění):
  Z   kontrola: živá kronika + živý handoff            → musí projít (exit 0)
  C1  ÚKOL 1.5: v kopii kroniky počet u `8h` na 99      → musí SPADNOUT
  C2  v kopii HANDOFFu se PŘEJMENUJE nadpis bloku 8h    → musí hlásit
      `NEZMĚŘENO`, a NESMÍ hlásit „skutečný počet omylů: 0" (to je ta vada H17)
  C3  v kopii kroniky se SMAŽE řádek bloku 8h           → musí hlásit ROZCHOD
  C4  v kopii HANDOFFu se PŘEJMENUJE `## 8. Vlastní omyly` → 8 bloků musí být
      NEZMĚŘENO (žádná naměřená nula), brána nesmí spadnout tracebackem

KAŽDÝ PŘÍPAD OVĚŘUJE MĚŘENOU PODMÍNKU Z DISKU (`overovani` §7.14), a na konci
se ověří SHA-256 obou ORIGINÁLŮ před a po — aby se nezměnil živý dokument.

Použití:  python _analyza\\v3-kronika-stavy.py
Návrat:   0 = brána má tři stavy a živý dokument se nezměnil | 1 = rozchod
"""

import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
BRANA = WS / "_analyza" / "kronika-kontrola.py"
ZIVA_K = WS / "KRONIKA-PROJEKTU.md"
ZIVY_H = WS / "HANDOFF.md"
DOCASNE = WS / "_analyza" / "_v3"


def sha(c: pathlib.Path) -> str:
    return hashlib.sha256(c.read_bytes()).hexdigest()


def spust(kronika: pathlib.Path, handoff: pathlib.Path):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([sys.executable, str(BRANA), str(kronika), str(handoff)],
                       capture_output=True, cwd=str(WS), env=env)
    return r.returncode, (r.stdout + r.stderr).decode("utf-8", "replace")


print("=" * 78)
print("OVĚŘENÍ BRÁNY KRONIKY — má TŘI stavy (zelená / červená / NEZMĚŘENO)?")
print("=" * 78)

sha_k_pred, sha_h_pred = sha(ZIVA_K), sha(ZIVY_H)
print("  SHA-256 PŘED: kronika %s" % sha_k_pred[:16])
print("  SHA-256 PŘED: handoff %s" % sha_h_pred[:16])

kron = ZIVA_K.read_text(encoding="utf-8")
hand = ZIVY_H.read_text(encoding="utf-8")
DOCASNE.mkdir(parents=True, exist_ok=True)

# Kotvy se čtou Z DOKUMENTU, neopisují se (když nejsou, test to řekne).
K_8H = "| **8h** |"
assert K_8H in kron, "v kronice není řádek bloku 8h (%r)" % K_8H
radek_8h = next(l for l in kron.splitlines() if l.startswith(K_8H))
print("  řádek kroniky 8h: %s" % radek_8h.strip())
assert "| **9** |" in radek_8h, "řádek 8h nemá počet 9: %r" % radek_8h

H_8H = "### 8h. Omyly AKČNÍ session"
assert H_8H in hand, "v HANDOFFu není nadpis bloku 8h"

# ⚠ DIAGNOSTIKA, KTERÁ ODHALILA REZIDUUM H17: brána testuje PŘÍTOMNOST kotvy
# jiným predikátem (`od in hand` = kdekoliv v textu), než jakým ji PAK HLEDÁ
# (`radek.startswith(od)` = začátek řádku). Kde se ta dvě čísla rozejdou,
# vrátí brána `""` → a vypíše to jako NAMĚŘENOU NULU (vada H17 v užší podobě).
ANCHORY = ["## 8. Vlastní omyly", "### 8b. Omyly ověřovací session",
           "### 8c. Omyly session 2. 10. 2026", "### 8d. Omyly PLÁNOVACÍ session",
           "### 8e. Omyly AKČNÍ session", "### 8f. Omyly PLÁNOVACÍ",
           "### 8g. Omyly PLÁNOVACÍ", "### 8h. Omyly AKČNÍ session"]
print("  kotva                                 kdekoliv / na začátku řádku")
for a in ANCHORY:
    kdekoliv = hand.count(a)
    na_radku = sum(1 for l in hand.splitlines() if l.startswith(a))
    znak = "   <-- ROZEŠLO SE" if kdekoliv != na_radku else ""
    print("    %-36s %d / %d%s" % (a, kdekoliv, na_radku, znak))
print()

vysledky = []


def zaznam(popis, kod, v, podminka_ok, detail):
    vysledky.append((popis, kod, podminka_ok, detail))
    print("  exit=%d  %s" % (kod, "PODMÍNKA SEDÍ" if podminka_ok else "!! PODMÍNKA NESEDÍ"))
    for l in v.splitlines():
        if ("CHYBA" in l or "NEZMĚŘENO" in l or "skutečný počet omylů" in l
                or "ROZCHOD" in l or "KRONIKA SEDÍ" in l):
            print("     %s" % l.strip()[:140])
    print("     → %s" % detail)
    print()


# ------------------------------------------------------------------ Z) kontrola
print("-" * 78)
print("Z) KONTROLA — živá kronika + živý HANDOFF (musí projít)")
print("-" * 78)
kod, v = spust(ZIVA_K, ZIVY_H)
zaznam("Z kontrola", kod, v, kod == 0, "očekáván exit 0")

# --------------------------------------------------- C1) ÚKOL 1.5 — počet 99
print("-" * 78)
print("C1) ÚKOL 1.5 — v KOPII kroniky počet u 8h na 99 (musí SPADNOUT)")
print("-" * 78)
c1 = kron.replace(radek_8h, radek_8h.replace("| **9** |", "| **99** |"), 1)
assert c1 != kron and "| **99** |" in c1, "C1: mutace se neprovedla"
kc1 = DOCASNE / "KRONIKA-c1.md"
kc1.write_bytes(c1.encode("utf-8"))
assert kc1.read_text(encoding="utf-8") == c1, "C1: zápis nesedí"
kod, v = spust(kc1, ZIVY_H)
podm = kod != 0 and re.search(r"blok 8h: kronika tvrdí 99 omylů, v HANDOFF\.md je 9", v)
zaznam("C1 počet 8h=99", kod, v, bool(podm),
       "hláška o rozchodu bloku 8h s čísly 99 vs. 9" if podm else "HLÁŠKA NENÍ")

# ------------------------------------- C2) chybějící NADPIS bloku v HANDOFFu
print("-" * 78)
print("C2) chybějící nadpis bloku 8h → musí hlásit NEZMĚŘENO, ne naměřenou nulu")
print("-" * 78)
c2 = hand.replace(H_8H, "### 8h. Omylů AKČNÍ session (nadpis přejmenován)", 1)
assert c2 != hand and H_8H not in c2, "C2: mutace se neprovedla"
hc2 = DOCASNE / "HANDOFF-c2.md"
hc2.write_bytes(c2.encode("utf-8"))
assert hc2.read_text(encoding="utf-8") == c2, "C2: zápis nesedí"
kod, v = spust(ZIVA_K, hc2)
ma_nezmereno = "NEZMĚŘENO" in v
ma_nulu = bool(re.search(r"8h\s+skutečný počet omylů:\s+0\b", v))
podm = kod != 0 and ma_nezmereno and not ma_nulu
zaznam("C2 chybí nadpis 8h", kod, v, podm,
       "NEZMĚŘENO=%s, naměřená nula u 8h=%s" % (ma_nezmereno, ma_nulu))

# ------------------------------------------- C3) blok v HANDOFFu, řádek chybí
print("-" * 78)
print("C3) blok 8h je v HANDOFFu, ale v kronice §3 řádek NEMÁ (musí být ROZCHOD)")
print("-" * 78)
c3 = kron.replace(radek_8h + "\n", "", 1)
assert c3 != kron and "| **8h** |" not in c3, "C3: mutace se neprovedla"
kc3 = DOCASNE / "KRONIKA-c3.md"
kc3.write_bytes(c3.encode("utf-8"))
kod, v = spust(kc3, ZIVY_H)
# ⚠ PODMÍNKA OPRAVENA (první verze měřila něco jiného): hláška brány zní
# „…(9 omylů), ale v tabulce kroniky §3 řádek NEMÁ — nepočítal by se".
# Můj první vzor čekal slovo „CHYBÍ" a max. 40 znaků mezi tím — což je
# TVAR, ne VÝZNAM (`overovani` §8.3). Správně se hledá to, co brána tvrdí.
podm = kod != 0 and re.search(r"blok 8h je v HANDOFF\.md \(9 omylů\).{0,120}?řádek NEMÁ", v, re.S)
zaznam("C3 chybí řádek v kronice", kod, v, bool(podm),
       "ROZCHOD pojmenován" if podm else "ROZCHOD SE NEHLÁSÍ")

# ------------------------------------------- C4) přejmenovaný HLAVNÍ nadpis §8
print("-" * 78)
print("C4) přejmenovaný `## 8. Vlastní omyly` → 1 blok NEZMĚŘENO, bez tracebacku")
print("-" * 78)
H_8 = "## 8. Vlastní omyly"
assert H_8 in hand, "v HANDOFFu není nadpis %r" % H_8
# ⚠ MUTACE OPRAVENA: první verze přidala za kotvu příponu
# („## 8. Vlastní omyly (nadpis přejmenován)") — a to kotvu NEVYPNE, protože
# kotva je PREFIX a `startswith` ji pořád najde. Naměřeno: brána správně
# změřila 13 a MŮJ TEST hlásil „rozchod" na správném chování souboru
# (tatáž třída jako omyl 80 — falešný poplach na správném souboru).
# Kotva se musí změnit na ZAČÁTKU, ne na konci.
c4 = hand.replace(H_8, "## 8. Moje omyly (kotva přejmenována)", 1)
assert c4 != hand and "## 8. Vlastní omyly" not in c4, "C4: kotva se nezměnila na začátku"
hc4 = DOCASNE / "HANDOFF-c4.md"
hc4.write_bytes(c4.encode("utf-8"))
kod, v = spust(ZIVA_K, hc4)
pocet_nezm = v.count("NEZMĚŘENO")
traceback = "Traceback" in v
jiny_bloky = all(("%-8s skutečný počet omylů: %3d" % (n, c)) in v
                 for n, c in (("8b", 10), ("8e", 11), ("8h", 9)))
podm = kod != 0 and pocet_nezm >= 1 and not traceback and jiny_bloky
zaznam("C4 chybí nadpis §8", kod, v, podm,
       "NEZMĚŘENO=%d, ostatní bloky změřeny=%s, traceback=%s"
       % (pocet_nezm, jiny_bloky, traceback))

# ------------------- C5) REZIDUUM H17: kotva zmizí jako NADPIS, zůstane v PRÓZE
print("-" * 78)
print("C5) nadpis 8g přejmenován, ale kotva zůstává CITOVANÁ v próze omylu 76")
print("-" * 78)
# Tenhle případ je dosažitelný právě proto, že si projekt své kotvy CITUJE
# v textu (omyl 76). Brána ale přítomnost testuje jako `od in hand` (kdekoliv)
# a extrakci dělá přes `startswith` (začátek řádku) — když se to rozejde,
# vrátí `blok_do_nadpisu` prázdný řetězec a `pocet_omylu("")` vrátí 0.
H_8G = "### 8g. Omyly PLÁNOVACÍ"
assert hand.count(H_8G) == 2, "kotva 8g není v HANDOFFu 2x (naměřeno %d)" % hand.count(H_8G)
c5 = hand.replace(H_8G, "### 8g. Omylů PLÁNOVACÍ (kotva přejmenována)", 1)
assert c5 != hand, "C5: mutace se neprovedla"
assert c5.count(H_8G) == 1, "C5: v próze kotva zůstat MĚLA (zbylo %d)" % c5.count(H_8G)
assert not any(l.startswith(H_8G) for l in c5.splitlines()), \
    "C5: žádný řádek teď kotvou nezačíná (což je měřená podmínka)"
hc5 = DOCASNE / "HANDOFF-c5.md"
hc5.write_bytes(c5.encode("utf-8"))
kod, v = spust(ZIVA_K, hc5)
ma_nezmereno = bool(re.search(r"8g\s+nadpis bloku NENALEZEN → NEZMĚŘENO", v))
ma_nulu = bool(re.search(r"8g\s+skutečný počet omylů:\s+0\b", v))
podm = kod != 0 and ma_nezmereno and not ma_nulu
zaznam("C5 kotva jen v próze", kod, v, podm,
       "NEZMĚŘENO=%s, NAMĚŘENÁ NULA=%s%s"
       % (ma_nezmereno, ma_nulu,
          " ← REZIDUUM H17 (brána tvrdí „je 0“, ačkoli blok v dokumentu JE)"
          if ma_nulu else ""))

# ------------------------------------------------------------------- úklid
shutil.rmtree(DOCASNE, ignore_errors=True)

# ------------------------------------------- original se NESMÍ změnit
sha_k_po, sha_h_po = sha(ZIVA_K), sha(ZIVY_H)
print("=" * 78)
print("VYHODNOCENÍ")
print("=" * 78)
print("  SHA-256 PO:   kronika %s  %s" % (sha_k_po[:16],
                                         "BEZ ZMĚNY" if sha_k_po == sha_k_pred else "ZMĚNĚNA!"))
print("  SHA-256 PO:   handoff %s  %s" % (sha_h_po[:16],
                                         "BEZ ZMĚNY" if sha_h_po == sha_h_pred else "ZMĚNĚN!"))
print()
chyby = []
if sha_k_po != sha_k_pred:
    chyby.append("KRONIKA-PROJEKTU.md se změnila — mutace utekla z kopie!")
if sha_h_po != sha_h_pred:
    chyby.append("HANDOFF.md se změnil — mutace utekla z kopie!")
for popis, kod, ok, detail in vysledky:
    print("  %-28s exit=%-3d %s   (%s)" % (popis, kod, "OK" if ok else "ROZCHOD", detail))
    if not ok:
        chyby.append("%s: %s" % (popis, detail))
print()
if chyby:
    print("NALEZENO %d ROZCHODŮ:" % len(chyby))
    for c in chyby:
        print("  CHYBA %s" % c)
    sys.exit(1)
print("BRÁNA MÁ TŘI STAVY — chybějící blok hlásí NEZMĚŘENO, ne naměřenou nulu;")
print("živý dokument se přitom nezměnil (SHA-256 před = po).")
sys.exit(0)
