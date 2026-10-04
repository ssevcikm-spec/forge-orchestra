# -*- coding: utf-8 -*-
"""SLEPOTA `audit2b` — PŘESNÉ měření: VIDÍ brána vložené tvrzení?

Navazuje na `s24-slepota-audit2b.py`. Ten měřil jen to, jestli se vložené číslo
objeví VE VÝSTUPU — jenže `audit2b` tiskne ze ZÁZNAMŮ jen **prvních 40**
(řádek `histor[:40]`), takže „není ve výstupu" **není totéž** jako „brána ho
nevidí". To je přesně past `overovani` §9.4: *naměřeno 0 může znamenat tři věci*.

Přesné měření proto používá **ČÍTAČ**, který výpis nezkresluje:
  · `ROZCHODŮ: N` ze souhrnu  → vložené tvrzení je TVRZENÍ (brána ho vidí)
  · beze změny                → vložené tvrzení je ZÁZNAM (kryto okolím)
A druhé nezávislé měření: **počet řádků v bloku ROZCHODY** (ne jen souhrn).

Mutace je obalena `try/finally` a návrat se ověřuje **bajtovou shodou**.
"""
import hashlib
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
CIL = WS / "HANDOFF.md"
PY = sys.executable
DATUM = re.compile(r"\d{1,2}\.\s*\d{1,2}\.\s*\d{4}")

VLOZENY = ("\n**Kontrolní tvrzení o dnešním stavu (vloženo testem slepoty):** "
           "schéma `conductor` má **54 sloupců**.\n")


def zmer() -> tuple:
    """Pustí audit2b; vrací (exit, rozchodu_ze_souhrnu, radku_v_bloku_rozchodu,
    hlasi_54_v_rozchodich, hlasi_54_kdekoli)."""
    r = subprocess.run([PY, "_analyza/audit2b-cisla-proti-zdroji.py"],
                       cwd=str(WS), capture_output=True, timeout=400)
    v = r.stdout.decode("utf-8", "replace")
    m = re.search(r"ROZCHODŮ:\s+(\d+)", v)
    souhrn = int(m.group(1)) if m else None
    # Blok ROZCHODY: řádky se 4 mezerami a "tvrdí"
    blok = v.split("ZÁZNAMY A CITACE MINULOSTI")[0]
    radku = len(re.findall(r"tvrdí\s+\d+\s+zdroj", blok))
    v_roz = bool(re.search(r"54\s+sloupc", blok))
    return r.returncode, souhrn, radku, v_roz, ("54" in v)


def main() -> int:
    orig = CIL.read_bytes()
    print("=" * 92)
    print("PŘESNÉ MĚŘENÍ SLEPOTY `audit2b` — VIDÍ brána vložené tvrzení?")
    print("=" * 92)
    print("HANDOFF.md: %d B, sha256 %s…" % (len(orig), hashlib.sha256(orig).hexdigest()[:20]))
    print()

    e0, s0, r0, v0, k0 = zmer()
    print("VÝCHOZÍ STAV      exit=%d · rozchodů(ze souhrnu)=%s · řádků v bloku=%d"
          % (e0, s0, r0))
    if v0:
        print("                  ⚠ „54“ se ve výstupu vyskytuje UŽ TEĎ — měření je znehodnocené")
    print()

    text = orig.decode("utf-8")
    radky = text.splitlines(keepends=True)

    vysledky = {}
    for jmeno, jen_datovane in (("A) NEDATOVANÝ oddíl", False), ("B) DATOVANÝ oddíl", True)):
        kandidati = [(i + 1, r) for i, r in enumerate(text.splitlines())
                     if r.startswith("## ") and bool(DATUM.search(r)) == jen_datovane]
        if not kandidati:
            print("%s: žádný kandidát — přeskakuji" % jmeno)
            continue
        cislo, nadpis = kandidati[0]
        novy = "".join(radky[:cislo]) + VLOZENY + "".join(radky[cislo:])
        assert novy != text, "MUTACE SE NEPROVEDLA (text stejný)"
        assert "54 sloupců" in novy, "MUTACE SE NEPROVEDLA (vložené tvrzení tam není)"
        print("-" * 92)
        print("%s — vkládám do ř.%d  %s" % (jmeno, cislo, nadpis[:56]))
        print("-" * 92)
        try:
            CIL.write_text(novy, encoding="utf-8", newline="")
            assert CIL.read_bytes() != orig, "zápis neproběhl"
            e, s, rr, v_roz, kdekoli = zmer()
        finally:
            CIL.write_bytes(orig)
            assert CIL.read_bytes() == orig, "HANDOFF.md NEVRÁCEN!"
        print("   exit=%d · rozchodů(ze souhrnu)=%s (bylo %s) · řádků v bloku=%d (bylo %d)"
              % (e, s, s0, rr, r0))
        print("   → vložené tvrzení je v ROZCHODECH: %s" % ("ANO" if v_roz else "NE"))
        print("   → vložené tvrzení je ve výstupu VŮBEC: %s"
              % ("ANO" if kdekoli else "NE (ani v záznamech)"))
        vysledky[jmeno] = (v_roz, s, s0)
        print()

    print("=" * 92)
    print("ZÁVĚR")
    print("  HANDOFF.md: %d B · %s"
          % (len(CIL.read_bytes()),
             "BIT PO BITU PŮVODNÍ" if CIL.read_bytes() == orig else "ZMĚNĚN!"))
    a = vysledky.get("A) NEDATOVANÝ oddíl")
    b = vysledky.get("B) DATOVANÝ oddíl")
    if a:
        print("  A (nedatovaný oddíl): rozchody %s → %s · v ROZCHODECH: %s"
              % (a[2], a[1], "ANO" if a[0] else "NE"))
        print("     → %s" % ("NENÍ slepota: brána vložené tvrzení OHLÁSÍ"
                             if a[0] else "SLEPOTA: brána vložené tvrzení NEHLÁSÍ"))
    if b:
        print("  B (datovaný oddíl):   rozchody %s → %s · v ROZCHODECH: %s"
              % (b[2], b[1], "ANO" if b[0] else "NE"))
        print("     → %s" % ("vidí, ale správně jako ZÁZNAM (kryto datem oddílu)"
                             if not b[0] else "ohlášeno jako ROZCHOD"))
    return 0 if CIL.read_bytes() == orig else 1


if __name__ == "__main__":
    sys.exit(main())
