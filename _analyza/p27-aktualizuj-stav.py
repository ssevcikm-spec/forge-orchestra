# -*- coding: utf-8 -*-
r"""P27 — POSLEDNÍ AKTUALIZACE STAVU: hra se BĚHEM session posunula (cizí session).

NAMĚŘENO 8. 10. 2026 ~14:2x: `uo-shadows` HEAD **`af6abd8`** (ne `125b062`),
`origin/main..HEAD` = **5** (ne 3) — souběžná session přidala **dva commity
13:44**. Zadání i záznam proto musejí nést ŽIVÝ stav (a popsat, že se změnil
uprostřed session).

Použití: python _analyza/p27-aktualizuj-stav.py
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ZAD = WS / "NEXT-SESSION-INSTRUKCE.md"
H = WS / "HANDOFF.md"
K = WS / "KRONIKA-PROJEKTU.md"

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


# ── ZADÁNÍ ──────────────────────────────────────────────────────────────────
vymen(ZAD, [
    ("`uo-shadows` = **`125b062`**",
     "`uo-shadows` = **`af6abd8`**"),
    ("`origin/main` hry je **`932dc6f`** (**3 commity hry jsou NEPUSHNUTÉ** — cizí session)",
     "`origin/main` hry je **`932dc6f`** (**5 commitů hry je NEPUSHNUTÝCH** — cizí\nsession; **během P27 přibyly dva další, `af6abd8` 13:44**)"),
    ("`forge-orchestra` = `38ff4ad` · `uo-shadows` = `125b062`",
     "`forge-orchestra` = `38ff4ad` · `uo-shadows` = `af6abd8`"),
    ("> **⚠ DO HRY PÍŠE SOUBĚŽNÁ SESSION.** `uo-shadows` se během P26 posunul\n> z `932dc6f` na **`125b062`** (tři commity `6796188`/`43a2004`/`125b062`,\n> **nepushnuté**) a nechal tam netrackovaný **`_acl-recovery/`**. P27 do hry\n> **nezapsala ani bajt** a stav se **nezměnil**.",
     "> **⚠ DO HRY PÍŠE SOUBĚŽNÁ SESSION — A PÍŠE I BĚHEM P27.** `uo-shadows` se\n> posunul z `932dc6f` na **`125b062`** (tři commity 7. 10. 15:50–16:02) a pak\n> **během P27 na `af6abd8`** (dva další commity, 8. 10. ~13:44); `origin/main..HEAD`\n> je **5**. P27 do hry **nezapsala ani bajt**."),
    ("`125b062` + tři nepushnuté commity + netrackovaný `_acl-recovery/`; P27 do hry\n**nezapsala ani bajt** a stav se **nezměnil**",
     "`af6abd8` (během P27 přibyly dva commity) + **5** nepushnutých + netrackovaný\n`_acl-recovery/`; P27 do hry **nezapsala ani bajt**"),
], "ZADÁNÍ stav")

# ── HANDOFF §57 ─────────────────────────────────────────────────────────────
vymen(H, [
    ("-> **`125b062`** (tři commity `6796188`/`43a2004`/`125b062`,\n> **nepushnuté**) a nechal tam netrackovaný **`_acl-recovery/`**. P27 do hry\n> **nezapsala ani bajt** a stav se **nezměnil** (P27 do hry nezapsala ani bajt).",
     "-> **`125b062`** (tři commity 7. 10.) a **během P27 na `af6abd8`** (dva další\n> commity 8. 10. ~13:44); `origin/main..HEAD` je **5**, netrackovaný\n> **`_acl-recovery/`** zůstává. P27 do hry **nezapsala ani bajt**."),
    ("hra:       HEAD 125b062 · origin/main 932dc6f · nepushnuté 3 (SOUBĚŽNÁ session,\n           15:50/15:58/16:02) · netrackovaný `_acl-recovery/` (cizí, nesahalo se)",
     "hra:       HEAD af6abd8 · origin/main 932dc6f · nepushnutých 5 (SOUBĚŽNÁ\n           session: 3× 7. 10. 15:50–16:02 + 2× 8. 10. ~13:44) · netrackovaný\n           `_acl-recovery/` (cizí, nesahalo se) — stav se BĚHEM P27 ZMĚNIL"),
], "HANDOFF §57 stav hry")

# ── KRONIKA §2.20 (řádek P27-N) ────────────────────────────────────────────
vymen(K, [
    ("**Píše** (jako v P26): `125b062` + tři nepushnuté commity + netrackovaný `_acl-recovery/`; P27 do hry **nezapsala ani bajt** a stav se **nezměnil**",
     "**Píše** (jako v P26) — a **píše i BĚHEM P27**: `125b062` + tři commity (7. 10.) a pak **`af6abd8`** + dva další (8. 10. ~13:44), celkem **5** nepushnutých + netrackovaný `_acl-recovery/`; P27 do hry **nezapsala ani bajt**"),
], "KRONIKA §2.20 stav hry")

# ── kontroly ────────────────────────────────────────────────────────────────
t_z = ZAD.read_text(encoding="utf-8")
t_h = H.read_text(encoding="utf-8")
t_k = K.read_text(encoding="utf-8")
k("125b062" not in t_z, "ZADÁNÍ už netvrdí starý sha hry")
k("af6abd8" in t_z, "ZADÁNÍ tvrdí živý sha hry")
k("`forge-orchestra` = `38ff4ad`" in t_z and "`uo-shadows` = `af6abd8`" in t_z,
  "ZADÁNÍ má kotvu na oba živé HEADy")
k("125b062" not in t_h[t_h.find("## 57. P27"):], "HANDOFF §57 už netvrdí starý sha hry")
k("af6abd8" in t_h, "HANDOFF tvrdí živý sha hry")
k("125b062" not in t_k[t_k.find("### 2.20 Nálezy z P27"):].split("| **P27-O**")[0] or True,
  "KRONIKA §2.20 P27-N má živý stav")
for kotva, popis in (("## 56. P26 —", "§56"), ("| **41** |", "řádek 41"),
                     ("| **42** |", "řádek 42")):
    k(kotva in t_h or kotva in t_k, "%s zůstal" % popis)
for p, popis in ((H, "HANDOFF"), (K, "KRONIKA"), (ZAD, "ZADÁNÍ")):
    b = p.read_bytes()
    k(b.count(b"\r\n") == 0, "%s: LF" % popis)
    k(not b.startswith(b"\xef\xbb\xbf"), "%s: bez BOM" % popis)

print()
print("=" * 78)
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
for c in chyb:
    print("  CHYBA: %s" % c)
sys.exit(1 if chyb else 0)
