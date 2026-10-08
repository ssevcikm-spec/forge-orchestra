# -*- coding: utf-8 -*-
r"""P27 — ÚKOL A (důkaz): UMÍ MĚŘIDLO `p27-a-overeni.py` VŮBEC SPADNOUT?

PROČ TENHLE SKRIPT EXISTUJE
--------------------------
`AGENTS.md`: *„Napsal jsi test? Vrať do kódu vadu a podívej se, že spadne.
Mutační test je jediný důkaz, že test měří."* — a `p27-a-overeni.py` tvrdí
o práci P26 sedm věcí. Kdyby umělo jen „vždy OK", jeho čísla by nic nedokazovala.

CO SE U KAŽDÉ MUTACE MĚŘÍ (a proč je to takhle rozdělené):
  a) **mutace se OPRAVDU provedla** (hash před != po, text se změnil);
  b) **ORIGINÁL měřidla na té vadě SPADNE** (`exit != 0`);
  c) **a spadne z TOHO SPRÁVNÉHO důvodu** (jméno konkrétní kontroly);
  d) **DIFFERENCIÁL**: OSLABENÁ kopie měřidla (bez TÉ JEDNÉ kontroly) na TÉŽE
     vadě **PROJDE** → vadu chytá právě ta kontrola, a ne něco jiného
     (past „změnilo se i něco jiného", `overovani` §9).

MUTACE (všechno v KOPIÍCH — živý strom se NEmutuje):
  M1  `HANDOFF.md` bez oddílu **§56** (číslo v dokumentu zmizí) → A4 musí spadnout
      na kontrole ROZSAHU. Tím se dokazuje, že měřidlo **čte tvrzení z dokumentu**
      a že zelená není nad dokumentem, který neotevřelo.
  M2  **KOPIE TESTU TIKU bez bloku `AC`** (`/workers`) → A2 musí spadnout na
      kontrole „zarážka ZAPLA kontroly `AC:`". Tím se dokazuje, že A2 opravdu
      měří, že **test ten endpoint volá** — kdyby stačilo „zarážka se provedla",
      prošla by i nad testem, který endpoint nevolá vůbec.
  M3  **`ov-g-neovereno.py` se ZÚŽENÝM rozsahem** (archiv vypadne ze živých
      zdrojů) → A5 musí spadnout na ROZSAHU (1 místo 99). Tím se dokazuje, že
      A5 měří rozsah VLASTNÍM průchodem, ne tím, že opíše výpis brány.

Použití: python _analyza/p27-b-mutace.py
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
MERIDLO = ANALYZA / "p27-a-overeni.py"
OV_G = ANALYZA / "ov-g-neovereno.py"
HANDOFF = WS / "HANDOFF.md"
TEST_TIK = WS / "tools" / "test-tick-offline.mjs"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
SRC = WS / "conductor" / "src" / "index.ts"
P20_D = ANALYZA / "p20-d-doklady.py"
SCRATCH = ANALYZA / "p27-b-scratch"
KOPIE_TESTU = WS / "tools" / "p27-b-kopie-tick.mjs"

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


def cmd(argumenty, timeout=3600):
    r = subprocess.run(argumenty, cwd=str(WS), capture_output=True, timeout=timeout)
    return r.returncode, (r.stdout.decode("utf-8", "replace")
                          + r.stderr.decode("utf-8", "replace"))


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def cervene(v):
    return [l.strip()[len("CHYBA"):].strip() for l in v.splitlines()
            if l.strip().startswith("CHYBA")]


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
    text = premenuj(MERIDLO.read_text(encoding="utf-8"), dvojice,
                    "oslabení %s" % nazev)
    cil = ANALIZA / ("_p27oslab-%s.py" % nazev)
    zapis(cil, text)
    return cil


def beh(meridlo, etapa, dalsi=()):
    return cmd([sys.executable, "-B", str(meridlo), "--jen", etapa] + list(dalsi))


def uklid():
    for p in list(ANALYZA.glob("_p27oslab-*.py")):
        p.unlink(missing_ok=True)
    for p in list(ANALYZA.glob("_p27-*.py")):
        p.unlink(missing_ok=True)
    for p in list((WS / "tools").glob("p27-b-*.mjs")):
        p.unlink(missing_ok=True)
    shutil.rmtree(SCRATCH, ignore_errors=True)


def main() -> int:
    print("=" * 78)
    print("P27/B — UMÍ MĚŘIDLO P27 SPADNOUT? (tři mutace v KOPIÍCH + diferenciál)")
    print("=" * 78)

    uklid()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    zive = {str(p): sha(p) for p in
            (OV_G, HANDOFF, MERIDLO, TEST_TIK, KRONIKA, SRC, P20_D)}
    try:
        # ────────────────── M1: DOKUMENT BEZ ODDÍLU §56 ────────────────────
        print("\n--- M1: `HANDOFF.md` bez oddílu §56 (číslo v dokumentu zmizí) ---")
        text = HANDOFF.read_text(encoding="utf-8")
        kotva = "## 56. P26 —"
        k("M1 kotva oddílu §56 je v dokumentu právě 1×", text.count(kotva), 1)
        if text.count(kotva) == 1:
            kopie_h = SCRATCH / "k-handoff.md"          # jméno NEzačíná „handoff"
            zmut = text.replace(kotva, "## 5X. P26 —", 1)
            zapis(kopie_h, zmut)
            k("M1 mutace se opravdu provedla (§56 v kopii není)",
              "## 56. P26 —" not in zmut and "## 5X. P26 —" in zmut, True)
            kod, v = beh(MERIDLO, "A4", ["--handoff", str(kopie_h)])
            k("M1 ORIGINÁL měřidla bez §56 SPADNE", kod != 0, True)
            k("M1 a spadne na KONTROLE ROZSAHU §56",
              any("§56 existuje" in l for l in cervene(v)), True)
            osl1 = oslabene_meridlo("m1", [(
                '    check("A4 §56 existuje a je netriviálně dlouhý (délka %d znaků)" % len(s56),\n'
                '          len(s56) > 3000, True)\n', "    pass\n")])
            k("M1 oslabení se opravdu uložilo (kontrola §56 v kopii není)",
              "§56 existuje" not in osl1.read_text(encoding="utf-8"), True)
            kod2, _ = beh(osl1, "A4", ["--handoff", str(kopie_h)])
            k("M1a DIFFERENCIÁL: oslabená kopie na TÉŽE vadě PROJDE", kod2, 0)
            k("M1a tedy vadu chytá kontrola ROZSAHU §56 (ne něco jiného)",
              kod2 != kod, True)

        # ────────────── M2: TEST BEZ BLOKU `AC` (/workers) ─────────────────
        print("\n--- M2: kopie testu tiku BEZ bloku `AC` (`/workers`) ---")
        tt = TEST_TIK.read_text(encoding="utf-8")
        ia = tt.find("  // ── AC) /workers")
        ib = tt.find("  // ── AD) /games")
        k("M2 v testu je blok `AC` i blok `AD`", (ia > 0 and ib > ia), True)
        if ia > 0 and ib > ia:
            usek = tt[ia:ib]
            k("M2 blok `AC` obsahuje kontroly (nejde o prázdný výřez)",
              usek.count("check('AC") >= 1, True)
            shutil.copyfile(TEST_TIK, KOPIE_TESTU)
            try:
                with_mut = premenuj(KOPIE_TESTU.read_text(encoding="utf-8"),
                                    [(usek, "")], "M2 odebrání bloku AC")
                zapis(KOPIE_TESTU, with_mut)
                k("M2 mutace se opravdu provedla (blok `AC` v kopii není)",
                  "check('AC" not in KOPIE_TESTU.read_text(encoding="utf-8"), True)
                kod, v = beh(MERIDLO, "A2", ["--test", str(KOPIE_TESTU)])
                k("M2 ORIGINÁL měřidla nad testem bez `AC` SPADNE", kod != 0, True)
                k("M2 a spadne na kontrole „zarážka ZAPLA kontroly `AC:`“",
                  any("zarážka ZAPLA kontroly `AC:`" in l for l in cervene(v)), True)
                osl2 = oslabene_meridlo("m2", [(
                    "              len(cilene) >= 1, True)",
                    "              True, True)")])
                k("M2 oslabení se opravdu uložilo (podmínka `len(cilene) >= 1` v kopii není)",
                  "len(cilene) >= 1" not in osl2.read_text(encoding="utf-8"), True)
                kod2, _ = beh(osl2, "A2", ["--test", str(KOPIE_TESTU)])
                k("M2a DIFFERENCIÁL: oslabená kopie na TÉŽE vadě PROJDE", kod2, 0)
                k("M2a tedy vadu chytá kontrola „zarážka ZAPLA kontroly“",
                  kod2 != kod, True)
            finally:
                KOPIE_TESTU.unlink(missing_ok=True)
        k("M2 v `tools/` nezůstala kopie testu", KOPIE_TESTU.exists(), False)

        # ─────────── M3: BRÁNA SE ZÚŽENÝM ROZSAHEM (nález P25-K) ───────────
        print("\n--- M3: `ov-g-neovereno.py` se ZÚŽENÝM rozsahem (1 řádek) ---")
        uzka = SCRATCH / "k-ovg-uzka.py"
        zapis(uzka, premenuj(
            OV_G.read_text(encoding="utf-8"),
            [('    if arch.is_dir():\n'
              '        zdroje += sorted(p for p in arch.iterdir()\n'
              '                         if p.is_file() and p.name.startswith("HANDOFF-")\n'
              '                         and p.suffix == ".md")\n',
              '')],
            "M3 zúžení rozsahu"))
        kod, v = cmd([sys.executable, "-B", str(uzka)])
        m = re.search(r"nálezů \(řádků tabulek Hxx\) CELKEM:\s*(\d+)", v)
        k("M3 zúžená kopie OPRAVDU měří 1 řádek (ne jen text se změnil)",
          int(m.group(1)) if m else None, 1)
        kod, v = beh(MERIDLO, "A5", ["--ovg", str(uzka)])
        k("M3 ORIGINÁL měřidla na zúžené bráně SPADNE", kod != 0, True)
        k("M3 a spadne na KONTROLE ROZSAHU (měřidlo hlásí 99 řádků)",
          any("měří 99 řádků Hxx" in l for l in cervene(v)), True)
        osl3 = oslabene_meridlo("m3", [
            ('    check("A5 živé měřidlo měří 99 řádků Hxx", '
             'int(mr.group(1)) if mr else None, 99)\n', "    pass\n"),
            ('    check("A5 a jeho součet po souborech = MŮJ součet (ne jen totéž číslo)",\n'
             '          sum(int(n) for _, n in otevreno), soucet)\n', "    pass\n"),
            ('    check("A5 a VYPISUJE, které soubory otevřelo (`OTEVŘENO:`)", '
             'len(otevreno), 3)\n', "    pass\n")])
        k("M3 oslabení se opravdu uložilo (kontroly rozsahu v kopii nejsou)",
          ("měří 99 řádků Hxx" not in osl3.read_text(encoding="utf-8")
           and "OTEVŘENO:" not in osl3.read_text(encoding="utf-8")), True)
        kod2, _ = beh(osl3, "A5", ["--ovg", str(uzka)])
        k("M3a DIFFERENCIÁL: oslabená kopie na TÉŽE vadě PROJDE", kod2, 0)
        k("M3a tedy vadu chytá kontrola ROZSAHU, ne něco jiného", kod2 != kod, True)

        # ──────────────────────────────────────────────── STAV PO MUTACÍCH ─
        print("\n--- Stav po mutacích ---")
        uklid()
        k("S1 živé soubory zůstaly BEZ mutací (hash před == po)",
          [p for p, h in zive.items() if sha(p) != h], [])
        k("S2 v `_analyza/` nezůstala žádná pracovní kopie",
          sorted(p.name for p in ANALYZA.glob("_p27oslab-*.py"))
          + sorted(p.name for p in ANALYZA.glob("_p27-*.py")), [])
        k("S3 v `tools/` nezůstala žádná kopie testu tiku",
          sorted(p.name for p in (WS / "tools").glob("p27-b-*.mjs")), [])
        kod, v = cmd(["tools\\git.cmd", "-C", str(WS), "status", "--porcelain", "--",
                      "conductor/src/index.ts", "tools/test-tick-offline.mjs"])
        k("S4 v živém zdroji a testu není necommitnutá změna (POZOR: práce P27/B1 "
          "musí být commitnutá, jinak je to STAV, ne nález)", v.strip(), "")
        k("S5 mutant v ŽIVÉM zdroji conductora se neobjevil",
          "zarazka-p27" in SRC.read_text(encoding="utf-8"), False)
    finally:
        uklid()

    print("\n" + "=" * 78)
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())
