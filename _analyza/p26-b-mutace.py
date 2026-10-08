# -*- coding: utf-8 -*-
r"""P26 — ÚKOL A (důkaz): UMÍ MĚŘIDLO `p26-a-overeni.py` VŮBEC SPADNOUT?

PROČ TENHLE SKRIPT EXISTUJE
---------------------------
`AGENTS.md`: *„Napsal jsi test? Vrať do kódu vadu a podívej se, že spadne.
Mutační test je jediný důkaz, že test měří."* — a `p26-a-overeni.py` tvrdí
o práci P25 šest věcí. Kdyby umělo jen „vždy OK", jeho čísla by nic nedokazovala
(`overovani` §7).

CO SE U KAŽDÉ MUTACE MĚŘÍ (a proč je to takhle rozdělené):
  a) **mutace se OPRAVDU provedla** (hash před != po, text se změnil) —
     „mutace, která se tiše neprovede, tvrdí totéž co mutace, která projde";
  b) **ORIGINÁL měřidla na té vadě SPADNE** (`exit != 0`);
  c) **a spadne z TOHO SPRÁVNÉHO důvodu** (jméno konkrétní kontroly);
  d) **DIFERENCIÁL**: OSLABENÁ kopie měřidla (bez té JEDNÉ kontroly) na TÉŽE
     vadě **PROJDE** → vadu chytá právě ta kontrola, a ne něco jiného
     (past „změnil se i stav", `overovani` §9).

MUTACE (všechno v KOPIÍCH — živý strom se NEmutuje):
  M1  `ov-g-neovereno.py` s **zúženým rozsahem** (archiv vypadne z `zive_zdroje`)
      → vrací 1 řádek místo 99; doplněno o verzi z `HEAD`, která měří totéž
      historicky (nález P25-K).
  M2  `ov-g-neovereno.py` bez **pojistky na prázdný rozsah** → na prázdné
      fixtuře vrátí `exit 0` (zelená nad ničím).
  M3  `HANDOFF.md` s číslem v §55 posunutým (`83/83` → `82/83`).

⚠ M2 a M3 míří na DVĚ RŮZNÉ VĚCI, které se pletou: M2 je o tom, že měřidlo
**nemá jak selhat**; M3 je o tom, že měřidlo **čte tvrzení z dokumentu** (a ne
vlastní zapečené číslo).

Použití: python _analyza/p26-b-mutace.py
"""

import hashlib
import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
MERIDLO = ANALYZA / "p26-a-overeni.py"
OV_G = ANALYZA / "ov-g-neovereno.py"
HANDOFF = WS / "HANDOFF.md"
SCRATCH = ANALYZA / "p26-b-scratch"

kontrol = 0
chyb = 0


def k(popis, zjisteno, ocekavano):
    global kontrol, chyb
    kontrol += 1
    if zjisteno == ocekavano:
        print("  OK    %s" % popis)
        return True
    chyb += 1
    print("  CHYBA %s\n          čekáno: %r\n          dáno:   %r"
          % (popis, ocekavano, zjisteno))
    return False


def cmd(argumenty, timeout=1800):
    r = subprocess.run(argumenty, cwd=str(WS), capture_output=True, timeout=timeout)
    return r.returncode, (r.stdout.decode("utf-8", "replace")
                          + r.stderr.decode("utf-8", "replace"))


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def cervene(v):
    return [l.strip()[len("CHYBA"):].strip() for l in v.splitlines()
            if l.strip().startswith("CHYBA")]


def blob(rev, cesta):
    r = subprocess.run(["tools\\git.cmd", "-C", str(WS), "show", "%s:%s" % (rev, cesta)],
                       capture_output=True, shell=True, timeout=120)
    return r.stdout if r.returncode == 0 else None


def zapis(cesta, obsah):
    pathlib.Path(cesta).write_bytes(obsah if isinstance(obsah, bytes)
                                    else obsah.encode("utf-8"))


def premenuj(text, dvojice, popis):
    """Provede náhrady a KAŽDOU ověří (kotva právě 1×, text se změnil)."""
    for stary, novy in dvojice:
        n = text.count(stary)
        if n != 1:
            raise ValueError("%s: kotva je v souboru %d× (musí být 1×): %r"
                             % (popis, n, stary[:70]))
        text2 = text.replace(stary, novy, 1)
        if text2 == text:
            raise ValueError("%s: náhrada NIC nezměnila: %r" % (popis, stary[:70]))
        text = text2
    return text


def oslabene_meridlo(nazev, dvojice):
    text = premenuj(MERIDLO.read_text(encoding="utf-8"), dvojice, "oslabení %s" % nazev)
    cil = ANALYZA / ("_p26-oslabene-%s.py" % nazev)
    zapis(cil, text)
    return cil


def beh(meridlo, etapa, dalsi=(), vystup=None):
    prikaz = [sys.executable, "-B", str(meridlo), "--jen", etapa] + list(dalsi)
    if vystup:
        prikaz += ["--vystup", str(vystup)]
    return cmd(prikaz)


def main() -> int:
    print("=" * 78)
    print("P26/B — UMÍ MĚŘIDLO P26 SPADNOUT? (tři mutace v KOPIÍCH + diferenciál)")
    print("=" * 78)

    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True, exist_ok=True)

    # Hashe ŽIVÝCH souborů PŘED — na konci se musí vrátit (past P24-A:
    # přerušený běh nechal v živém zdroji čtyři mutanty).
    zive = {str(p): sha(p) for p in
            (OV_G, HANDOFF, MERIDLO, WS / "KRONIKA-PROJEKTU.md",
             WS / "conductor" / "src" / "index.ts",
             WS / "tools" / "test-tick-offline.mjs")}
    vystup = SCRATCH / "vystup.txt"
    try:
        # ─────────────────────── M1: ZÚŽENÝ ROZSAH BRÁNY (nález P25-K) ────
        print("\n--- M1: `ov-g-neovereno.py` se ZÚŽENÝM rozsahem (1 řádek) ---")
        # ⚠ NE `HEAD` NASLEPO: po commitu opravy je v `HEAD` už OPRAVENÁ verze
        # (naměřeno 7. 10. 2026). Hledá se ZPĚT, dokud se nenajde verze, která
        # čte 1 řádek — jinak by „důkaz P25-K" spadl na správně opraveném repu.
        # ⚠ OKNO SE ROZŠÍŘILO 8. 10. 2026 (P27, nález P27-Q): původní rozsah
        # `HEAD`…`HEAD~4` stačil, dokud byly P25+P26 poslední commity. Po dvou
        # commitech P27 se verze PŘED opravou (`ef58327`) posunula na `HEAD~5`
        # — a **důkaz P25-K se tiše rozpadl** (naměřeno: `p26-b` **26/4**,
        # „verze měřidla PŘED opravou nalezena v historii (None)").
        # Pevné okno je **křehké**: s každým dalším commitem se zub posouvá.
        # Hledá se proto dál (a když se nenajde, hlásí se to NAHLAS).
        hist = ANALYZA / "_p26-blind-head.py"
        nalezeno = None
        for rev in ["HEAD"] + ["HEAD~%d" % k for k in range(1, 21)]:
            b = blob(rev, "_analyza/ov-g-neovereno.py")
            if b is None:
                continue
            zapis(hist, b)
            kod, v = cmd([sys.executable, "-B", str(hist)])
            m = re.search(r"nálezů \(řádků tabulek Hxx\):\s*(\d+)", v)
            if m and int(m.group(1)) == 1:
                nalezeno = rev
                break
        hist.unlink(missing_ok=True)
        k("M1a verze měřidla PŘED opravou nalezena v historii (%s)" % nalezeno,
          nalezeno is not None, True)
        k("M1a ta verze měří JEN 1 řádek Hxx (P25-K jako fakt)",
          bool(nalezeno), True)

        # Zúžení je přesně ta vada: vypadne archiv z `zive_zdroje()`.
        uzka = ANALYZA / "_p26-uzka.py"
        zapis(uzka, premenuj(
            OV_G.read_text(encoding="utf-8"),
            [('    if arch.is_dir():\n'
              '        zdroje += sorted(p for p in arch.iterdir()\n'
              '                         if p.is_file() and p.name.startswith("HANDOFF-")\n'
              '                         and p.suffix == ".md")\n',
              '')],
            "M1 zúžení rozsahu"))
        kod, v = cmd([sys.executable, "-B", str(uzka)])
        m = re.search(r"nálezů \(řádků tabulek Hxx\) CELKEM:\s*(\d+)", v)
        k("M1b zúžená kopie OPRAVDU měří 1 řádek (ne jen text se změnil)",
          int(m.group(1)) if m else None, 1)
        kod, v = beh(MERIDLO, "A5", ["--ovg", str(uzka)], vystup)
        k("M1b ORIGINÁL měřidla na zúžené bráně SPADNE", kod != 0, True)
        k("M1b a spadne na KONTROLE ROZSAHU (99 řádků Hxx)",
          any("měří 99 řádků Hxx" in l for l in cervene(v)), True)
        # Diferenciál musí sundat VŠECHNY kontroly, které na zúženém rozsahu
        # padají: rozsah (99) i POČET OTEVŘENÝCH ZDROJŮ. Obojí je kontrola
        # ROZSAHU — a přesně to se tu dokazuje.
        osl1 = oslabene_meridlo("m1", [
            ('    check("A5 živé měřidlo měří 99 řádků Hxx (1 + 98)", '
             'int(mr.group(1)) if mr else None, 99)\n', "    pass\n"),
            ('    check("A5 a VYPISUJE, které soubory otevřelo (`OTEVŘENO:`)",\n'
             '          len(re.findall(r"^  OTEVŘENO:", v, re.M)), 3)\n',
             "    pass\n")])
        k("M1c oslabení se opravdu uložilo (kontroly rozsahu v kopii nejsou)",
          ("měří 99 řádků Hxx" not in osl1.read_text(encoding="utf-8")
           and "OTEVŘENO:" not in osl1.read_text(encoding="utf-8")), True)
        kod2, _ = beh(osl1, "A5", ["--ovg", str(uzka)], vystup)
        k("M1c DIFFERENCIÁL: oslabená kopie na TÉŽE vadě PROJDE", kod2, 0)
        k("M1c tedy vadu chytá kontrola ROZSAHU (ne něco jiného)", kod2 != kod, True)

        # ─────────────────── M2: BRÁNA BEZ POJISTKY NA PRÁZDNÝ ROZSAH ────
        print("\n--- M2: `ov-g-neovereno.py` bez pojistky na PRÁZDNÝ rozsah ---")
        stary = ('        print("Zelená nad prázdným rozsahem není měření (P25-K).")\n'
                 '        print("=" * 90)\n'
                 '        return 1\n')
        bez = ANALYZA / "_p26-bez-pojistky.py"
        zapis(bez, premenuj(OV_G.read_text(encoding="utf-8"),
                            [(stary,
                              '        print("Zelená nad prázdným rozsahem není měření (P25-K).")\n')],
                            "M2 odebrání pojistky"))
        k("M2 pojistka se opravdu odebrala (řádek `return 1` v kopii není)",
          "        return 1\n" not in bez.read_text(encoding="utf-8"), True)
        kod, v = beh(MERIDLO, "A5", ["--ovg", str(bez)], vystup)
        k("M2 ORIGINÁL měřidla na bráně bez pojistky SPADNE", kod != 0, True)
        ch = cervene(v)
        k("M2 a spadne na kontrole PRÁZDNÉHO ROZSAHU",
          any("prázdný rozsah" in l for l in ch), True)
        k("M2 ale kontrola „fixtura s NEOVĚŘENO“ NEpadla (nespadlo naslepo)",
          any("fixtura" in l for l in ch), False)
        osl2 = oslabene_meridlo("m2", [
            ('    check("A5 NEGATIVNÍ KONTROLA: prázdný rozsah → NEMĚŘENO '
             '(exit 1)", kod, 1)\n', "    pass\n"),
            ('    check("A5 a řekne to slovy (ne tichá zelená)", '
             '"NEMĚŘENO" in v, True)\n', "    pass\n")])
        kod2, _ = beh(osl2, "A5", ["--ovg", str(bez)], vystup)
        k("M2a DIFFERENCIÁL: oslabená kopie na TÉŽE vadě PROJDE", kod2, 0)
        k("M2a tedy vadu chytá pojistka PRÁZDNÉHO ROZSAHU", kod2 != kod, True)

        # ───────────────── M3: ČÍSLO PŘEČTENÉ Z DOKUMENTU (§55) ───────────
        print("\n--- M3: §55 s posunutým číslem (83/83 → 82/83) ---")
        text = HANDOFF.read_text(encoding="utf-8")
        # ⚠ MUTACE SE DĚLÁ POUZE UVNITŘ §55. Naměřeno 7. 10. 2026: kotva, která
        # je v dokumentu JEDNOZNAČNÁ, může být v JINÉM oddílu — mutace se pak
        # „provede", ale měřené tvrzení zůstane nezměněné a diferenciál to
        # odhalí jako „originál nespadl".
        stary = "`handoff-kontrola-uplnost` \u2192 **83/83**"
        novy_jen = "`handoff-kontrola-uplnost` \u2192 **82/83**"
        m55 = re.search(r"\n## 55\.", text)
        i = m55.start() if m55 else None
        m2 = re.search(r"\n## ", text[i + 4:]) if i is not None else None
        j = i + 4 + m2.start() if (i is not None and m2) else (len(text) if i is not None else 0)
        sekce55 = text[i:j] if i is not None else ""
        k("M3 kotva je v §55 právě 1× (ne jen v dokumentu)",
          sekce55.count(stary), 1)
        if sekce55.count(stary) == 1:
            kopie_h = SCRATCH / "handoff.md"
            zmut = text[:i] + sekce55.replace(stary, novy_jen, 1) + text[j:]
            zapis(kopie_h, zmut)
            k("M3 číslo v §55 KOPIE se opravdu změnilo (a je to v §55)",
              ("**82/83**" in zmut and zmut.count("**83/83**") < text.count("**83/83**")),
              True)
            kod, v = beh(MERIDLO, "A4", ["--handoff", str(kopie_h)], vystup)
            k("M3 ORIGINÁL měřidla nad posunutým číslem SPADNE", kod != 0, True)
            k("M3 a spadne na KONTROLE, KTERÁ ČTE TVRZENÍ Z DOKUMENTU",
              any("úplnost handoffu = tvrzených" in l for l in cervene(v)), True)
            osl3 = oslabene_meridlo("m3", [(
                '        check("A4 úplnost handoffu = tvrzených %d/%d" % tv,\n'
                '              (int(m.group(1)), int(m2.group(1))), tv)\n',
                "        pass\n")])
            k("M3 oslabení se opravdu uložilo (porovnání s §55 v kopii není)",
              "úplnost handoffu = tvrzených" not in osl3.read_text(encoding="utf-8"),
              True)
            kod2, _ = beh(osl3, "A4", ["--handoff", str(kopie_h)], vystup)
            k("M3a DIFFERENCIÁL: oslabená kopie na TÉŽE vadě PROJDE", kod2, 0)
            k("M3a tedy vadu chytá čtení TVRZENÍ Z §55", kod2 != kod, True)

        # ──────────────────────────────────────────────── STAV PO MUTACÍCH ─
        print("\n--- Stav po mutacích ---")
        # Nejdřív UKLIDIT pracovní kopie, teprve pak měřit, že nezůstaly.
        for p in list(ANALYZA.glob("_p26-*.py")):
            p.unlink(missing_ok=True)
        k("S1 živé soubory zůstaly BEZ mutací (hash před == po)",
          [p for p, h in zive.items() if sha(p) != h], [])
        k("S2 v `_analyza/` nezůstala žádná pracovní kopie",
          sorted(p.name for p in ANALYZA.glob("_p26-*.py")), [])
        k("S3 v `tools/` nezůstala žádná kopie testu tiku",
          sorted(p.name for p in (WS / "tools").glob("p26-*.mjs")), [])
        kod, v = cmd(["tools\\git.cmd", "-C", str(WS), "status", "--porcelain", "--",
                      "conductor/src/index.ts", "tools/test-tick-offline.mjs"])
        k("S4 v živém zdroji a testu není necommitnutá změna", v.strip(), "")
        k("S5 mutant v ŽIVÉM zdroji conductora se neobjevil",
          "zarazka-p26" in (WS / "conductor" / "src" / "index.ts").read_text(
              encoding="utf-8"), False)
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)
        for p in list(ANALYZA.glob("_p26-*.py")):
            p.unlink(missing_ok=True)

    print("\n" + "=" * 78)
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())
