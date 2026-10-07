# -*- coding: utf-8 -*-
r"""P25 — ÚKOL A, DRUHÁ POLOVINA: MŮŽE VLASTNÍ MĚŘIDLO VŮBEC SPADNOUT?

PROČ TENHLE DOKLAD EXISTUJE
---------------------------
Zadání P25 §2.1 žádá, aby doklad **uměl selhat** — bez toho by
`p25-a-overeni.py` mohl být jen dalším „zeleným nad ničím" (`overovani`
§7.13). P24 to řešila mutačním testem svého měřidla; **to se musí udělat
i pro měřidlo P25** — jinak by platilo, že „kdo ověřuje ověřovatele, sám
ověřen není".

⚠ MUTUJE SE **V KOPIÍCH**, ne v živém stromě. Je to přímý důsledek nálezu
P24-A: přerušený mutační běh nechal v živém `conductor/src/index.ts` **čtyři
mutanty**. Živé soubory (KRONIKA, conductor, g3, validate-all, p20-d) se
proto jen **kopírují** a měřidlo dostane cestu kopie (`--zdroj`, `--kronika`,
`--g3`, `--validate`, `--p20d`).

CO SE DOKAZUJE
--------------
  0  KONTROLA: na ŽIVÉM (nezmutovaném) stavu měřidlo projde — jinak by
     „spadlo po mutaci" mohlo znamenat jen to, že je rozbité pořád
  1  A2: v kopii zdroje se `SET eskalovano = datetime('now')` změní na
     `SET eskalovano = NULL` → měřidlo MUSÍ ohlásit, že se značka maže
  2  A5: v kopii kroniky se řádek session `**39**` přejmenuje → MUSÍ spadnout
  3  A6: do kopie `g3` se vloží SONDa do `BRANY` → MUSÍ spadnout
  4  A6: v kopii `p20-d` se ze `PRESKOCIT` ubere sonda → MUSÍ spadnout
  5  A6: v kopii `validate-all` se `spust()` obrátí na sondu → MUSÍ spadnout
  6  A3: rozhodovací funkce `a3_verdikt` se ZAVOLÁ nad syntetickým výstupem
     (oběma směry) — zarážka, která nezapne kontroly, musí být nález
  7  A1: DIFFERENCIÁL — na TÉŽE vadě (ubraný `| **B4** |`) originální měřidlo
     P24 spadne, ale jeho oslabená kopie (bez kontroly B4) projde

Použití: python _analyza/p25-b-mutace.py
"""

import hashlib
import importlib.util
import pathlib
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj                                            # noqa: E402

MERIDLO = ANALYZA / "p25-a-overeni.py"
SCRATCH = ANALYZA / "p25-b-scratch"

kontrol = 0
chyb = 0


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


def spust(*argumenty, timeout=1800):
    r = subprocess.run([sys.executable, "-B", str(MERIDLO)] + list(argumenty),
                       cwd=str(WS), capture_output=True, timeout=timeout)
    return r.returncode, (r.stdout.decode("utf-8", "replace")
                          + r.stderr.decode("utf-8", "replace"))


def citac(vystup):
    import re
    posledni = None
    for posledni in re.finditer(r"(\d+) kontrol, (\d+) chyb", vystup,
                                re.IGNORECASE):
        pass
    return (int(posledni.group(1)), int(posledni.group(2))) if posledni else None


def hash_souboru(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def nacti_meridlo():
    """Načte měřidlo jako MODUL (main je pod `if __name__`, takže neběží)."""
    spec = importlib.util.spec_from_file_location("p25a_modul", MERIDLO)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    print("=" * 78)
    print("P25/B — MUTAČNÍ TEST MĚŘIDLA p25-a-overeni.py (mutace V KOPIÍCH)")
    print("=" * 78)

    if not MERIDLO.is_file():
        print("CHYBA: chybí %s" % MERIDLO)
        return 1
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)

    # ── 0) KONTROLA ─────────────────────────────────────────────────────────
    kod, v = spust("--jen", "A2,A5,A6")
    c = citac(v)
    check("0 KONTROLA: živý stav → měřidlo projde (exit 0)", kod, 0)
    check("0 KONTROLA: vykázalo čítač", c is not None, True)
    check("0 KONTROLA: měřilo se něco (aspoň 10 kontrol)",
          (c[0] >= 10) if c else False, True)

    # ── 1) A2: značka se v kopii zdroje ZAČNE MAZAT ─────────────────────────
    kopie_src = SCRATCH / "index-zmaz.py"
    shutil.copyfile(WS / "conductor" / "src" / "index.ts", kopie_src)
    kotva1 = "UPDATE roadmap SET eskalovano = datetime('now') WHERE item_id = ?"
    vada1 = "UPDATE roadmap SET eskalovano = NULL WHERE item_id = ?"
    try:
        with mutuj(kopie_src, kotva1, vada1) as m:
            kod, v = spust("--zdroj", str(kopie_src), "--jen", "A2")
        check("1 změna souboru opravdu proběhla (hash před != po)",
              m.hash_pred != m.hash_po_mutaci, True)
        check("1 po vložení MAZACÍHO UPDATE měřidlo SPADLO", kod != 0, True)
        check("1 a důvod je NÁLEZ o mazání značky",
              "MAŽE" in v or "MAZE" in v, True)
    except ValueError as e:
        check("1 mutace se provedla (%s)" % e, False, True)

    # ── 2) A5: řádek session v kopii kroniky se přejmenuje ──────────────────
    kopie_kr = SCRATCH / "kronika.py.md"
    shutil.copyfile(WS / "KRONIKA-PROJEKTU.md", kopie_kr)
    try:
        with mutuj(kopie_kr, "| **39** |", "| **39x** |") as m:
            kod, v = spust("--kronika", str(kopie_kr), "--jen", "A5")
        check("2 změna kroniky opravdu proběhla",
              m.hash_pred != m.hash_po_mutaci, True)
        check("2 po přejmenování řádku session 39 měřidlo SPADLO", kod != 0, True)
    except ValueError as e:
        check("2 mutace se provedla (%s)" % e, False, True)

    # ── 3) A6: do kopie g3 se vloží SONDa do BRANY ──────────────────────────
    kopie_g3 = SCRATCH / "g3-sonda.py"
    shutil.copyfile(ANALYZA / "g3-brany.py", kopie_g3)
    mod = nacti_meridlo()
    import ast
    prvni = None
    try:
        strom = ast.parse(ANALYZA.joinpath("g3-brany.py").read_text(encoding="utf-8"))
        for node in ast.walk(strom):
            if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "BRANY" for t in node.targets):
                prvni = node.value.elts[0].elts[0].value
    except (AttributeError, IndexError, SyntaxError):
        prvni = None
    check("3 z g3 jde přečíst první bránu (pro kotvu mutace)",
          isinstance(prvni, str) and bool(prvni), True)
    if prvni:
        kotva3 = '("%s", [' % prvni
        vada3 = ('("p25-sonda-fiktivni.py", ["python", "sonda.py"], r"(\\d+)"),\n'
                 '    ("pryc-%s", [' % prvni[:10])
        try:
            with mutuj(kopie_g3, kotva3, vada3) as m:
                kod, v = spust("--g3", str(kopie_g3), "--jen", "A6")
            check("3 změna g3 opravdu proběhla",
                  m.hash_pred != m.hash_po_mutaci, True)
            check("3 po vložení SONDy do BRANY měřidlo SPADLO", kod != 0, True)
            check("3 a důvod je NÁLEZ o sondě v BRANY",
                  "SONDa" in v or "SONDA" in v, True)
        except ValueError as e:
            check("3 mutace se provedla (%s)" % e, False, True)

    # ── 4) A6: v kopii p20-d se ze PRESKOCIT ubere sonda ────────────────────
    kopie_p20 = SCRATCH / "p20-d-bez-sondy.py"
    shutil.copyfile(ANALYZA / "p20-d-doklady.py", kopie_p20)
    kotva4 = '"p24-sonda-site.py", "p24-sonda-m2.py"'
    vada4 = '"p24-sonda-site.py"'
    try:
        with mutuj(kopie_p20, kotva4, vada4) as m:
            kod, v = spust("--p20d", str(kopie_p20), "--jen", "A6")
        check("4 změna p20-d opravdu proběhla",
              m.hash_pred != m.hash_po_mutaci, True)
        check("4 po ubrání sondy z PRESKOCIT měřidlo SPADLO", kod != 0, True)
        check("4 a důvod je NÁLEZ o PRESKOCIT",
              "PRESKOCIT" in v, True)
    except ValueError as e:
        check("4 mutace se provedla (%s)" % e, False, True)

    # ── 5) A6: v kopii validate-all se spust() obrátí na sondu ──────────────
    kopie_val = SCRATCH / "validate-all-sonda.mjs"
    shutil.copyfile(WS / "tools" / "validate-all.mjs", kopie_val)
    kotva5 = "const licenceTest = spust('python', [`${ORCH}/tools/test-licence.py`]);"
    vada5 = "const licenceTest = spust('python', [`${ORCH}/_analyza/p24-sonda-site.py`]);"
    try:
        with mutuj(kopie_val, kotva5, vada5) as m:
            kod, v = spust("--validate", str(kopie_val), "--jen", "A6")
        check("5 změna validate-all opravdu proběhla",
              m.hash_pred != m.hash_po_mutaci, True)
        check("5 po vložení sondy do spust() měřidlo SPADLO", kod != 0, True)
        check("5 a důvod je NÁLEZ o sondě v validate-all",
              "validate-all je sonda" in v, True)
    except ValueError as e:
        check("5 mutace se provedla (%s)" % e, False, True)

    # ── 6) A3: rozhodovací funkce nad SYNTETICKÝM výstupem (oběma směry) ────
    mod = nacti_meridlo()
    ocek = ["N: /poll odpoví 200", "O: /claim odpoví 200"]
    kontrolni = ["A: /tick odpoví 200"]
    ch1, kr1 = mod.a3_verdikt([], ocek, kontrolni)
    check("6 A3: KDYŽ zarážka nezapne nic, verdikt je NÁLEZ (obě chybějící)",
          (ch1, kr1), (ocek, []))
    ch2, kr2 = mod.a3_verdikt(ocek + kontrolni, ocek, kontrolni)
    check("6 A3: KDYŽ padne i kontrolní kontrola, verdikt to ŘEKNE",
          (ch2, kr2), ([], kontrolni))
    ch3, kr3 = mod.a3_verdikt(ocek, ocek, kontrolni)
    check("6 A3: KDYŽ padnou právě očekávané a nic jiného, verdikt je OK",
          (ch3, kr3), ([], []))

    # ── 7) A1: DIFFERENCIÁL (originál spadne, oslabená kopie projde) ────────
    kopie_planu = SCRATCH / "plan-rozvoj-bez-B4.md"
    shutil.copyfile(WS / "PLAN-ROZVOJ-ORCHESTRA.md", kopie_planu)
    kopie_planu2 = SCRATCH / "plan-agenti.md"
    shutil.copyfile(WS / "PLAN-ORCHESTRA-AI-AGENTI.md", kopie_planu2)
    agr = ["--jen-dokumenty", "--plan-rozvoj", str(kopie_planu),
           "--plan-agenti", str(kopie_planu2)]
    try:
        with mutuj(kopie_planu, "| **B4** |", "") as m:
            kod_orig, v_orig = None, ""
            r = subprocess.run([sys.executable, "-B",
                                str(ANALYZA / "p24-a-overeni.py")] + agr,
                               cwd=str(WS), capture_output=True, timeout=900)
            kod_orig = r.returncode
            v_orig = r.stdout.decode("utf-8", "replace")
        check("7 změna plánu opravdu proběhla",
              m.hash_pred != m.hash_po_mutaci, True)
        check("7 ORIGINÁL p24-a-overeni.py na té vadě SPADNE", kod_orig != 0, True)
        # Oslabená kopie: kontrola B4 je z ní VYBRANÁ (nic jiného se nemění).
        text = (ANALYZA / "p24-a-overeni.py").read_text(encoding="utf-8")
        text = text.replace('        for b in ("B1", "B2", "B3", "B4", "B5"):',
                            '        for b in ("B1", "B2", "B3", "B5"):', 1)
        text = text.replace('WS = pathlib.Path(__file__).resolve().parents[1]',
                            'WS = pathlib.Path(r"%s")' % WS, 1)
        oslabene = SCRATCH / "p24-a-bez-B4.py"
        oslabene.write_text(text, encoding="utf-8", newline="")
        r2 = subprocess.run([sys.executable, "-B", str(oslabene)] + agr,
                            cwd=str(WS), capture_output=True, timeout=900)
        kod_osl = r2.returncode
        check("7 a OSLABENÁ kopie (bez kontroly B4) na TÉŽE vadě PROJDE",
              kod_osl, 0)
        check("7 tedy kontrola B4 je to, co vadu chytá (ne něco jiného)",
              (kod_orig != 0 and kod_osl == 0), True)
    except ValueError as e:
        check("7 mutace se provedla (%s)" % e, False, True)

    # ── 8) úklid: živé soubory nesmí nést mutaci ────────────────────────────
    # Autorita je `git diff` (ne hledání markeru v textu — ten by trefil
    # i komentář, který mutaci popisuje; `overovani` §1).
    zive = []
    for cesta in ("conductor/src/index.ts", "KRONIKA-PROJEKTU.md",
                  "_analyza/g3-brany.py", "_analyza/p20-d-doklady.py",
                  "tools/validate-all.mjs"):
        # `tools/git.cmd` (OpenSSL backend) — na téhle stanici je git z PATH
        # náchylný na schannel; lokální `diff` sice projde, ale ať je cesta JEDNA.
        r = subprocess.run([str(WS / "tools" / "git.cmd"), "-C", str(WS),
                            "diff", "--quiet", "--", cesta],
                           capture_output=True, shell=True)
        if r.returncode != 0:
            zive.append(cesta)
    check("8 živé soubory zůstaly BEZ mutací (git diff je čistý)", zive, [])
    shutil.rmtree(SCRATCH, ignore_errors=True)
    check("8 scratch uklizen", SCRATCH.exists(), False)

    print()
    if chyb:
        print("VÝSLEDEK: %d kontrol, %d CHYB" % (kontrol, chyb))
        return 1
    print("VÝSLEDEK: %d kontrol, 0 chyb" % kontrol)
    return 0


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
        vystup = ANALYZA / "p25-b-mutace-vystup.txt"
        vystup.write_bytes("".join(_tee.buffer).encode("utf-8"))
        print("plný výstup: %s (%d bajtů, UTF-8)"
              % (vystup.name, vystup.stat().st_size))
    sys.exit(_kod)
