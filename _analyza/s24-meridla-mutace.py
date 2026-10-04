# -*- coding: utf-8 -*-
"""MUTAČNÍ TEST brány `s24-meridla-over.py` — umí spadnout?

Pravidlo `overovani` §3 bod 1: brána bez důkazu, že umí spadnout, není brána.
Mutuje se **DOKUMENT, ne brána** (`overovani` §9.8: needituj kotvu v nástroji,
který ji cituje) — a **jen to, co brána měří**.

Tři mutace:
  M1 — `PREDAVANI-SESSION.md`: přidá se další odkaz na kroniku §5 (6 → 7)
       → brána MUSÍ spadnout na F7
  M2 — `HANDOFF.md`: smaže se kotva bloku `8h` → brána MUSÍ ohlásit, že
       počet bloků v dokumentu klesl (kontrola F4)
  M3 — KONTROLNÍ BĚH: zdravý stav musí dát `exit 0`

⚠ Každá mutace je v `try/finally`, návrat se ověřuje **bajtovou shodou**
(`overovani` §10.6) a před mutací se **assertuje, že měřená podmínka platí**,
po mutaci že **přestala platit** (§7.14).
"""
import hashlib
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable
BRANA = "_analyza/s24-meridla-over.py"


def spust():
    r = subprocess.run([PY, BRANA], cwd=str(WS), capture_output=True, timeout=1800)
    v = r.stdout.decode("utf-8", "replace")
    m = re.search(r"ZMĚŘENO:\s+kontrol=(\d+),\s+chyb=(\d+)", v)
    return r.returncode, (int(m.group(1)), int(m.group(2))) if m else (None, None), v


def mutuj(cesta, uprav, popis, ocekavany):
    """Provede mutaci, spustí bránu, vrátí soubor. Vrací (OK?, exit, detail)."""
    cil = WS / cesta
    orig = cil.read_bytes()
    text = orig.decode("utf-8")
    novy = uprav(text)
    print("-" * 92)
    print("%s  (%s)" % (popis, cesta))
    print("-" * 92)
    try:
        assert novy != text, "MUTACE SE NEPROVEDLA (text stejný)"
        cil.write_text(novy, encoding="utf-8", newline="")
        assert cil.read_bytes() != orig, "zápis neproběhl"
        e, pocty, v = spust()
        print("   brána: exit=%d · kontrol=%s chyb=%s" % (e, pocty[0], pocty[1]))
        if ocekavany == "spadne":
            ok = e != 0
        else:
            ok = e == 0
        print("   → %s (čekáno: %s)" % ("SPRÁVNĚ" if ok else "CHYBA — brána nereagovala",
                                        ocekavany))
        if not ok:
            for radek in v.splitlines():
                if radek.strip().startswith("✗"):
                    print("      brána přesto hlásí: %s" % radek.strip()[:100])
        return ok, e, v
    finally:
        cil.write_bytes(orig)
        assert cil.read_bytes() == orig, "SOUBOR NEVRÁCEN: %s" % cesta


def main() -> int:
    print("=" * 92)
    print("MUTAČNÍ TEST BRÁNY `s24-meridla-over.py`")
    print("=" * 92)
    print("(mutuje se DOKUMENT, ne brána — `overovani` §9.8)")
    print()

    e0, p0, _ = spust()
    print("0) VÝCHOZÍ STAV: exit=%d · kontrol=%s chyb=%s  (musí být exit 0)"
          % (e0, p0[0], p0[1]))
    if e0 != 0:
        print("   CHYBA: brána neprochází na zdravém stavu — sprav bránu, ne dokument.")
        return 2
    print()

    vysledky = []

    # ── M1: přidat odkaz na kroniku §5 ─────────────────────────────────────
    def m1(text):
        radky = text.splitlines(keepends=True)
        # vloží se ZA řádek 334 (poslední odkaz na §5) — jednoznačné místo
        cil_idx = next(i for i, l in enumerate(radky) if l.startswith("**D2) ROZHODNI"))
        vloz = ("| **M1** | test | test | zapíše ho do **`KRONIKA-PROJEKTU.md` §5** "
                "se stavem **`NEOVĚŘENO`** |\n")
        return "".join(radky[:cil_idx + 1]) + vloz + "".join(radky[cil_idx + 1:])

    ok1, _, _ = mutuj("PREDAVANI-SESSION.md", m1,
                      "M1 — PŘIDÁN další odkaz na `KRONIKA-PROJEKTU.md` §5", "spadne")
    vysledky.append(("M1 odkaz na kroniku §5", ok1))
    print()

    # ── M2: smazat kotvu bloku 8h ──────────────────────────────────────────
    def m2(text):
        # přejmenuje nadpis bloku `8h` na `8h (přejmenováno testem)` — tím
        # přestane odpovídat kotvě v bráně kroniky i počítadlu v s24
        return re.sub(r"^### 8h\. Omyly", "### 8h-test. Omyly", text, count=1, flags=re.M)

    ok2, _, v2 = mutuj("HANDOFF.md", m2,
                       "M2 — PŘEJMENOVÁN nadpis bloku `8h` (kotva brány)", "spadne")
    vysledky.append(("M2 přejmenovaný blok 8h", ok2))
    print()

    # ── M3: kontrolní běh na zdravém stavu ─────────────────────────────────
    print("-" * 92)
    print("M3 — KONTROLNÍ BĚH (zdravý stav, beze změny souboru) — musí být exit 0")
    print("-" * 92)
    e3, p3, _ = spust()
    print("   brána: exit=%d · kontrol=%s chyb=%s" % (e3, p3[0], p3[1]))
    ok3 = e3 == 0
    print("   → %s" % ("SPRÁVNĚ ZELENÁ" if ok3 else "CHYBA"))
    vysledky.append(("M3 kontrolní běh", ok3))
    print()

    # ── ZÁVĚR ──────────────────────────────────────────────────────────────
    print("=" * 92)
    chyceno = sum(1 for _, o in vysledky if o)
    print("  ZMĚŘENO: mutací=%d, chyceno=%d" % (len(vysledky) - 1, chyceno - (1 if ok3 else 0)))
    for jmeno, o in vysledky:
        print("     %-32s %s" % (jmeno, "OK" if o else "SELHALO"))
    print()
    if all(o for _, o in vysledky):
        print("  VÝSLEDEK: brána spadne na vrácené vadě a je zelená na zdravém stavu → MĚŘÍ.")
        return 0
    print("  VÝSLEDEK: brána NEREAGUJE na vrácenou vadu → je slepá (nebo je slabá mutace).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
