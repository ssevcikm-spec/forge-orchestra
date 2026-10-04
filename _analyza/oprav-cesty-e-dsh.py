#!/usr/bin/env python3
"""Odstrani zastaralou konstantu E:\\DSH\\data\\sessions ze skriptu.

PROC: `E:\\DSH` je oznacene ke smazani. Konstanta je ale i tak REDUNDANTNI —
`~/.dsh/sessions` je junction a `realpathSync` ho prelozi na stejne misto.
Odstranenim se cesty prestanou rozchazet a skripty preziji smazani.

Pouziva DOSLOVNE nahrady (ne regex) — u cesty s backslashe je to jedina
bezpecna varianta. Zapisuje bajty (UTF-8), aby se nerozbila diakritika.

Nenulovy exit, kdyz neco zbyde nebo se neco nenajde -> test umi selhat.
"""
import sys
from pathlib import Path

B = chr(92)          # jeden backslash
Q = chr(39)          # apostrof

KONST = Q + "E:" + B * 2 + "DSH" + B * 2 + "data" + B * 2 + "sessions" + Q
DOTSH = Q + "C:" + B * 2 + "Users" + B * 2 + "Ssevc" + B * 2 + ".dsh" + B * 2 + "sessions" + Q

NAHRADY = [
    # A) findLogs(join(home,'sessions'), seen), ...findLogs(KONST, seen)]
    (", ...findLogs(" + KONST + ", seen)", ""),
    # B) roots = [join(home, 'sessions'), KONST]
    ("[join(home, 'sessions'), " + KONST + "]", "[join(home, 'sessions')]"),
    # C) roots = [DOTSH, KONST]
    ("[" + DOTSH + ", " + KONST + "]", "[" + DOTSH + "]"),
    # D) c.push(KONST, DOTSH)
    ("c.push(" + KONST + ", " + DOTSH + ")", "c.push(" + DOTSH + ")"),
    # E) report.mjs: fallback pres DSH_DATA_HOME ?? KONST  -> jen DSH_HOME (pres junction)
    ("process.env.DSH_DATA_HOME ?? " + KONST, "join(home, 'sessions')"),
]

CILE = (
    sorted(Path(r"C:\Users\Ssevc\Local-Deepseek\_analyza").glob("*.mjs"))
    + [
        Path(r"C:\Users\Ssevc\.dsh\skills\dsh-usage\report.mjs"),
        Path(r"C:\Users\Ssevc\.dsh\skills\dsh-usage\analyza.mjs"),
    ]
)

print("=" * 72)
print("ODSTRANENI KONSTANTY  E:\\DSH\\data\\sessions")
print("=" * 72)

zmenene, beze_zmeny, nenalezeno = [], [], []

for cesta in CILE:
    if not cesta.exists():
        nenalezeno.append(str(cesta))
        continue
    puvodni = cesta.read_bytes().decode("utf-8")
    novy = puvodni
    pouzite = []
    for i, (stary, novy_str) in enumerate(NAHRADY):
        if stary in novy:
            novy = novy.replace(stary, novy_str)
            pouzite.append("ABCDE"[i])
    if novy == puvodni:
        beze_zmeny.append(cesta.name)
        continue
    cesta.write_bytes(novy.encode("utf-8"))
    zmenene.append((cesta, pouzite))

for cesta, pouzite in zmenene:
    print(f"  ZMENENO [{'+'.join(pouzite)}]  {cesta}")

if beze_zmeny:
    print(f"\n  beze zmeny ({len(beze_zmeny)}): {', '.join(beze_zmeny)}")
if nenalezeno:
    print(f"\n  NENALEZENO ({len(nenalezeno)}):")
    for n in nenalezeno:
        print(f"    {n}")

print()
print("=" * 72)
print("KONTROLA: zbyla nekde konstanta?")
print("=" * 72)
zbytky = []
for cesta in CILE:
    if not cesta.exists():
        continue
    for i, radek in enumerate(cesta.read_bytes().decode("utf-8").splitlines(), 1):
        if "E:" + B * 2 + "DSH" in radek:
            zbytky.append(f"  {cesta.name}:{i}: {radek.strip()}")
if zbytky:
    print("  ZBYTEK (vady):")
    for z in zbytky:
        print(z)
else:
    print("  OK - zadny vyskyt konstanty")

print()
print(f"Zmeneno: {len(zmenene)}   Beze zmeny: {len(beze_zmeny)}   Nenalezeno: {len(nenalezeno)}")
sys.exit(1 if (zbytky or nenalezeno) else 0)
