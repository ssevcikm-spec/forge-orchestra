# -*- coding: utf-8 -*-
"""DŮKAZY KE 13 OPATŘENÍM z `_analyza\AUDIT-DOKUMENTACE.md` §6.

Plánovací session 2. 10. 2026. NENÍ brána — je to sběr naměřených faktů
ke každému opatření, aby se u něj dalo rozhodnout „hotovo / ne / čí je to".
"""
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable


def cti(rel):
    return (WS / rel).read_text(encoding="utf-8")


print("=" * 88)
print("DŮKAZY KE 13 OPATŘENÍM (AUDIT-DOKUMENTACE.md §6)")
print("=" * 88)

# ── opatření 1: AGENTS.md:63 značka času ───────────────────────────────────
print("\n[1] `AGENTS.md` řádek se sloupci — má značku času?")
for i, radek in enumerate(cti("AGENTS.md").splitlines(), 1):
    if "sloupc" in radek and ("32" in radek or "39" in radek or "40" in radek):
        print("    ř.%-4d %s" % (i, radek.strip()[:118]))

# ── opatření 2: popisek v ag-over-cisla.py ────────────────────────────────
print("\n[2] `ag-over-cisla.py` — popisek u sloupců D1 (hledá se napevno psané číslo)")
t = cti("_analyza/ag-over-cisla.py")
for i, radek in enumerate(t.splitlines(), 1):
    if "sloupc" in radek and ("D1" in radek or "schema" in radek or "40" in radek or "39" in radek):
        print("    ř.%-4d %s" % (i, radek.strip()[:118]))

# ── opatření 3: rozšířit na řádek 62 ──────────────────────────────────────
print("\n[3] `ag-over-cisla.py` — KTERÉ řádky dokumentu měří (kotvy)")
for i, radek in enumerate(t.splitlines(), 1):
    if re.search(r"AGENTS\.md", radek) and re.search(r"\d{2,3}", radek):
        print("    ř.%-4d %s" % (i, radek.strip()[:118]))
print("    → kolik tvrzení nástroj ověřuje (z běhu):")
r = subprocess.run([PY, "_analyza/ag-over-cisla.py"], cwd=str(WS),
                   capture_output=True, timeout=300)
v = r.stdout.decode("utf-8", "replace")
for radek in v.splitlines():
    if "v pořádku" in radek or "ZMĚŘENO" in radek or "řádků s číslem" in radek:
        print("       %s" % radek.strip())

# ── opatření 4 + 5: HANDOFF.md ────────────────────────────────────────────
print("\n[4][5] `HANDOFF.md` — délka a oddíly §10–§22")
h = cti("HANDOFF.md")
radky = h.splitlines()
print("    řádků: %d · znaků: %d · bajtů: %d" % (len(radky), len(h), len(h.encode("utf-8"))))
for i, radek in enumerate(radky, 1):
    if re.match(r"^## (1[0-9]|2[0-2])\.", radek):
        print("    ř.%-5d %s" % (i, radek[:78]))
print("    → sekce §10–§22 jsou v HANDOFF.md POŘÁD (opatření 5 neprovedeno)")

# ── opatření 6: ruční seznam v kontrola-diakritiky.py ─────────────────────
print("\n[6] `orchestra/tools/kontrola-diakritiky.py` — ruční seznam, nebo projití složky?")
k = cti("orchestra/tools/kontrola-diakritiky.py")
kr = k.splitlines()
print("    řádků: %d" % len(kr))
n_rglob = len(re.findall(r"rglob|\.glob\(|os\.walk", k))
print("    výskytů rglob/.glob(/os.walk: %d" % n_rglob)
for i, radek in enumerate(kr, 1):
    if re.search(r"rglob|\.glob\(|os\.walk", radek):
        print("       ř.%-4d %s" % (i, radek.strip()[:110]))
md_v_seznamu = re.findall(r'"([^"]*\.md)"', k) + re.findall(r"'([^']*\.md)'", k)
print("    .md cest vyjmenovaných v souboru: %d" % len(md_v_seznamu))
print("    → projití složky: %s" % ("ANO" if n_rglob else "NE (pořád ruční seznam)"))

# ── opatření 7: hlavičky dokumentů ────────────────────────────────────────
print("\n[7] Hlavičky dokumentů (z inventáře `audit1-inventar.py`)")
r = subprocess.run([PY, "_analyza/audit1-inventar.py"], cwd=str(WS),
                   capture_output=True, timeout=300)
v = r.stdout.decode("utf-8", "replace")
for radek in v.splitlines():
    if ("dokumentů celkem" in radek or "bez hlavičky" in radek
            or "živých / sirotků" in radek):
        print("       %s" % radek.strip())

# ── opatření 8: verzování dokumentace ─────────────────────────────────────
print("\n[8] Verzování dokumentace — je kořen workspace v git repu?")
r = subprocess.run(["git", "-C", "orchestra", "ls-files", "--error-unmatch", "HANDOFF.md"],
                   cwd=str(WS), capture_output=True, shell=True, timeout=60)
print("    git ls-files HANDOFF.md: %s" % r.stdout.decode("utf-8", "replace").strip()
      or "    (prázdné)")
print("    → exit=%d (nenulový = soubor NENÍ v gitu)" % r.returncode)
for kandidat in (".git", "_analyza/.git"):
    print("    %-16s existuje: %s" % (kandidat, (WS / kandidat).exists()))

# ── opatření 10: brány bez čítače ─────────────────────────────────────────
print("\n[10] Brány, které nic nevykázaly (z `g3-brany-vystup`/běhu g3)")
g3v = WS / "_analyza" / "g3-brany-vystup.txt"
if g3v.is_file():
    txt = g3v.read_text(encoding="utf-8", errors="replace")
    print("    (plný výstup g3: %d znaků)" % len(txt))

# ── opatření 12: mutační testy branám bez důkazu ──────────────────────────
print("\n[12] `audit6-brany-mutace.py` — kolik bran má důkaz")
r = subprocess.run([PY, "_analyza/audit6-brany-mutace.py"], cwd=str(WS),
                   capture_output=True, timeout=1800)
v = r.stdout.decode("utf-8", "replace")
print("    exit=%d" % r.returncode)
for radek in v.splitlines():
    if re.search(r"bez důkazu|ZMĚŘENO|R6|neproběh|NEPROBĚH", radek):
        print("       %s" % radek.strip()[:118])

print()
print("=" * 88)
