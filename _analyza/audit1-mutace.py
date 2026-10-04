# -*- coding: utf-8 -*-
"""MUTAČNÍ TEST INVENTÁŘE (`audit1-inventar.py`).

PROČ: plán auditu to žádá doslova — *„A ověřit ho mutací: přesuň dokument do
archivu → inventář ho musí přestat vidět mezi živými; přidej nový .md → musí se
objevit. Bez toho je to jen další tabulka, která vypadá ověřeně."*

A `overovani` §3 to žádá taky: **napsal jsi test? Vrať do kódu vadu a podívej
se, že spadne.**

⚠ DVĚ PRAVIDLA, KTERÁ SE TU DODRŽUJÍ (obě naměřená, viz `overovani` §7.9/§7.14):
  1. **Ověř, že mutace SKUTEČNĚ PROBĚHLA** — ne jen že se soubor změnil.
     Proto se po každé mutaci kontroluje, že nastala MĚŘENÁ PODMÍNKA.
  2. **Zálohuj KOPIÍ, ne `git checkout`** — soubory mají necommitnuté změny
     a `git checkout` by je smazal.

CO SE MUTUJE:
  A) nový `.md` v `_analyza`        → musí se objevit jako SIROTEK
  B) přejmenování na `*-pred-*`     → musí se přesunout mezi ZÁLOHY
  C) smazání z RUČNÍHO seznamu brány→ musí se přesunout mezi SIROTKY
     (to je test klíčového rozlišení „ruční seznam vs. projití složky")

Použití:  python _analyza/audit1-mutace.py
Návrat:   0 = všechny mutace chyceny | 1 = některá ne (inventář je slepý)
"""

import json
import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
INVENTAR = WS / "_analyza" / "audit1-inventar.py"
KD = WS / "orchestra" / "tools" / "kontrola-diakritiky.py"
TMP_JSON = WS / "_analyza" / "audit1-mutace-inventar.json"


def spust_inventar():
    """Spustí inventář do DOČASNÉHO JSONu (aby se nepřepsal ostrý výsledek)."""
    r = subprocess.run([sys.executable, str(INVENTAR), "--json", str(TMP_JSON)],
                       cwd=str(WS), capture_output=True, timeout=600)
    if not TMP_JSON.is_file():
        print("      CHYBA inventář nevypsal JSON (exit=%d)" % r.returncode)
        print("      " + r.stderr.decode("utf-8", "replace")[-400:])
        return None
    return json.loads(TMP_JSON.read_text(encoding="utf-8"))


def najdi(inv, cesta):
    return next((z for z in inv["dokumenty"] if z["cesta"] == cesta), None)


def main() -> int:
    vysledky = []

    # ── 0. Výchozí stav ────────────────────────────────────────────────────
    print("=" * 92)
    print("MUTAČNÍ TEST INVENTÁŘE")
    print("=" * 92)
    print()
    print("  0) VÝCHOZÍ STAV")
    inv0 = spust_inventar()
    if inv0 is None:
        return 1
    zaklad = {z["cesta"]: z["kategorie_zivota"] for z in inv0["dokumenty"]}
    print("      dokumentů: %d   živých/sirotků/záloh/kopií: %d/%d/%d/%d"
          % (inv0["dokumentu"], inv0["zive"], inv0["sirotci"],
             inv0["zalohy"], inv0["kopie"]))
    print()

    # ── MUTACE A: nový .md se musí objevit ─────────────────────────────────
    novy = WS / "_analyza" / "aaa-mutace-test.md"
    print("  A) NOVÝ SOUBOR `_analyza\\aaa-mutace-test.md`")
    novy.write_text("# mutační test\n\nTenhle soubor vznikl jen pro test.\n",
                    encoding="utf-8")
    # Ověření, že mutace PROBĚHLA (ne jen že se něco stalo).
    assert novy.is_file(), "MUTACE NEPROBĚHLA: soubor nevznikl"
    invA = spust_inventar()
    z = najdi(invA, "_analyza\\aaa-mutace-test.md") if invA else None
    okA = z is not None and z["kategorie_zivota"] == "sirotek"
    print("      v inventáři: %s   kategorie: %s"
          % ("ANO" if z else "NE", z["kategorie_zivota"] if z else "—"))
    print("      → %s" % ("CHYCENO (nový soubor se objevil jako sirotek)"
                          if okA else "SLEPÉ MÍSTO — nový soubor inventář nevidí"))
    vysledky.append(("A: nový .md se objeví jako sirotek", okA))
    novy.unlink(missing_ok=True)
    assert not novy.exists(), "ÚKLID NEPROBĚHL: soubor zůstal"
    print()

    # ── MUTACE B: přejmenování na zálohu ───────────────────────────────────
    cil = "_analyza\\pr-mining-body.md"
    print("  B) PŘEJMENOVÁNÍ `%s` → `pr-mining-body-pred-testem.md`" % cil)
    puvodni = WS / cil
    zaloha = puvodni.with_name("pr-mining-body-pred-testem.md")
    pred = zaklad.get(cil)
    print("      před mutací v inventáři jako: %s" % pred)
    if not puvodni.is_file():
        print("      CHYBA: soubor neexistuje — mutaci nelze provést")
        vysledky.append(("B: přejmenování na zálohu", False))
    else:
        shutil.copyfile(puvodni, zaloha)      # KOPIÍ, ne git checkout
        puvodni.unlink()
        assert zaloha.is_file() and not puvodni.exists(), "MUTACE NEPROBĚHLA"
        invB = spust_inventar()
        z = najdi(invB, "_analyza\\pr-mining-body-pred-testem.md") if invB else None
        okB = z is not None and z["kategorie_zivota"] == "zaloha"
        print("      po mutaci: %s   kategorie: %s"
              % ("ANO" if z else "NE", z["kategorie_zivota"] if z else "—"))
        print("      → %s" % ("CHYCENO (přesunul se mezi zálohy)"
                              if okB else "SLEPÉ MÍSTO — záloha se nepoznala"))
        vysledky.append(("B: přejmenování na *-pred-* → mezi zálohy", okB))
        shutil.copyfile(zaloha, puvodni)
        zaloha.unlink()
        assert puvodni.is_file(), "ÚKLID NEPROBĚHL"
    print()

    # ── MUTACE C: smazání z RUČNÍHO seznamu brány ──────────────────────────
    # Testuje klíčové rozlišení „ruční seznam vs. projití složky": dokument
    # vyjmutý z ručního seznamu musí SPADNOUT mezi sirotky, i když ho g1
    # pořád vidí (protože prochází složku).
    print("  C) VYJMUTÍ `_analyza\\HLOUBKOVA-MERENI-2.md` Z RUČNÍHO SEZNAMU BRÁNY")
    klic = "_analyza\\HLOUBKOVA-MERENI-2.md"
    pred = zaklad.get(klic)
    print("      před mutací: %s" % pred)
    s = KD.read_text(encoding="utf-8")
    radek = '    WS / "_analyza" / "HLOUBKOVA-MERENI-2.md",\n'
    if radek not in s:
        print("      CHYBA: řádek v bráně nenalezen — mutaci nelze provést")
        vysledky.append(("C: vyjmutí z ručního seznamu", False))
    else:
        shutil.copyfile(KD, KD.with_suffix(".py.zaloha-mutace"))
        KD.write_text(s.replace(radek, ""), encoding="utf-8")
        # Ověření, že MĚŘENÁ PODMÍNKA přestala platit.
        s2 = KD.read_text(encoding="utf-8")
        assert "HLOUBKOVA-MERENI-2.md" not in s2, "MUTACE NEPROBĚHLA (řádek tam je)"
        invC = spust_inventar()
        z = najdi(invC, klic) if invC else None
        okC = z is not None and z["otevira_brana"] == "—" and z["kategorie_zivota"] == "sirotek"
        print("      po mutaci: brána=%s  kategorie=%s"
              % (z["otevira_brana"] if z else "—", z["kategorie_zivota"] if z else "—"))
        print("      → %s" % ("CHYCENO (vypadl z ručního seznamu → sirotek)"
                              if okC else "SLEPÉ MÍSTO — inventář ho vede dál jako živý"))
        vysledky.append(("C: vyjmutí z ručního seznamu → sirotek", okC))
        shutil.copyfile(KD.with_suffix(".py.zaloha-mutace"), KD)
        KD.with_suffix(".py.zaloha-mutace").unlink()
        assert 'HLOUBKOVA-MERENI-2.md' in KD.read_text(encoding="utf-8"), "ÚKLID NEPROBĚHL"
    print()

    TMP_JSON.unlink(missing_ok=True)

    # ── Souhrn ─────────────────────────────────────────────────────────────
    print("=" * 92)
    print("  VÝSLEDEK")
    print("=" * 92)
    for popis, ok in vysledky:
        print("      %-58s %s" % (popis, "CHYCENO" if ok else "SLEPÉ MÍSTO"))
    chyceno = sum(1 for _, ok in vysledky if ok)
    print()
    print("  mutací: %d, chyceno: %d" % (len(vysledky), chyceno))
    if chyceno == len(vysledky):
        print("  INVENTÁŘ MĚŘÍ — každá vrácená vada se projevila.")
    else:
        print("  ⚠ INVENTÁŘ JE SLEPÝ v %d případech — čísla z něj nic neznamenají."
              % (len(vysledky) - chyceno))
    return 0 if chyceno == len(vysledky) else 1


if __name__ == "__main__":
    sys.exit(main())
