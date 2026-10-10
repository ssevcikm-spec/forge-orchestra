# -*- coding: utf-8 -*-
r"""P33 — VLASTNÍ PŘEMĚŘENÍ PRÁCE P32 + ZAVŘENÍ H112 (Úkol A a B zadání P33).

CO TENHLE DOKLAD DĚLÁ (a čím se liší od měřidla P32):
  * **Čísla NEČTE Z HLAVY** — každé tvrzení se nejdřív **PŘEČTE Z §63**
    (`HANDOFF.md` = záznam P32) a vypíše se **okno, které vzor trefil**.
  * **MÁ VLASTNÍ KONTRAMUTACE, ne opisy** — vady P32 se vracejí do **KOPIÍ**
    měřidel a u H142 do **ŽIVÉHO patcheru** (přes `mutuj`, tedy s návratem bajt
    na bajt) a měří se, že to měřidlo/brána **ZACHYTÍ**. Fixtury H142 jsou
    **moje**, ne opsané z `p32-test-zapis-kotvy.py`.
  * **Úkol B (H112) měří TŘEMI vrstvami:** offline fixtury predikátu → ŽIVÝ tep
    cronu → a **uložený stav PŘED nasazením**, na kterém musí brána **SPADNOUT**
    (jinak by „zelená proti živé službě“ nebyla k rozeznání od slepé brány).
  * **Rozlišuje CHYBU, ROZDÍL a NEZMĚŘENO** — tvrzení o měřidle musí sedět
    (`CHYBA`); tvrzení o živém stavu se posunout smí (`ROZDÍL` s vysvětlením).
  * **Umí selhat** — `_analyza/p33-mutace.py` (zmutovaná KOPIE dokumentu
    přes `P33_HANDOFF` a uložený před-nasazovací stav přes `P33_HEALTH`).

SEKCE:
  C0  pojistky (co měřidlo předpokládá)
  C1  (A1) umí opravy P32 spadnout? (VLASTNÍ kontramutace H140/H142/H145)
  C2  (A2) co P32 nasadila? (git; TŘI KROKY nasazení jen `--plne`)
  C3  (A3) sedí čísla z §63? (tvrzení se čte z §63, pak se měří)
  C4  (A4) dávka dokladů nepřepisuje dokumenty — JEN `--jen C4` (~35 min)
  C5  (A5) registr bran (49) proti číslu v `AGENTS.md` a v §63
  C6  (A6) uklízí se měřidla po sobě? (H146 a spol.)
  C7  (A7) nic se nerozbilo (inventář → g3 → validate-all, NE současně)
  C8  (Úkol B) H112 — brána „cron běží (čas)“ už měří TEP cronu
  C9  (A3-dlouhé) přeměření `p31-a --plne` a `p32-a --plne` — JEN `--jen C9`

Použití:
    python _analyza\p33-a-overeni.py                # LEVNÉ (bez mutací a sítě, ~2 min)
    python _analyza\p33-a-overeni.py --plne         # i kontramutace, úklid a živé sondy
    python _analyza\p33-a-overeni.py --jen C8       # jen Úkol B
    python _analyza\p33-a-overeni.py --jen C4       # dávka dokladů (~35 min)
    python _analyza\p33-a-overeni.py --jen C9       # p31-a --plne + p32-a --plne (~80 min)

⚠ `--plne`/`--jen C9` POUŠTÍ MUTAČNÍ BĚHY, které dočasně mění ŽIVÉ soubory
(`HANDOFF.md`, `p27-dopln-zaznamy.py`, `tools/over-skilly.py`) — vždy pod
`_mutace.mutuj` (návrat bajt na bajt). **Během plného běhu se do stromu NEPÍŠE.**
⚠ `--jen C9` volá `POST /tick` (uvnitř `p31-a --plne`, sekce A2) = ZÁSAH DO
ŽIVÉHO STAVU. Je to součástí zadání A3; v dokladu je to vidět.
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
# ⚠ TEST SEAM (P33): `HANDOFF.md` jde přepsat z PROSTŘEDÍ, aby mutační test
# měřil nad KOPIÍ dokumentu a **nesahal na živý záznam** (vzor P32).
HANDOFF = pathlib.Path(os.environ.get("P33_HANDOFF") or (WS / "HANDOFF.md"))
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
NEXT = WS / "NEXT-SESSION-INSTRUKCE.md"
REGISTR = ANALYZA / "_registr-bran.json"
P22T = ANALYZA / "p22-test-mutace.py"
P27P = ANALYZA / "p27-dopln-zaznamy.py"
P29A = ANALYZA / "p29-a-overeni.py"
P30A = ANALYZA / "p30-a-overeni.py"
P30M = ANALYZA / "p30-mutace.py"
P31A = ANALYZA / "p31-a-overeni.py"
P31M = ANALYZA / "p31-mutace.py"
P32A = ANALYZA / "p32-a-overeni.py"
P32M = ANALYZA / "p32-mutace.py"
P32T = ANALYZA / "p32-test-zapis-kotvy.py"
P28B = ANALYZA / "p28-b-mutace.py"
G3 = ANALYZA / "g3-brany.py"
INVENTAR = ANALYZA / "hl-neanglicky-v-kodu.py"
OVG = ANALYZA / "ov-g-neovereno.py"
GIT = TOOLS / "git.cmd"
VALIDATE = TOOLS / "validate-all.mjs"
CRON_HELP = TOOLS / "cron-stav.mjs"
CRON_TEST = TOOLS / "test-cron-stav.mjs"
SONDA_HEALTH = ANALYZA / "p33-sonda-health.mjs"
SONDA_CF = ANALYZA / "p32-sonda-cf-verze.mjs"
SONDA_DEPLOY = ANALYZA / "p30-sonda-deploy.mjs"
CONDUCTOR = WS / "conductor" / "src" / "index.ts"
SCRATCH = ANALYZA / "p33-scratch"
DOKLAD = ANALYZA / "p33-a-overeni-vystup.txt"
DOKLAD_HEALTH_PO = ANALYZA / "p33-health-po-vystup.txt"
# Stav PŘED nasazením H112 (odebraný 9. 10. 2026 ~23:00 +02:00, kdy `/health`
# ještě `last_cron` neposílalo). Na TOMHLE vstupu musí nová brána SPADNOUT.
DOKLAD_HEALTH_PRED = pathlib.Path(
    os.environ.get("P33_HEALTH") or (ANALYZA / "p33-health-pred-vystup.txt"))
# Test seam (P33): přeskočí se DRAHÁ NOHA, která už byla změřena jindy — a VŽDY
# se to vypíše jako NEZMĚŘENO s odkazem na doklad (nikdy tiše).
P33_C9_PRESKOC = os.environ.get("P33_C9_PRESKOC", "")

SLEDOVANE = [KRONIKA, WS / "HANDOFF.md", NEXT, REGISTR]

# ── kotvy kontramutací (MUSÍ se shodovat se zdrojem; ověřuje se v C0/C1) ──────
# H140: OPRAVENÁ kontrola (parsuje měřený řádek) vs. PŮVODNÍ vadná (podřetězec).
NOVY_BLOK_H140 = ('    zk(z1 is not None and z1[1] > 0,\n'
                  '       "a její MĚŘENÝ řádek hlásí mrtvé cesty (diferenciál, ne podřetězec)",\n'
                  '       f"zdravá {z0} → zmutovaná {z1}")')
STARY_BLOK_H140 = ('    zk("0 mrtvých" not in v1,\n'
                   '       "PUVODNI VADNA kontrola (podretezec): vystup nehlasi 0 mrtvych",\n'
                   '       f"zdravá {z0} → zmutovaná {z1}")')
# H142: hlídání kotvy PŘED zápisem — vypne se na `if False]`.
GUARD_P27 = "if text.count(stary) != 1]"
# H145: kotva v p30-mutace.py (dlouhá, z MĚŘENÉHO oddílu §60) vs. KRÁTKÁ.
# ⚠ ROZLIŠUJ ZDROJ a HODNOTU: `ZDROJ` je řádek KÓDU (hledá se v `p30-mutace.py`),
# `HODNOTA` je text, který je v DOKUMENTU (a v §60). Kdo je zamění, měří jinam —
# naměřeno P33: první verze hledala v dokumentu řádek kódu a kontrola hlásila
# „kotva není 1×“, ačkoli v dokumentu JE.
KOTVA_DOK_30_ZDROJ = ('KOTVA_DOK = "test-tick-offline → 215/0 (bylo 205/0) · '
                      'tick-mutace → 20 vrat, 41/0"')
KOTVA_DOK_30_HODNOTA = ('test-tick-offline → 215/0 (bylo 205/0) · '
                        'tick-mutace → 20 vrat, 41/0')
KOTVA_KRATKA_30 = 'KOTVA_DOK = "test-tick-offline → 215/0"'
KOTVA_KRATKA_TEXT = "test-tick-offline → 215/0"

# ⚠ KOPIE SPUSTITELNÝCH MĚŘIDEL MUSÍ LEŽET PŘÍMO V `_analyza/` — nástroje si
# odvozují cestu z `Path(__file__).resolve().parents[1]`, takže kopie v
# PODADRESÁŘI spadne na `ModuleNotFoundError: No module named '_mutace'`
# (naměřeno P33 napoprvé). Jména začínají `_`, aby je nevzal vzor dávky dokladů.
MUT_P22 = ANALYZA / "_p33-mut-p22.py"
MUT_P30 = ANALYZA / "_p33-mut-p30.py"

FIX_H = ("# FIXTURA P33 HANDOFF — kotvy §57 tu ZÁMĚRNĚ NEJSOU\r\n"
         "15. **PŘEPSANÝ ŘÁDEK SESSION** je tu proto, aby blok §57 nic nepsal.\r\n")
FIX_K = ("# FIXTURA P33 KRONIKA\r\n"
         "| **P27-P** | je tu proto, aby blok §2.20 nic nepsal |\r\n")

ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj  # noqa: E402

_vystup = []
# Výstupy dlouhých běhů ze sekce C9 (aby se čítače neopisovaly z hlavy a aby se
# druhý běh téhož nástroje nedělal dvakrát).
_VYSTUP_C9 = {}


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


def sha(cesta):
    return hashlib.sha256(pathlib.Path(cesta).read_bytes()).hexdigest()


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


def pregeneruj_inventar():
    kod, _, _ = spust([sys.executable, str(INVENTAR), "--json", str(ANALYZA / "_inventar.json")],
                      timeout=1800)
    return kod == 0


def uklid_po_meridlech():
    zbyle = [x.name for x in ANALYZA.glob("p29-mut-*")]
    zbyle += [x.name for x in ANALYZA.glob("p22-mutace-*")]
    zbyle += [x.name for x in ANALYZA.glob("p32-mutace-scratch")]
    zbyle += [x.name for x in ANALYZA.glob("p29-kopie-tick.mjs")]
    zbyle += [x.name for x in ANALYZA.glob("_p32-mut-*")]
    zbyle += [x.name for x in ANALYZA.glob("_p33-mut-*")]
    return sorted(zbyle)


def zapis_kopii_s_vadou(cesta, zdroj, stary, novy, popis, m):
    """Zapíše KOPII se vrácenou vadou a OVĚŘÍ, že se mutace opravdu provedla.

    ⚠ `cesta` musí být v `_analyza/` (ne v podadresáři) — spustitelná kopie si
    odvozuje `_mutace` z `parents[1]`; v podadresáři spadne na importu.
    """
    txt = zdroj.replace(stary, novy, 1)
    provedla = (txt != zdroj and txt.count(novy) == 1 and txt.count(stary) == 0)
    m.ok_(provedla, "%s MUTACE SE PROVEDLA (v kopii je vada, opravený tvar NENÍ)" % popis)
    if not provedla:
        return None
    cesta.write_bytes(txt.encode("utf-8"))
    return cesta


# ── C0 ──────────────────────────────────────────────────────────────────────
def sekce_C0(m):
    p("")
    p("── C0: POJISTKY (co měřidlo předpokládá) ──")
    for cesta, popis in ((HANDOFF, "HANDOFF.md"), (P22T, "p22-test-mutace.py"),
                         (P27P, "p27-dopln-zaznamy.py"), (P30M, "p30-mutace.py"),
                         (P32M, "p32-mutace.py"), (P32T, "p32-test-zapis-kotvy.py"),
                         (P29A, "p29-a-overeni.py"), (P31A, "p31-a-overeni.py"),
                         (P31M, "p31-mutace.py"), (P28B, "p28-b-mutace.py"),
                         (G3, "g3-brany.py"), (VALIDATE, "validate-all.mjs"),
                         (CRON_HELP, "tools/cron-stav.mjs"), (CRON_TEST, "tools/test-cron-stav.mjs"),
                         (SONDA_HEALTH, "p33-sonda-health.mjs")):
        m.ok_(cesta.is_file(), "C0 %s existuje" % popis)
    text63, l0, l1 = oddil(r"^##\s+63\.")
    p("            okno §63: HANDOFF.md řádky %d–%d (%d znaků)" % (l0, l1, len(text63)))
    m.ok_(len(text63) > 5000, "C0 §63 je načtený CELÝ (%d znaků)" % len(text63))
    # ⚠ MĚŘIDLO SÁM SOBĚ: vlastní soubory NESMÍ mít BOM (`.py` s BOM je pro brány
    # nekompilovatelný — omyl 189).
    for cesta in (pathlib.Path(__file__), ANALYZA / "p33-mutace.py", SONDA_HEALTH):
        b = cesta.read_bytes()
        m.ok_(b[:3] != b"\xef\xbb\xbf", "C0 %s NEMÁ BOM" % cesta.name)
    m.ok_(not uklid_po_meridlech(), "C0 na začátku nejsou zbytky měřidel (%s)"
          % (uklid_po_meridlech() or "žádné"))
    # pojistky kotov kontramutací
    z22 = P22T.read_text(encoding="utf-8")
    m.ok_(z22.count(NOVY_BLOK_H140) == 1, "C0 kotva OPRAVENÉ kontroly H140 je ve zdroji právě 1×")
    z27 = P27P.read_text(encoding="utf-8")
    m.ok_(z27.count(GUARD_P27) == 1, "C0 kotva hlídání kotvy H142 je ve zdroji právě 1×")
    z30 = P30M.read_text(encoding="utf-8")
    m.ok_(z30.count(KOTVA_DOK_30_ZDROJ) == 1, "C0 DLOUHÁ kotva H145 je ve ZDROJI právě 1×")
    m.ok_(HANDOFF.read_text(encoding="utf-8").count(KOTVA_DOK_30_HODNOTA) == 1,
          "C0 a její HODNOTA je v ŽIVÉM dokumentu právě 1× (kotva z MĚŘENÉHO oddílu)")


# ── C1 (A1) ─────────────────────────────────────────────────────────────────
def sekce_C1(m, plne):
    p("")
    p("── C1 (A1): UMÍ OPRAVY P32 SPADNOUT? (VLASTNÍ kontramutace) ──")
    if not plne:
        m.nezmereno("C1 (kontramutace mění KOPIE i živý patcher) — spusť --plne")
        return
    SCRATCH.mkdir(parents=True, exist_ok=True)

    # ── (a) H140: kontrola v p22-test-mutace.py se nechala uspokojit podřetězcem
    p("   (a) H140 — kontrola hledala `\"0 mrtvých\"` PODŘETĚZCEM")
    zdroj22 = P22T.read_text(encoding="utf-8")
    # ⚠ Statická kontrola musí číst KÓD, ne komentáře: vadný tvar je v souboru
    # ZÁMĚRNĚ popsaný v komentáři (aby se past nezapomněla) — v KÓDU být nesmí.
    kod22 = "\n".join(r for r in zdroj22.splitlines() if not r.lstrip().startswith("#"))
    m.ok_('"0 mrtvých" not in' not in kod22,
          "C1-a v KÓDU (bez komentářů) NENÍ podřetězcová podmínka `\"0 mrtvých\" not in`")
    m.ok_('"0 mrtvých" not in' in zdroj22,
          "C1-a (a v komentáři je popsaná — komentář popisující vadu NENÍ vada)")
    m.ok_("mrtve_cesty(v1)" in zdroj22, "C1-a kontrola parsuje čítač z MĚŘENÉHO řádku")
    kod1, v1, tr1 = spust([sys.executable, "-B", str(P22T)], timeout=1800)
    c1 = citac_text(v1)
    m.ok_((kod1, c1) == (0, ("20", "0")),
          "C1-a ŽIVÝ `p22-test-mutace.py` → exit 0 a 20/0 (naměřeno %s, %s, %.0f s)"
          % (kod1, c1, tr1))
    kopie = zapis_kopii_s_vadou(MUT_P22, zdroj22,
                                NOVY_BLOK_H140, STARY_BLOK_H140, "C1-a", m)
    if kopie:
        kod2, v2, _ = spust([sys.executable, "-B", str(kopie)], timeout=1800)
        c2 = citac_text(v2)
        m.ok_(kod2 != 0,
              "C1-a s VRÁCENOU vadnou kontrolou test SPADNE (exit=%d, čítač %s) — "
              "verdikt se MĚNÍ, kontrola je nosná" % (kod2, c2))
        m.ok_(c2 is not None and c2[1] != "0",
              "C1-a a spadne PRÁVĚ NA TÉ kontrole (počet chyb %s)"
              % (c2[1] if c2 else "BEZ ČÍTAČE — spadl jinde, než měl"))
        kopie.unlink(missing_ok=True)

    # ── (b) H142: patcher zapisoval i bez nalezené kotvy (VLASTNÍ fixtury)
    p("   (b) H142 — patcher zapisoval soubor i bez kotvy")
    zdroj27 = P27P.read_text(encoding="utf-8")
    sha27 = sha(P27P)
    h = SCRATCH / "fixtura-handoff-p33.md"
    kk = SCRATCH / "fixtura-kronika-p33.md"
    h.write_bytes(FIX_H.encode("utf-8"))
    kk.write_bytes(FIX_K.encode("utf-8"))
    m.ok_(b"\r\n" in h.read_bytes() and b"\r\n" in kk.read_bytes(),
          "C1-b fixtury mají PŘED během CRLF (jinak by zápis nebyl vidět)")
    sh, sk = sha(h), sha(kk)
    env27 = {"P27_HANDOFF": str(h), "P27_KRONIKA": str(kk)}
    kod3, v3, _ = spust([sys.executable, "-B", str(P27P)], env=env27, timeout=300)
    m.ok_(kod3 != 0, "C1-b živý patcher nad fixturami s CHYBĚJÍCÍMI kotvami → exit != 0 (%d)" % kod3)
    m.ok_("NEZAPSÁNO" in v3 and "NEDOTČEN" in v3, "C1-b a ŘEKNE, že NEZAPSAL")
    m.ok_(sha(h) == sh and sha(kk) == sk, "C1-b fixtury jsou bajt na bajt NEDOTČENÉ (H142 opraven)")
    # kontramutace: v ŽIVÉM patcheru se vypne hlídání kotvy (přes `mutuj` → vrátí se)
    with mutuj(P27P, GUARD_P27, "if False]"):
        m.ok_(P27P.read_text(encoding="utf-8").count("if False]") == 1,
              "C1-b v živém patcheru je vypnuté hlídání PRÁVĚ 1× (mutace se provedla)")
        kod4, v4, _ = spust([sys.executable, "-B", str(P27P)], env=env27, timeout=300)
        zapsano = sha(h) != sh
    m.ok_(kod4 != 0, "C1-b oslabený patcher taky hlásí chybu (exit=%d) — rozdíl NENÍ v exitu" % kod4)
    m.ok_(zapsano, "C1-b ALE fixturu ZAPSAL (%s → %s) → kontrola „nezapsáno“ MĚŘÍ"
          % (sh[:12], sha(h)[:12]))
    m.ok_(sha(P27P) == sha27, "C1-b živý patcher je vrácen BAJT NA BAJT (sha256)")
    m.ok_(sha(P22T) == sha(P22T), "C1-b (kontrola: ani `p22-test-mutace.py` se nezměnil)")

    # ── (c) H145: vlastní záznam P31 zdvojil kotvu → `mutuj` spadl na ValueError
    p("   (c) H145 — dvojznačná kotva v DOKUMENTU (vlastní záznam P31 ji citoval)")
    text_dok = HANDOFF.read_text(encoding="utf-8")
    zdroj30 = P30M.read_text(encoding="utf-8")
    m.ok_(text_dok.count(KOTVA_DOK_30_HODNOTA) == 1,
          "C1-c DLOUHÁ kotva je v dokumentu právě 1× (kotva z MĚŘENÉHO oddílu §60)")
    s60 = oddil(r"^##\s+60\.")[0]
    m.ok_(s60.count(KOTVA_DOK_30_HODNOTA) == 1,
          "C1-c a v MĚŘENÉM oddílu §60 právě 1× (proto se bere odtud)")
    m.ok_(text_dok.count(KOTVA_KRATKA_TEXT) > 1,
          "C1-c KRÁTKÁ kotva je v dokumentu %d× — to je past H145"
          % text_dok.count(KOTVA_KRATKA_TEXT))
    kod5, v5, tr5 = spust([sys.executable, "-B", str(P30M)], timeout=3600)
    c5 = citac_text(v5)
    m.ok_((kod5, c5) == (0, ("16", "0")),
          "C1-c ŽIVÝ `p30-mutace.py` → exit 0 a 16/0 (naměřeno %s, %s, %.0f s)"
          % (kod5, c5, tr5))
    kopie30 = zapis_kopii_s_vadou(MUT_P30, zdroj30,
                                  KOTVA_DOK_30_ZDROJ, KOTVA_KRATKA_30, "C1-c", m)
    if kopie30:
        # POJISTKA: `p30-mutace.py` NEMÁ seam na dokument, takže pracuje s ŽIVÝM
        # `HANDOFF.md`. U dvojznačné kotvy `mutuj` vyhodí `ValueError` JEŠTĚ PŘED
        # zápisem — a to se tady ověřuje hashem (doklad, ne víra).
        sha_live_pred = sha(WS / "HANDOFF.md")
        kod6, v6, _ = spust([sys.executable, "-B", str(kopie30)], timeout=3600)
        c6 = citac_text(v6)
        m.ok_(sha(WS / "HANDOFF.md") == sha_live_pred,
              "C1-c živý `HANDOFF.md` zůstal bajt na bajt (dvojznačná kotva se zapisuje až po kontrole)")
        m.ok_(kod6 != 0, "C1-c s DVOJZNAČNOU kotvou test skončí nenulově (exit=%d)" % kod6)
        m.ok_("NELZE PROVÉST" in v6,
              "C1-c a vadná kotva se hlásí POJMENOVANĚ (ne jen pád)")
        m.ok_("ValueError" not in v6 or "NELZE PROVÉST" in v6,
              "C1-c a nespadne na neodchycený `ValueError`")
        m.ok_(c6 is not None,
              "C1-c a DOBĚHNE S ČÍTAČEM (%s) — dřív to byl `exit 1` BEZ čítače, "
              "takže se ztratil celý diferenciál" % (c6,))
        kopie30.unlink(missing_ok=True)

    # ── (d) základní měřidlo P32 a jeho mutační důkaz
    p("   (d) vlastní měřidlo P32 a JEHO mutační důkaz")
    kod7, v7, tr7 = spust([sys.executable, "-B", str(P32M)], timeout=3600)
    c7 = citac_text(v7)
    m.ok_((kod7, c7) == (0, ("18", "0")),
          "C1-d `p32-mutace.py` → exit 0 a 18/0 (naměřeno %s, %s, %.0f s)" % (kod7, c7, tr7))

    # ── (e) úklid kopií kontramutací ────────────────────────────────────────
    for x in (MUT_P22, MUT_P30):
        x.unlink(missing_ok=True)
    zbyle = uklid_po_meridlech()
    m.ok_(not zbyle, "C1-e po kontramutacích nezůstaly kopie měřidel v `_analyza/` (%s)"
          % (zbyle or "žádné"))

    # ── (f) test patcheru H142 jako celek (vlastní běh) ─────────────────────
    kod8, v8, tr8 = spust([sys.executable, "-B", str(P32T)], timeout=1800)
    c8 = citac_text(v8)
    m.ok_((kod8, c8) == (0, ("16", "0")),
          "C1-f `p32-test-zapis-kotvy.py` → exit 0 a 16/0 (naměřeno %s, %s, %.0f s)"
          % (kod8, c8, tr8))
    m.ok_(not (ANALYZA / "p32-scratch").exists(),
          "C1-f a nezůstal po něm `p32-scratch/` ani `_p32-mut-p27.py`")
    m.ok_(not (ANALYZA / "_p32-mut-p27.py").exists(), "C1-f kopie patcheru je smazaná")


# ── C2 (A2) ─────────────────────────────────────────────────────────────────
def sekce_C2(m, plne):
    p("")
    p("── C2 (A2): CO P32 NASADILA? ──")
    for commit, popis, ocekavane in (
            ("41aa981", "P31 — měřidla a záznamy (21 souborů)", 0),
            ("d3f1a48", "P31 — oprava kotvy hry (1 soubor)", 0),
            ("0b86c2d", "P32 — C4′ komentáře conductora (NASADIL SE)", 1)):
        kod, v, _ = git("show", "--name-only", "--format=", commit)
        soubory = [x.strip() for x in v.splitlines() if x.strip()]
        cd = [x for x in soubory if x.startswith("conductor/") or x.startswith(".github/")]
        if ocekavane == 0:
            m.ok_(kod == 0 and not cd,
                  "C2 %s (%d souborů): ŽÁDNÝ z `conductor/` ani `.github/`" % (commit, len(soubory)))
        else:
            m.ok_(cd == ["conductor/src/index.ts"],
                  "C2 %s: mění PRÁVĚ `conductor/src/index.ts` (%s)" % (commit, cd or "nic"))
    m.ok_("JEDNU změnu" in oddil(r"^##\s+63\.")[0],
          "C2 §63 tvrdí, že P32 nasadila JEDINOU změnu (jen text komentářů)")
    if not plne:
        m.nezmereno("C2-3 tři kroky nasazení (síť) — spusť --plne")
        return
    # KROK 1: push dorazil (živý stav, ne lokální `origin/main`)
    kod, v, _ = git("ls-remote", "origin", "refs/heads/main")
    zivy = (v.split() or [""])[0]
    kod2, head, _ = git("rev-parse", "HEAD")
    m.ok_(zivy == head.strip(), "C2-1 `ls-remote` = živý `HEAD` (%s)" % zivy[:12])
    # KROK 2: deploy.yml na TOM commitu
    # ⚠ ZADÁVÁ SE PLNÝ SHA: GitHub API `?head_sha=<KRÁTKÝ>` tiše vrátí PRÁZDNO
    # (naměřeno P33: `head_sha=0b86c2d` → „na commitu NENÍ žádný běh“, ačkoli
    # tam běh #36 JE). Krátký sha se proto nejdřív přeloží gitem.
    _, plny, _ = git("rev-parse", "0b86c2d")
    plny = plny.strip()
    m.ok_(len(plny) == 40, "C2 plný sha pro `0b86c2d` = %s…" % plny[:12])
    kod, v, tr = spust(["node", str(SONDA_DEPLOY), plny], timeout=600)
    (ANALYZA / "p33-deploy-c4-vystup.txt").write_bytes(v.encode("utf-8"))
    m.ok_(kod == 0 and "completed/success" in v,
          "C2-2 `deploy.yml` na `0b86c2d` → completed/success (exit=%d, %.0f s)" % (kod, tr))
    # KROK 3: VERZE z LOGU nasazení (u změny jen v textu není na chování co vidět)
    kod, v, tr = spust(["node", str(SONDA_CF), plny,
                        str((ANALYZA / "p33-cf-verze-vystup.txt").relative_to(WS))], timeout=600)
    m.ok_(kod == 0 and "bb32fe74" in v,
          "C2-3 verze z LOGU nasazení obsahuje `bb32fe74` (exit=%d, %.0f s)" % (kod, tr))


# ── C3 (A3) ─────────────────────────────────────────────────────────────────
# `tvr` = vzor TVRZENÍ v §63 (musí se najít — jinak měřidlo měří jinam);
# `out` = vzory čítače ve výstupu nástroje (bere se první, který zabere);
# `druh` = "meridlo" (čítač musí sedět) / "stav" (posun se smí pojmenovat).
TABULKA = [
    dict(jmeno="over-skilly", drahe=False, druh="meridlo",
         tvr=[r"`over-skilly`\s*\*\*(\d+)/(\d+)\*\*"],
         cmd=[sys.executable, "tools/over-skilly.py"],
         out=[r"Cesty k nástrojům:\s*(\d+)\s*zmínek,\s*(\d+)\s*mrtvých"]),
    dict(jmeno="over-dokumentaci", drahe=False, druh="meridlo",
         tvr=[r"`over-dokumentaci`\s*\*\*(\d+)/(\d+)\*\*"],
         cmd=[sys.executable, "tools/over-dokumentaci.py"],
         out=[r"Kontrol:\s*(\d+),\s*chyb:\s*(\d+)"]),
    dict(jmeno="ov-g-neovereno", drahe=False, druh="meridlo",
         tvr=[r"`ov-g`\s*\*\*(\d+)\s*řádků Hxx", r"ov-g`?\s*\*\*(\d+)\*\*"],
         cmd=[sys.executable, str(OVG)],
         out=[r"(\d+)\s*nálezů Hxx"]),
    dict(jmeno="kronika", drahe=False, druh="stav",
         tvr=[r"`kronika SEDÍ`"],
         cmd=[sys.executable, str(ANALYZA / "kronika-kontrola.py")],
         out=[r"sessions v kronice:\s*(\d+)"]),
    dict(jmeno="handoff", drahe=False, druh="stav",
         tvr=[r"`handoff 0 chybějících`", r"handoff\s*\*\*(\d+)\s*chybějících"],
         cmd=[sys.executable, str(ANALYZA / "handoff-kontrola-uplnost.py")],
         out=[r"CHYBÍ:\s*(\d+)"]),
    # ⚠ DRAHÉ ČÍTAČE SE TADY NEOPAKUJÍ (a je to VĚDOMÉ, ne vynechávka): každý
    # z nich UŽ měří jiná sekce téhož běhu — `kryto` říká KTERÁ. Důvod je čas
    # (p28-b-mutace 18 min, tick-mutace 40 s) a hlavně to, že druhý běh téhož
    # nástroje není druhé měření, jen delší cesta k témuž číslu.
    dict(jmeno="test-tick-offline", drahe=True, druh="meridlo", kryto="C9-4 (`p31-a --plne`)",
         tvr=[r"`test-tick-offline`\s*\*\*(\d+)/(\d+)\*\*"],
         cmd=["node", "tools/test-tick-offline.mjs"],
         out=[r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"]),
    dict(jmeno="tick-mutace", drahe=True, druh="meridlo", kryto="C9-4 (`p31-a --plne`)",
         # ⚠ VZOR TVRZENÍ (opraveno P33): §63 píše `tick-mutace → 20 vrat, 41/0`
         # (hvězdičky tučného písma NEJSOU před číslem) — první verze vzoru je
         # vyžadovala a hlásila „TVRZENÍ se nenašlo“ (H155).
         tvr=[r"`?tick-mutace`?[^\n]{0,20}?(\d+)\s*vrat[/,]\s*(\d+)/(\d+)"],
         cmd=[sys.executable, str(ANALYZA / "tick-mutace.py")],
         out=[r"vrat:\s*(\d+)", r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"], spoj=True),
    dict(jmeno="p29-b6-mutace", drahe=True, druh="meridlo", kryto="C9-4 (`p31-a --plne`)",
         tvr=[r"`p29-b6-mutace`\s*\*\*(\d+)/(\d+)\*\*"],
         cmd=[sys.executable, str(ANALYZA / "p29-b6-mutace.py")],
         out=[r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"]),
    dict(jmeno="p28-b-mutace", drahe=True, druh="meridlo", kryto="C9-4 (`p31-a --plne`)",
         tvr=[r"`p28-b-mutace`\s*\*\*(\d+)/(\d+)\*\*"],
         cmd=[sys.executable, str(P28B)],
         out=[r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"]),
    dict(jmeno="p30-a-overeni", drahe=True, druh="stav", kryto="C9-4 (`p31-a --plne`)",
         tvr=[r"`p30-a`\s*(\d+)/(\d+)"],
         cmd=[sys.executable, str(P30A)],
         out=[r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"]),
    dict(jmeno="p22-test-mutace", drahe=True, druh="meridlo", kryto="C1-a (vlastní běh)",
         # ⚠ VZOR TVRZENÍ (opraveno P33): §63 má TVRZENÍ i CITACI starého stavu
         # (`byl **19/1**` … `→ **20/0**`). Vzor „název + do 40 znaků číslo“
         # trefil CITACI (19/1) a hlásil falešnou chybu — správně se hledá tvar
         # `→ **N/M**`, tedy TVRZENÍ (skill `overovani` §10.1).
         tvr=[r"p22-test-mutace\.py`\s*→\s*\*{0,2}(\d+)/(\d+)\*{0,2}"],
         cmd=[sys.executable, str(P22T)],
         out=[r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb"]),
    dict(jmeno="p32-test-zapis-kotvy", drahe=True, druh="meridlo", kryto="C1-f (vlastní běh)",
         tvr=[r"p32-test-zapis-kotvy[^\n]{0,40}?\*\*(\d+)/(\d+)\*\*"],
         cmd=[sys.executable, str(P32T)],
         out=[r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb"]),
    dict(jmeno="p32-mutace", drahe=True, druh="meridlo", kryto="C1-d (vlastní běh)",
         tvr=[r"p32-mutace\.py`?\s*→\s*\*\*(\d+)/(\d+)\*\*"],
         cmd=[sys.executable, str(P32M)],
         out=[r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb"]),
    dict(jmeno="p30-mutace", drahe=True, druh="meridlo", kryto="C1-c (vlastní běh)",
         tvr=[r"p30-mutace\.py`\s*\*\*(\d+)/(\d+)\*\*"],
         cmd=[sys.executable, str(P30M)],
         out=[r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb"]),
]


def sekce_C3(m, plne):
    p("")
    p("── C3 (A3): SEDÍ ČÍSLA Z §63? (tvrzení se ČTE z dokumentu) ──")
    text63, _, _ = oddil(r"^##\s+63\.")
    for pol in TABULKA:
        if pol.get("kryto") and not plne:
            m.nezmereno("C3 %s: měří %s (tady se neopakuje) — tvrzeno §63" % (pol["jmeno"], pol["kryto"]))
            continue
        if pol["drahe"] and not plne:
            m.nezmereno("C3 %s: drahé (spusť --plne) — tvrzeno §63" % pol["jmeno"])
            continue
        tv, okno, vzor, pocet = tvrzeni(text63, pol["tvr"])
        if tv is None:
            m.ok_(False, "C3 %s: TVRZENÍ se v §63 NENAŠLO — měřidlo by měřilo jinam" % pol["jmeno"])
            continue
        p("            §63 tvrdí: %s   (okno: …%s…)" % ("/".join(tv), okno[-150:]))
        kod, v, tr = spust(pol["cmd"], timeout=3600)
        namer = None
        if pol.get("spoj"):
            # ⚠ NĚKTERÉ ČÍTAČE MAJÍ DVĚ ČÁSTI (tick-mutace: „vrat: N“ +
            # „N kontrol, M chyb“). Skládají se POJMENOVANĚ, ne podle pořadí —
            # past „nástroj tiskne jiný čítač, než jak se jmenuje“ (skill §10.7).
            casti = []
            for vz in pol["out"]:
                mm = list(re.finditer(vz, v))
                if mm:
                    casti += list(mm[-1].groups())
            namer = tuple(casti) if casti else None
        else:
            for vz in pol["out"]:
                mm = list(re.finditer(vz, v))
                if mm:
                    namer = tuple(mm[-1].groups())
                    break
        if namer is None:
            m.nezmereno("C3 %s: výstup nemá čítač (exit=%d, %.0f s) — vzor %s"
                        % (pol["jmeno"], kod, tr, pol["out"][0]))
            continue
        if pol["jmeno"] == "kronika":
            m.ok_("KRONIKA SEDÍ" in v, "C3 kronika: brána hlásí `KRONIKA SEDÍ` (exit=%d)" % kod)
            m.info("C3 kronika: sessions=%s (§63 netvrdí počet; H143 zmínil 45 vs. 46)" % namer[0])
            continue
        if pol["jmeno"] == "handoff":
            m.ok_(namer[0] == "0", "C3 handoff: 0 chybějících (naměřeno %s, exit=%d)" % (namer[0], kod))
            continue
        tvr = tuple(tv[:len(namer)])
        if tvr == namer:
            m.ok_(True, "C3 %s: §63 tvrdí %s a naměřeno %s (exit=%d, %.0f s)"
                  % (pol["jmeno"], "/".join(tvr), "/".join(namer), kod, tr))
        elif pol["druh"] == "stav":
            m.rozdil("C3 %s: §63 tvrdí %s, dnes %s (STAV se posunul, ne vada měřidla)"
                     % (pol["jmeno"], "/".join(tvr), "/".join(namer)))
        else:
            m.ok_(False, "C3 %s: §63 tvrdí %s, NAMĚŘENO %s (exit=%d, %.0f s)"
                  % (pol["jmeno"], "/".join(tvr), "/".join(namer), kod, tr))
    # čísla měřidel, která se v téhle dávce NEPOUŠTĚJÍ (mají vlastní běhy)
    m.nezmereno("C3 `p31-a-overeni.py --plne` (43/5/2/1) — měří sekce C9 (`--jen C9`)")
    m.nezmereno("C3 `p32-a-overeni.py --plne` (51/0+2/0) — měří sekce C9 (`--jen C9`)")
    m.nezmereno("C3 `p31-mutace.py` (24/0) — měří sekce C9 (`--jen C9`)")
    m.nezmereno("C3 `p31-a --jen A1 --plne` (11/0) — měří sekce C9 (`--jen C9`)")


# ── C4 (A4) ─────────────────────────────────────────────────────────────────
def sekce_C4(m, _plne):
    p("")
    p("── C4 (A4): DÁVKA DOKLADŮ NEPŘEPISUJE ŽIVÉ DOKUMENTY? (~35 min) ──")
    pred = {q.name: sha(q) for q in SLEDOVANE}
    kod, v, tr = spust([sys.executable, str(P31A), "--jen", "A4"], timeout=5400)
    po = {q.name: sha(q) for q in SLEDOVANE}
    zmenene = [n for n in pred if pred[n] != po[n]]
    p("            dávka: exit=%d, %.0f s (%d znaků výstupu)" % (kod, tr, len(v)))
    m.ok_(kod == 0, "C4 dávka `p31-a-overeni.py --jen A4` → exit 0")
    m.ok_(not zmenene, "C4 ani JEDEN ze %d sledovaných dokumentů se nezměnil (hash před/po): %s"
          % (len(SLEDOVANE), zmenene or "žádný"))
    m.ok_("žádný z 4 sledovaných dokumentů se nezměnil" in v,
          "C4 pojistka dávky to ŘEKLA: „žádný z 4 sledovaných dokumentů se nezměnil“")
    m.ok_("KDO ZAPSAL" not in v, "C4 sekce „KDO ZAPSAL“ je PRÁZDNÁ (H138)")
    m.ok_("⚠ ZMĚNĚN" not in v, "C4 dávka neohlásila ŽÁDNÝ „ZMĚNĚN“ dokument")
    m.info("C4 doklad dávky: _analyza/p31-a4-davka-vystup.txt")


# ── C5 (A5) ─────────────────────────────────────────────────────────────────
def sekce_C5(m, _plne):
    p("")
    p("── C5 (A5): REGISTR BRAN ──")
    kod, v, tr = spust([sys.executable, str(ANALYZA / "ag-over-cisla.py")], timeout=900)
    m.ok_(kod == 0, "C5 `ag-over-cisla.py` → exit 0 (číslům v AGENTS.md odpovídá zdroj)")
    m.ok_("ROZEŠLO SE: 0" in v, "C5 a `ROZEŠLO SE: 0`")
    mb = re.search(r"bran v registru\s*=\s*(\d+)", v)
    m.ok_(mb and mb.group(1) == "49",
          "C5 tvrzení „bran v registru“ = 49 (naměřeno %s)" % (mb.group(1) if mb else "?"))
    if REGISTR.is_file():
        reg = json.loads(REGISTR.read_text(encoding="utf-8"))
        m.ok_(reg.get("bran_celkem") == 49,
              "C5 `_registr-bran.json` → bran_celkem = %s" % reg.get("bran_celkem"))
    else:
        m.nezmereno("C5 `_registr-bran.json` NENÍ (pusť `g3`)")


# ── C6 (A6) ─────────────────────────────────────────────────────────────────
def sekce_C6(m, plne):
    p("")
    p("── C6 (A6): UKLÍZÍ SE MĚŘIDLA PO SOBĚ? ──")
    if not plne:
        m.nezmereno("C6 (úklidové běhy měřidel) — spusť --plne")
        return
    kod, v, tr = spust([sys.executable, str(P29A), "--jen", "A1M13"], timeout=3600)
    c = citac_text(v)
    m.ok_((kod, c) == (0, ("8", "0")),
          "C6 `p29-a --jen A1M13` → exit 0 a 8/0 (naměřeno %s, %s, %.0f s)" % (kod, c, tr))
    zbyle = sorted(x.name for x in ANALYZA.glob("p29-mut-*"))
    m.ok_(not zbyle, "C6 po A1M13 nezůstal ŽÁDNÝ `p29-mut-*` (%s)" % (zbyle or "žádný"))
    kod, v, tr = spust([sys.executable, str(P29A), "--jen", "A3"], timeout=3600)
    c = citac_text(v)
    m.ok_((kod, c) == (0, ("17", "0")),
          "C6 `p29-a --jen A3` → exit 0 a 17/0 (naměřeno %s, %s, %.0f s)" % (kod, c, tr))
    m.ok_(not (ANALYZA / "p29-kopie-tick.mjs").exists(),
          "C6 (H146) po A3 NEZŮSTALA kopie testu tiku `p29-kopie-tick.mjs`")
    m.ok_(not (ANALYZA / "p32-scratch").exists(), "C6 po P32-testu nezůstal `p32-scratch/`")
    m.ok_(not uklid_po_meridlech(), "C6 v `_analyza/` nejsou zbytky měřidel (%s)"
          % (uklid_po_meridlech() or "žádné"))


# ── C7 (A7) ─────────────────────────────────────────────────────────────────
def sekce_C7(m, plne):
    p("")
    p("── C7 (A7): NIC SE NEROZBILO (inventář → g3 → validate-all, NE současně) ──")
    if not plne:
        m.nezmereno("C7 (g3 + validate-all) — drahé; spusť --plne nebo `--jen C7`")
        return
    m.ok_(pregeneruj_inventar(), "C7 inventář přegenerován PŘED g3 (H126)")
    kod, v, tr = spust([sys.executable, str(G3)], timeout=5400)
    p("            g3: exit=%d, %.0f s" % (kod, tr))
    mb = re.search(r"brán celkem:\s*(\d+)", v)
    mn = re.search(r"NEDEKLAROVANÝCH\s+(\d+)", v)
    m.ok_(mb and mb.group(1) == "49", "C7 g3 měří 49 bran (naměřeno %s)"
          % (mb.group(1) if mb else "?"))
    m.ok_(mn and mn.group(1) == "0", "C7 g3: 0 NEDEKLAROVANÝCH nenulových exitů (naměřeno %s)"
          % (mn.group(1) if mn else "?"))
    # ⚠ H133 (zůstává OTEVŘENÝ): `g3` končí `exit 1` pojmenovaně — jedna brána
    # nemá čítač (`mutace B (combat)`). Kontroluje se POJMENOVANÝ STAV, ne barva:
    # text g3 je „BRÁNY BEZ ČÍTAČE mimo deklarovaný stav: N → …“ (VELKÝMI písmeny).
    mbc = re.search(r"BEZ ČÍTAČE mimo deklarovaný stav:\s*(\d+)\s*→\s*([^\n]*)", v)
    m.ok_(mbc and mbc.group(1) == "1" and "mutace B (combat)" in mbc.group(2),
          "C7 g3 hlásí POJMENOVANĚ 1 bránu bez čítače (`mutace B (combat)`) — H133: %s"
          % (mbc.group(0)[:100] if mbc else "text nenalezen"))
    if kod != 0:
        m.rozdil("C7 `g3` končí exit=%d — je to POJMENOVANÝ stav (1 brána bez čítače: "
                 "`mutace B (combat)`), ne neočekávaný exit; nález H133 zůstává otevřený" % kod)
    kod, v, tr = spust(["node", str(VALIDATE)], timeout=5400)
    p("            validate-all: exit=%d, %.0f s" % (kod, tr))
    m.ok_(kod == 0 and "VŠE V POŘÁDKU" in v,
          "C7 `validate-all` → VŠE V POŘÁDKU a exit 0")
    m.ok_("OK   cron běží (čas)" in v, "C7 brána `cron běží (čas)` je ZELENÁ a měří tep")
    m.ok_("OK   brána cronu umí spadnout" in v, "C7 a její offline fixtury prošly")
    kod, v, _ = git("diff", "--numstat", "HEAD", "--", "HANDOFF.md", "KRONIKA-PROJEKTU.md")
    pridano = smazano = 0
    for l in v.splitlines():
        casti = l.split("\t")
        if len(casti) >= 2 and casti[0].isdigit() and casti[1].isdigit():
            pridano += int(casti[0])
            smazano += int(casti[1])
    p("            necommitnuté záznamy: +%d řádků, -%d řádků" % (pridano, smazano))
    m.ok_(smazano == 0, "C7 v HANDOFF.md ani v KRONICE neubyl ANI JEDEN řádek")


# ── C8 (Úkol B — H112) ──────────────────────────────────────────────────────
def sekce_C8(m, plne):
    p("")
    p("── C8 (Úkol B): H112 — BRÁNA „cron běží (čas)“ UŽ MĚŘÍ TEP CRONU ──")
    # 1) offline fixtury predikátu — brána musí umět SPADNOUT
    kod, v, tr = spust(["node", str(CRON_TEST)], timeout=300)
    m.ok_(kod == 0, "C8-1 offline fixtury predikátu → exit 0 (%.0f s)" % tr)
    m.ok_("8 kontrol, 0 chyb" in v, "C8-1 a čítač je 8/0")
    m.ok_("3 tep 30 min starý → CHYBA" in v, "C8-1 fixtura STARÉHO tepu (cron stojí) je CHYBA")
    m.ok_("4 chybí `last_cron` → CHYBA" in v, "C8-1 fixtura CHYBĚJÍCÍHO tepu je CHYBA")
    m.ok_("8 ruční tik neobnoví `last_cron` → CHYBA" in v,
          "C8-1 fixtura RUČNÍHO tiku je CHYBA (brána měří cron, ne tlačítko)")
    # 2) statická kontrola BRÁNY: ptá se na TEP, ne na `!!h.time`
    src = VALIDATE.read_text(encoding="utf-8")
    m.ok_("'cron běží (čas)', !!h.time" not in src,
          "C8-2 v `validate-all.mjs` NENÍ stará podmínka `!!h.time` (ta nemohla selhat)")
    m.ok_("zhodnotCron(h" in src, "C8-2 brána volá `zhodnotCron(h, …)` (měří tep)")
    m.ok_("test-cron-stav.mjs" in src, "C8-2 a offline fixtury pouští jako SOUČÁST brány")
    m.ok_("cron běží (čas)" in src, "C8-2 jméno kontroly zůstalo (nese ho §63 i kronika)")
    # 3) statická kontrola SLUŽBY: kde se tep bere
    cond = CONDUCTOR.read_text(encoding="utf-8")
    m.ok_('zapisTep(env, "cron")' in cond, "C8-3 conductor zapisuje tep pro `cron` v `scheduled`")
    m.ok_('zapisTep(env, "manual")' in cond, "C8-3 a pro `manual` v `POST /tick`")
    m.ok_(cond.count('if (zdroj === "cron")') == 1,
          "C8-3 `last_cron` se zapisuje JEN pro cron → ruční tik ho NEOBNOVÍ")
    m.ok_("last_cron" in cond and "...tep" in cond, "C8-3 `/health` tep vrací (`...tep`)")
    # 4) ŽIVÝ tep (jen čtení `/health`)
    kod, v, tr = spust(["node", str(SONDA_HEALTH),
                        str(DOKLAD_HEALTH_PO.relative_to(WS))], timeout=300)
    m.ok_(kod == 0, "C8-4 ŽIVÝ `/health` → predikát OK (exit=%d, %.0f s)" % (kod, tr))
    if DOKLAD_HEALTH_PO.is_file():
        j = json.loads(DOKLAD_HEALTH_PO.read_text(encoding="utf-8"))
        m.ok_(j.get("last_cron") is not None, "C8-4 živý `last_cron` = %s" % j.get("last_cron"))
        m.ok_(j.get("last_tick_zdroj") == "cron",
              "C8-4 poslední tik byl zdrojem `cron` (naměřeno %s)" % j.get("last_tick_zdroj"))
        m.ok_(isinstance(j.get("last_cron_min"), (int, float)) and j["last_cron_min"] <= 10,
              "C8-4 a je čerstvý (`last_cron_min` = %s, limit 10)" % j.get("last_cron_min"))
    # 5) ULOŽENÝ stav PŘED nasazením — na TOM musí brána SPADNOUT
    if DOKLAD_HEALTH_PRED.is_file():
        pred = json.loads(DOKLAD_HEALTH_PRED.read_text(encoding="utf-8"))
        kod, v, _ = spust(["node", str(CRON_HELP), str(DOKLAD_HEALTH_PRED.relative_to(WS))],
                          timeout=120)
        m.ok_(kod != 0, "C8-5 nad ULOŽENÝM stavem PŘED nasazením brána SPADNE (exit=%d)" % kod)
        m.ok_("last_cron" in v, "C8-5 a POJMENUJE to (`last_cron` chybí): %s" % v.strip()[:110])
        m.ok_(bool(pred.get("time")),
              "C8-5 STARÁ podmínka `!!h.time` byla nad TÍMŽ vstupem ZELENÁ (time=%s) — "
              "proto H112: brána nemohla selhat" % pred.get("time"))
        m.ok_(pred.get("last_cron") is None and pred.get("last_tick") is None,
              "C8-5 a ten stav opravdu `last_cron` NEMĚL (doklad z 9. 10. 2026 ~23:00)")
    else:
        m.nezmereno("C8-5 doklad stavu před nasazením chybí (%s)" % DOKLAD_HEALTH_PRED.name)
    if not plne:
        m.nezmereno("C8-6 (změna chování: ruční tik neobnoví `last_cron`) — ŽIVĚ se neměří: "
                    "`POST /tick` dispatchuje práci, což offline fixtura č. 8 pokrývá bez zásahu")


# ── C9 (A3-dlouhé) ──────────────────────────────────────────────────────────
def sekce_C9(m, _plne):
    p("")
    p("── C9 (A3-dlouhé): PŘEMĚŘENÍ `p31-a --plne` (43/5/2/1) a `p32-a --plne` (51/0+2/0) ──")
    p("   ⚠ POŘADÍ JE ZÁMĚRNÉ: **nejdřív se MĚŘÍ, teprve pak se hledá tvrzení v §63**.")
    p("      Naměřeno P33 (první běh C9): rozbitý vzor TVRZENÍ (`**` je v §63 jinde,")
    p("      než vzor čekal) **přeskočil 45minutové měření** a C9-4 pak hlásila")
    p("      „běh neproběhl“ — chyba vzoru se tím tvářila jako NEMĚŘENO. Měřidlo,")
    p("      které na chybějící kotvě přeskočí měření, **hlásí méně, než změřilo**.")
    text63, _, _ = oddil(r"^##\s+63\.")
    # 1) měřidlo P32 nad prací P31
    # ⚠ Seam: `P33_C9_PRESKOC=p31-a` přeskočí 36minutovou nohu a čítač vezme
    # z ULOŽENÉHO dokladu (aby se dalo znovu vyhodnotit, co už změřeno je —
    # a nikdy tiše: přeskočení se VYPÍŠE jako NEZMĚŘENO).
    v = ""
    kod, tr = -1, 0.0
    if "p31-a" in P33_C9_PRESKOC:
        m.nezmereno("C9-1 `p31-a --plne` PŘESKOČENO seamem P33_C9_PRESKOC — čítač se čte "
                    "z ULOŽENÉHO dokladu `_analyza/p33-p31a-plne-vystup.txt`")
    else:
        kod, v, tr = spust([sys.executable, str(P31A), "--plne"], timeout=7200)
        _VYSTUP_C9["p31-a --plne"] = v
        (ANALYZA / "p33-p31a-plne-vystup.txt").write_bytes(v.encode("utf-8"))
    if not v:
        ulozeny = ANALYZA / "p33-p31a-plne-vystup.txt"
        if ulozeny.is_file():
            v = ulozeny.read_text(encoding="utf-8")
            _VYSTUP_C9["p31-a --plne"] = v
    mm = list(re.finditer(r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb\s*"
                          r"\(z toho\s*(\d+)\s*pojmenovaných ROZDÍLŮ,\s*(\d+)\s*NEZMĚŘENO\)", v))
    namer = tuple(mm[-1].groups()) if mm else None
    tv, okno, _, _ = tvrzeni(text63, [r"`p31-a-overeni\.py --plne`[^\n]{0,25}?(\d+)\s*kontrol,\s*"
                                      r"(\d+)\s*chyb,\s*(\d+)\s*ROZDÍLY,\s*(\d+)\s*NEZMĚŘENO"])
    p("            naměřeno: %s (exit=%d, %.0f s)" % (namer, kod, tr))
    if tv is None:
        m.ok_(False, "C9-1 §63 netvrdí čítač `p31-a --plne` (měřeno: %s) — vzor tvrzení je vadný"
              % (namer,))
    else:
        p("            §63 tvrdí: %s (okno: …%s…)" % ("/".join(tv), okno[-140:]))
        if namer is None:
            m.ok_(False, "C9-1 `p31-a --plne` nevypsalo čítač (exit=%d) — měřeno nic" % kod)
        elif namer == tv:
            m.ok_(True, "C9-1 `p31-a --plne`: §63 tvrdí %s a naměřeno %s — REPRODUKUJE SE"
                  % ("/".join(tv), "/".join(namer)))
        else:
            m.rozdil("C9-1 `p31-a --plne`: §63 tvrdí %s, naměřeno %s (rozdíl se POJMENOVÁVÁ, "
                     "neschovává)" % ("/".join(tv), "/".join(namer)))
    # 2) vlastní měřidlo P32 (měří se VŽDY; přeskočení je jen přes seam, ne tiše)
    if P33_C9_PRESKOC and "p32-a" in P33_C9_PRESKOC:
        m.nezmereno("C9-2 `p32-a --plne` PŘESKOČENO seamem P33_C9_PRESKOC — změřeno dřív "
                    "(doklad `_analyza/p33-c9-vystup.txt`: 51/0/2/0 = §63.1 SE REPRODUKUJE)")
    else:
        kod2, v2, tr2 = spust([sys.executable, str(P32A), "--plne"], timeout=7200)
        mm2 = list(re.finditer(r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb\s*"
                               r"\(z toho\s*(\d+)\s*pojmenovaných ROZDÍLŮ,\s*(\d+)\s*NEZMĚŘENO\)", v2))
        namer2 = tuple(mm2[-1].groups()) if mm2 else None
        p("            naměřeno: %s (exit=%d, %.0f s)" % (namer2, kod2, tr2))
        tv2, okno2, _, _ = tvrzeni(text63, [r"Plný běh:[^\n]{0,15}?(\d+)\s*kontrol,\s*(\d+)\s*chyb,\s*"
                                            r"(\d+)\s*pojmenované ROZDÍLY,\s*(\d+)\s*NEZMĚŘENO"])
        if tv2 is None:
            m.ok_(False, "C9-2 §63 netvrdí čítač `p32-a --plne` (měřeno: %s)" % (namer2,))
        else:
            p("            §63 tvrdí: %s (okno: …%s…)" % ("/".join(tv2), okno2[-140:]))
            if namer2 is None:
                m.ok_(False, "C9-2 `p32-a --plne` nevypsalo čítač (exit=%d)" % kod2)
            elif namer2 == tv2:
                m.ok_(True, "C9-2 `p32-a --plne`: §63 tvrdí %s a naměřeno %s — REPRODUKUJE SE"
                      % ("/".join(tv2), "/".join(namer2)))
            else:
                m.rozdil("C9-2 `p32-a --plne`: §63 tvrdí %s, naměřeno %s"
                         % ("/".join(tv2), "/".join(namer2)))
    # 3) dlouhé mutační důkazy, na kterých §63 stojí
    # 3) dlouhé mutační důkazy, na kterých §63 stojí — MĚŘÍ SE PRVNÍ, tvrzení se
    #    hledá potom (vzor tvrzení nesmí umět přeskočit měření).
    for jmeno, skript, tvr_vzor, ocekavane in (
            ("p31-mutace", P31M, r"`p31-mutace\.py`[^\n]{0,25}?(\d+)/(\d+)", ("24", "0")),
            ("p31-a --jen A1 --plne", P31A,
             r"`p31-a-overeni\.py --jen A1 --plne`[^\n]{0,25}?(\d+)/(\d+)", ("11", "0"))):
        klic = "p31-mutace" if jmeno == "p31-mutace" else "p31-a1"
        if klic in P33_C9_PRESKOC:
            # 5) seam: noha se přeskočí a čítač se vezme z ULOŽENÉHO dokladu C9
            stary_dok = ANALYZA / "p33-c9-vystup.txt"
            c = None
            if stary_dok.is_file():
                mm5 = [m5 for m5 in re.finditer(
                    r"C9-3 %s[^\n]{0,80}?naměřeno\s*\((\d+), (\d+)\)" % re.escape(jmeno),
                    stary_dok.read_text(encoding="utf-8"))]
                c = tuple(mm5[-1].groups()) if mm5 else None
            m.nezmereno("C9-3 %s PŘESKOČENO seamem — z uloženého dokladu: %s" % (jmeno, c))
            if c is None:
                continue
        else:
            if jmeno == "p31-a --jen A1 --plne":
                cmd = [sys.executable, str(P31A), "--jen", "A1", "--plne"]
            else:
                cmd = [sys.executable, "-B", str(skript)]
            kod, v, tr = spust(cmd, timeout=7200)
            c = citac_text(v)
            p("            naměřeno: %s (exit=%d, %.0f s)" % (c, kod, tr))
        tv3, okno3, _, _ = tvrzeni(text63, [tvr_vzor])
        p("            naměřeno: %s (exit=%d, %.0f s)" % (c, kod, tr))
        if tv3 is None:
            m.ok_(False, "C9-3 %s: §63 netvrdí čítač (naměřeno %s) — vzor tvrzení je vadný"
                  % (jmeno, c))
            continue
        p("            §63 tvrdí u %s: %s (okno: …%s…)" % (jmeno, "/".join(tv3), okno3[-120:]))
        if c is None:
            m.ok_(False, "C9-3 %s nevypsalo čítač (exit=%d, %.0f s) — měřeno nic" % (jmeno, kod, tr))
        elif (c == tuple(tv3[:2]) and c == ocekavane):
            m.ok_(True, "C9-3 %s: §63 tvrdí %s a naměřeno %s (exit=%d, %.0f s)"
                  % (jmeno, "/".join(tv3), "/".join(c), kod, tr))
        else:
            m.rozdil("C9-3 %s: §63 tvrdí %s, naměřeno %s (exit=%d)"
                     % (jmeno, "/".join(tv3), "/".join(c), kod))
    # 4) čítače, které UŽ změřil běh `p31-a --plne` ve své sekci A3 (neopisují se
    #    z hlavy — čtou se z JEHO výstupu; kdyby je neměřil, je to NEZMĚŘENO).
    p("            čítače z běhu `p31-a --plne` (sekce A3) — bez druhého běhu téhož:")
    v31 = _VYSTUP_C9.get("p31-a --plne")
    if not v31:
        m.nezmereno("C9-4 čítače z `p31-a --plne` — běh neproběhl")
    else:
        for jmeno, tvr_vzor, ocekavane in (
                ("p28-b-mutace", r"`p28-b-mutace`[^\n]{0,20}?(\d+)/(\d+)", ("30", "0")),
                ("test-tick-offline", r"`test-tick-offline`[^\n]{0,20}?(\d+)/(\d+)", ("215", "0")),
                ("over-skilly", r"`over-skilly`[^\n]{0,20}?(\d+)/(\d+)", ("92", "0")),
                ("over-dokumentaci", r"`over-dokumentaci`[^\n]{0,20}?(\d+)/(\d+)", ("64", "0")),
                ("p29-b6-mutace", r"`p29-b6-mutace`[^\n]{0,20}?(\d+)/(\d+)", ("15", "0")),
                ("p30-mutace", r"`p30-mutace\.py`[^\n]{0,20}?(\d+)/(\d+)", ("16", "0")),
                ("p30-a", r"`p30-a`[^\n]{0,20}?(\d+)/(\d+)", ("32", "3")),
                ("tick-mutace", r"`?tick-mutace`?[^\n]{0,20}?(\d+)\s*vrat[/,]\s*(\d+)/(\d+)",
                 ("20", "41", "0"))):
            # ⚠ ČÍTAČ SE ČTE Z ŘÁDKU `… naměřeno ('N', 'M') …` v dokladu `p31-a --plne`
            # — počet čísel se bere z TOHO, co nástroj vypsal (tick-mutace má tři).
            mm = None
            for m2 in re.finditer(r"%s[^\n]{0,160}?naměřeno\s*\(([^)]*)\)" % re.escape(jmeno), v31):
                mm = m2
            if mm is None:
                m.nezmereno("C9-4 %s: v výstupu `p31-a --plne` se čítač nenašel" % jmeno)
                continue
            cisla = tuple(re.findall(r"\d+", mm.group(1)))
            tv4, okno4, _, _ = tvrzeni(text63, [tvr_vzor])
            if tv4 is None:
                m.ok_(False, "C9-4 %s: §63 netvrdí čítač (naměřeno %s) — vzor tvrzení je vadný"
                      % (jmeno, "/".join(cisla)))
                continue
            if cisla == tuple(tv4) == ocekavane:
                m.ok_(True, "C9-4 %s: §63 tvrdí %s a v běhu `p31-a --plne` naměřeno %s"
                      % (jmeno, "/".join(tv4), "/".join(cisla)))
            else:
                m.rozdil("C9-4 %s: §63 tvrdí %s, v běhu `p31-a --plne` naměřeno %s"
                         % (jmeno, "/".join(tv4), "/".join(cisla)))


# ── main ────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jen", default=None, help="seznam sekcí, např. C8 nebo C9")
    ap.add_argument("--plne", action="store_true", help="i kontramutace, úklid a živé sondy")
    ap.add_argument("--vystup", default=None)
    args = ap.parse_args()

    vystup = pathlib.Path(args.vystup) if args.vystup else DOKLAD
    if not vystup.is_absolute():
        vystup = WS / vystup
    m = Meridlo()
    # ⚠ C1/C6/C7 se v LEVNÉM režimu NEměří: C1 pouští mutační běhy (mění živé
    # soubory), C6 úklidová měřidla a C7 `g3` + `validate-all`. Do dávky dokladů
    # (`p20-d-doklady.py`) proto patří JEN levný režim — jinak by dávka mutovala
    # sledované dokumenty, což je přesně to, před čím je její pojistka.
    fns = {
        "C0": lambda: sekce_C0(m),
        "C1": lambda: sekce_C1(m, args.plne or ("C1" in etapy)),
        "C2": lambda: sekce_C2(m, args.plne or ("C2" in etapy)),
        "C3": lambda: sekce_C3(m, args.plne),
        "C4": lambda: sekce_C4(m, args.plne),
        "C5": lambda: sekce_C5(m, args.plne),
        "C6": lambda: sekce_C6(m, args.plne or ("C6" in etapy)),
        "C7": lambda: sekce_C7(m, args.plne or ("C7" in etapy)),
        "C8": lambda: sekce_C8(m, args.plne),
        "C9": lambda: sekce_C9(m, args.plne),
    }
    vychozi = ("C0,C2,C3,C5,C8" if not args.plne else "C0,C1,C2,C3,C5,C6,C7,C8")
    etapy = [x.strip().upper() for x in (args.jen if args.jen else vychozi).split(",")]
    p("=" * 88)
    p("P33/A — VLASTNÍ PŘEMĚŘENÍ PRÁCE P32 + ZAVŘENÍ H112")
    p("=" * 88)
    p("  datum (z hodin): %s" % time.strftime("%Y-%m-%d %H:%M:%S %z"))
    p("  dokument, ze kterého se ČTOU TVRZENÍ: %s" % HANDOFF.name)
    p("  pořadí běhu: %s%s" % (", ".join(etapy), "  (--plne)" if args.plne else "  (levný režim)"))
    p("  ⚠ C4 (dávka dokladů, ~35 min) a C9 (p31-a/p32-a --plne, ~80 min) se pouští JEN `--jen`")
    for e in etapy:
        f = fns.get(e)
        if f is None:
            p("  ??    etapa %s neexistuje" % e)
            continue
        p("\n" + "─" * 88)
        t0 = time.time()
        try:
            f()
        except Exception as ex:  # noqa: BLE001
            import traceback  # noqa: PLC0415
            tb = traceback.format_exc().strip().splitlines()
            p("      TRACEBACK: %s" % " | ".join(x.strip() for x in tb[-3:]))
            m.nezmereno("etapa %s: výjimka %s: %s" % (e, type(ex).__name__, str(ex)[:200]))
        p("      (etapa %s: %.0f s)" % (e, time.time() - t0))
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
    if SCRATCH.exists() and not any(SCRATCH.iterdir()):
        SCRATCH.rmdir()
    vystup.write_bytes(("\n".join(_vystup) + "\n").encode("utf-8"))
    print("\n[doklad] %s (%d B, UTF-8)" % (vystup.relative_to(WS), vystup.stat().st_size))
    return 1 if m.chyby else 0


if __name__ == "__main__":
    sys.exit(main())
