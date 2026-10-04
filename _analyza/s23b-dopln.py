r"""Doplněk k zápisu session 19 — tři věci, které odhalily BRÁNY, ne čtení.

CO SE DOPLŇUJE A PROČ
  1. **Označení nálezů H24–H28 v `HANDOFF.md` §23.** `kronika-kontrola.py`
     správně vyžaduje, aby každý nález zapsaný v kronize byl zmíněný
     **i v `HANDOFF.md`** — jinak by nález žil jen v jednom dokumentu.
     Naměřeno: `NALEZENO 5 ROZCHODŮ: nález H24–H28 je v kronice, ale
     v HANDOFF.md není`. Popisy v §23 **byly**, chyběly jen **značky**.
     *(To je přesně ta vada, kterou brána hledá — a chytila ji.)*
  2. **Omyl 94** — falešný poplach mého vlastního ověřovatele v `s23-kronika.py`:
     hlásil „4 řádky zmizely", ale ty čtyři řádky se **ZÁMĚRNĚ aktualizovaly**
     (nesou stará čísla 86 / 65 / 9 / 81). Je to `overovani` §9.6
     („očekávaná nepřítomnost není vada") a zapsání si to zaslouží, protože
     **falešný poplach na správných datech** je horší než slepé místo.
  3. **Přepočet v kronize** podle omylu 94 (blok `8j`: 7 → 8).

Skript nic neodebere; na konci spustí `kronika-kontrola.py`
i `handoff-kontrola-uplnost.py` a skončí `exit 1`, když některá nesedí.

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\s23b-dopln.py
"""
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
K = WS / "KRONIKA-PROJEKTU.md"

# ── 1) Značky nálezů do §23 ────────────────────────────────────────────────
# (starý text, nový text) — každý musí být v souboru právě 1×
ZNAČKY = [
    ("### 23.2 ⚠ NÁLEZ: ZADÁNÍ MĚLO U ÚKOLU 1 NESPLNITELNÉ KRITÉRIUM — a mířilo vedle",
     "### 23.2 ⚠ NÁLEZ **H24**: ZADÁNÍ MĚLO U ÚKOLU 1 NESPLNITELNÉ KRITÉRIUM — a mířilo vedle"),
    ("- **`audit2b` má 27 rozchodů, z toho většina je falešných**",
     "- **NÁLEZ H25 — `audit2b` má 27 rozchodů, z toho většina je falešných**"),
    ("- **`OPATŘENÍ 2 A 3 Z AUDITU NEBYLA ZADÁNÍM PŘIDĚLENA ŽÁDNÉ SESSION** —",
     "- **NÁLEZ H26 — OPATŘENÍ 2 A 3 Z AUDITU NEBYLA ZADÁNÍM PŘIDĚLENA ŽÁDNÉ SESSION** —"),
    ("- **`audit1-inventar.py` viděl 101 dokumentů, z toho 51 v `_analyza`**",
     "- **NÁLEZ H27 (vlastní omyl 92) — SNAPSHOT ZNE Platnil BASELINE INVENTÁŘE.**\n"
     "  `audit-snapshot.py` (opatření 9) kopíruje dokumentaci do\n"
     "  `_analyza\\snapshot-<čas>\\` — a `audit1-inventar.py` ty **kopie začal\n"
     "  počítat jako dokumenty**: naměřeno **159 dokumentů místo 98**, **66 záloh\n"
     "  místo 8**, „bez hlavičky\" **116 z 159** místo **62 z 98**. **Opraveno**\n"
     "  vyloučením předpony `snapshot-` (inventář zpět na **101 / 8 záloh**).\n"
     "  Obecné poučení: **opatření, které něco kopíruje, musí měřidlům říct, že je\n"
     "  to kopie** — viz `KRONIKA-PROJEKTU.md` §5 **L23** a návrh **NA21**.\n"
     "- **`audit1-inventar.py` viděl 101 dokumentů, z toho 51 v `_analyza`**"),
    ("`SOUBEH-SESSION-NALEZY.md`.\n\n> **⚠ A je to nález o ZADÁNÍ, ne jen o souboru:**",
     "`SOUBEH-SESSION-NALEZY.md`.\n\n> **⚠ NÁLEZ H28 — a je to nález o ZADÁNÍ, ne jen o souboru:**"),
]

# ── 2) Omyl 94 do §8j ──────────────────────────────────────────────────────
OMYL_94 = (
    "| **94** | **Můj ověřovatel „nic nezmizelo\" vyrobil FALEŠNÝ POPLACH** — "
    "ohlásil, že v kronize zmizely **4 řádky** | v `s23-kronika.py` jsem po "
    "zápisu porovnával, že každý neprázdný řádek původního textu je i v novém. "
    "Jenže **čtyři řádky se aktualizovaly ZÁMĚRNĚ** — nesou stará čísla "
    "(`86` / `65` / `9` / `81`) a v nové verzi mít **nemají** | `CHYBI: | "
    "**omylů celkem v HANDOFF.md (unikátní id)** | **86** | …` a tři další | "
    "Je to `overovani` **§9.6**: **očekávaná nepřítomnost není vada.** "
    "Kontrola „nic nezmizelo\" musí mít **seznam záměrných změn** a odečíst ho; "
    "jinak hlásí ztrátu tam, kde proběhla plánovaná aktualizace — a takový "
    "poplach se hledá hůř než slepé místo |\n"
)

# ── 3) Přepočet v kronize ──────────────────────────────────────────────────
PRECOUNTS = [
    ("| **8j** | akční (dokončení auditu) 2. 10. 18:1x | **7** | **7** | **0** |",
     "| **8j** | akční (dokončení auditu) 2. 10. 18:1x | **8** | **8** | **0** |"),
    ("| **celkem** | **10 bloků, 19 sessions** | **88** | **72 = 82 %** | **37** |",
     "| **celkem** | **10 bloků, 19 sessions** | **89** | **73 = 82 %** | **37** |"),
    ("| **z toho vad MĚŘIDLA** | **72 = 82 %** |",
     "| **z toho vad MĚŘIDLA** | **73 = 82 %** |"),
    ("| **omylů celkem v `HANDOFF.md` (unikátní id)** | **93** |",
     "| **omylů celkem v `HANDOFF.md` (unikátní id)** | **94** |"),
    ("| **87–93** |", "| **87–94** |"),
    ("`audit2a-schema.py` → **`exit 0`** — **ale kritérium zadání "
     "bylo nesplnitelné, viz H24**",
     "`audit2a-schema.py` → **`exit 0`** — **ale kritérium zadání "
     "bylo nesplnitelné, viz H24**"),
]


def spust(skript):
    r = subprocess.run([sys.executable, str(WS / "_analyza" / skript)], cwd=str(WS),
                       capture_output=True, timeout=300)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def main() -> int:
    h_pred = HANDOFF.read_bytes()
    k_pred = K.read_bytes()
    h = h_pred.decode("utf-8")
    k = k_pred.decode("utf-8")

    print("=" * 88)
    print("DOPLNĚK — značky nálezů H24–H28, omyl 94, přepočet kroniky")
    print("=" * 88)

    # 1) značky do §23
    for stary, novy in ZNAČKY:
        if novy in h:
            continue                      # už aplikováno (skript je opakovatelný)
        assert h.count(stary) == 1, "kotva není 1× (%dx): %s" % (h.count(stary), stary[:70])
        h = h.replace(stary, novy, 1)
    for znacka in ("H24", "H25", "H26", "H27", "H28"):
        assert ("**%s**" % znacka) in h or ("NÁLEZ %s" % znacka) in h, \
            "%s v HANDOFF.md není" % znacka
    print("  značky H24–H28 v §23: OK")

    # 2) omyl 94 do §8j (na konec tabulky bloku 8j)
    if "| **94** |" not in h:
        kotva94 = ("**A jeden údaj, který tomu nasvědčuje:** omyl **88** je **třetí "
                   "výskyt téže")
        assert h.count(kotva94) == 1, "kotva pro omyl 94 není 1×"
        h = h.replace(kotva94, OMYL_94 + "\n" + kotva94, 1)
    assert "| **94** |" in h, "omyl 94 se nevložil"
    # hlavička bloku 8j se musí rozšířit na 87–94
    stara_hlav = "### 8j. Omyly AKČNÍ session 2. 10. 2026 (dokončení auditu dokumentace) — **87–93**"
    nova_hlav = "### 8j. Omyly AKČNÍ session 2. 10. 2026 (dokončení auditu dokumentace) — **87–94**"
    if stara_hlav in h:
        h = h.replace(stara_hlav, nova_hlav, 1)
    assert nova_hlav in h, "hlavička 8j se neopravila"
    h = h.replace("**Sedm, všechny v měřidlech**", "**Osm, všechny v měřidlech**")
    print("  omyl 94 v §8j: OK")

    HANDOFF.write_bytes(h.encode("utf-8"))

    # 3) přepočet kroniky
    for stary, novy in PRECOUNTS:
        if stary == novy or novy in k:
            continue                      # už aplikováno
        assert k.count(stary) >= 1, "v kronize není: %s" % stary[:70]
        k = k.replace(stary, novy, 1)
    K.write_bytes(k.encode("utf-8"))
    print("  přepočet kroniky (8j 7→8, celkem 88→89, měřidla 72→73, id 93→94): OK")

    # ── Ověření: nic nezmizelo (s odečtením ZÁMĚRNÝCH změn — omyl 94) ──────
    # ⚠ POZOR (a je to omyl 94, podruhé): do „záměrných změn\" se musí vzít
    # CELÉ ŘÁDKY, které nahrazovaný podřetězec obsahují — ne jen ten podřetězec.
    # První verze tohohle ověření brala podřetězce a hlásila 3 „ztracené\"
    # řádky, které se přitom správně aktualizovaly.
    zamerne = set()
    for stary, novy in ZNAČKY + PRECOUNTS:
        if stary != novy:
            zamerne.update(l for l in h_pred.decode("utf-8").splitlines() if stary in l)
    zamerne.add(stara_hlav)
    zamerne.update(l for l in h_pred.decode("utf-8").splitlines()
                   if "**Sedm, všechny v měřidlech**" in l)
    for jmeno, pred, po in (("HANDOFF.md", h_pred, HANDOFF.read_bytes()),
                            ("KRONIKA-PROJEKTU.md", k_pred, K.read_bytes())):
        t_po = po.decode("utf-8")
        chybejici = [l for l in pred.decode("utf-8").splitlines()
                     if l.strip() and l not in t_po and l not in zamerne]
        print("  %-20s řádků %d -> %d, záměrných změn: %d, neobjasněně chybějících: %d"
              % (jmeno, len(pred.decode("utf-8").splitlines()),
                 len(t_po.splitlines()), len(zamerne), len(chybejici)))
        for l in chybejici[:3]:
            print("      CHYBI: %s" % l[:100])
        if chybejici:
            print("\nVYSLEDEK: něco zmizelo → exit 1")
            return 1

    kod_k, v_k = spust("kronika-kontrola.py")
    for l in v_k.splitlines():
        if l.strip().startswith(("omylů celkem", "nálezů H", "KRONIKA SEDÍ", "CHYBA", "NALEZENO")):
            print("  kronika: %s" % l.strip())
    kod_h, v_h = spust("handoff-kontrola-uplnost.py")
    for l in v_h.splitlines():
        if "kontrolovaných klíčů" in l or "CHYBÍ" in l or "VŠE OK" in l:
            print("  handoff: %s" % l.strip())
    print("\n  kronika-kontrola.py exit=%d | handoff-kontrola-uplnost.py exit=%d"
          % (kod_k, kod_h))
    if kod_k or kod_h:
        print("\nVYSLEDEK: některá brána nesedí → exit 1")
        return 1
    print("\nVYSLEDEK: doplněno, nic nezmizelo, obě brány sedí. exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
