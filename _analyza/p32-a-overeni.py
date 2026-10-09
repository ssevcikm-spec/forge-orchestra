# -*- coding: utf-8 -*-
r"""P32 — VLASTNÍ PŘEMĚŘENÍ PRÁCE P31 (Úkol A zadání P32).

CO TENHLE DOKLAD DĚLÁ (a čím se liší od měřidla P31):
  * **Čísla NEČTE Z HLAVY** — každé tvrzení se nejdřív **PŘEČTE Z DOKUMENTU**
    (`HANDOFF.md` **§62** = záznam P31) a vypíše se **okno, které vzor trefil**
    (past „brána může číst citaci místo tvrzení").
  * **Má VLASTNÍ diferenciály, ne opisy těch P31** — u opravy H131 volá živou
    funkci `kotva_m1` z `p28-b-mutace.py` nad živým dokumentem **a** nad kopií
    s PŮVODNÍ vadou; u H124 pustí ŽIVÉ měřidlo P29 a jeho **oslabenou kopii**
    (úklid vypnutý). Rozdíl mezi nimi je důkaz, že oprava měří.
  * **Rozlišuje CHYBU, ROZDÍL a NEZMĚŘENO** — tvrzení o měřidle musí sedět
    (`CHYBA`); tvrzení o živém stavu se posunout smí (`ROZDÍL` s vysvětlením).
  * **Umí selhat** — `_analyza/p32-mutace.py` vrací vady do kopií i do dokumentu
    a ověřuje diferenciál (vzor `p31-mutace.py`).

SEKCE:
  B0  pojistky (co měřidlo předpokládá)
  B1  umí opravy P31 spadnout? (VLASTNÍ diferenciály H131 a H124)
  B2  co P31 nasadila? (git + živé sondy TŘEMI kroky)
  B3  sedí čísla z §62? (tvrzení se čte z §62, pak se měří)
  B4  opravy P32 (H136 `p27-dopln-zaznamy.py`, H140/H141 `p22-test-mutace.py`)
  B5  integrita záznamů (kronika, handoff, ov-g, smazané řádky)

Použití:
    python _analyza\p32-a-overeni.py                # LEVNÉ sekce (~3 min, bez sítě)
    python _analyza\p32-a-overeni.py --plne         # i drahé brány a živé sondy
    python _analyza\p32-a-overeni.py --jen B3       # jen jedna sekce
    python _analyza\p32-a-overeni.py --tik          # navíc `POST /tick` (MĚNÍ STAV)

⚠ `--tik` je ZÁSAH DO ŽIVÉHO STAVU (dispatchuje práci a pálí kvótu). Bez něj se
tik NEVOLÁ a sekce to řekne jako `NEZMĚŘENO`.
⚠ V `--plne` se dočasně zapisují MUTANTI do `_analyza/` (kopie měřidel) — na konci
se uklízejí a měřidlo to ověřuje.
"""

import argparse
import hashlib
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
# ⚠ TEST SEAM (P32): `HANDOFF.md` jde přepsat z PROSTŘEDÍ, aby mutační test
# (`p32-mutace.py`) měřil nad KOPIÍ dokumentu a **nesahal na živý záznam**.
# Výchozí hodnota je živý dokument (běžný běh se NEMĚNÍ).
HANDOFF = pathlib.Path(os.environ.get("P32_HANDOFF") or (WS / "HANDOFF.md"))
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
NEXT = WS / "NEXT-SESSION-INSTRUKCE.md"
REGISTR = ANALYZA / "_registr-bran.json"
P20D = ANALYZA / "p20-d-doklady.py"
P28B = ANALYZA / "p28-b-mutace.py"
P29A = ANALYZA / "p29-a-overeni.py"
P31M = ANALYZA / "p31-mutace.py"
P22T = ANALYZA / "p22-test-mutace.py"
P32T = ANALYZA / "p32-test-zapis-kotvy.py"
GIT = WS / "tools" / "git.cmd"
SONDA_DEPLOY = ANALYZA / "p30-sonda-deploy.mjs"
SONDA_STAV = ANALYZA / "p30-sonda-stav.mjs"
DOKLAD_STAV = ANALYZA / "p32-stav-vystup.txt"
SCRATCH = ANALYZA / "p32-a-scratch"
MUT_P29A = ANALYZA / "_p32-mut-p29a.py"
MUT_P28B = ANALYZA / "_p32-mut-p28b.py"
DOKLAD = ANALYZA / "p32-a-overeni-vystup.txt"

ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj  # noqa: E402

# ── kotvy diferenciálů (MUSÍ se shodovat se zdrojem; ověřuje se v B0) ─────────
# PŮVODNÍ vada H131 (kotva v CELÉM dokumentu) a ŽIVÝ tvar (kotva v oddílu).
STARY_TVAR = ('    return ((kopie_text.count("**98 řádků Hxx**"),\n'
              '             text.count("**99 řádků Hxx**")), '
              '(1, s57.count("**99 řádků Hxx**")))')
NOVY_TVAR = ('    return ((sekce("57", kopie_text).count("**98 řádků Hxx**"),\n'
             '             s57.count("**98 řádků Hxx**")), (1, 0))')
# ŽIVÝ úklid v `p29-a-overeni.py` a jeho VYPNUTÁ varianta (H124).
UKLID_ZIVY = ('    for jmeno in MUTANTI:\n'
              '        (ANALYZA / jmeno).unlink(missing_ok=True)\n'
              '    return [jmeno for jmeno in MUTANTI if (ANALYZA / jmeno).exists()]')
UKLID_VYPNUTY = ('    zbyle = [jmeno for jmeno in MUTANTI\n'
                 '             if (ANALYZA / jmeno).exists()]\n'
                 '    return zbyle')
KOTVA_HXX = "**99 řádků Hxx**"

_vystup = []


def p(radek=""):
    print(radek)
    _vystup.append(radek)


def spust(cmd, timeout=3600, env=None):
    t0 = time.time()
    try:
        r = subprocess.run([str(a) for a in cmd], cwd=str(WS), env={**ENV, **(env or {})},
                           capture_output=True, timeout=timeout)
        out = (r.stdout or b"").decode("utf-8", "replace") + \
              (r.stderr or b"").decode("utf-8", "replace")
        return r.returncode, out, time.time() - t0
    except subprocess.TimeoutExpired:
        return -9, "TIMEOUT po %d s" % timeout, time.time() - t0
    except Exception as e:  # noqa: BLE001
        return -1, "SPUŠTĚNÍ SELHALO: %s" % e, time.time() - t0


def citac_text(t):
    """Poslední čítač „VÝSLEDEK: N kontrol, M chyb“."""
    vse = list(re.finditer(r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb", t))
    return (vse[-1].group(1), vse[-1].group(2)) if vse else None


def oddil(vzor, cesta=None):
    """(text, první_řádek, poslední_řádek) oddílu úrovně `##`."""
    cesta = cesta or HANDOFF
    radky = cesta.read_text(encoding="utf-8").splitlines()
    start = next((i for i, r in enumerate(radky) if re.match(vzor, r)), None)
    if start is None:
        raise SystemExit("CHYBA: oddíl %r v %s NENÍ — měřidlo by měřilo jinam"
                         % (vzor, cesta.name))
    konec = len(radky)
    for j in range(start + 1, len(radky)):
        if re.match(r"^##\s", radky[j]):
            konec = j
            break
    return "\n".join(radky[start:konec]), start + 1, konec


def tvrzeni(text, vzory):
    """(čísla, okno, použitý vzor, počet výskytů) — poslední člen je POJISTKA."""
    for v in vzory:
        vse = list(re.finditer(v, text))
        if vse:
            m = vse[-1]
            okno = text[max(0, m.start() - 70): m.end() + 70].replace("\n", " / ")
            return tuple(m.groups()), okno, v, len(vse)
    return None, None, None, 0


class Meridlo:
    def __init__(self):
        self.ok = 0
        self.chyby = []
        self.rozdily = []
        self.nezmerene = []

    def _v(self, stav, text):
        p("  %-9s %s" % (stav, text))
        if stav == "OK":
            self.ok += 1
        elif stav == "CHYBA":
            self.chyby.append(text)

    def ok_(self, podminka, text):
        self._v("OK" if podminka else "CHYBA", text)

    def rozdil(self, text):
        p("  ROZDÍL    %s" % text)
        self.rozdily.append(text)

    def nezmereno(self, text):
        p("  NEZMĚŘENO %s" % text)
        self.nezmerene.append(text)

    def info(self, text):
        p("  INFO      %s" % text)


def git(*args, timeout=300):
    return spust([str(GIT), "-C", str(WS), *args], timeout=timeout)


def nacti_modul(cesta, jmeno):
    spec = importlib.util.spec_from_file_location(jmeno, str(cesta))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mutanty_p29():
    return sorted(x.name for x in ANALYZA.glob("p29-mut-*"))


def uklid_p29():
    for x in ANALYZA.glob("p29-mut-*"):
        x.unlink(missing_ok=True)
    return mutanty_p29()


# ── B0 ──────────────────────────────────────────────────────────────────────
def sekce_B0(m):
    p("")
    p("── B0: POJISTKY (co měřidlo předpokládá) ──")
    for cesta, popis in ((HANDOFF, "HANDOFF.md"), (P28B, "p28-b-mutace.py"),
                         (P29A, "p29-a-overeni.py"), (P31M, "p31-mutace.py")):
        m.ok_(cesta.is_file(), "B0 %s existuje" % popis)
    text62, l0, l1 = oddil(r"^##\s+62\.")
    p("            okno §62: HANDOFF.md řádky %d–%d (%d znaků)" % (l0, l1, len(text62)))
    zdroj_p28 = P28B.read_text(encoding="utf-8")
    m.ok_(zdroj_p28.count(NOVY_TVAR) == 1,
          "B0 ŽIVÝ tvar `kotva_m1` je v p28-b-mutace.py právě 1× (kotva diferenciálu)")
    m.ok_(zdroj_p28.count(STARY_TVAR) == 0,
          "B0 PŮVODNÍ tvar H131 v živém měřidle NENÍ (jinak by diferenciál nic neukázal)")
    zdroj_p29 = P29A.read_text(encoding="utf-8")
    m.ok_(zdroj_p29.count(UKLID_ZIVY) == 1,
          "B0 ŽIVÝ úklid je v p29-a-overeni.py právě 1× (kotva diferenciálu)")
    text = HANDOFF.read_text(encoding="utf-8")
    s57 = nacti_modul(P28B, "p32_p28b_zivy").sekce("57", text)
    m.ok_(s57.count(KOTVA_HXX) == 1,
          "B0 kotva %r je v oddílu §57 právě 1× (%d×)" % (KOTVA_HXX, s57.count(KOTVA_HXX)))
    m.ok_(text.count(KOTVA_HXX) > 1,
          "B0 a v CELÉM dokumentu je VÍC než 1× (%d×) — to je past H131"
          % text.count(KOTVA_HXX))
    m.ok_(not mutanty_p29(), "B0 na začátku nejsou v `_analyza/` žádní mutanti P29")


# ── B1 ──────────────────────────────────────────────────────────────────────
def sekce_B1(m, plne):
    p("")
    p("── B1: UMÍ OPRAVY P31 SPADNOUT? (VLASTNÍ diferenciály, ne opis) ──")

    # (a) H131 — kotva v MĚŘENÉM oddílu: živá funkce vs. kopie s PŮVODNÍ vadou
    text = HANDOFF.read_text(encoding="utf-8")
    mod = nacti_modul(P28B, "p32_p28b_zivy")
    s57 = mod.sekce("57", text)
    kotva = KOTVA_HXX
    if s57.count(kotva) != 1:
        m.ok_(False, "B1-a oddíl §57 nemá kotvu %r právě 1× → diferenciál by lhal" % kotva)
        return
    i57 = text.find(s57)
    kopie = (text[:i57] + s57.replace(kotva, "**98 řádků Hxx**", 1)
             + text[i57 + len(s57):])
    zive = mod.kotva_m1(text, s57, kopie)
    p("            živá `kotva_m1` na (živý dokument + mutovaná kopie §57): %r" % (zive,))
    m.ok_(zive == ((1, 0), (1, 0)),
          "B1-a ŽIVÁ `kotva_m1` → SHODA (%r) — kotva se počítá v MĚŘENÉM oddílu" % (zive,))
    osl = None
    shutil.copyfile(P28B, MUT_P28B)
    try:
        with mutuj(MUT_P28B, NOVY_TVAR, STARY_TVAR):
            o = nacti_modul(MUT_P28B, "p32_p28b_osl")
            osl = o.kotva_m1(text, s57, kopie)
        p("            OSLABENÁ (původní vada H131): %r" % (osl,))
        m.ok_(osl is not None and osl[0] != osl[1],
              "B1-a OSLABENÁ `kotva_m1` (kotva v CELÉM dokumentu) → ROZCHOD %r" % (osl,))
        m.ok_(osl == ((1, text.count(kotva)), (1, s57.count(kotva))),
              "B1-a a rozchod je PŘESNĚ ten, který měřidlo shazoval: %r" % (osl,))
    except ValueError as e:
        m.ok_(False, "B1-a oslabenou kopii NELZE vyrobit: %s" % str(e)[:120])
    finally:
        MUT_P28B.unlink(missing_ok=True)
    m.ok_(not MUT_P28B.exists(), "B1-a oslabená kopie p28-b je smazaná")

    if not plne:
        m.nezmereno("B1-b úklid P29 (živé + oslabené měřidlo) a `p28-b-mutace.py` — drahé, spusť --plne")
        return

    # (b) H124 — úklid po měřidle P29: živé vs. oslabená kopie
    kod, v, tr = spust([sys.executable, str(P29A), "--jen", "A1M13",
                        "--vystup", "_analyza/p32-a1m13-zivy-vystup.txt"], timeout=2400)
    c = citac_text(v)
    zbyle = mutanty_p29()
    p("            ŽIVÉ `p29-a --jen A1M13`: exit=%d, čítač=%s, %.0f s, zbylí mutanti: %s"
      % (kod, c, tr, zbyle or "(žádní)"))
    m.ok_(kod == 0 and c == ("8", "0"), "B1-b živé měřidlo P29/A → 8/0 (naměřeno %s)" % (c,))
    m.ok_(not zbyle, "B1-b a po běhu NEZŮSTAL žádný mutant")
    m.ok_("úklid: po běhu nezůstal" in v, "B1-b a měřidlo to ŘEKLO (kontrola úklidu)")

    shutil.copyfile(P29A, MUT_P29A)
    try:
        with mutuj(MUT_P29A, UKLID_ZIVY, UKLID_VYPNUTY):
            zmut = MUT_P29A.read_bytes()
        MUT_P29A.write_bytes(zmut)
        kod2, v2, _ = spust([sys.executable, str(MUT_P29A), "--jen", "A1M13",
                             "--vystup", "_analyza/p32-a1m13-osl-vystup.txt"], timeout=2400)
        zbyle2 = mutanty_p29()
        p("            OSLABENÁ kopie (úklid vypnut): exit=%d, zbylí: %s"
          % (kod2, ", ".join("%s (%d B)" % (x, (ANALYZA / x).stat().st_size)
                             for x in zbyle2) or "(žádní)"))
        m.ok_(len(zbyle2) > 0,
              "B1-b OSLABENÁ kopie mutanty ZANECHÁ → kontrola „nezůstal“ MĚŘÍ")
        m.ok_(kod2 != 0 and "CHYBA" in v2,
              "B1-b a její kontrola úklidu to hlásí jako CHYBU (exit=%d)" % kod2)
    except ValueError as e:
        m.ok_(False, "B1-b oslabenou kopii NELZE vyrobit: %s" % str(e)[:120])
    finally:
        MUT_P29A.unlink(missing_ok=True)
        zbyle3 = uklid_p29()
        m.ok_((zbyle3, MUT_P29A.exists()) == ([], False),
              "B1-b po diferenciálu jsou mutanti i oslabená kopie UKLIZENÉ")

    # (c) §62 tvrdí `p28-b-mutace.py` → 30/0; spustí se ZNOVU
    kod, v, tr = spust([sys.executable, str(P28B)], timeout=3600)
    c = citac_text(v)
    (ANALYZA / "p32-a-p28b-vystup.txt").write_bytes(v.encode("utf-8"))
    p("            `p28-b-mutace.py`: exit=%d, čítač=%s, %.0f s" % (kod, c, tr))
    m.ok_(kod == 0 and c is not None and c[1] == "0" and int(c[0]) > 20,
          "B1-c VLASTNÍ běh `p28-b-mutace.py` → %s (0 chyb, >20 kontrol)" % (c,))
    for l in v.splitlines():
        if "CHYBA" in l:
            p("            · %s" % l.strip()[:150])

    # (d) `p31-mutace.py` — povinný běh A1 (spouští se v téhle session zvlášť)
    dok = ANALYZA / "p31-mutace-vystup.txt"
    if dok.is_file():
        cd = citac_text(dok.read_text(encoding="utf-8", errors="replace"))
        m.info("B1-d `p31-mutace.py` (povinný běh A1 v této session) → %s (doklad %s)"
               % (cd, dok.name))
    else:
        m.nezmereno("B1-d doklad `p31-mutace.py` v této session není")


# ── B2 ──────────────────────────────────────────────────────────────────────
def sekce_B2(m, plne, tik):
    p("")
    p("── B2: CO P31 NASADILA? (git; živé sondy jen v --plne) ──")
    for sha, popis in (("41aa981", "práce P31"), ("d3f1a48", "oprava kotvy hry")):
        kod, out, _ = git("show", "--name-only", "--format=", sha)
        soubory = [l.strip() for l in out.splitlines() if l.strip()]
        kriticke = [s for s in soubory if s.startswith("conductor/") or s.startswith(".github/")]
        m.ok_(kod == 0 and not kriticke,
              "B2 commit %s (%s): %d souborů, z toho v conductor/ nebo .github/: %d"
              % (sha, popis, len(soubory), len(kriticke)))
    kod, out, _ = git("status", "--porcelain", "--", "conductor", ".github")
    m.ok_(kod == 0 and not out.strip(),
          "B2 v pracovním stromu není NEZAKOMMITOVANÁ změna conductor/ ani .github/")
    kod, out, _ = git("rev-parse", "HEAD")
    head = out.strip()
    kod2, out2, tr2 = git("ls-remote", "origin", "refs/heads/main")
    remote = out2.split()[0].strip() if out2.split() else ""
    p("            HEAD=%s · ls-remote=%s (%.0f s)" % (head[:8], remote[:8], tr2))
    m.ok_(kod == 0 and kod2 == 0, "B2 `rev-parse` i `ls-remote` proběhly (exit 0/0)")
    m.ok_(head == remote and head != "", "B2 push DORAZIL: `origin/main` == HEAD")

    text62, _, _ = oddil(r"^##\s+62\.")
    cit, okno, _, n = tvrzeni(text62, [
        r"deploy\.yml`?\s*\*{0,2}(?:běh\s*)?#(\d+)\*{0,2}\s*na\s*`?([0-9a-f]{7,40})`?"])
    if cit is None:
        m.ok_(False, "B2 v §62 se NENAŠLO nasazené `deploy.yml` #N na commitu")
    else:
        p("            §62 tvrdí: deploy.yml #%s na `%s` (%d× v oddílu) · okno: …%s…"
          % (cit[0], cit[1], n, okno))
        if not plne:
            m.nezmereno("B2-živé: sonda `deploy.yml` (síť) — spusť --plne")
        else:
            kod, out, tr = spust(["node", str(SONDA_DEPLOY), cit[1]], timeout=300)
            uspech = re.search(r"#(\d+) na %s je completed/success" % cit[1][:7], out)
            m.ok_(kod == 0, "B2 nasazený kód: sonda deploy.yml na %s → exit 0 (%.0f s)"
                  % (cit[1][:8], tr))
            m.ok_(bool(uspech), "B2 a běh je `completed/success` na TOM commitu: %s"
                  % (uspech.group(0) if uspech else "—"))
            kod, out, tr = spust(["node", str(SONDA_STAV), str(DOKLAD_STAV.relative_to(WS))]
                                 + (["--tik"] if tik else []), timeout=300)
            m.ok_(kod == 0, "B2 živá služba (sonda stav%s) → exit 0 (%.0f s)"
                  % (", S TIKEM" if tik else ", bez tiku", tr))
            if DOKLAD_STAV.is_file():
                t = DOKLAD_STAV.read_text(encoding="utf-8", errors="replace")
                osirele = [int(x) for x in re.findall(r'"osirelych_radku":\s*(\d+)', t)]
                m.ok_(bool(osirele) and all(x == 0 for x in osirele),
                      "B2 `/tasks/cleanup {dry_run}` → osiřelých 0 (naměřeno %s)" % (osirele,))
            else:
                m.ok_(False, "B2 sonda NEZAPSALA doklad %s" % DOKLAD_STAV.name)
            if tik:
                p("            ⚠ `POST /tick` BYL VOLÁN (--tik): mění stav a pálí kvótu")
            else:
                m.info("B2 `POST /tick` NEVOLÁN (--tik nepředán) — tik je ZÁSAH DO STAVU")


# ── B3 ──────────────────────────────────────────────────────────────────────
def sekce_B3(m, plne):
    p("")
    p("── B3: SEDÍ ČÍSLA Z §62? (tvrzení se ČTE z §62, pak se měří) ──")
    text62, l0, l1 = oddil(r"^##\s+62\.")
    p("            okno §62: HANDOFF.md řádky %d–%d (%d znaků)" % (l0, l1, len(text62)))

    TVRZENI = [
        dict(jmeno="test-tick-offline", dok=[r"test-tick-offline`?\s*\*{0,2}(\d+)/(\d+)"],
             cmd=["node", "tools/test-tick-offline.mjs"],
             out=[r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"], exity={0}, drahe=False),
        dict(jmeno="over-skilly", dok=[r"over-skilly`?\s*\*{0,2}(\d+)/(\d+)"],
             cmd=[sys.executable, "tools/over-skilly.py"],
             out=[r"(\d+)\s*zmínek,\s*(\d+)\s*mrtvých"], exity={0}, drahe=False),
        dict(jmeno="p29-b6-mutace", dok=[r"p29-b6-mutace`?\s*\*{0,2}(\d+)/(\d+)"],
             cmd=[sys.executable, "_analyza/p29-b6-mutace.py"],
             out=[r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"], exity={0}, drahe=False),
        dict(jmeno="over-dokumentaci", dok=[r"over-dokumentaci`?\s*\*{0,2}(\d+)/(\d+)"],
             cmd=[sys.executable, "tools/over-dokumentaci.py"],
             out=[r"Kontrol:\s*(\d+),\s*chyb:\s*(\d+)", r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"],
             exity={0}, drahe=False),
        dict(jmeno="p28-b-mutace", dok=[r"p28-b-mutace[^\n]{0,40}?\*{0,2}(\d+)/(\d+)"],
             cmd=[sys.executable, str(P28B)], out=[r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb"],
             exity={0}, drahe=True),
    ]
    for t in TVRZENI:
        jmeno = t["jmeno"]
        cit, okno, _, n = tvrzeni(text62, t["dok"])
        if cit is None:
            m.ok_(False, "B3 %s: TVRZENÍ SE V §62 NENAŠLO (kontrola by se tiše přeskočila)"
                  % jmeno)
            continue
        p("            %s: §62 tvrdí %s (%d×) · okno: …%s…" % (jmeno, cit, n, okno))
        if t["drahe"] and not plne:
            m.nezmereno("B3 %s: měření je drahé — spusť --plne (tvrzeno %s)" % (jmeno, cit))
            continue
        kod, out, tr = spust(t["cmd"], timeout=2400)
        if kod not in t["exity"]:
            posledni = out.strip().splitlines()[-1][:130] if out.strip() else "—"
            m.ok_(False, "B3 %s: exit=%d (čekán %s) za %.0f s — %s"
                  % (jmeno, kod, sorted(t["exity"]), tr, posledni))
            continue
        hodnoty = []
        for v in t["out"]:
            nn = re.findall(v, out, re.S)
            if nn:
                posledni = nn[-1]
                hodnoty.extend(posledni if isinstance(posledni, tuple) else (posledni,))
        if not hodnoty:
            m.ok_(False, "B3 %s: ve výstupu NENÍ čítač (měřilo by se naslepo)" % jmeno)
            continue
        hodnoty = tuple(hodnoty)
        p("            naměřeno: %s (%.0f s)" % (hodnoty, tr))
        shoda = all(str(cit[i]) == str(hodnoty[i]) for i in range(min(len(cit), len(hodnoty))))
        if t.get("poznamka") and not shoda:
            m.rozdil("B3 %s: §62 %s vs naměřeno %s — %s" % (jmeno, cit, hodnoty, t["poznamka"]))
        else:
            m.ok_(shoda, "B3 %s: §62 %s == naměřeno %s" % (jmeno, cit, hodnoty))

    # ov-g: rozsah i NEOVĚŘENO
    cit, okno, _, n = tvrzeni(text62, [r"ov-g`?[^\n]{0,30}?(\d+)\s*řádků Hxx"])
    kod, out, tr = spust([sys.executable, "_analyza/ov-g-neovereno.py"], timeout=600)
    nev = re.search(r"NEOVĚŘENO:\s*(\d+)", out)
    rozsah = re.search(r"(\d+)\s*nálezů Hxx", out)
    if cit is None:
        m.ok_(False, "B3 ov-g: v §62 se NENAŠEL rozsah řádků Hxx")
    else:
        p("            ov-g: §62 tvrdí %s · okno: …%s…" % (cit, okno))
        m.ok_(kod == 0 and rozsah is not None and rozsah.group(1) == cit[0],
              "B3 ov-g: rozsah §62 %s == naměřeno %s"
              % (cit[0], rozsah.group(1) if rozsah else "—"))
    m.ok_(nev is not None and nev.group(1) == "0",
          "B3 ov-g: NEOVĚŘENO = %s" % (nev.group(1) if nev else "—"))

    # kronika a handoff-uplnost
    kod, out, tr = spust([sys.executable, "_analyza/kronika-kontrola.py"], timeout=300)
    m.ok_(kod == 0 and "SEDÍ" in out.upper(),
          "B3 kronika-kontrola: exit=%d a hlásí SEDÍ" % kod)
    r = re.search(r"sessions v kronice:\s*(\d+)", out)
    cit, okno, _, _ = tvrzeni(text62, [r"kronika[^\n]{0,30}?\((\d+)\s*řádků\)"])
    if r and cit:
        p("            kronika: §62 tvrdí %s řádků · okno: …%s…" % (cit[0], okno))
        if str(r.group(1)) != str(cit[0]):
            m.rozdil("B3 kronika: §62 tvrdí %s řádků, naměřeno %s — §62.5 vznikl PŘED "
                     "zápisem vlastního řádku session P31" % (cit[0], r.group(1)))
        else:
            m.ok_(True, "B3 kronika: §62 tvrdí %s řádků == naměřeno" % cit[0])
    elif r:
        m.info("B3 kronika: naměřeno %s řádků (v §62 tvrzení o počtu není)" % r.group(1))
    kod, out, tr = spust([sys.executable, "_analyza/handoff-kontrola-uplnost.py"], timeout=600)
    ch = re.search(r"CHYBÍ:\s*(\d+)", out)
    par = re.search(r"(\d+)/(\d+)", out)
    ok_upl = kod == 0 and ((ch is not None and ch.group(1) == "0")
                           or (par and par.group(1) == par.group(2)))
    m.ok_(ok_upl, "B3 handoff-kontrola-uplnost: 0 chybějících (naměřeno %s)"
          % (("%s/%s" % (par.group(1), par.group(2))) if par else
             (ch.group(1) if ch else "—")))

    # registr bran
    kod, out, tr = spust([sys.executable, "_analyza/ag-over-cisla.py"], timeout=600)
    m.ok_(kod == 0, "B3 ag-over-cisla → exit 0 (registr bran sedí)")
    reg = re.search(r'"bran_celkem":\s*(\d+)', REGISTR.read_text(encoding="utf-8"))
    m.ok_(reg is not None and reg.group(1) == "49",
          "B3 `_registr-bran.json`: bran_celkem = %s (H137/H138)" % (reg.group(1) if reg else "—"))

    m.info("B3 INFO — drahé brány, které v této session měří POVINNÝ běh A3/A7 "
           "(`p31-a-overeni.py --plne`, `--jen A4`, `g3`, `validate-all`): "
           "`p30-mutace` 16/0, `tick-mutace` 20 vrat/41/0, `g3` 49/0/1, "
           "`validate-all` 0 problémů, `p30-a` 32/3. Tady se NEOPAKUJÍ "
           "(dvojí běh téhož by nic nepřidal a stál ~40 min).")


# ── B4 ──────────────────────────────────────────────────────────────────────
def sekce_B4(m):
    p("")
    p("── B4: OPRAVY P32 (H136 patcher, H140/H141 kontrola P22) ──")
    kod, out, tr = spust([sys.executable, "-B", str(P22T)], timeout=600)
    c = citac_text(out)
    p("            `p22-test-mutace.py`: exit=%d, čítač=%s" % (kod, c))
    sh = re.findall(r"zdravá \((\d+), (\d+)\) → zmutovaná \((\d+), (\d+)\)", out)
    m.ok_(kod == 0 and c == ("20", "0"),
          "B4 H139/H140 ZAVŘENO: `p22-test-mutace.py` → %s (P31 měřila 19 kontrol / 1 chybu)" % (c,))
    m.ok_(bool(sh) and sh[-1][3] != "0",
          "B4 a jeho MĚŘENÝ diferenciál je vidět: zdravá→zmutovaná %s"
          % (str(sh[-1]) if sh else "—"))
    text62, _, _ = oddil(r"^##\s+62\.")
    cit, okno, _, n = tvrzeni(text62, [r"test dál hlásí\s*\*{0,2}(\d+)\s*chyb"])
    if cit is None:
        m.nezmereno("B4 v §62 se nenašlo tvrzení o počtu chyb testu P22")
    else:
        p("            §62 o P22 tvrdí: %s chyb (%d×) · okno: …%s…" % (cit[0], n, okno))
        if c is not None and c[1] != cit[0]:
            m.rozdil("B4 §62 tvrdí u `p22-test-mutace` %s chyb, naměřeno %s — ZÁMĚRNÁ "
                     "změna: P32 opravila KONTROLU (H140/H141), ne měřenou bránu"
                     % (cit[0], c[1]))
        else:
            m.ok_(True, "B4 §62 tvrdí %s chyb == naměřeno" % cit[0])
    kod2, out2, tr2 = spust([sys.executable, "-B", str(P32T)], timeout=600)
    c2 = citac_text(out2)
    p("            `p32-test-zapis-kotvy.py`: exit=%d, čítač=%s" % (kod2, c2))
    m.ok_(kod2 == 0 and c2 is not None and c2[1] == "0",
          "B4 H136 ZAVŘENO: patcher se špatnými kotvami NEZAPÍŠE → %s" % (c2,))
    m.ok_("ZAPSALA (bajty se změnily)" in out2,
          "B4 a diferenciál (oslabená kopie ZAPÍŠE) je součástí důkazu")
    _, out3, _ = git("diff", "--numstat", "HEAD", "--", "HANDOFF.md", "KRONIKA-PROJEKTU.md")
    smazano = 0
    for l in out3.splitlines():
        casti = l.split("\t")
        if len(casti) >= 2 and casti[1].isdigit():
            smazano += int(casti[1])
    m.ok_(smazano == 0, "B4 záznamy se jen PŘIDÁVALY (0 smazaných řádků v HANDOFF/KRONICE)")


# ── B5 ──────────────────────────────────────────────────────────────────────
def sekce_B5(m):
    p("")
    p("── B5: INTEGRITA (dokumenty a registr) ──")
    SLEDOVANE = [KRONIKA, HANDOFF, NEXT, REGISTR]
    for q in SLEDOVANE:
        m.ok_(q.is_file() and q.stat().st_size > 0,
              "B5 sledovaný dokument %s existuje a není prázdný" % q.name)
    reg = re.search(r'"bran_celkem":\s*(\d+)', REGISTR.read_text(encoding="utf-8"))
    m.ok_(reg is not None and reg.group(1) == "49",
          "B5 `_registr-bran.json` je ŽIVÝ registr (49 bran), ne harness z fixtury")
    kod, out, _ = git("status", "--porcelain")
    radky = [l for l in out.splitlines() if l.strip()]
    p("            `git status --porcelain`: %d řádků" % len(radky))
    m.info("B5 H130/H138: dávka dokladů se v této session měří POVINNÝM během A4 "
           "(`p31-a-overeni.py --jen A4`) — pojistka musí hlásit "
           "„žádný z 4 sledovaných dokumentů se nezměnil“ a sekce „KDO ZAPSAL“ "
           "musí být prázdná (doklad `_analyza/p31-a4-davka-vystup.txt`)")


# ── main ────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jen", default=None, help="seznam sekcí, např. B3")
    ap.add_argument("--plne", action="store_true", help="i drahé brány a živé sondy")
    ap.add_argument("--tik", action="store_true", help="navíc `POST /tick` (MĚNÍ STAV)")
    ap.add_argument("--vystup", default=None)
    args = ap.parse_args()

    vystup = pathlib.Path(args.vystup) if args.vystup else DOKLAD
    if not vystup.is_absolute():
        vystup = WS / vystup
    m = Meridlo()
    fns = {
        "B0": lambda: sekce_B0(m),
        "B1": lambda: sekce_B1(m, args.plne),
        "B2": lambda: sekce_B2(m, args.plne, args.tik),
        "B3": lambda: sekce_B3(m, args.plne),
        "B4": lambda: sekce_B4(m),
        "B5": lambda: sekce_B5(m),
    }
    sekce = [x.strip().upper() for x in
             (args.jen if args.jen else "B0,B1,B2,B3,B4,B5").split(",")]
    p("=" * 88)
    p("P32/A — VLASTNÍ PŘEMĚŘENÍ PRÁCE P31 (Úkol A zadání P32)")
    p("=" * 88)
    p("  datum (z hodin): %s" % time.strftime("%Y-%m-%d %H:%M:%S %z"))
    p("  pořadí běhu: %s%s" % (", ".join(sekce),
                               "  (--plne)" if args.plne else "  (levný režim)"))
    p("  doklad: %s" % vystup.name)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    for e in sekce:
        f = fns.get(e)
        if f is None:
            p("  ??    sekce %s neexistuje" % e)
            continue
        p("\n" + "─" * 88)
        try:
            f()
        except Exception as ex:  # noqa: BLE001
            import traceback  # noqa: PLC0415
            tb = traceback.format_exc().strip().splitlines()
            p("      TRACEBACK: %s" % " | ".join(x.strip() for x in tb[-3:]))
            m.nezmereno("sekce %s: výjimka %s: %s" % (e, type(ex).__name__, str(ex)[:200]))
    p("\n" + "=" * 88)
    p("POJMENOVANÉ ROZDÍLY (stav se posunul, nebo je změna ZÁMĚRNÁ): %d" % len(m.rozdily))
    for x in m.rozdily:
        p("  · %s" % x[:220])
    p("\nNEZMĚŘENO (není nula a není zelená): %d" % len(m.nezmerene))
    for x in m.nezmerene:
        p("  · %s" % x[:220])
    p("=" * 88)
    p("VÝSLEDEK: %d kontrol, %d chyb (z toho %d pojmenovaných ROZDÍLŮ, %d NEZMĚŘENO)"
      % (m.ok, len(m.chyby), len(m.rozdily), len(m.nezmerene)))
    p("=" * 88)
    vystup.write_bytes(("\n".join(_vystup) + "\n").encode("utf-8"))
    print("\n[doklad] %s (%d B, UTF-8)" % (vystup.relative_to(WS), vystup.stat().st_size))
    return 1 if m.chyby else 0


if __name__ == "__main__":
    sys.exit(main())
