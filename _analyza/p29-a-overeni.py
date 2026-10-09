# -*- coding: utf-8 -*-
r"""P29/A — NEZÁVISLÉ PŘEMĚŘENÍ PRÁCE P28 (A1–A7) VLASTNÍM POSTUPEM.

CO TO JE: měřidlo session **P29**. Ověřuje práci P28 — záznam `HANDOFF.md` **§59**
— a to **jiným postupem, než jak vznikla** (`AGENTS.md`: „autor není nezávislý
reviewer“; `hlouchkova-analyza` §1).

⚠ ČÍM SE LIŠÍ OD `p28-a-overeni.py` (a proč to není jeho kopie):
  * **A1** netestuje měřidlo P27, ale **měřidlo P28** — VLASTNÍMI kontramutacemi
    (kopie `HANDOFF.md` s posunutým číslem, kopie `g3` s 50. branou, kopie `ov-g`
    bez hlášení rozsahu) a každá se **TŘEMI NOHAMI**: živé → baseline;
    mutant → měřidlo spadne NA TÉ KONTROLE; mutant + oslabené měřidlo → projde;
  * **A2** vrací do handleru **ZARÁŽKU** (P28 poškozovala ODPOVĚĎ) a měří navíc
    **IZOLACI**: zarážka na jednom endpointu nesmí zčervenat skupinu jinou;
  * **A3** pouští KOPII testu s **PRÁZDNOU falešnou D1** (P28 poškozovala TEXT
    dotazu) a třídí, které kontroly zůstanou ZELENÉ — to je měřený rozdíl
    TVAR vs OBSAH;
  * **A4** čte čísla **z §59** (P28 četla z §57/§58) a u každého tvrzení VYPÍŠE
    **OKNO, které vzor trefil** — jinak brána čte citaci místo tvrzení;
  * **A5** počítá rozsah Hxx i kontinuitu id **vlastním průchodem**, ne výpisem;
  * **A6** měří opravu B5 na **fixturách** (`FORGE_SKILLS`), včetně toho, že
    deklarovaná výjimka **NEPROSÁKNE** do jiného skillu;
  * **A7** pouští **inventář → g3 → validate-all** v tomto pořadí a ověřuje, že
    g3 hlásí jen POJMENOVANÉ stavy (+ přepočet otisku dvěma způsoby).

⚠ PROČ SE A4 POUŠTÍ AŽ PO A7: A4 srovnává čísla bran a ta se měří jednou.
Pořadí běhu je proto A1, A2, A3, A5, A6, **A7**, **A4** — je vypsané v hlavičce.

⚠ DOKLADY SE ZAPISUJÍ BAJTŮ (UTF-8), ne přesměrováním v PowerShellu: naměřeno
9. 10. 2026 — tři doklady P28 (`p28-b-mutace-vystup.txt`, `p28-baseline-p27a-
vystup.txt`, `p28-p26b-dnes-vystup.txt`) jsou **UTF-16LE s BOM** a `read` tool
je odmítne jako binárku.

⚠ CO NEMĚŘÍ: kvalitu kódu conductora ani správnost rozhodnutí P28 — měří shodu
JEJÍCH TVRZENÍ s živým stavem a schopnost měřidla spadnout.

Použití:
    python _analyza/p29-a-overeni.py            # dávka: A2, A3, A5, A6, A7, A4
    python _analyza/p29-a-overeni.py --plne     # i A1 (drahé kontramutace)
    python _analyza/p29-a-overeni.py --jen A5
"""

import argparse
import hashlib
import json
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
TOOLS = WS / "tools"
HRA = WS.parent / "uo-shadows"
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
SRC = WS / "conductor" / "src" / "index.ts"
TEST_TIK = TOOLS / "test-tick-offline.mjs"
KOPIE_TESTU = ANALYZA / "p29-kopie-tick.mjs"
G3 = ANALYZA / "g3-brany.py"
OV_G = ANALYZA / "ov-g-neovereno.py"
P28_A = ANALYZA / "p28-a-overeni.py"
P28_B = ANALYZA / "p28-b-mutace.py"
NEANGL = ANALYZA / "hl-neanglicky-v-kodu.py"
INVENTAR = ANALYZA / "_inventar.json"
OVER_SKILLY = TOOLS / "over-skilly.py"
SKILL_MUTACE = ANALYZA / "test-over-skilly-delegovane.py"
TICK_MUTACE = ANALYZA / "tick-mutace.py"
OVER_DOK = TOOLS / "over-dokumentaci.py"
HANDOFF_K = ANALYZA / "handoff-kontrola-uplnost.py"
KRONIKA_K = ANALYZA / "kronika-kontrola.py"
OBNOV_KRONIKU = ANALYZA / "p28-obnov-kroniku.py"
ZIVA = ANALYZA / "p28-ziva-sluzba.mjs"
VALIDATE = TOOLS / "validate-all.mjs"
SONDA_ULOHY = ANALYZA / "p29-sonda-ulohy.mjs"
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
ROWS = ANALYZA / "p29-sluzba-rows.mjs"
ROADMAP_HRA = HRA / ".forge" / "roadmap.json"
SCRATCH = ANALYZA / "p29-scratch"
PY = sys.executable
NODE = "node"

kontrol = 0
chyb = 0
nezmereno = []
ROZDILY = []
MER = {}

ZARAZKY = (
    ("X", "/health", 'if (path === "/health") {'),
    ("Y", "/queue", 'if (path === "/queue") {'),
    ("Z", "/roadmap", 'if (path === "/roadmap") {'),
    ("AA", "/failed", 'if (path === "/failed") {'),
    ("AB", "/status", 'if (path === "/status") {'),
    ("AC", "/workers", 'if (path === "/workers") {'),
    ("AD", "/games", 'if (path === "/games") {'),
)


class Tee:
    """Výstup na obrazovku I do souboru (bajty UTF-8) — doklad musí být čitelný."""

    def __init__(self, cesta):
        self.soubor = open(cesta, "wb")
        self.orig = sys.__stdout__

    def write(self, s):
        self.orig.write(s)
        self.soubor.write(s.encode("utf-8", "replace"))

    def flush(self):
        self.orig.flush()
        self.soubor.flush()

    def isatty(self):
        return False


def check(popis, zjisteno, ocekavano):
    global kontrol, chyb
    kontrol += 1
    if zjisteno == ocekavano:
        print("  OK    %s" % popis)
        return True
    chyb += 1
    print("  CHYBA %s\n        čekáno:   %r\n        naměřeno: %r"
          % (popis, ocekavano, zjisteno))
    return False


def rozdil(popis, tvrzene, namerene, druh, poznamka=""):
    """Pojmenovaný ROZDÍL proti tvrzení z dokumentu (≠ vada kódu)."""
    global kontrol, chyb
    kontrol += 1
    chyb += 1
    ROZDILY.append((popis, tvrzene, namerene, druh, poznamka))
    print("  ROZDÍL %s\n        tvrzeno:  %r\n        naměřeno: %r%s"
          % (popis, tvrzene, namerene, ("\n        " + poznamka) if poznamka else ""))
    return False


def sedi(popis, tvrzene, namerene):
    global kontrol
    kontrol += 1
    print("  OK    %s (tvrzeno i naměřeno: %r)" % (popis, namerene))
    return True


def srovnej(popis, tvrzene, namerene, druh="čítač", poznamka=""):
    """Tvrzení vs. měření — jediná cesta, jak srovnat (nedá se zapomenout)."""
    if tvrzene == namerene:
        return sedi(popis, tvrzene, namerene)
    return rozdil(popis, tvrzene, namerene, druh, poznamka)


def nezmereno_zapis(popis, duvod):
    nezmereno.append("%s — %s" % (popis, duvod))
    print("  ??    %s (NEZMĚŘENO: %s)" % (popis, duvod))


def cmd(argumenty, timeout=7200, env=None, cwd=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    try:
        r = subprocess.run([str(a) for a in argumenty], cwd=str(cwd or WS), env=e,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT po %d s" % timeout


def citac(v, vzor=r"(\d+) kontrol, (\d+) chyb"):
    """POSLEDNÍ čítač ve výstupu (dřívější mohou být z dílčích běhů)."""
    m = None
    for m in re.finditer(vzor, v, re.IGNORECASE):
        pass
    return (int(m.group(1)), int(m.group(2))) if m else None


def citac_obecny(v):
    """Čítač v OBOU používaných tvarech (`N kontrol, M chyb` i `Kontrol: N, chyb: M`)."""
    for vzor in (r"(\d+) kontrol, (\d+) chyb", r"Kontrol:\s*(\d+),\s*chyb:\s*(\d+)"):
        m = None
        for m in re.finditer(vzor, v, re.IGNORECASE):
            pass
        if m:
            return (int(m.group(1)), int(m.group(2)))
    return None


def cervene(v):
    return [l.strip()[5:].strip() for l in v.splitlines() if l.strip().startswith("CHYBA")]


def zelene(v):
    return [l.strip()[2:].strip() for l in v.splitlines() if l.strip().startswith("OK ")]


def skupina(popis):
    m = re.match(r"^([A-Z]{1,2}):\s", popis)
    return m.group(1) if m else None


def sha(p):
    try:
        return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
    except OSError:
        return None


def zapis_doklad(jmeno, text):
    cesta = ANALYZA / jmeno
    b = text.encode("utf-8", "replace")
    cesta.write_bytes(b)
    print("      doklad: %s (%d B, UTF-8)" % (jmeno, len(b)))
    return cesta


def sekce(cislo, text):
    """Tělo oddílu `## <cislo>.` (od nadpisu k dalšímu `## `)."""
    m = re.search(r"^## %s\." % re.escape(str(cislo)), text, re.M)
    if not m:
        return ""
    m2 = re.search(r"^## ", text[m.end():], re.M)
    return text[m.start(): m.end() + m2.start()] if m2 else text[m.start():]


def s59():
    return sekce(59, HANDOFF.read_text(encoding="utf-8", errors="replace"))


def tvrzeni(text, vzor, popis, okno=140):
    """Skupiny regexu PŘEČTENÉ Z DOKUMENTU + VYPSANÉ OKNO, které vzor trefil.

    Drží dvě naměřené pasti: (1) chybějící tvrzení se NESMÍ tiše přeskočit;
    (2) velkorysé okno = slepota → vypisuje se, co přesně se přečetlo.
    """
    m = re.search(vzor, text, re.S)
    if m is None:
        global kontrol, chyb
        kontrol += 1
        chyb += 1
        print("  CHYBA tvrzení se v §59 NENAŠLO (kontrola by se tiše přeskočila): %s"
              % popis)
        return None
    print("      okno: %s" % re.sub(r"\s+", " ", m.group(0))[:okno])
    return tuple(m.groups())


def tvrzeni_v(vzor, popis, okno=140):
    """Tvrzení, které NEMUSÍ být v §59 — hledá se v §59 a pak v ZADÁNÍ.

    ⚠ DVA RŮZNÉ PŘÍPADY, KTERÉ SE NESMÍ SLÉVAT:
      * tvrzení, které v dokumentu MÁ být, a není → je to CHYBA (`tvrzeni`);
      * tvrzení, které je v JINÉM dokumentu (zadání §2.3) → hledá se tam
        a když není ani tam, hlásí se **NEZMĚŘENO** (pojmenovaně), protože
        „tvrzení se nepíše tam, kde jsem ho hledal“ není vada dokumentu.
    """
    for jmeno, text in (("§59", s59()),
                        ("zadání", ZADANI.read_text(encoding="utf-8", errors="replace")
                         if ZADANI.is_file() else "")):
        m = re.search(vzor, text, re.S)
        if m:
            print("      okno (%s): %s" % (jmeno, re.sub(r"\s+", " ", m.group(0))[:okno]))
            return tuple(m.groups())
    nezmereno_zapis(popis, "tvrzení není ani v §59, ani v zadání")
    return None


# ═══════════════════════════════════════════════════════ měření (cachovaná) ═══
def mer_g3():
    if "g3" not in MER:
        MER["g3"] = cmd([PY, str(G3)], timeout=3600)
    return MER["g3"]


def mer_validate():
    if "validate" not in MER:
        MER["validate"] = cmd([NODE, str(VALIDATE)], timeout=3600)
    return MER["validate"]


def mer_tick():
    if "tick" not in MER:
        MER["tick"] = cmd([NODE, str(TEST_TIK)], timeout=3600)
    return MER["tick"]


def mer_ziva():
    if "ziva" not in MER:
        kod, v = cmd([NODE, str(ZIVA)], timeout=600)
        try:
            MER["ziva"] = json.loads(v)
        except ValueError:
            MER["ziva"] = {"chyba": "výstup není JSON", "raw": v[:400]}
    return MER["ziva"]


def mer_rows():
    """ŘÁDKY z /roadmap a /queue (živě, jen čtení) — vlastním skriptem v Node."""
    if "rows" not in MER:
        if not ROWS.is_file():
            MER["rows"] = {"chyba": "p29-sluzba-rows.mjs není"}
        else:
            kod, v = cmd([NODE, str(ROWS)], timeout=600)
            try:
                MER["rows"] = json.loads(v)
            except ValueError:
                MER["rows"] = {"chyba": "výstup není JSON (exit=%d)" % kod, "raw": v[:300]}
    return MER["rows"]


def mer_kontrakt():
    """Kontrakt roadmapy hry — VLASTNÍM výpočtem (ne z výpisu sondy P28).

    ⚠ Hra patří CIZÍ session: čte se JEN SOUBOR, nikam se nezapisuje.
    """
    if "kontrakt" in MER:
        return MER["kontrakt"]
    out = {"soubor": None, "chyba": None}
    try:
        data = json.loads(ROADMAP_HRA.read_text(encoding="utf-8"))
        grains = data.get("grains") or data.get("tasks") or []
        out["soubor"] = {
            "celkem": len(grains),
            "bez_size_lines": [g.get("id") for g in grains if g.get("size_lines") in (None, "")],
            "bez_model": [g.get("id") for g in grains if not g.get("model")],
            "bez_acceptance": [g.get("id") for g in grains if not g.get("acceptance")],
            "strong": [g.get("id") for g in grains if g.get("model") == "strong"],
            "vsechna_id": [g.get("id") for g in grains],
        }
    except Exception as e:  # noqa: BLE001
        out["chyba"] = "roadmap.json: %s" % str(e)[:160]
    MER["kontrakt"] = out
    return out


# ═══════════════════════════════════════════════════════════════════════ A1 ══
def oslab_check(kopie, klic):
    """Vypne JEDNU kontrolu měřidla — 3. noha důkazu.

    ⚠ NESMÍ SE NAHRADIT ŘÁDEK ZA `pass`: kontrola bývá rozepsaná na VÍC ŘÁDKŮ
    (`check("…",\n  naměřeno,\n  očekáváno)`) a osiřelé argumenty jsou
    `SyntaxError` — naměřeno 9. 10. 2026: „oslabená“ kopie pak SPADLA a její
    prázdný výstup vypadal jako „kontrola zmizela“ (diferenciál by lhal).
    Obalí se proto `if False:` a původní řádek se jen odsadí — pokračovací
    řádky zůstanou uvnitř bloku a kód je pořád platný.
    """
    radky = kopie.read_text(encoding="utf-8").splitlines()
    for i, l in enumerate(radky):
        if klic in l:
            odsazeni = l[:len(l) - len(l.lstrip())]
            radky[i] = (odsazeni + "if False:  # P29/A1: 3. noha (kontrola vypnuta)\n"
                        + odsazeni + "    " + l.strip())
            kopie.write_bytes(("\n".join(radky) + "\n").encode("utf-8"))
            return True
    return False


def beh_p28(tag, etapy, prepinace=None, timeout=10800, plne=False, nastroj=None):
    """Běh měřidla P28 — VŽDY s vlastním `--vystup` (jinak přepíše doklad P28).

    ⚠ `plne=True` JE NUTNÉ U ETAPY A6: bez `--plne` se v ní `g3` a `validate-all`
    vůbec neměří ("(g3 a validate-all se v dávce neměří — sahají na inventář)")
    a diferenciál by pak nebyl diferenciál — naměřeno 9. 10. 2026: mutace g3
    s 50. branou nechala A6 zelené, protože ta kontrola VŮBEC NEBĚŽELA.

    ⚠ `nastroj` JE TŘETÍ NOHA: 3. noha musí spustit **OSLABENOU KOPII** měřidla,
    ne živé měřidlo. Naměřeno 9. 10. 2026: první verze spouštěla živé měřidlo
    i po „oslabení kopie“ → 3. noha byla PRÁZDNÁ a diferenciál lhal.
    """
    vystup = ANALYZA / ("p29-p28-%s-vystup.txt" % tag)
    a = [PY, str(nastroj or P28_A), "--jen", etapy, "--vystup", str(vystup)]
    if plne:
        a.append("--plne")
    for p in (prepinace or []):
        a += list(p)
    kod, v = cmd(a, timeout=timeout)
    return kod, v, set(cervene(v))


def _leg(kopie_meridla, klic, tag, etapy, prepinace, zive_v, popis, plne=False):
    """3. noha: mutant + OSLABENÉ měřidlo → spadlá kontrola zmizí (diferenciál sedí)."""
    if not oslab_check(kopie_meridla, klic):
        nezmereno_zapis("%s (3. noha)" % popis, "kontrolu `%s` nešlo vypnout" % klic)
        return
    kod2, v2, cerv2 = beh_p28(tag + "-oslabene", etapy, prepinace, plne=plne,
                              nastroj=kopie_meridla)
    zapis_doklad("p29-a1-%s-oslabene-vystup.txt" % tag, v2)
    check("%s: oslabené měřidlo + mutant → spadlá kontrola ZMIZELA" % popis,
          [x for x in cerv2 if klic in x], [])
    c0, c2 = citac(zive_v), citac(v2)
    check("%s: oslabený běh NENÍ prázdný (kontrol ubylo nejvýš o 1: %s → %s)"
          % (popis, c0, c2),
          bool(c0 and c2 and 0 <= (c0[0] - c2[0]) <= 1), True)


def a1():
    print("\n--- A1: UMÍ MĚŘIDLO P28 SPADNOUT? (vlastní kontramutace v KOPIÍCH) ---")
    t = s59()

    # (a) důkaz P28 o sobě samém — p28-b-mutace.py
    kod, v = cmd([PY, str(P28_B)], timeout=10800)
    zapis_doklad("p29-p28b-vystup.txt", v)
    tv = tvrzeni(t, r"p28-b-mutace\.py`?\s*→\s*\*\*(\d+) kontrol, (\d+) chyb\*\*",
                 "§59.1 B1: p28-b-mutace → 27/0")
    c = citac(v)
    if tv:
        srovnej("A1 p28-b-mutace.py", (int(tv[0]), int(tv[1])), c)
    check("A1 p28-b → exit 0", kod, 0)
    check("A1 p28-b měřil víc než 10 kontrol (jinak by důkaz nic nevážil)",
          (c[0] if c else 0) > 10, True)

    # (b) PLNÝ BĚH měřidla P28 — pod VLASTNÍM jménem dokladu
    print("      spouštím `p28-a-overeni.py --plne` (drahé; vlastní --vystup, "
          "aby se NEPŘEPSAL doklad P28)")
    t0 = time.time()
    vystup = ANALYZA / "p29-p28a-plne-vystup.txt"
    kod, v = cmd([PY, str(P28_A), "--plne", "--vystup", str(vystup)], timeout=21600)
    trvani = (time.time() - t0) / 60
    c = citac(v)
    print("      p28-a --plne: čítač=%s, exit=%d, trvání %.1f min" % (c, kod, trvani))
    tv = tvrzeni(t, r"p28-a-overeni\.py --plne`?\s*→\s*\*\*(\d+) kontrol, (\d+) chyb\*\*",
                 "§59.1 A: p28-a --plne → 122/14")
    if tv:
        srovnej("A1 p28-a --plne", (int(tv[0]), int(tv[1])), c, "čítač",
                "tvrzení §59.1 vs. DNEŠNÍ běh téhož příkazu")
    # NÁLEZ: doklad, který §59.1 uvádí jako doklad plného běhu
    dok = ANALYZA / "p29-p28a-doklad-jaky-byl.txt"
    if dok.is_file():
        cd = citac_obecny(dok.read_text(encoding="utf-8", errors="replace"))
        print("      doklad uvedený v §59.1 (`p28-a-overeni-vystup.txt`) měl čítač %s" % (cd,))
        if tv:
            check("A1 doklad uvedený v §59.1 JE plný běh (ne dílčí)",
                  cd == (int(tv[0]), int(tv[1])), True)
    else:
        nezmereno_zapis("A1 doklad P28", "zachovaná kopie p29-p28a-doklad-jaky-byl.txt není")

    print("      ⚠ tři VLASTNÍ kontramutace běží jako samostatná etapa `A1M` "
          "(spouští se `--jen A1M`), aby se drahý baseline neopakoval")


def a1m():
    """Tři VLASTNÍ kontramutace měřidla P28 — každá se TŘEMI nohami.

    ⚠ PROČ SAMOSTATNĚ: baseline (`p28-b-mutace.py` + `p28-a-overeni.py --plne`)
    trvá ~25 min; kontramutace se k němu vracejí jen čtením uloženého dokladu.
    """
    print("\n--- A1M: TŘI VLASTNÍ KONTRAMUTACE MĚŘIDLA P28 (3 nohy každá) ---")
    dok = ANALYZA / "p29-p28a-plne-vystup.txt"
    if dok.is_file():
        c = citac_obecny(dok.read_text(encoding="utf-8", errors="replace"))
        print("      baseline z dokladu %s: čítač=%s" % (dok.name, c))
    SCRATCH.mkdir(parents=True, exist_ok=True)
    _m1_handoff()
    _m2_g3()
    _m3_ovg()


def _cervene_a6_z_dokladu():
    """Červené kontroly oddílu A6 z ULOŽENÉHO plného běhu měřidla P28.

    ⚠ PROČ Z DOKLADU: `--jen A6` bez `--plne` g3 vůbec neměří, takže „baseline“
    z takového běhu je prázdný a diferenciál by lhal (naměřeno 9. 10. 2026).
    """
    dok = ANALYZA / "p29-p28a-plne-vystup.txt"
    if not dok.is_file():
        return None
    m = re.search(r"^--- A6[^\n]*$", dok.read_text(encoding="utf-8", errors="replace"), re.M)
    if not m:
        return None
    telo = dok.read_text(encoding="utf-8", errors="replace")[m.end():]
    m2 = re.search(r"^--- A", telo, re.M)
    telo = telo[:m2.start()] if m2 else telo
    return {l.strip()[5:].strip() for l in telo.splitlines()
            if l.strip().startswith("CHYBA")}


def a1m13():
    """M1 + M3 (LEVNÉ kontramutace) — opakovatelný běh po opravě `oslab_check`."""
    print("\n--- A1M13: DVĚ LEVNÉ KONTRAMUTACE (M1 §57, M3 ov-g) ---")
    _m1_handoff()
    _m3_ovg()


def _m1_handoff():
    """M1: posunuté ČÍSLO v §57 (kopie HANDOFF.md) → měřidlo P28 musí spadnout.

    ⚠ KOTVA JE SCHVÁLNĚ JINÁ, NEŽ MĚLA P28: bere se `99 řádků Hxx` — to číslo
    čte etapa **A5** měřidla P28 (která je LEVNÁ), kdežto `205/0` čte etapa A4
    (ta uvnitř pouští `g3` + `validate-all`, ~6 min na nohu). Diferenciál se tím
    nemění: pořád jde o to, že měřidlo čte tvrzení Z DOKUMENTU a po posunutí
    čísla **spadne**.
    """
    popis, tag = "M1 (§57: 99 řádků Hxx → 98)", "m1"
    klic = "A5 vlastní počet řádků Hxx v ŽIVÝCH zdrojích = tvrzených"
    kopie = ANALYZA / "p29-mut-handoff.md"
    zdroj = HANDOFF.read_text(encoding="utf-8")
    kotva = "99 řádků Hxx"
    # ⚠ KOTVA SE BERE Z MĚŘENÉHO ODDÍLU: `99 řádků Hxx` je v CELÉM dokumentu
    # **5×** (naměřeno 9. 10. 2026), ale měřidlo P28 čte to číslo z **§57**.
    # Mutace mimo §57 by posunula jiné místo, než které kontrola čte — a
    # diferenciál by byl **falešný nález o měřidle** (omyl P28-H/2).
    i57 = zdroj.find("\n## 57.")
    if i57 < 0:
        nezmereno_zapis("%s kotva" % popis, "§57 v HANDOFF.md není")
        return
    konec = zdroj.find("\n## ", i57 + 5)
    konec = konec if konec > 0 else len(zdroj)
    telo = zdroj[i57:konec]
    if telo.count(kotva) < 1:
        nezmereno_zapis("%s kotva" % popis, "v §57 kotva NENÍ")
        return
    # ⚠ V §57 je kotva **2×** (naměřeno 9. 10. 2026) — a to NEVADÍ: měřidlo P28
    # čte `re.search` = PRVNÍ výskyt, takže mutovat se musí PRVNÍ. Počet se
    # vypisuje, aby bylo vidět, že se mutovalo měřené místo, ne náhodné.
    kopie.write_bytes((zdroj[:i57] + telo.replace(kotva, "98 řádků Hxx", 1)
                       + zdroj[konec:]).encode("utf-8"))
    print("    %s: kopie HANDOFF.md, PRVNÍ `99 řádků Hxx` v §57 → `98` "
          "(v §57 je kotva %d×, v celém dokumentu 5×)" % (popis, telo.count(kotva)))
    _, v0, c0 = beh_p28("a1-m1-zive", "A5")
    zapis_doklad("p29-a1-m1-zive-vystup.txt", v0)
    print("      živé: červených=%d, kontrol=%s" % (len(c0), citac(v0)))
    _, v1, c1 = beh_p28("a1-m1-mutant", "A5", [("--handoff", str(kopie))])
    zapis_doklad("p29-a1-m1-mutant-vystup.txt", v1)
    check("%s: mutant ZAPL kontrolu, která ho čte" % popis, any(klic in x for x in c1), True)
    check("%s: mutant přidal právě JEDNU červenou (ne lavinu)" % popis, len(c1 - c0), 1)
    kmer = ANALYZA / "p29-mut-meridlo-m1.py"
    shutil.copyfile(P28_A, kmer)
    try:
        _leg(kmer, klic, tag, "A5", [("--handoff", str(kopie))], v0, popis)
    finally:
        kmer.unlink(missing_ok=True)


def _m2_g3():
    popis, tag, klic = "M2 (g3 s 50. branou)", "m2", "A6 g3 měří 49 bran"
    kopie = ANALYZA / "p29-mut-g3.py"
    fixtura = ANALYZA / "p29-mut-fixtura.py"
    fixtura.write_bytes(b"print('1 kontrol, 0 chyb')\n")
    zdroj = G3.read_text(encoding="utf-8")
    if zdroj.count("BRANY = [") != 1:
        nezmereno_zapis("%s kotva BRANY" % popis, "`BRANY = [` je v g3 %d×" % zdroj.count("BRANY = ["))
        return
    # ⚠ Náhrada NESMÍ obsahovat starý text jako podřetězec (`_mutace` to hlídá) —
    # proto `BRANY =[` (bez mezery za `=`), což je pořád platný Python.
    kopie.write_bytes(zdroj.replace(
        "BRANY = [", 'BRANY =[("p29-fixtura", ["python", %r], r"(\\d+)"),' % str(fixtura)
    ).encode("utf-8"))
    print("    %s: kopie g3-brany.py, fixtura je 50. branou" % popis)
    # ⚠ BASELINE SE ČTE Z ULOŽENÉHO PLNÉHO BĚHU, ne z běhu `--jen A6`: bez
    # `--plne` se v A6 `g3` VŮBEC NEMĚŘÍ (naměřeno 9. 10. 2026 — mutace pak
    # nechala A6 zelené, protože kontrolovaná kontrola vůbec neběžela).
    cerv0 = _cervene_a6_z_dokladu()
    if cerv0 is None:
        nezmereno_zapis("%s baseline" % popis,
                        "v dokladu p29-p28a-plne-vystup.txt není oddíl A6")
        return
    print("      baseline z plného běhu: červených v A6 = %d %s"
          % (len(cerv0), sorted(cerv0)[:2]))
    _, v1, c1 = beh_p28("a1-m2-mutant", "A6", [("--g3", str(kopie))], plne=True,
                        timeout=900)
    zapis_doklad("p29-a1-m2-mutant-vystup.txt", v1)
    if v1.startswith("TIMEOUT"):
        # ⚠ POJMENOVANÉ NEZMĚŘENO, ne tichý přeskočení: mutant g3 s fixturou
        # v této session NEDOBĚHL (naměřeno 9. 10. 2026, dvakrát). Diferenciál
        # pro TUTÉŽ mutaci ale existuje nezávisle: `p28-b-mutace.py` (M2, tři
        # nohy) — a jeho výsledek jsem přeměřil vlastním během: **27/0**.
        nezmereno_zapis("%s mutant" % popis,
                        "běh s 50. branou NEDOBĚHL (TIMEOUT 900 s); tutéž mutaci "
                        "měří třínoze `p28-b-mutace.py` (přeměřeno: 27/0)")
        return
    check("%s: mutant ZAPL kontrolu, která ho čte" % popis, any(klic in x for x in c1), True)
    kmer = ANALYZA / "p29-mut-meridlo-m2.py"
    shutil.copyfile(P28_A, kmer)
    try:
        _leg(kmer, klic, tag, "A6", [("--g3", str(kopie))], v1, popis, plne=True)
    finally:
        kmer.unlink(missing_ok=True)


def _m3_ovg():
    popis, tag, klic = "M3 (ov-g bez hlášení rozsahu)", "m3", \
        "A5 ROZSAH MIMO živé zdroje = vlastní počet"
    kopie = ANALYZA / "p29-mut-ovg.py"
    zdroj = OV_G.read_text(encoding="utf-8")
    kotva = "celkem mimo: {sum(n for _, n in mimo)} řádků v {len(mimo)} souborech"
    if zdroj.count(kotva) != 1:
        nezmereno_zapis("%s kotva rozsahu" % popis, "kotva je v ov-g %d×" % zdroj.count(kotva))
        return
    kopie.write_bytes(zdroj.replace(kotva, "celkem mimo: 0 řádků v 0 souborech").encode("utf-8"))
    print("    %s: kopie ov-g-neovereno.py hlásí NULOVÝ rozsah mimo živé zdroje" % popis)
    _, v0, c0 = beh_p28("a1-m3-zive", "A5")
    _, v1, c1 = beh_p28("a1-m3-mutant", "A5", [("--ovg", str(kopie))])
    zapis_doklad("p29-a1-m3-mutant-vystup.txt", v1)
    check("%s: mutant ZAPL kontrolu, která ho čte" % popis, any(klic in x for x in c1), True)
    kmer = ANALYZA / "p29-mut-meridlo-m3.py"
    shutil.copyfile(P28_A, kmer)
    try:
        _leg(kmer, klic, tag, "A5", [("--ovg", str(kopie))], v0, popis)
    finally:
        kmer.unlink(missing_ok=True)


# ═══════════════════════════════════════════════════════════════════════ A2 ══
def sha_hlavy(cesta):
    r = subprocess.run([str(TOOLS / "git.cmd"), "-C", str(WS), "show",
                        "HEAD:%s" % pathlib.Path(cesta).relative_to(WS).as_posix()],
                       capture_output=True, shell=True, timeout=120)
    return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else None


def a2():
    print("\n--- A2: VOLÁ test tiku SEDM endpointů? (ZARÁŽKA V HANDLERU) ---")
    if not SRC.is_file():
        nezmereno_zapis("A2", "conductor/src/index.ts neexistuje")
        return
    kod0, v0 = mer_tick()
    check("A2 KONTROLA: živý test tiku → exit 0 (naměřeno %s)" % (citac(v0),), kod0, 0)
    po_skupinach = {}
    for p in zelene(v0):
        g = skupina(p)
        if g:
            po_skupinach[g] = po_skupinach.get(g, 0) + 1
    for pref, _, _ in ZARAZKY:
        check("A2 skupina `%s:` má v živém běhu aspoň 1 KONTROLU" % pref,
              po_skupinach.get(pref, 0) >= 1, True)

    from _mutace import mutuj  # noqa: PLC0415
    for pref, cesta, kotva in ZARAZKY:
        print("    zarážka v handleru %s" % cesta)
        nahrada = ('if (path === "%s" || path === "/p29-zarazka") '
                   '{ return json({ error: "zarazka-p29%s" }, 599);'
                   % (cesta, cesta.replace("/", "-")))
        try:
            with mutuj(SRC, kotva, nahrada) as m:
                check("A2 %s zarážka se provedla (hash před != po)" % cesta,
                      m.hash_pred != m.hash_po_mutaci, True)
                kod, v = cmd([NODE, str(TEST_TIK)], timeout=3600)
        except ValueError as e:
            nezmereno_zapis("A2 zarážka v handleru %s" % cesta, str(e))
            continue
        cr = cervene(v)
        cilene = [x for x in cr if skupina(x) == pref]
        jine = sorted({skupina(x) for x in cr if skupina(x) and skupina(x) != pref})
        print("      test tiku: čítač=%s, červených=%d, z toho `%s:` = %d, jiné skupiny: %s"
              % (citac(v), len(cr), pref, len(cilene), jine or "—"))
        for x in cilene[:3]:
            print("        · %s" % x[:115])
        check("A2 %s zarážka ZAPLA kontroly SVÉ skupiny `%s:` (aspoň 1)" % (cesta, pref),
              len(cilene) >= 1, True)
        check("A2 %s zarážka NEZAPLA skupinu jinou (izolace)" % cesta, jine, [])
        check("A2 %s a kontrolní `A: /tick odpoví 200` zůstala ZELENÁ" % cesta,
              "A: /tick odpoví 200" in zelene(v), True)
    check("A2 zdroj conductora je na konci ČISTÝ (disk == HEAD)", sha(SRC), sha_hlavy(SRC))


# ═══════════════════════════════════════════════════════════════════════ A3 ══
def a3():
    print("\n--- A3: TVRDÍ testy TVAR i OBSAH? (KOPIE testu s PRÁZDNOU falešnou D1) ---")
    kod0, v0 = mer_tick()
    check("A3 KONTROLA: živý test tiku → exit 0 a 0 červených",
          (kod0, len(cervene(v0))), (0, 0))
    text = TEST_TIK.read_text(encoding="utf-8")
    kotva = "    zapis(sql);\n    // ── P27 / Úkol B1: ČTECÍ ENDPOINTY"
    if text.count(kotva) != 1:
        nezmereno_zapis("A3", "kotva pro prázdnou falešnou D1 je v testu %d×" % text.count(kotva))
        return
    shutil.copyfile(TEST_TIK, KOPIE_TESTU)
    from _mutace import mutuj  # noqa: PLC0415
    try:
        with mutuj(KOPIE_TESTU, kotva,
                   "    zapis(sql);\n    if (true) return { results: [] };  // P29/A3\n"
                   "    // ── P27 / Úkol B1: ČTECÍ ENDPOINTY") as m:
            check("A3 mutace se provedla (hash před != po)",
                  m.hash_pred != m.hash_po_mutaci, True)
            kod, v = cmd([NODE, str(KOPIE_TESTU)], timeout=3600)
    except ValueError as e:
        nezmereno_zapis("A3 kopie testu s prázdnou falešnou D1", str(e))
        return
    zapis_doklad("p29-a3-prazdna-d1-vystup.txt", v)
    cr, zl = cervene(v), zelene(v)
    print("      s PRÁZDNOU falešnou D1: čítač=%s, červených=%d, zelených=%d"
          % (citac(v), len(cr), len(zl)))
    for pref, _, _ in ZARAZKY:
        cil = [x for x in cr if skupina(x) == pref]
        # ⚠ TVAROVÁ kontrola má u `/health` JINÉ ZNĚNÍ než u ostatních šesti:
        # naměřeno 9. 10. 2026 — skupina `X:` žádné „odpoví 200“ nemá, její tvar
        # nesou `ok: true` a „jde BEZ tajemství“. Kdo hledá jen „odpoví 200“,
        # hlásí u `/health` falešný nález (a to udělala první verze měřidla).
        tvary = [x for x in zl if skupina(x) == pref
                 and ("odpoví 200" in x or "ok: true" in x or "BEZ tajemství" in x)]
        check("A3 prázdná odpověď SHODÍ obsahové kontroly `%s:`" % pref, len(cil) >= 1, True)
        check("A3 a TVAROVÁ kontrola `%s:` zůstala ZELENÁ (TVAR přežil OBSAH)" % pref,
              len(tvary) >= 1, True)
        for x in cil[:2]:
            print("        červená: %s" % x[:115])
        for x in tvary[:2]:
            print("        ZELENÁ (tvar): %s" % x[:115])


# ═══════════════════════════════════════════════════════════════════════ A5 ══
def a5():
    print("\n--- A5: ROZSAH `ov-g` A KONTINUITA ID (vlastní počítadlo) ---")
    t = s59()
    radek_h = re.compile(r"^\|\s*\*\*(H\d+)\*\*\s*\|")
    zdroje = [HANDOFF] + sorted(
        p for p in (WS / "_archiv").glob("HANDOFF-*.md") if p.is_file())
    vlastni = {}
    for p in zdroje:
        vlastni[p.name] = len([l for l in p.read_text(encoding="utf-8", errors="replace")
                               .splitlines() if radek_h.match(l)])
    celkem = sum(vlastni.values())
    print("      vlastní počet řádků Hxx: %s = %d"
          % (", ".join("%s %d" % (k, v) for k, v in vlastni.items()), celkem))
    tv = tvrzeni(t, r"rozsah (\d+) řádků Hxx", "§59.5: rozsah 99 řádků Hxx")
    if tv:
        srovnej("A5 vlastní počet řádků Hxx", int(tv[0]), celkem)
    check("A5 živých zdrojů je víc než jeden (jinak by rozsah mohl být zúžený)",
          len(zdroje) > 1, True)
    kod, v = cmd([PY, str(OV_G)], timeout=1800)
    zapis_doklad("p29-a5-ovg-vystup.txt", v)
    check("A5 ov-g → exit 0 (žádné NEOVĚŘENO)", kod, 0)
    m = re.search(r"nálezů \(řádků tabulek Hxx\) CELKEM:\s*(\d+)", v)
    check("A5 brána hlásí TOTÉŽ číslo jako vlastní počítadlo",
          int(m.group(1)) if m else None, celkem)
    m2 = re.search(r"celkem mimo:\s*(\d+) řádků v (\d+) souborech", v)
    print("      brána: mimo živé zdroje %s" % str(m2.groups() if m2 else "NENALEZENO"))
    check("A5 rozsah MIMO živé zdroje je NENULOVÝ (zúžení by muselo být vidět)",
          (int(m2.group(1)) if m2 else 0) > 0, True)

    radky = KRONIKA.read_text(encoding="utf-8", errors="replace").splitlines()
    idcka = [int(mm.group(1)) for l in radky
             if (mm := re.match(r"^\|\s*\*\*(\d+)\*\*\s*\|", l))]
    diry = [n for n in range(1, (max(idcka) if idcka else 0) + 1) if n not in idcka]
    print("      kronika: řádků session=%d, id %s..%s, díry=%s"
          % (len(idcka), min(idcka) if idcka else "—", max(idcka) if idcka else "—",
             diry or "žádné"))
    check("A5 id řádků session jdou 1..N BEZ DĚR", diry, [])
    kod_k, v_k = cmd([PY, str(KRONIKA_K)], timeout=1800)
    check("A5 kronika-kontrola → exit 0 a SEDÍ", (kod_k, "SEDÍ" in v_k.upper()), (0, True))
    check("A5 kronika-kontrola VYPISUJE kontinuitu id (nová pojistka P28-E)",
          "chybějící id" in v_k, True)
    tv_k = tvrzeni(t, r"kronika-kontrola\.py`?\s*→\s*\*\*([A-ZÁ-Ž]+)\*\*",
                   "§59.1: kronika-kontrola → SEDÍ")
    if tv_k:
        srovnej("A5 tvrzení kronika-kontrola", tv_k[0], "SEDÍ" if "SEDÍ" in v_k.upper() else "NE")

    SCRATCH.mkdir(parents=True, exist_ok=True)
    obsah = KRONIKA.read_text(encoding="utf-8", errors="replace")
    kotva = "| **30** |"
    if obsah.count(kotva) == 1:
        fx = SCRATCH / "kronika-bez-radku.md"
        fx.write_bytes(obsah.replace(kotva, "| **31** |").encode("utf-8"))
        # ⚠ POZOR: `kronika-kontrola.py` bere cestu POZICIONÁLNĚ (`sys.argv[1]`),
        # NE přepínačem. Naměřeno 9. 10. 2026: `--kronika <cesta>` skončí
        # `CHYBA: --kronika neexistuje` a `exit 1` — tedy STEJNÝ verdikt jako
        # „našel chybějící id“. Kdo to nerozliší, má falešně zelenou kontrolu
        # (a to se stalo první verzi tohohle měřidla).
        kod_f, v_f = cmd([PY, str(KRONIKA_K), str(fx)], timeout=900)
        check("A5 fixtura NENÍ odmítnuta jako nečitelný vstup (jinak by spadla z jiného důvodu)",
              "neexistuje" in v_f, False)
        check("A5 FIXTURA kronika bez řádku 30 → exit != 0", kod_f != 0, True)
        check("A5 a POJMENUJE chybějící id 30 (ne že spadne z jiného důvodu)",
              "30" in v_f, True)
    else:
        nezmereno_zapis("A5 fixtura kroniky",
                        "kotva `| **30** |` je v kronice %d×" % obsah.count(kotva))
    prazdna = SCRATCH / "kronika-prazdna.md"
    prazdna.write_bytes("# prázdná kronika\n".encode("utf-8"))
    kod_p, v_p = cmd([PY, str(KRONIKA_K), str(prazdna)], timeout=900)
    check("A5 prázdná fixtura kroniky → exit != 0 (a je vidět, že se NEMĚŘILO)",
          (kod_p != 0, "neexistuje" in v_p), (True, False))

    # ⚠ Fixtury se NESMÍ jmenovat `handoff*` — `ov-g` skenuje `REPO.rglob("*.md")`
    # a každý soubor s tím jménem počítá do „mimo živé zdroje“. Naměřeno 9. 10. 2026:
    # fixtura `handoff-nevereno.md` zvedla rozsah z 139/7 na 140/8 a vypadalo to
    # jako změna projektu, ne měřidla.
    f1 = SCRATCH / "fixtura-nevereno.md"
    f1.write_bytes("| **H999** | testovaci nalez | NEOVĚŘENO |\n".encode("utf-8"))
    kod1, v1 = cmd([PY, str(OV_G), "--handoff", str(f1)], timeout=900)
    check("A5 fixtura s NEOVĚŘENO → exit 1", kod1 != 0, True)
    check("A5 a je to kvůli tomu nálezu (ne z jiného důvodu)", "H999" in v1, True)
    f2 = SCRATCH / "fixtura-prazdna.md"
    f2.write_bytes("# nic\n".encode("utf-8"))
    kod2, v2 = cmd([PY, str(OV_G), "--handoff", str(f2)], timeout=900)
    check("A5 PRÁZDNÁ fixtura → NEMĚŘENO (nula není úspěch)", "NEMĚŘENO" in v2, True)
    check("A5 a prázdná fixtura → exit 1", kod2 != 0, True)


# ═══════════════════════════════════════════════════════════════════════ A6 ══
def _fixtura_skill(jmeno, obsah):
    d = SCRATCH / "skills" / jmeno
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_bytes(obsah.encode("utf-8"))
    return d


def _over_skilly_fixtura():
    kod, v = cmd([PY, str(OVER_SKILLY)], timeout=900,
                 env={"FORGE_SKILLS": str(SCRATCH / "skills")})
    m = re.search(r"Cesty k nástrojům:\s*(\d+) zmínek,\s*(\d+) mrtvých", v)
    return kod, v, (int(m.group(1)), int(m.group(2))) if m else None


def a6():
    print("\n--- A6: OPRAVA B5 MĚŘÍ, CO TVRDÍ (fixtury přes FORGE_SKILLS) ---")
    t = s59()
    kod, v = cmd([PY, str(OVER_SKILLY)], timeout=1800)
    zapis_doklad("p29-a6-overskilly-vystup.txt", v)
    tv = tvrzeni(t, r"over-skilly\.py`?\s*→\s*\*\*(\d+) zmínek\*\*",
                 "§59.1 B5: over-skilly → 90 zmínek")
    m = re.search(r"Cesty k nástrojům:\s*(\d+) zmínek,\s*(\d+) mrtvých", v)
    dnes = (int(m.group(1)), int(m.group(2))) if m else None
    print("      živý běh: zmínek/mrtvých=%s, exit=%d" % (dnes, kod))
    if tv:
        srovnej("A6 over-skilly zmínky", int(tv[0]), dnes[0] if dnes else None)
    check("A6 over-skilly → exit 0 a 0 mrtvých cest", (kod, dnes[1] if dnes else None), (0, 0))
    tv2 = tvrzeni(t, r"mutační dvojče\s*\*\*(\d+)/(\d+)\s*→\s*(\d+)/(\d+)\*\*",
                  "§59.1 B5: mutační dvojče 8/0 → 17/0")
    kod_d, v_d = cmd([PY, str(SKILL_MUTACE)], timeout=3600)
    zapis_doklad("p29-a6-skill-mutace-vystup.txt", v_d)
    c = citac_obecny(v_d)
    if tv2:
        srovnej("A6 mutační dvojče (test-over-skilly)", (int(tv2[2]), int(tv2[3])), c)

    # NOVÝ TVAR CESTY (jádro B5): cesta v ``` bloku musí být VIDĚT a POČÍTAT SE
    # STEJNĚ jako táž cesta na řádku. Srovnává se DVĚMA fixturami — jedna s cestou
    # v bloku, druhá s toutéž cestou inline; rozdíl čítačů musí být NULA.
    SCRATCH.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(SCRATCH / "skills", ignore_errors=True)
    (SCRATCH / "skills").mkdir(parents=True, exist_ok=True)
    kod_0, v_0, c_0 = _over_skilly_fixtura()
    print("      fixtura 0: PRÁZDNÝ adresář skillů → čítač=%s (základ pro srovnání)" % (c_0,))
    shutil.rmtree(SCRATCH / "skills", ignore_errors=True)
    _fixtura_skill("p29-blok", "---\nname: p29-blok\ndescription: fixtura P29 (blok)\n---\n\n"
                               "text\n\n```\npython tools\\over-skilly.py\n```\n")
    kod_b, v_b, c_b = _over_skilly_fixtura()
    print("      fixtura A: cesta v ``` bloku → čítač=%s, exit=%d" % (c_b, kod_b))
    shutil.rmtree(SCRATCH / "skills", ignore_errors=True)
    _fixtura_skill("p29-inline", "---\nname: p29-inline\ndescription: fixtura P29 (inline)\n---\n\n"
                                 "text\n\npython tools\\over-skilly.py\n")
    kod_i, v_i, c_i = _over_skilly_fixtura()
    print("      fixtura B: TÁŽ cesta inline → čítač=%s, exit=%d" % (c_i, kod_i))
    check("A6 cesta v ``` BLOKU se počítá STEJNĚ jako tatáž cesta na řádku "
          "(dřív byla neviditelná — jádro B5)", c_b, c_i)
    check("A6 a obě fixtury jsou ZELENÉ (počítá se to, ale nezabíjí)", (kod_b, kod_i), (0, 0))

    shutil.rmtree(SCRATCH / "skills", ignore_errors=True)
    _fixtura_skill("p29-mrtva", "---\nname: p29-mrtva\ndescription: fixtura P29 (mrtvá)\n---\n\n"
                                "```\npython tools\\p29-tento-neni.py\n```\n")
    kod_m, v_m, c_m = _over_skilly_fixtura()
    print("      fixtura C: MRTVÁ cesta v bloku → čítač=%s, exit=%d" % (c_m, kod_m))
    check("A6 MRTVÁ cesta v ``` BLOKU bránu SHODÍ (tvar se nejen počítá, ale i měří)",
          kod_m != 0, True)

    shutil.rmtree(SCRATCH / "skills", ignore_errors=True)
    _fixtura_skill("p29-stary", "---\nname: p29-stary\ndescription: fixtura P29 (starý tvar)\n---\n\n"
                                "text `tools\\over-skilly.py` text\n")
    kod_s, v_s, c_s = _over_skilly_fixtura()
    print("      fixtura D: STARÝ tvar (backtick) → čítač=%s, exit=%d" % (c_s, kod_s))
    check("A6 STARÝ TVAR se nezhoršil — TÁŽ cesta se počítá stejně jako v bloku",
          c_s, c_b)
    if c_0 and c_b and c_s:
        check("A6 každá z fixtur A/D přidá PRÁVĚ 1 zmínku proti prázdnému adresáři "
              "(bez toho by rovnost čítačů nic neznamenala)",
              (c_b[0] - c_0[0], c_s[0] - c_0[0]), (1, 1))
    else:
        nezmereno_zapis("A6 základ čítače", "čítač fixtury se nepodařilo přečíst")

    # DEKLAROVANÁ VÝJIMKA NESMÍ PROSÁKNOUT do jiného skillu.
    # Bere se DOSLOVNÁ cesta z výjimek skillu `vision` (`tools\vision.py`) a dá se
    # do skillu JINÉHO: klíč výjimky je (jméno skillu, cesta), takže tam platit
    # NESMÍ — jinak by výjimka byla plošná a brána by nad cizím textem mlčela.
    shutil.rmtree(SCRATCH / "skills", ignore_errors=True)
    _fixtura_skill("p29-vyjimka", "---\nname: p29-vyjimka\ndescription: fixtura P29 (výjimka)\n---\n\n"
                                  "text\n\n```\npython tools\\vision.py\n```\n")
    kod_v, v_v, c_v = _over_skilly_fixtura()
    print("      fixtura: `tools\\vision.py` v JINÉM skillu → čítač=%s, exit=%d" % (c_v, kod_v))
    check("A6 deklarovaná výjimka NEPROSÁKNE do jiného skillu (brána ji tam SHODÍ)",
          (kod_v != 0, (c_v[1] if c_v else 0) >= 1), (True, True))


# ═══════════════════════════════════════════════════════════════════════ A7 ══
def a7():
    print("\n--- A7: INVENTÁŘ → g3 → validate-all (V TOMTO POŘADÍ, nic mezi tím) ---")
    kod_i, v_i = cmd([PY, str(NEANGL), "--json", str(INVENTAR)], timeout=3600)
    check("A7 inventář přegenerován (exit 0)", kod_i, 0)
    kod_g, v_g = cmd([PY, str(G3)], timeout=3600)
    kod_v, v_v = cmd([NODE, str(VALIDATE)], timeout=3600)
    MER["g3"] = (kod_g, v_g)
    MER["validate"] = (kod_v, v_v)
    zapis_doklad("p29-a7-g3-vystup.txt", v_g)
    zapis_doklad("p29-a7-validate-vystup.txt", v_v)
    t = s59()

    m = re.search(r"registr zapsán:.*?\((\d+) bran", v_g)
    bran = int(m.group(1)) if m else None
    tv = tvrzeni(t, r"g3 →\s*(\d+) bran", "§59.3: g3 → 49 bran")
    if tv:
        srovnej("A7 počet bran g3", int(tv[0]), bran)
    mn = re.search(r"NEDEKLAROVANÝCH (\d+):", v_g)
    nedekl = int(mn.group(1)) if mn else None
    jmena = re.findall(r"NEOČEKÁVANÝ:\s*([^\n→]+?)\s*→\s*exit=(\d+)", v_g)
    print("      g3: %s bran, exit=%d, nedeklarovaných exitů=%s, jména=%s"
          % (bran, kod_g, nedekl, [n.strip() for n, _ in jmena] or "—"))
    check("A7 g3 hlásí POJMENOVANÉ stavy (každý nedeklarovaný exit má jméno)",
          all(bool(n.strip()) for n, _ in jmena), True)
    check("A7 počet nedeklarovaných exitů = počet POJMENOVANÝCH",
          nedekl, len(jmena))
    check("A7 inventář je po přegenerování ČERSTVÝ (n1-over-inventar NENÍ v chybách)",
          any("n1-over-inventar" in n for n, _ in jmena), False)
    problemy = 0 if "VŠE V POŘÁDKU" in v_v else None
    if problemy is None:
        mv = re.search(r"NALEZENO (\d+) PROBLÉM", v_v)
        problemy = int(mv.group(1)) if mv else None
    zname = re.findall(r"^\s*CHYBA (.+)$", v_v, re.M)
    print("      validate-all: %s problémů: %s" % (problemy, [x[:70] for x in zname]))
    check("A7 každý problém validate-all je POJMENOVANÝ (ne jen číslo)",
          len(zname) == (problemy or 0), True)
    tvp = tvrzeni(t, r"validate-all.{0,60}?\*\*(\d+) problémy\*\*",
                  "§59.2/59.3: validate-all → 2 problémy")
    if tvp:
        srovnej("A7 validate-all problémy", int(tvp[0]), problemy, "stav",
                "dnešní problémy: %s" % "; ".join(x[:60] for x in zname))

    # OTISK VSTUPŮ — dvě nezávislé kontroly
    try:
        inv = json.loads(INVENTAR.read_text(encoding="utf-8"))
        o = inv.get("otisk_vstupu") or {}
        repa = o.get("repozitare") or []
        pocty = {r.get("repo"): r.get("souboru") for r in repa}
        print("      inventář: souborů=%s, repa=%s, vynecháno=%s"
              % (o.get("souboru"), pocty, o.get("otisk_vynechane")))
        check("A7 otisk počítá OBĚ repa (jinak by změna ve hře nebyla vidět)",
              len(repa) >= 2 and all((r.get("souboru") or 0) > 0 for r in repa), True)
        # 1) přepočet z ULOŽENÝCH záznamů (nezávisle na implementaci nástroje)
        h = hashlib.sha256()
        for r in repa:
            h.update(("%s\n" % r.get("repo")).encode("utf-8"))
            for z in r.get("soubory") or []:
                h.update(("%s|%s|%s\n" % (z.get("cesta"), z.get("bajtu"),
                                          z.get("sha256"))).encode("utf-8"))
        check("A7 uložený otisk = PŘEPOČET z uložených záznamů (záznam je konzistentní)",
              h.hexdigest(), o.get("sha256"))
        # 2) otisk z DNEŠNÍCH BAJTŮ (nástroj to umí přes --otisk) = uložený
        kod_o, v_o = cmd([PY, str(NEANGL), "--otisk"], timeout=1800)
        try:
            dnes_o = json.loads(v_o.strip().splitlines()[-1]).get("sha256")
        except Exception:  # noqa: BLE001
            dnes_o = None
        check("A7 otisk z DNEŠNÍCH bajtů (--otisk) = uložený (inventář je čerstvý)",
              dnes_o, o.get("sha256"))
    except Exception as e:  # noqa: BLE001
        nezmereno_zapis("A7 otisk inventáře", str(e)[:200])


# ═══════════════════════════════════════════════════════════════════════ A4 ══
def a4():
    print("\n--- A4: SEDÍ ČÍSLA V §59? (každý tvrzený čítač znovu spuštěn) ---")
    t = s59()
    if not t:
        nezmereno_zapis("A4", "§59 v HANDOFF.md není")
        return

    kod_t, v_t = mer_tick()
    tv = tvrzeni(t, r"test-tick-offline (\d+)/(\d+)", "§59.3: test-tick-offline 205/0")
    if tv:
        srovnej("A4 test-tick-offline", (int(tv[0]), int(tv[1])), citac(v_t))
    check("A4 test-tick-offline → exit 0", kod_t, 0)

    kod_h, v_h = cmd([PY, str(HANDOFF_K)], timeout=1800)
    m = re.search(r"kontrolovaných klíčů:\s*(\d+)", v_h)
    m2 = re.search(r"nalezených:\s*(\d+)", v_h)
    if m and m2:
        print("      handoff-kontrola-uplnost: %s/%s klíčů" % (m.group(1), m2.group(1)))
        check("A4 handoff-kontrola-uplnost: NIC nezmizelo", m.group(1), m2.group(1))
    check("A4 handoff-kontrola-uplnost → exit 0", kod_h, 0)

    kod_o, v_o = cmd([PY, str(OVER_DOK)], timeout=1800)
    dnes_o = citac_obecny(v_o)
    print("      over-dokumentaci: %s" % (dnes_o,))
    check("A4 over-dokumentaci → exit 0", kod_o, 0)
    tv = tvrzeni_v(r"over-dokumentaci\.py\s*->\s*(\d+)/(\d+)",
                   "zadání §2.3: over-dokumentaci → 64/0")
    if tv:
        srovnej("A4 over-dokumentaci", (int(tv[0]), int(tv[1])), dnes_o)

    kod_tm, v_tm = cmd([PY, str(TICK_MUTACE)], timeout=3600)
    zapis_doklad("p29-a4-tick-mutace-vystup.txt", v_tm)
    c_tm = citac(v_tm)
    mv = re.search(r"vrat:\s*(\d+)", v_tm)
    tv = tvrzeni_v(r"tick-mutace\.py\s*->\s*(\d+) vrat, (\d+)/(\d+)",
                   "zadání §2.3: tick-mutace → 20 vrat, 41/0")
    if tv:
        dnes = (mv.group(1) if mv else None, c_tm)
        print("      tick-mutace: vrat=%s, čítač=%s" % dnes)
        srovnej("A4 tick-mutace (vrat)", int(tv[0]), int(mv.group(1)) if mv else None)
        srovnej("A4 tick-mutace (čítač)", (int(tv[1]), int(tv[2])), c_tm)
    check("A4 tick-mutace → exit 0", kod_tm, 0)

    kod_k, v_k = cmd([PY, str(OBNOV_KRONIKU), "--kontrola"], timeout=1800)
    c_k = citac_obecny(v_k)
    tv = tvrzeni(t, r"p28-obnov-kroniku\.py`?\s*→\s*\*\*(\d+) kontrol, (\d+) chyb\*\*",
                 "§59.1 D: p28-obnov-kroniku → 9/0")
    if tv:
        srovnej("A4 p28-obnov-kroniku --kontrola", (int(tv[0]), int(tv[1])), c_k)
    check("A4 p28-obnov-kroniku --kontrola → exit 0", kod_k, 0)

    # ── ŽIVÁ SLUŽBA (JEN ČTENÍ) ────────────────────────────────────────────
    z = mer_ziva()
    h = z.get("health") or {}
    print("      živě /health: status=%s ok=%s ready=%s running=%s games=%s"
          % (h.get("status"), h.get("ok"), h.get("ready"), h.get("running"), h.get("games")))
    check("A4 živě /health bez tajemství → 200", h.get("status"), 200)
    check("A4 živě /health nese stav CÍLE (`targets`)", (h.get("cilu") or 0) >= 1, True)
    ch = z.get("chranene") or {}
    check("A4 živě: všech 6 chráněných endpointů BEZ tajemství → 401",
          sorted({v.get("bez") for v in ch.values()}), [401])
    check("A4 živě: všech 6 chráněných endpointů S tajemstvím → 200",
          sorted({v.get("s") for v in ch.values()}), [200])
    tv = tvrzeni(t, r"ok=(\w+) ready=(\d+) running=(\d+) games=(\d+)",
                 "§59.3: živá služba ok=true ready=2 running=0 games=1")
    if tv:
        tvr = (tv[0], int(tv[1]), int(tv[2]), int(tv[3]))
        dnes = (str(h.get("ok")).lower(), h.get("ready"), h.get("running"), h.get("games"))
        srovnej("A4 živě /health", tvr, dnes, "stav",
                "záznam je okamžik zápisu (8. 10. 19:1x); služba se posunula")
    rm = z.get("roadmap") or {}
    q = z.get("queue") or {}
    print("      živě /roadmap: %s řádků, stavy=%s, max pokusů=%s"
          % (rm.get("granul"), rm.get("stavy"), rm.get("max_pokusu")))
    print("      živě /queue: %s úloh, stavy=%s" % (q.get("uloh"), q.get("stavy")))
    tv = tvrzeni(t, r"/roadmap (\d+) granul\s+\((\w+) (\d+), (\w+) (\d+), (\w+) (\d+); max pokusů (\d+)\)",
                 "§59.3: /roadmap 22 granul (done 19, queued 2, blocked 1; max pokusů 5)")
    if tv:
        stavy = rm.get("stavy") or {}
        tvr = (int(tv[0]), int(tv[2]), int(tv[4]), int(tv[6]), int(tv[7]))
        dnes = (rm.get("granul"), stavy.get(tv[1]), stavy.get(tv[3]), stavy.get(tv[5]),
                rm.get("max_pokusu"))
        srovnej("A4 živě /roadmap (stav při zápisu §59.3)", tvr, dnes, "stav",
                "záznam je okamžik zápisu (8. 10. 19:1x); cache mezitím narostla")
    check("A4 živě: strop 8 NIKOHO NEBLOKUJE (max pokusů < 8)",
          (rm.get("max_pokusu") or 0) < 8, True)

    # ── KONTRAKT ROADMAPY (vlastním výpočtem) ──────────────────────────────
    k = mer_kontrakt()
    if k.get("soubor"):
        s = k["soubor"]
        print("      soubor roadmapy hry: %d granul" % s["celkem"])
        for klic, popis, vzor in (
            ("bez_size_lines", "bez `size_lines`", r"\*\*(\d+)/(\d+)\*\* granul bez `size_lines`"),
            ("bez_model", "bez `model`", r"\*\*(\d+)/(\d+)\*\* bez `model`"),
            ("strong", "`model: strong`", r"\(a \*\*(\d+)/(\d+)\*\* je `strong`"),
            ("bez_acceptance", "bez `acceptance`", r"(\d+)/(\d+) bez `acceptance`"),
        ):
            tv = tvrzeni(t, vzor, "§59.6: %s" % popis)
            if tv:
                srovnej("A4 kontrakt %s" % popis, (int(tv[0]), int(tv[1])),
                        (len(s[klic]), s["celkem"]), "stav")
    else:
        nezmereno_zapis("A4 kontrakt roadmapy", k.get("chyba") or "neznámá chyba")

    # ── OSIŘELÉ ŘÁDKY CACHE + ÚLOHY NA NEEXISTUJÍCÍ GRANULI ────────────────
    rows = mer_rows()
    if rows.get("chyba"):
        nezmereno_zapis("A4 osiřelé řádky cache", rows["chyba"])
    elif k.get("soubor"):
        holy = lambda x: re.sub(r"^[^/]+/", "", str(x or ""))  # noqa: E731
        v_souboru = set(k["soubor"]["vsechna_id"])
        cache = rows.get("roadmap") or []
        fronta = rows.get("queue") or []
        osir = [r for r in cache if holy(r.get("item_id")) not in v_souboru]
        chybejici = [i for i in v_souboru if i not in {holy(r.get("item_id")) for r in cache}]
        print("      cache D1: %d řádků; OSIŘELÉ (v cache, v souboru NE): %d → %s"
              % (len(cache), len(osir),
                 [(r.get("item_id"), r.get("status"), r.get("task_id")) for r in osir]))
        print("      V SOUBORU, ale NE v cache: %d %s" % (len(chybejici), chybejici))
        task_na_grain = {r.get("task_id"): holy(r.get("item_id"))
                         for r in cache if r.get("task_id") is not None}
        mimo = [(t.get("id"), t.get("status"), t.get("attempts"), task_na_grain.get(t.get("id")))
                for t in fronta if task_na_grain.get(t.get("id")) not in (None, *v_souboru)]
        print("      úlohy na granule, které V SOUBORU NEJSOU: %d → %s" % (len(mimo), mimo))
        tv = tvrzeni(t, r"cache má \*\*(\d+) osiřelých\*\*", "§59.6: cache má 5 osiřelých")
        if tv:
            srovnej("A4 osiřelé řádky cache", int(tv[0]), len(osir), "stav",
                    "osiřelé: %s" % [r.get("item_id") for r in osir])

    _a4_behy(t)


def _a4_behy(t):
    print("\n      ── BĚHY ÚLOH #240–#243 (sonda páruje podle ID ÚLOHY v názvu) ──")
    if not SONDA_ULOHY.is_file():
        nezmereno_zapis("A4 běhy #240–#243", "sonda p29-sonda-ulohy.mjs není")
        return
    kod, v = cmd([NODE, str(SONDA_ULOHY), "60", "238,239,240,241,242,243"], timeout=1800)
    zapis_doklad("p29-a4-behy-uloh-vystup.txt", v)
    try:
        d = json.loads(v)
    except ValueError:
        nezmereno_zapis("A4 běhy #240–#243", "výstup sondy není JSON (exit=%d)" % kod)
        return
    if d.get("chyba"):
        nezmereno_zapis("A4 běhy #240–#243", d["chyba"])
        return
    nalezeno = d.get("behy") or []
    print("      v posledních %d bězích nalezeno běhů úloh %s: %d"
          % (d.get("nacteno_behu"), d.get("hledano_uloh"), len(nalezeno)))
    for b in nalezeno:
        print("        úloha #%-4s run#%-5s %-9s RTL=%-2s TPM=%-2s RTLarge=%-2s dvojprefix=%-2s %s"
              % (b["uloha"], b["run_number"], b["conclusion"], b.get("ratelimit"),
                 b.get("tpm"), b.get("rtl"), b.get("dvojprefix"), b.get("created_at")))
    tv = tvrzeni(t, r"Poslední \*\*(\d+) běhy\*\* agenta \(`#(\d+)`–`#(\d+)`\) skončily `failure`",
                 "§59.6: poslední 4 běhy (#240–#243) skončily failure")
    if not tv:
        return
    od, do = int(tv[1]), int(tv[2])
    cil = [b for b in nalezeno if od <= b["uloha"] <= do]
    fail = [b for b in cil if b["conclusion"] == "failure"]
    rtl = [b for b in fail if (b.get("ratelimit") or 0) > 0]
    print("      tvrzení: posledních %s běhů #%d–#%d = failure a VŠECHNY na RateLimitError"
          % (tv[0], od, do))
    srovnej("A4 počet běhů #%d–#%d, které skončily failure" % (od, do),
            "%s z %s úloh" % (tv[0], do - od + 1),
            "%d z %d nalezených" % (len(fail), len(cil)), "stav")
    srovnej("A4 z nich s `litellm.RateLimitError`" % (),
            "%d/%d" % (len(fail), len(fail)), "%d/%d" % (len(rtl), len(fail)), "stav",
            "selhavší kroky: %s" % ", ".join(
                "#%s:%s" % (b["uloha"], ",".join(b.get("selhale_kroky") or ["?"])[:38])
                for b in fail[:8]))


# ═══════════════════════════════════════════════════════════════════════ main ══
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jen", default=None, help="seznam etap, např. A1,A5")
    ap.add_argument("--plne", action="store_true", help="i A1 (drahé kontramutace)")
    ap.add_argument("--vystup", default=None)
    args = ap.parse_args()

    vystup = pathlib.Path(args.vystup) if args.vystup else ANALYZA / "p29-a-overeni-vystup.txt"
    etapy = [x.strip().upper() for x in
             (args.jen if args.jen else
              ("A1,A2,A3,A5,A6,A7,A4" if args.plne else "A2,A3,A5,A6,A7,A4")).split(",")]
    sys.stdout = Tee(vystup)
    print("=" * 88)
    print("P29/A — NEZÁVISLÉ PŘEMĚŘENÍ PRÁCE P28 VLASTNÍM POSTUPEM (A1–A7)")
    print("=" * 88)
    print("  datum (z hodin): %s" % time.strftime("%Y-%m-%d %H:%M:%S %z"))
    print("  pořadí běhu: %s" % ", ".join(etapy))
    print("  doklad: %s" % vystup.name)
    print("  ⚠ A1 se pouští JEN s --plne (drahé kontramutace měřidla P28)")
    for e in etapy:
        f = globals().get(e.lower())
        if f is None:
            print("  ??    etapa %s neexistuje" % e)
            continue
        print("\n" + "─" * 88)
        try:
            f()
        except Exception as ex:  # noqa: BLE001
            import traceback  # noqa: PLC0415
            tb = traceback.format_exc().strip().splitlines()
            print("      TRACEBACK: %s" % " | ".join(x.strip() for x in tb[-3:]))
            nezmereno_zapis("etapa %s" % e, "výjimka %s: %s" % (type(ex).__name__, str(ex)[:200]))
    print("\n" + "=" * 88)
    print("POJMENOVANÉ ROZDÍLY PROTI §59 (nejsou to vady kódu): %d" % len(ROZDILY))
    for p, tt, n, dr, pozn in ROZDILY:
        print("  · %-48s tvrzeno=%r naměřeno=%r  [%s]" % (p[:48], tt, n, dr))
        if pozn:
            print("      %s" % pozn[:150])
    print("\nNEZMĚŘENO (není nula a není zelená): %d" % len(nezmereno))
    for x in nezmereno:
        print("  · %s" % x[:170])
    print("=" * 88)
    print("VÝSLEDEK: %d kontrol, %d chyb (z toho %d pojmenovaných ROZDÍLŮ, %d NEZMĚŘENO)"
          % (kontrol, chyb, len(ROZDILY), len(nezmereno)))
    print("=" * 88)
    sys.stdout.flush()
    return 0 if chyb == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
