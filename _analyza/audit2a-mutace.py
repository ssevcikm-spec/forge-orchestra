r"""MUTAČNÍ TEST `_analyza\audit2a-schema.py`.

PROČ: `overovani` §9.7 — „opravuješ-li měřidlo, mutačně ověř OPRAVU — ne jen
to, že původní vada zmizela". Oprava z 2. 10. 2026 (Úkol 1 zadání
`ZADANI-DOKONCENI-AUDITU.md`) zavedla rozlišení tvrzení / citace / záznamu.
Bez tohohle testu by se dalo myslet, že brána měří — a přitom by mohla být
**slepá k té jediné vadě, kvůli které vznikla**: že `AGENTS.md` tvrdí o dnešku
staré číslo bez značky času.

CO SE MĚŘÍ (4 mutace, každá míří na JINOU část pravidla):

  M1  ZNAČKA ČASU ZMIZÍ (`**39** (stav před B1; dnes **40**)` → `**39**`)
      → to je PŘESNĚ vada R1, kvůli které Úkol 1 existuje.
      Brána MUSÍ spadnout. Kdyby ne, oprava zavedla slepé místo.

  M2  CITACE SE STANE TVRZENÍM (v `AGENTS.md` : `„32 sloupců"` → `32 sloupců`)
      → pravidlo „v uvozovkách = citace" se tím vypne.
      Brána MUSÍ spadnout (32 je rozchod).

  M3  TABULKA LŽE (`40 sloupců` v tabulce jazyka → `39 sloupců`)
      → ověří, že se kontroluje i číslo u slova, ne jen próza.
      Brána MUSÍ spadnout.

  M4  ZÁZNAM SE NEHLÍDÁ JAKO ROZCHOD (beze změny souboru — KONTROLNÍ BĚH)
      → týž stav jako na začátku MUSÍ dát `exit 0`.
      Je to protiváha k M1–M3: bez ní by test prošel i bránou, která padá vždy.

POJISTKY PROTI TŘEM PASTem `overovani` §7.9/§7.12/§7.14:
  * mutuje se v PYTHONU (`read_text`/`write_text`, `utf-8`), ne shellem;
  * PŘED spuštěním brány se `assert`uje, že se text ZMĚNIL;
  * a navíc že **MĚŘENÁ PODMÍNKA přestala platit** (ne jen že se změnil text);
  * originál se vrací **bajt po bajtu** (`write_bytes`) a na konci se
    `assert`uje, že je soubor bit po bitu původní — ne `git checkout`
    (soubor není v gitu).

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\audit2a-mutace.py
"""
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
AGENTS = WS / "AGENTS.md"
BRANA = WS / "_analyza" / "audit2a-schema.py"


def spust():
    r = subprocess.run([sys.executable, str(BRANA)],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def souhrn(vystup):
    for l in vystup.splitlines():
        if "ZMĚŘENO: výskytů celkem" in l:
            return l.strip()
    return "(souhrn se nenašel — brána nedoběhla)"


def rozchody(vystup):
    return [l.strip() for l in vystup.splitlines() if l.strip().startswith("ROZCHOD:")]


orig = AGENTS.read_bytes()

print("=" * 92)
print("MUTAČNÍ TEST `audit2a-schema.py` — umí ještě spadnout?")
print("=" * 92)

prvni_kod, prvni_vystup = spust()
print("\n  0) výchozí stav (KONTROLA, musí být exit 0):")
print("     %s" % souhrn(prvni_vystup))
if prvni_kod != 0:
    print("     !! CHYBA: výchozí stav NEPROCHÁZÍ (exit=%d) — test nic nezměří." % prvni_kod)
    for r in rozchody(prvni_vystup):
        print("        %s" % r)
    sys.exit(2)

MUTACE = [
    ("M1", "ZNAČKA ČASU ZMIZÍ (vrací se vada R1)",
     " (stav před B1; dnes **40**)", "",
     True, "značka času „stav před"),
    ("M2", "CITACE SE STANE TVRZENÍM",
     "**„32 sloupců\"**", "**32 sloOpců**",
     True, "cituje cizí slova"),
    ("M3", "TABULKA LŽE (40 → 39)",
     "5 tabulek, **40 sloupců, českých 0**", "5 tabulek, **39 sloupců, českých 0**",
     True, "tvrdí 39"),
]

selhalo = []
vysledky = []
try:
    for kod_m, popis, najdi, nahrad, ma_spadnout, podminka in MUTACE:
        if kod_m == "M2":
            # M2 je zvláštní: mění UVOZOVKY, aby číslo přestalo být citací.
            #
            # ⚠ KOTVA SE 2. 10. 2026 ZPŘESNILA (naměřeno, vlastní omyl 95):
            # pouhé `**„32 sloupců"**` přestalo být jednoznačné, protože touž
            # session přibyl do `AGENTS.md` **odstavec, který vadu R1 popisuje**
            # — a v něm je ten řetězec **citovaný podruhé**. Test pak správně
            # odmítl mutovat („kotva 2x") a hlásil problém.
            # **Je to přesně past `overovani` §9.8**: kotva, kterou do dokumentu
            # přidá i JEHO VLASTNÍ POPIS. Proto se bere **delší, jednoznačné
            # okolí** — `…**, správně je` — které je v dokumentu jen jednou.
            najdi = "**„32 sloupců\"**, správně je"
            nahrad = "**32 sloupců**, správně je"

        text = orig.decode("utf-8")
        pocet = text.count(najdi)
        print("\n  %s) %s" % (kod_m, popis))
        print("     hledám: %s   (výskytů: %d)" % (najdi[:64], pocet))
        if pocet != 1:
            print("     NEZMUTOVÁNO — kotva není v souboru právě 1×.")
            selhalo.append("%s se neprovedla (kotva %dx)" % (kod_m, pocet))
            continue

        zmut = text.replace(najdi, nahrad)
        assert zmut != text, "%s: text se nezmenil!" % kod_m
        # §7.14: musí přestat platit MĚŘENÁ PODMÍNKA, ne jen změnit text.
        if kod_m == "M1":
            assert "stav před" not in zmut.split("**39**")[1][:40], "M1: značka času zůstala!"
            assert "(stav před B1; dnes **40**)" not in zmut, "M1: podmínka platí dál!"
        if kod_m == "M2":
            # Měřená podmínka: v MĚNĚNÉM okolí už uvozovky nejsou. (Druhý
            # výskyt řetězce — v odstavci, který vadu popisuje — zůstat MÁ;
            # proto se neassertuje „nikde v souboru", ale jen na té kotvě.)
            assert najdi not in zmut, "M2: uvozovky zůstaly!"
            assert "**32 sloupců**, správně je" in zmut, "M2: náhrada není v textu!"
        if kod_m == "M3":
            assert "**40 sloupců, českých 0**" not in zmut, "M3: tabulka se nezměnila!"

        AGENTS.write_text(zmut, encoding="utf-8", newline="")
        # PO ZÁPISU: vada musí být V SOUBORU (§7.9)
        na_disku = AGENTS.read_text(encoding="utf-8")
        assert najdi not in na_disku, "%s: vada v souboru NENÍ!" % kod_m

        kod, vystup = spust()
        spadla = kod != 0
        print("     %s" % souhrn(vystup))
        for r in rozchody(vystup):
            print("        %s" % r)
        ok = (spadla == ma_spadnout)
        print("     exit=%d → %s" % (kod, "SPRÁVNĚ SPADLA" if spadla else "PROŠLA"))
        if not ok:
            selhalo.append("%s: brána %s" % (kod_m, "nechytila vadu" if ma_spadnout
                                             else "padá i na zdravém stavu"))
        vysledky.append((kod_m, spadla, ma_spadnout))

        AGENTS.write_bytes(orig)

        # návrat MUSÍ být zelený — jinak je to nález o návratu, ne o bráně
        kod_n, vystup_n = spust()
        assert kod_n == 0, "%s: po vrácení originálu brána NEPROCHÁZÍ!" % kod_m
finally:
    AGENTS.write_bytes(orig)
    assert AGENTS.read_bytes() == orig, "AGENTS.md NEBYL vrácen bit po bitu!"

# ── M4: kontrolní běh na nezměněném souboru ────────────────────────────────
print("\n  M4) KONTROLNÍ BĚH (zdravý stav, beze změny souboru) — musí být exit 0")
kod4, vystup4 = spust()
print("     %s" % souhrn(vystup4))
print("     exit=%d → %s" % (kod4, "SPRÁVNĚ ZELENÁ" if kod4 == 0 else "PADÁ VŽDY!"))
if kod4 != 0:
    selhalo.append("M4: brána padá i na zdravém stavu → test by prošel vždy")
vysledky.append(("M4", kod4 != 0, False))

print("\n" + "=" * 92)
print("  VÝSLEDEK: %d mutací, %d chyceno, %d problémů"
      % (len(vysledky), sum(1 for _, s, m in vysledky if s == m), len(selhalo)))
for kod_m, spadla, ma in vysledky:
    print("     %-4s %s (čekáno: %s)" % (kod_m, "spadla" if spadla else "prošla",
                                         "spadne" if ma else "projde"))
print("     AGENTS.md vrácen bit po bitu: %s"
      % ("ANO" if AGENTS.read_bytes() == orig else "NE"))

if selhalo:
    print()
    for s in selhalo:
        print("  CHYBA: %s" % s)
    print("\nVYSLEDEK: brána NENÍ ověřená → exit 1")
    sys.exit(1)
print("\nVYSLEDEK: brána chytí vadu R1 (i citaci a lež v tabulce) a na zdravém"
      " stavu je zelená → MĚŘÍ. exit 0")
sys.exit(0)
