# -*- coding: utf-8 -*-
r"""P32 — SONDA H139: mění mutace `REPO` v `tools/over-skilly.py` verdikt, nebo ne?

JEDNORÁZOVÁ DIAGNOSTIKA (patří do `PRESKIP` dávky `p20-d-doklady.py`), ne doklad.

PROČ: P31 zapsala H139 s tvrzením **„mutace `REPO` nic nezmění"**. Naměřený
výstup `p22-test-mutace.py` ale ukazoval `exit=1` u zmutované brány a řádek
`Cesty k nástrojům: 43 zmínek, 40 mrtvých` — tedy **verdikt se změnil**. Sonda
měří, co je pravda, a rozlišuje tři možné příčiny spadlé kontroly:

  (a) mutace opravdu nic nemění (tvrzení P31),
  (b) mutace mění verdikt, ale kontrola hledá řetězec, který v měřené části
      výstupu **není** — například proto, že literál v TESTU je v **jiné
      normalizaci Unicode** (NFD) než výstup brány (NFC),
  (c) mutace se tiše neprovede.

Použití: python _analyza/p32-sonda-h139.py
"""

import pathlib
import re
import subprocess
import sys
import unicodedata

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
BRANA = WS / "tools" / "over-skilly.py"
TEST = ANALYZA / "p22-test-mutace.py"
sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj  # noqa: E402

# TOTÉŽ, CO MUTUJE `p22-test-mutace.py` (kotva se MUSÍ shodovat se zdrojem).
KOTVA_REPO = ('# VIDĚT; tiché rozšíření rozsahu by bylo přesně ta vada, '
              'kterou P25-K popisuje).\n'
              'REPO = pathlib.Path(__file__).resolve().parents[1]')
NOVA_REPO = KOTVA_REPO.replace(
    'pathlib.Path(__file__).resolve().parents[1]',
    'pathlib.Path(r"E:\\NEEXISTUJE-tato-cesta\\hluboko\\tam")')

VZOR_RADEK = re.compile(r"Cesty k nástrojům:\s*(\d+)\s*zmínek,\s*(\d+)\s*mrtvých")
NFC = "mrtvých"
NFD = unicodedata.normalize("NFD", NFC)


def spust():
    r = subprocess.run([sys.executable, "-B", str(BRANA)], capture_output=True,
                       cwd=str(WS), timeout=900)
    v = (r.stdout or b"").decode("utf-8", "replace") + \
        (r.stderr or b"").decode("utf-8", "replace")
    return r.returncode, v


def tvary(text):
    return {jmeno: text.count(tvar) for tvar, jmeno in ((NFC, "NFC"), (NFD, "NFD"))}


def vypis(ozn, kod, v):
    m = VZOR_RADEK.search(v)
    radky = [l for l in v.splitlines() if "mrtv" in l]
    print("  %s: exit=%d" % (ozn, kod))
    print("    čítač měřeného řádku: %r" % (m.group(0) if m else None))
    print("    řádků s 'mrtv': %d" % len(radky))
    for l in radky[:4]:
        print("      | %s" % l[:150])
    t = tvary(v)
    print("    výskytů NFD 'mrtvých': %d | NFC 'mrtvých': %d" % (t["NFD"], t["NFC"]))
    return (int(m.group(1)), int(m.group(2))) if m else None


def main() -> int:
    print("=" * 78)
    print("P32 — SONDA H139: mění mutace `REPO` verdikt brány `over-skilly.py`?")
    print("=" * 78)

    print("\n1) DOSLOVNÉ TVARY V TESTU `p22-test-mutace.py` (rozhoduje BAJT)")
    tb = TEST.read_bytes()
    tt = tb.decode("utf-8")
    i = tt.find("0 mrtv")
    if i < 0:
        print("   CHYBA: v testu NENÍ literál '0 mrtv...' — sonda by měřila jinam")
        return 1
    okno = tt[i - 60:i + 60]
    print("   okno: %r" % okno)
    print("   kódové body okna: %s" % " ".join("U+%04X" % ord(c) for c in okno if ord(c) > 127))
    print("   v TESTU: NFD 'mrtvých'=%d | NFC 'mrtvých'=%d"
          % (tt.count(NFD), tt.count(NFC)))
    print("   v TESTU: NFD '0 mrtvých'=%d | NFC '0 mrtvých'=%d"
          % (tt.count("0 " + NFD), tt.count("0 " + NFC)))

    print("\n2) ZDRAVÁ BRÁNA")
    kod0, v0 = spust()
    z0 = vypis("zdravá", kod0, v0)

    print("\n3) BRÁNA SE MUTACÍ `REPO` (tatáž kotva jako v testu)")
    print("   kotva v souboru: %d×" % BRANA.read_text(encoding="utf-8").count(KOTVA_REPO))
    with mutuj(BRANA, KOTVA_REPO, NOVA_REPO) as mut:
        print("   hash %s → %s" % (mut.hash_pred[:12], mut.hash_po_mutaci[:12]))
        kod1, v1 = spust()
        z1 = vypis("zmutovaná", kod1, v1)
        # přesně podmínka z testu, rozložená na části
        print("   podmínka testu: 'mrtvých'(NFC) in v1 = %s | '0 mrtvých'(NFC) not in v1 = %s"
              % (NFC in v1, ("0 " + NFC) not in v1))
        print("   podmínka testu s NFD literálem: 'mrtvých'(NFD) in v1 = %s" % (NFD in v1))
    print("   brána vrácena bajt na bajt: %s" % (mut.hash_po_navratu == mut.hash_pred))

    print("\n" + "=" * 78)
    verdikt = "MUTACE MĚNÍ VERDIKT" if (z0 and z1 and z0 != z1) else "MUTACE NEMĚNÍ VERDIKT"
    print("ZÁVĚR: %s (zdravá %s → zmutovaná %s)" % (verdikt, z0, z1))
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
