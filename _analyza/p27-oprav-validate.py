# -*- coding: utf-8 -*-
r"""P27 — OPRAVA NEPRAVDIVÉHO TVRZENÍ O `validate-all`.

NAMĚŘENO 8. 10. 2026 (závěrečné brány, čerstvý inventář):
  * `g3` → 49 bran, **2 nenulové exity, oba NEDEKLAROVANÉ a oba MIMO REPO**
    (`over-skilly` + její mutační dvojče) → `exit 1`
  * `validate-all` → **✓ VŠE V POŘÁDKU** (`exit 0`) — `over-skilly` v ní **NENÍ**

Zapsal jsem ale, že `validate-all` **padá na `over-skilly`** — což je
**nepravda**. Jeho dřívější pád (12:0x) způsobil **ZASTARALÝ INVENTÁŘ** (můj
log mimo vylučovací vzor), ne skill. Opravuje se v `HANDOFF.md` §57,
`KRONIKA` §2.20 (P27-R) a v `NEXT-SESSION-INSTRUKCE.md`.

Použití: python _analyza/p27-oprav-validate.py
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
H = WS / "HANDOFF.md"
K = WS / "KRONIKA-PROJEKTU.md"
Z = WS / "NEXT-SESSION-INSTRUKCE.md"

kontrol = 0
chyb = []


def k(ok, popis):
    global kontrol
    kontrol += 1
    print("  %s  %s" % ("OK  " if ok else "CHYBA", popis))
    if not ok:
        chyb.append(popis)


def vymen(cesta, dvojice, popis):
    t = cesta.read_text(encoding="utf-8")
    for stary, novy in dvojice:
        n = t.count(stary)
        if n != 1:
            k(False, "%s: kotva %d× (musí 1×): %r" % (popis, n, stary[:70]))
            continue
        t = t.replace(stary, novy, 1)
        print("      %s: OK %r" % (popis, stary[:60]))
    cesta.write_bytes(t.encode("utf-8"))
    k(True, "%s: zapsáno" % popis)


vymen(H, [
    ("`validate-all` → **NENÍ zelený, padá na `over-skilly`** (týž stav)",
     "`validate-all` → **VŠE V POŘÁDKU** (exit 0; `over-skilly` v ní **není**)"),
    ("brány:     g3 → 49 bran; 2 NEDEKLAROVANÉ exity, oba MIMO REPO (`over-skilly`\n           a její mutační dvojče) → exit 1; validate-all padá na TÝŽ stav\n           (cizí session přepsala SKILL `game-developer`, mtime 11:22)",
     "brány:     g3 → 49 bran; 2 NEDEKLAROVANÉ exity, oba MIMO REPO (`over-skilly`\n           a její mutační dvojče) → exit 1 · validate-all → VŠE V POŘÁDKU\n           (exit 0; `over-skilly` v něm NENÍ) — cizí stav: session přepsala\n           SKILL `game-developer` (mtime 11:22)"),
], "HANDOFF")

vymen(K, [
    ("Kaskádou shodí `g3` (2 nedeklarované exity), `validate-all`, `p24-a` A6, `p25-a` A4, `p26-a` (90 → 85 kontrol) i `p26-b` (diferenciál M3a).",
     "Kaskádou shodí `g3` (2 nedeklarované exity), `p24-a` A6, `p25-a` A4, `p26-a` (90 → 85 kontrol) i `p26-b` (diferenciál M3a) — **`validate-all` je přitom ZELENÝ** (`over-skilly` v něm není; jeho dřívější pád způsobil **zastaralý inventář**, nález P27-S)."),
], "KRONIKA")

vymen(Z, [
    ("`g3` → **49 bran**; **2 nedeklarované exity, oba MIMO REPO** (`over-skilly` + její mutační dvojče) → **exit 1**; `validate-all` **NENÍ zelený** (týž stav);",
     "`g3` → **49 bran**; **2 nedeklarované exity, oba MIMO REPO** (`over-skilly` + její mutační dvojče) → **exit 1**; `validate-all` → **VŠE V POŘÁDKU** (`over-skilly` v něm není);"),
    ("**49 bran / 2 nedeklarované exity MIMO REPO / exit 1**, `validate-all` **NENÍ\nzelený** (týž cizí stav),",
     "**49 bran / 2 nedeklarované exity MIMO REPO / exit 1**, `validate-all` → **VŠE\nV POŘÁDKU** (`over-skilly` v něm není),"),
], "ZADÁNÍ")

print()
print("=" * 78)
for p, popis in ((H, "HANDOFF"), (K, "KRONIKA"), (Z, "ZADÁNÍ")):
    t = p.read_text(encoding="utf-8")
    k("padá na `over-skilly`" not in t and "NENÍ zelený" not in t,
      "%s už netvrdí, že validate-all padá" % popis)
    k("VŠE V POŘÁDKU" in t, "%s tvrdí, že validate-all je v pořádku" % popis)
    b = p.read_bytes()
    k(b.count(b"\r\n") == 0 and not b.startswith(b"\xef\xbb\xbf"),
      "%s: LF a bez BOM" % popis)
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
for c in chyb:
    print("  CHYBA: %s" % c)
sys.exit(1 if chyb else 0)
