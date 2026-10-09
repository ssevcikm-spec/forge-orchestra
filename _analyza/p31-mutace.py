# -*- coding: utf-8 -*-
r"""P31 — MUTAČNÍ TEST OPRAVY C1 A C2: dokazuje, že opravy MĚŘÍ.

PROČ: `AGENTS.md` — „Napsal jsi test? Vrať do kódu vadu a podívej se, že spadne.“
A druhá polovina téhož: **„spadlo to“ není důkaz — důkaz je DIFERENCIÁL.**

CO SE MĚŘÍ (každá noha SPOUŠTÍ kód, ne že ho čte):

  * **C1-a (integrace):** živé `p28-b-mutace.py` po opravě → **0 chyb**
    (před opravou hlásilo **27/2** — naměřeno v P31).
  * **C1-b (diferenciál na TÉŽE vstupní dvojici):** funkce `kotva_m1` živého
    měřidla se zavolá nad živým `HANDOFF.md` + jeho zmutovanou kopií §57 — a to
    i v **oslabené kopii** měřidla, kde je **vrácena PŮVODNÍ vada** (kotva
    v CELÉM dokumentu). Živá verze musí sedět, oslabená **nesmí** — jinak by
    kontrola neměřila nic (H131).
  * **C1-c (H132):** mutace `BRANY` v `g3` se **spustí** — se starým zápisem
    (2 prvky) mutant spadne na `ValueError`, s novým (3 prvky) vykáže
    **50 bran**. Tím se dokazuje, že se M2 neměří na tracebacku.
  * **C2 (H124):** `p29-a-overeni.py --jen A1M13` po sobě **nezanechá** v živém
    `_analyza/` žádného mutanta — a v **oslabené kopii** (úklid vypnutý) je
    **zanechá**, takže kontrola „nezůstal žádný mutant“ opravdu měří.

⚠ BĚHEM TOHOHLE BĚHU SE ZAPISUJE DO STROMU (kopie mutantů) — nepouštěj souběžně
jiné měřidlo. Všechny mutanty se na konci mažou a test to ověřuje.

Použití: python _analyza/p31-mutace.py
"""

import importlib.util
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
HANDOFF = WS / "HANDOFF.md"
P28B = ANALYZA / "p28-b-mutace.py"
P29A = ANALYZA / "p29-a-overeni.py"
G3 = ANALYZA / "g3-brany.py"
SCRATCH = ANALYZA / "p31-scratch"
OSL_C1 = ANALYZA / "_p31-mut-p28b.py"
OSL_C2 = ANALYZA / "_p31-mut-p29a.py"
DOKLAD = ANALYZA / "p31-mutace-vystup.txt"

sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj  # noqa: E402

ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
_vystup = []
kontrol = 0
chyb = 0

# Tvar kontroly v ŽIVÉM měřidle (kotva v měřeném oddílu) a PŮVODNÍ (v celém
# dokumentu) — záměna jednoho za druhé je „vrácení vady do kódu“.
NOVY_TVAR = ('    return ((sekce("57", kopie_text).count("**98 řádků Hxx**"),\n'
             '             s57.count("**98 řádků Hxx**")), (1, 0))')
STARY_TVAR = ('    return ((kopie_text.count("**98 řádků Hxx**"),\n'
              '             text.count("**99 řádků Hxx**")), '
              '(1, s57.count("**99 řádků Hxx**")))')
# Úklid v živém `p29-a-overeni.py` a jeho vypnutá varianta.
UKLID_ZIVY = ('    for jmeno in MUTANTI:\n'
              '        (ANALYZA / jmeno).unlink(missing_ok=True)\n'
              '    return [jmeno for jmeno in MUTANTI if (ANALYZA / jmeno).exists()]')
# ⚠ Vypnutá varianta NESMÍ obsahovat živý text jako PODŘETĚZEC — `_mutace.mutuj`
# to hlídá (omyly #18/#106) a musela by mít jiný tvar, ne jen uříznutý řádek.
UKLID_VYPNUTY = ('    zbyle = [jmeno for jmeno in MUTANTI\n'
                 '             if (ANALYZA / jmeno).exists()]\n'
                 '    return zbyle')


def p(radek=""):
    print(radek)
    _vystup.append(radek)


def k(popis, zjisteno, ocekavano):
    global kontrol, chyb
    kontrol += 1
    if zjisteno == ocekavano:
        p("  OK    %s" % popis)
        return True
    chyb += 1
    p("  CHYBA %s\n        čekáno:   %r\n        naměřeno: %r"
      % (popis, ocekavano, zjisteno))
    return False


def cmd(args, timeout=3600, env=None):
    r = subprocess.run([str(a) for a in args], cwd=str(WS), env={**ENV, **(env or {})},
                       capture_output=True, timeout=timeout)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace") + \
        (r.stderr or b"").decode("utf-8", "replace")


def citac(v):
    """Poslední čítač „VÝSLEDEK: N kontrol, M chyb“ ve výstupu."""
    vse = list(re.finditer(r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb", v))
    return (int(vse[-1].group(1)), int(vse[-1].group(2))) if vse else None


def nacti_modul(cesta, jmeno):
    spec = importlib.util.spec_from_file_location(jmeno, str(cesta))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mutanty_p29():
    return sorted(x.name for x in ANALYZA.glob("p29-mut-*"))


def mutant_g3(zapis, jmeno):
    """Zapíše do KOPIE `g3` záznam fixtury podle `zapis` a mutant SPUSTÍ.

    ⚠ H137 (vlastní omyl P31, naměřený): mutant `g3` MUSÍ dostat `FORGE_REGISTR`
    do scratch. Bez toho **zapíše ŽIVÝ `_analyza/_registr-bran.json`** svým
    seznamem (50 bran) — a `ag-over-cisla.py` pak spadne na „bran v registru:
    tvrdí 49, naměřeno 50" (`g3` to má v komentáři u `FORGE_REGISTR`, past je
    zapsaná i z P20; přesto se to stalo znovu). Náprava je pustit `g3`.
    """
    fixtura = SCRATCH / "p31-fixtura-brana.py"
    fixtura.write_bytes(b'print("0 kontrol, 0 chyb")\n')
    cil = SCRATCH / jmeno
    zdroj = G3.read_text(encoding="utf-8")
    text = zdroj.replace("BRANY = [", zapis % str(fixtura))
    text = re.sub(r"^WS = .*$", lambda m: "WS = pathlib.Path(r'%s')" % WS,
                  text, count=1, flags=re.M)
    cil.write_bytes(text.encode("utf-8"))
    return cmd([sys.executable, str(cil)], timeout=1800,
               env={"FORGE_REGISTR": str(SCRATCH / "p31-registr-mutant.json")})


def main() -> int:
    p("=" * 78)
    p("P31 — MUTAČNÍ TEST OPRAVY C1 (H131, H132) A C2 (H124)")
    p("datum (z hodin): %s" % time.strftime("%Y-%m-%d %H:%M:%S %z"))
    p("=" * 78)
    SCRATCH.mkdir(parents=True, exist_ok=True)

    # ── pojistky ────────────────────────────────────────────────────────────
    p("\n── P0: POJISTKY (co test předpokládá) ──")
    k("P0 živé měřidlo P28/B existuje", P28B.is_file(), True)
    k("P0 živé měřidlo P29/A existuje", P29A.is_file(), True)
    text = HANDOFF.read_text(encoding="utf-8")
    mod = nacti_modul(P28B, "p31_p28b_zivy")
    s57 = mod.sekce("57", text)
    kotva = "**99 řádků Hxx**"
    k("P0 §57 existuje a kotva je v něm právě 1×", s57.count(kotva), 1)
    k("P0 a v CELÉM dokumentu je táž kotva VÍC než 1× (to je past H131)",
      text.count(kotva) > 1, True)
    p("      v celém dokumentu %d×, mimo §57 %d×"
      % (text.count(kotva), text.count(kotva) - s57.count(kotva)))
    i57 = text.find(s57)
    kopie = (text[:i57] + s57.replace(kotva, "**98 řádků Hxx**", 1)
             + text[i57 + len(s57):])
    k("P0 kopie §57 má mutaci (98) právě 1× a živý §57 ji nemá",
      (mod.sekce("57", kopie).count("**98 řádků Hxx**"),
       s57.count("**98 řádků Hxx**")), (1, 0))
    k("P0 v živém měřidle je tvar kontroly právě 1× (kotva pro vrácení vady)",
      P28B.read_text(encoding="utf-8").count(NOVY_TVAR), 1)
    k("P0 v živém měřidle P29/A je úklid právě 1× (kotva pro vrácení vady)",
      P29A.read_text(encoding="utf-8").count(UKLID_ZIVY), 1)
    k("P0 na začátku nejsou v `_analyza/` žádní mutanti P29", mutanty_p29(), [])
    # ⚠ PŘEGENEROVAT INVENTÁŘ PŘED g3 (H126): bez toho hlásí `g3` dva
    # NEDEKLAROVANÉ exity (`n1-over-inventar`, `C2: mutace N1`) a vypadá to jako
    # vada — naměřeno v P31 prvním během sondy `p31-sonda-g3.py`.
    kod_i, _ = cmd([sys.executable, str(ANALYZA / "hl-neanglicky-v-kodu.py"),
                    "--json", str(ANALYZA / "_inventar.json")], timeout=900)
    k("P0 inventář přegenerován PŘED měřením g3 (H126)", kod_i, 0)

    # ── C1-a: INTEGRACE — živé měřidlo po opravě MUSÍ projít ────────────────
    p("\n── C1-a: ŽIVÉ `p28-b-mutace.py` po opravě (před opravou 27/2) ──")
    t0 = time.time()
    kod, v = cmd([sys.executable, str(P28B)], timeout=3600)
    c = citac(v)
    p("      exit=%d, čítač=%s, trvání %.0f s" % (kod, c, time.time() - t0))
    (ANALYZA / "p31-mutace-p28b-vystup.txt").write_bytes(v.encode("utf-8"))
    k("C1-a živé měřidlo P28/B → 0 chyb (oprava H131+H132 zabrala)",
      c[1] if c else None, 0)
    k("C1-a a měřidlo vůbec něco naměřilo (čítač > 20)",
      (c[0] if c else 0) > 20, True)
    for l in v.splitlines():
        if "CHYBA" in l:
            p("      · %s" % l.strip()[:150])

    # ── C1-b: DIFERENCIÁL — vrácená vada v kopii měřidla ────────────────────
    p("\n── C1-b: diferenciál `kotva_m1` (živá vs. OSLABENÁ s původní vadou) ──")
    k("C1-b ŽIVÁ `kotva_m1` nad živým dokumentem + mutovanou kopií → SHODA",
      mod.kotva_m1(text, s57, kopie), ((1, 0), (1, 0)))
    shutil.copyfile(P28B, OSL_C1)
    try:
        with mutuj(OSL_C1, NOVY_TVAR, STARY_TVAR):
            osl = nacti_modul(OSL_C1, "p31_p28b_oslabeny")
            namereno_osl = osl.kotva_m1(text, s57, kopie)
        p("      oslabená (původní tvar) naměřila: %r" % (namereno_osl,))
        k("C1-b OSLABENÁ `kotva_m1` (kotva v CELÉM dokumentu) → ROZCHOD",
          namereno_osl[0] != namereno_osl[1], True)
        k("C1-b a rozchod je přesně ten, který měřidlo shazoval: (1, 3) vs. (1, 1)",
          namereno_osl, ((1, text.count(kotva)), (1, s57.count(kotva))))
    except ValueError as e:
        k("C1-b oslabenou kopii šlo vyrobit", False, str(e)[:120])
    finally:
        OSL_C1.unlink(missing_ok=True)
    k("C1-b oslabená kopie měřidla je smazaná", OSL_C1.exists(), False)

    # ── C1-c: H132 — mutace `BRANY` MUSÍ VYKÁZAT 50 BRAN ────────────────────
    p("\n── C1-c: mutace `BRANY` v `g3` — starý zápis vs. nový (H132) ──")
    stary_zaznam = 'BRANY= [("p31-fixtura", ["python", %r]),'
    kod_s, v_s = mutant_g3(stary_zaznam, "g3-mutant-stary.py")
    p("      starý zápis (2 prvky): exit=%d, ValueError=%s"
      % (kod_s, "ANO" if "ValueError" in v_s else "NE"))
    k("C1-c STARÝ zápis fixtury → mutant `g3` SPADNE na `ValueError` (vada H132)",
      "not enough values to unpack" in v_s, True)
    k("C1-c a starý mutant VŮBEC nevykázal počet bran (měřilo se na tracebacku)",
      bool(re.search(r"brán celkem:\s*\d+", v_s)), False)
    kod_n, v_n = mutant_g3(mod.ZAZNAM_FIXTURY, "g3-mutant-novy.py")
    m = re.search(r"brán celkem:\s*(\d+)", v_n)
    p("      nový zápis (3 prvky): exit=%d, brán celkem=%s"
      % (kod_n, m.group(1) if m else "—"))
    k("C1-c NOVÝ zápis fixtury → mutant `g3` VYKÁŽE 50 bran",
      int(m.group(1)) if m else None, 50)
    k("C1-c a nový mutant nespadl na `ValueError`", "ValueError" in v_n, False)

    # ── C2: ÚKLID PO MĚŘIDLE P29 ────────────────────────────────────────────
    p("\n── C2: `p29-a-overeni.py --jen A1M13` po sobě uklidí (H124) ──")
    kod, v = cmd([sys.executable, str(P29A), "--jen", "A1M13",
                  "--vystup", str(SCRATCH / "p31-a1m13-zivy-vystup.txt")], timeout=2400)
    zbyle = mutanty_p29()
    p("      živé měřidlo: exit=%d, čítač=%s, zbylé `p29-mut-*`: %s"
      % (kod, citac(v), zbyle or "(žádné)"))
    k("C2-a živé měřidlo P29/A po sobě NEZANECHÁ žádného mutanta", zbyle, [])
    k("C2-a a jeho vlastní kontrola úklidu to ŘEKLA (ne že mlčelo)",
      "úklid: po běhu nezůstal" in v, True)

    shutil.copyfile(P29A, OSL_C2)
    try:
        with mutuj(OSL_C2, UKLID_ZIVY, UKLID_VYPNUTY):
            # ⚠ Čte se UVNITŘ bloku: `mutuj` soubor po bloku VRACÍ, takže zápis až
            #    po bloku by uložil ZDRAVÝ text (a diferenciál by lhal).
            zmut = OSL_C2.read_bytes()
        OSL_C2.write_bytes(zmut)
        kod2, v2 = cmd([sys.executable, str(OSL_C2), "--jen", "A1M13",
                        "--vystup", str(SCRATCH / "p31-a1m13-oslabeny-vystup.txt")],
                       timeout=2400)
        zbyle2 = mutanty_p29()
        p("      oslabená kopie (úklid vypnutý): exit=%d, zbylé: %s"
          % (kod2, ", ".join("%s (%d B)" % (x, (ANALYZA / x).stat().st_size)
                             for x in zbyle2) or "(žádné)"))
        k("C2-b OSLABENÁ kopie (bez úklidu) mutanty ZANECHÁ — kontrola tedy měří",
          len(zbyle2) > 0, True)
        k("C2-b a její kontrola úklidu to hlásí jako CHYBU a běh má exit≠0",
          ("úklid: po běhu nezůstal" in v2 and "CHYBA" in v2 and kod2 != 0), True)
    except ValueError as e:
        k("C2-b oslabenou kopii šlo vyrobit", False, str(e)[:120])
    finally:
        OSL_C2.unlink(missing_ok=True)
        for x in ANALYZA.glob("p29-mut-*"):
            x.unlink(missing_ok=True)
        k("C2-b po testu jsou mutanty i oslabená kopie UKLIZENÉ",
          (mutanty_p29(), OSL_C2.exists()), ([], False))

    p("\n" + "=" * 78)
    p("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    p("=" * 78)
    DOKLAD.write_bytes(("\n".join(_vystup) + "\n").encode("utf-8"))
    print("\n[doklad] %s (%d B, UTF-8)" % (DOKLAD.relative_to(WS), DOKLAD.stat().st_size))
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())
