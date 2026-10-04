# -*- coding: utf-8 -*-
"""SLEPOTA `audit2b` NA APPEND-ONLY DOKUMENTECH — měření, ne dojem.

Otázka (ze zadání §2.3 bod 2): `audit2b` má přiznanou mez — nehlídá append-only
dokumenty. **Je to slepota, nebo je to kryté jinudy?**

Postup: do `HANDOFF.md` se vloží NEPRAVDIVÉ tvrzení (číslo proti živému zdroji)
do oddílu, který NENÍ datovaný; pak se pustí `audit2b` a hledá se, jestli to
ohlásí. Pak se dokument vrátí **bit po bitu**.

Dvě varianty (aby se rozlišilo, ČÍM to je):
  A) vložit `54 sloupců` do NEDATOVANÉHO oddílu  → měří se, jestli chybí datum
  B) vložit totéž do DATOVANÉHO oddílu           → kontrolní vzorek

Mutace je obalena `try/finally` (`overovani` §10.6) a po návratu se ověřuje
**bajtová shoda**, ne jen „něco se vrátilo".
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


def vypis_nadpisy() -> None:
    """Vypíše nadpisy `##` a `###` s tím, jestli nesou datum."""
    radky = CIL.read_text(encoding="utf-8").splitlines()
    print("Nadpisy v HANDOFF.md (jen ty bez data — kandidáti na vložení):")
    bez, s = [], 0
    for i, radek in enumerate(radky):
        if radek.startswith("##") and not radek.startswith("####"):
            if DATUM.search(radek):
                s += 1
            else:
                bez.append((i + 1, radek))
    print("  s datem: %d · bez data: %d" % (s, len(bez)))
    for cislo, radek in bez[:14]:
        print("    ř.%-5d %s" % (cislo, radek[:78]))
    return bez


def spust_audit2b() -> tuple:
    """Pustí audit2b a vrátí (exit, jestli hlásí vložené číslo)."""
    r = subprocess.run([PY, "_analyza/audit2b-cisla-proti-zdroji.py"],
                       cwd=str(WS), capture_output=True, timeout=400)
    v = r.stdout.decode("utf-8", "replace")
    # Hledá se KONKRÉTNÍ vložená hodnota 54 u veličiny `sloupců`
    hlasi = bool(re.search(r"sloupc\S*\s+tvrdí\s+54\b", v))
    pocet = re.search(r"ROZCHODŮ:\s+(\d+)", v)
    return r.returncode, hlasi, (int(pocet.group(1)) if pocet else None), v


def main() -> int:
    orig = CIL.read_bytes()
    puvodni_hash = hashlib.sha256(orig).hexdigest()
    print("=" * 90)
    print("SLEPOTA audit2b NA APPEND-ONLY DOKUMENTECH")
    print("=" * 90)
    print("HANDOFF.md: %d B, sha256 %s…" % (len(orig), puvodni_hash[:20]))
    print()

    bez_data = vypis_nadpisy()
    print()

    exit0, hlasi0, pocet0, _ = spust_audit2b()
    print("VÝCHOZÍ STAV: audit2b exit=%d, rozchodů=%s, hlásí '54'=%s"
          % (exit0, pocet0, hlasi0))
    print()

    text = orig.decode("utf-8")

    # ── A) vložení do NEDATOVANÉHO oddílu ───────────────────────────────────
    if not bez_data:
        print("CHYBA: v HANDOFF.md není oddíl bez data — test A nelze provést.")
        return 2
    cil_radek, cil_nadpis = bez_data[0]
    radky = text.splitlines(keepends=True)
    vlozeny = ("\n**Kontrolní tvrzení o dnešním stavu (vloženo testem slepoty):** "
               "schéma `conductor` má **54 sloupců**.\n")
    novy = "".join(radky[:cil_radek]) + vlozeny + "".join(radky[cil_radek:])
    assert novy != text, "MUTACE A SE NEPROVEDLA"
    assert "54 sloupců" in novy, "podmínka neplatí: vložené tvrzení tam není"

    print("-" * 90)
    print("A) VKLÁDÁM do NEDATOVANÉHO oddílu: ř.%d %s" % (cil_radek, cil_nadpis[:60]))
    print("   text: „schéma `conductor` má **54 sloupců**“  (živý zdroj = 40)")
    print("-" * 90)
    try:
        CIL.write_text(novy, encoding="utf-8", newline="")
        assert CIL.read_bytes() != orig, "zápis neproběhl"
        exitA, hlasiA, pocetA, vystupA = spust_audit2b()
    finally:
        CIL.write_bytes(orig)
        assert CIL.read_bytes() == orig, "HANDOFF.md NEVRÁCEN!"

    print("   audit2b exit=%d · rozchodů=%s · HLÁSÍ vložené '54 sloupců': %s"
          % (exitA, pocetA, "ANO" if hlasiA else "NE"))
    if not hlasiA:
        # Rozlišit DVĚ příčiny: (a) číslo se nenašlo vůbec (vzor),
        # (b) našlo se, ale bylo zařazeno jako ZÁZNAM.
        vZ = re.search(r"54\s+sloupc\S*[^\n]*", vystupA)
        print("   → vložené číslo ve výstupu: %s"
              % (("zařazeno jako ZÁZNAM: " + vZ.group(0)[:70]) if vZ
                 else "VŮBEC SE NEVYSKYTUJE (vzor nenašel)"))
    print()

    # ── B) totéž do DATOVANÉHO oddílu (kontrolní vzorek) ───────────────────
    datovane = [(i + 1, r) for i, r in enumerate(text.splitlines())
                if r.startswith("## ") and DATUM.search(r)]
    if not datovane:
        print("CHYBA: není datovaný oddíl — kontrolní vzorek nelze provést.")
        return 2
    cil2, nadpis2 = datovane[-1]
    radky2 = text.splitlines(keepends=True)
    novy2 = "".join(radky2[:cil2]) + vlozeny + "".join(radky2[cil2:])
    assert novy2 != text and "54 sloupců" in novy2, "MUTACE B SE NEPROVEDLA"
    print("-" * 90)
    print("B) KONTROLNÍ VZOREK — totéž do DATOVANÉHO oddílu: ř.%d %s"
          % (cil2, nadpis2[:56]))
    print("-" * 90)
    try:
        CIL.write_text(novy2, encoding="utf-8", newline="")
        assert CIL.read_bytes() != orig, "zápis neproběhl"
        exitB, hlasiB, pocetB, vystupB = spust_audit2b()
    finally:
        CIL.write_bytes(orig)
        assert CIL.read_bytes() == orig, "HANDOFF.md NEVRÁCEN!"

    print("   audit2b exit=%d · rozchodů=%s · HLÁSÍ vložené '54 sloupců': %s"
          % (exitB, pocetB, "ANO" if hlasiB else "NE"))
    if not hlasiB:
        vZb = re.search(r"54\s+sloupc\S*[^\n]*", vystupB)
        print("   → vložené číslo ve výstupu: %s"
              % (("zařazeno jako ZÁZNAM: " + vZb.group(0)[:70]) if vZb
                 else "VŮBEC SE NEVYSKYTUJE (vzor nenašel)"))
    print()

    # ── ZÁVĚR ──────────────────────────────────────────────────────────────
    print("=" * 90)
    print("ZÁVĚR")
    print("  HANDOFF.md po testu: %d B, sha256 %s…  → %s"
          % (len(CIL.read_bytes()), hashlib.sha256(CIL.read_bytes()).hexdigest()[:20],
             "BIT PO BITU PŮVODNÍ" if CIL.read_bytes() == orig else "ZMĚNĚN!"))
    verdikt = ("NENÍ slepota — brána vložené tvrzení OHLÁSÍ" if hlasiA
               else "SLEPOTA POTVRZENA — brána vložené tvrzení v NEDATOVANÉM oddílu NEHLÁSÍ")
    print("  A (nedatovaný oddíl): %s" % verdikt)
    print("  B (datovaný oddíl):   %s"
          % ("ohlásí" if hlasiB else "nehlásí (kryto datem — správně, je to záznam)"))
    return 0 if CIL.read_bytes() == orig else 1


if __name__ == "__main__":
    sys.exit(main())
