# -*- coding: utf-8 -*-
"""P16 (OVĚŘOVACÍ session) — VLASTNÍ měřidlo k tvrzení A z §33: vada H70.

NENÍ to test P15 (`_analyza/test-h70-vetev.py`). Postup je jiný ve čtyřech
věcech:

  1. fixtura má JINÉ jméno neznámého repa (`zanikle-repo`, ne `neznamy-repo`)
     i jiný tvar hlavičky,
  2. mutant se vyrábí v KOPII (`p16a1-mutant.py`), takže živý
     `_analyza/zadani-kontrola.py` se **ani nedotkne** (P15 ho mutoval a vracel),
  3. „byly DVA výskyty" (H80) se neměří P15 testem, ale **blobem z gitu PŘED
     P15** (`ce49234~1` = `c620a06`) — přímým počtem výskytů v textu,
  4. plošný sken je **Python walk nad oběma repy** (ne `grep` — `dsh-prostredi`
     §1) a má **pozitivní kontrolu** (syntetický soubor s vadou).

⚠ PAST PROSTŘEDÍ, na kterou se tady narazilo a která se týká každého, kdo měří
„stav před P15": `git.cmd` je BATCE a jde přes `cmd.exe`, který **žere `^`**.
`git show ce49234^:soubor` proto tiše vrátí **stav PO P15** (a rozdíl „0 změn"
je pak pravdivý omylem). Správně `ce49234~1`, nebo `git.exe` přímo.
Doklad: `git.cmd rev-parse --short ce49234^` -> `ce49234`, `git.exe` -> `c620a06`.

Nic nemění (kromě vlastních `p16a1-*`), nic neopravuje.
"""

import ast
import io
import pathlib
import subprocess
import sys
import tokenize

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
HRA = WS.parent / "uo-shadows"
ANALYZA = WS / "_analyza"
GIT = str(WS / "tools" / "git.cmd")
ZA = ANALYZA / "zadani-kontrola.py"          # živá brána (NEMUTUJE SE)
MUTANT = ANALYZA / "p16a1-mutant.py"         # kopie s vrácenou vadou
FIX_VADNA = ANALYZA / "p16a1-fixtura-neznama.md"
FIX_OK = ANALYZA / "p16a1-fixtura-ok.md"
PRE_P15 = "ce49234~1"                        # NIKDY `ce49234^` (viz docstring)

kontrol = 0
chyb = 0


def zk(ok: bool, popis: str, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if ok:
        print(f"  OK   {popis}" + (f"  [{detail}]" if detail else ""))
    else:
        chyb += 1
        print(f"  CHYBA {popis}" + (f"  [{detail}]" if detail else ""))


def git(*args, exe=None):
    prikaz = [exe or GIT, *args]
    r = subprocess.run(prikaz, capture_output=True, shell=(exe is None))
    return (r.returncode,
            (r.stdout or b"").decode("utf-8", "replace"),
            (r.stderr or b"").decode("utf-8", "replace"))


def spust_zadani(soubor: pathlib.Path, skript: pathlib.Path):
    r = subprocess.run([sys.executable, str(skript), "--soubor", str(soubor)],
                       capture_output=True, cwd=str(WS))
    return (r.returncode,
            (r.stdout or b"").decode("utf-8", "replace")
            + (r.stderr or b"").decode("utf-8", "replace"))


print("=" * 78)
print("P16/A1 — VLASTNÍ měřidlo k H70 (živá brána se NEMUTUJE, mutuje se KOPIE)")
print("=" * 78)

# ── 0) Živé HEADy (fixtura proti nim nesmí být zastaralá) ───────────────────
_, head_o, _ = git("-C", str(WS), "rev-parse", "HEAD")
_, head_h, _ = git("-C", str(HRA), "rev-parse", "HEAD")
head_o, head_h = head_o.strip(), head_h.strip()
print(f"  živé HEADy: {WS.name}={head_o[:9]}  {HRA.name}={head_h[:9]}")

# ── 1) FIXTURY ─────────────────────────────────────────────────────────────
# Formát hlavičky je daný `zadani-kontrola.py`: hledá se řádek „Stav obou repů"
# v PRVNÍCH 30 řádcích a z něj dvojice `jmeno = sha`.
hlavicka = (
    "# FIXTURA P16 (vlastní měřidlo) — cvičné zadání pro `zadani-kontrola.py`\n"
    "\n"
    f"**Stav obou repů při psaní:** `forge-orchestra` = `{head_o}` · "
    f"`uo-shadows` = `{head_h}`\n"
    "\n"
    "Tohle je fixtura. Nic se podle ní neprovádí.\n"
)

text_vadna = hlavicka.replace(
    "`uo-shadows` = `%s`" % head_h,
    "`uo-shadows` = `%s` · `zanikle-repo` = `deadbeef`" % head_h)
text_ok = hlavicka

FIX_VADNA.write_text(text_vadna, encoding="utf-8", newline="")
FIX_OK.write_text(text_ok, encoding="utf-8", newline="")

vadna_radky = [l for l in text_vadna.splitlines() if "Stav obou repů" in l]
zk(len(vadna_radky) == 1 and "zanikle-repo" in vadna_radky[0],
   "fixtura má tvar, který brána PARSOVALA (řádek se stavem repů + neznámé jméno)",
   vadna_radky[0][:110] if vadna_radky else "—")

# ── 2) ŽIVÁ BRÁNA na vadné fixtuře ─────────────────────────────────────────
print("\n--- 1) ŽIVÁ brána na fixtuře s NEZNÁMÝM jménem repa -----------------")
kod, vystup = spust_zadani(FIX_VADNA, ZA)
print(f"  exit={kod}")
zk(kod == 1, "brána skončila `exit 1` (ne 2 a ne pád)", f"exit={kod}")
zk("nepodařilo přiřadit" in vystup,
   "brána VYPÁSALA vlastní hlášení „nepodařilo přiřadit k repu")
zk("zanikle-repo" in vystup, "hlášení pojmenovává to neznámé jméno")
zk("ValueError" not in vystup and "Traceback" not in vystup,
   "výstup NEOBSAHUJE ValueError ani Traceback (to je jádro H70)")
zk("známá jména repů" in vystup,
   "hlášení vypisuje známá jména repů (to dělá opravená větev na ř. 215)")

# ── 3) KONTROLNÍ fixtura (bez neznámého repa) ──────────────────────────────
print("\n--- 2) KONTROLNÍ fixtura (jen známé repy) ---------------------------")
kod_ok, vystup_ok = spust_zadani(FIX_OK, ZA)
print(f"  exit={kod_ok}")
zk(kod_ok == 0, "zdravá fixtura projde (`exit 0`)", f"exit={kod_ok}")
zk("nepodařilo přiřadit" not in vystup_ok,
   "větev s vadou se na zdravé fixtuře VŮBEC NEZAVOLÁ "
   "(proto ji nikdo neviděl — a proto ji test musí ZAVOLAT)")

# ── 4) MUTANT v KOPII (živý soubor zůstává) ────────────────────────────────
print("\n--- 3) MUTACE: vada se vrací do KOPIE, ne do živého souboru ---------")
zdroj_zyvy = ZA.read_bytes()
TEXT_ZYVY = zdroj_zyvy.decode("utf-8")


def smycky_nad(text: str, jmeno: str = "zivy"):
    """(řádky s JEDNOPRVKOVÝM cílem, řádky s DVOUPRVKOVÝM cílem) — z AST.

    ⚠ Dvě věci, které první verze tohohle měřidla minula (a obě vypadaly jako
    „vada zmizela"):
      1. **KOMENTÁŘE**: `for j, _ in zivy` stojí i v komentářích, které vadu
         popisují (past `overovani` §3). Měří se proto **AST**, ne text.
      2. **GENERÁTOROVÉ VÝRAZY**: obě opravená místa jsou uvnitř
         `any(... for j in zivy)` a `join(j for j in zivy)` — tedy
         `ast.GeneratorExp`, NE `ast.For`. Kdo hledá jen `ast.For`, najde **0**
         i s vrácenou vadou. (`overovani` §7.14: mutace musí změnit měřenou
         PODMÍNKU — a měřená podmínka musí být ta správná.)
    """
    jedn, dvoj = [], []
    uzly = []
    for n in ast.walk(ast.parse(text, filename="<smycky_nad>")):
        if isinstance(n, ast.For):
            uzly.append((n.target, n.iter, n.lineno))
        elif isinstance(n, (ast.GeneratorExp, ast.ListComp, ast.SetComp, ast.DictComp)):
            for g in n.generators:
                uzly.append((g.target, g.iter, n.lineno))
    for cil, it, rad in uzly:
        if isinstance(it, ast.Name) and it.id == jmeno:
            (dvoj if isinstance(cil, ast.Tuple) else jedn).append(rad)
    return sorted(jedn), sorted(dvoj)


jed_a, dvoj_a = smycky_nad(TEXT_ZYVY)
zk(len(jed_a) == 2 and len(dvoj_a) == 0,
   "V KÓDU živé brány jsou 2 smyčky `for j in zivy` a 0 dvouprvkových (H70 opraven)",
   f"jednoprvkove={jed_a} dvouprvkove={dvoj_a}")
zmut = TEXT_ZYVY.replace("for j in zivy", "for j, _ in zivy")
zk(zmut != TEXT_ZYVY, "MUTACE SE SKUTEČNĚ PROVEDLA (text se liší)")
jed_m, dvoj_m = smycky_nad(zmut)
zk(len(dvoj_m) == 2 and len(jed_m) == 0,
   "po mutaci jsou v KÓDU 2 DVOUPRVKOVÉ smyčky nad slovníkem (vada je zpět)",
   f"jednoprvkove={jed_m} dvouprvkove={dvoj_m}")
MUTANT.write_text(zmut, encoding="utf-8", newline="")
zk(MUTANT.read_bytes() != zdroj_zyvy, "mutant na disku se liší od živého souboru")

kod_m, vystup_m = spust_zadani(FIX_VADNA, MUTANT)
print(f"  exit={kod_m}")
zk("ValueError" in vystup_m or "Traceback" in vystup_m,
   "s vrácenou vadou brána SPADNE (ValueError/Traceback) — měření umí selhat")
zk("nepodařilo přiřadit" not in vystup_m,
   "s vrácenou vadou se hlášení „nepodařilo přiřadit VŮBEC NEVYPÍŠE")

kod_mo, _ = spust_zadani(FIX_OK, MUTANT)
zk(kod_mo == 0,
   "kontrolní fixtura zůstává `exit 0` i s vadou (vada je v záchranné větvi)",
   f"exit={kod_mo}")

zk(ZA.read_bytes() == zdroj_zyvy, "ŽIVÝ `zadani-kontrola.py` je bajt na bajt netknutý")

# ── 5) H80: „byly DVA výskyty" — dá se to z gitu vůbec doložit? ───────────
print("\n--- 4) H80: kolik výskytů bylo PŘED P15 (blob z gitu, ne P15 test) --")
kod_g, blob_pre, err_g = git("-C", str(WS), "show", f"{PRE_P15}:_analyza/zadani-kontrola.py")
zk(kod_g == 0, f"blob {PRE_P15}:_analyza/zadani-kontrola.py se podařilo přečíst",
   err_g.strip()[:80])
kod_p, blob_po, _ = git("-C", str(WS), "show", "ce49234:_analyza/zadani-kontrola.py")
zk(kod_p == 0, "blob `ce49234:_analyza/zadani-kontrola.py` se podařilo přečíst")

jed_pre, dvoj_pre = smycky_nad(blob_pre)
_, dvoj_po = smycky_nad(blob_po)
print(f"  {PRE_P15}: {len(blob_pre.splitlines())} řádků, "
      f"dvouprvkových smyček nad `zivy` v KÓDU: {len(dvoj_pre)}")
print(f"  ce49234: {len(blob_po.splitlines())} řádků, "
      f"dvouprvkových smyček nad `zivy` v KÓDU: {len(dvoj_po)}")
zk("nepodařilo přiřadit" not in blob_pre,
   f"PŘEDPOKLAD ZADÁNÍ JE NESPLNĚN: `{PRE_P15}` (={PRE_P15} znamená c620a06) "
   "NENÍ stav před P15 — větev H70 v něm vůbec není (je to stav před P13c)")
zk(len(dvoj_pre) == 0,
   "…proto H80 (dva výskyty) NELZE z gitu doložit: v žádném commitu není",
   f"dvoj={len(dvoj_pre)}")
zk(len(dvoj_po) == 0 and len(smycky_nad(blob_po)[0]) == 2,
   "v tom, co je v gitu DNES (ce49234), je v KÓDU 0 dvouprvkových a 2 jednoprvkové",
   f"dvoj={len(dvoj_po)}")

disk_text = ZA.read_bytes().decode("utf-8")
jed_d, dvoj_d = smycky_nad(disk_text)
zk(dvoj_d == [], "na DISKU (živý soubor) není v KÓDU ani jedna dvouprvková smyčka")
h80 = ("H80 (DVA výskyty) je doložitelné JEN artefakty P15 — v gitu není stav "
       "před P15; nezávisle je doloženo jen to, že DNES je jich 0")
print(f"  ⚠ MEZ MĚŘENÍ: {h80}")

# ── 6) PLOŠNÝ SKEN obou repů (Python walk, ne grep) ───────────────────────
print("\n--- 5) PLOŠNÝ SKEN: `for X, Y in SLOVNIK` nad OBĚMA repy -----------")


def kandidati(text: str, jmeno_souboru: str = "<kandidati>"):
    """For-smyčky s DVOUPRVKOVÝM cílem nad jménem (ne nad `.items()`)."""
    try:
        strom = ast.parse(text, filename=jmeno_souboru)
    except SyntaxError:
        return None
    slovniky = set()
    for n in ast.walk(strom):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Dict):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    slovniky.add(t.id)
        if isinstance(n, ast.AnnAssign) and isinstance(n.annotation, ast.Name) \
                and n.annotation.id in ("dict", "Dict") and isinstance(n.target, ast.Name):
            slovniky.add(n.target.id)
    nalez = []
    uzly = []
    for n in ast.walk(strom):
        if isinstance(n, ast.For):
            uzly.append((n.target, n.iter, n.lineno))
        elif isinstance(n, (ast.GeneratorExp, ast.ListComp, ast.SetComp, ast.DictComp)):
            for g in n.generators:
                uzly.append((g.target, g.iter, n.lineno))
    for cil, it, rad in uzly:
        if not (isinstance(cil, ast.Tuple) and len(cil.elts) >= 2):
            continue
        if isinstance(it, (ast.Call, ast.Attribute)):
            continue                      # `zip(...)`, `.items()` je správně
        if isinstance(it, ast.Name):
            nalez.append((rad, it.id, it.id in slovniky))
    return nalez


sken = {"souboru": 0, "bez_parsovani": 0, "kandidatu": 0, "nad_slovnikem": [],
        "presne": [], "vlastni": []}


def rozdel_vyskyty(text: str, vzor: str):
    """(výskytů v KOMENTÁŘÍCH a ŘETĚZCÍCH, výskytů v KÓDU) — přes `tokenize`."""
    v_txt = text.count(vzor)
    v_kom = 0
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type in (tokenize.COMMENT, tokenize.STRING):
                v_kom += tok.string.count(vzor)
    except (tokenize.TokenError, IndentationError):
        return None
    return v_kom, v_txt - v_kom


for koren in (WS, HRA):
    for p in sorted(koren.rglob("*.py")):
        if ".git" in set(p.parts):
            continue
        # ⚠ VLASTNÍ ARTEFAKTY SE VYLUČUJÍ: `p16*` soubory obsahují vzor
        # ZÁMĚRNĚ (popis vady, mutant, syntetická fixtura). Kdyby se počítaly,
        # měřidlo by „našlo vadu", kterou samo vyrobilo — a to je falešný nález
        # na správném kódu (`overovani` §9.5). Vyloučení se VYPISUJE.
        if p.name.startswith("p16"):
            sken["vlastni"].append(str(p.relative_to(koren)))
            continue
        sken["souboru"] += 1
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "for j, _ in zivy" in t:
            r = rozdel_vyskyty(t, "for j, _ in zivy")
            sken["presne"].append((str(p.relative_to(koren)), r))
        k = kandidati(t, str(p))
        if k is None:
            sken["bez_parsovani"] += 1
            continue
        for rad, jmeno, je_dict in k:
            sken["kandidatu"] += 1
            if je_dict:
                sken["nad_slovnikem"].append(f"{p.relative_to(koren)}:{rad} ({jmeno})")

print(f"  proskenováno .py souborů: {sken['souboru']} "
      f"(neparsovatelných: {sken['bez_parsovani']}); "
      f"vyloučeno vlastních `p16*`: {len(sken['vlastni'])} "
      f"({[c.split(chr(92))[-1] for c in sken['vlastni']]})")
print(f"  for-smyček s dvouprvkovým cílem nad JMÉNEM: {sken['kandidatu']}")
print(f"  z toho nad jménem, které je v TÉMŽ souboru slovník: "
      f"{len(sken['nad_slovnikem'])}")
for x in sken["nad_slovnikem"]:
    print(f"      {x}")
print(f"  přesný vzor `for j, _ in zivy` — soubory, které ho mají v TEXTU:")
kod_hit = 0
for cesta, r in sken["presne"]:
    if r is None:
        print(f"      {cesta}: (nepodařilo se tokenizovat)")
        continue
    v_kom, v_kod = r
    kod_hit += v_kod
    print(f"      {cesta}: v komentářích/řetězcích {v_kom}, V KÓDU {v_kod}")
zk(sken["souboru"] > 100, "sken SKUTEČNĚ proběhl (prošel stovky souborů)",
   f"{sken['souboru']} souborů")
zk(kod_hit == 0,
   "H80 rozšířený: v KÓDU obou repů není ANI JEDEN `for j, _ in zivy`",
   f"v kódu={kod_hit}")
zk(len(sken["nad_slovnikem"]) == 2,
   "…a zbylí 2 KANDIDÁTI jsou NEŠKODNÍ: `OCEKAVANE = {}` má za klíče 2-tuple "
   "`(soubor, text)`, takže rozbalení `for (s, t) in OCEKAVANE` funguje "
   "(ověšeno čtením definice na ř. 69/74 obou kopií) — NENÍ to vada",
   f"{len(sken['nad_slovnikem'])}")

SYNT = ANALYZA / "p16a1-synteticka-vada.py"
SYNT.write_text("zivy = {'a': 1}\nfor j, _ in zivy:\n    pass\n", encoding="utf-8")
zk("for j, _ in zivy" in SYNT.read_text(encoding="utf-8"),
   "pozitivní kontrola: syntetický soubor vadu OBSAHUJE")
k_synt = kandidati(SYNT.read_text(encoding="utf-8"))
zk(bool(k_synt) and k_synt[0][2] is True,
   "AST sken ji NAD SLOVNÍKEM najde (sken umí zabrat)", str(k_synt))

print("\n" + "=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
print("=" * 78)
sys.exit(1 if chyb else 0)
