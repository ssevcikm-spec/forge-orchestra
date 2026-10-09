# -*- coding: utf-8 -*-
r"""P31 — VLASTNÍ PŘEMĚŘENÍ PRÁCE P30 (Úkol A zadání P31).

CO TENHLE DOKLAD DĚLÁ (a čím se liší od měřidel P30):
  * **Čísla NEČTE Z HLAVY** — každé tvrzení se nejdřív **PŘEČTE Z DOKUMENTU**
    (`HANDOFF.md` **§61** = záznam P30) a vypíše se **okno, které vzor trefil**
    (pravidlo „brána může číst citaci místo tvrzení").
  * **Rozlišuje TVRZENÍ O MĚŘIDLE a TVRZENÍ O STAVU** — čítač brány musí sedět
    (`CHYBA`); číslo o živém stavu se posunout smí (`ROZDÍL` s vysvětlením).
  * **Umí selhat** — `_analyza/p31-mutace.py` vrací vady do OPRAV (C1/C2)
    a ověřuje diferenciál; sekce A1 tu dělá VLASTNÍ diferenciál měřidla P30.
  * **Sekce A4 (dávka dokladů) se pouští JEN `--jen A4`** (~35 min) — běží
    v ní `p20-d-doklady.py`, který sám spouští ostatní doklady.

SEKCE (zadání P31 §2.1):
  A1  umí měřidlo P30 spadnout? (jeho běh + VLASTNÍ diferenciál)
  A2  nasazení TŘEMI kroky (push → deploy na commitu → živý artefakt)
  A3  sedí čísla z §61? (každý tvrzený čítač znovu spuštěn)
  A4  H130: dávka dokladů už NEPŘEPISUJE dokumenty (pojistka + hash)
  A5  H111: strop granule vs. zámek (D1 sonda, jen SELECT)
  A6  H124: uklidí se měřidlo P29 po sobě?
  A7  nic se nerozbilo (záznamy, kronika, handoff, ov-g)

Použití:
    python _analyza\p31-a-overeni.py                 # levné kontroly (§61)
    python _analyza\p31-a-overeni.py --plne          # i drahé brány a živé sondy
    python _analyza\p31-a-overeni.py --jen A6        # jedna sekce
    python _analyza\p31-a-overeni.py --jen A4        # dávka dokladů (~35 min)

⚠ `--plne` VOLÁ `POST /tick` (sekce A2) = ZÁSAH DO ŽIVÉHO STAVU (dispatchuje práci
a pálí kvótu). Bez `--plne` se tik nevolá a sekce to řekne jako NEZMĚŘENO.
"""

import argparse
import hashlib
import os
import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
TOOLS = WS / "tools"
GIT = TOOLS / "git.cmd"
SONDA_DEPLOY = ANALYZA / "p30-sonda-deploy.mjs"
SONDA_STAV = ANALYZA / "p30-sonda-stav.mjs"
SONDA_D1 = ANALYZA / "p30-sonda-d1.mjs"
P20D = ANALYZA / "p20-d-doklady.py"
P30A = ANALYZA / "p30-a-overeni.py"
DOKLAD_STAV = ANALYZA / "p31-stav-vystup.txt"
DOKLAD_D1 = ANALYZA / "p31-d1-vystup.txt"

ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj  # noqa: E402

_vystup = []


def p(radek=""):
    print(radek)
    _vystup.append(radek)


def spust(cmd, timeout=1800, env=None):
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


def oddil(vzor_nadpisu):
    """(text, první_řádek, poslední_řádek) oddílu úrovně `##` (i s pododdíly)."""
    radky = HANDOFF.read_text(encoding="utf-8").splitlines()
    start = next((i for i, r in enumerate(radky) if re.match(vzor_nadpisu, r)), None)
    if start is None:
        raise SystemExit("CHYBA: oddíl %r v HANDOFF.md NENÍ — měřidlo by měřilo jinam"
                         % vzor_nadpisu)
    konec = len(radky)
    for j in range(start + 1, len(radky)):
        if re.match(r"^##\s", radky[j]):
            konec = j
            break
    return "\n".join(radky[start:konec]), start + 1, konec


def tvrzeni(text, vzory):
    """Zkusí vzory popořadě; vrátí (čísla, okno, použitý vzor) nebo (None, None, None)."""
    for v in vzory:
        m = re.search(v, text)
        if m:
            okno = text[max(0, m.start() - 70): m.end() + 70].replace("\n", " / ")
            return tuple(m.groups()), okno, v
    return None, None, None


def citac_text(t):
    """Poslední čítač „VÝSLEDEK: N kontrol, M chyb“ v textu."""
    vse = list(re.finditer(r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb", t))
    return (vse[-1].group(1), vse[-1].group(2)) if vse else None


def citac_dokladu(cesta):
    cesta = pathlib.Path(cesta)
    if not cesta.is_file():
        return None
    return citac_text(cesta.read_text(encoding="utf-8", errors="replace"))


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


def git(*args, timeout=300):
    return spust([str(GIT), "-C", str(WS), *args], timeout=timeout)


# ── A1 ──────────────────────────────────────────────────────────────────────
def sekce_A1(m, plne, cache):
    p("")
    p("── A1: UMÍ MĚŘIDLO P30 SPADNOUT? (jeho běh + VLASTNÍ diferenciál) ──")
    if not plne:
        m.nezmereno("A1 `p30-mutace.py` i vlastní diferenciál — drahé (spusť --plne)")
        return
    kod, out, tr = spust([sys.executable, str(ANALYZA / "p30-mutace.py")], timeout=2400)
    c = citac_text(out)
    if c:
        cache["p30-mutace"] = c
    text61, _, _ = oddil(r"^##\s+61\.")
    cit, okno, _ = tvrzeni(text61, [r"p30-mutace\s*\*{0,2}(\d+)/(\d+)"])
    p("            dokument tvrdí %s · okno: …%s…" % (cit, okno))
    m.ok_(kod == 0, "A1 `p30-mutace.py` exit=%d (%.0f s)" % (kod, tr))
    m.ok_(c is not None and cit is not None and c == cit,
          "A1 mutační důkaz měřidla P30: tvrzeno %s, naměřeno %s" % (cit, c))

    # ── VLASTNÍ diferenciál měřidla P30 (ne opis jeho M1) ───────────────────
    text = HANDOFF.read_text(encoding="utf-8")
    # ⚠ P32 (H145): kotva MUSÍ BÝT V DOKUMENTU JEDNOZNAČNÁ. Naměřeno 9. 10. 2026
    # v P32: P31 do svého záznamu **§62 citovala** přesně `test-tick-offline → 215/0`
    # → původní kotva byla **2×**, `mutuj` spadl na `ValueError` a VLASTNÍ
    # diferenciál se stal `NEZMĚŘENO` (a `p30-mutace.py` tím přišlo o celý běh).
    # Je to táž past jako H131, jen na kotvě DOKUMENTU: kotva proto nese i okolní
    # text z §60 (záznam, který se needituje).
    kotva = "test-tick-offline → 215/0 (bylo 205/0) · tick-mutace → 20 vrat, 41/0"
    kotva_nova = kotva.replace("215/0", "216/0")
    k_ok = text.count(kotva) == 1
    m.ok_(k_ok, "A1 kotva %r je v HANDOFF.md právě 1× (%d×)" % (kotva, text.count(kotva)))
    text_mer = P30A.read_text(encoding="utf-8")
    RADEK_ROZCHOD = ('m.ok_(False, f"A3 {jmeno}: ROZCHOD — dokument {cit} vs '
                     'naměřeno {hodnoty}")')
    RADEK_WS = "WS = pathlib.Path(__file__).resolve().parents[1]"
    osl_ok = text_mer.count(RADEK_ROZCHOD) == 1 and text_mer.count(RADEK_WS) == 1
    m.ok_(osl_ok, "A1 oslabovaný řádek i řádek s `WS` jsou v měřidle P30 právě 1×")
    if not (k_ok and osl_ok):
        m.nezmereno("A1 vlastní diferenciál — chybí jednoznačná kotva nebo oslabení")
        return
    scratch = ANALYZA / "tick-scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    osl = scratch / "p31-oslabene-a3.py"
    osl_text = text_mer.replace(RADEK_ROZCHOD, 'm.ok_(True, "OSLABENO (P31)")')
    osl_text = osl_text.replace(RADEK_WS, 'WS = pathlib.Path(r"%s")' % WS)
    osl.write_bytes(osl_text.encode("utf-8"))

    def beh(cesta, jmeno):
        return spust([sys.executable, str(cesta), "--jen", "A3",
                      "--vystup", str(ANALYZA / jmeno)], timeout=1200)

    k0, _, _ = beh(P30A, "p31-a1-zivy-vystup.txt")
    m.ok_(k0 == 0, "A1-a ŽIVÉ měřidlo P30 nad živým dokumentem → exit 0")
    k1, _, _ = beh(osl, "p31-a1-oslabene-zdrave-vystup.txt")
    m.ok_(k1 == 0, "A1 POJISTKA: oslabená kopie ve zdravém stavu projde (exit=%d)" % k1)
    # ⚠ P32 (H145): dvojznačná kotva NESMÍ SHODIT CELOU ETAPU — dnes se hlásí
    # pojmovanou chybou a zbytek A1 (úklid oslabené kopie) doběhne.
    try:
        with mutuj(HANDOFF, kotva, kotva_nova) as mut:
            p("            kotva %d× · %s → %s" % (mut.pocet_vyskytu, mut.hash_pred[:12],
                                                   mut.hash_po_mutaci[:12]))
            k2, o2, _ = beh(P30A, "p31-a1-mutant-vystup.txt")
            k3, _, _ = beh(osl, "p31-a1-mutant-oslabene-vystup.txt")
        m.ok_(k2 == 1, "A1-b MUTANTNÍ dokument + živé měřidlo → exit 1 (spadlo)")
        m.ok_(("ROZCHOD" in o2) and ("test-tick-offline" in o2),
              "A1-b a spadlo NA KONTROLE, která to číslo čte (ROZCHOD `test-tick-offline`)")
        m.ok_(k3 == 0, "A1-c MUTANTNÍ dokument + OSLABENÉ měřidlo → exit 0 "
                       "(červená šla z TOHO porovnání, ne odjinud)")
        m.ok_(mut.hash_po_navratu == mut.hash_pred, "A1 HANDOFF.md vrácen bajt na bajt")
    except ValueError as e:
        m.ok_(False, "A1 diferenciál NELZE provést (dvojznačná kotva): %s" % str(e)[:130])
    osl.unlink(missing_ok=True)
    m.ok_(not osl.exists(), "A1 oslabená kopie měřidla je smazaná")
    p("            (doklady: p31-a1-*-vystup.txt)")


# ── A2 ──────────────────────────────────────────────────────────────────────
def sekce_A2(m, plne):
    p("")
    p("── A2: NASAZENÍ TŘEMI KROKY (push → deploy na SPRÁVNÉM commitu → živý artefakt) ──")
    text61, l0, l1 = oddil(r"^##\s+61\.")
    p("            okno dokumentu: HANDOFF.md řádky %d–%d (%d znaků)" % (l0, l1, len(text61)))

    kod, out, _ = git("rev-parse", "HEAD")
    head = out.strip()
    kod2, out2, tr2 = git("ls-remote", "origin", "refs/heads/main")
    remote = out2.split()[0].strip() if out2.split() else ""
    p("            HEAD=%s · ls-remote=%s (%.0f s)" % (head[:8], remote[:8], tr2))
    m.ok_(kod == 0 and kod2 == 0, "A2-1 `rev-parse` i `ls-remote` proběhly (exit 0/0)")
    m.ok_(head == remote and head != "", "A2-1 push DORAZIL: `origin/main` == HEAD")

    cit, okno, _ = tvrzeni(text61, [
        r"deploy\.yml`?\s*\*{0,2}(?:běh\s*)?#(\d+)\*{0,2}\s*na\s*`?([0-9a-f]{7,40})`?"])
    if cit is None:
        m.ok_(False, "A2-2 v §61 se NENAŠEL běh `deploy.yml` na commitu "
                     "(kontrola by se tiše přeskočila)")
    else:
        p("            dokument tvrdí: deploy.yml #%s na `%s` · okno: …%s…"
          % (cit[0], cit[1], okno))
        kod, out, tr = spust(["node", str(SONDA_DEPLOY), cit[1]], timeout=300)
        uspech = re.search(r"#(\d+) na %s je completed/success" % cit[1][:7], out)
        m.ok_(kod == 0, "A2-2 sonda deploy.yml na commitu %s → exit 0 (%.0f s)"
              % (cit[1][:8], tr))
        m.ok_(bool(uspech), "A2-2 a běh je `completed/success` na TOM commitu: %s"
              % (uspech.group(0) if uspech else "—"))

    if not plne:
        m.nezmereno("A2-3 živý artefakt (`POST /tick` pojmenuje, co přeskočil) — spusť --plne")
        return
    p("            ⚠ VOLÁM `POST /tick` (--plne): MĚNÍ STAV, dispatchuje práci a pálí kvótu")
    kod, _, tr = spust(["node", str(SONDA_STAV), str(DOKLAD_STAV.relative_to(WS)), "--tik"],
                       timeout=300)
    m.ok_(kod == 0, "A2-3 sonda živé služby (s tikem) → exit 0 (%.0f s)" % tr)
    m.ok_(DOKLAD_STAV.is_file(), "A2-3 sonda zapsala doklad %s" % DOKLAD_STAV.name)
    if not DOKLAD_STAV.is_file():
        return
    t = DOKLAD_STAV.read_text(encoding="utf-8", errors="replace")
    osirele = [int(x) for x in re.findall(r'"osirelych_radku":\s*(\d+)', t)]
    zpravy = re.findall(r'"message":\s*"([^"]{0,400})"', t)
    p("            osiřelých řádků v odpovědích: %s" % osirele)
    for z in zpravy[:2]:
        p("            tik: %s" % z[:220])
    m.ok_(bool(osirele) and all(x == 0 for x in osirele),
          "A2-3 `/tasks/cleanup {dry_run}` → osiřelých 0 (nový kód uklidil: bylo 5)")
    # ⚠ TVAR ZPRÁVY JE STAV, NE MĚŘIDLO (naměřeno 9. 10. 2026, 13:12): seznam
    # `v cooldownu N úloh` se připojuje JEN když nějaké úlohy v cooldownu jsou;
    # s prázdným seznamem zpráva končí „roadmapa je hotová (nebo čeká na
    # závislosti / cooldown)“ — a to je TAKÉ text z opravy B6. Měří se proto, že
    # zpráva POJMENOVÁVÁ důvod; kdyby se vázala na konkrétní seznam, byl by
    # výsledek falešně červený kvůli stavu (přesně to se v prvním běhu stalo).
    pojmenovava = any(re.search(r"v cooldownu\s+\d+\s+úloh", z) for z in zpravy)
    novy_tvar = any("nebo čeká na závislosti / cooldown" in z for z in zpravy)
    m.ok_(pojmenovava or novy_tvar,
          "A2-3 tik POJMENOVÁVÁ, co přeskočil (text z B6; `v cooldownu`: %s)"
          % ("ano" if pojmenovava else "dnes prázdný seznam"))
    if not pojmenovava:
        p("            (poznámka: `v cooldownu N úloh` se dnes neobjevilo — seznam "
          "cooldownu je prázdný; to je STAV, ne rozchod)")


# ── A3 ──────────────────────────────────────────────────────────────────────
def sekce_A3(m, plne, cache):
    p("")
    p("── A3: SEDÍ ČÍSLA Z §61? (tvrzení se ČTE z dokumentu, pak se měří) ──")
    text61, l0, l1 = oddil(r"^##\s+61\.")
    p("            okno dokumentu: HANDOFF.md řádky %d–%d (%d znaků)" % (l0, l1, len(text61)))
    if plne:
        # ⚠ PŘED DRAHÝMI BRANAMI PŘEGENEROVAT INVENTÁŘ (H126). Naměřeno 9. 10. 2026
        # v P31, PRVNÍ běh A3: bez přegenerování hlásil `g3` **2 NEDEKLAROVANÉ
        # exity a 2 brány bez čítače** (`n1-over-inventar`, `C2: mutace N1`) a
        # `validate-all` **1 problém** — a A3 to přečetlo jako ROZCHOD tvrzení
        # §61, ačkoli se rozcházel STAV MĚŘENÍ, ne dokument. Je to táž past,
        # kterou má `p28-a-overeni.py` v A6 (`pregeneruj_inventar()`).
        kod, _, tr = spust([sys.executable, "_analyza/hl-neanglicky-v-kodu.py",
                            "--json", "_analyza/_inventar.json"], timeout=900)
        m.ok_(kod == 0, "A3 inventář přegenerován PŘED drahými branami (H126), %.0f s" % tr)

    TVRZENI = [
        dict(jmeno="test-tick-offline", dok=[r"test-tick-offline\s*\*{0,2}(\d+)/(\d+)"],
             cmd=["node", "tools/test-tick-offline.mjs"],
             out=[r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"], exity={0}, drahe=False),
        dict(jmeno="over-skilly", dok=[r"over-skilly`?\s*\*{0,2}(\d+)\s*zmínek,\s*(\d+)\s*mrtvých",
                                        r"over-skilly`?\s*\*{0,2}(\d+)/(\d+)"],
             cmd=[sys.executable, "tools/over-skilly.py"],
             out=[r"(\d+)\s*zmínek,\s*(\d+)\s*mrtvých"], exity={0}, drahe=False),
        dict(jmeno="ov-g-neovereno", dok=[r"ov-g[^\n]{0,24}?(\d+)\s*řádků Hxx"],
             cmd=[sys.executable, "_analyza/ov-g-neovereno.py"],
             out=[r"(\d+)\s*nálezů Hxx"], exity={0}, drahe=False),
        dict(jmeno="p29-b6-mutace", dok=[r"p29-b6-mutace\s*\*{0,2}(\d+)/(\d+)"],
             cmd=[sys.executable, "_analyza/p29-b6-mutace.py"],
             out=[r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"], exity={0}, drahe=False),
        dict(jmeno="over-dokumentaci", dok=[r"over-dokumentaci`?\s*\*{0,2}(\d+)/(\d+)"],
             cmd=[sys.executable, "tools/over-dokumentaci.py"],
             out=[r"Kontrol:\s*(\d+),\s*chyb:\s*(\d+)", r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"],
             exity={0}, drahe=False),
        dict(jmeno="p28-b-mutace (STAV PO OPRAVĚ C1)",
             dok=[r"přestalo reprodukovat\s*\((\d+)/(\d+)\)"],
             cmd=None, doklad=ANALYZA / "p31-mutace-vystup.txt", drahe=False,
             poznamka="po opravě C1 (H131+H132) měřidlo hlásí 0 chyb — číslo 27/2 v §61 "
                      "je ZÁZNAM STAVU PŘED opravou a mění se PRÁVĚ tou opravou"),
        dict(jmeno="p30-mutace", dok=[r"p30-mutace\s*\*{0,2}(\d+)/(\d+)"],
             cmd=[sys.executable, "_analyza/p30-mutace.py"],
             out=[r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb"], exity={0}, drahe=True),
        dict(jmeno="tick-mutace", dok=[r"tick-mutace[^\n]{0,30}?(\d+)\s*vrat[/,]\s*(\d+)/(\d+)"],
             cmd=[sys.executable, "_analyza/tick-mutace.py"],
             out=[r"vrat:\s*(\d+)", r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"], exity={0}, drahe=True),
        dict(jmeno="g3-brany", dok=[r"g3\s*→\s*(\d+)\s*bran\s*/\s*(\d+)\s*NEDEKLAROVANÝCH"],
             cmd=[sys.executable, "_analyza/g3-brany.py"],
             out=[r"brán celkem:\s*(\d+)", r"NEDEKLAROVANÝCH\s+(\d+)"],
             exity={0, 1}, drahe=True),
        dict(jmeno="validate-all", dok=[r"validate-all\s*→\s*(?:\d+\s*→\s*)?(\d+)\s*problém"],
             cmd=["node", "tools/validate-all.mjs"], out=[r"NALEZENO\s+(\d+)\s+PROBLÉM"],
             exity={0, 1}, drahe=True, kdyz_vse_ok=("0",)),
        dict(jmeno="p30-a-overeni", dok=[r"p30-a\s*\*{0,2}(\d+)/(\d+)"],
             cmd=[sys.executable, "_analyza/p30-a-overeni.py", "--plne", "--vystup",
                  "_analyza/p31-p30a-plne-vystup.txt"],
             out=[r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb"], exity={0}, drahe=True,
             doklad_pri_chybe=ANALYZA / "p31-p30a-plne-vystup.txt"),
    ]
    for t in TVRZENI:
        jmeno = t["jmeno"]
        cit, okno, _ = tvrzeni(text61, t["dok"])
        if cit is None:
            m.ok_(False, "A3 %s: TVRZENÍ SE V §61 NENAŠLO (kontrola by se tiše přeskočila)"
                  % jmeno)
            continue
        p("            %s: dokument tvrdí %s · okno: …%s…" % (jmeno, cit, okno))
        if jmeno in cache:
            nam = cache[jmeno]
            p("            naměřeno: %s (změřeno dřív v tomhle běhu)" % (nam,))
            m.ok_(all(str(cit[i]) == str(nam[i]) for i in range(min(len(cit), len(nam)))),
                  "A3 %s: dokument %s == naměřeno %s" % (jmeno, cit, nam))
            continue
        if t["drahe"] and not plne:
            m.nezmereno("A3 %s: měření je drahé — spusť --plne (tvrzeno %s)" % (jmeno, cit))
            continue
        if t.get("cmd") is None:
            cd = citac_dokladu(t["doklad"])
            if cd is None:
                m.nezmereno("A3 %s: doklad %s není (spusť `p31-mutace.py`)"
                            % (jmeno, pathlib.Path(t["doklad"]).name))
                continue
            cache[jmeno] = cd
            p("            naměřeno: %s (z dokladu %s, kontrola ukazuje %s chyb)"
              % (cd, pathlib.Path(t["doklad"]).name, cd[1]))
            if t.get("poznamka"):
                m.rozdil("A3 %s: %s (dokument %s vs naměřeno %s)"
                         % (jmeno, t["poznamka"], cit, cd))
            else:
                m.ok_(all(str(cit[i]) == str(cd[i]) for i in range(min(len(cit), len(cd)))),
                      "A3 %s: dokument %s == naměřeno %s" % (jmeno, cit, cd))
            continue
        kod, out, tr = spust(t["cmd"], timeout=2400)
        if kod not in t["exity"]:
            posledni = out.strip().splitlines()[-1][:130] if out.strip() else "—"
            m.ok_(False, "A3 %s: exit=%d (čekán %s) za %.0f s — %s"
                  % (jmeno, kod, sorted(t["exity"]), tr, posledni))
            # ⚠ U TVRZENÍ O CIZÍM MĚŘIDLE SE VYPÍŠE, KTERÉ JEHO KONTROLY SPADLY —
            #    jinak by „exit 1" nešlo vysvětlit (a číslo by se četlo jako lež).
            q = t.get("doklad_pri_chybe")
            if q and pathlib.Path(q).is_file():
                for l in pathlib.Path(q).read_text(encoding="utf-8",
                                                    errors="replace").splitlines():
                    if l.strip().startswith("CHYBA:"):
                        p("            · %s" % l.strip()[:170])
            continue
        m.ok_(True, "A3 %s: exit=%d za %.0f s" % (jmeno, kod, tr))
        hodnoty = []
        for v in t["out"]:
            n = re.findall(v, out, re.S)
            if n:
                posledni = n[-1]
                hodnoty.extend(posledni if isinstance(posledni, tuple) else (posledni,))
        if not hodnoty and "kdyz_vse_ok" in t and "VŠE V POŘÁDKU" in out:
            hodnoty = list(t["kdyz_vse_ok"])
            p("            (brána hlásí „VŠE V POŘÁDKU“ — bere se 0 problémů)")
        if not hodnoty:
            m.ok_(False, "A3 %s: ve výstupu NENÍ čítač (měřilo by se naslepo)" % jmeno)
            continue
        cache[jmeno] = tuple(hodnoty)
        p("            naměřeno: %s" % (tuple(hodnoty),))
        if jmeno == "g3-brany":
            bez = re.search(r"BRÁNY BEZ ČÍTAČE mimo deklarovaný stav:\s*(\d+)", out)
            m.ok_(bez is not None and bez.group(1) == "1",
                  "A3 g3: bran bez čítače = %s (§61.5 tvrdí 1: `mutace B (combat)`, "
                  "cizí brána hry)" % (bez.group(1) if bez else "—"))
            if kod == 1:
                m.rozdil("A3 g3: `g3` končí exit=1, protože 1 brána NEMÁ čítač a "
                         "`OCEKAVANE_BEZ_CITACE` je prázdný — NENÍ to neočekávaný exit; "
                         "`p28-a-overeni.py` A6 na tom ale stojí (H133)")
        m.ok_(all(str(cit[i]) == str(hodnoty[i]) for i in range(min(len(cit), len(hodnoty)))),
              "A3 %s: dokument %s == naměřeno %s" % (jmeno, cit, tuple(hodnoty)))

    kod, out, tr = spust([sys.executable, "_analyza/kronika-kontrola.py"], timeout=300)
    m.ok_(kod == 0 and "SEDÍ" in out.upper(),
          "A3 kronika-kontrola: exit=%d a hlásí SEDÍ (%.0f s)" % (kod, tr))
    r = re.search(r"sessions v kronice:\s*(\d+)", out)
    if r:
        p("            kronika: naměřeno %s řádků session (řádek 46 přibude v této session)"
          % r.group(1))


# ── A4 ──────────────────────────────────────────────────────────────────────
def sekce_A4(m, _plne):
    p("")
    p("── A4 (H130): DÁVKA DOKLADŮ UŽ NEPŘEPISUJE ŽIVÉ DOKUMENTY? ──")
    SLEDOVANE = [KRONIKA, HANDOFF, WS / "NEXT-SESSION-INSTRUKCE.md",
                 ANALYZA / "_registr-bran.json"]
    pred = {q.name: hashlib.sha256(q.read_bytes()).hexdigest() for q in SLEDOVANE}
    kod, out, tr = spust([sys.executable, str(P20D)], timeout=5400)
    p("            dávka: exit=%d, %.0f s (%d znaků výstupu)" % (kod, tr, len(out)))
    po = {q.name: hashlib.sha256(q.read_bytes()).hexdigest() for q in SLEDOVANE}
    zmenene = [n for n in pred if pred[n] != po[n]]
    m.ok_(not zmenene, "A4-1 ani JEDEN ze %d sledovaných dokumentů se nezměnil (hash "
                       "před/po): %s" % (len(SLEDOVANE), zmenene or "žádný"))
    m.ok_("žádný z 4 sledovaných dokumentů se nezměnil" in out,
          "A4-2 POJISTKA dávky to ŘEKLA: „žádný z 4 sledovaných dokumentů se nezměnil“")
    m.ok_("⚠ ZMĚNĚN" not in out, "A4-3 dávka neohlásila ŽÁDNÝ „ZMĚNĚN“ dokument")
    (ANALYZA / "p31-a4-davka-vystup.txt").write_bytes(out.encode("utf-8"))
    selhale = re.findall(r"exit=\d+\s+(\S+\.py)", out)
    p("            doklady s nenulovým exit: %d — %s" % (len(selhale), ", ".join(selhale[:12])))
    p("            (úplný výstup dávky: p31-a4-davka-vystup.txt)")


# ── A5 ──────────────────────────────────────────────────────────────────────
def sekce_A5(m, _plne):
    p("")
    p("── A5 (H111): STROP GRANULE vs. ZÁMEK — nezávisle z D1 (jen SELECT) ──")
    kod, _, tr = spust(["node", str(SONDA_D1), str(DOKLAD_D1.relative_to(WS))], timeout=1800)
    m.ok_(kod == 0, "A5-0 sonda D1 → exit 0 (%.0f s)" % tr)
    if not DOKLAD_D1.is_file():
        m.ok_(False, "A5-0 sonda D1 NEZAPSALA doklad %s" % DOKLAD_D1.name)
        return
    t = DOKLAD_D1.read_text(encoding="utf-8", errors="replace")

    def sekce_d1(cislo):
        mm = re.search(r"^## %s\).*?$" % cislo, t, re.M)
        if not mm:
            return None
        zbytek = t[mm.end():]
        m2 = re.search(r"^## \d+\)", zbytek, re.M)
        return zbytek[:m2.start()] if m2 else zbytek

    s1 = sekce_d1(1)
    if s1:
        dvojice = re.findall(r'"item_id":\s*"([^"]+)"[^}]*?"runs":\s*(\d+)', s1, re.S)
        nad = [(j, int(n)) for j, n in dvojice if int(n) >= 8]
        p("            granulí s počítadlem běhů ≥ 8 (strop): %d — %s" % (len(nad), nad[:6]))
        reg = [n for j, n in dvojice
               if j == "engine.registry" or j.endswith("/engine.registry")]
        m.ok_(bool(reg) and int(reg[0]) >= 3,
              "A5-1 `engine.registry` má počítadlo ≥ 3 (mechanismus stropu: roste od vzniku "
              "řádku v cache) — naměřeno %s" % (reg[0] if reg else "—"))
        m.ok_(not [x for x in nad if "sim.crafting" not in x[0]],
              "A5-1 žádná VYDÁVANÁ granule dnes není za stropem "
              "(výjimka `sim.crafting` = `done`, nevydává se)")
    else:
        m.nezmereno("A5-1 oddíl 1) sondy D1 chybí")

    s11 = sekce_d1(11)
    if s11 is not None:
        ids = re.findall(r'"id":\s*(\d+)', s11)
        m.ok_(not ids, "A5-2 ZÁMEK VYLOUČEN: žádná úloha nezůstala `running` (naměřeno: %s)"
              % (ids or "žádná"))
    else:
        m.nezmereno("A5-2 oddíl 11) (klíče zámku) v dokladu chybí")

    s5 = sekce_d1(5)
    if s5:
        starty = re.findall(r'"started_at":\s*"([^"]+)"', s5)
        if starty:
            p("            běhy v dokladu D1 (oddíl 5): od %s do %s" % (min(starty), max(starty)))
            m.ok_(True, "A5-3 časová osa běhů je v dokladu (%d běhů)" % len(starty))
        else:
            m.nezmereno("A5-3 v oddílu 5) D1 nejsou žádné běhy")
    else:
        m.nezmereno("A5-3 oddíl 5) sondy D1 chybí")
    p("            (POZNÁMKA: přesný důkaz „mezi posledním během a tichým tikem nic "
      "neběželo“ je v §61.3 a v `_analyza/p30-d1-vystup.txt`; dnešní D1 ukazuje stav "
      "PO úklidu cache)")


# ── A6 ──────────────────────────────────────────────────────────────────────
def sekce_A6(m, _plne):
    p("")
    p("── A6 (H124): UKLIDÍ SE MĚŘIDLO P29 PO SOBĚ? ──")
    _, out, _ = git("status", "--porcelain")
    pred = set(out.splitlines())
    p("            `git status` před: %d řádků" % len(pred))
    kod, out, tr = spust([sys.executable, str(ANALYZA / "p29-a-overeni.py"),
                          "--jen", "A1M13",
                          "--vystup", "_analyza/p31-a6-a1m13-vystup.txt"], timeout=2400)
    m.ok_(True, "A6-1 `p29-a-overeni.py --jen A1M13` exit=%d za %.0f s" % (kod, tr))
    zbyle = sorted(q.name for q in ANALYZA.glob("p29-mut-*"))
    m.ok_(not zbyle, "A6-2 po běhu NEZŮSTAL v `_analyza/` žádný mutant: %s"
          % (zbyle or "žádný"))
    m.ok_("úklid: po běhu nezůstal" in out,
          "A6-3 měřidlo to ŘEKLO (kontrola úklidu je součástí jeho výsledku)")
    _, out2, _ = git("status", "--porcelain")
    nove = sorted(x for x in set(out2.splitlines()) - pred if "p29-mut" in x)
    m.ok_(not nove, "A6-4 a v `git status` nepřibyl žádný mutant: %s" % (nove or "žádný"))


# ── A7 ──────────────────────────────────────────────────────────────────────
def sekce_A7(m, plne):
    p("")
    p("── A7: NIC SE NEROZBILO (záznamy, kronika, handoff, ov-g) ──")
    _, out, _ = git("diff", "--numstat", "HEAD", "--", "HANDOFF.md", "KRONIKA-PROJEKTU.md")
    pridano = smazano = 0
    for l in out.splitlines():
        casti = l.split("\t")
        if len(casti) >= 2 and casti[0].isdigit() and casti[1].isdigit():
            pridano += int(casti[0])
            smazano += int(casti[1])
    p("            necommitnuté záznamy: +%d řádků, -%d řádků" % (pridano, smazano))
    m.ok_(smazano == 0, "A7 záznamy se jen PŘIDÁVALY (0 smazaných řádků v HANDOFF/KRONICE)")

    kod, out, _ = spust([sys.executable, "_analyza/kronika-kontrola.py"], timeout=300)
    m.ok_(kod == 0 and "SEDÍ" in out.upper(), "A7 kronika-kontrola → SEDÍ, exit 0")
    kod, out, _ = spust([sys.executable, "_analyza/handoff-kontrola-uplnost.py"], timeout=600)
    ch = re.search(r"CHYBÍ:\s*(\d+)", out)
    m.ok_(kod == 0 and ch is not None and ch.group(1) == "0",
          "A7 handoff-kontrola-uplnost → 0 chybějících (naměřeno %s)"
          % (ch.group(1) if ch else "—"))
    kod, out, _ = spust([sys.executable, "_analyza/ov-g-neovereno.py"], timeout=600)
    n = re.search(r"(\d+)\s*nálezů Hxx", out)
    nev = re.search(r"NEOVĚŘENO:\s*(\d+)", out)
    m.ok_(kod == 0, "A7 ov-g-neovereno → exit 0 (rozsah %s řádků Hxx)"
          % (n.group(1) if n else "—"))
    m.ok_(nev is not None and nev.group(1) == "0",
          "A7 a NEOVĚŘENO = 0 (naměřeno %s)" % (nev.group(1) if nev else "—"))
    if not plne:
        m.nezmereno("A7 drahé brány (`g3`, `validate-all`) — ty měří sekce A3, spusť --plne")
    else:
        m.ok_(True, "A7 drahé brány (`g3`, `validate-all`) změřila sekce A3 — neopakují se")


# ── main ────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jen", default=None, help="seznam etap, např. A3,A6")
    ap.add_argument("--plne", action="store_true", help="i drahé brány a živé sondy")
    ap.add_argument("--vystup", default=None)
    args = ap.parse_args()

    vystup = pathlib.Path(args.vystup) if args.vystup else ANALYZA / "p31-a-overeni-vystup.txt"
    if not vystup.is_absolute():
        vystup = WS / vystup
    m = Meridlo()
    cache = {}
    fns = {
        "A1": lambda: sekce_A1(m, args.plne, cache),
        "A2": lambda: sekce_A2(m, args.plne),
        "A3": lambda: sekce_A3(m, args.plne, cache),
        "A4": lambda: sekce_A4(m, args.plne),
        "A5": lambda: sekce_A5(m, args.plne),
        "A6": lambda: sekce_A6(m, args.plne),
        "A7": lambda: sekce_A7(m, args.plne),
    }
    etapy = [x.strip().upper() for x in
             (args.jen if args.jen else ("A1,A2,A3,A5,A6,A7" if args.plne else "A3")).split(",")]
    p("=" * 88)
    p("P31/A — VLASTNÍ PŘEMĚŘENÍ PRÁCE P30 (Úkol A zadání P31)")
    p("=" * 88)
    p("  datum (z hodin): %s" % time.strftime("%Y-%m-%d %H:%M:%S %z"))
    p("  pořadí běhu: %s%s" % (", ".join(etapy), "  (--plne)" if args.plne else "  (levný režim)"))
    p("  doklad: %s" % vystup.name)
    p("  ⚠ A4 (dávka dokladů, ~35 min) se pouští JEN `--jen A4` — má vlastní běhy")
    for e in etapy:
        f = fns.get(e)
        if f is None:
            p("  ??    etapa %s neexistuje" % e)
            continue
        p("\n" + "─" * 88)
        try:
            f()
        except Exception as ex:  # noqa: BLE001
            import traceback  # noqa: PLC0415
            tb = traceback.format_exc().strip().splitlines()
            p("      TRACEBACK: %s" % " | ".join(x.strip() for x in tb[-3:]))
            m.nezmereno("etapa %s: výjimka %s: %s" % (e, type(ex).__name__, str(ex)[:200]))
    p("\n" + "=" * 88)
    p("POJMENOVANÉ ROZDÍLY (stav se posunul, nebo je změna ZÁMĚRNÁ): %d" % len(m.rozdily))
    for x in m.rozdily:
        p("  · %s" % x[:200])
    p("\nNEZMĚŘENO (není nula a není zelená): %d" % len(m.nezmerene))
    for x in m.nezmerene:
        p("  · %s" % x[:200])
    p("=" * 88)
    p("VÝSLEDEK: %d kontrol, %d chyb (z toho %d pojmenovaných ROZDÍLŮ, %d NEZMĚŘENO)"
      % (m.ok, len(m.chyby), len(m.rozdily), len(m.nezmerene)))
    p("=" * 88)
    vystup.write_bytes(("\n".join(_vystup) + "\n").encode("utf-8"))
    print("\n[doklad] %s (%d B, UTF-8)" % (vystup.relative_to(WS), vystup.stat().st_size))
    return 1 if m.chyby else 0


if __name__ == "__main__":
    sys.exit(main())
