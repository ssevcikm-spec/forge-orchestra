# -*- coding: utf-8 -*-
r"""P28/B — MUTAČNÍ DŮKAZ MĚŘIDLA P28: umí spadnout, a spadne z PRAVÉHO důvodu?

PROČ: „Napsal jsi test? Vrať do kódu vadu a podívej se, že spadne“ (`AGENTS.md`).
A druhá polovina téhož: **„spadlo to“ není důkaz — důkaz je DIFERENCIÁL**
(naměřeno v P27: mutant spadl z jiného důvodu, `FileNotFoundError` v podsložce,
a měření to prošlo). Proto má každá mutace **tři nohy**:

    (a) živý artefakt + živé měřidlo      → 0 chyb        (kontrola)
    (b) MUTOVANÝ artefakt + živé měřidlo  → SPADNE        (měřidlo to vidí)
    (c) MUTOVANÝ artefakt + OSLABENÉ měřidlo → 0 chyb     (spadlo PRÁVĚ tou kontrolou)

Tři mutace:
  * **M1** — číslo v dokumentu (`**83/83**` → `**82/83**`): měřidlo musí číst
    tvrzení Z DOKUMENTU, ne ho mít zapečené;
  * **M2** — `g3` s 50. branou: měřidlo musí počítat brány z BĚHU, ne z hlavy;
  * **M3** — `ov-g` s vypnutým hlášením rozsahu: měřidlo musí měřit ROZSAH
    (zúžení rozsahu je vada P25-K — „zelená nad 1 % rozsahu“).

⚠ VŠECHNY MUTACE JSOU V KOPIÍCH (`_analyza/p28-b-scratch/`) — živý dokument,
živé `g3` ani živý `ov-g` se nemutují. Kopie měřidla se po běhu mažou.
⚠ `FORGE_REGISTR` míří do scratch: měřidlo NESMÍ přepsat živý registr bran
obsahem z fixtury (naměřeno 6. 10. 2026: v živém registru skončila fixtura
`A1: zdravá` a běh byl „zelený“).

Použití: python _analyza/p28-b-mutace.py
"""

import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
HANDOFF = WS / "HANDOFF.md"
G3 = ANALYZA / "g3-brany.py"
OV_G = ANALYZA / "ov-g-neovereno.py"
P28A = ANALYZA / "p28-a-overeni.py"
SCRATCH = ANALYZA / "p28-b-scratch"
REGISTR = SCRATCH / "registr-scratch.json"

sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj  # noqa: E402

kontrol = 0
chyb = 0
ENV = {"FORGE_REGISTR": str(REGISTR)}


def k(popis, zjisteno, ocekavano):
    global kontrol, chyb
    kontrol += 1
    if zjisteno == ocekavano:
        print("  OK    %s" % popis)
    else:
        chyb += 1
        print("  CHYBA %s\n        čekáno:   %r\n        naměřeno: %r"
              % (popis, ocekavano, zjisteno))


def cmd(argumenty, timeout=3600):
    r = subprocess.run([str(a) for a in argumenty], cwd=str(WS),
                       env={**os.environ, **ENV}, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def citac(v):
    m = None
    for m in re.finditer(r"VÝSLEDEK: (\d+) kontrol, (\d+) chyb", v):
        pass
    return (int(m.group(1)), int(m.group(2))) if m else None


def beh(meridlo, *argumenty, jmeno="vystup.txt"):
    """Spustí měřidlo s výstupem do SCRATCH (aby nepřepsalo ŽIVÝ doklad)."""
    return cmd([sys.executable, str(meridlo), *argumenty,
                "--vystup", str(SCRATCH / jmeno)])


def cervene(v):
    return [l.strip()[6:].strip() for l in v.splitlines() if l.strip().startswith("CHYBA ")]


def sekce(cislo, text):
    """Tělo oddílu `## <cislo>.` — mutuje se V NĚM, ne přes celý dokument."""
    m = re.search(r"^## %s\." % re.escape(str(cislo)), text, re.M)
    if not m:
        return ""
    m2 = re.search(r"^## ", text[m.end():], re.M)
    return text[m.start(): m.end() + m2.start()] if m2 else text[m.start():]


def vypis_cervene(v, popis):
    """Vypíše červené kontroly POMOCNÉHO běhu (jinak se „3 chyby“ nedá vysvětlit).

    ⚠ Naměřeno 8. 10. 2026: bez toho se u M3c hlásilo „3 chyby“ a NEBYLO VIDĚT
    které — a diagnostika se musela dělat zvláštním skriptem.
    """
    red = cervene(v)
    if red:
        print("      · %s: %d červených — první tři:" % (popis, len(red)))
        for x in red[:3]:
            print("          %s" % x[:110])


def oslabena_kopie(cil, stary, novy, popis):
    """Kopie měřidla s OSLABENOU kontrolou (kotva → náhrada), zapsaná natrvalo.

    `mutuj` soubor po bloku vrací — proto se mutant čte UVNITŘ bloku a zapisuje
    se až po vrácení. Kontroluje se, že kopie je KOMPILOVATELNÁ (nekompilovatelná
    „oslabená“ kopie by spadla z jiného důvodu a diferenciál by lhal).

    ⚠ Vrací `None`, když kotva v měřidle NENÍ právě 1× — a to je **CHYBA**, ne
    pád skriptu: naměřeno 8. 10. 2026, kdy kotva `(int(m.group(1)), …)` byla
    v měřidle 2× a skript spadl **uprostřed** (a zůstala po něm oslabená kopie).
    """
    shutil.copyfile(P28A, cil)
    try:
        with mutuj(cil, stary, novy):
            zmut = cil.read_bytes()
    except ValueError as e:
        k("%s: oslabenou kopii NELZE vyrobit" % popis, False, str(e)[:160])
        cil.unlink(missing_ok=True)
        return None
    cil.write_bytes(zmut)
    r = subprocess.run([sys.executable, "-m", "py_compile", str(cil)],
                       capture_output=True, text=True, timeout=120)
    k("%s: oslabená kopie je KOMPILOVATELNÁ" % popis, r.returncode, 0)
    return cil


def main():
    print("=" * 78)
    print("P28/B — MUTAČNÍ DŮKAZ MĚŘIDLA P28 (tři mutace, každá s diferenciálem)")
    print("=" * 78)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    k("kontrola: živé měřidlo P28 existuje", P28A.is_file(), True)
    osl = []

    # ⚠ KOPIE NÁSTROJŮ MUSÍ LEŽET VE STEJNÉM ADRESÁŘI JAKO ORIGINÁL. Nástroje
    # (`ov-g-neovereno.py`, `g3-brany.py`) si kořen repa odvozují jako
    # `Path(__file__).parents[1]` — kopie v PODSLOŽCE `p28-b-scratch/` tedy míří
    # o úroveň VÝŠ a měří úplně jiný strom: naměřeno 8. 10. 2026, kdy mutant
    # „spadl“ ze špatného důvodu (4 červené místo 1) a diferenciál nemohl vyjít.
    # Je to týž omyl, který má P27 zapsaný jako nález 10.
    k_o = ANALYZA / "_p28b-k-ovg.py"
    k_g = ANALYZA / "_p28b-k-g3.py"
    k("M2/M3 kontrola: kopie ov-g leží ve stejném adresáři jako originál",
      k_o.parent == OV_G.parent, True)
    k("M2/M3 kontrola: kopie g3 leží ve stejném adresáři jako originál",
      k_g.parent == G3.parent, True)
    shutil.copyfile(OV_G, k_o)
    shutil.copyfile(G3, k_g)

    # ─────────────────────── M1: číslo v DOKUMENTU (§57, které čte etapa A5) ─
    # ⚠ PRVNÍ POKUS MÍŘIL DO §56 („83/83“) — a byl ŠPATNĚ: měřidlo P28 čte
    # **§57/§58**, takže mutace v §56 nemohla zapnout žádnou jeho kontrolu
    # (a „živý dokument → 0 chyb“ padalo na pojmenovaných rozdílech STAVU, ne na
    # mutaci). Mutuje se proto tvrzení, které P28 OPRAVDU čte: §57 tvrdí
    # „**99 řádků Hxx**“ a etapa A5 ho srovnává s vlastním počítadlem.
    print("\n--- M1: číslo v dokumentu (§57 „99 řádků Hxx“ → „98“) ---")
    text = HANDOFF.read_text(encoding="utf-8")
    s57 = sekce("57", text)
    kotva = "**99 řádků Hxx**"
    k_ctl = SCRATCH / "k-handoff-ctl.md"
    k_mut = SCRATCH / "k-handoff-mut.md"
    k_ctl.write_bytes(HANDOFF.read_bytes())
    i57 = text.find(s57)
    k_mut.write_text(text[:i57] + s57.replace(kotva, "**98 řádků Hxx**", 1)
                     + text[i57 + len(s57):], encoding="utf-8")
    k("M1 kotva „99 řádků Hxx“ je v §57 právě 1×", s57.count(kotva), 1)
    k("M1 a mutace se provedla (v kopii je 98, v živém dokumentu ne)",
      (k_mut.read_text(encoding="utf-8").count("**98 řádků Hxx**"), text.count(kotva)),
      (1, s57.count(kotva)))

    kod, v = beh(P28A, "--jen", "A5", "--handoff", str(k_ctl), jmeno="m1a.txt")
    ca = citac(v)
    if (ca[1] if ca else -1) != 0:
        vypis_cervene(v, "M1a kontrola (NEMUTOVANÝ dokument)")
    k("M1a KONTROLA: NEMUTOVANÝ dokument + živé měřidlo → 0 chyb", ca[1] if ca else None, 0)
    k("M1a a měřidlo vůbec něco naměřilo (čítač > 5)", (ca[0] if ca else 0) > 5, True)

    kod, v = beh(P28A, "--jen", "A5", "--handoff", str(k_mut), jmeno="m1b.txt")
    cb = citac(v)
    k("M1b MUTOVANÝ dokument + živé měřidlo → VÍC chyb než kontrola",
      (cb[1] if cb else -1) > (ca[1] if ca else 10 ** 6), True)
    k("M1b a spadlo na kontrole, která to číslo ČTE z dokumentu",
      any("vlastní počet řádků Hxx" in x for x in cervene(v)), True)

    osl.append(oslabena_kopie(ANALYZA / "_p28b-oslabene-m1.py",
                              "celkem, int(tv[0]))", "celkem, celkem)", "M1"))
    if osl[-1] is None:
        print("  ??    M1c se neměří (oslabenou kopii nešlo vyrobit)")
    else:
        kod, v = beh(osl[-1], "--jen", "A5", "--handoff", str(k_mut), jmeno="m1c.txt")
        cc = citac(v)
        # ⚠ SROVNÁVÁ SE S KONTROLOU, ne s nulou: měřidlo může být červené i z JINÉHO
        # důvodu (stav mimo repo) — a pak by „0 chyb“ neměřilo diferenciál, ale cizí stav.
        k("M1c MUTOVANÝ dokument + OSLABENÉ měřidlo → stejně chyb jako kontrola",
          cc[1] if cc else None, ca[1] if ca else -1)
        k("M1c a oslabené měřidlo měřilo stejně kontrol jako živé (není to prázdný běh)",
          (cc[0] if cc else 0), (ca[0] if ca else -1))
    k("M1 dokument na disku je vrácen (sha256)", hashlib.sha256(HANDOFF.read_bytes()).hexdigest(),
      hashlib.sha256(text.encode("utf-8")).hexdigest())

    # ─────────────────────────────────────────── M2: počet BRAN v `g3` ────
    print("\n--- M2: `g3` s 50. branou (měřidlo musí počítat z BĚHU) ---")
    fixtura = SCRATCH / "fixtura-brana.py"
    fixtura.write_text('print("0 kontrol, 0 chyb")\n', encoding="utf-8")
    kod, v = beh(P28A, "--plne", "--jen", "A6", jmeno="m2a.txt")
    ca = citac(v)
    k("M2a živé g3 + živé měřidlo → měřidlo má čítač", ca is not None, True)
    chyby_a6 = ca[1] if ca else -1

    with mutuj(k_g, "BRANY = [",
               'BRANY= [("p28-fixtura", ["python", %r]),' % str(fixtura)):
        kod, v = beh(P28A, "--plne", "--jen", "A6", "--g3", str(k_g), jmeno="m2b.txt")
    cb = citac(v)
    k("M2b g3 s 50. branou + živé měřidlo → VÍC chyb než baseline",
      (cb[1] if cb else -1) > chyby_a6, True)
    k("M2b a spadlo na kontrole počtu bran",
      any("49 bran" in x for x in cervene(v)), True)

    osl.append(oslabena_kopie(
        ANALYZA / "_p28b-oslabene-m2.py",
        "int(m.group(1)) if m else None, 49)",
        "int(m.group(1)) if m else None, int(m.group(1)) if m else None)",
        "M2"))
    if osl[-1] is None:
        print("  ??    M2c se neměří (oslabenou kopii nešlo vyrobit)")
    else:
        with mutuj(k_g, "BRANY = [",
                   'BRANY= [("p28-fixtura", ["python", %r]),' % str(fixtura)):
            kod, v = beh(osl[-1], "--plne", "--jen", "A6", "--g3", str(k_g), jmeno="m2c.txt")
        cc = citac(v)
        k("M2c g3 s 50. branou + OSLABENÉ měřidlo → stejně chyb jako baseline (diferenciál)",
          cc[1] if cc else None, chyby_a6)

    # ─────────────────────────────────────── M3: ROZSAH měřidla `ov-g` ────
    print("\n--- M3: `ov-g` s vypnutým hlášením ROZSAHU (vada P25-K) ---")
    kod, v = beh(P28A, "--jen", "A5", jmeno="m3a.txt")
    ca = citac(v)
    k("M3a živé ov-g + živé měřidlo → 0 chyb", ca[1] if ca else None, 0)

    kotva_ovg = ('    print("\\n  ── MIMO ŽIVÉ ZDROJE (zmrazené kopie a zálohy'
                 ' — ZÁMĚRNĚ se nečtou) ──")')
    # ⚠ MUTACE MUSÍ MĚNIT JEDNU VLASTNOST, NE VÍC. První pokus vypínal CELÝ
    # VYPISOVACÍ řádek — a naměřeno: mutovaná brána pak shodila **4** kontroly
    # (i fixtury), takže diferenciál „oslabená kopie projde“ nemohl vyjít a byl
    # to **falešný nález o měřidle**. Dnes se mění jen ČÍSLO v hlášení rozsahu:
    # brána tvrdí „0 řádků mimo“, což je přesně ta vada P25-K (zúžení rozsahu).
    kotva_cisla = "celkem mimo: {sum(n for _, n in mimo)} řádků"
    with mutuj(k_o, kotva_cisla, "celkem mimo: {0} řádků"):
        # ⚠ KONTROLA MUTACE PATŘÍ DOVNITŘ BLOKU: `mutuj` soubor po bloku VRACÍ,
        # takže kontrola čtená po bloku hlásí „mutace není v kopii“ na SPRÁVNĚ
        # provedené mutaci (naměřeno 8. 10. 2026 — falešný poplach).
        k("M3b mutace rozsahu JE v kopii (brána tvrdí 0 řádků mimo)",
          "celkem mimo: {0} řádků" in k_o.read_text(encoding="utf-8"), True)
        kod, v = beh(P28A, "--jen", "A5", "--ovg", str(k_o), jmeno="m3b.txt")
    cb = citac(v)
    vypis_cervene(v, "M3b živé měřidlo + mutované ov-g")
    k("M3b mutované ov-g + živé měřidlo → aspoň 1 chyba",
      (cb[1] if cb else -1) >= 1, True)
    k("M3b a spadlo na kontrole ROZSAHU",
      any("ROZSAH" in x for x in cervene(v)), True)

    osl.append(oslabena_kopie(
        ANALYZA / "_p28b-oslabene-m3.py",
        "(sum(n for _, n in mimo), len(mimo)))",
        "((int(m2.group(1)), int(m2.group(2))) if m2 else None))",
        "M3"))
    if osl[-1] is None:
        print("  ??    M3c se neměří (oslabenou kopii nešlo vyrobit)")
    else:
        with mutuj(k_o, kotva_cisla, "celkem mimo: {0} řádků"):
            kod, v = beh(osl[-1], "--jen", "A5", "--ovg", str(k_o), jmeno="m3c.txt")
        cc = citac(v)
        if (cc[1] if cc else -1) != (ca[1] if ca else -1):
            vypis_cervene(v, "M3c oslabené měřidlo + mutované ov-g")
        k("M3c ov-g bez hlášení rozsahu + OSLABENÉ měřidlo → stejně chyb jako baseline",
          cc[1] if cc else None, ca[1] if ca else -1)

    # ─────────────────────────────────────────────────────────── úklid ────
    print("\n--- úklid: kopie měřidla ani scratch nesmí zůstat ---")
    for p in osl:
        p.unlink(missing_ok=True)
    k("oslabené kopie měřidla jsou smazané", [p.name for p in osl if p.exists()], [])
    # ⚠ I KOPIE NÁSTROJŮ (`k_o`, `k_g`) MUSÍ ZMIZET: leží v `_analyza/`, takže by
    # vstoupily do obsahového otisku inventáře a `g3` by hlásil zastaralý stav.
    for p in (k_o, k_g):
        p.unlink(missing_ok=True)
    k("kopie nástrojů (ov-g, g3) jsou smazané",
      [p.name for p in (k_o, k_g) if p.exists()], [])
    shutil.rmtree(SCRATCH, ignore_errors=True)
    k("scratch je smazaný", SCRATCH.exists(), False)

    print("\n" + "=" * 78)
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())
