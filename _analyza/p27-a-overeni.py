# -*- coding: utf-8 -*-
r"""P27 — ÚKOL A: PŘEMĚŘIT PRÁCI P26 VLASTNÍM POSTUPEM (A1–A7).

PROČ TENHLE SKRIPT EXISTUJE
---------------------------
Zadání P27 §2.1 a `AGENTS.md`: *„autor není nezávislý reviewer"*. Záznamy P26
(`HANDOFF.md` §56, kronika řádek 41 + §2.19) i měřidlo `p26-a-overeni.py` psala
**tatáž session**. P27 je proto přeměřuje **jiným postupem, než jak vznikl** —
a tam, kde to jinak nejde, to aspoň **pojmenuje** jako odvození.

CO SE MĚŘÍ (a čím jinak, než to vzniklo)
----------------------------------------
  A1  **KONTRAMUTACE V KOPIÍCH** měřidla P26: vloží se vada do KAŽDÉHO vstupu,
      který měřidlo tvrdí, že čte (`--handoff` = oddíl §55, `--g3` = seznam
      BRANY, `--ovg` = hlášení rozsahu) a měří se, že **každá vada shodí
      měřidlo z JINÉHO důvodu**. + běh `p26-b-mutace.py` (mutační důkaz P26).
  A2  **ZARÁŽKA V HANDLERU pro SEDM nových endpointů** (`/health`, `/queue`,
      `/roadmap`, `/failed`, `/status`, `/workers`, `/games`). P26 to dělala pro
      tři zapisující endpointy; pro tyhle se to **nikdy neměřilo** — a „test
      endpoint volá" se dokazuje jen zarážkou **UVNITŘ handleru** (routerová
      zarážka zapne i kontroly, které s handlerem nesouvisí).
  A3  **TVRDÍ TESTY OBSAH, NEBO JEN `status === 200`?** V KOPII testu se falešná
      D1 přinutí vracet **prázdné výsledky** (`all()` → `{results: []}`) a měří
      se, které kontroly zčervenají — a které `… odpoví 200` zůstanou ZELENÉ.
      To je celý rozdíl mezi „přítomnost" a „chování".
  A4  **KAŽDÉ ČÍSLO TVRZENÉ V §56 se znovu NAMĚŘÍ** (ne přečte) a porovná
      s tvrzením **PŘEČTENÝM Z DOKUMENTU**. + **ŽIVÁ SLUŽBA**: tvar odpovědí
      sedmi endpointů se měří na nasazeném conductoru (bez zápisu).
  A5  **ROZSAH MĚŘIDLA `ov-g-neovereno.py`** (nález P25-K): 99 řádků Hxx se
      počítá **VLASTNÍM průchodem souborů**, ne čtením jeho výpisu; fixtura
      s `NEOVĚŘENO` musí spadnout, prázdná fixtura hlásit `NEMĚŘENO`; a verze
      z **`HEAD`** (ne jen z pracovního stromu) musí měřit totéž.
  A6  **INTEGRITA**: `g3`, `validate-all`, úplnost handoffu, kronika.
  A7  **INVENTÁŘ A POŘADÍ BRAN** (nález P26/10): otisk počítá **I DRUHÉ REPO**;
      doklad `_analyza/*-vystup.txt` je z otisku **VYLUČEN**; jiný nový `.txt`
      otisk **ZMĚNÍ** a brána pak hlásí pojmenovaný STAV (ne ticho).

⚠ TŘETÍ STAV: „neměřeno" se hlásí jako `NEZMĚŘENO` (`overovani` §7.13) — není to
nula a není to zelená.

Použití:
    python _analyza/p27-a-overeni.py              # DÁVKA: A1, A4(levné), A5, A6(levné), A7
    python _analyza/p27-a-overeni.py --plne       # VŠE + A2, A3, dlouhá měření, g3, validate-all
    python _analyza/p27-a-overeni.py --jen A2     # jen vybrané etapy

Přepínače cest (`--handoff`, `--test`, `--ovg`, `--g3`) existují **kvůli
mutačnímu důkazu** (`p27-b-mutace.py`) — bez nich by se musel mutovat živý strom.
"""

import argparse
import ast
import contextlib
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
TOOLS = WS / "tools"
GIT = TOOLS / "git.cmd"
SRC = WS / "conductor" / "src" / "index.ts"
TEST_TIK = TOOLS / "test-tick-offline.mjs"
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
G3 = ANALYZA / "g3-brany.py"
VALIDATE = TOOLS / "validate-all.mjs"
P20_D = ANALYZA / "p20-d-doklady.py"
P26_A = ANALYZA / "p26-a-overeni.py"
P26_B = ANALYZA / "p26-b-mutace.py"
P25_A = ANALYZA / "p25-a-overeni.py"
P25_B = ANALYZA / "p25-b-mutace.py"
P24_A = ANALYZA / "p24-a-overeni.py"
P24_B = ANALYZA / "p24-b-mutace.py"
TICK_MUT = ANALYZA / "tick-mutace.py"
OV_G = ANALYZA / "ov-g-neovereno.py"
RIZIKA = ANALYZA / "hl-rizika-jazyka.py"
NEANGL = ANALYZA / "hl-neanglicky-v-kodu.py"
INVENTAR = ANALYZA / "_inventar.json"
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
ARCHIV = WS / "_archiv"
SCRATCH = ANALYZA / "p27-scratch"
KOPIE_TESTU = TOOLS / "p27-kopie-tick.mjs"
DOBOVA_KOPIE = TOOLS / "p27-dobova-kopie-tick.mjs"

sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj                                            # noqa: E402

kontrol = 0
chyb = 0
nezmereno = []
VYSTUP_CESTA = None

# Zarážky v HANDLERU pro sedm endpointů, které do P27 nevolal žádný test.
# (prefix kontrol v testu, cesta, kotva v handleru)
ZARAZKY = (
    ("X", "/health", 'if (path === "/health") {'),
    ("Y", "/queue", 'if (path === "/queue") {'),
    ("Z", "/roadmap", 'if (path === "/roadmap") {'),
    ("AA", "/failed", 'if (path === "/failed") {'),
    ("AB", "/status", 'if (path === "/status") {'),
    ("AC", "/workers", 'if (path === "/workers") {'),
    ("AD", "/games", 'if (path === "/games") {'),
)


def check(popis, zjisteno, ocekavano):
    global kontrol, chyb
    kontrol += 1
    if zjisteno == ocekavano:
        print("  OK    %s" % popis)
        return True
    chyb += 1
    print("  CHYBA %s\n          čekáno: %r\n          dáno:   %r"
          % (popis, ocekavano, zjisteno))
    return False


def nezmereno_zapis(popis, duvod):
    nezmereno.append(popis)
    print("  NEZMĚŘENO  %s\n          důvod: %s" % (popis, duvod))


def cmd(argumenty, cwd=None, timeout=3600):
    # ⚠ H138 (P31): viz `p25-a-overeni.py` — `g3-brany.py` bez `FORGE_REGISTR`/
    # `FORGE_BEZ_REGISTRU` zapíše ŽIVÝ `_analyza/_registr-bran.json`, a dávka
    # dokladů to hlásí jako „ZMĚNĚN dokument".
    r = subprocess.run(argumenty, cwd=str(cwd or WS), capture_output=True,
                       env={**os.environ, "FORGE_BEZ_REGISTRU": "1"},
                       timeout=timeout)
    return r.returncode, (r.stdout.decode("utf-8", "replace")
                          + r.stderr.decode("utf-8", "replace"))


def citac(vystup, vzor=r"(\d+) kontrol, (\d+) chyb"):
    """Poslední výskyt čítače (mutace tiskne `CHYB` velkými)."""
    m = None
    for m in re.finditer(vzor, vystup, re.IGNORECASE):
        pass
    return (int(m.group(1)), int(m.group(2))) if m else None


def cervene(vystup):
    """Popisy červených kontrol (`  CHYBA <popis>`)."""
    return [l.strip()[len("CHYBA"):].strip() for l in vystup.splitlines()
            if l.strip().startswith("CHYBA")]


def zelene(vystup):
    return [l.strip()[len("OK"):].strip() for l in vystup.splitlines()
            if l.strip().startswith("OK ")]


def sha(cesta):
    return hashlib.sha256(pathlib.Path(cesta).read_bytes()).hexdigest()


def blob(rev, cesta):
    """Bajty blobu z revize. ⚠ `~1`/konkrétní sha, NIKDY `^` (`git.cmd` ho žere)."""
    r = subprocess.run([str(GIT), "-C", str(WS), "show", "%s:%s" % (rev, cesta)],
                       capture_output=True, shell=True, timeout=120)
    return r.stdout if r.returncode == 0 else None


def rev_podle_predmetu(vzor):
    """Sha commitu, jehož předmět odpovídá vzoru (pro „dobovou kotvu" P26)."""
    r = subprocess.run([str(GIT), "-C", str(WS), "log", "-1", "--format=%H",
                        "--grep", vzor],
                       capture_output=True, shell=True, timeout=120)
    out = r.stdout.decode("utf-8", "replace").strip().splitlines()
    return out[0] if r.returncode == 0 and out else None


def sekce(nazev, text):
    """Text oddílu `## <nazev>.` z dokumentu (do dalšího `## `)."""
    m = re.search(r"\n## %s\." % re.escape(nazev), text)
    if not m:
        return ""
    zbytek = text[m.start():]
    m2 = re.search(r"\n## ", zbytek[4:])
    return zbytek[:m2.start() + 4] if m2 else zbytek


def souhrn_g3(vystup):
    """(celkem, deklarovaných, NEDEKLAROVANÝCH) z výstupu `g3` — DVA TVARY."""
    m = re.search(r"NENULOVÉ EXITY:\s*(\d+)[^\n]*deklarovaných \(očekávaných\)\s*(\d+)"
                  r"[^\n]*NEDEKLAROVANÝCH\s*(\d+)", vystup)
    if m:
        return tuple(int(x) for x in m.groups())
    if re.search(r"NENULOVÉ EXITY:\s*0\b", vystup):
        return (0, 0, 0)
    return None


@contextlib.contextmanager
def docasne_nahrad(cesta, obsah: bytes):
    """Zapíše `obsah` do `cesta` a v `finally` vrátí PŮVODNÍ BAJTY (sha kontrola).

    Používá se pro „dobovou kotvu": měřidlo P26 se musí dát pustit nad verzí
    testu, o které jeho tvrzení platí. Návrat je bajt na bajt — jinak by se
    z měření stala tichá ztráta práce.
    """
    p = pathlib.Path(cesta)
    puvodni = p.read_bytes() if p.is_file() else None
    pred = hashlib.sha256(puvodni).hexdigest() if puvodni is not None else None
    p.write_bytes(obsah)
    try:
        yield
    finally:
        if puvodni is None:
            p.unlink(missing_ok=True)
        else:
            p.write_bytes(puvodni)
            if hashlib.sha256(p.read_bytes()).hexdigest() != pred:
                raise ValueError("docasne_nahrad: NÁVRAT SELHAL — %s" % p)


# ═══════════════════════════════════════════════════════════════════ A1 ═══
_CIZI = "NEMĚŘENO"


def cizi_skill():
    """Cesty, na kterých je `over-skilly` červená a které v repu NEJSOU.

    ⚠ STAV MIMO REPO (naměřeno 8. 10. 2026 v P27): SKILL `game-developer`
    v `~\\.dsh\\skills\\` **mimo repo** odkazuje na cesty, které v repu orchestra
    neexistují (patří sourozeneckému projektu `game-clone`); skill **změnila
    cizí session** během P27 (mtime 8. 10. 2026 11:22). Tenhle stav shodí
    `g3`/`validate-all` i SLOŽENÁ měřidla (p26-a, p25-a, p24-a, p26-b) — proto
    se hlásí jako POJMENOVANÝ STAV, ne jako vada orchestra.
    Vrací `None`, když je `over-skilly` zelená (nebo padá na cestách V REPU).
    """
    global _CIZI
    if _CIZI != "NEMĚŘENO":
        return _CIZI
    kod, v = cmd(["python", str(TOOLS / "over-skilly.py")], timeout=600)
    _CIZI = None
    if kod != 0:
        cesty = re.findall(r"ř\.\s*\d+:\s*(\S+)", v)
        v_repe = [c for c in cesty if (WS / c.replace("\\", "/")).exists()]
        if cesty and not v_repe:
            _CIZI = cesty
            print("      ⚠ STAV MIMO REPO: `over-skilly` (exit %d) padá na cestách "
                  "%s — patří jinému projektu; shodí i složená měřidla"
                  % (kod, cesty[:3]))
    return _CIZI


def slozene_mimo_repo(nazev, kod, v):
    """True = červená je VYSVĚTLENÁ stavem mimo repo (a je pojmenovaná)."""
    c = cizi_skill()
    if c and kod != 0 and "over-skilly" in v:
        nezmereno_zapis(nazev,
                        "STAV MIMO REPO: `over-skilly` je červená na cestách "
                        "skillu (%s) → měřidlo padá kvůli tomu, ne kvůli "
                        "orchestře" % ", ".join(c[:3]))
        return True
    return False


_P26A_A4 = "NEMĚŘENO"


def p26a_a4_na_skille():
    """MĚŘÍ MECHANISMUS: padá `p26-a --jen A4` na `over-skilly`? (kvůli `p26-b` M3a)"""
    global _P26A_A4
    if _P26A_A4 != "NEMĚŘENO":
        return _P26A_A4
    kd, vd = cmd(["python", str(P26_A), "--jen", "A4"], timeout=1800)
    _P26A_A4 = bool(kd != 0 and "over-skilly" in vd)
    print("      mechanismus: `p26-a --jen A4` padá na `over-skilly`: %s"
          % _P26A_A4)
    return _P26A_A4


def a1():
    print("\n--- A1: měří měřidlo P26 to, co tvrdí? (kontramutace v KOPIÍCH) ---")
    s56 = sekce("56", HANDOFF.read_text(encoding="utf-8", errors="replace"))
    check("A1 §56 existuje (délka %d znaků)" % len(s56), len(s56) > 3000, True)

    # KONTROLA: měřidlo P26 musí projít na NEZMUTOVANÝCH vstupech — bez toho by
    # „spadlo po mutaci" mohlo znamenat jen to, že je rozbité pořád.
    kod, v = cmd(["python", str(P26_A), "--jen", "A5,A6"])
    check("A1a KONTROLA: měřidlo P26 na nemutovaných vstupech → exit 0", kod, 0)
    check("A1a KONTROLA: a má čítač (naměřeno %s)" % (citac(v),), citac(v) is not None, True)

    SCRATCH.mkdir(parents=True, exist_ok=True)
    kopie_h = SCRATCH / "k-handoff.md"        # ⚠ jméno NESMÍ začínat „handoff"
    kopie_g = SCRATCH / "k-g3.py"             # (jinak ho ov-g počítá jako „mimo živé zdroje")
    kopie_o = SCRATCH / "k-ovg.py"
    shutil.copyfile(HANDOFF, kopie_h)
    shutil.copyfile(G3, kopie_g)
    shutil.copyfile(OV_G, kopie_o)

    # (1) HANDOFF bez oddílu §55 → A1 měřidla P26 musí spadnout
    print("    (1) kopie handoffu bez `## 55.`")
    try:
        with mutuj(kopie_h, "## 55. P25 —", "## 5U. P25 —"):
            check("A1b1 mutace se provedla (§55 v kopii není)",
                  "## 55. P25 —" not in kopie_h.read_text(encoding="utf-8"), True)
            kod, v = cmd(["python", str(P26_A), "--jen", "A1",
                          "--handoff", str(kopie_h)])
        check("A1b1 měřidlo P26 po vzetí §55 SPADLO", kod != 0, True)
        ch = [x for x in cervene(v) if "§55" in x]
        check("A1b1 a spadlo na KONTROLE §55 (ne na něčem jiném)", bool(ch), True)
        if ch:
            print("        · %s" % ch[0][:110])
    except ValueError as e:
        nezmereno_zapis("A1b1 kontramutace handoffu", str(e))
    check("A1b1 kopie handoffu je vrácena (hash sedí s živým)", sha(kopie_h), sha(HANDOFF))

    # (2) `g3` s JEDNOU branou NAVÍC → měřidlo P26 to musí vidět.
    # ⚠ NAMĚŘENO 8. 10. 2026: přepínač `--g3` je v DÁVKOVÉM režimu A4 **mrtvý** —
    # kontrola počtu bran je v `a4()` AŽ ZA `if not plne: return`.
    print("    (2) kopie g3 s 50. branou v seznamu BRANY")
    try:
        # ⚠ `BRANY= [` (bez mezery) — jinak by nový text OBSAHOVAL starý
        # podřetězec a `mutuj` by mutaci správně odmítl.
        with mutuj(kopie_g, "BRANY = [",
                   'BRANY= [("p27-fixtura", ["python", "x.py"]),'):
            check("A1b2 mutace se provedla (fixtura v kopii g3 je)",
                  "p27-fixtura" in kopie_g.read_text(encoding="utf-8"), True)
            kb, vb = cmd(["python", str(P26_A), "--jen", "A4"], timeout=1800)
            kod, v = cmd(["python", str(P26_A), "--jen", "A4", "--g3", str(kopie_g)])
            # ⚠ SROVNÁVÁ SE ČÍTAČ S BASELINE, ne `exit 0`: dávkové A4 může být
            # červené z JINÉHO důvodu (např. cizí stav skillu) — a pak by
            # „pozměněná kopie g3 nic neovlivní" nešlo změřit vůbec.
            check("A1b2a NÁLEZ O MĚŘIDLE: v DÁVKOVÉM režimu `--g3` nic neovlivní "
                  "(stejný čítač jako bez kopie)", citac(v), citac(vb))
    except ValueError as e:
        nezmereno_zapis("A1b2 kontramutace g3", str(e))
    check("A1b2 kopie g3 je vrácena (hash sedí s živou)", sha(kopie_g), sha(G3))

    # (2b) TVRZENÍ V §55 POSUNUTÉ (83/83 → 82/83) → A4 měřidla P26 musí spadnout.
    # Tím se měří, že měřidlo čte číslo Z DOKUMENTU (ne že ho má zapečené).
    print("    (2b) kopie handoffu s posunutým číslem v §55 (83/83 → 82/83)")
    text_h = HANDOFF.read_text(encoding="utf-8")
    m55 = re.search(r"\n## 55\.", text_h)
    i55 = m55.start() if m55 else None
    m2 = re.search(r"\n## ", text_h[i55 + 4:]) if i55 is not None else None
    j55 = (i55 + 4 + m2.start()) if (i55 is not None and m2) else None
    if i55 is None or j55 is None:
        nezmereno_zapis("A1b2b posun čísla v §55", "oddíl §55 se nedá vymezit")
    else:
        s55 = text_h[i55:j55]
        stary = "**83/83**"
        check("A1b2b kotva čísla je v §55 právě 1× (ne jen v dokumentu)",
              s55.count(stary), 1)
        if s55.count(stary) == 1:
            kopie2 = SCRATCH / "k-handoff2.md"
            zmut = text_h[:i55] + s55.replace(stary, "**82/83**", 1) + text_h[j55:]
            kopie2.write_bytes(zmut.encode("utf-8"))
            check("A1b2b mutace se provedla a JEN v §55",
                  ("**82/83**" in zmut
                   and zmut.count("**83/83**") == text_h.count("**83/83**") - 1), True)
            kod, v = cmd(["python", str(P26_A), "--jen", "A4",
                          "--handoff", str(kopie2)])
            check("A1b2b měřidlo P26 nad POSUNUTÝM číslem SPADNE", kod != 0, True)
            check("A1b2b a spadne na kontrole, KTERÁ ČTE TVRZENÍ Z DOKUMENTU",
                  any("úplnost handoffu = tvrzených" in x for x in cervene(v)), True)

    # (3) `ov-g` bez hlášení rozsahu MIMO živé zdroje → A5 musí spadnout
    print("    (3) kopie `ov-g-neovereno.py` bez hlášení „MIMO ŽIVÉ ZDROJE“")
    try:
        # ⚠ PREDIKÁT MUSÍ MÍŘIT NA KÓD, NE NA KOMENTÁŘ: řetězec „MIMO ŽIVÉ
        # ZDROJE“ je v tom skriptu i v komentáři, který vadu popisuje —
        # kontrola „řetězec v souboru není“ by hlásila, že se mutace
        # neprovedla, i když se provedla (past `overovani` §10.1).
        with mutuj(kopie_o,
                   '    print("\\n  ── MIMO ŽIVÉ ZDROJE (zmrazené kopie a zálohy'
                   ' — ZÁMĚRNĚ se nečtou) ──")',
                   '    print("\\n  ── (hlášení rozsahu mimo živé zdroje je vypnuto)"'
                   ' ──")'):
            text_o = kopie_o.read_text(encoding="utf-8")
            check("A1b3 mutace se provedla (VYPISOVACÍ řádek je pryč, komentář zůstal)",
                  ("je vypnuto" in text_o
                   and "── MIMO ŽIVÉ ZDROJE (zmrazené kopie" not in text_o), True)
            kod, v = cmd(["python", str(P26_A), "--jen", "A5", "--ovg", str(kopie_o)])
        check("A1b3 měřidlo P26 po vypnutí hlášení rozsahu SPADLO", kod != 0, True)
        ch = [x for x in cervene(v) if "MIMO" in x]
        check("A1b3 a spadlo na HLÁŠENÍ ROZSAHU (ne na něčem jiném)", bool(ch), True)
        if ch:
            print("        · %s" % ch[0][:110])
    except ValueError as e:
        nezmereno_zapis("A1b3 kontramutace ov-g", str(e))
    check("A1b3 kopie ov-g je vrácena (hash sedí s živou)", sha(kopie_o), sha(OV_G))

    # (4) mutační důkaz P26 — musí vykázat SVŮJ čítač a ten musí sedět na §56
    print("    (4) `p26-b-mutace.py` (mutační důkaz měřidla P26)")
    kod, v = cmd(["python", str(P26_B)], timeout=3600)
    c = citac(v)
    tv = najdi56(r"p26-b-mutace\.py`\s*→\s*\*\*(\d+) kontrol, (\d+) chyb\*\*",
                 "p26-b-mutace.py")
    # ⚠ `p26-b` padá, když se rozpadne diferenciál M3a — a ten pouští
    # `p26-a --jen A4`, kde je i kontrola `over-skilly` (skill MIMO repo).
    # Proto se ten MECHANISMUS měří: je `p26-a --jen A4` červené na skille?
    if cizi_skill() and kod != 0:
        if p26a_a4_na_skille():
            nezmereno_zapis("A1c p26-b-mutace.py = 26/0 (naměřeno %s)" % (c,),
                            "STAV MIMO REPO: `p26-a --jen A4` padá na "
                            "`over-skilly` (cesty SKILLU MIMO REPO) → diferenciál "
                            "M3a nemůže projít")
        else:
            check("A1c p26-b-mutace.py → exit 0 (naměřeno %s)" % (c,), kod, 0)
    else:
        check("A1c p26-b-mutace.py → exit 0 (naměřeno %s)" % (c,), kod, 0)
    if tv and not (cizi_skill() and c and c[1] > 0 and p26a_a4_na_skille()):
        check("A1c p26-b-mutace.py = tvrzených %d/%d" % tv, c, tv)
    check("A1c mutací bylo víc než jedna (jinak by důkaz nic nevážil)",
          (c[0] if c else 0) > 10, True)


# ═══════════════════════════════════════════════════════════════════ A2 ═══
def a2():
    print("\n--- A2: VOLÁ test tiku SEDM nových endpointů? (zarážka V HANDLERU) ---")
    kde = blob("HEAD", "conductor/src/index.ts")
    if kde is None:
        nezmereno_zapis("A2 kontrola čistoty zdroje",
                        "git show HEAD:conductor/src/index.ts selhalo")
        return
    cisty = hashlib.sha256(kde).hexdigest() == sha(SRC)
    if not cisty:
        print("      POZNÁMKA: zdroj conductora NENÍ shodný s `HEAD` (pracovní strom)")

    for pref, cesta, kotva in ZARAZKY:
        print("    zarážka v handleru %s" % cesta)
        # ⚠ NÁHRADA NESMÍ OBSAHOVAT KOTVU (jinak ji `mutuj` správně odmítne jako
        # „kontrola by hledala totéž", omyly #18/#106) — proto se podmínka
        # rozšíří (`|| path === "/p27-zarazka"`), místo aby se jen vložil return.
        nahrada = ('if (path === "%s" || path === "/p27-zarazka") '
                   '{ return json({ error: "zarazka-p27%s" }, 599);'
                   % (cesta, cesta.replace("/", "-")))
        try:
            with mutuj(SRC, kotva, nahrada) as m:
                check("A2 %s zarážka se provedla (hash před != po)" % cesta,
                      m.hash_pred != m.hash_po_mutaci, True)
                kod, v = cmd(["node", str(TEST_TIK)], timeout=1800)
            if cisty:
                check("A2 %s zdroj je po zarážce zpět (disk == HEAD)" % cesta,
                      sha(SRC), hashlib.sha256(kde).hexdigest())
        except ValueError as e:
            nezmereno_zapis("A2 zarážka v handleru %s" % cesta, str(e))
            continue
        cr = cervene(v)
        cilene = [x for x in cr if x.startswith("%s:" % pref)]
        print("      test tiku: čítač=%s, červených=%d, z toho `%s:` = %d"
              % (citac(v), len(cr), pref, len(cilene)))
        for x in cilene[:3]:
            print("        · %s" % x[:100])
        check("A2 %s zarážka ZAPLA kontroly `%s:` (aspoň 1)" % (cesta, pref),
              len(cilene) >= 1, True)
        check("A2 %s a kontrolní `A: /tick odpoví 200` zůstala ZELENÁ" % cesta,
              "A: /tick odpoví 200" in zelene(v), True)
    if cisty:
        check("A2 zdroj conductora je na konci čistý (disk == HEAD)",
              sha(SRC), hashlib.sha256(kde).hexdigest())


# ═══════════════════════════════════════════════════════════════════ A3 ═══
def a3():
    print("\n--- A3: tvrdí nové testy OBSAH, nebo jen `status === 200`? ---")
    kod0, v0 = cmd(["node", str(TEST_TIK)], timeout=1800)
    c0 = citac(v0)
    check("A3 KONTROLA: živý test tiku → exit 0 (naměřeno %s)" % (c0,), kod0, 0)
    shutil.copyfile(TEST_TIK, KOPIE_TESTU)
    try:
        try:
            with mutuj(
                KOPIE_TESTU,
                "    zapis(sql);\n    // ── P27 / Úkol B1: ČTECÍ ENDPOINTY",
                "    zapis(sql);\n    if (true) return { results: [] };"
                "   // P27/A3 zarážka\n    // ── P27 / Úkol B1: ČTECÍ ENDPOINTY",
            ) as m:
                check("A3 mutace se provedla (hash před != po)",
                      m.hash_pred != m.hash_po_mutaci, True)
                kod, v = cmd(["node", str(KOPIE_TESTU)], timeout=1800)
        except ValueError as e:
            nezmereno_zapis("A3 kopie testu s prázdnou falešnou D1", str(e))
            return
        cr = cervene(v)
        zl = zelene(v)
        print("      s PRÁZDNOU falešnou D1: čítač=%s, červených=%d" % (citac(v), len(cr)))
        for pref in ("X", "Y", "Z", "AA", "AB", "AC", "AD"):
            cil = [x for x in cr if x.startswith("%s:" % pref)]
            check("A3 prázdná odpověď SHODÍ obsahové kontroly `%s:`" % pref,
                  len(cil) >= 1, True)
            if cil:
                print("        · %s" % cil[0][:100])
        # TOHLE JE CELÝ SMYSL ETAPY: kontrola „odpoví 200" prázdnou odpověď
        # NEODLIŠÍ — kdyby testy tvrdily jen ji, byla by zelená nad ničím.
        for popis in ("Y: /queue odpoví 200", "Z: /roadmap odpoví 200",
                      "AA: /failed odpoví 200", "AB: /status odpoví 200",
                      "AC: /workers odpoví 200", "AD: /games odpoví 200",
                      "X: /health jde BEZ tajemství (veřejný pro monitoring)"):
            check("A3 a kontrola „%s“ zůstala ZELENÁ (tvar projde i nad prázdnem)"
                  % popis, popis in zl, True)
    finally:
        if KOPIE_TESTU.exists():
            KOPIE_TESTU.unlink()
    check("A3 kopie testu je uklizena (v `tools/` nezůstala)",
          KOPIE_TESTU.exists(), False)


# ═══════════════════════════════════════════════════════════════════ A4 ═══
def najdi56(vzory, nazev):
    """Tvrzení PŘEČTENÉ Z §56 (ne zapečené v kódu). Vrací tuple intů nebo None.

    ⚠ `vzory` smí být víc: táž hodnota bývá v dokumentu jednou v tabulce
    (`` `nástroj` → **3/0** ``) a podruhé v PRÓZE („živé měření je **3/0**") —
    a kdo hledá jen první tvar, vykáže „číslo v dokumentu není" (past
    `dokumentace` §2: číslo bez jednotky je pro vzor neviditelné).
    """
    if isinstance(vzory, str):
        vzory = [vzory]
    s56 = sekce("56", HANDOFF.read_text(encoding="utf-8", errors="replace"))
    for vzor in vzory:
        shody = [tuple(int(g) for g in m.groups()) for m in re.finditer(vzor, s56)]
        if not shody:
            continue
        jedine = sorted(set(shody))
        if len(jedine) > 1:
            nezmereno_zapis("A4 tvrzení §56: %s" % nazev,
                            "vzor má v §56 VÍC hodnot: %s" % jedine)
            return None
        return jedine[0]
    nezmereno_zapis("A4 tvrzení §56: %s" % nazev,
                    "číslo v §56 není (ani v tabulce, ani v próze)")
    return None


def ziva_sluzba():
    """Změří TVAR odpovědí sedmi endpointů na ŽIVÉ službě. Nic nezapisuje.

    ⚠ Cloudflare blokuje `Python-urllib` (403, error code 1010) — posílá se
    User-Agent prohlížeče (naměřeno v P24/P25).
    """
    import urllib.error
    import urllib.request

    env = {}
    p = WS / ".env"
    # ⚠ `utf-8-sig`, NE `utf-8`: `.env` i `.secrets/cf-secrets.json` mají na
    # začátku **UTF-8 BOM**, takže klíč vyjde jako `"\ufeffFORGE_URL"` a hledání
    # `env.get("FORGE_URL")` **tiše selže** (naměřeno 8. 10. 2026 v P27).
    if p.is_file():
        for l in p.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            if "=" in l and not l.strip().startswith("#"):
                k, _, v2 = l.partition("=")
                env[k.strip()] = v2.strip()
    # Když `.env` tajemství nenese, je v trezoru Cloudflare (`.secrets/cf-secrets.json`).
    if not env.get("FORGE_SECRET"):
        q = WS / ".secrets" / "cf-secrets.json"
        if q.is_file():
            try:
                env["FORGE_SECRET"] = json.loads(
                    q.read_text(encoding="utf-8-sig")).get("WEBHOOK_SECRET", "")
            except Exception:
                pass
    url = env.get("FORGE_URL", "").rstrip("/")
    taj = env.get("FORGE_SECRET", "")
    if not url or not taj:
        nezmereno_zapis("A4 živá služba", "chybí FORGE_URL nebo tajemství (.env/.secrets)")
        return

    def volej(cesta, secret=True):
        req = urllib.request.Request(url + cesta)
        req.add_header("User-Agent", "Mozilla/5.0 (forge-p27)")
        if secret:
            req.add_header("x-forge-secret", taj)
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.status, json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode("utf-8", "replace"))
            except Exception:
                return e.code, None
        except Exception as e:                                # síť / TLS
            return None, str(e)[:120]

    print("      živá služba: %s" % url)
    kod, b = volej("/health", secret=False)
    check("A4 živě /health bez tajemství → 200 (veřejný, kvůli monitoringu)", kod, 200)
    if isinstance(b, dict):
        check("A4 živě /health má TVAR, který testy offline předpokládají",
              [k for k in ("ok", "ready", "running", "games", "workers", "targets")
               if k not in b], [])
        print("      §56 tvrdí ok=true ready=1 running=0 games=1 a běh 323 (failure);")
        print("      NAMĚŘENO TEĎ: ok=%s ready=%s running=%s games=%s (stav se mění v čase)"
              % (b.get("ok"), b.get("ready"), b.get("running"), b.get("games")))
        cile = b.get("targets") or []
        check("A4 živě: /health hlásí i stav CÍLE (aspoň jedna hra)", len(cile) >= 1, True)

    # Šest CHRÁNĚNÝCH endpointů: bez tajemství 401 (pojistka je živá), s ním 200.
    klice = {"/queue": "tasks", "/roadmap": "roadmap", "/failed": "tasks",
             "/status": "runs", "/workers": "workers", "/games": "games"}
    bez, s_tajemstvim = [], []
    for cesta, klic in klice.items():
        k1, _ = volej(cesta, secret=False)
        if k1 != 401:
            bez.append("%s → %s" % (cesta, k1))
        k2, b2 = volej(cesta, secret=True)
        if k2 != 200 or not isinstance(b2, dict) or klic not in b2:
            s_tajemstvim.append("%s → %s/%s" % (cesta, k2, klic))
        elif not isinstance(b2.get(klic), list):
            s_tajemstvim.append("%s: `%s` není seznam" % (cesta, klic))
    check("A4 živě: každý chráněný endpoint vrátí BEZ tajemství 401", bez, [])
    check("A4 živě: se tajemstvím vrátí 200 a SVŮJ klíč-seznam", s_tajemstvim, [])
    print("      (živá služba se jen ČTE — `/tick` ani `/poll` se nevolá: měnily by stav)")


def a4(plne):
    print("\n--- A4: každé číslo tvrzené v §56 se znovu NAMĚŘÍ ---")
    # ⚠ KONTROLA ROZSAHU, NE SEZNAMU: kdyby §56 z dokumentu zmizel, všechny
    # `najdi56` by vrátily „číslo v dokumentu není" (`NEZMĚŘENO`) a měřidlo by
    # skončilo ZELENÉ nad dokumentem, který nikdy neotevřelo (`overovani` §7.10).
    s56 = sekce("56", HANDOFF.read_text(encoding="utf-8", errors="replace"))
    check("A4 §56 existuje a je netriviálně dlouhý (délka %d znaků)" % len(s56),
          len(s56) > 3000, True)
    ziva_sluzba()

    # ── LEVNÉ (běží i v dávce) ────────────────────────────────────────────
    kod, v = cmd(["python", str(ANALYZA / "handoff-kontrola-uplnost.py")], timeout=600)
    m = re.search(r"kontrolovaných klíčů:\s*(\d+)", v)
    m2 = re.search(r"nalezených:\s*(\d+)", v)
    tv = najdi56(r"`handoff-kontrola-uplnost`\s*→\s*\*\*(\d+)/(\d+)\*\*",
                 "handoff-kontrola-uplnost")
    check("A4 handoff-kontrola-uplnost.py → exit 0", kod, 0)
    if m and m2 and tv:
        check("A4 úplnost handoffu = tvrzených %d/%d" % tv,
              (int(m.group(1)), int(m2.group(1))), tv)

    kod, v = cmd(["python", str(TOOLS / "over-skilly.py")], timeout=900)
    ms = re.search(r"Skillů:\s*(\d+),\s*chyb:\s*(\d+)", v)
    tv = najdi56(r"`over-skilly`\s*\*\*(\d+)/(\d+)\*\*", "over-skilly")
    # ⚠ STAV MIMO REPO (naměřeno 8. 10. 2026 v P27): `over-skilly` padá, protože
    # SKILL `game-developer` v `~\.dsh\skills\` (MIMO repo) odkazuje na cesty,
    # které v repu orchestra nejsou (patří sourozenci `E:\Workspaces\game-clone`).
    # Skill **změnila cizí session** během P27 (mtime 8. 10. 2026 11:22). Je to
    # **stav mimo repo**, ne vada orchestra — a shodí i složená měřidla.
    if kod == 0:
        check("A4 over-skilly.py → exit 0", kod, 0)
    else:
        cesty = re.findall(r"ř\.\s*\d+:\s*(\S+)", v)
        v_repe = [c for c in cesty if (WS / c.replace("\\", "/")).exists()]
        check("A4 over-skilly.py padá JEN na cestách MIMO REPO "
              "(žádná z nahlášených v repu NENÍ)", v_repe, [])
        nezmereno_zapis("A4 over-skilly.py → exit %d (13/0)" % kod,
                        "STAV MIMO REPO: skill `game-developer` (mimo repo) "
                        "odkazuje na %s — patří sourozenci `game-clone`; "
                        "skill změnila cizí session" % (cesty or "?"))

    if ms and tv:
        check("A4 over-skilly.py = tvrzených %d/%d" % tv,
              (int(ms.group(1)), int(ms.group(2))), tv)

    kod, v = cmd(["python", str(TOOLS / "over-dokumentaci.py")], timeout=900)
    md = re.search(r"Kontrol:\s*(\d+),\s*chyb:\s*(\d+)", v)
    tv = najdi56([r"`over-dokumentaci`\s*\*\*(\d+)/(\d+)\*\*",
                  r"\*\*živé měření je (\d+)/(\d+)\*\*"], "over-dokumentaci")
    check("A4 over-dokumentaci.py → exit 0", kod, 0)
    if md and tv:
        check("A4 over-dokumentaci.py = tvrzených %d/%d" % tv,
              (int(md.group(1)), int(md.group(2))), tv)

    kod, v = cmd(["python", str(OV_G)], timeout=600)
    mr = re.search(r"nálezů \(řádků tabulek Hxx\) CELKEM:\s*(\d+)", v)
    check("A4 ov-g-neovereno.py → exit 0 (0× NEOVĚŘENO)", kod, 0)
    check("A4 ov-g-neovereno.py měří CELÝ rozsah (99 řádků Hxx)",
          int(mr.group(1)) if mr else None, 99)

    kod, v = cmd(["python", str(KRONIKA.parent / "_analyza" / "kronika-kontrola.py")],
                 timeout=600)
    check("A4 kronika-kontrola.py → exit 0 a hlásí SEDÍ",
          (kod, "SEDÍ" in v.upper()), (0, True))

    # ── DLOUHÉ (jen s `--plne`) ───────────────────────────────────────────
    if not plne:
        for popis in ("p26-a-overeni.py --plne", "p26-b-mutace.py", "p25-a --plne",
                      "p25-b-mutace.py", "p24-a-overeni.py", "p24-b-mutace.py",
                      "test-tick-offline.mjs", "tick-mutace.py", "g3-brany.py",
                      "validate-all.mjs"):
            nezmereno_zapis("A4 %s" % popis,
                            "dávkový režim (dlouhé běhy); pouští se s `--plne`")
        return

    # ── STAV MIMO REPO: viz `cizi_skill()` (skill `game-developer` mimo repo) ─
    # Tenhle stav shodí i SLOŽENÁ měřidla — hlásí se jako POJMENOVANÝ STAV, aby
    # se „červené skoro všechno" nečetlo jako vada orchestra.
    cizi = cizi_skill()

    # 1) měřidlo P26 a jeho mutační důkaz
    # ⚠ PŘEDPOKLAD: měřidlo P26 má **90 kontrol nad ČERSTVÝM inventářem** a **86
    # nad ZASTARALÝM** — jeho A6 totiž u zastaralého inventáře hlásí pojmenovaný
    # STAV místo čtyř `check(...)` (g3 exit, g3 bez čítače, validate-all ×2).
    # Naměřeno 8. 10. 2026 v P27 OBĚMA směry. Kdo to nezměří, zapíše „čítač
    # nesedí" jako vadu měřidla, ačkoli je to STAV (`overovani` §7.13).
    k_riz, v_riz = cmd(["python", str(RIZIKA)], timeout=900)
    inventar_cerstvy = (k_riz == 0)
    kod, v = cmd(["python", str(P26_A), "--plne"], timeout=5400)
    c26 = citac(v)
    cerv26 = cervene(v)
    tv = najdi56(r"p26-a-overeni\.py --plne`\s*→\s*\*\*(\d+) kontrol, (\d+) chyb\*\*",
                 "p26-a-overeni.py --plne")
    print("      p26-a --plne: čítač=%s, červených=%d, inventář čerstvý=%s"
          % (c26, len(cerv26), inventar_cerstvy))
    for x in cerv26[:6]:
        print("        · %s" % x[:120])
    if not inventar_cerstvy:
        nezmereno_zapis("A4 p26-a-overeni.py --plne = 90/0",
                        "během měření byl inventář ZASTARALÝ → p26-a hlásí "
                        "pojmenovaný STAV (4 kontroly místo `check`); náprava je "
                        "přegenerovat inventář a spustit znovu")
        check("A4 a úbytek proti tvrzeným 90 kontrolám je PRÁVĚ 4 (cena stavu)",
              (90 - c26[0]) if c26 else None, 4)
    elif slozene_mimo_repo("p26-a-overeni.py --plne", kod, v):
        check("A4 a p26-a má v červených JMÉNO VINÍKA (`over-skilly`)",
              any("over-skilly" in x for x in cerv26), True)
    elif tv:
        if c26 == tv:
            check("A4 p26-a-overeni.py --plne = tvrzených %d/%d" % tv, c26, tv)
        else:
            # ⚠ NÁLEZ P27: měřidlo P26 čte tvrzení z JEDNOHO historického oddílu
            # (§55) a porovnává je s ŽIVÝM měřením. Když pozdější session
            # legitimně změní čítač testu (§55 tvrdí 146, dnes 205), je červená
            # PŘESNĚ ta jedna kontrola — a nic jiného.
            jen_test = [x for x in cerv26
                        if "test-tick-offline" in x and "tvrzených" in x]
            check("A4 p26-a --plne: odchylka od §56 je PRÁVĚ kontrola čítače testu "
                  "(dobová kotva, ne vada)", (len(cerv26), len(jen_test)), (1, 1))
            check("A4 a počet kontrol zůstal (jen jedno číslo se posunulo)",
                  (c26 or (0, 0))[0], tv[0])
    kod, v = cmd(["python", str(P26_B)], timeout=1800)
    c = citac(v)
    tv = najdi56(r"p26-b-mutace\.py`\s*→\s*\*\*(\d+) kontrol, (\d+) chyb\*\*",
                 "p26-b-mutace.py")
    if not slozene_mimo_repo("p26-b-mutace.py", kod, v):
        if cizi_skill() and kod != 0 and p26a_a4_na_skille():
            nezmereno_zapis("p26-b-mutace.py (v A4)",
                            "STAV MIMO REPO: diferenciál M3a pouští "
                            "`p26-a --jen A4`, které padá na `over-skilly`")
        else:
            check("A4 p26-b-mutace.py → exit 0 (naměřeno %s)" % (c,), kod, 0)
    if tv and not (cizi_skill() and c and c[1] > 0 and p26a_a4_na_skille()):
        check("A4 p26-b-mutace.py = tvrzených %d/%d" % tv, c, tv)

    # 2) měřidla P25 / P24
    kod, v = cmd(["python", str(P25_A), "--plne"], timeout=5400)
    c = citac(v)
    tv = najdi56(r"`p25-a --plne`\s*\*\*(\d+)/(\d+)\*\*", "p25-a-overeni.py --plne")
    mimo25 = slozene_mimo_repo("p25-a-overeni.py --plne", kod, v)
    if not mimo25:
        check("A4 p25-a-overeni.py --plne → exit 0 (naměřeno %s)" % (c,), kod, 0)
    if tv and not mimo25:
        check("A4 p25-a-overeni.py --plne = tvrzených %d/%d" % tv, c, tv)

    kod, v = cmd(["python", str(P25_B)], timeout=1800)
    c = citac(v)
    tv = najdi56(r"`p25-b-mutace`\s*\*\*(\d+)/(\d+)\*\*", "p25-b-mutace.py")
    check("A4 p25-b-mutace.py → exit 0 (naměřeno %s)" % (c,), kod, 0)
    if tv:
        check("A4 p25-b-mutace.py = tvrzených %d/%d" % tv, c, tv)

    kod, v = cmd(["python", str(P24_A)], timeout=5400)
    c24 = citac(v)
    cerv24 = cervene(v)
    mimo_a8 = [x for x in cerv24 if not x.startswith("A8")]
    print("      p24-a: čítač=%s, červených=%d (mimo A8: %d)"
          % (c24, len(cerv24), len(mimo_a8)))
    check("A4 p24-a-overeni.py: 99 kontrol (stav hry měřen zvlášť)",
          c24[0] if c24 else None, 99)
    if not slozene_mimo_repo("p24-a-overeni.py (červené mimo A8)", kod, v):
        check("A4 p24-a-overeni.py: KAŽDÁ červená je A8 = dobový stav hry (ne vada)",
              mimo_a8, [])
    else:
        check("A4 a p24-a má v červených JMÉNO VINÍKA (`over-skilly`)",
              any("over-skilly" in x for x in mimo_a8), True)

    kod, v = cmd(["python", str(P24_B)], timeout=1800)
    c = citac(v)
    tv = najdi56(r"`p24-b-mutace`\s*\*\*(\d+)/(\d+)\*\*", "p24-b-mutace.py")
    check("A4 p24-b-mutace.py → exit 0 (naměřeno %s)" % (c,), kod, 0)
    if tv:
        check("A4 p24-b-mutace.py = tvrzených %d/%d" % tv, c, tv)

    # 3) test tiku — a DOBOVÁ KOTVA: tvrzení §56 platí o verzi z P26
    kod, v = cmd(["node", "tools/test-tick-offline.mjs"], timeout=1800)
    zivy = citac(v)
    check("A4 test-tick-offline.mjs (živý) → exit 0 (naměřeno %s)" % (zivy,), kod, 0)
    tv = najdi56(r"`test-tick-offline`\s*\*\*(\d+)/(\d+)\*\*", "test-tick-offline.mjs")
    rev = rev_podle_predmetu("^P26: zaznamy")
    if tv and rev:
        b = blob(rev, "tools/test-tick-offline.mjs")
        if b is None:
            nezmereno_zapis("A4 dobová kotva testu",
                            "v commitu %s není `tools/test-tick-offline.mjs`" % rev[:9])
        else:
            with docasne_nahrad(DOBOVA_KOPIE, b):
                check("A4 dobová kopie testu z %s existuje" % rev[:9],
                      DOBOVA_KOPIE.is_file(), True)
                kd, vd = cmd(["node", str(DOBOVA_KOPIE)], timeout=1800)
            dobovy = citac(vd)
            check("A4 dobově test z `%s` → exit 0 (naměřeno %s)" % (rev[:9], dobovy), kd, 0)
            check("A4 a TVRZENÍ §56 %d/%d o téhle verzi PLATÍ" % tv, dobovy, tv)
            if zivy and dobovy:
                check("A4 živý čítač je VYŠŠÍ než dobový (práce P27/B1 přidala kontroly)",
                      zivy[0] > dobovy[0], True)
                print("      posun: %d → %d kontrol (+%d) — z práce P27/B1"
                      % (dobovy[0], zivy[0], zivy[0] - dobovy[0]))
    check("A4 dobová kopie testu je uklizena", DOBOVA_KOPIE.exists(), False)

    kod, v = cmd(["python", str(TICK_MUT)], timeout=1800)
    c = citac(v)
    mv = re.search(r"vrat:\s*(\d+)", v)
    vrat = int(mv.group(1)) if mv else None
    tv = najdi56(r"`tick-mutace`\s*\*\*(\d+) vrat / (\d+)/(\d+)\*\*", "tick-mutace.py")
    check("A4 tick-mutace.py → exit 0 (naměřeno %s)" % (c,), kod, 0)
    if tv:
        check("A4 tick-mutace.py = tvrzených %d vrat / %d/%d" % tv,
              (vrat,) + c if c else None, tv)

    # 4) počet bran a deklarovaných exitů (čte se z KÓDU, ne z výpisu)
    strom = ast.parse(G3.read_text(encoding="utf-8", errors="replace"))
    brany, ocek = [], []
    for node in ast.walk(strom):
        if not isinstance(node, ast.Assign):
            continue
        jmena = [t_.id for t_ in node.targets if isinstance(t_, ast.Name)]
        if "BRANY" in jmena and isinstance(node.value, ast.List):
            brany = list(node.value.elts)
        if "OCEKAVANE_NENULOVE" in jmena and isinstance(node.value, ast.Dict):
            ocek = [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
    tv = najdi56(r"`g3`\s*→\s*\*\*(\d+) bran", "g3 počet bran")
    if tv:
        check("A4 g3 má %d bran (tvrzeno v §56: %d)" % (len(brany), tv[0]),
              len(brany), tv[0])
    check("A4 g3 má JEDEN deklarovaný nenulový exit (`zadání kontrola`)",
          len(ocek), 1)


# ═══════════════════════════════════════════════════════════════════ A5 ═══
RADEK_H = re.compile(r"^\|\s*\*\*(H\d+)\*\*\s*\|")


def radky_h(cesta):
    try:
        text = cesta.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return [l for l in text.splitlines() if RADEK_H.match(l)]


def zive_zdroje_h():
    """VLASTNÍ odvození živých zdrojů Hxx (ne opis toho, co dělá brána)."""
    zdroje = [WS / "HANDOFF.md"]
    if ARCHIV.is_dir():
        zdroje += sorted(p for p in ARCHIV.iterdir()
                         if p.is_file() and p.name.startswith("HANDOFF-")
                         and p.suffix == ".md")
    return [p for p in zdroje if p.is_file()]


def a5():
    print("\n--- A5: rozsah `ov-g-neovereno.py` (nález P25-K) ---")
    # (a) VLASTNÍ POČÍTADLO: kolik řádků Hxx je v živých zdrojích.
    zdroje = zive_zdroje_h()
    muj = {str(p.relative_to(WS)): len(radky_h(p)) for p in zdroje}
    soucet = sum(muj.values())
    print("      vlastní průchod: %s = %d" % (muj, soucet))
    check("A5 vlastní průchod najde 99 řádků Hxx (1 + 98)", soucet, 99)
    check("A5 a otevřel 3 živé zdroje (HANDOFF + 2 v `_archiv`)", len(zdroje), 3)

    # (b) měřidlo hlásí TOTÉŽ číslo a VYPISUJE, co otevřelo
    kod, v = cmd(["python", str(OV_G)], timeout=300)
    mr = re.search(r"nálezů \(řádků tabulek Hxx\) CELKEM:\s*(\d+)", v)
    otevreno = re.findall(r"^  OTEVŘENO:\s*(\S+)\s+řádků Hxx:\s*(\d+)", v, re.M)
    check("A5 živé měřidlo měří 99 řádků Hxx", int(mr.group(1)) if mr else None, 99)
    check("A5 a jeho součet po souborech = MŮJ součet (ne jen totéž číslo)",
          sum(int(n) for _, n in otevreno), soucet)
    check("A5 a VYPISUJE, které soubory otevřelo (`OTEVŘENO:`)", len(otevreno), 3)
    check("A5 a hlásí i rozsah MIMO živé zdroje (aby zúžení nebylo tiché)",
          "MIMO ŽIVÉ ZDROJE" in v, True)

    # (c) VLASTNÍ měření rozsahu MIMO živé zdroje — Python walk (grep tool
    #     přeskakuje skryté složky a `Select-String` soubory tiše vynechává).
    zit = {p.resolve() for p in zdroje}
    mimo = {}
    for p in sorted(WS.rglob("*.md")):
        if ".git" in p.parts or p.resolve() in zit:
            continue
        if not p.name.lower().startswith("handoff"):
            continue
        n = len(radky_h(p))
        if n:
            mimo[str(p.relative_to(WS))] = n
    mm = re.search(r"celkem mimo:\s*(\d+) řádků v (\d+) souborech", v)
    check("A5 rozsah mimo živé zdroje = MŮJ vlastní součet",
          (sum(mimo.values()), len(mimo)),
          (int(mm.group(1)), int(mm.group(2))) if mm else None)
    print("      mimo živé zdroje: %d řádků v %d souborech" % (sum(mimo.values()), len(mimo)))

    # (d) VERZE Z `HEAD` — oprava nesmí žít jen v pracovním stromě
    b = blob("HEAD", "_analyza/ov-g-neovereno.py")
    if b is None:
        nezmereno_zapis("A5 verze měřidla z HEAD", "git show HEAD:… selhalo")
    else:
        tmp = ANALYZA / "_p27-head-ovg.py"
        tmp.write_bytes(b)
        try:
            kd, vd = cmd(["python", str(tmp)], timeout=300)
            mh = re.search(r"nálezů \(řádků tabulek Hxx\) CELKEM:\s*(\d+)", vd)
            check("A5 i verze v `HEAD` měří 99 řádků (oprava je COMMITNUTÁ)",
                  int(mh.group(1)) if mh else None, 99)
            check("A5 a verze v `HEAD` skončila exit 0", kd, 0)
        finally:
            tmp.unlink(missing_ok=True)

    # (e) NEGATIVNÍ KONTROLA 1: fixtura s NEOVĚŘENO → měřidlo MUSÍ spadnout
    fixt = SCRATCH / "fixtura-nevereno.md"
    SCRATCH.mkdir(parents=True, exist_ok=True)
    fixt.write_text("# fixtura\n\n| # | Nález | Doklad |\n|---|---|---|\n"
                    "| **H900** | vymyšlený nález, který čeká | stav NEOVĚŘENO |\n",
                    encoding="utf-8", newline="")
    kod, v = cmd(["python", str(OV_G), "--handoff", str(fixt)], timeout=300)
    check("A5 NEGATIVNÍ KONTROLA: fixtura s NEOVĚŘENO → exit 1", kod, 1)
    check("A5 a měřidlo ten nález JMENUJE", "H900" in v, True)

    # (f) NEGATIVNÍ KONTROLA 2: PRÁZDNÝ rozsah → NEMĚŘENO, ne zelená
    prazdna = SCRATCH / "fixtura-prazdna.md"
    prazdna.write_text("# fixtura bez tabulky nálezů\n", encoding="utf-8", newline="")
    kod, v = cmd(["python", str(OV_G), "--handoff", str(prazdna)], timeout=300)
    check("A5 NEGATIVNÍ KONTROLA: prázdný rozsah → NEMĚŘENO (exit 1)", kod, 1)
    check("A5 a řekne to slovy (ne tichá zelená)", "NEMĚŘENO" in v, True)
    check("A5 obě fixtury existovaly (negativní kontroly neběžely nad ničím)",
          (fixt.is_file(), prazdna.is_file()), (True, True))


# ═══════════════════════════════════════════════════════════════════ A6 ═══
def a6(plne):
    print("\n--- A6: nic se nerozbilo ani neztratilo ---")
    kod, v = cmd(["python", str(ANALYZA / "kronika-kontrola.py")], timeout=600)
    check("A6 kronika-kontrola.py → exit 0", kod, 0)
    check("A6 a řekla SEDÍ (ne jen nespadla)", "SEDÍ" in v.upper(), True)
    kod, v = cmd(["python", str(ANALYZA / "handoff-kontrola-uplnost.py")], timeout=600)
    check("A6 handoff-kontrola-uplnost.py → exit 0", kod, 0)
    check("A6 a hlásí CHYBÍ: 0", "CHYBÍ:                0" in v or "CHYBÍ: 0" in v, True)
    kod, v = cmd(["python", str(OV_G)], timeout=600)
    check("A6 ov-g-neovereno.py → exit 0 a měří 99 řádků",
          (kod, "nálezů (řádků tabulek Hxx) CELKEM: 99" in v), (0, True))

    # Doklady P27 musí pokrýt vzor dávky `p20-d` a sondy patří do PRESKOCIT
    zdroj_p20 = P20_D.read_text(encoding="utf-8", errors="replace")
    mv = re.search(r"VZOR\s*=\s*re\.compile\(\s*r?[\"']([^\"']+)[\"']\s*\)", zdroj_p20)
    vzz = re.compile(mv.group(1)) if mv else None
    pres = set()
    for node in ast.walk(ast.parse(zdroj_p20)):
        if isinstance(node, ast.Assign) and any(
                isinstance(t_, ast.Name) and t_.id == "PRESKOCIT"
                for t_ in node.targets) and isinstance(node.value, ast.Set):
            pres = {e.value for e in node.value.elts if isinstance(e, ast.Constant)}
    check("A6 doklady P27 pokrývá vzor dávky `p20-d`",
          [j for j in ("p27-a-overeni.py", "p27-b-mutace.py")
           if vzz is None or not vzz.match(j)], [])
    check("A6 sondy P27 jsou v PRESKOCIT dávky",
          sorted(j for j in pres if j.startswith("p27-sonda")),
          ["p27-sonda-endpointy.py", "p27-sonda-inventar.py"])
    check("A6 negativní kontrola: predikát chybějící doklad NAJDE",
          [j for j in ("p27-a-overeni.py", "nedoklad-p27.py")
           if vzz is None or not vzz.match(j)], ["nedoklad-p27.py"])

    if not plne:
        nezmereno_zapis("A6 g3 a validate-all",
                        "dávkový režim (sahají na inventář a jsou dlouhé); "
                        "pouští se s `--plne`")
        return

    kod, v = cmd(["python", str(G3)], timeout=5400)
    ZAST = ("C2: mutace N1 (5 běhů)", "n1-over-inventar", "validate-all (CELEK)")
    # ⚠ DRUHÝ POJMENOVANÝ STAV: brány `over-skilly` (a její mutační dvojče)
    # měří SKILL MIMO REPO — viz vysvětlení v A4. Když padnou jen ony, je to
    # STAV MIMO REPO, ne vada orchestra (a `g3` kvůli nim končí nenulově).
    MIMO_REPO = ("over-skilly", "over-skilly: mutace delegovaných cest")
    jmena, nedekl = [], 0
    s = souhrn_g3(v)
    if s is None:
        nezmereno_zapis("A6 g3 souhrn", "souhrn ve výstupu g3 nenalezen")
    else:
        celkem, dekl, nedekl = s
        jmena = re.findall(r"NEOČEKÁVANÝ:\s*(.+?)\s*→", v)
        print("      g3: nenulových=%d deklarovaných=%d NEDEKLAROVANÝCH=%d %s"
              % (celkem, dekl, nedekl, jmena or ""))
        if dekl == 1:
            check("A6 g3: deklarovaný nenulový exit je právě 1", dekl, 1)
        else:
            # ⚠ STAVOVÉ ČÍSLO (naměřeno 8. 10. 2026 v P27): `zadání kontrola`
            # vrací 1 **jen když je hlavička zadání ZASTARALÁ** (kotva != HEAD).
            # Když sedí, vrací 0 a `g3` vypíše poznámku „už není potřeba" —
            # a to je POJMENOVANÝ STAV, ne chybějící deklarace. Kdo čeká
            # natvrdo 1, hlásí vadu na správném repu.
            poznamka = ("už není potřeba" in v) and ("zadání kontrola" in v)
            check("A6 g3: 0 nenulových exitů — a je to POJMENOVANÉ (hlavička "
                  "zadání SEDÍ na HEAD, deklarovaný exit se nespustil)",
                  poznamka, True)
        if nedekl:
            zname = [j for j in jmena if j in ZAST]
            mimo = [j.strip() for j in jmena if j.strip() in MIMO_REPO]
            if mimo and len(zname) + len(mimo) == len(jmena):
                nezmereno_zapis("A6 každý nedeklarovaný exit g3 je pojmenovaný STAV",
                                "g3 padá na branách %s — ty měří SKILL MIMO REPO, "
                                "ne orchestra (stav prostředí, ne vada repa)"
                                % ", ".join("`%s`" % m for m in mimo))
            else:
                check("A6 každý nedeklarovaný exit g3 je pojmenovaný STAV "
                      "(zastaralý inventář)", len(zname), len(jmena))
        else:
            check("A6 g3: žádný nedeklarovaný nenulový exit", nedekl, 0)
    mb = re.search(r"BRÁNY BEZ ČÍTAČE mimo deklarovaný stav:\s*(\d+)", v)
    pocet_bez = int(mb.group(1)) if mb else None
    jmena_bez = re.findall(r"BRÁNY BEZ ČÍTAČE[^\n]*→\s*(.+)", v)
    zastaraly = ("n1-over-inventar" in jmena) or ("validate-all (CELEK)" in jmena)
    if zastaraly and pocet_bez == 1 and jmena_bez and "C2:" in jmena_bez[0]:
        nezmereno_zapis("A6 g3: brány bez čítače mimo deklarovaný stav",
                        "1 = `%s` — odmítá měřit nad ZASTARALÝM inventářem "
                        "(náprava je PŘEGENEROVAT)" % jmena_bez[0].strip())
    else:
        check("A6 g3: brány bez čítače mimo deklarovaný stav", pocet_bez, 0)
    if kod == 0:
        check("A6 g3 → exit 0 (jen deklarované exity)", kod, 0)
    elif jmena and all((j in ZAST) or (j.strip() in MIMO_REPO) for j in jmena):
        # ⚠ DVA POJMENOVANÉ STAVY V JEDNOM BĚHU (naměřeno 8. 10. 2026 v P27):
        # (a) ZASTARALÝ INVENTÁŘ — do otisku vstupů vstupuje i `__pycache__`,
        #     který vzniká IMPORtem během běhu (náprava: přegenerovat);
        # (b) SKILL MIMO REPO (`over-skilly`) — cizí změna v `~\.dsh\skills\`.
        # Ani jeden není vada orchestra — a měřidlo to musí POJMENOVAT, ne
        # hlásit „g3 padá".
        nezmereno_zapis("A6 g3 → exit 0 (jen deklarované exity)",
                        "g3 padá na POJMENOVANÝCH STAVECH: %s "
                        "(zastaralý inventář = přegenerovat; `over-skilly` = "
                        "skill MIMO repo)" % ", ".join("`%s`" % j for j in jmena))
    else:
        check("A6 g3 → exit 0 (jen deklarované exity)", kod, 0)

    kod, v = cmd(["node", str(VALIDATE)], timeout=5400)
    if kod == 0:
        check("A6 validate-all.mjs → exit 0", kod, 0)
        check("A6 a hlásí VŠE V POŘÁDKU", "VŠE V POŘÁDKU" in v, True)
    elif "INVENTÁŘ JE ZASTARALÝ" in v:
        nezmereno_zapis("A6 validate-all → VŠE V POŘÁDKU",
                        "validate-all padá na ZASTARALÉM INVENTÁRI (náprava: "
                        "přegenerovat)")
    else:
        # Není to zastaralý inventář — ověř, jestli selhání neleží MIMO REPO
        # (skill `game-developer`); jinak je to skutečný nález.
        ko, vo = cmd(["python", str(TOOLS / "over-skilly.py")], timeout=600)
        cesty = re.findall(r"ř\.\s*\d+:\s*(\S+)", vo)
        v_repe = [c for c in cesty if (WS / c.replace("\\", "/")).exists()]
        if ko != 0 and cesty and v_repe == []:
            nezmereno_zapis("A6 validate-all → VŠE V POŘÁDKU",
                            "validate-all padá na `over-skilly` (exit %d), která "
                            "hlásí cesty SKILLU MIMO REPO (%s) — stav prostředí, "
                            "ne vada orchestra" % (ko, ", ".join(cesty[:3])))
        else:
            check("A6 validate-all.mjs → exit 0", kod, 0)
            check("A6 a hlásí VŠE V POŘÁDKU", "VŠE V POŘÁDKU" in v, True)


# ═══════════════════════════════════════════════════════════════════ A7 ═══
def a7():
    print("\n--- A7: inventář a brány po sobě (pořadí, otisk OBOU rep) ---")
    if not INVENTAR.is_file():
        nezmereno_zapis("A7 inventář", "`_analyza/_inventar.json` neexistuje")
        return
    text_inv = INVENTAR.read_text(encoding="utf-8", errors="replace")
    inv = json.loads(text_inv)
    ot = inv.get("otisk_vstupu") or {}
    check("A7 otisk vstupů počítá OBĚ repa (ne jen orchestra)", len(ot.get("repozitare") or []), 2)
    check("A7 a je v něm i sourozenecká hra", "uo-shadows" in text_inv, True)
    check("A7 otisk má verzi a sha256",
          bool(ot.get("verze")) and bool(ot.get("sha256")), True)

    def pregeneruj():
        r = subprocess.run(["python", str(NEANGL), "--json", str(INVENTAR)],
                           cwd=str(WS), capture_output=True, timeout=1800)
        if r.returncode != 0:
            return None
        d = json.loads(INVENTAR.read_text(encoding="utf-8"))
        return d.get("otisk_vstupu", {}).get("sha256")

    # (0) REGENERACE je součástí měření: A7 měří POŘADÍ (inventář → g3 →
    #     validate-all), takže si nejdřív musí ustavit čerstvý stav — jinak
    #     by měřilo zastaralý inventář a hlásilo to jako vadu brány.
    sha0 = pregeneruj()
    check("A7 přegenerování inventáře proběhlo (má sha256)", bool(sha0), True)
    if not sha0:
        nezmereno_zapis("A7 měření otisku", "přegenerování inventáře selhalo")
        return
    kod, v = cmd(["python", str(RIZIKA)], timeout=900)
    check("A7 KONTROLA: brána `hl-rizika-jazyka.py` na ČERSTVÉM inventáři → exit 0",
          kod, 0)
    if kod != 0:
        nezmereno_zapis("A7 měření otisku",
                        "inventář se nepodařilo uvést do čerstvého stavu")
        return

    # (1) DOKLAD podle vylučovacího vzoru otisk NEZMĚNÍ
    doklad = ANALYZA / "p27-a-overeni-vystup.txt"
    stavalo = doklad.is_file()
    doklad.write_bytes(b"# p27: doklad (vylouceny vzorem z otisku)\n")
    try:
        sha1 = pregeneruj()
        check("A7 doklad `*-vystup.txt` otisk NEZMĚNÍ (vyloučený artefakt)",
              sha1, sha0)
    finally:
        if not stavalo:
            doklad.unlink(missing_ok=True)

    # (2) JINÝ nový `.txt` otisk ZMĚNÍ a brána spadne POJMENOVANÝM STAVEM
    # ⚠ POŘADÍ JE MĚŘENÁ VĚC: brána musí spadnout v OKNĚ mezi přidáním souboru
    # a přegenerováním. Kdo po přidání hned přegeneruje, měří ČERSTVÝ inventář
    # a „brána nespadla" je falešný nález (naměřeno 8. 10. 2026 v P27).
    # ⚠ A PREDIKÁT MUSÍ BÝT KONKRÉTNÍ: v ZELENÉM výstupu je slovo „nezměněno"
    # v próze („řetězce jako ‚schváleno a nezměněno'"), takže kontrola „obsahuje
    # ZASTARAL/NEZMĚNĚN" projde i nad zelenou — falešně pozitivní.
    # ⚠ JMÉNO NESMÍ ODPOVÍDAT VZORU SOND (`p27-fixtura-*`, ne `p27-sonda-*`):
    # sonda patří do `PRESKOCIT` dávky a je to TRVALÝ soubor, kdežto tohle je
    # jednorázová fixtura, která po měření zmizí.
    sonda = ANALYZA / "p27-fixtura-otisk.txt"
    sonda.write_bytes(b"# P27: sonda pro A7 (nemeni kod, jen otisk vstupu)\n")
    try:
        kod, v = cmd(["python", str(RIZIKA)], timeout=900)
        check("A7 nový soubor ve stromě SHODÍ bránu (inventář se nečte tiše)",
              kod != 0, True)
        check("A7 a je to POJMENOVANÝ STAV „INVENTÁŘ JE ZASTARALÝ“",
              "INVENTÁŘ JE ZASTARALÝ" in v, True)
        sha2 = pregeneruj()
        check("A7 a přegenerovaný otisk se ZMĚNIL (nový soubor je v něm)",
              sha2 != sha0, True)
        kod, v = cmd(["python", str(RIZIKA)], timeout=900)
        check("A7 NEGATIVNÍ KONTROLA: nad ČERSTVÝM inventářem brána projde",
              kod, 0)
        check("A7 a hlášení „INVENTÁŘ JE ZASTARALÝ“ tam NENÍ (predikát není slepý)",
              "INVENTÁŘ JE ZASTARALÝ" in v, False)
    finally:
        sonda.unlink(missing_ok=True)
    # (3) návrat: přegenerovat a brána musí být zase zelená
    sha3 = pregeneruj()
    check("A7 po úklidu se otisk vrátil na původní hodnotu", sha3, sha0)
    kod, v = cmd(["python", str(RIZIKA)], timeout=900)
    check("A7 a brána je zase zelená (exit 0)", kod, 0)


# ══════════════════════════════════════════════════════════════════ main ═══
def main() -> int:
    global HANDOFF, TEST_TIK, OV_G, G3, VYSTUP_CESTA
    ap = argparse.ArgumentParser()
    ap.add_argument("--jen", default=None, help="seznam etap (např. A2,A5)")
    ap.add_argument("--plne", action="store_true",
                    help="VŠE: A1–A7 včetně mutací živého zdroje a g3/validate-all")
    # Přepínače cest existují kvůli mutačnímu důkazu (`p27-b-mutace.py`).
    ap.add_argument("--handoff", default=None, help="cesta k HANDOFF.md")
    ap.add_argument("--test", default=None, help="cesta k testu tiku")
    ap.add_argument("--ovg", default=None, help="cesta k ov-g-neovereno.py")
    ap.add_argument("--g3", default=None, help="cesta k g3-brany.py")
    ap.add_argument("--vystup", default=None, help="cesta k uloženému výstupu")
    args = ap.parse_args()
    VYSTUP_CESTA = pathlib.Path(args.vystup).resolve() if args.vystup else None
    for jmeno, hodnota in (("HANDOFF", args.handoff), ("TEST_TIK", args.test),
                           ("OV_G", args.ovg), ("G3", args.g3)):
        if hodnota:
            globals()[jmeno] = pathlib.Path(hodnota).resolve()

    etapy = {x.strip().upper() for x in
             (args.jen if args.jen else
              ("A1,A2,A3,A4,A5,A6,A7" if args.plne else "A1,A4,A5,A6,A7")).split(",")
             if x.strip()}

    print("=" * 78)
    print("P27/A — PŘEMĚŘENÍ PRÁCE P26 VLASTNÍM POSTUPEM (A1–A7)")
    print("=" * 78)
    if not args.plne and not args.jen:
        print("⚠ REŽIM DÁVKY: A1 (kontramutace v kopiích), A4 (levné čítače + živá\n"
              "  služba), A5, A6 (levné), A7 — bez mutace živého zdroje a bez\n"
              "  `g3`/`validate-all`. Plná kontrola je `--plne`.\n")

    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    try:
        if "A1" in etapy:
            a1()
        if "A2" in etapy:
            a2()
        if "A3" in etapy:
            a3()
        if "A4" in etapy:
            a4(args.plne)
        if "A5" in etapy:
            a5()
        if "A6" in etapy:
            a6(args.plne)
        if "A7" in etapy:
            a7()
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)
        if KOPIE_TESTU.exists():
            KOPIE_TESTU.unlink()
        if DOBOVA_KOPIE.exists():
            DOBOVA_KOPIE.unlink()
        for p in ANALYZA.glob("_p27-*.py"):
            p.unlink(missing_ok=True)

    print("\n" + "=" * 78)
    print("NEZMĚŘENO (není nula a není zelená): %d" % len(nezmereno))
    for p in nezmereno:
        print("   · %s" % p)
    print("=" * 78)
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    return 1 if chyb else 0


if __name__ == "__main__":
    _orig = sys.stdout

    class _Tee:
        def __init__(self, cil):
            self.cil = cil
            self.buffer = []

        def write(self, s):
            self.cil.write(s)
            self.buffer.append(s)
            return len(s)

        def flush(self):
            self.cil.flush()

        def reconfigure(self, **kw):
            pass

    _tee = _Tee(_orig)
    sys.stdout = _tee
    try:
        _kod = main()
    finally:
        sys.stdout = _orig
        vystup = VYSTUP_CESTA or (ANALYZA / "p27-a-overeni-vystup.txt")
        vystup.write_bytes("".join(_tee.buffer).encode("utf-8"))
        print("plný výstup: %s (%d bajtů, UTF-8)"
              % (vystup.name, vystup.stat().st_size))
    sys.exit(_kod)
