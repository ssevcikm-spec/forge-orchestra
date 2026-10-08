# -*- coding: utf-8 -*-
r"""P27 (dodatek) — ZÁZNAM ROZHODNUTÍ UŽIVATELE do `PLAN-ROZVOJ-ORCHESTRA.md` §6.

Uživatel 8. 10. 2026 rozhodl (doslovně): „2 podle tvého doporučení“ (skill/rozsah
brány), „Uprav strop granulí podle sebe“, „B5 … Můžeš určit ty?“, „O10 souhlasím“,
„O5 souhlasím“, „O6 souhlasím“, „O7 jaká druhá hra?“, „O8 … klidně jako celek, ale
pokud vývoj prvních bodů ovlivní dojem nebo realizaci těch dalších, tak postupně“,
„O9 ano hned“.

Ten skript mění JEN stavový sloupec §6 (plán se přepisuje — je to plán, ne kronika)
a přidává k `B3` větu o nasazení stropu. Nic nemaže: texty otázek zůstávají.

Použití: python _analyza/p27-plan-rozhodnuti.py
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
PLAN = WS / "PLAN-ROZVOJ-ORCHESTRA.md"

kontrol = 0
chyb = []


def k(ok, popis):
    global kontrol
    kontrol += 1
    print("  %s  %s" % ("OK  " if ok else "CHYBA", popis))
    if not ok:
        chyb.append(popis)


D = "8. 10. 2026"

# (kotva, nový text) — kotva je CELÝ řádek tabulky, aby se neměnilo nic jiného
ZMENY = [
    ("| **O3** | Mám opravit vady conductoru? | ⏳ **ČEKÁ — a je to fáze B** |",
     f"| **O3** | Mám opravit vady conductoru? | ✅ **ZODPOVĚZENO A NASAZENO {D}** (P27) |"),
    ("| **O5** | Cesty v `forge.config.json`, nebo konvencí? | ⏳ **ČEKÁ** |",
     f"| **O5** | Cesty v `forge.config.json`, nebo konvencí? | ✅ **ZODPOVĚZENO {D}** (P27, uživatel: „souhlasím“) |"),
    ("| **O6** | Které soubory **patří hře**? | ⏳ **ČEKÁ (věcné rozhodnutí uživatele)** |",
     f"| **O6** | Které soubory **patří hře**? | ✅ **ZODPOVĚZENO {D}** (P27, uživatel: „souhlasím“) |"),
    ("| **O7** | Druhá hra reálná, nebo testovací? | ⏳ **ČEKÁ** |",
     f"| **O7** | Druhá hra reálná, nebo testovací? | ⏳ **ODLOŽENO S PRAVIDLEM {D}** (P27) |"),
    ("| **O8** | Fáze schvalovat jednotlivě, nebo F0–F2 jako celek? | ⏳ **ČEKÁ** |",
     f"| **O8** | Fáze schvalovat jednotlivě, nebo F0–F2 jako celek? | ✅ **ZODPOVĚZENO {D}** (P27, uživatel) |"),
    ("| **O9** | **NOVÉ:** Opravit `NAZEV-REPA` hned (`${{ github.repository }}`), nebo až v rámci onboardingu? | ⏳ **ČEKÁ** |",
     f"| **O9** | **NOVÉ:** Opravit `NAZEV-REPA` hned (`${{ github.repository }}`), nebo až v rámci onboardingu? | ✅ **HOTOVO A OVĚŘENO {D}** (P27) |"),
    ("| **O10** | **NOVÉ:** Má být **ST9-část** (testy conductora čtou SQL ze zdrojáku) součástí fáze B, ne až F2? | ⏳ **ČEKÁ** |",
     f"| **O10** | **NOVÉ:** Má být **ST9-část** (testy conductora čtou SQL ze zdrojáku) součástí fáze B, ne až F2? | ✅ **ZODPOVĚZENO {D}** (P27, uživatel: „souhlasím“) |"),
]

text = PLAN.read_text(encoding="utf-8")
for kotva, novy in ZMENY:
    najdi = [l for l in text.splitlines() if l.startswith(kotva)]
    if len(najdi) != 1:
        k(False, "kotva %d× pro: %s" % (len(najdi), kotva[:50]))
        continue
    stary_radek = najdi[0]
    # ⚠ MĚNÍ SE JEN SLOUPEC STAVU — text otázky i odůvodnění zůstávají
    casti = stary_radek.split("|")
    if len(casti) < 5:
        k(False, "řádek nemá očekávaný tvar: %s" % stary_radek[:60])
        continue
    novy_radek = "|".join(casti[:3] + [" " + novy.split("|")[3].strip() + " "] + casti[4:])
    text = text.replace(stary_radek, novy_radek, 1)
    k(True, "stav přepsán: %s" % kotva[:46])

# ── B3: doplnit, že strop je ZAPNUTÝ a nasazený ────────────────────────────
DOPLNENI_B3 = (" | a **8. 10. 2026 strop ZAPNUT na `\"8\"` a NASAZEN** "
               "(push `07169c7` → `deploy.yml` #34 `success`) — ověřeno živě: "
               "`/health` ok, `/roadmap` 21 granul, **0 blokovaných** (strop "
               "blokuje až od 8 běhů) |")
if "strop ZAPNUT na" not in text:
    m = re.search(r"^(\| \*\*B3\*\* \|.*)$", text, re.M)
    if m:
        text = text[:m.end()] + DOPLNENI_B3 + text[m.end():]
        k(True, "B3: doplněno nasazení stropu")
    else:
        k(False, "řádek B3 nenalezen")
else:
    k(True, "B3 už nasazení stropu zmiňuje")

# ── nový odstavec: rozhodnutí B5 (rozsah brány) ─────────────────────────────
if "ROZHODNUTÍ B5" not in text:
    kotva = "\n## 7. "
    blok = (
        "\n### 6.1 ROZHODNUTÍ B5 — ROZSAH BRÁNY `over-skilly` (8. 10. 2026, P27)\n\n"
        "**Otázka:** které cesty má brána `tools/over-skilly.py` měřit a proti kterému\n"
        "projektu? Uživatel ji delegoval na agenta („Nevím podle čeho B5 rozhodnout.\n"
        "Nerozumíš tomu lépe? Můžeš určit ty?“), takže rozhodnutí je tady **zapsané\n"
        "i s důvodem**, aby se za měsíc nehádalo, proč to tak je.\n\n"
        "**Naměřeno před rozhodnutím:** skill `game-developer` (STANIČNÍ, přepsaný cizí\n"
        "session) odkazuje na `tools/plan-status.py` a `tools/roadmap-gen.py`; ty\n"
        "existují v sourozenci `E:\\Workspaces\\game-clone`, ale brána znala jen\n"
        "orchestra + hru → hlásila **3 mrtvé cesty** a shodila `g3` (2 nedeklarované\n"
        "exity). To je **falešný poplach** — a ten nutil „opravovat“ správný text.\n\n"
        "**ROZHODNUTÍ:** skilly jsou **STANIČNÍ**, ne projektové. Cesta se proto uzná,\n"
        "když existuje v orchestře, ve hře, **nebo v některém sourozeneckém projektu**\n"
        "(adresář v `REPO.parent` s `.git`). **Skutečně mrtvá cesta (nikde) bránu dál\n"
        "SHODÍ** — o to jde. A co se našlo mimo orchestra/hru, brána **vypíše jako\n"
        "poznámku** (rozsah musí být VIDĚT; tiché rozšíření rozsahu je táž vada, jakou\n"
        "popisuje P25-K).\n\n"
        "**Druhá část rozhodnutí:** slepé místo z `HANDOFF.md` §51.3 (brána měřila jiný\n"
        "tvar cest, než dokumenty používají) zůstává **otevřené jako samostatná práce**\n"
        "— dnešní oprava řeší **rozsah**, ne tvar cest.\n"
    )
    if kotva in text:
        text = text.replace(kotva, blok + kotva, 1)
        k(True, "§6.1 s rozhodnutím B5 vložen před §7")
    else:
        text = text.rstrip("\n") + "\n" + blok
        k(True, "§6.1 s rozhodnutím B5 připojen na konec")

PLAN.write_bytes(text.encode("utf-8"))
t2 = PLAN.read_text(encoding="utf-8")
k(t2.count("✅ **ZODPOVĚZENO A NASAZENO 8. 10. 2026**") == 1, "O3 je zodpovězené")
k("ROZHODNUTÍ B5" in t2, "rozhodnutí B5 je v plánu")
k("strop ZAPNUT na" in t2, "B3 nese nasazení stropu")
for kotva in ("| **O5** |", "| **O6** |", "| **O7** |", "| **O8** |",
              "| **O9** |", "| **O10** |"):
    k(kotva in t2, "řádek %s zůstal" % kotva)
k(t2.count("\r\n") == 0 and not t2.startswith("\ufeff"), "plán: LF a bez BOM")

print()
print("=" * 78)
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
for c in chyb:
    print("  CHYBA: %s" % c)
sys.exit(1 if chyb else 0)
