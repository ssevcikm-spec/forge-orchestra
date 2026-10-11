# -*- coding: utf-8 -*-
r"""P34 — VLASTNÍ PŘEMĚŘENÍ PRÁCE P33 (Úkol A) + PŘÍČINA VÝPADKU CRONU (Úkol B, H156).

CO TENHLE DOKLAD DĚLÁ A ČÍM SE LIŠÍ OD MĚŘIDLA P33:
  * Měří **A1–A8 zadání P34** (`NEXT-SESSION-INSTRUKCE.md` §2.1) — ne C0–C9 P33.
    Měřidlo P33 je přitom jen JEDEN Z MĚŘENÝCH PŘEDMĚTŮ (sekce A3), ne základ.
  * **Tvrzení se NEČTOU Z HLAVY**: nejdřív se MĚŘÍ, teprve pak se hledá tvrzení
    v §64 (H155) — a **nenalezené tvrzení je CHYBA**, ne přeskočení.
  * **Diferenciál cronu (A1) je TŘÍVRSTVÝ a v KOPIÍCH** (zadání to žádá):
    (a) predikát bez kontroly stáří, (b) fixtura s `last_cron: null`,
    (c) predikát s VRÁCENOU STAROU logikou `!!h.time` nad ULOŽENÝM
    před-nasazovacím stavem — tam musí být **ZELENÝ** (to je důkaz, že vada
    existovala). Kopie jsou BAJT NA BAJT shodné s živými (`sha256`) a živé
    soubory se přitom NEMUTUJÍ.
  * **Úkol B (H156) = PŘÍČINA, ne okno**: čte se ze TŘÍ nezávislých dokladů —
    Cloudflare Analytics (historie invokací a `outcome`), `wrangler tail` (živý
    cron event) a D1 `state` (uložený tep) — a měřidlo ověřuje, že na sebe
    navazují. **Živý výpadek je NÁLEZ O SLUŽBĚ, ne vada měřidla** (zadání §2.1/A8).
  * **Umí selhat** — `_analyza/p34-mutace.py` (doklad, že měřidlo není ani
    „vždy zelené“, ani „vždy červené“).

SEKCE A POUŽITÍ:
    python _analyza\p34-a-overeni.py            # LEVNÉ (A0,A1,A2,A5,A8,B1; ~1 min)
    python _analyza\p34-a-overeni.py --plne     # i A3, A6, A7 (mutace, g3, validate-all)
    python _analyza\p34-a-overeni.py --jen A1   # jedna sekce (u A2/A3/A6/A7 i drahé nohy)
    python _analyza\p34-a-overeni.py --jen A4   # dávka dokladů (hodiny; v P33 nedoběhla)
  A0  pojistky (co měřidlo předpokládá)
  A1  (A1) umí brána cronu spadnout? fixtury + TŘI vady v kopiích
  A2  (A2) co P33 nasadila? (git) + nasazení TŘEMI kroky s PLNÝM sha
  A3  (A3) sedí čísla z §64? (nejdřív měřit, pak hledat tvrzení)
  A4  (A4) dávka dokladů nic nezapisuje (jen `--jen A4`, dlouhé)
  A5  (A5) registr bran (49) proti číslu v `AGENTS.md`
  A6  (A6) uklízí se měřidla po sobě?
  A7  (A7) nic se nerozbilo (inventář → g3 → validate-all, NE současně)
  A8  (A8) žije cron? (ŽIVÝ tep; když ne, je to stav SLUŽBY)
  B1  (Úkol B) H156 — PŘÍČINA výpadku: Analytics + tail + D1

POUŽITÍ SEAMŮ (pro `p34-mutace.py`):
  P34_HANDOFF=<kopie HANDOFF.md>   — měřidlo čte tvrzení z KOPIE, ne z živého
  P34_HEALTH=<json s /health>      — měřidlo hodnotí PODSTRČENÝ stav služby
  P34_CF=<json analytiky>          — měřidlo čte PODSTRČENÝ doklad analytiky
  P34_TAIL=<jsonl živých eventů>   — měřidlo čte PODSTRČENÝ doklad tailu
  P34_D1=<json tabulky state>      — měřidlo čte PODSTRČENÝ uložený tep

⚠ Výchozí doklad je `p34-a-overeni-levny-vystup.txt`, s `--plne`/`--jen`
  `p34-a-overeni-vystup.txt`. Důvod: dávka dokladů (`p20-d-doklady.py`) pouští
  tenhle skript v LEVNÉM režimu, takže by plný doklad přepsala — a přepsaný
  doklad je ztracený důkaz.
⚠ `--plne`/`--jen A3,A6,A7` POUŠTÍ MUTAČNÍ BĚHY jiných měřidel (pod `mutuj`,
  tedy s návratem bajt na bajt) a `g3`/`validate-all`. **Během plného běhu se
  do stromu NEPÍŠE** (H154).
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
from datetime import datetime, timedelta, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
TOOLS = WS / "tools"
GIT = TOOLS / "git.cmd"
HANDOFF = pathlib.Path(os.environ.get("P34_HANDOFF") or (WS / "HANDOFF.md"))
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
NEXT = WS / "NEXT-SESSION-INSTRUKCE.md"
REGISTR = ANALYZA / "_registr-bran.json"

CRON_PRED = TOOLS / "cron-stav.mjs"
CRON_TEST = TOOLS / "test-cron-stav.mjs"
VALIDATE = TOOLS / "validate-all.mjs"
G3 = ANALYZA / "g3-brany.py"
AG_OVER = ANALYZA / "ag-over-cisla.py"
INVENTAR = ANALYZA / "hl-neanglicky-v-kodu.py"
KRONIKA_K = ANALYZA / "kronika-kontrola.py"
HANDOFF_K = ANALYZA / "handoff-kontrola-uplnost.py"
OVG = ANALYZA / "ov-g-neovereno.py"
P33A = ANALYZA / "p33-a-overeni.py"
P33M = ANALYZA / "p33-mutace.py"
P29A = ANALYZA / "p29-a-overeni.py"
P22T = ANALYZA / "p22-test-mutace.py"
P32T = ANALYZA / "p32-test-zapis-kotvy.py"
P20D = ANALYZA / "p20-d-doklady.py"
SONDA_HEALTH = ANALYZA / "p33-sonda-health.mjs"
SONDA_DEPLOY = ANALYZA / "p30-sonda-deploy.mjs"
SONDA_CF = ANALYZA / "p32-sonda-cf-verze.mjs"
CONDUCTOR = WS / "conductor" / "src" / "index.ts"

# ── doklady, které měřidlo ČTE (neopisuje z hlavy) ───────────────────────────
HEALTH_PRED = ANALYZA / "p33-health-pred-vystup.txt"      # stav PŘED nasazením H112
HEALTH_LIVE = pathlib.Path(os.environ.get("P34_HEALTH") or (ANALYZA / "p34-health-vystup.txt"))
CF_DOKLAD = pathlib.Path(os.environ.get("P34_CF") or (ANALYZA / "p34-cf-analytika-vystup.txt"))
TAIL_DOKLAD = pathlib.Path(os.environ.get("P34_TAIL") or (ANALYZA / "p34-tail-cron-plny-vystup.txt"))
D1_DOKLAD = pathlib.Path(os.environ.get("P34_D1") or (ANALYZA / "p34-d1-state-vystup.txt"))
TAIL_RAW = ANALYZA / "p34-tail-raw-vystup.txt"

SCRATCH = ANALYZA / "p34-scratch"
DOKLAD_PLNY = ANALYZA / "p34-a-overeni-vystup.txt"
DOKLAD_LEVNY = ANALYZA / "p34-a-overeni-levny-vystup.txt"

ENV = dict(os.environ, PYTHONIOENCODING="utf-8")   # PLNÉ prostředí (ne ořezané!)
_vystup = []
# Čísla NAMĚŘENÁ jednotlivými sekcemi; A3 (tvrzení) je čte odsud — a je proto
# v pořadí POSLEDNÍ („měř dřív, než hledáš tvrzení“, H155).
MERENO = {}
# Doklad se zapisuje PRŮBĚŽNĚ (viz `p()`) — přerušený dlouhý běh tak neztratí,
# co už naměřil (P33: „naměřený čas není odpracovaný čas“).
_doklad_handle = None


# ── infrastruktura ───────────────────────────────────────────────────────────
def p(radek=""):
    print(radek)
    _vystup.append(radek)
    if _doklad_handle is not None:
        _doklad_handle.write(radek + "\n")
        _doklad_handle.flush()


def spust(cmd, timeout=1800, env=None):
    t0 = time.time()
    try:
        r = subprocess.run([str(a) for a in cmd], cwd=str(WS), env={**ENV, **(env or {})},
                           capture_output=True, timeout=timeout)
        out = ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace")
        return r.returncode, out, time.time() - t0
    except subprocess.TimeoutExpired:
        return -9, "TIMEOUT po %d s" % timeout, time.time() - t0
    except Exception as e:  # noqa: BLE001
        return -1, "SPUŠTĚNÍ SELHALO: %s" % e, time.time() - t0


def citac(t):
    """Poslední čítač `VÝSLEDEK: N kontrol, M chyb`."""
    vse = list(re.finditer(r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb", t))
    return (vse[-1].group(1), vse[-1].group(2)) if vse else None


def oddil(vzor, cesta=None):
    """(text, první řádek, poslední řádek) oddílu úrovně `##` — jinak SystemExit."""
    cesta = pathlib.Path(cesta or HANDOFF)
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


def najdi_tvrzeni(text, vzory):
    """Poslední výskyt vzoru + OKNO, které trefil. Vrací (m, okno, vzor).

    ⚠ H155: nenalezené tvrzení je CHYBA volajícího, ne ticho. Okno se VYPISUJE
    proto, aby bylo vidět, KTERÝ výskyt vzor trefil (ne jen že „něco našel“).
    """
    for v in vzory:
        vse = list(re.finditer(v, text))
        if vse:
            m = vse[-1]
            okno = text[max(0, m.start() - 60): m.end() + 60].replace("\n", " / ")
            return m, okno, v
    return None, None, None


def sha(cesta):
    return hashlib.sha256(pathlib.Path(cesta).read_bytes()).hexdigest()


def git(*args, timeout=300):
    return spust([str(GIT), "-C", str(WS), *args], timeout=timeout)


class Meridlo:
    """Čtyři druhy výsledku: CHYBA měřidla, ROZDÍL stavu, NEZMĚŘENO a NÁLEZ
    O SLUŽBĚ (stav měřeného objektu — NENÍ to chyba měřidla, a proto nemění
    `exit` kód; zadání §2.1/A8 to tak chce)."""

    def __init__(self):
        self.ok = 0
        self.chyby = []
        self.rozdily = []
        self.nezmerene = []
        self.sluzba = []

    def _v(self, stav, text):
        p("  %-10s %s" % (stav, text))
        if stav == "OK":
            self.ok += 1
        elif stav == "CHYBA":
            self.chyby.append(text)

    def ok_(self, podminka, text):
        self._v("OK" if podminka else "CHYBA", text)
        return bool(podminka)

    def rozdil(self, text):
        p("  ROZDÍL     %s" % text)
        self.rozdily.append(text)

    def nezmereno(self, text):
        p("  NEZMĚŘENO  %s" % text)
        self.nezmerene.append(text)

    def nalezeno(self, text):
        p("  NÁLEZ      %s" % text)
        self.sluzba.append(text)

    def info(self, text):
        p("  INFO       %s" % text)


# ── A0: pojistky ─────────────────────────────────────────────────────────────
def sekce_A0(m):
    p("A0) POJISTKY — co měřidlo předpokládá (a co by ho poslalo měřit jinam)")
    for cesta, popis in [
        (CRON_PRED, "predikát brány `tools/cron-stav.mjs`"),
        (CRON_TEST, "offline fixtury `tools/test-cron-stav.mjs`"),
        (VALIDATE, "brána `tools/validate-all.mjs`"),
        (G3, "souhrn bran `_analyza/g3-brany.py`"),
        (AG_OVER, "`_analyza/ag-over-cisla.py`"),
        (P33A, "měřidlo P33 `_analyza/p33-a-overeni.py`"),
        (P33M, "mutační důkaz P33 `_analyza/p33-mutace.py`"),
        (HEALTH_PRED, "ULOŽENÝ stav PŘED nasazením H112 (`/health` bez `last_cron`)"),
        (CONDUCTOR, "kód conductora"),
    ]:
        m.ok_(cesta.is_file(), "%s existuje (%s)" % (popis, cesta.name))

    kod, out, _ = git("rev-parse", "HEAD")
    p("  INFO       orchestra HEAD = %s" % out.strip()[:12])
    m.ok_(kod == 0, "git v orchestra funguje (rev-parse exit=%d)" % kod)

    try:
        h = json.loads(HEALTH_PRED.read_text(encoding="utf-8"))
        m.ok_("last_cron" not in h,
              "před-nasazovací stav `last_cron` NEMÁ (proto na něm stará kontrola `!!h.time` nemohla selhat)")
        m.ok_(bool(h.get("time")), "a `time` MÁ (proto na něm stará kontrola ZELENÁ byla)")
    except Exception as e:  # noqa: BLE001
        m.ok_(False, "před-nasazovací doklad se nedá přečíst: %s" % e)

    zbyle = [x.name for x in ANALYZA.glob("p34-scratch*")] + \
            [x.name for x in ANALYZA.glob("p34-mutace-scratch*")]
    m.ok_(not zbyle, "po předchozích bězích nezůstal scratch (%s)" % (zbyle or "nic"))


# ── A1: umí brána cronu spadnout? (fixtury + diferenciál v KOPIÍCH) ──────────
def sekce_A1(m):
    p("")
    p("A1) UMÍ OPRAVA H112 SPADNOUT? fixtury + tři vady v KOPIÍCH")

    sha_test0, sha_pred0 = sha(CRON_TEST), sha(CRON_PRED)

    kod, out, sec = spust(["node", str(CRON_TEST)], timeout=120)
    c = citac(out)
    m.ok_(kod == 0, "živá brána `tools/test-cron-stav.mjs` → exit 0 (naměřeno %d, %.0f s)" % (kod, sec))
    m.ok_(c == ("8", "0"), "a její čítač je 8/0 (naměřeno %s)" % (c,))

    SCRATCH.mkdir(parents=True, exist_ok=True)
    kopie_test = SCRATCH / "test-cron-stav.mjs"
    kopie_pred = SCRATCH / "cron-stav.mjs"
    shutil.copyfile(CRON_TEST, kopie_test)
    shutil.copyfile(CRON_PRED, kopie_pred)
    m.ok_(sha(kopie_test) == sha_test0, "kopie fixtur je BAJT NA BAJT shodná s živými")
    m.ok_(sha(kopie_pred) == sha_pred0, "kopie predikátu je BAJT NA BAJT shodná s živým")
    kod, out, _ = spust(["node", str(kopie_test)], timeout=120)
    c = citac(out)
    m.ok_(kod == 0 and c == ("8", "0"),
          "a NEMUTOVANÁ kopie dává TOTÉŽ (exit=%d, %s) — kopie tedy měří, ne jen existuje" % (kod, c))

    # ── (a) predikát BEZ kontroly stáří ──────────────────────────────────────
    pred_txt = kopie_pred.read_text(encoding="utf-8")
    kotva_a = "  if (min > limitMin) {"
    m.ok_(pred_txt.count(kotva_a) == 1, "kotva (a) je v predikátu PRÁVĚ 1× (jinak by mutace trefila jinam)")
    vada_a = pred_txt.replace(kotva_a, "  if (false) {", 1)
    m.ok_(vada_a != pred_txt and vada_a.count("  if (false) {") == 1,
          "(a) MUTACE SE PROVEDLA: kontrola stáří je v kopii pryč")
    kopie_pred.write_text(vada_a, encoding="utf-8")
    ted = datetime.now(timezone.utc)
    stare = {"last_cron": (ted - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
             "last_tick_zdroj": "cron", "time": ted.strftime("%Y-%m-%dT%H:%M:%S.000Z")}
    soubor = SCRATCH / "health-30min.json"
    soubor.write_text(json.dumps(stare), encoding="utf-8")
    kod, out, _ = spust(["node", str(kopie_pred), str(soubor)], timeout=60)
    m.ok_(kod == 0, "(a) MUTOVANÝ predikát nad 30 min starým tepem tvrdí OK (exit=%d) — kontrola stáří je NOSNÁ" % kod)
    kod, out, _ = spust(["node", str(kopie_test)], timeout=120)
    m.ok_(kod != 0, "(a) a BRÁNA (fixtury) nad tou vadou SPADNE (exit=%d)" % kod)
    m.ok_("CHYBA 3 tep 30 min starý" in out, "(a) a spadne PRÁVĚ na fixtuře 3 („tep 30 min starý“), ne jinde")

    # ── (b) fixtura s `last_cron: null` ──────────────────────────────────────
    shutil.copyfile(CRON_TEST, kopie_test)
    shutil.copyfile(CRON_PRED, kopie_pred)
    fx = kopie_test.read_text(encoding="utf-8")
    kotva_b = "    { last_cron: iso(0.5), last_tick: iso(0.5), last_tick_zdroj: 'cron' }, NYNI);"
    m.ok_(fx.count(kotva_b) == 1, "kotva (b) je ve fixturách PRÁVĚ 1×")
    fx2 = fx.replace(kotva_b,
                     "    { last_cron: null, last_tick: iso(0.5), last_tick_zdroj: 'cron' }, NYNI);", 1)
    m.ok_(fx2 != fx, "(b) MUTACE SE PROVEDLA: fixtura 1 má `last_cron: null`")
    kopie_test.write_text(fx2, encoding="utf-8")
    kod, out, _ = spust(["node", str(kopie_test)], timeout=120)
    m.ok_(kod != 0, "(b) BRÁNA nad fixturou bez tepu SPADNE (exit=%d)" % kod)
    m.ok_("CHYBA 1 čerstvý tep" in out, "(b) a spadne PRÁVĚ na fixtuře 1")

    # ── (c) predikát s VRÁCENOU starou logikou `!!h.time` ────────────────────
    shutil.copyfile(CRON_TEST, kopie_test)
    shutil.copyfile(CRON_PRED, kopie_pred)
    pt = kopie_pred.read_text(encoding="utf-8")
    kotva_c = "export function zhodnotCron(h, nyni = Date.now(), limitMin = VYCHOZI_LIMIT_MIN) {"
    m.ok_(pt.count(kotva_c) == 1, "kotva (c) je v predikátu PRÁVĚ 1×")
    stary = kotva_c + "\n  return { ok: !!h.time, duvod: 'STARA KONTROLA (!!h.time) — o cronu netvrdí nic' };"
    pt2 = pt.replace(kotva_c, stary, 1)
    m.ok_(pt2 != pt, "(c) MUTACE SE PROVEDLA: predikát má zpět starou logiku `!!h.time`")
    kopie_pred.write_text(pt2, encoding="utf-8")
    kod_mut, _, _ = spust(["node", str(kopie_pred), str(HEALTH_PRED)], timeout=60)
    m.ok_(kod_mut == 0,
          "(c) STARÁ logika nad ULOŽENÝM před-nasazovacím stavem je ZELENÁ (exit=%d) — proto H112" % kod_mut)
    shutil.copyfile(CRON_PRED, kopie_pred)
    kod_new, out_new, _ = spust(["node", str(kopie_pred), str(HEALTH_PRED)], timeout=60)
    m.ok_(kod_new != 0, "(c) a NOVÁ logika nad TÝMŽ vstupem SPADNE (exit=%d) — vada je opravdu zavřená" % kod_new)
    m.ok_("last_cron" in out_new, "(c) a pojmenuje to POJMENOVANĚ („neposílá last_cron“)")

    # ── úklid + návrat ───────────────────────────────────────────────────────
    shutil.rmtree(SCRATCH, ignore_errors=True)
    m.ok_(not SCRATCH.exists(), "scratch `p34-scratch/` je uklizený")
    m.ok_(sha(CRON_TEST) == sha_test0, "živé fixtury jsou po testu BAJT NA BAJT původní (mutovaly se jen kopie)")
    m.ok_(sha(CRON_PRED) == sha_pred0, "živý predikát je po testu BAJT NA BAJT původní (mutovaly se jen kopie)")


# ── A2: co P33 nasadila + nasazení třemi kroky ───────────────────────────────
def sekce_A2(m, drahe):
    p("")
    p("A2) CO P33 NASADILA? (git) — a je to nasazené? (tři kroky, PLNÝ sha)")

    kod, out, _ = git("rev-parse", "675f13a")
    full = out.strip()
    m.ok_(kod == 0 and len(full) == 40,
          "plný sha `675f13a` = %s (H153: GitHub API chce PLNÝ sha)" % full[:12])

    kod, out, _ = git("show", "--name-only", "--format=", "675f13a")
    soubory = [x for x in out.splitlines() if x.strip()]
    m.ok_(kod == 0 and soubory == ["conductor/src/index.ts"],
          "675f13a mění PRÁVĚ `conductor/src/index.ts` (naměřeno %s)" % (soubory or "nic"))

    kod, out, _ = git("show", "--name-only", "--format=", "62df458")
    vse = [x for x in out.splitlines() if x.strip()]
    m.ok_(kod == 0 and not any(x.startswith("conductor/") for x in vse),
          "62df458 (P33 záznamy+měřidla) NEMÁ v sobě `conductor/` (naměřeno %d souborů)" % len(vse))

    kod, out, _ = git("rev-parse", "HEAD")
    head = out.strip()
    m.ok_(kod == 0, "HEAD orchestra = %s" % head[:12])
    kod, out, _ = spust([str(GIT), "ls-remote", "origin", "refs/heads/main"], timeout=180)
    remote = out.split()[0] if out.split() else "?"
    m.ok_(remote == head, "KROK 1 ls-remote: origin/main == HEAD (%s == %s)" % (remote[:12], head[:12]))

    if not drahe:
        m.nezmereno("A2 kroky 2 a 3 (deploy.yml na commitu + verze z logu) — pouští se s --plne/--jen A2")
        return
    kod, out, sec = spust(["node", str(SONDA_DEPLOY), full], timeout=900)
    m.ok_(kod == 0 and "completed/success" in out,
          "KROK 2 `deploy.yml` na TOM commitu → completed/success (exit=%d, %.0f s)" % (kod, sec))
    m.info("       %s" % " | ".join(x.strip() for x in out.splitlines() if x.strip())[:220])
    kod, out, sec = spust(["node", str(SONDA_CF), full], timeout=900)
    m.ok_(kod == 0, "KROK 3 VERZE z LOGU nasazení (exit=%d, %.0f s)" % (kod, sec))
    m.info("       %s" % " | ".join(x.strip() for x in out.splitlines() if x.strip())[:220])
    verze = re.search(r"Current Version ID:\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", out)
    if verze and TAIL_RAW.is_file() and TAIL_RAW.stat().st_size:
        tail = TAIL_RAW.read_text(encoding="utf-8", errors="replace")
        m.ok_(verze.group(1) in tail,
              "a TU SAMOU verzi posílá i ŽIVÝ event v `wrangler tail` (%s)" % verze.group(1)[:8])
    elif verze is None:
        # ⚠ NAMĚŘENO PŘED OPRAVOU (P34): první verze vzala PRVNÍ UUID v logu —
        # a to je `Worker ID: {9195eb73-…}`, ne verze. Kontrola pak hlásila
        # „verze nesedí“, ačkoli log na jiném řádku posílá `Current Version ID:
        # d21a7911-…` = přesně tu, kterou posílá živý tail. Táž třída jako H152:
        # **ptať se, KTERÝ výskyt vzor trefil.**
        m.ok_(False, "v logu nasazení NENÍ `Current Version ID` — verzi nelze srovnat s živým tailem")
    else:
        m.nezmereno("křížová kontrola verze z logu vs. živý `wrangler tail` (chybí doklad %s)"
                    % TAIL_RAW.name)


# ── A3: sedí čísla z §64? ────────────────────────────────────────────────────
def sekce_A3(m, drahe):
    p("")
    p("A3) SEDÍ ČÍSLA Z §64 (a z §0.3 zadání)? — nejdřív se MĚŘÍ, teprve pak hledá tvrzení (H155)")

    # ⚠ `p33-a-overeni.py --plne` je ZVLÁŠŤ: pouští uvnitř `g3` + `validate-all`
    # (druhý nejdelší běh) a jeho C1 pouští `p28-b-mutace.py` (22 min) — naměřeno
    # P34: po 45 min nebyl hotový a přechodné soubory `_p28b-*` už rozcházely
    # otisk inventáře (H154). Pouští se proto JEN na výslovné přání:
    #   P34_P33PLNE=1 python _analyza\p34-a-overeni.py --jen A3
    if drahe and os.environ.get("P34_P33PLNE") == "1":
        kod, out, sec = spust([sys.executable, "-B", str(P33A), "--plne",
                               "--vystup", str(ANALYZA / "p34-p33a-plne-vystup.txt")], timeout=7200)
        MERENO["p33-a plný"] = citac(out)
        m.info("p33-a-overeni.py --plne: exit=%d, čítač=%s, %.0f s" % (kod, MERENO["p33-a plný"], sec))
    else:
        m.nezmereno("§64.1 „plný běh P33 (C0–C8): 112/3/2/4“ — p33-a-overeni.py --plne se "
                    "NEPOUŠTĚL: pouští uvnitř `g3`+`validate-all` a jeho C1 pouští "
                    "`p28-b-mutace` (~22 min); spouštěj `P34_P33PLNE=1 … --jen A3`")
    # Levný běh měřidla P33 — měří se VŽDY (je rychlý) a je to základ §64.1.
    kod, out, sec = spust([sys.executable, "-B", str(P33A),
                           "--vystup", str(ANALYZA / "p34-p33a-levny-vystup.txt")], timeout=3600)
    MERENO["p33-a levný"] = citac(out)
    m.info("p33-a-overeni.py (levný režim): exit=%d, čítač=%s, %.0f s"
           % (kod, MERENO["p33-a levný"], sec))

    # ── TVRZENÍ: §64 v HANDOFFu + §0.3 ZADÁNÍ P34 (commitnutá verze = stabilní) ──
    text64, l0, l1 = oddil(r"^##\s+64\.", HANDOFF)
    m.info("tvrzení §64: řádky %d–%d (%d znaků)" % (l0, l1, len(text64)))
    # ⚠ Tvrzení §0.3 se čtou z PRACOVNÍHO STROMU, ne z gitu: `git.cmd` jde přes
    # `cmd.exe` a čeština se v jeho výstupu rozsype (naměřeno P34: blok
    # „OSTATNÍ BRÁNY PŘI ZÁPISU“ se nenašel, ačkoli v souboru JE). Kdo čte
    # dokument s diakritikou, musí ho číst Pythnem, ne trubkou přes cmd.
    zad = NEXT.read_text(encoding="utf-8") if NEXT.is_file() else ""
    if not zad:
        kod, zad, _ = git("show", "HEAD:NEXT-SESSION-INSTRUKCE.md")
        m.nezmereno("zadání se čte z gitu (exit=%d) — pracovní strom ho nemá" % kod)
    # §0.3 zadání = blok „OSTATNÍ BRÁNY PŘI ZÁPISU“
    i03 = zad.find("OSTATNÍ BRÁNY PŘI ZÁPISU")
    blok03 = zad[i03:i03 + 2500] if i03 >= 0 else zad
    m.ok_(i03 >= 0, "v zadání P34 je blok „OSTATNÍ BRÁNY PŘI ZÁPISU“ (§0.3) — odtud se čtou čísla")

    def hledej(text, vzory):
        mm, okno, vzor = najdi_tvrzeni(text, vzory)
        return (mm, okno)

    def tvr(popis, zdroj, vzory, klic, ocekavany):
        mm, okno = hledej(zdroj, vzory)
        if mm is None:
            m.ok_(False, "TVRZENÍ NENALEZENO: %s — nenalezené tvrzení je CHYBA, ne přeskočení "
                         "(vzory: %s)" % (popis, vzory))
            return
        m.info("tvrzení „%s“: …%s…" % (popis, okno))
        nam = MERENO.get(klic)
        if nam is None:
            m.nezmereno("%s: tvrzení %s — měření „%s“ se v tomhle běhu nepouštělo"
                        % (popis, "/".join(mm.groups()) or ocekavany, klic))
            return
        if str(nam) == str(ocekavany):
            m.ok_(True, "%s: tvrzení %s a naměřeno %s" % (popis, ocekavany, nam))
        else:
            m.rozdil("%s: tvrzení %s, naměřeno %s (rozdíl se POJMENOVÁVÁ, neschovává)"
                     % (popis, ocekavany, nam))

    # §64: plný běh P33
    mm, _ = hledej(text64, [r"Plný běh \(C0–C8\):\s*(\d+)/(\d+)/(\d+)/(\d+)"])
    if mm is None:
        m.ok_(False, "TVRZENÍ NENALEZENO: §64.1 „Plný běh (C0–C8): 112/3/2/4“")
    else:
        chce = "/".join(mm.groups())
        nam = MERENO.get("p33-a plný")
        if nam is None:
            m.nezmereno("§64.1 plný běh P33: tvrzení %s — měření se nepouštělo" % chce)
        elif nam == chce:
            m.ok_(True, "§64.1 plný běh P33: tvrzení %s a naměřeno %s" % (chce, nam))
        else:
            m.rozdil("§64.1 plný běh P33: tvrzení %s, naměřeno %s" % (chce, nam))

    # §64.2: příčina se nezměřila (P34 ji měří — sekce B1)
    mm, _ = hledej(text64, [r"Příčinu z tohoto pracoviště určit[\s\n]+nelze"])
    if mm is None:
        m.ok_(False, "TVRZENÍ NENALEZENO: §64.2 „Příčinu z tohoto pracoviště určit nelze“")
    else:
        m.ok_(True, "§64.2 tvrdí „příčinu z tohoto pracoviště určit NELZE“ — P34 ji MĚŘÍ "
                    "(sekce B1) a staví proti tomu nový záznam (H157)")
    mm, _ = hledej(text64, [r"wrangler` v sandboxu padá na"])
    m.ok_(mm is not None, "a §64.2 pojmenovává PŘÍČINU té nemožnosti (`wrangler` padal na `spawn EPERM`)")

    # §64.4 / §0.3: brány
    tvr("§64 g3 = 49 bran", text64, [r"g3\s*→\s*\*{0,2}(\d+)\*{0,2} bran"], "g3 bran", "49")
    tvr("§0.3 g3 = 49 bran", blok03, [r"g3\s*→\s*\*{0,2}(\d+)\*{0,2}\s*bran"], "g3 bran", "49")
    tvr("§0.3 g3 = 0 NEDEKLAROVANÝCH", blok03, [r"(\d+)\s*NEDEKLAROVANÝCH"], "g3 nedeklarovaných", "0")
    tvr("§0.3 g3 = 1 bez čítače", blok03, [r"/\s*(\d+)\s*bez čítače"], "g3 bez čítače", "1")
    tvr("§0.3 validate-all = 0 problémů", blok03,
        [r"validate-all\s*→\s*\*{0,2}(\d+)\*{0,2}\s*problémů"], "validate-all problémů", "0")
    tvr("§0.3 ag-over-cisla = 49 bran", blok03,
        [r"ag-over-cisla\*{0,2}\s*\*{0,2}exit 0\*{0,2}\s*\((\d+) bran\)"], "registr bran", "49")
    tvr("§0.3 kronika = 48 řádků", blok03,
        [r"kronika\s*SEDÍ\s*\(?\*{0,2}(\d+)\*{0,2}\s*řádků"], "kronika řádků", "48")
    tvr("§0.3 ov-g = 0 NEOVĚŘENO", blok03, [r"ov-g\*{0,2}\s*\*{0,2}(\d+)\*{0,2}\s*NEOVĚŘENO"],
        "ov-g neověřeno", "0")
    tvr("§0.3 ov-g rozsah = 99 řádků Hxx", blok03, [r"rozsah\s*\*{0,2}(\d+)\*{0,2}\s*řádků Hxx"],
        "ov-g řádků Hxx", "99")
    tvr("§0.3 handoff = 0 chybějících", blok03, [r"handoff\*{0,2}\s*\*{0,2}(\d+)\*{0,2}\s*chybějících"],
        "handoff chybějících", "0")
    tvr("§0.3 over-skilly = 92/0", blok03, [r"over-skilly\*{0,2}\s*\*{0,2}(\d+)/(\d+)"],
        "over-skilly", "92/0")
    tvr("§0.3 over-dokumentaci = 64/0", blok03, [r"over-dokumentaci\*{0,2}\s*\*{0,2}(\d+)/(\d+)"],
        "over-dokumentaci", "64/0")
    tvr("§0.3 p22-test-mutace = 20/0", blok03, [r"p22-test-mutace\*{0,2}\s*\*{0,2}(\d+)/(\d+)"],
        "p22-test-mutace", "20/0")
    tvr("§0.3 p32-test-zapis-kotvy = 16/0", blok03, [r"p32-test-zapis-kotvy\*{0,2}\s*\*{0,2}(\d+)/(\d+)"],
        "p32-test-zapis-kotvy", "16/0")
    tvr("§0.3 p33-mutace = 19/0", blok03, [r"p33-mutace\*{0,2}\s*\*{0,2}(\d+)/(\d+)"], "p33-mutace", "19/0")
    tvr("§0.3 p29-a --jen A1M13 = 8/0", blok03,
        [r"p29-a --jen A1M13\*{0,2}\s*\*{0,2}(\d+)/(\d+)"], "p29-a A1M13", "8/0")
    tvr("§0.3 p29-a --jen A3 = 17/0", blok03, [r"--jen A3\*{0,2}\s*\*{0,2}(\d+)/(\d+)"], "p29-a A3", "17/0")
    tvr("§0.3 p30-mutace = 16/0", blok03, [r"p30-mutace\*{0,2}\s*\*{0,2}(\d+)/(\d+)"], "p30-mutace", "16/0")
    tvr("§0.3 p32-mutace = 18/0", blok03, [r"p32-mutace\*{0,2}\s*\*{0,2}(\d+)/(\d+)"], "p32-mutace", "18/0")
    tvr("§0.3 p28-b-mutace = 30/0", blok03, [r"p28-b-mutace\*{0,2}\s*\*{0,2}(\d+)/(\d+)"], "p28-b-mutace", "30/0")

    # Co se v P34 NEMĚŘILO — musí to být VIDĚT, ne ticho (a proč)
    m.nezmereno("§0.3 C9 (p31-a --plne 51/4/2/0 · p32-a --plne 51/0/2/0 · p31-mutace 24/0 · A1 11/0) "
                "— dlouhé nohy (~60–80 min), pouští se `python _analyza\\p33-a-overeni.py --jen C9`")
    m.nezmereno("§0.3 A4 (dávka dokladů) — pouští se `python _analyza\\p34-a-overeni.py --jen A4`")


# ── A4: dávka dokladů (jen na vyžádání) ─────────────────────────────────────
def sekce_A4(m):
    p("")
    p("A4) DÁVKA DOKLADŮ NIC NEZAPISUJE? (`p20-d-doklady.py`; v P33 NEDOBĚHLA)")
    pred = {c.name: sha(c) for c in [KRONIKA, HANDOFF, NEXT, REGISTR] if c.is_file()}
    m.ok_(P20D.is_file(), "dávka `_analyza/p20-d-doklady.py` existuje")
    kod, out, sec = spust([sys.executable, "-B", str(P20D)], timeout=21600)
    (ANALYZA / "p34-c4-davka-vystup.txt").write_bytes(out.encode("utf-8"))
    m.info("dávka: exit=%s, %.0f s, doklad _analyza/p34-c4-davka-vystup.txt" % (kod, sec))
    if kod == -9:
        m.nezmereno("dávka NEDOBĚHLA (TIMEOUT) — naměřený čas není odpracovaný čas (P33)")
    else:
        m.ok_(kod == 0, "dávka dokladů → exit 0 (naměřeno %s)" % kod)
    po = {c.name: sha(c) for c in [KRONIKA, HANDOFF, NEXT, REGISTR] if c.is_file()}
    zmenene = [n for n in pred if pred[n] != po[n]]
    m.ok_(not zmenene, "ani JEDEN ze 4 sledovaných dokumentů se nezměnil (hash před/po): %s"
          % (zmenene or "žádný"))
    m.ok_(kod == -9 or "ZMĚNĚN:" not in out, "dávka neohlásila ŽÁDNÝ „ZMĚNĚN“ dokument")
    if "KDO ZAPSAL" in out:
        blok = out.split("KDO ZAPSAL", 1)[1][:600]
        m.ok_("→" not in blok, "sekce „KDO ZAPSAL“ je PRÁZDNÁ (H138)")


# ── A5: registr bran ─────────────────────────────────────────────────────────
def sekce_A5(m):
    p("")
    p("A5) JE REGISTR BRAN V POŘÁDKU? (`ag-over-cisla.py` proti číslům v AGENTS.md)")
    kod, out, sec = spust([sys.executable, "-B", str(AG_OVER)], timeout=900)
    m.ok_(kod == 0, "`ag-over-cisla.py` → exit 0 (naměřeno %d, %.0f s)" % (kod, sec))
    MERENO["ag-over-cisla exit"] = kod
    if kod != 0:
        m.info("       %s" % " | ".join(x.strip() for x in out.splitlines()[-6:])[:300])
    try:
        reg = json.loads(REGISTR.read_text(encoding="utf-8"))
        n = reg.get("bran_celkem")
        MERENO["registr bran"] = n
        m.ok_(n == 49, "`_registr-bran.json` → bran_celkem = 49 (naměřeno %s)" % n)
    except Exception as e:  # noqa: BLE001
        m.ok_(False, "registr bran se nedá přečíst: %s" % e)


# ── A6: uklízí se měřidla po sobě? ───────────────────────────────────────────
def sekce_A6(m, drahe):
    p("")
    p("A6) UKLÍZÍ SE MĚŘIDLA PO SOBĚ? (a běží cizí měřidla dál?)")
    if not drahe:
        m.nezmereno("A6 běhy cizích měřidel (p29-a, p22-test-mutace, p32-test-zapis-kotvy, p33-mutace) "
                    "— pouští se s --plne/--jen A6")
    else:
        kod, out, sec = spust([sys.executable, "-B", str(P29A), "--jen", "A1M13"], timeout=1800)
        c = citac(out)
        MERENO["p29-a A1M13"] = "/".join(c) if c else None
        m.ok_(kod == 0 and c == ("8", "0"),
              "p29-a --jen A1M13 → exit=%d a 8/0 (naměřeno %s, %.0f s)" % (kod, c, sec))
        kod, out, sec = spust([sys.executable, "-B", str(P29A), "--jen", "A3"], timeout=1800)
        c = citac(out)
        MERENO["p29-a A3"] = "/".join(c) if c else None
        m.ok_(kod == 0 and c == ("17", "0"),
              "p29-a --jen A3 → exit=%d a 17/0 (naměřeno %s, %.0f s)" % (kod, c, sec))
        for skript, chce, klic in [(P22T, ("20", "0"), "p22-test-mutace"),
                                   (P32T, ("16", "0"), "p32-test-zapis-kotvy"),
                                   (P33M, ("19", "0"), "p33-mutace"),
                                   (ANALYZA / "p30-mutace.py", ("16", "0"), "p30-mutace"),
                                   (ANALYZA / "p32-mutace.py", ("18", "0"), "p32-mutace"),
                                   (ANALYZA / "p28-b-mutace.py", ("30", "0"), "p28-b-mutace")]:
            # ⚠ `p28-b-mutace.py` je NEJDELŠÍ z nich (~22 min) a pouští se proto
            # jen na výslovné přání: `P34_P28B=1`.
            if skript.name == "p28-b-mutace.py" and os.environ.get("P34_P28B") != "1":
                m.nezmereno("p28-b-mutace — NEpouštělo se (trvá ~22 min); spouštěj `P34_P28B=1 …`")
                continue
            kod, out, sec = spust([sys.executable, "-B", str(skript)], timeout=3600)
            c = citac(out)
            MERENO[klic] = "/".join(c) if c else None
            if c == chce:
                m.ok_(True, "%s → %s (exit=%d, %.0f s)" % (skript.name, "/".join(c), kod, sec))
            else:
                m.rozdil("%s: očekáváno %s, naměřeno %s (exit=%d, %.0f s)"
                         % (skript.name, "/".join(chce), "/".join(c) if c else "—", kod, sec))

    for vzor in ("p29-mut-*", "p22-mutace-*", "p32-mutace-scratch", "p29-kopie-tick.mjs",
                 "_p33-mut-*", "p33-mutace-scratch", "_p34-mut-*", "p34-mutace-scratch"):
        zbyle = sorted(x.name for x in ANALYZA.glob(vzor))
        m.ok_(not zbyle, "po měřidlech nezůstalo `%s` (%s)" % (vzor, zbyle or "nic"))


# ── A7: nic se nerozbilo ─────────────────────────────────────────────────────
def sekce_A7(m, drahe):
    p("")
    p("A7) NIC SE NEROZBILO? (inventář → g3 → validate-all; NE současně)")
    if not drahe:
        m.nezmereno("A7 g3 + validate-all + kronika/handoff/ov-g — pouští se s --plne/--jen A7")
        return

    kod, out, sec = spust([sys.executable, str(INVENTAR), "--json", str(ANALYZA / "_inventar.json")],
                          timeout=1800)
    m.ok_(kod == 0, "inventář přegenerován (exit=%d, %.0f s)" % (kod, sec))

    kod, out, sec = spust([sys.executable, "-B", str(G3)], timeout=7200)
    (ANALYZA / "p34-g3-vystup.txt").write_bytes(out.encode("utf-8"))
    p("  INFO       g3: exit=%d, %.0f s (doklad _analyza/p34-g3-vystup.txt)" % (kod, sec))
    br = re.search(r"brán celkem:\s*(\d+),\s*s nenulovým exit:\s*(\d+)", out)
    MERENO["g3 bran"] = br.group(1) if br else None
    m.ok_(br is not None and br.group(1) == "49",
          "g3 měří 49 bran (naměřeno %s)" % (br.group(1) if br else "?"))
    bez_cit = re.search(r"NEVYKÁZALY ČÍTAČ \((\d+)\)", out)
    MERENO["g3 bez čítače"] = bez_cit.group(1) if bez_cit else None
    m.ok_(bez_cit is not None and bez_cit.group(1) == "1",
          "g3 hlásí POJMENOVANĚ 1 bránu bez čítače (naměřeno %s) — H133"
          % (bez_cit.group(1) if bez_cit else "?"))
    # ⚠ NAMĚŘENO PŘED OPRAVOU (P34, vlastní past): první verze čtla počet
    # NEDEKLAROVANÝCH vzorem `NEDEKLAROVAN[^\(]*\((\d+)\)` — ten v g3 výstupu
    # NENÍ (text je „…a NEDEKLAROVANÝCH 1:“), takže návratová hodnota byla
    # `None` a kód si z ní udělal **0** → kontrola „0 NEDEKLAROVANÝCH“ byla
    # ZELENÁ nad stavem, kdy g3 hlásí **1**. Přesně past H155 („vzor, který
    # nezabere, přeskočí měření“) — a tady navíc tvrdila nulu.
    nedekl = re.search(r"NEDEKLAROVAN[ÝY]CH\s+(\d+)\s*:", out) or \
        re.search(r"a\s+NEDEKLAROVAN[ÝY]CH\s+(\d+)", out)
    if nedekl is None:
        MERENO["g3 nedeklarovaných"] = None
        m.ok_(False, "g3 NEVYKÁZAL počet NEDEKLAROVANÝCH exitů — vzor nezabral a „nula“ "
                     "by tu byla SLEPÁ (kontrola musí umět selhat, ne mlčet)")
    else:
        n_nedekl = int(nedekl.group(1))
        MERENO["g3 nedeklarovaných"] = n_nedekl
        if n_nedekl == 0:
            m.ok_(True, "g3: 0 NEDEKLAROVANÝCH nenulových exitů")
        else:
            neocek = [x.strip() for x in re.findall(r"NEOČEKÁVAN[ÝY]:\s*([^\n]+)", out)]
            # ⚠ H160: živý výpadek cronu se PROPÍŠE do čítačů bran — je to NÁLEZ
            # O SLUŽBĚ, ale musí se DOKÁZAT jménem, ne předpokládat.
            m.nalezeno("g3 hlásí %d NEDEKLAROVANÝCH exitů (%s) — H160: živý výpadEk cronu se "
                       "propisuje do čítačů bran" % (n_nedekl, "; ".join(neocek)[:120] or "?"))
            m.ok_("validate-all" in out,
                  "a je to POJMENOVANĚ `validate-all (CELEK)` (ne jiná brána)")

    kod, out, sec = spust(["node", str(VALIDATE)], timeout=1800)
    (ANALYZA / "p34-validate-all-vystup.txt").write_bytes(out.encode("utf-8"))
    p("  INFO       validate-all: exit=%d, %.0f s" % (kod, sec))
    problemy = [x.strip() for x in out.splitlines() if x.strip().startswith("CHYBA")]
    MERENO["validate-all problémů"] = 0 if kod == 0 else len(problemy)
    if kod == 0:
        m.ok_(True, "`validate-all` → 0 problémů")
    else:
        # ⚠ Fixtury vypisují řádky `OK  3 tep 30 min starý → CHYBA …` — ty NEJSOU
        # problémy brány. Počítají se proto JEN řádky ZAČÍNAJÍCÍ „CHYBA“.
        cron_red = [x for x in problemy if "cron běží" in x]
        kod_red = [x for x in problemy if "lokální kód = repo" in x]
        ostatni = [x for x in problemy if x not in cron_red and x not in kod_red]
        if cron_red:
            m.nalezeno("validate-all je červený na bráně `cron běží (čas)` (%s) — ŽIVÝ VÝPADEK "
                       "(H156/H160), ne vada měřidla" % cron_red[0][:110])
        if kod_red:
            m.rozdil("validate-all: „lokální kód = repo“ je červené (%s) — změna P34 ještě NENÍ "
                     "PUSHNUTÁ; push je poslední krok P34, pak se to srovná" % kod_red[0][:110])
        m.ok_(not ostatni, "a ŽÁDNÝ jiný problém v `validate-all` není (problémů %d: %s)"
              % (len(problemy), " | ".join(x[:70] for x in problemy)))

    kod, out, sec = spust([sys.executable, "-B", str(KRONIKA_K)], timeout=1800)
    m.ok_(kod == 0 and "SEDÍ" in out, "`kronika-kontrola.py` → SEDÍ (exit=%d)" % kod)
    r = re.search(r"řádků sessions:\s*(\d+)", out)
    MERENO["kronika řádků"] = r.group(1) if r else None
    m.info("       řádků sessions: %s" % (r.group(1) if r else "?"))
    kod, out, sec = spust([sys.executable, "-B", str(HANDOFF_K)], timeout=1800)
    m.ok_(kod == 0, "`handoff-kontrola-uplnost.py` → 0 chybějících (exit=%d)" % kod)
    ch = re.search(r"chybějících[^\d]{0,20}(\d+)", out)
    MERENO["handoff chybějících"] = ch.group(1) if ch else ("0" if kod == 0 else None)
    kod, out, sec = spust([sys.executable, "-B", str(OVG)], timeout=1800)
    m.ok_(kod == 0, "`ov-g-neovereno.py` → 0 NEOVĚŘENO (exit=%d)" % kod)
    rr = re.search(r"nálezů \(řádků tabulek Hxx\) CELKEM:\s*(\d+)", out)
    if rr:
        MERENO["ov-g řádků Hxx"] = rr.group(1)
        m.ok_(rr.group(1) == "99", "a měří rozsah 99 řádků Hxx (naměřeno %s)" % rr.group(1))
    else:
        m.nezmereno("ov-g nevykázal počet řádků Hxx — rozsah se nedá ověřit")
    nn = re.search(r"s textem NEOVĚŘENO na tom řádku:\s*(\d+)", out)
    MERENO["ov-g neověřeno"] = nn.group(1) if nn else None

    # Dvě dokumentové brány, na jejichž číslech stojí §0.3
    for skript, klic in [(TOOLS / "over-skilly.py", "over-skilly"),
                         (TOOLS / "over-dokumentaci.py", "over-dokumentaci")]:
        kod, out, sec = spust([sys.executable, str(skript)], timeout=1800)
        c = citac(out)
        if c is None:
            c = re.search(r"Kontrol:\s*(\d+),\s*chyb:\s*(\d+)", out)
            c = (c.group(1), c.group(2)) if c else None
        if c is None:
            # `over-skilly.py` nemá tvar „VÝSLEDEK: N kontrol“ — jeho čítač je
            # „Cesty k nástrojům: 92 zmínek, 0 mrtvých“ (§0.3 mu říká „92/0“).
            c = re.search(r"Cesty k nástrojům:\s*(\d+)\s*zmínek,\s*(\d+)\s*mrtvých", out)
            c = (c.group(1), c.group(2)) if c else None
        MERENO[klic] = "/".join(c) if c else None
        m.ok_(kod == 0, "%s → exit 0 (naměřeno %s, %.0f s)" % (skript.name, MERENO[klic], sec))


# ── A8: žije cron? ───────────────────────────────────────────────────────────
def sekce_A8(m):
    p("")
    p("A8) ŽIJE CRON? — ŽIVÝ tep z `/health` (a když ne, je to stav SLUŽBY)")
    if os.environ.get("P34_HEALTH"):
        m.info("⚠ seam P34_HEALTH: hodnotí se PODSTRČENÝ stav (%s), ne živá služba" % HEALTH_LIVE.name)
    else:
        # ⚠ Sonda si cestu skládá přes `join(WS, argument)` — ABSOLUTNÍ cesta by
        # se slepila do nesmyslu (a doklad by nevznikl). Předává se RELATIVNÍ.
        kod, out, sec = spust(["node", str(SONDA_HEALTH), os.path.relpath(HEALTH_LIVE, WS)],
                              timeout=180)
        m.ok_(HEALTH_LIVE.is_file(), "živá sonda `/health` uložila doklad (%s)" % HEALTH_LIVE.name)
        if kod != 0:
            m.info("       sonda exit=%d: %s" % (kod, out.strip()[:200]))
    try:
        h = json.loads(HEALTH_LIVE.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        m.ok_(False, "doklad `/health` se nedá přečíst (%s): %s" % (HEALTH_LIVE.name, e))
        return

    p("  INFO       /health HTTP %s · ready=%s running=%s · last_cron=%s · last_tick_zdroj=%s"
      % (h.get("http_status", "?"), h.get("ready"), h.get("running"),
         h.get("last_cron"), h.get("last_tick_zdroj")))
    m.ok_(h.get("http_status") == 200, "služba odpovídá (HTTP %s)" % h.get("http_status"))

    # Rozhoduje PREDIKÁT BRÁNY, ne jeho opis (dvě implementace téhož = druhá pravda).
    kod, out, _ = spust(["node", str(CRON_PRED), str(HEALTH_LIVE)], timeout=60)
    if kod == 0:
        m.ok_(True, "predikát brány nad tím tepem: OK (exit=0)")
    else:
        posledni = out.strip().splitlines()[-1] if out.strip() else "?"
        m.nalezeno("predikát brány nad ŽIVÝM tepem: CHYBA (exit=%d) — %s" % (kod, posledni[:170]))
        m.nalezeno("a JE TO NÁLEZ O SLUŽBĚ (H156), ne vada měřidla: služba odpovídá (HTTP 200), "
                   "ale `last_cron_min` = %s (limit 10)" % h.get("last_cron_min"))

    # KONTROLA, KTERÁ UMÍ PROJÍT I SPADNOUT: predikát a ULOŽENÝ stav si nesmí
    # odporovat. `last_cron_min` počítá SLUŽBA (jiná cesta než predikát), limit
    # 10 min je smlouva brány — kdyby predikát přestal měřit, ROZEJDE SE to.
    cmin = h.get("last_cron_min")
    if isinstance(cmin, int):
        ocekavano_ok = cmin <= 10
        m.ok_(ocekavano_ok == (kod == 0),
              "predikát a ULOŽENÝ stav si neodporují (služba: %s min → očekáváno %s, predikát exit=%d)"
              % (cmin, "OK" if ocekavano_ok else "CHYBA", kod))
    else:
        m.nezmereno("`last_cron_min` v `/health` chybí (%r) — konzistenci predikátu se stavem nelze ověřit" % cmin)


# ── B1: Úkol B — PŘÍČINA výpadku (H156) ─────────────────────────────────────
def sekce_B1(m):
    p("")
    p("B1) ÚKOL B / H156 — PŘÍČINA VÝPADKU CRONU (tři nezávislé doklady)")

    if D1_DOKLAD.is_file():
        try:
            d1 = json.loads(D1_DOKLAD.read_text(encoding="utf-8"))
            m.ok_(True, "D1 doklad `state` existuje (%s)" % D1_DOKLAD.name)
            p("  INFO       D1 state: %s" % json.dumps(d1, ensure_ascii=False)[:220])
        except Exception as e:  # noqa: BLE001
            m.ok_(False, "D1 doklad se nedá přečíst: %s" % e)
    else:
        m.nezmereno("D1 doklad `state` chybí (%s) — řetěz příčiny by nebyl doložený" % D1_DOKLAD.name)

    if CF_DOKLAD.is_file():
        try:
            cf = json.loads(CF_DOKLAD.read_text(encoding="utf-8"))
            radky = cf.get("radky") or []
            m.ok_(bool(radky), "Cloudflare Analytics: doklad má %d řádků (historie invokací)" % len(radky))
            podle = {}
            for x in radky:
                k = x["dimensions"]["status"]
                podle[k] = podle.get(k, 0) + x["sum"]["requests"]
            p("  INFO       historie: %s" % ", ".join("%s=%d" % kv for kv in sorted(podle.items())))
            m.ok_(podle.get("exceededResources", 0) > 0,
                  "a je v ní `exceededResources` (%d invokací) — invokace umírají na LIMIT, ne na logiku"
                  % podle.get("exceededResources", 0))
        except Exception as e:  # noqa: BLE001
            m.ok_(False, "doklad analytiky se nedá přečíst: %s" % e)
    else:
        m.nezmereno("doklad Cloudflare Analytics chybí (%s)" % CF_DOKLAD.name)

    if TAIL_DOKLAD.is_file() and TAIL_DOKLAD.stat().st_size > 0:
        eventy = []
        for radek in TAIL_DOKLAD.read_text(encoding="utf-8", errors="replace").splitlines():
            radek = radek.strip()
            if not radek.startswith("{"):
                continue
            try:
                eventy.append(json.loads(radek))
            except Exception:  # noqa: BLE001
                continue
        cron = [e for e in eventy if (e.get("event") or {}).get("cron") is not None]
        m.ok_(bool(cron), "živý tail: doklad má %d CRON eventů (z %d eventů)" % (len(cron), len(eventy)))
        if cron:
            e = cron[-1]
            p("  INFO       cron event: outcome=%s cpu=%sms wall=%sms verze=%s"
              % (e.get("outcome"), e.get("cpuTime"), e.get("wallTime"),
                 (e.get("scriptVersion") or {}).get("id")))
            ex = [x for x in cron if x.get("outcome") == "exceededCpu"]
            m.ok_(bool(ex), "a mezi cron eventy je `exceededCpu` (%d z %d) — trigger DORAZÍ, invocation umírá"
                  % (len(ex), len(cron)))
    else:
        m.nezmereno("doklad živého `wrangler tail` chybí nebo je prázdný (%s)" % TAIL_DOKLAD.name)

    p("  INFO       ŘETĚZ (každý článek má doklad):")
    p("  INFO         1. cron trigger DORAZÍ (tail: `event.cron = '* * * * *'`)")
    p("  INFO         2. invocation skončí `exceededCpu` (CPU limit free plánu = 10 ms)")
    p("  INFO         3. `tick()` se nedokončí → `zapisTep()` se nezavolá → `last_cron` zestárne")
    p("  INFO         4. brána to hlásí jako „cron NETIKÁ“ — ČERVENÁ je správně,")
    p("  INFO            ale pojmenovává to ŠPATNĚ (nechybí trigger, umírá tik)")


def main():
    global _doklad_handle
    ap = argparse.ArgumentParser()
    ap.add_argument("--jen", default=None, help="seznam sekcí, např. A1 nebo A1,A8")
    ap.add_argument("--plne", action="store_true", help="i A3/A6/A7 (mutace, g3, validate-all)")
    ap.add_argument("--levne", action="store_true",
                    help="i u `--jen X` přeskoč drahé nohy (pro mutační test měřidla)")
    ap.add_argument("--vystup", default=None)
    args = ap.parse_args()

    if args.vystup:
        vystup = pathlib.Path(args.vystup)
        if not vystup.is_absolute():
            vystup = WS / vystup
    else:
        vystup = DOKLAD_PLNY if (args.plne or args.jen) else DOKLAD_LEVNY

    m = Meridlo()
    vystup.parent.mkdir(parents=True, exist_ok=True)
    _doklad_handle = vystup.open("w", encoding="utf-8")

    # ⚠ NAMĚŘENÁ ČÍSLA SE PRENÁŠEJÍ MEZI BĚHY (`MERENO`), aby se sekce A3
    # (tvrzení) dala pustit SAMOSTATNĚ (`--jen A3`) a přitom nesrovnávala
    # s prázdnem. Zdroj a STÁŘÍ se vypisují — „měření z dokladu“ musí být vidět.
    mereno_doklad = ANALYZA / "p34-mereno-vystup.txt"
    if mereno_doklad.is_file():
        try:
            ulozene = json.loads(mereno_doklad.read_text(encoding="utf-8"))
            stari_min = (time.time() - ulozene.get("cas", 0)) / 60
            MERENO.update({k: v for k, v in (ulozene.get("mereno") or {}).items() if v is not None})
            p("  INFO       MERENO: načteno z %s (stáří %.0f min, sekce %s)"
              % (mereno_doklad.name, stari_min, ",".join(ulozene.get("sekce") or [])))
        except Exception as e:  # noqa: BLE001
            p("  INFO       MERENO: doklad %s se nedá přečíst (%s)" % (mereno_doklad.name, e))
    vychozi = "A0,A1,A2,A5,A8,B1" if not args.plne else "A0,A1,A2,A5,A6,A7,A8,B1,A3"
    etapy = [x.strip().upper() for x in (args.jen if args.jen else vychozi).split(",")]
    drahe = (args.plne or bool(args.jen)) and not args.levne  # `--jen X` = chci i drahou nohu

    fns = {
        "A0": lambda: sekce_A0(m),
        "A1": lambda: sekce_A1(m),
        "A2": lambda: sekce_A2(m, drahe),
        "A3": lambda: sekce_A3(m, drahe),
        "A4": lambda: sekce_A4(m),
        "A5": lambda: sekce_A5(m),
        "A6": lambda: sekce_A6(m, drahe),
        "A7": lambda: sekce_A7(m, drahe),
        "A8": lambda: sekce_A8(m),
        "B1": lambda: sekce_B1(m),
    }

    p("=" * 92)
    p("P34/A — VLASTNÍ PŘEMĚŘENÍ PRÁCE P33 (A1–A8) + PŘÍČINA VÝPADKU CRONU (H156)")
    p("=" * 92)
    p("  datum (z hodin): %s" % time.strftime("%Y-%m-%d %H:%M:%S %z"))
    p("  dokument, ze kterého se ČTOU TVRZENÍ: %s" % HANDOFF.name)
    p("  pořadí běhu: %s%s" % (", ".join(etapy), "  (--plne)" if args.plne else "  (levný režim)"))
    p("  ⚠ A4 (dávka dokladů) se pouští JEN `--jen A4`; A3/A6/A7 mají drahé nohy")
    for e in etapy:
        f = fns.get(e)
        if f is None:
            p("  ??    etapa %s neexistuje" % e)
            continue
        p("\n" + "─" * 92)
        t0 = time.time()
        try:
            f()
        except Exception as ex:  # noqa: BLE001
            import traceback  # noqa: PLC0415
            tb = traceback.format_exc().strip().splitlines()
            p("      TRACEBACK: %s" % " | ".join(x.strip() for x in tb[-3:]))
            m.nezmereno("etapa %s: výjimka %s: %s" % (e, type(ex).__name__, str(ex)[:200]))
        p("      (etapa %s: %.0f s)" % (e, time.time() - t0))

    p("\n" + "=" * 92)
    p("POJMENOVANÉ ROZDÍLY (stav se posunul, nebo je změna ZÁMĚRNÁ): %d" % len(m.rozdily))
    for x in m.rozdily:
        p("  · %s" % x[:220])
    p("\nNÁLEZY O SLUŽBĚ (stav měřeného objektu — NENÍ to chyba měřidla): %d" % len(m.sluzba))
    for x in m.sluzba:
        p("  · %s" % x[:220])
    p("\nNEZMĚŘENO (není nula a není zelená): %d" % len(m.nezmerene))
    for x in m.nezmerene:
        p("  · %s" % x[:220])
    p("=" * 92)
    p("VÝSLEDEK: %d kontrol, %d chyb (z toho %d ROZDÍLŮ, %d NEZMĚŘENO, %d NÁLEZŮ O SLUŽBĚ)"
      % (m.ok, len(m.chyby), len(m.rozdily), len(m.nezmerene), len(m.sluzba)))
    p("=" * 92)
    if SCRATCH.exists() and not any(SCRATCH.iterdir()):
        SCRATCH.rmdir()
    # Úklid dokladu o naměřených číslech: co sekce ZMĚŘILY, se předá A3 i příště.
    try:
        mereno_doklad.write_bytes((json.dumps(
            {"cas": time.time(), "sekce": [e for e in etapy if e != "A3"],
             "mereno": {k: v for k, v in MERENO.items()}}, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    except Exception as e:  # noqa: BLE001
        print("  ⚠ doklad MERENO se nepodařilo zapsat: %s" % e)
    _doklad_handle.close()
    _doklad_handle = None
    print("\n[doklad] %s (%d B, UTF-8)" % (vystup.relative_to(WS), vystup.stat().st_size))
    return 1 if m.chyby else 0


if __name__ == "__main__":
    sys.exit(main())
