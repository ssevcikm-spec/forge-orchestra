# -*- coding: utf-8 -*-
"""OPATŘENÍ 6 — je ruční seznam v `kontrola-diakritiky.py` nahrazen projitím složky?

Otázka z auditu (§6 opatření 6): soubor má **105 cest a 96 řádků komentářů**;
náhrada „projitím složky" má odstranit vadu S27 („brána je zelená nad
dokumentem, který nikdy neotevřela").

Tenhle skript NENÍ brána — měří POKRYTÍ: které dokumenty v kořeni a v `_analyza`
brána vůbec OTEVŘE, a které zůstanou neviditelné.
"""
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable
BRANA = WS / "orchestra" / "tools" / "kontrola-diakritiky.py"

k = BRANA.read_text(encoding="utf-8")

# 1) Které vzory v bráně vypadají jako SBĚR SOUBORŮ (ne jako seznam)?
print("=" * 88)
print("OPATŘENÍ 6 — POKRYTÍ BRÁNY DIAKRITIKY")
print("=" * 88)
print("\n--- všechny řádky, které sbírají soubory ---")
for i, radek in enumerate(k.splitlines(), 1):
    if re.search(r"glob|rglob|walk|SKUPINY|SEZNAM|SKUPINA|^SOUBORY|cesty|soubory\s*=", radek):
        if not radek.strip().startswith("#"):
            print("  ř.%-4d %s" % (i, radek.rstrip()[:112]))

# 2) Kolik .md cest je vyjmenovaných NA PEVNO
pevne = sorted(set(re.findall(r"[A-Za-z0-9_\-\\/]+\.md", k)))
print("\n--- .md cesty vyjmenované V KÓDU (ne komentáře) ---")
v_kodu = []
for i, radek in enumerate(k.splitlines(), 1):
    if radek.strip().startswith("#"):
        continue
    for m in re.finditer(r"[\w\\/\.\-]+\.md", radek):
        v_kodu.append((i, m.group(0)))
print("  celkem výskytů: %d · různých cest: %d"
      % (len(v_kodu), len({c for _, c in v_kodu})))

# 3) Co brána OTEVŘELA při skutečném běhu
r = subprocess.run([PY, str(BRANA)], cwd=str(WS), capture_output=True, timeout=900)
vystup = r.stdout.decode("utf-8", "replace")
print("\n--- skutečný běh brány ---")
print("  exit=%d" % r.returncode)
for radek in vystup.splitlines():
    if re.search(r"ZMĚŘENO|soubor|otevřel|VŠE OK|vad", radek, re.I):
        print("  %s" % radek.strip()[:118])

# 4) Kolik dokumentů v kořeni a v _analyza brána VIDÍ
koren = {p.name for p in WS.glob("*.md")}
analyza = {p.name for p in (WS / "_analyza").glob("*.md")}
print("\n--- kolik dokumentů existuje vs. je zmíněno v bráně ---")
print("  .md v kořeni workspace      : %d" % len(koren))
print("  .md v _analyza              : %d" % len(analyza))
zminene = {pathlib.PurePath(c).name for _, c in v_kodu}
print("  různých .md jmen v kódu brány: %d" % len(zminene))
chybi_koren = sorted(koren - zminene)
print("  z kořene NENÍ v bráně (%d): %s" % (len(chybi_koren), chybi_koren[:12]))
chybi_an = sorted(analyza - zminene)
print("  z _analyza NENÍ v bráně (%d): %s" % (len(chybi_an), chybi_an[:12]))

# 5) Je nový dokument téhle session v bráně?
print("\n--- nové dokumenty 2. 10. 2026 ---")
for jmeno in ("ZADANI-PO-AUDITU.md", "ZADANI-DOKONCENI-AUDITU.md",
              "NEXT-SESSION-INSTRUKCE.md", "PLAN-DALSI-KROK.md"):
    print("  %-30s v bráně: %s" % (jmeno, "ANO" if jmeno in zminene else "NE"))
print()
