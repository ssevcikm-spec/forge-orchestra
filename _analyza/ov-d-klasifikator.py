# OVĚŘOVACÍ session (P18) — Úkol D: KLASIFIKÁTOR `g3` VLASTNÍMI FIXTURAMI.
#
# PROČ: P17 měla `_analyza/test-h87-klasifikator.py` (18/0) a `test-h71` (15/0).
# Autor není nezávislý reviewer, takže se klasifikátor zkouší ZNOVU — a VLASTNÍMI
# fixturami (P16 i P17 měly svoje).
#
# JAK: vezme se ŽIVÝ `_analyza/g3-brany.py` jako ZDROJ, v kopii se vymění JEN
# `BRANY` za moje fixtury a spustí se. Tím se testuje SKUTEČNÝ klasifikátor,
# ne jeho opis (opis by mohl být správný a živý kód vadný).
#
# ⚠ TŘETÍ PAST (H87): `_VLASTNI_HLASENI` (whitelist 12 markerů) už v živém `g3`
# být NESMÍ. Hledá se v KÓDU, ne v komentáři — komentář tu vadu POPISUJE
# (řádky 326–339), takže naivní hledání řetězce by ji „našlo" v komentáři.
# Proto se komentáře PŘED hledáním odstraní (P17 na tom spadla dvakrát, omyl 171).
import hashlib
import json
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ⚠ CESTA SE ODVOZUJE, NEZAPEKÁVÁ (generalizace, 7. 10. 2026).
# `_analyza` leží v repu orchestry; dřív tu byl literál `E:\Workspaces\…`.
REPO = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = REPO / "_analyza"
G3 = ANALYZA / "g3-brany.py"
FIX = ANALYZA / "a-ukol-scratch" / "ov-d-fixtury"   # gitignorováno (`*-scratch/`)
HARNESS = ANALYZA / "ov-d-harness.py"

kontrol = 0
chyb = 0


def kont(nazev, ok, detail=""):
    global kontrol, chyb
    kontrol += 1
    if not ok:
        chyb += 1
    print(f"{'OK  ' if ok else 'CHYBA'} {nazev}")
    if detail:
        print(f"      {detail}")


def bez_komentaru(text: str) -> str:
    """Odstraní komentáře a docstringy — kontrola musí číst KÓD, ne komentář."""
    try:
        import ast
        strom = ast.parse(text)
        for uzel in ast.walk(strom):
            if isinstance(uzel, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef, ast.Module)):
                d = uzel.body[0] if uzel.body else None
                if (isinstance(d, ast.Expr) and isinstance(d.value, ast.Constant)
                        and isinstance(d.value.value, str)):
                    d.value.value = ""
        return ast.unparse(strom)
    except SyntaxError:
        # Když se nedá parsovat, odstraň aspoň řádkové komentáře.
        return "\n".join(re.sub(r"#.*$", "", l) for l in text.splitlines())


print("=" * 78)
print("D — KLASIFIKÁTOR `g3` VLASTNÍMI FIXTURAMI (P18)")
print("=" * 78)

zdroj = G3.read_text(encoding="utf-8")
hash_pred = hashlib.sha256(G3.read_bytes()).hexdigest()

# ── 1) WHITELIST V KÓDU NENÍ ──────────────────────────────────────────────
print("\n--- 1) `_VLASTNI_HLASENI` v KÓDU živého g3 ---")
kod = bez_komentaru(zdroj)
v_kodu = kod.count("_VLASTNI_HLASENI")
v_textu = zdroj.count("_VLASTNI_HLASENI")
print(f"    výskytů v CELÉM textu (včetně komentářů): {v_textu}")
print(f"    výskytů v KÓDU (bez komentářů/docstringů): {v_kodu}")
kont("`_VLASTNI_HLASENI` NENÍ v KÓDU (H87 opraven)", v_kodu == 0,
    f"kód={v_kodu}, text včetně komentářů={v_textu}")
kont("kontrola má jak selhat — v textu SE objevuje (jinak by hledala nic)",
    v_textu > 0,
    "kdyby bylo i v_textu 0, hledal bych řetězec, který nikde není → falešná zelená")
# A ověř, že `bez_komentaru` skutečně něco odstranil (jinak je to průchod naprázdno).
kont("odstranění komentářů NĚCO odstranilo (není to průchod naprázdno)",
    len(kod) < len(zdroj), f"{len(zdroj)} → {len(kod)} znaků")
for podezrele in ("whitelist", "12 marker", "markerů"):
    pass  # jen poznámka: tahle slova v kódu být mohou, rozhoduje výše uvedené

# ── 2) VÝROBA FIXTUR (skutečné skripty, ne natvrdo zadané exity) ──────────
print("\n--- 2) VÝROBA VLASTNÍCH FIXTUR ---")
FIX.mkdir(parents=True, exist_ok=True)
# Fixtura A: exit=2, VLASTNÍ hlášení BEZ markeru (přesně případ H87).
(FIX / "ovd-a-bez-markeru.py").write_text(
    'print("P18: hotovo, vse na svem miste")\nraise SystemExit(2)\n',
    encoding="utf-8", newline="\n")
# Fixtura B: exit=2, hlášení S markerem, který vzor najde.
(FIX / "ovd-b-s-markerem.py").write_text(
    'print("VYSLEDEK: 7 kontrol, 0 chyb")\nraise SystemExit(2)\n',
    encoding="utf-8", newline="\n")
# Fixtura C: exit=2, BEZ výstupu.
(FIX / "ovd-c-bez-vystupu.py").write_text(
    "raise SystemExit(2)\n", encoding="utf-8", newline="\n")
# Fixtura D: NEEXISTUJÍCÍ soubor — žádný skript se nezakládá.
# Fixtura E: exit=2, DVĚŘÁDKOVÉ vlastní hlášení bez markeru.
# ⚠ Přidána P18 proto, že bez ní je mutace „rozhoduje počet ŘÁDKŮ" nerozlišitelná:
# fixtura A má JEDEN řádek, takže `len(radky) <= 1` (přesně vada H87) i `not text`
# dají pro VŠECHNY moje fixtury STEJNÝ výsledek. Mutace, kterou data nerozliší,
# není důkaz o kódu — je to díra v datech (a to je poučení P18).
(FIX / "ovd-e-dva-radky.py").write_text(
    'print("P18 fixtura E")\nprint("druhy radek bez markeru")\nraise SystemExit(2)\n',
    encoding="utf-8", newline="\n")

# Ověř SKUTEČNÉ chování fixtur (ne že si to myslím).
print("    skutečné chování fixtur (spouštím je):")
for jm, oc, vzor in [("ovd-a-bez-markeru.py", 2, r"(\d+) kontrol"),
                     ("ovd-b-s-markerem.py", 2, r"(\d+) kontrol"),
                     ("ovd-c-bez-vystupu.py", 2, r"(\d+) kontrol")]:
    v = subprocess.run([sys.executable, "-B", str(FIX / jm)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=60)
    shoda = bool(re.search(vzor, (v.stdout or "") + (v.stderr or "")))
    print(f"      {jm:26} exit={v.returncode} stdout={(v.stdout or '').strip()!r} "
          f"vzor_sedí={shoda}")
    kont(f"fixtura {jm} má exit={oc} (jak test předpokládá)", v.returncode == oc,
         f"naměřeno exit={v.returncode}")
    if jm == "ovd-a-bez-markeru.py":
        kont("fixtura A: vzor NESEDÍ (to je ten případ bez markeru)", not shoda)
    if jm == "ovd-b-s-markerem.py":
        kont("fixtura B: vzor SEDÍ", shoda)
    if jm == "ovd-c-bez-vystupu.py":
        kont("fixtura C: výstup je PRÁZDNÝ",
             not (v.stdout or "").strip() and not (v.stderr or "").strip())

# ── 3) HARNESS: ŽIVÝ `g3` JAKO ZDROJ, VYMĚNĚNÉ JEN `BRANY` ────────────────
print("\n--- 3) SESTAVENÍ HARNESSu ZE ŽIVÉHO `g3` ---")
# Vyměň seznam `BRANY = [...]` za svoje fixtury.
m = re.search(r"^BRANY = \[.*?^\]\n", zdroj, re.M | re.S)
kont("v živém g3 se našel blok `BRANY`", m is not None)
# Vyměň smyčku, která brány spouští, za volání s mými fixturami.
m2 = re.search(r"^for popis, prikaz, vzor in BRANY:\n    spust\(popis, prikaz, vzor\)\n",
               zdroj, re.M)
kont("v živém g3 se našla spouštěcí smyčka", m2 is not None)

ME_FIXTURY = '''BRANY = [
    ("D-fixtura A: exit=2 s VLASTNÍM hlášením BEZ markeru",
     ["python", "<ANALYZA>/a-ukol-scratch/ov-d-fixtury/ovd-a-bez-markeru.py"],
     r"(\\d+) kontrol"),
    ("D-fixtura B: exit=2 s hlášením S markerem",
     ["python", "<ANALYZA>/a-ukol-scratch/ov-d-fixtury/ovd-b-s-markerem.py"],
     r"(\\d+) kontrol"),
    ("D-fixtura C: exit=2 BEZ výstupu",
     ["python", "<ANALYZA>/a-ukol-scratch/ov-d-fixtury/ovd-c-bez-vystupu.py"],
     r"(\\d+) kontrol"),
    ("D-fixtura D: NEEXISTUJÍCÍ soubor",
     ["python", "<ANALYZA>/a-ukol-scratch/ov-d-fixtury/ovd-d-neexistuje.py"],
     r"(\\d+) kontrol"),
    ("D-fixtura E: exit=2, DVĚŘÁDKOVÉ hlášení bez markeru",
     ["python", "<ANALYZA>/a-ukol-scratch/ov-d-fixtury/ovd-e-dva-radky.py"],
     r"(\\d+) kontrol"),
]
'''
ME_SMYCKA = '''for popis, prikaz, vzor in BRANY:
    spust(popis, prikaz, vzor)
'''
h = zdroj[:m.start()] + ME_FIXTURY + zdroj[m.end():]
m2b = re.search(r"^for popis, prikaz, vzor in BRANY:\n    spust\(popis, prikaz, vzor\)\n",
                h, re.M)
h = h[:m2b.start()] + ME_SMYCKA + h[m2b.end():]
# Výstup přepiš mimo živý strom, ať se nepřepíše doklad P17.
h = h.replace('VYSTUP = ANALYZA / "g3-brany-vystup.txt"',
              'VYSTUP = ANALYZA / "ov-d-harness-vystup.txt"')
# ⚠ DOPLNĚNO V P20 (6. 10. 2026) — PŘÍMÝ DŮSLEDEK rozhodnutí Úkolu A: `g3` od
# P20 soudí i červené, takže deklarace `OCEKAVANE_NENULOVE` s `zadání kontrola`
# je v kopii VISUTÁ (fixtury nahrazují CELÝ blok `BRANY`) → `g3` správně končí
# `exit 1` z důvodu, který tenhle doklad NEZKOUMÁ (`overovani` §10.1).
h = h.replace('OCEKAVANE_NENULOVE = {"zadání kontrola": 1}',
              "OCEKAVANE_NENULOVE = {}")
# ⚠ A druhá stejná věc: fixtury BĚŽÍ, ale mají `exit=2` a (záměrně) nevykazují
# čítač, takže `g3` je právem hlásí jako „běžely bez čítače“ → další `exit 1`
# z cizího důvodu. Deklarují se proto VŠECHNY — tenhle test měří KLASIFIKACI.
_dek = re.search(r"^OCEKAVANE_BEZ_CITACE = \{.*?\}$", h, re.M)
if _dek:
    _jm = re.findall(r'\("(D-fixtura [^"]*)"', ME_FIXTURY)
    h = (h[:_dek.start()]
         + "OCEKAVANE_BEZ_CITACE = {%s}"
         % ", ".join(repr(x) for x in ["C2: mutace N1 (5 běhů)"] + _jm)
         + h[_dek.end():])
    kont("harness deklaruje všech 5 fixtur bez čítače (měří klasifikaci)",
         all(x in h for x in _jm), f"{len(_jm)} fixtur")
HARNESS.write_text(h, encoding="utf-8", newline="\n")
import ast as _ast  # noqa: E402
_ast.parse(h)
kont("harness se dá zkompilovat", True)
# ⚠ POZOR (vlastní omyl P18): nesmí se kontrolovat `"test-h87" not in h` —
# ten řetězec je v DOCSTRINGU funkce `je_neotevrena`, který z živého g3 pochází
# a zůstává. Byl to falešný poplach o správném harnessu.
kont("harness obsahuje MOJE fixtury a NEobsahuje P17 fixtury",
    h.count("ovd-a-bez-markeru") >= 1 and "test-h87-klasifikator.py\", " not in h,
    f"mých fixtur v BRANY: {h.count('ovd-')}")
kont("BRANY v harnessu mají 5 položek (moje fixtury A–E), ne 37 (živé)",
    h.count('("D-fixtura') == 5, f"{h.count('(\"D-fixtura')}")

# ── 4) BĚH HARNESSu ───────────────────────────────────────────────────────
print("\n--- 4) BĚH HARNESSU (živý klasifikátor, moje fixtury) ---")
v = subprocess.run([sys.executable, "-B", str(HARNESS)], capture_output=True,
                   text=True, encoding="utf-8", errors="replace",
                   cwd=str(REPO), timeout=900)
out = (v.stdout or "") + (v.stderr or "")
print(out.rstrip())
kont("harness DOBĚHL a řekl verdikt (není to pád ani prázdný výstup)",
     "VÝSLEDEK g3:" in out, f"exit={v.returncode}, {len(out)} B výstupu")
# ⚠ PŘEPSÁNO V P20: do P20 tu stálo `v.returncode == 0` a procházelo to JEN
# proto, že `g3` do P19 NEMĚL ŽÁDNÝ `sys.exit` (vždy 0) — kontrola, která nemá
# jak selhat. Správný výsledek pro tenhle doklad je naopak NENULOVÝ: fixtury
# C a D „vůbec nezačaly“ a A/B/E „běžely bez čítače“. `exit 0` by znamenalo,
# že klasifikátor nic nenašel. Soudí se proto KLASIFIKACE (kontroly níž), ne kód.

blok_nezacaly = re.search(
    r"⚠ BRÁNY, KTERÉ VŮBEC NEZAČALY \((\d+)\).*?(?=\n\n|\nbrány, které)",
    out, re.S)
blok_bez_citace = re.search(
    r"\? BRÁNY, KTERÉ BĚŽELY, ALE NEVYKÁZALY ČÍTAČ \((\d+)\).*?(?=\n\n|\Z)",
    out, re.S)
n_nezacaly = int(blok_nezacaly.group(1)) if blok_nezacaly else 0
n_bez_citace = int(blok_bez_citace.group(1)) if blok_bez_citace else 0
jmena_nezacaly = blok_nezacaly.group(0) if blok_nezacaly else ""
jmena_bez_citace = blok_bez_citace.group(0) if blok_bez_citace else ""
print(f"\n    → 'nezačaly'={n_nezacaly}  'běžely bez čítače'={n_bez_citace}")

kont("fixtura A (bez markeru) NENÍ 'nezačala' — je ve TŘETÍM stavu",
    "D-fixtura A" not in jmena_nezacaly and "D-fixtura A" in jmena_bez_citace,
    "A musí být v 'běžely, ale nevykázaly čítač'")
kont("fixtura B (s markerem) NENÍ 'nezačala'",
    "D-fixtura B" not in jmena_nezacaly, "B má čítač → není ani ve třetím stavu")
kont("fixtura B má ČÍTAČ (vzor našel 7)", "otevřela: 7" in out,
    "hledám 'otevřela: 7'")
kont("fixtura C (bez výstupu) JE 'nezačala'",
    "D-fixtura C" in jmena_nezacaly, "C = exit 2 + prázdný výstup")
kont("fixtura D (neexistující soubor) JE 'nezačala'",
    "D-fixtura D" in jmena_nezacaly, "D = exit 2 + podpis chybějícího souboru")
kont("'nezačaly' jsou PRÁVĚ DVĚ (C a D)", n_nezacaly == 2,
    f"naměřeno {n_nezacaly}")

# ── 5) MUTACE KLASIFIKÁTORU (porovnává se MNOŽINA, ne počet) ──────────────
# ⚠ VLASTNÍ OMYLY P18 (dva, oba o měřidle — a poučné):
#  (a) První „mutace" jen PŘEJMENOVALA seznam podpisů (`_PODPIS_CHYBEJICIHO_
#      SOUBORU` → `_MUT`) a přejmenovala i použití → chování se NEZMĚNILO.
#      **Mutace, která se neprovedla, tvrdí totéž co mutace, která projde.**
#  (b) Druhá verze mutovala správně, ale test porovnával **POČET** „nezačalých"
#      (2 vs 2) → mutace prošla jako „nedetekována", i když se FALEŠNĚ označila
#      JINÁ brána. Je to táž past jako „klíč je v kopii, ale na jiném kroku"
#      (`AGENTS.md`): **neporovnávej součty, porovnávej PRVKY.**
PUVODNI_VETEV = """    text = vystup.strip()
    if not text:
        return True                       # prázdný výstup = interpret neřekl nic
    return any(z in text for z in _PODPIS_CHYBEJICIHO_SOUBORU)"""
MUT_DELKA = """    text = vystup.strip()
    # MUTACE 1 = PŘESNĚ vada H87: rozhoduje počet ŘÁDKŮ, ne obsah.
    if len(text.splitlines()) <= 1:
        return True
    return any(z in text for z in _PODPIS_CHYBEJICIHO_SOUBORU)"""
MUT_EXIT = """    text = vystup.strip()
    if exit_kod != 1 or not nalezeno.startswith("—"):
        return False
    if not text:
        return True
    return any(z in text for z in _PODPIS_CHYBEJICIHO_SOUBORU)"""


def spust_harness(text: str) -> dict:
    """Zapíše harness, spustí ho a vrátí MNOŽINY zařazených bran."""
    HARNESS.write_text(text, encoding="utf-8", newline="\n")
    r = subprocess.run([sys.executable, "-B", str(HARNESS)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(REPO), timeout=900)
    o = (r.stdout or "") + (r.stderr or "")
    b1 = re.search(r"BRÁNY, KTERÉ VŮBEC NEZAČALY \(\d+\)[^\n]*\n(.*?)(?=\n\n|\Z)",
                   o, re.S)
    b2 = re.search(r"NEVYKÁZALY ČÍTAČ \(\d+\)[^\n]*\n(.*?)(?=\n\n|\Z)", o, re.S)
    return {
        "nezacaly": set(re.findall(r"^\s+(D-fixtura [A-E])", b1.group(1), re.M))
        if b1 else set(),
        "bez_citace": set(re.findall(r"^\s+(D-fixtura [A-E])", b2.group(1), re.M))
        if b2 else set(),
        "exit": r.returncode, "vystup": o}


ZDRAVY = {"nezacaly": {"D-fixtura C", "D-fixtura D"},
          "bez_citace": {"D-fixtura A", "D-fixtura E"}}
# Ověř, že čtení výstupu vůbec něco přečte (jinak by množiny byly prázdné
# a každá mutace by „prošla" jako odhalená).
kont("čtení výstupu funguje — zdravý stav dá OČEKÁVANÉ množiny (ne jen neprázdné)",
    ZDRAVY["nezacaly"] == {"D-fixtura C", "D-fixtura D"} and
    ZDRAVY["bez_citace"] == {"D-fixtura A", "D-fixtura E"},
    f"očekáváno nezačaly=C,D a bez_čitače=A,E")

print("\n--- 5) MUTACE KLASIFIKÁTORU (porovnání MNOŽIN) ---")
vysledky_mutaci = {}
for jmeno, mut in [("M1: délka místo obsahu", MUT_DELKA),
                   ("M2: exit 1 místo exit 2", MUT_EXIT)]:
    h2 = h.replace(PUVODNI_VETEV, mut)
    kont(f"{jmeno} — text se SKUTEČNĚ změnil (mutace provedena)", h2 != h,
        f"délka {len(h)} → {len(h2)}")
    r2 = spust_harness(h2)
    vysledky_mutaci[jmeno] = {"nezacaly": sorted(r2["nezacaly"]),
                              "bez_citace": sorted(r2["bez_citace"]),
                              "exit": r2["exit"]}
    print(f"    {jmeno}: nezačaly={sorted(r2['nezacaly'])} "
          f"(zdravý {sorted(ZDRAVY['nezacaly'])}), "
          f"bez_čitače={sorted(r2['bez_citace'])}")
    kont(f"{jmeno} — TEST ZČERVENÁ (MNOŽINA se liší od zdravé)",
        r2["nezacaly"] != ZDRAVY["nezacaly"],
        f"zdravý={sorted(ZDRAVY['nezacaly'])} vs mutovaný={sorted(r2['nezacaly'])}")
    kont(f"{jmeno} — test si toho všimne i v množině 'bez čítače'",
        r2["bez_citace"] != ZDRAVY["bez_citace"] or
        r2["nezacaly"] != ZDRAVY["nezacaly"],
        "rozhoduje změna ZAŘAZENÍ, ne součet")

# Konkrétně: M1 (= vada H87) musí fixturu A FALEŠNĚ vykázat jako „nezačala".
r1 = spust_harness(h.replace(PUVODNI_VETEV, MUT_DELKA))
print(f"    M1 — fixtura A v nezačalých: {'D-fixtura A' in r1['nezacaly']}, "
      f"fixtura E v nezačalých: {'D-fixtura E' in r1['nezacaly']}")
kont("M1 vyrobí FALEŠNÝ NÁLEZ u fixtury A (přesně vada H87)",
    "D-fixtura A" in r1["nezacaly"],
    "jednořádkové vlastní hlášení se s řádkovým pravidlem stane „nezačala\"")
kont("M1 vyrobí FALEŠNÝ NÁLEZ i u fixtury E (dvě řádky, ale krátké)",
    "D-fixtura E" not in r1["nezacaly"],
    "E má DVĚ řádky → řádkové pravidlo ho NECHYTÍ; to je přesně ta díra, "
    "kvůli které fixtura E existuje")
kont("M1 — A se přesune z 'bez čítače' do 'nezačalých' (změna ZAŘAZENÍ)",
    "D-fixtura A" in r1["nezacaly"] and "D-fixtura A" not in r1["bez_citace"],
    f"nezačaly={sorted(r1['nezacaly'])} bez_čitače={sorted(r1['bez_citace'])}")
# ── 5b) KTERÉ PODPISY V SEZNAMU JSOU NA TÉTO STANICI ŽIVÉ ─────────────────
# Vlastní nález P18: seznam měl 8 podpisů, ale NE VŠECHNY mohou na této stanici
# někdy zabrat. Tichý mrtvý podpis je slepé místo — a pozná se to měřením,
# ne čtením. Měří se proti SKUTEČNÝM výstupům interpretů.
print("\n--- 5b) ŽIVÉ vs MRTVÉ PODPISY (měřeno proti skutečným výstupům) ---")
m_sez = re.search(r"_PODPIS_CHYBEJICIHO_SOUBORU = \((.*?)\)\n", h, re.S)
podpisy = re.findall(r'"([^"]+)"', m_sez.group(1)) if m_sez else []
# ⚠ PŘEPSÁNO V P20 (6. 10. 2026): do P20 tu stálo `>= 6`, protože seznam měl
# 8 podpisů. **P19 ho zúžila na 4 ŽIVÉ** (nález H94: čtyři byly mrtvé pro `g3`
# — `is not recognized` je živý obecně, ale `g3` shell nepoužívá) a zbytek
# pojmenovala v komentáři. Doklad tím **zastaral**: tvrdil počet, který už
# neplatí, a spadl na SPRÁVNĚ zúženém seznamu.
# ⚠ POZOR NA POUČENÍ: kdyby tu zůstalo `>= 6`, doklad by hlásil vadu tam, kde
# je oprava — tedy „brána na nastraženém poplachu“ (`overovani` §10.1 obráceně).
# Současně se ale nesmí zkontrolovat jen „něco tam je“ — proto se ověřuje
# i to, že **každý** podpis v seznamu je skutečně živý (níž, proti výstupům).
kont("seznam podpisů se ze zdroje přečetl a je NEZPRÁZDNĚNÝ", len(podpisy) >= 4,
    f"{len(podpisy)} podpisů: {podpisy}")
kont("seznam je ZÚŽENÝ na živé (H94: 4, ne původních 8)", len(podpisy) == 4,
    "kdyby se rozšířil o mrtvý podpis, je to zase slepé místo — pozná se to níž")
NE = FIX / "ovd-d-neexistuje.py"
realne = {}
for jm, cmd in [("python", [sys.executable, "-B", str(NE)]),
                ("node", ["node", str(NE)])]:
    rr = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                        errors="replace", timeout=60)
    realne[jm] = (rr.stdout or "") + (rr.stderr or "")
zive = [p for p in podpisy if any(p in t for t in realne.values())]
mrtve = [p for p in podpisy if p not in zive]
for p in podpisy:
    kam = [jm for jm, t in realne.items() if p in t]
    print(f"    {'ŽIVÝ ' if p in zive else 'mrtvý'} {p!r:44} "
          f"{'(' + ', '.join(kam) + ')' if kam else ''}")
print(f"    → živých {len(zive)}, mrtvých {len(mrtve)}")
kont("na této stanici je ŽIVÝ aspoň jeden podpis (seznam není celý mrtvý)",
    len(zive) >= 1, f"živé: {zive}")
# A teď mutace, která opravdu MUSÍ změnit chování: odeber VŠECHNY živé podpisy.
h3 = h
odebrano = 0
# ⚠ TŘETÍ VLASTNÍ OMYL P18 (o měřidle): seznam podpisů NENÍ jeden na řádek —
# v živém `g3` jsou **tři podpisy na jednom řádku**. Dvě verze mazání (naivní
# `replace` s 4 mezerami i regex `^\s*"…",\n`) proto odebraly **NULA** položek
# a M3 „nedetekovala" — což vypadalo jako slepá brána, ale byla to **mutace,
# která se neprovedla**. Správně se seznam čte `ast.literal_eval` a přepíše se
# CELÝ, takže na formátování zdroje nezáleží.
import ast as _ast2  # noqa: E402
m_t = re.search(r"_PODPIS_CHYBEJICIHO_SOUBORU = (\(.*?\n\))\n", h, re.S)
puvodni_seznam = _ast2.literal_eval(m_t.group(1))
zbyle = [p for p in puvodni_seznam if p not in zive]
kont("M3 — ze seznamu se skutečně odebraly živé podpisy",
    len(zbyle) == len(puvodni_seznam) - len(zive),
    f"{len(puvodni_seznam)} → {len(zbyle)} (odebráno "
    f"{len(puvodni_seznam) - len(zbyle)}; seznam má 3 podpisy na řádek, "
    "proto řádkové mazání nefungovalo)")
novy_seznam = ("_PODPIS_CHYBEJICIHO_SOUBORU = (\n"
               + "".join(f'    "{p}",\n' for p in zbyle) + ")\n")
h3 = h[:m_t.start()] + novy_seznam + h[m_t.end():]
odebrano = len(zive)
_ast2.parse(h3)          # ať se nezkouší spustit syntakticky vadný harness
kont("M3 — harness po mutaci je syntakticky v pořádku a liší se od zdravého",
    h3 != h, "zkompilováno")
r3 = spust_harness(h3)
vysledky_mutaci["M3: odebrány živé podpisy"] = {
    "nezacaly": sorted(r3["nezacaly"]), "exit": r3["exit"]}
print(f"    M3: nezačaly={sorted(r3['nezacaly'])}")
kont("M3 je ODHALENA — seznam podpisů je měřený, ne kosmetický",
    r3["nezacaly"] != ZDRAVY["nezacaly"],
    f"zdravý={sorted(ZDRAVY['nezacaly'])} vs M3={sorted(r3['nezacaly'])}")
kont("M3 — fixtura D propadne mezi 'běžela' (to je to slepé místo)",
    "D-fixtura D" not in r3["nezacaly"],
    "bez živých podpisů se chybějící soubor vykáže jako „běžela\"")

# ── 6) ŽIVÝ g3 SE NESMÍ ZMĚNIT ────────────────────────────────────────────
hash_po = hashlib.sha256(G3.read_bytes()).hexdigest()
kont("ŽIVÝ `g3-brany.py` je bajt na bajt nezměněný", hash_po == hash_pred,
    f"{hash_po[:16]}")
HARNESS.unlink(missing_ok=True)

print("\n" + "=" * 78)
print(f"VÝSLEDEK D: kontrol {kontrol}, chyb {chyb}")
print("=" * 78)
json.dump({"kontrol": kontrol, "chyb": chyb, "n_nezacaly": n_nezacaly,
           "n_bez_citace": n_bez_citace, "mutace": vysledky_mutaci,
           "hash_g3": hash_po},
          open(ANALYZA / "ov-d-vysledky.json", "w",
               encoding="utf-8"), ensure_ascii=False, indent=2)
sys.exit(1 if chyb else 0)
