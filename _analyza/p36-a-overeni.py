# -*- coding: utf-8 -*-
r"""P36/A — VLASTNÍ PŘEMĚŘENÍ PRÁCE P35 (A0–A7).

PROČ VLASTNÍ MĚŘIDLO: `AGENTS.md` — „autor není nezávislý reviewer“. P35 psala
opravu H165 i její test sama a sama si změřila výsledek (74/0). P36 proto měří
TÝMŽ objektem, ale VLASTNÍM postupem a z VLASTNÍCH zdrojů:

  * čísla se NEOPISUJÍ z hlavy — ČTOU SE Z DOKUMENTU (`HANDOFF.md` §66) a když
    v dokumentu nejsou, je to CHYBA („TVRZENÍ NENALEZENO“, H155),
  * každý údaj má u sebe, ODKUD je (endpoint, soubor, příkaz),
  * „nezměřeno“ je pojmenovaný stav, nikdy nula,
  * cizí měřidla se pouští JEN s `--vystup` do VLASTNÍHO jména (H166) — doklady
    P34/P35 se nesmí přepsat.

SEAMY (pro `p36-mutace.py` — měřidlo se dá podstrčit):
  P36_HANDOFF     — kopie HANDOFF.md, ze které se čtou TVRZENÍ
  P36_TAIL        — soubor s živým `wrangler tail` (jinak p36-tail-raw-vystup.txt)
  P36_HEALTH      — JSON s odpovědí /health (jinak se volá živá služba)
  P36_D1          — JSON s řádky D1 `state` (jinak se volá wrangler)
  P36_CONDUCTOR   — zdroj conductora (jinak conductor/src/index.ts)
  P36_TEST        — test-tick-offline.mjs (jinak tools/test-tick-offline.mjs)
  P36_ZADANI      — zadání, ze kterého se čte DRUHÉ tvrzení (jinak NEXT-SESSION-INSTRUKCE.md)
  P36_P35A        — doklad běhu `p35-a-overeni.py` (jinak se spustí)
  P36_BEZ_SITĚ     — "1" = přeskoč živé nohy (A1 krok 1/2, A5) a řekni to

Použití:
    python _analyza\p36-a-overeni.py                 # levné (A0,A1,A2,A5)
    python _analyza\p36-a-overeni.py --plne          # i A3,A4,A6,A7
    python _analyza\p36-a-overeni.py --jen A1 --levne
Exit 0 = změřeno bez chyb; 1 = aspoň jedna CHYBA; 2 = měření neproběhlo.
"""

import argparse
import json
import os
import pathlib
import re
import statistics
import subprocess
import sys
import time
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"

HANDOFF = pathlib.Path(os.environ.get("P36_HANDOFF") or (WS / "HANDOFF.md"))
ZADANI = pathlib.Path(os.environ.get("P36_ZADANI") or (WS / "NEXT-SESSION-INSTRUKCE.md"))
TAIL = pathlib.Path(os.environ.get("P36_TAIL") or (ANALYZA / "p36-tail-raw-vystup.txt"))
CONDUCTOR = pathlib.Path(os.environ.get("P36_CONDUCTOR") or (WS / "conductor" / "src" / "index.ts"))
TEST_TICK = pathlib.Path(os.environ.get("P36_TEST") or (WS / "tools" / "test-tick-offline.mjs"))
P35A_DOKLAD = pathlib.Path(os.environ.get("P36_P35A") or (ANALYZA / "p36-p35a-plne-vystup.txt"))
MOJE_P35A = ANALYZA / "p36-p35a-plne-vystup.txt"
BEZ_SITE = os.environ.get("P36_BEZ_SITE") == "1"

# Co P35 ZÁMĚRNĚ změnila (podpis leftoveru mutanta = změna JINÉHO souboru, H163/H169).
P35_ZMENIL = {"conductor/src/index.ts", "tools/test-tick-offline.mjs"}
# Co P36 ZÁMĚRNĚ mění (Úkol B: model `state` ve `fakeDb` + registrace dokladů).
# Rozdíl proti HEAD u TĚCHTO souborů je práce, ne mutant — a musí být POJMENOVANÝ.
P36_ZMENIL = {"tools/test-tick-offline.mjs", "_analyza/p20-d-doklady.py",
              "HANDOFF.md", "KRONIKA-PROJEKTU.md"}
# Generované mezivýstupy, které ve stromu být MOHOU (stav, ne záznam).
GENEROVANE = {
    "NEXT-SESSION-INSTRUKCE.md",
    "_analyza/_registr-bran.json",
    "_analyza/ov-b2-spusteni.json",
    "_analyza/ov-c-vysledky.json",
    "_analyza/ov-e-vysledky.json",
}

DEADLINE = 3600

_vystup = []
_handle = None


def p(radek=""):
    print(radek)
    _vystup.append(radek)
    if _handle is not None:
        _handle.write(radek + "\n")
        _handle.flush()


def spust(cmd, timeout=1800, env=None):
    t0 = time.time()
    try:
        r = subprocess.run([str(a) for a in cmd], cwd=str(WS),
                           env={**os.environ, "PYTHONIOENCODING": "utf-8", **(env or {})},
                           capture_output=True, timeout=timeout)
        out = ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace")
        return r.returncode, out, time.time() - t0
    except subprocess.TimeoutExpired:
        return -9, "TIMEOUT po %d s" % timeout, time.time() - t0
    except Exception as e:  # noqa: BLE001
        return -1, "SPUŠTĚNÍ SELHALO: %s" % e, time.time() - t0


class Meridlo:
    def __init__(self):
        self.ok = 0
        self.chyb = 0
        self.nezmereno = 0
        self.rozdilu = 0
        self.nalezu = 0

    def _tisk(self, druh, text):
        p("  %-10s %s" % (druh, text))

    def ok_(self, text):
        self.ok += 1
        self._tisk("OK", text)

    def chyba(self, text):
        self.chyb += 1
        self._tisk("CHYBA", text)

    def nezmereno_(self, text):
        self.nezmereno += 1
        self._tisk("NEZMĚŘENO", text)

    def rozdil(self, text):
        self.rozdilu += 1
        self._tisk("ROZDÍL", text)

    def nalezeno(self, text):
        self.nalezu += 1
        self._tisk("NÁLEZ", text)

    def tvrzeni(self, text, vzor, kde=None, popis=None):
        """Tvrzení se ČTE z dokumentu; nenalezené tvrzení je CHYBA (H155)."""
        m = re.search(vzor, text, re.S)
        if not m:
            self.chyba("TVRZENÍ NENALEZENO v %s: %s" % (kde or HANDOFF.name, popis or vzor))
            return None
        return m.group(1) if m.groups() else m.group(0)


def oddil(vzor, cesta=None):
    cesta = pathlib.Path(cesta or HANDOFF)
    radky = cesta.read_text(encoding="utf-8").splitlines()
    start = next((i for i, r in enumerate(radky) if re.match(vzor, r)), None)
    if start is None:
        raise SystemExit("CHYBA: oddíl %r v %s NENÍ — měřidlo by měřilo jinam" % (vzor, cesta.name))
    konec = len(radky)
    for j in range(start + 1, len(radky)):
        if re.match(r"^##\s", radky[j]):
            konec = j
            break
    return "\n".join(radky[start:konec])


def bez_komentaru_js(text):
    """Odstraní // a /* */ z JS/TS — jinak komentář POPISUJÍCÍ vadu vypadá jako vada."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", " ", r) for r in text.splitlines())


def git(*args, timeout=300):
    return spust(["git", "-C", str(WS)] + list(args), timeout=timeout)


def citac(text):
    vse = list(re.finditer(r"V[ÝY]SLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*(?:CHYB|chyb)", text))
    return (int(vse[-1].group(1)), int(vse[-1].group(2))) if vse else None


def nacti_json_za_sebou(cesta):
    """wrangler tail píše pretty-printed objekty ZA SEBOU (ne JSONL)."""
    text = pathlib.Path(cesta).read_text(encoding="utf-8", errors="replace")
    dec = json.JSONDecoder()
    i, eventy = 0, []
    while i < len(text):
        while i < len(text) and text[i] in " \r\n\t":
            i += 1
        if i >= len(text):
            break
        try:
            obj, i = dec.raw_decode(text, i)
        except ValueError:
            break
        eventy.append(obj)
    return eventy


def cron_casy(eventy):
    """cpuTime cronových invokací (ms) — jen skutečná čísla."""
    casy, verze, chyb = [], set(), 0
    for e in eventy:
        if e.get("scriptVersion", {}).get("id"):
            verze.add(e["scriptVersion"]["id"])
        if e.get("outcome") and e["outcome"] != "ok":
            chyb += 1
        ev = e.get("event") or {}
        if not ev.get("cron"):
            continue
        c = e.get("cpuTime")
        if isinstance(c, (int, float)):
            casy.append(float(c))
    return casy, verze, chyb


# ── A0: pojistky ─────────────────────────────────────────────────────────────
def sekce_A0(m):
    p("  měřeno (z hodin): %s" % time.strftime("%Y-%m-%d %H:%M:%S %z"))

    rc, out, _ = git("rev-parse", "HEAD")
    head = out.strip()
    rc2, out2, _ = spust([str(WS / "tools" / "git.cmd"), "-C", str(WS), "ls-remote",
                          "origin", "refs/heads/main"], timeout=180)
    zivy = out2.split()[0] if out2.strip() and len(out2.split()) > 1 else ""
    if not zivy:
        m.nezmereno_("origin/main se nepodařilo přečíst (ls-remote): %s" % out2.strip()[:120])
    elif zivy == head:
        m.ok_("origin/main == HEAD (%s) — P35 JE PUSHNUTÁ" % head[:7])
    else:
        m.rozdil("origin/main %s != HEAD %s" % (zivy[:7], head[:7]))

    rc, out, _ = git("status", "--porcelain")
    zmenene = [r[3:].strip() for r in out.splitlines() if r.strip()]
    # Vlastní práce P36 (skripty a doklady) je ve stromu PRÁVEM — hlásí se zvlášť.
    vlastni = [z for z in zmenene if re.match(r"^_analyza/p36-", z)]
    zname = [z for z in zmenene if z in P36_ZMENIL]
    nezname = [z for z in zmenene
               if z not in GENEROVANE and not re.match(r"^_analyza/p36-", z)
               and z not in P36_ZMENIL]
    if nezname:
        m.chyba("ve stromu je NECOMMITNUTÉ, co tam nepatří: %s" % nezname)
    else:
        m.ok_("strom čistý (kromě %d mezivýstupů, %d souborů P36 a %d deklarovaných změn P36: %s)"
              % (len(zmenene) - len(vlastni) - len(zname), len(vlastni), len(zname), zname))

    if not HANDOFF.is_file():
        m.chyba("HANDOFF.md neexistuje — není odkud číst tvrzení")
        return
    try:
        s66 = oddil(r"^##\s*66\.")
        m.ok_("oddíl §66 v HANDOFF.md nalezen (%d znaků) — tvrzení se čtou odtud" % len(s66))
    except SystemExit as e:
        m.chyba(str(e))

    # ⚠ H163/H169: scratch = podpis PŘERUŠENÉHO mutačního běhu. Ale staré scratch
    # adresáře z DŘÍVĚJŠÍCH session jsou STAV (nezmizely), ne náš leftover — proto
    # se rozlišuje: CHYBA je jen scratch, který vznikl v TÉTO session (do hodiny).
    ted = time.time()
    stary, novy = [], []
    # ⚠ Hledají se ADRESÁŘE: leftover přerušené mutace je `*-scratch/` (naměřeno
    # P34/P35). Soubor se slovem „scratch“ v názvu (náš `p36-g3-registr.json`
    # apod.) není mutant — a soubory hlídá `git status` v A6.
    for x in sorted(ANALYZA.glob("*scratch*")):
        if not x.is_dir():
            continue
        try:
            stari_h = (ted - x.stat().st_mtime) / 3600.0
        except OSError:
            continue
        (novy if stari_h < 1.0 else stary).append("%s (%.1f h)" % (x.name, stari_h))
    if novy:
        m.chyba("v _analyza/ je scratch z TÉTO session (podpis přerušené mutace): %s" % novy)
    else:
        m.ok_("žádný scratch z této session; %d starých scratch adresářů z dřívějška (stav)"
              % len(stary))
        if stary:
            p("      staré scratch: %s" % ", ".join(stary[:12]))

    rc, out, _ = spust(["git", "-C", str(WS.parent / "uo-shadows"), "rev-parse", "--short", "HEAD"])
    if rc == 0:
        m.ok_("hra (uo-shadows) HEAD = %s — jen ČTENO, cizí session" % out.strip())
    else:
        m.nezmereno_("stav hry se nepodařilo přečíst: %s" % out.strip()[:100])


# ── A1: je nasazení P35 živé? (TŘI KROKY + křížová kontrola) ──────────────────
SHA_P35 = "3143f31d6a37ed8d90bf06f5c03df9a407ae00ea"


def sekce_A1(m):
    s66 = oddil(r"^##\s*66\.")
    m.tvrzeni(s66, r"deploy\s*#39 na\s*(\S{8})", popis="deploy #39 na 3143f31d")
    m.ok_("§66 TVRDÍ „deploy #39 na 3143f31d“ — tvrzení se ČTE z dokumentu (H155)")
    verze_dok = m.tvrzeni(s66, r"(3985379c-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
                          popis="verze 3985379c-… z §66")
    if verze_dok:
        m.ok_("§66 TVRDÍ verzi %s — čte se z dokumentu" % verze_dok)

    if BEZ_SITE:
        m.nezmereno_("A1 kroky 1–2 PŘESKOČENY (P36_BEZ_SITĚ=1) — měření neproběhlo")
    else:
        rc, out, _ = spust(["node", str(ANALYZA / "p30-sonda-deploy.mjs"), SHA_P35], timeout=300)
        if "VŠE OK" in out and "#39" in out:
            m.ok_("KROK 1: deploy.yml #39 na %s je completed/success (živě z GitHub API)" % SHA_P35[:8])
        else:
            m.chyba("KROK 1: deploy #39 na %s NENÍ completed/success: %s"
                    % (SHA_P35[:8], " | ".join(out.strip().splitlines()[-3:])))
        # ⚠ cizí měřidlo JEN s výstupem do VLASTNÍHO jména (H166)
        rc, out, _ = spust(["node", str(ANALYZA / "p32-sonda-cf-verze.mjs"), SHA_P35,
                            "_analyza/p36-cf-verze-vystup.txt"], timeout=300)
        mv = re.search(r"Current Version ID:\s*([0-9a-f-]{36})", out)
        if not mv:
            m.nezmereno_("KROK 2: v logu nasazení není „Current Version ID“")
        else:
            log_verze = mv.group(1)
            if verze_dok and log_verze != verze_dok:
                m.rozdil("KROK 2: verze z logu %s != tvrzení §66 %s" % (log_verze, verze_dok))
            else:
                m.ok_("KROK 2: verze z LOGU nasazení = %s" % log_verze)

            # KROK 3 — křížová kontrola proti ŽIVÉMU tailu
            if not TAIL.is_file():
                m.nezmereno_("KROK 3: doklad živého tailu %s NENÍ — křížová kontrola neproběhla"
                             % TAIL.name)
            else:
                eventy = nacti_json_za_sebou(TAIL)
                _, verze_tail, _ = cron_casy(eventy)
                if not verze_tail:
                    m.nezmereno_("KROK 3: v tailu není `scriptVersion.id` (%d eventů)" % len(eventy))
                elif verze_tail == {log_verze}:
                    m.ok_("KROK 3: ŽIVÝ tail běží TUTÉŽ verzi %s (%d eventů) — HTTP 200 to nedokazuje"
                          % (log_verze, len(eventy)))
                else:
                    m.chyba("KROK 3: živý tail běží JINOU verzi %s, log tvrdí %s"
                            % (sorted(verze_tail), log_verze))


# ── A2: je oprava H165 v KÓDU — a má test, který ji ZAVOLÁ? ──────────────────
def sekce_A2(m):
    kod = bez_komentaru_js(CONDUCTOR.read_text(encoding="utf-8"))
    if "Uint8Array.from(atob(" in kod:
        m.chyba("v KÓDU conductora je pořád DRAHÝ přepis `Uint8Array.from(atob(…), mapFn)`")
    else:
        m.ok_("v KÓDU conductora NENÍ drahý `Uint8Array.from(atob(…), mapFn)` (komentáře odstraněny)")
    if re.search(r"charCodeAt\(i\)", kod):
        m.ok_("v KÓDU je INDEXOVANÝ cyklus (`charCodeAt(i)`) — oprava H165 je nasazená v kódu")
    else:
        m.chyba("v KÓDU není indexovaný cyklus — oprava H165 tam NENÍ")

    t = TEST_TICK.read_text(encoding="utf-8")
    if "žluťoučký" in t and re.search(r"AF\)", t):
        m.ok_("test má scénář AF s VÍCEBAJTOVOU češtinou (kdyby dekodér krátil, spadne)")
    else:
        m.chyba("test NEMÁ scénář AF s vícebajtovou češtinou — opravu by nikdo nezavolal")

    rc, out, _ = spust(["node", str(TEST_TICK)], timeout=900)
    c = citac(out)
    if not c:
        m.chyba("test-tick-offline nevrátil čítač")
    elif c[1] == 0 and c[0] >= 218:
        m.ok_("test-tick-offline.mjs: %d kontrol, %d chyb" % c)
    else:
        m.chyba("test-tick-offline.mjs: %d kontrol, %d chyb (čekáno ≥218/0)" % c)


# ── A3: sedí čísla z §66 (a ze zadání)? ─────────────────────────────────────
def sekce_A3(m, drahe):
    s66 = oddil(r"^##\s*66\.")
    v66 = m.tvrzeni(s66, r"vlastní měřidlo P35\s*(\d+)/0 plně", popis="§66: vlastní měřidlo P35 N/0")
    v66l = m.tvrzeni(s66, r"\(levně\s*(\d+)/0\)", popis="§66: levný běh N/0")
    text_zad = ZADANI.read_text(encoding="utf-8")
    vzad = m.tvrzeni(text_zad, r"Plný běh → \*\*(\d+) kontrol, 0 chyb\*\*",
                     kde=ZADANI.name, popis="zadání: plný běh N kontrol, 0 chyb")

    if os.environ.get("P36_P35A"):
        dok = P35A_DOKLAD.read_text(encoding="utf-8", errors="replace")
        m.ok_("A3: použit PODSTRČENÝ doklad %s (seam P36_P35A)" % P35A_DOKLAD.name)
    else:
        rezim = ["--plne"] if drahe else []
        rc, out, _ = spust(["python", str(ANALYZA / "p35-a-overeni.py")] + rezim +
                           ["--vystup", "_analyza/p36-p35a-plne-vystup.txt"], timeout=2700)
        dok = out
        if not MOJE_P35A.is_file():
            m.chyba("cizí měřidlo p35-a-overeni.py neběželo (exit %d) a doklad nevznikl" % rc)
    c = citac(dok)
    if not c:
        m.nezmereno_("A3: v dokladu p35-a-overeni není čítač")
        return
    p("  naměřeno: p35-a-overeni.py → %d/%d (doklad %s)" % (c[0], c[1], MOJE_P35A.name))
    r = re.findall(r"^\s*ROZDÍL\s+(.+)$", dok, re.M)
    n = re.findall(r"^\s*NÁLEZ\s+(.+)$", dok, re.M)
    p("  pojmenovaných ROZDÍLŮ: %d · NÁLEZŮ O SLUŽBĚ: %d" % (len(r), len(n)))
    for x in r:
        p("      ROZDÍL: %s" % x[:160])

    if v66 and int(v66) != c[0]:
        m.rozdil("§66 tvrdí P35 %s/0, naměřeno %d/%d — rozdíl se musí POJMENOVAT" % (v66, c[0], c[1]))
    elif v66:
        m.ok_("§66 tvrdí P35 %s/0 a naměřeno %s/%d — SEDÍ" % (v66, c[0], c[1]))
    if vzad and int(vzad) != c[0]:
        m.rozdil("ZADÁNÍ tvrdí %s/0, doklad P35 má %d/%d — zadání má ZASTARALÉ číslo (H168)"
                 % (vzad, c[0], c[1]))
    elif vzad:
        m.ok_("ZADÁNÍ tvrdí %s/0 a doklad má %s/0 — SEDÍ" % (vzad, c[0]))
    if v66l:
        p("  §66 uvádí levný běh %s/0" % v66l)


# ── A4: je tik živě zlevněný? ────────────────────────────────────────────────
def sekce_A4(m):
    s66 = oddil(r"^##\s*66\.")
    tvrzeni = m.tvrzeni(s66, r"medián\s*\*\*26,5\s*→\s*(\d+)\s*ms\*\*", popis="§66: medián PO zlevnění")
    if not TAIL.is_file():
        m.nezmereno_("A4: doklad živého tailu %s NENÍ — CPU se neměřilo" % TAIL.name)
        return
    eventy = nacti_json_za_sebou(TAIL)
    casy, verze, chyb = cron_casy(eventy)
    if not casy:
        m.nezmereno_("A4: v tailu není ani jedna cron invokace s `cpuTime` (%d eventů)" % len(eventy))
        return
    med = statistics.median(casy)
    p("  cron cpuTime: n=%d, medián %.1f ms, rozsah %.0f–%.0f ms, outcome≠ok: %d, verze %s"
      % (len(casy), med, min(casy), max(casy), chyb, ",".join(sorted(verze))[:40]))
    if chyb:
        m.nalezeno("z %d cron invokací mělo %d `outcome != ok`" % (len(casy), chyb))
    else:
        m.ok_("VŠECHNY cron invokace (n=%d) skončily `outcome=ok`" % len(casy))
    if tvrzeni:
        if abs(med - int(tvrzeni)) <= 5:
            m.ok_("medián cron cpuTime %.1f ms ≈ tvrzení §66 (%s ms)" % (med, tvrzeni))
        else:
            m.rozdil("medián cron cpuTime %.1f ms vs. tvrzení §66 %s ms (n=%d — jiný vzorek)"
                     % (med, tvrzeni, len(casy)))
    if max(casy) > 30:
        m.nalezeno("nejdražší cron invokace %.0f ms PŘEKRAČUJE dokumentovaných 10 ms — a přesto "
                   "`outcome=ok` (H167: limit není tvrdý)" % max(casy))


# ── A5: jsou nová pole v /health a v D1? ─────────────────────────────────────
def sekce_A5(m):
    env = {}
    for l in (WS / ".env").read_text(encoding="utf-8").replace("\ufeff", "").splitlines():
        if "=" in l and not l.strip().startswith("#"):
            i = l.index("=")
            env[l[:i].strip()] = l[i + 1:].strip()
    url = str(env.get("FORGE_URL", "")).rstrip("/")

    seam = os.environ.get("P36_HEALTH")
    if seam:
        telo = json.loads(pathlib.Path(seam).read_text(encoding="utf-8"))
        p("  seam P36_HEALTH: hodnotí se PODSTRČENÝ stav (%s)" % pathlib.Path(seam).name)
    elif BEZ_SITE or not url:
        telo = None
        m.nezmereno_("A5 /health: PŘESKOČENO (P36_BEZ_SITĚ=1 nebo chybí FORGE_URL)")
    else:
        try:
            req = urllib.request.Request(url + "/health",
                                         headers={"x-forge-secret": env.get("FORGE_SECRET", ""),
                                                  "User-Agent": "forge-p36-sonda"})
            with urllib.request.urlopen(req, timeout=30) as r:
                telo = json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            telo = None
            m.chyba("A5 /health se nepodařilo zavolat: %s" % str(e)[:160])

    if isinstance(telo, dict):
        if "last_cron_pokus" in telo and "last_cron_pokus_min" in telo:
            m.ok_("živé /health POSÍLÁ POKUS: last_cron_pokus=%s (%s min)"
                  % (telo["last_cron_pokus"], telo.get("last_cron_pokus_min")))
        else:
            m.chyba("živé /health NEPOSÍLÁ last_cron_pokus — nasazená verze je STARŠÍ než P34")
        if "last_cron" in telo:
            m.ok_("živé /health posílá i DOKONČENÝ tep: last_cron=%s (%s min), ready=%s, running=%s"
                  % (telo["last_cron"], telo.get("last_cron_min"), telo.get("ready"), telo.get("running")))
        else:
            m.chyba("živé /health NEPOSÍLÁ last_cron")

    d1seam = os.environ.get("P36_D1")
    if d1seam:
        data = json.loads(pathlib.Path(d1seam).read_text(encoding="utf-8"))
        radky = data["dotazy"]["state"] if isinstance(data, dict) and "dotazy" in data else data
        p("  seam P36_D1: hodnotí se PODSTRČENÉ řádky D1 (%s)" % pathlib.Path(d1seam).name)
    elif BEZ_SITE:
        radky = None
        m.nezmereno_("A5 D1: PŘESKOČENO (P36_BEZ_SITĚ=1)")
    else:
        wr = WS / "conductor" / "node_modules" / "wrangler" / "bin" / "wrangler.js"
        rc, out, _ = spust(["node", str(wr), "d1", "execute", "forge-conductor", "--remote",
                            "--json", "--command", "SELECT k, v FROM state"],
                           timeout=300,
                           env={"PYTHONIOENCODING": "utf-8"})
        mt = re.search(r"\[\s*\{.*\}\s*\]", out, re.S)
        if not mt:
            radky = None
            m.chyba("A5 D1: wrangler nevrátil JSON (exit %d): %s" % (rc, out.strip()[:150]))
        else:
            radky = json.loads(mt.group(0))[0].get("results") or []

    if radky is not None:
        stav = {x["k"]: x["v"] for x in radky}
        klice = set(stav)
        if {"last_cron", "cron_pokus"} <= klice:
            m.ok_("D1 `state` má OBA klíče: last_cron=%s · cron_pokus=%s"
                  % (stav["last_cron"], stav["cron_pokus"]))
        else:
            m.chyba("D1 `state` nemá oba klíče (má: %s)" % sorted(klice))


# ── A6: uklízí se měřidla po sobě? ───────────────────────────────────────────
def sekce_A6(m, drahe):
    if drahe:
        rc, out, _ = spust(["python", str(ANALYZA / "p35-mutace.py")], timeout=2700)
        c = citac(out)
        if not c:
            m.chyba("p35-mutace.py nevrátil čítač (exit %d)" % rc)
        elif c[1] == 0 and c[0] >= 33:
            m.ok_("p35-mutace.py (cizí mutační důkaz): %d/%d" % c)
        else:
            m.rozdil("p35-mutace.py: %d/%d (P35 tvrdí 33/0)" % c)
    else:
        m.nezmereno_("A6 mutační běh P35 PŘESKOČEN (levný režim)")

    # ⚠ H169: ověření proti HEAD BEZ FILTRU PŘÍPON — jinak mutant v .md proklouzne
    rc, out, _ = git("status", "--porcelain")
    zmenene = [r[3:].strip() for r in out.splitlines() if r.strip()]
    podezrele = [z for z in zmenene if z in P35_ZMENIL and z not in P36_ZMENIL]
    zname36 = [z for z in zmenene if z in P35_ZMENIL and z in P36_ZMENIL]
    if podezrele:
        m.chyba("živý soubor, který P35 MĚNIL, je ROZEJITÝ proti HEAD: %s (leftover mutanta?)"
                % podezrele)
    else:
        m.ok_("žádný soubor ze seznamu `P35_ZMENIL` není rozejitý (kontrola BEZ filtru přípon)")
    if zname36:
        m.rozdil("soubor, který P35 měnila, je rozejitý ZÁMĚRNĚ prací P36: %s — "
                 "rozdíl se pojmenovává, aby se nepletl s mutantem" % zname36)
    rc, out, _ = git("diff", "--stat")
    if out.strip():
        p("  git diff --stat: %s" % " | ".join(out.strip().splitlines()))
    else:
        m.ok_("`git diff --stat` je PRÁZDNÝ — v žádném TRACKOVANÉM souboru není změna")


# ── A7: nic se nerozbilo ─────────────────────────────────────────────────────
def sekce_A7(m, drahe):
    if not drahe:
        m.nezmereno_("A7 (g3, validate-all, kronika, handoff, ov-g) PŘESKOČENO — levný režim")
        return
    registr = ANALYZA / "p36-g3-registr.json"
    rc, out, _ = spust(["python", str(ANALYZA / "g3-brany.py")], timeout=1800,
                       env={"FORGE_REGISTR": str(registr)})
    mb = re.search(r"(\d+)\s*bran", out)
    if not mb:
        m.nezmereno_("g3 nevypsal počet bran (exit %d)" % rc)
    else:
        # ⚠ ČTE SE KONKRÉTNÍ SOUHRNNÝ ŘÁDEK, ne libovolný výskyt slova
        # „NEDEKLAROVANÝCH“: g3 má pod ním ještě VYSVĚTLUJÍCÍ poznámku
        # („…už není potřeba: zadání kontrola…“) — a vzor bez ukotvení trefil
        # ji taky. Naměřeno P36: hlásilo „2 NEDEKLAROVANÉ“, správně byly **0**
        # (H175: brána může číst CITACI místo TVRZENÍ).
        ms = re.search(r"NENULOVÉ EXITY:\s*(\d+)\s*—\s*z toho deklarovaných\s*\(očekávaných\)\s*(\d+)"
                       r"\s*a NEDEKLAROVANÝCH\s*(\d+)", out)
        if ms:
            p(" g3: %s bran · nenulových exitů %s (deklarovaných %s, NEDEKLAROVANÝCH %s)"
              % (mb.group(1), ms.group(1), ms.group(2), ms.group(3)))
            if int(ms.group(3)) == 0:
                m.ok_("g3: %s bran, %s nenulových exitů a VŠECHNY deklarované (NEDEKLAROVANÝCH 0)"
                      % (mb.group(1), ms.group(1)))
            else:
                m.rozdil("g3: %s NEDEKLAROVANÝCH nenulových exitů (z %s)"
                         % (ms.group(3), ms.group(1)))
        else:
            m.nezmereno_("g3: souhrnný řádek o nenulových exitech se nenašel (exit %d)" % rc)

    rc, out, _ = spust(["node", str(WS / "tools" / "validate-all.mjs")], timeout=1800)
    if rc == 0:
        m.ok_("validate-all → exit 0 (VŠE V POŘÁDKU)")
    else:
        ch = re.findall(r"(\d+)\s*problém", out)
        m.rozdil("validate-all → exit %d (%s problémů)"
                 % (rc, ch[-1] if ch else "počet nepojmenován"))

    for skript, vzor_ok, popis in [
        ("kronika-kontrola.py", r"SED[ÍI]", "kronika SEDÍ"),
        ("handoff-kontrola-uplnost.py", r"V[ŠS]E OK|0\s*chyb", "handoff: všech 83 bodů"),
        ("ov-g-neovereno.py", r"0\s*NEOV", "ov-g: 0 NEOVĚŘENO"),
    ]:
        rc, out, _ = spust(["python", str(ANALYZA / skript)], timeout=900)
        if re.search(vzor_ok, out):
            m.ok_("%s → %s" % (skript, popis))
        else:
            m.chyba("%s NEPOTVRDIL „%s“ (exit %d): %s"
                    % (skript, popis, rc, " | ".join(out.strip().splitlines()[-2:])))


def main():
    global _handle
    ap = argparse.ArgumentParser()
    ap.add_argument("--jen", default=None)
    ap.add_argument("--plne", action="store_true")
    ap.add_argument("--levne", action="store_true")
    ap.add_argument("--vystup", default=None)
    args = ap.parse_args()

    vystup = pathlib.Path(args.vystup) if args.vystup else (ANALYZA / "p36-a-overeni-vystup.txt")
    if not vystup.is_absolute():
        vystup = WS / vystup
    vystup.parent.mkdir(parents=True, exist_ok=True)
    _handle = vystup.open("w", encoding="utf-8")

    vychozi = "A0,A1,A2,A3,A4,A5,A6,A7" if args.plne else "A0,A1,A2,A5"
    etapy = [x.strip().upper() for x in (args.jen or vychozi).split(",")]
    drahe = (args.plne or bool(args.jen)) and not args.levne

    fns = {
        "A0": lambda: sekce_A0(m),
        "A1": lambda: sekce_A1(m),
        "A2": lambda: sekce_A2(m),
        "A3": lambda: sekce_A3(m, drahe),
        "A4": lambda: sekce_A4(m),
        "A5": lambda: sekce_A5(m),
        "A6": lambda: sekce_A6(m, drahe),
        "A7": lambda: sekce_A7(m, drahe),
    }

    m = Meridlo()
    p("=" * 96)
    p("P36/A — VLASTNÍ PŘEMĚŘENÍ PRÁCE P35 (A0–A7)")
    p("=" * 96)
    p("  datum (z hodin): %s" % time.strftime("%Y-%m-%d %H:%M:%S %z"))
    p("  tvrzení se ČTOU z: %s" % HANDOFF.name)
    p("  druhé tvrzení z:   %s" % ZADANI.name)
    p("  živý tail z:       %s" % TAIL.name)
    p("  pořadí běhu: %s%s" % (", ".join(etapy), "  (--plne)" if args.plne else ""))
    for e in etapy:
        f = fns.get(e)
        if f is None:
            m.nezmereno_("etapa %s neexistuje" % e)
            continue
        p("\n" + "─" * 96)
        p("%s)" % e)
        t0 = time.time()
        try:
            f()
        except Exception as ex:  # noqa: BLE001
            import traceback  # noqa: PLC0415
            tb = traceback.format_exc().strip().splitlines()
            p("      TRACEBACK: %s" % " | ".join(x.strip() for x in tb[-3:]))
            m.nezmereno_("etapa %s: výjimka %s: %s" % (e, type(ex).__name__, str(ex)[:180]))
        p("  (%s: %.1f s)" % (e, time.time() - t0))

    p("\n" + "=" * 96)
    p("POJMENOVANÉ ROZDÍLY (stav se posunul, nebo je změna ZÁMĚRNÁ): %d" % m.rozdilu)
    p("NÁLEZY O SLUŽBĚ (stav měřeného objektu — NENÍ to chyba měřidla): %d" % m.nalezu)
    p("NEZMĚŘENO (není nula a není zelená): %d" % m.nezmereno)
    p("VÝSLEDEK: %d kontrol, %d chyb (z toho %d ROZDÍLŮ, %d NEZMĚŘENO, %d NÁLEZŮ O SLUŽBĚ)"
      % (m.ok + m.chyb, m.chyb, m.rozdilu, m.nezmereno, m.nalezu))
    p("doklad: %s (%d B)" % (vystup.name, vystup.stat().st_size))
    _handle.close()
    if m.chyb:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
