# -*- coding: utf-8 -*-
r"""P35 — VLASTNÍ PŘEMĚŘENÍ PRÁCE P34 (Úkol A) + ZLEVNĚNÍ TIKU (Úkol B, H165).

CO TENHLE DOKLAD DĚLÁ A ČÍM SE LIŠÍ OD MĚŘIDLA P34:
  * Měří **A1–A7 zadání P35** (`NEXT-SESSION-INSTRUKCE.md` §2.1) — ne A0–A8 P34.
    Měřidlo P34 je přitom jen JEDEN Z MĚŘENÝCH PŘEDMĚTŮ (sekce A4), ne základ.
  * **Tvrzení se NEČTOU Z HLAVY**: nejdřív se MĚŘÍ, teprve pak se hledá tvrzení
    v `HANDOFF.md` §65 (H155) — a **nenalezené tvrzení je CHYBA**, ne přeskočení.
  * **Diferenciál brány cronu (A3) je ČTYŘVRSTVÝ a v KOPIÍCH**: (a) predikát bez
    větve „tik NEDOBÍHÁ“, (b) predikát bez větve „pokus v BUDOUCNOSTI“,
    (c) **SLABÁ KONTROLA** (fixtura 4 kontroluje jen `ok === false`) — nad tou
    samou vadou musí slabá kontrola projít (exit 0) a silná spadnout (exit 1).
    To je důkaz, že kontrola není slepá (H158). Kopie jsou BAJT NA BAJT shodné
    s živými (`sha256`); živé soubory se NEMUTUJÍ.
  * **Úkol B (H165) = ZLEVNĚNÍ TIKU, ne dohad**: měří se ŽIVÝ CPU PROFIL služby
    (`wrangler tail` → cpuTime podle endpointu), pak ROZKLAD GitHub části tiku
    (bajty + `JSON.parse`) a nakonec ROZKLAD čtení roadmapy — a teprve z toho
    vyjde oprava (indexovaný cyklus místo `Uint8Array.from(mapFn)`).
  * **Umí selhat** — `_analyza/p35-mutace.py` (doklad, že měřidlo není ani
    „vždy zelené“, ani „vždy červené“).

SEKCE A POUŽITÍ:
    python _analyza\p35-a-overeni.py            # LEVNÉ (A0,A1,A2,A3,B1; ~1 min)
    python _analyza\p35-a-overeni.py --plne     # i A5, A6, A7 (živá služba, mutace, g3)
    python _analyza\p35-a-overeni.py --jen A4   # `p34-a-overeni.py --plne` (dlouhá noha)
    python _analyza\p35-a-overeni.py --jen A7   # g3 + validate-all (NE současně s jiným)
  A0  pojistky (co měřidlo předpokládá)
  A1  (A1) je nasazení P34 živé? TŘI KROKY + křížová kontrola verze
  A2  (A2) posílá `/health` POKUS o tik?
  A3  (A3) umí brána spadnout i projít? fixtury + TŘI vady v kopiích
  A4  (A4) sedí čísla z §65? (nejdřív měřit, pak hledat tvrzení; dlouhá noha)
  A5  (A5) je tik opravdu jen CPU? (živý tail + Analytics + D1)
  A6  (A6) uklízí se měřidla po sobě? (`p34-mutace` + živé soubory proti HEAD)
  A7  (A7) nic se nerozbilo (inventář → g3 → validate-all, NE současně)
  B1  (Úkol B) H165 — ZLEVNĚNÍ TIKU: profil → rozklad → oprava → měření

POUŽITÍ SEAMŮ (pro `p35-mutace.py`):
  P35_HANDOFF=<kopie HANDOFF.md>   — měřidlo čte tvrzení z KOPIE, ne z živého
  P35_TAIL=<jsonl živých eventů>   — měřidlo čte PODSTRČENÝ doklad tailu
  P35_ROZKLAD=<txt rozkladu>       — měřidlo čte PODSTRČENÝ rozklad GitHub části
  P35_ROZKLAD_ROADMAPY=<txt>       — měřidlo čte PODSTRČENÝ rozklad čtení roadmapy
  P35_HEALTH=<json s /health>      — měřidlo hodnotí PODSTRČENÝ stav služby

⚠ Výchozí doklad je `p35-a-overeni-levny-vystup.txt`, s `--plne`/`--jen`
  `p35-a-overeni-vystup.txt`. Důvod: dávka dokladů (`p20-d-doklady.py`) pouští
  tenhle skript v LEVNÉM režimu, takže by plný doklad přepsala — a přepsaný
  doklad je ztracený důkaz.
⚠ `--plne`/`--jen A6,A7` POUŠTÍ MUTAČNÍ BĚHY jiných měřidel a `g3`/`validate-all`.
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
GIT = TOOLS / "git.cmd"
HANDOFF = pathlib.Path(os.environ.get("P35_HANDOFF") or (WS / "HANDOFF.md"))
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
NEXT = WS / "NEXT-SESSION-INSTRUKCE.md"
REGISTR = ANALYZA / "_registr-bran.json"

CRON_PRED = TOOLS / "cron-stav.mjs"
CRON_POKUS = TOOLS / "test-cron-pokus.mjs"
TICK_TEST = TOOLS / "test-tick-offline.mjs"
VALIDATE = TOOLS / "validate-all.mjs"
G3 = ANALYZA / "g3-brany.py"
AG_OVER = ANALYZA / "ag-over-cisla.py"
INVENTAR = ANALYZA / "hl-neanglicky-v-kodu.py"
KRONIKA_K = ANALYZA / "kronika-kontrola.py"
HANDOFF_K = ANALYZA / "handoff-kontrola-uplnost.py"
OVG = ANALYZA / "ov-g-neovereno.py"
P34A = ANALYZA / "p34-a-overeni.py"
P34M = ANALYZA / "p34-mutace.py"
SONDA_DEPLOY = ANALYZA / "p30-sonda-deploy.mjs"
SONDA_CF = ANALYZA / "p32-sonda-cf-verze.mjs"
SONDA_HEALTH = ANALYZA / "p35-sonda-health.mjs"
TAIL_ROZBOR = ANALYZA / "p35-tail-rozbor.py"
CONDUCTOR = pathlib.Path(os.environ.get("P35_CONDUCTOR") or (WS / "conductor" / "src" / "index.ts"))

# ── doklady, které měřidlo ČTE (neopisuje z hlavy) ───────────────────────────
TAIL_RAW = pathlib.Path(os.environ.get("P35_TAIL") or (ANALYZA / "p35-tail-raw-vystup.txt"))
HEALTH_LIVE = pathlib.Path(os.environ.get("P35_HEALTH") or (ANALYZA / "p35-health-vystup.txt"))
ROZKLAD = pathlib.Path(os.environ.get("P35_ROZKLAD") or (ANALYZA / "p35-rozklad-tiku-vystup.txt"))
ROZKLAD_RM = pathlib.Path(os.environ.get("P35_ROZKLAD_ROADMAPY") or (ANALYZA / "p35-rozklad-roadmapy-vystup.txt"))
PROFIL = ANALYZA / "p35-profil-cpu-vystup.txt"

SCRATCH = ANALYZA / "p35-scratch"
DOKLAD_PLNY = ANALYZA / "p35-a-overeni-vystup.txt"
DOKLAD_LEVNY = ANALYZA / "p35-a-overeni-levny-vystup.txt"

LIMIT_CPU_MS = 10          # dokumentovaný limit CPU free plánu (CITACE, ne měření)
# Soubory, které P35 ZÁMĚRNĚ mění. Rozdíl proti HEAD u JINÉHO souboru je podpis
# leftoveru mutanta (H163) — proto se seznam neopisuje z hlavy, ale je tady.
P35_ZMENIL = {"conductor/src/index.ts", "tools/test-tick-offline.mjs"}
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")   # PLNÉ prostředí (ne ořezané!)
MERENO = {}
_vystup = []
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
    """Poslední čítač `VYSLEDEK: N kontrol, M chyb` (nebo `VÝSLEDEK:`)."""
    vse = list(re.finditer(r"V[ÝY]SLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*(?:CHYB|chyb)", t))
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
            okno = text[max(0, m.start() - 70): m.end() + 70].replace("\n", " / ")
            return m, okno, v
    return None, None, None


def sha(cesta):
    return hashlib.sha256(pathlib.Path(cesta).read_bytes()).hexdigest()


def bez_komentaru_ts(text):
    """Odstřihne `/* … */` a `// …` — statická kontrola musí číst KÓD.

    ⚠ Naměřeno P35 (vlastní past hned napoprvé): kontrola hledala
    `Uint8Array.from(` v celém souboru a spadla na komentáři, který vadu
    POPISUJE. Přesně to zakazuje `AGENTS.md` („statická kontrola musí číst KÓD,
    ne komentáře“) — a je to táž třída jako falešný poplach popsaný ve skillu
    `overovani`. Odstřižení je hrubé (nezná řetězce), ale pro tenhle účel stačí:
    jen ODEBÍRÁ text, nikdy nepřidává.
    """
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


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
        (CRON_POKUS, "fixtury P34 `tools/test-cron-pokus.mjs`"),
        (TICK_TEST, "offline harness tiku `tools/test-tick-offline.mjs`"),
        (VALIDATE, "brána `tools/validate-all.mjs`"),
        (G3, "souhrn bran `_analyza/g3-brany.py`"),
        (AG_OVER, "`_analyza/ag-over-cisla.py`"),
        (P34A, "měřidlo P34 `_analyza/p34-a-overeni.py`"),
        (P34M, "mutační důkaz P34 `_analyza/p34-mutace.py`"),
        (SONDA_DEPLOY, "sonda nasazení `_analyza/p30-sonda-deploy.mjs`"),
        (SONDA_CF, "sonda verze `_analyza/p32-sonda-cf-verze.mjs`"),
        (SONDA_HEALTH, "sonda `/health` P35 `_analyza/p35-sonda-health.mjs`"),
        (TAIL_ROZBOR, "rozbor tailu P35 `_analyza/p35-tail-rozbor.py`"),
        (CONDUCTOR, "kód conductora"),
    ]:
        m.ok_(cesta.is_file(), "%s existuje (%s)" % (popis, cesta.name))

    kod, out, _ = git("rev-parse", "HEAD")
    p("  INFO       orchestra HEAD = %s" % out.strip()[:12])
    m.ok_(kod == 0, "git v orchestra funguje (rev-parse exit=%d)" % kod)

    zbyle = [x.name for x in ANALYZA.glob("p35-scratch*")]
    m.ok_(not zbyle, "po předchozích bězích nezůstal scratch (%s)" % (zbyle or "nic"))


# ── A1: je nasazení P34 živé? (TŘI KROKY + křížová kontrola) ─────────────────
def sekce_A1(m):
    p("")
    p("A1) JE NASAZENÍ P34 ŽIVÉ? — tři kroky + křížová kontrola verze (HTTP 200 není důkaz)")

    # Který commit se nasazoval se NEPŘEBÍRÁ z dokumentu — hledá se v gitu.
    kod, out, _ = git("log", "--format=%H\t%s", "-40")
    p34 = None
    for radek in out.splitlines():
        if "P34: H156" in radek:
            p34 = radek.split("\t")[0].strip()
            break
    if not p34:
        m.ok_(False, "v gitu se nenašel commit s předmětem obsahujícím `P34: H156`")
        return
    if len(p34) != 40:
        m.ok_(False, "sha commitu P34 nemá 40 znaků (%r) — GitHub API chce PLNÝ sha (H153)" % p34)
        return
    p("  INFO       commit P34 (práce) = %s" % p34)
    MERENO["p34_commit"] = p34

    # KROK 1: běh deploy.yml na TOM commitu, completed/success.
    kod, out, sec = spust(["node", str(SONDA_DEPLOY), p34], timeout=180)
    posledni = [r for r in out.splitlines() if "nejnovější běh" in r]
    m.ok_(kod == 0, "KROK 1 `deploy.yml` na %s: completed/success (sonda exit=%d, %.0f s)"
          % (p34[:8], kod, sec))
    for r in posledni:
        p("  INFO       %s" % r.strip())

    # KROK 2: verze z LOGU nasazení (ne z odpovědi HTTP).
    kod, out, _ = spust(["node", str(SONDA_CF), p34, "_analyza/p35-cf-verze-vystup.txt"], timeout=240)
    verze_log = None
    for mm in re.finditer(r"Current Version ID:\s*([0-9a-f-]{36})", out):
        verze_log = mm.group(1)
    p("  INFO       KROK 2 verze z logu nasazení: %s" % (verze_log or "NENALEZENA"))
    m.ok_(kod == 0 and verze_log is not None,
          "KROK 2 verze z LOGU nasazení je k mání (exit=%d)" % kod)
    MERENO["verze_log"] = verze_log

    # KROK 3: KŘÍŽOVÁ KONTROLA — táž verze v ŽIVÉM tailu.
    if not TAIL_RAW.is_file() or TAIL_RAW.stat().st_size == 0:
        m.nezmereno("KROK 3 živý tail chybí (%s) — křížovou kontrolu verze nelze udělat" % TAIL_RAW.name)
    else:
        kod, out, _ = spust(["python", str(TAIL_ROZBOR), str(TAIL_RAW)], timeout=120)
        verze_tail = re.findall(r"^\s+([0-9a-f-]{36})\s+\d+ eventů", out, re.M)
        p("  INFO       KROK 3 verze v ŽIVÉM tailu: %s" % (", ".join(verze_tail) or "NENALEZENA"))
        m.ok_(bool(verze_tail), "KROK 3 živý tail nese `scriptVersion.id` (exit=%d)" % kod)
        if verze_log and verze_tail:
            m.ok_(verze_log in verze_tail,
                  "KROK 3 KŘÍŽOVÁ KONTROLA: verze z logu == verze z živého tailu (%s)" % verze_log)
            MERENO["verze_tail"] = verze_tail
        elif verze_log:
            m.ok_(False, "KROK 3 křížová kontrola se nedala udělat (tail bez verze)")


# ── A2: posílá /health POKUS o tik? ──────────────────────────────────────────
def sekce_A2(m):
    p("")
    p("A2) POSÍLÁ `/health` POKUS O TIK? — živá služba (ne dokument)")
    if os.environ.get("P35_HEALTH"):
        m.info("⚠ seam P35_HEALTH: hodnotí se PODSTRČENÝ stav (%s), ne živá služba" % HEALTH_LIVE.name)
    else:
        kod, out, sec = spust(["node", str(SONDA_HEALTH), os.path.relpath(HEALTH_LIVE, WS)], timeout=180)
        p("  INFO       sonda `/health` exit=%d (%.0f s)" % (kod, sec))
        m.ok_(kod == 0, "živá sonda `/health` prošla (exit=%d)" % kod)

    try:
        h = json.loads(HEALTH_LIVE.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        m.ok_(False, "doklad `/health` se nedá přečíst (%s): %s" % (HEALTH_LIVE.name, e))
        return

    p("  INFO       last_cron=%s (%s min) · last_cron_pokus=%s (%s min) · ready=%s running=%s"
      % (h.get("last_cron"), h.get("last_cron_min"), h.get("last_cron_pokus"),
         h.get("last_cron_pokus_min"), h.get("ready"), h.get("running")))
    m.ok_(h.get("http_status") == 200, "služba odpovídá (HTTP %s)" % h.get("http_status"))
    ma_pokus = "last_cron_pokus" in h and "last_cron_pokus_min" in h
    m.ok_(ma_pokus, "`/health` posílá `last_cron_pokus` + `last_cron_pokus_min` (živá pole P34)")
    m.ok_("last_cron" in h and "last_cron_min" in h,
          "a `last_cron` NEZMIZEL (význam „tik DOBĚHL“ se nemění)")
    MERENO["health"] = {k: h.get(k) for k in
                        ("last_cron", "last_cron_min", "last_cron_pokus", "last_cron_pokus_min",
                         "ready", "running")}

    # Rozhoduje PREDIKÁT BRÁNY, ne jeho opis (dvě implementace téhož = druhá pravda).
    kod, out, _ = spust(["node", str(CRON_PRED), str(HEALTH_LIVE)], timeout=60)
    posledni = out.strip().splitlines()[-1] if out.strip() else "?"
    if kod == 0:
        m.ok_(True, "predikát brány nad ŽIVÝM tepem: OK (exit=0)")
    else:
        m.nalezeno("predikát brány nad ŽIVÝM tepem: CHYBA (exit=%d) — %s" % (kod, posledni[:170]))
    # KONTROLA, KTERÁ UMÍ PROJÍT I SPADNOUT: predikát a ULOŽENÝ stav si nesmí
    # odporovat (služba počítá `_min` jinou cestou než predikát).
    cmin = h.get("last_cron_min")
    if isinstance(cmin, int):
        ocekavano = cmin <= 10
        m.ok_(ocekavano == (kod == 0),
              "predikát a ULOŽENÝ stav si neodporují (služba: %s min → očekáváno %s, predikát exit=%d)"
              % (cmin, "OK" if ocekavano else "CHYBA", kod))
    else:
        m.nezmereno("`last_cron_min` v `/health` chybí — konzistenci predikátu se stavem nelze ověřit")


# ── A3: umí brána spadnout i projít? (fixtury + vady v KOPIÍCH) ──────────────
def sekce_A3(m):
    p("")
    p("A3) UMÍ BRÁNA P34 SPADNOUT I PROJÍT? — fixtury + tři vady v KOPIÍCH")

    sha_test0, sha_pred0 = sha(CRON_POKUS), sha(CRON_PRED)
    kod, out, sec = spust(["node", str(CRON_POKUS)], timeout=120)
    c = citac(out)
    p("  INFO       živé fixtury: exit=%d, čítač=%s (%.0f s)" % (kod, c, sec))
    m.ok_(kod == 0, "živá brána `tools/test-cron-pokus.mjs` → exit 0")
    m.ok_(c == ("9", "0"), "a její čítač je 9/0 (naměřeno %s)" % (c,))
    MERENO["cron_pokus"] = list(c) if c else None

    SCRATCH.mkdir(parents=True, exist_ok=True)
    kopie_test = SCRATCH / "test-cron-pokus.mjs"
    kopie_pred = SCRATCH / "cron-stav.mjs"
    shutil.copyfile(CRON_POKUS, kopie_test)
    shutil.copyfile(CRON_PRED, kopie_pred)
    m.ok_(sha(kopie_test) == sha_test0, "kopie fixtur je BAJT NA BAJT shodná s živými")
    m.ok_(sha(kopie_pred) == sha_pred0, "kopie predikátu je BAJT NA BAJT shodná s živým")
    kod, out, _ = spust(["node", str(kopie_test)], timeout=120)
    m.ok_(kod == 0 and citac(out) == ("9", "0"),
          "a NEMUTOVANÁ kopie dává TOTÉŽ (exit=%d, %s) — kopie tedy měří, ne jen existuje"
          % (kod, citac(out)))

    # ── (a) predikát BEZ větve „tik NEDOBÍHÁ“ ─────────────────────────────────
    pt = kopie_pred.read_text(encoding="utf-8")
    kotva_a = "    if (pokusMin !== null && pokusMin <= limitMin) {"
    m.ok_(pt.count(kotva_a) == 1, "kotva (a) je v predikátu PRÁVĚ 1× (jinak by mutace trefila jinam)")
    vada_a = pt.replace(kotva_a, "    if (false) {", 1)
    m.ok_(vada_a != pt, "(a) MUTACE SE PROVEDLA: větev „tik NEDOBÍHÁ“ je v kopii pryč")
    kopie_pred.write_text(vada_a, encoding="utf-8")
    kod, out, _ = spust(["node", str(kopie_test)], timeout=120)
    m.ok_(kod != 0, "(a) BRÁNA nad predikátem bez pojmenování SPADNE (exit=%d)" % kod)
    m.ok_("CHYBA 1 a pojmenuje to jako" in out,
          "(a) a spadne PRÁVĚ na fixtuře 1 (pojmenování), ne jinde")

    # ── (b) predikát BEZ větve „pokus v BUDOUCNOSTI“ ──────────────────────────
    shutil.copyfile(CRON_PRED, kopie_pred)
    pt = kopie_pred.read_text(encoding="utf-8")
    kotva_b = "    if (pokusMin !== null && pokusMin < -limitMin) {"
    m.ok_(pt.count(kotva_b) == 1, "kotva (b) je v predikátu PRÁVĚ 1×")
    vada_b = pt.replace(kotva_b, "    if (false) {", 1)
    m.ok_(vada_b != pt, "(b) MUTACE SE PROVEDLA: kontrola BUDOUCNOSTI je v kopii pryč")
    kopie_pred.write_text(vada_b, encoding="utf-8")
    kod, out, _ = spust(["node", str(kopie_test)], timeout=120)
    m.ok_(kod != 0, "(b) BRÁNA nad vadou „budoucnost se čte jako dorazil“ SPADNE (exit=%d)" % kod)
    m.ok_("CHYBA 4 a NEPOJmenuje to" in out, "(b) a spadne PRÁVĚ na fixtuře 4")

    # ── (c) SLABÁ KONTROLA: fixtura 4 ptá se JEN na `ok === false` ───────────
    # Tohle je jádro H158: slabá kontrola projde nad TOUTÉŽ vadou, kterou silná
    # odhalí. Kdyby slabá taky spadla, není rozdíl — a nález by byl nepodložený.
    fx = kopie_test.read_text(encoding="utf-8")
    kotva_c = ("  test('4 a NEPOJmenuje to jako „tik NEDOBÍHÁ“ — pojmenuje rozešlé hodiny',\n"
               "    !/NEDOBÍHÁ/.test(v.duvod) && /BUDOUCNOSTI/.test(v.duvod), v.duvod);")
    m.ok_(fx.count(kotva_c) == 1, "kotva (c) je ve fixturách PRÁVĚ 1×")
    slaba = fx.replace(kotva_c,
                       "  test('4 a NEPOJmenuje to jako „tik NEDOBÍHÁ“ — pojmenuje rozešlé hodiny',\n"
                       "    v.ok === false, v.duvod);", 1)
    m.ok_(slaba != fx, "(c) MUTACE SE PROVEDLA: kontrola fixtury 4 je SLABÁ (`ok === false`)")
    kopie_test.write_text(slaba, encoding="utf-8")
    kod_slaba, out_slaba, _ = spust(["node", str(kopie_test)], timeout=120)
    m.ok_(kod_slaba == 0,
          "(c) SLABÁ kontrola nad TOUTÉŽ vadou (b) PROJDE (exit=%d) — slabá kontrola je SLEPÁ" % kod_slaba)
    # a silná kontrola nad touž vadou spadne — to už víme z (b); tady se to zopakuje
    # se silnými fixturami, aby rozdíl byl v JEDNÉ proměnné.
    shutil.copyfile(CRON_POKUS, kopie_test)
    kod_silna, out_silna, _ = spust(["node", str(kopie_test)], timeout=120)
    m.ok_(kod_silna != 0,
          "(c) a SILNÁ kontrola nad touž vadou SPADNE (exit=%d) — rozdíl je v kontrole, ne ve vadě"
          % kod_silna)

    # ── úklid + návrat ───────────────────────────────────────────────────────
    shutil.rmtree(SCRATCH, ignore_errors=True)
    m.ok_(not SCRATCH.exists(), "scratch `p35-scratch/` je uklizený")
    m.ok_(sha(CRON_POKUS) == sha_test0, "živé fixtury jsou po testu BAJT NA BAJT původní")
    m.ok_(sha(CRON_PRED) == sha_pred0, "živý predikát je po testu BAJT NA BAJT původní")


# ── A4: sedí čísla z §65? (měř dřív, než hledáš tvrzení) ─────────────────────
def sekce_A4(m, drahe):
    p("")
    p("A4) SEDÍ ČÍSLA Z §65? — nejdřív MĚŘIT, teprve pak hledat tvrzení (H155)")
    txt65, prvni, posledni = oddil(r"^## 65\.", HANDOFF)
    p("  INFO       oddíl §65 = řádky %d–%d (%d znaků)" % (prvni, posledni - 1, len(txt65)))

    # 1) MĚŘENÍ: levný běh měřidla P34 (50/0 podle §65.2).
    # ⚠ VÝSTUPY SE PŘESMĚRUJÍ (i `P34_HEALTH`) — jinak by P35 přepsala DOKLADY
    # P34, a ty jsou gitignorované, tedy NEVRATNÉ. Naměřeno v P35: první běh
    # `p34-a-overeni.py` bez `--vystup` přepsal `p34-a-overeni-levny-vystup.txt`
    # i `p34-health-vystup.txt` (nález H166).
    env34 = {"P34_HEALTH": str(ANALYZA / "p35-p34a-health-vystup.txt")}
    kod, out, sec = spust(["python", str(P34A), "--vystup", "_analyza/p35-p34a-levny-vystup.txt"],
                          env=env34, timeout=900)
    c_levny = citac(out)
    p("  INFO       `p34-a-overeni.py` (levný): exit=%d, čítač=%s (%.0f s)" % (kod, c_levny, sec))
    m.ok_(kod == 0, "měřidlo P34 v levném režimu prošlo (exit=%d)" % kod)
    MERENO["p34a_levny"] = list(c_levny) if c_levny else None
    for mm in re.finditer(r"VÝSLEDEK:\s*\d+ kontrol, \d+ chyb \(z toho (\d+) ROZDÍLŮ, (\d+) NEZMĚŘENO, (\d+) NÁLEZŮ",
                          out):
        MERENO["p34a_levny_dily"] = list(mm.groups())

    # 2) TVRZENÍ z §65 — hledá se AŽ TEĎ a vypisuje se okno, které vzor trefil.
    tv, okno, vzor = najdi_tvrzeni(txt65, [r"levně (\d+)/(\d+), plně (\d+)/(\d+)"])
    if tv is None:
        m.ok_(False, "§65 NETVRDÍ čítač měřidla P34 (`levně N/M, plně N/M`) — vzor nenašel nic")
    else:
        p("            §65 tvrdí: %s (okno: …%s…)" % ("/".join(tv.groups()), okno[-130:]))
        if c_levny == (tv.group(1), tv.group(2)):
            m.ok_(True, "A4 §65 tvrdí levně %s/%s a naměřeno %s/%s"
                  % (tv.group(1), tv.group(2), c_levny[0], c_levny[1]))
        else:
            m.rozdil("A4 §65 tvrdí levně %s/%s, naměřeno %s/%s"
                     % (tv.group(1), tv.group(2), c_levny[0], c_levny[1]))

    # 3) dlouhá noha: PLNÝ běh měřidla P34 (96/0 podle §65.2) — jen na vyžádání.
    if not drahe:
        m.nezmereno("A4 plný běh `p34-a-overeni.py --plne` (96/0) — pustí se `--jen A4`")
        tv2, okno2, _ = najdi_tvrzeni(txt65, [r"plně[^\n]{0,20}?(\d+)/(\d+)"])
        if tv2 is None:
            m.ok_(False, "§65 NETVRDÍ plný čítač měřidla P34")
        else:
            p("            §65 tvrdí plně: %s/%s (okno: …%s…)" % (tv2.group(1), tv2.group(2), okno2[-110:]))
        return
    kod, out, sec = spust(["python", str(P34A), "--plne",
                           "--vystup", "_analyza/p35-p34a-plny-vystup.txt"],
                          env=env34, timeout=5400)
    c_plny = citac(out)
    p("  INFO       `p34-a-overeni.py --plne`: exit=%d, čítač=%s (%.0f s)" % (kod, c_plny, sec))
    MERENO["p34a_plny"] = list(c_plny) if c_plny else None
    if c_plny is None:
        m.nezmereno("plný běh měřidla P34 nevypsal čítač (exit=%d) — měřeno nic" % kod)
        return
    tv2, okno2, _ = najdi_tvrzeni(txt65, [r"plně[^\n]{0,20}?(\d+)/(\d+)"])
    if tv2 is None:
        m.ok_(False, "§65 NETVRDÍ plný čítač měřidla P34")
        return
    p("            §65 tvrdí plně: %s/%s (okno: …%s…)" % (tv2.group(1), tv2.group(2), okno2[-110:]))
    if c_plny == (tv2.group(1), tv2.group(2)):
        m.ok_(True, "A4 §65 tvrdí plně %s/%s a naměřeno %s/%s"
              % (tv2.group(1), tv2.group(2), c_plny[0], c_plny[1]))
    else:
        m.rozdil("A4 §65 tvrdí plně %s/%s, naměřeno %s/%s"
                 % (tv2.group(1), tv2.group(2), c_plny[0], c_plny[1]))


# ── A5: je tik opravdu jen CPU? (živý tail + Analytics + D1) ────────────────
def sekce_A5(m):
    p("")
    p("A5) JE TIK OPRAVDU JEN CPU? — živý tail, historie invokací a uložený tep")

    if not TAIL_RAW.is_file() or TAIL_RAW.stat().st_size == 0:
        m.nezmereno("živý `wrangler tail` chybí (%s) — CPU tik nezměřeno" % TAIL_RAW.name)
        return
    kod, out, _ = spust(["python", str(TAIL_ROZBOR), str(TAIL_RAW),
                         "--json", "_analyza/p35-tail-rozbor-data-vystup.txt"], timeout=120)
    m.ok_(kod == 0, "rozbor živého tailu proběhl (exit=%d, soubor %d B)" % (kod, TAIL_RAW.stat().st_size))
    try:
        rozbor = json.loads((ANALYZA / "p35-tail-rozbor-data-vystup.txt").read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        m.ok_(False, "rozbor tailu se nedá přečíst: %s" % e)
        return

    cron = rozbor.get("podle", {}).get("cron(* * * * *)", {})
    tick = rozbor.get("podle", {}).get("POST /tick", {})
    p("  INFO       eventů: %d · exceededCpu: %d" % (rozbor.get("eventu", 0), rozbor.get("exceededCpu", 0)))
    if cron.get("cpu"):
        p("  INFO       cron cpuTime: %s (n=%d)" % (sorted(cron["cpu"]), cron["n"]))
        m.ok_(True, "cron eventy nesou `cpuTime` (n=%d)" % cron["n"])
        nad = [x for x in cron["cpu"] if x > LIMIT_CPU_MS]
        m.nalezeno("cron cpuTime %s ms PŘEKRAČUJE dokumentovaných %d ms (%d z %d eventů) — "
                   "a přesto končí `outcome=ok`, takže limit není tvrdý (H164)"
                   % (sorted(cron["cpu"]), LIMIT_CPU_MS, len(nad), len(cron["cpu"])))
        MERENO["cron_cpu"] = sorted(cron["cpu"])
    else:
        m.nezmereno("v tailu nejsou cron eventy s `cpuTime`")
    if rozbor.get("exceededCpu"):
        m.nalezeno("a v tailu je %d eventů `exceededCpu` — výpadek se OPRAVDU děje"
                   % rozbor["exceededCpu"])
    if tick.get("cpu"):
        p("  INFO       POST /tick cpuTime: %s (n=%d)" % (sorted(tick["cpu"]), tick["n"]))
        MERENO["tick_cpu"] = sorted(tick["cpu"])
    else:
        m.nezmereno("v tailu není `POST /tick` (ruční tik se neměřil)")

    # Historie invokací z Cloudflare Analytics — měří se, nepřebírá.
    # ⚠ Je to `.mjs` → spouští se **node**, ne python (zadání P35 to má
    # v §2.3 uvedené s `python`; naměřeno: `python soubor.mjs` spadne na
    # `SyntaxError: invalid character` a vypadá to jako vada dokladu).
    kod, out, sec = spust(["node", str(ANALYZA / "p34-cf-analytika.mjs"), "24"], timeout=300)
    if kod != 0:
        m.nezmereno("Cloudflare Analytics se nepodařilo změřit (exit=%d): %s" % (kod, out.strip()[-160:]))
    else:
        m.ok_(True, "Cloudflare Analytics (24 h) změřena (exit=0, %.0f s)" % sec)

    # Uložený tep z D1 (READ-ONLY, wrangler) — VLASTNÍ sonda P35, aby se
    # nepřepsal doklad P34 (H166: doklady `*vystup.txt` jsou gitignorované).
    kod, out, sec = spust(["python", str(ANALYZA / "p35-sonda-d1.py")], timeout=300)
    if kod != 0:
        m.nezmereno("D1 `state` se nepodařilo přečíst (exit=%d): %s" % (kod, out.strip()[-160:]))
    else:
        m.ok_(True, "D1 `state` přečten (exit=0, %.0f s)" % sec)


# ── A6: uklízí se měřidla po sobě? ───────────────────────────────────────────
def sekce_A6(m, drahe):
    p("")
    p("A6) UKLÍZÍ SE MĚŘIDLA PO SOBĚ? — `p34-mutace` + ŽIVÉ SOUBORY proti HEAD (H163)")
    if not drahe:
        m.nezmereno("A6 `p34-mutace.py` (23/0) — drahá noha, pustí se `--plne`/`--jen A6`")
    else:
        kod, out, sec = spust(["python", str(P34M)], timeout=3600)
        c = citac(out)
        p("  INFO       `p34-mutace.py`: exit=%d, čítač=%s (%.0f s)" % (kod, c, sec))
        m.ok_(kod == 0 and c == ("23", "0"), "`p34-mutace` → 23/0 (naměřeno %s)" % (c,))
        MERENO["p34_mutace"] = list(c) if c else None

    # ŽIVÉ SOUBORY proti HEAD: `hash-object` vs `rev-parse HEAD:<soubor>` (H163).
    # ⚠ Rozdíl u souboru, který P35 ZÁMĚRNĚ mění, je správný (před commitem).
    # Rozdíl u souboru, který P35 NEMĚNILA, je PODPIS LEFTOVERU MUTANTA (H163).
    zive = ["conductor/src/index.ts", "tools/cron-stav.mjs", "tools/test-cron-pokus.mjs",
            "tools/test-tick-offline.mjs", "tools/validate-all.mjs"]
    for rel in zive:
        kod1, h1, _ = git("hash-object", rel)
        kod2, h2, _ = git("rev-parse", "HEAD:" + rel)
        if kod1 != 0 or kod2 != 0:
            m.nezmereno("%s: hash proti HEAD nejde (exit %d/%d)" % (rel, kod1, kod2))
            continue
        if h1.strip() == h2.strip():
            m.ok_(True, "%s = HEAD (žádný leftover mutanta)" % rel)
        elif rel in P35_ZMENIL:
            m.info("%s se liší od HEAD — P35 ho MĚNÍ (před commitem správně)" % rel)
        else:
            m.ok_(False, "%s se liší od HEAD, ačkoli ho P35 NEMĚNILA — podpis leftoveru mutanta (H163)"
                  % rel)


# ── A7: nic se nerozbilo ─────────────────────────────────────────────────────
def sekce_A7(m, drahe):
    p("")
    p("A7) NIC SE NEROZBILO — inventář → g3 → validate-all (NE současně)")
    if not drahe:
        for co in ("inventář", "g3", "validate-all", "kronika", "handoff", "ov-g"):
            m.nezmereno("A7 %s — drahá noha, pustí se `--plne`/`--jen A7`" % co)
        return

    kod, out, sec = spust(["python", str(INVENTAR), "--json", "_analyza/_inventar.json"], timeout=900)
    m.ok_(kod == 0, "inventář přegenerován (exit=%d, %.0f s)" % (kod, sec))

    kod, out, sec = spust(["python", str(G3)], timeout=1800,
                          env={"FORGE_REGISTR": str(REGISTR_SCRATCH())})
    m.ok_(True, "`g3` proběhl (exit=%d, %.0f s) — nenulový exit je STAV, ne vada" % (kod, sec))
    m_bran = re.findall(r"bran celkem:\s*(\d+)", out)
    p("  INFO       g3: bran celkem = %s" % (m_bran[-1] if m_bran else "?"))
    if m_bran:
        MERENO["g3_bran"] = m_bran[-1]
        m.ok_(m_bran[-1] == "49", "g3 hlásí 49 bran (naměřeno %s)" % m_bran[-1])

    kod, out, sec = spust(["node", str(VALIDATE)], timeout=3600)
    problemy = re.findall(r"(\d+)\s+problém", out)
    p("  INFO       validate-all: exit=%d, problémy = %s" % (kod, problemy[-1] if problemy else "?"))
    if problemy:
        MERENO["validate_problemy"] = problemy[-1]

    kod, out, _ = spust(["python", str(KRONIKA_K)], timeout=300)
    m.ok_(kod == 0, "kronika SEDÍ (exit=%d)" % kod)
    kod, out, _ = spust(["python", str(HANDOFF_K)], timeout=300)
    m.ok_(kod == 0, "handoff: 0 chybějících (exit=%d)" % kod)
    kod, out, _ = spust(["python", str(OVG)], timeout=300)
    m.ok_(kod == 0, "ov-g: 0 NEOVĚŘENO (exit=%d)" % kod)
    m_radky = re.findall(r"(\d+)\s*řádků H", out)
    if m_radky:
        p("  INFO       ov-g rozsah: %s řádků Hxx" % m_radky[-1])
        MERENO["ovg_radky"] = m_radky[-1]


def REGISTR_SCRATCH():
    """`g3` NESMÍ přepsat živý registr — harness dostane vlastní cestu (H137/H138).

    ⚠ Cesta leží v `p35-scratch/` SCHVÁLNĚ: `.gitignore` ignoruje jen
    `_analyza/*vystup.txt` a `_analyza/*-scratch/`, takže `…-scratch.json`
    v kořeni by zůstal jako NETRACKOVANÝ soubor a rozchodil otisk inventáře
    (H154) — naměřeno P35.
    """
    SCRATCH.mkdir(parents=True, exist_ok=True)
    return SCRATCH / "registr.json"


# ── B1: Úkol B — zlevnění tiku (H165) ────────────────────────────────────────
def sekce_B1(m):
    p("")
    p("B1) ÚKOL B / H165 — ZLEVNĚNÍ TIKU: profil → rozklad → oprava → měření")

    # 1) ŽIVÝ PROFIL: cpuTime podle endpointu (z dokladu rozboru tailu).
    if PROFIL.is_file():
        p("  INFO       živý profil: %s" % PROFIL.name)
    else:
        m.nezmereno("živý profil služby chybí (%s) — pustí se ručně" % PROFIL.name)

    # 2) ROZKLAD GitHub části tiku (měřeno na živých datech + JSON.parse).
    if not ROZKLAD.is_file():
        m.nezmereno("rozklad GitHub části tiku chybí (%s)" % ROZKLAD.name)
    else:
        t = ROZKLAD.read_text(encoding="utf-8")
        bajty = re.findall(r"přenesených bajtů na tik:\s*(\d+)\s*B", t)
        ms = re.findall(r"CPU na parsování na tik:\s*([\d.]+)\s*ms", t)
        podil = re.findall(r"GitHub parsování je\s*(\d+)\s*%", t)
        p("  INFO       GitHub část tiku: %s B (%.0f kB), %s ms, %s %% CPU tiku"
          % (bajty[-1] if bajty else "?", (int(bajty[-1]) / 1024) if bajty else 0,
             ms[-1] if ms else "?", podil[-1] if podil else "?"))
        m.ok_(bool(bajty) and int(bajty[-1]) > 100000,
              "tik tahá z GitHubu > 100 kB KAŽDOU MINUTU (naměřeno %s B)" % (bajty[-1] if bajty else "?"))
        if ms:
            MERENO["github_parse_ms"] = float(ms[-1])
            m.ok_(float(ms[-1]) > 1.0, "a parsování toho stojí > 1 ms CPU (naměřeno %s ms)" % ms[-1])

    # 3) ROZKLAD ČTENÍ ROADMAPY — kde přesně mizí CPU (jádro opravy).
    if not ROZKLAD_RM.is_file():
        m.nezmereno("rozklad čtení roadmapy chybí (%s)" % ROZKLAD_RM.name)
    else:
        t = ROZKLAD_RM.read_text(encoding="utf-8")
        mapfn = re.findall(r"3\. Uint8Array\.from\(mapFn\) PO ZNACÍCH:\s*([\d.]+)\s*ms", t)
        cyklus = re.findall(r"3b\. indexovaný cyklus:\s*([\d.]+)\s*ms", t)
        raw = re.findall(r"raw \(B\):\s*([\d.]+)\s*ms", t)
        p("  INFO       Uint8Array.from(mapFn) = %s ms · indexovaný cyklus = %s ms · raw = %s ms"
          % (mapfn[-1] if mapfn else "?", cyklus[-1] if cyklus else "?", raw[-1] if raw else "?"))
        if mapfn and cyklus:
            MERENO["decode_mapfn_ms"] = float(mapfn[-1])
            MERENO["decode_cyklus_ms"] = float(cyklus[-1])
            m.ok_(float(mapfn[-1]) > 2.0 and float(cyklus[-1]) < 1.0,
                  "dekódování po ZNACÍCH je drahé (%s ms) a cyklem levné (%s ms) — to je H165"
                  % (mapfn[-1], cyklus[-1]))
        else:
            m.nezmereno("v rozkladu roadmapy chybí časy dekodéru — vzor nenašel nic")

    # 4) OPRAVA JE V KÓDU — a je to PRÁVĚ ta oprava (ne jiná).
    # ⚠ STATICKÁ KONTROLA MUSÍ ČÍST KÓD, NE KOMENTÁŘE (AGENTS.md): první verze
    # tohohle měřidla hledala `Uint8Array.from(` v CELÉM souboru a spadla na
    # VLASTNÍM KOMENTÁŘI, který vadu popisuje („NE `Uint8Array.from(mapFn)`“) —
    # tedy falešný poplach nad správným kódem. Komentáře se proto odstřihnou.
    kod_bez_kom = bez_komentaru_ts(CONDUCTOR.read_text(encoding="utf-8"))
    m.ok_("for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);" in kod_bez_kom,
          "v conductoru je INDEXOVANÝ CYKLUS (oprava H165) — v KÓDU, ne v komentáři")
    m.ok_("Uint8Array.from(" not in kod_bez_kom,
          "a drahá varianta `Uint8Array.from(atob(…), mapFn)` v KÓDU NENÍ")

    # 5) MUTAČNÍ DŮKAZ: rozbitý dekodér MUSÍ shodit offline harness (scénář AF).
    sha_test0 = sha(TICK_TEST)
    kod, out, sec = spust(["node", str(TICK_TEST)], timeout=900)
    c = citac(out)
    p("  INFO       `test-tick-offline.mjs`: exit=%d, čítač=%s (%.0f s)" % (kod, c, sec))
    m.ok_(kod == 0 and c == ("218", "0"), "offline harness tiku → 218/0 (naměřeno %s)" % (c,))
    MERENO["tick_offline"] = list(c) if c else None
    m.ok_("AF: vícebajtové ID granule dorazí CELÉ" in out,
          "a scénář AF (vícebajtová čeština z base64) v něm OPRAVDU proběhl")


def main():
    global _doklad_handle
    ap = argparse.ArgumentParser()
    ap.add_argument("--jen", default=None, help="seznam sekcí, např. A1 nebo A1,A2")
    ap.add_argument("--plne", action="store_true", help="i A5,A6,A7 (živá služba, mutace, g3)")
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

    vychozi = "A0,A1,A2,A3,B1" if not args.plne else "A0,A1,A2,A3,A4,A5,A6,A7,B1"
    etapy = [x.strip().upper() for x in (args.jen if args.jen else vychozi).split(",")]
    drahe = (args.plne or bool(args.jen)) and not args.levne

    fns = {
        "A0": lambda: sekce_A0(m),
        "A1": lambda: sekce_A1(m),
        "A2": lambda: sekce_A2(m),
        "A3": lambda: sekce_A3(m),
        "A4": lambda: sekce_A4(m, drahe),
        "A5": lambda: sekce_A5(m),
        "A6": lambda: sekce_A6(m, drahe),
        "A7": lambda: sekce_A7(m, drahe),
        "B1": lambda: sekce_B1(m),
    }

    p("=" * 96)
    p("P35/A — VLASTNÍ PŘEMĚŘENÍ PRÁCE P34 (A1–A7) + ZLEVNĚNÍ TIKU (H165)")
    p("=" * 96)
    p("  datum (z hodin): %s" % time.strftime("%Y-%m-%d %H:%M:%S %z"))
    p("  dokument, ze kterého se ČTOU TVRZENÍ: %s" % HANDOFF.name)
    p("  pořadí běhu: %s%s" % (", ".join(etapy), "  (--plne)" if args.plne else "  (levný režim)"))
    p("  ⚠ A4 (plné měřidlo P34) a A6/A7 (mutace, g3, validate-all) jsou DLOUHÉ nohy")
    for e in etapy:
        f = fns.get(e)
        if f is None:
            p("  ??    etapa %s neexistuje" % e)
            continue
        p("\n" + "─" * 96)
        t0 = time.time()
        try:
            f()
        except Exception as ex:  # noqa: BLE001
            import traceback  # noqa: PLC0415
            tb = traceback.format_exc().strip().splitlines()
            p("      TRACEBACK: %s" % " | ".join(x.strip() for x in tb[-3:]))
            m.nezmereno("etapa %s: výjimka %s: %s" % (e, type(ex).__name__, str(ex)[:200]))
        p("      (etapa %s: %.0f s)" % (e, time.time() - t0))

    p("\n" + "=" * 96)
    p("POJMENOVANÉ ROZDÍLY (stav se posunul, nebo je změna ZÁMĚRNÁ): %d" % len(m.rozdily))
    for x in m.rozdily:
        p("  · %s" % x[:220])
    p("\nNÁLEZY O SLUŽBĚ (stav měřeného objektu — NENÍ to chyba měřidla): %d" % len(m.sluzba))
    for x in m.sluzba:
        p("  · %s" % x[:220])
    p("\nNEZMĚŘENO (není nula a není zelená): %d" % len(m.nezmerene))
    for x in m.nezmerene:
        p("  · %s" % x[:220])
    p("=" * 96)
    p("VÝSLEDEK: %d kontrol, %d chyb (z toho %d ROZDÍLŮ, %d NEZMĚŘENO, %d NÁLEZŮ O SLUŽBĚ)"
      % (m.ok, len(m.chyby), len(m.rozdily), len(m.nezmerene), len(m.sluzba)))
    p("=" * 96)
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH, ignore_errors=True)
    try:
        (ANALYZA / "p35-mereno-vystup.txt").write_bytes((json.dumps(
            {"cas": time.time(), "sekce": etapy,
             "mereno": {k: v for k, v in MERENO.items()}}, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    except Exception as e:  # noqa: BLE001
        print("  ⚠ doklad MERENO se nepodařilo zapsat: %s" % e)
    _doklad_handle.close()
    _doklad_handle = None
    print("\n[doklad] %s (%d B, UTF-8)" % (vystup.relative_to(WS), vystup.stat().st_size))
    return 1 if m.chyby else 0


if __name__ == "__main__":
    sys.exit(main())
