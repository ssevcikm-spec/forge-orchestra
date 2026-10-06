# -*- coding: utf-8 -*-
"""Prepocet hlavicky zadani: radek se stavem repu MUSI mit tvar `<repo> = <sha>`.

PROC: `_analyza/zadani-kontrola.py` bere tvrzeny commit z PRVNiHO radku, ktery
obsahuje text „Stav obou repu“, a vzorem `` `<repo>` = `<sha>` `` z nej vytahne
dvojice. Kdyz je na tom radku jen popis (a dvojice je na radku dalsim), hlasi
`zadani netvrdi zadny commit` a `exit 1` — coz vypada jako vada brany, ale je to
vada ZAPISU (a presne to se stalo pri psani tohohle zadani).

Skript je idempotentni a zapisuje bajty (LF).
"""
import io
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
P = WS / "NEXT-SESSION-INSTRUKCE.md"
VZOR = r"`?([A-Za-z0-9_-]+)`?\s*=\s*`?([0-9a-f]{7,40})`?"

puvodni = P.read_bytes()
L = puvodni.decode("utf-8").splitlines(keepends=True)

kandidati = [i for i, l in enumerate(L[:30]) if "Stav obou rep" in l]
print("radky se 'Stav obou rep':", [i + 1 for i in kandidati])
for i in kandidati:
    print(f"  radek {i+1}: shody={re.findall(VZOR, L[i])}")

i = kandidati[0] if kandidati else None
if i is None:
    print("CHYBA: radek se stavem repu v hlavicce neni")
    sys.exit(1)

if re.findall(VZOR, L[i]):
    print("OK: radek uz dvojice obsahuje — neměním")
    sys.exit(0)

# Najdi nasledujici radek s obema dvojicemi a PRESUN dvojice do radku s klicem.
j = next((n for n in range(i + 1, min(i + 6, len(L))) if len(re.findall(VZOR, L[n])) >= 2), None)
if j is None:
    print("CHYBA: v hlavicce neni radek s DVOJICI `<repo> = <sha>` — nedoplnim to odhadem")
    sys.exit(1)

dvojice = " · ".join(f"`{r}` = `{s}`" for r, s in re.findall(VZOR, L[j]))
klic = L[i].rstrip("\n").rstrip()
# Popis v zavorce na konci klice NENI duvod, proc veta existuje — odstranime ho.
klic = re.sub(r"\s*\(tvar čte [^)]*\)", "", klic)
L[i] = f"{klic} {dvojice}\n"
L[j] = ""
print("novy radek:", repr(L[i]))

nove = "".join(L).encode("utf-8")
P.write_bytes(nove)
text = P.read_bytes().decode("utf-8")
print("shody na klicovem radku po zapisu:",
      re.findall(VZOR, text.splitlines()[i]))
print("znaku:", len(puvodni), "->", len(nove))
print("LF ok:", b"\r\n" not in nove, "| BOM:", nove[:3] == b"\xef\xbb\xbf")
