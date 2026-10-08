# -*- coding: utf-8 -*-
r"""P25 — ÚKOL A: PŘEMĚŘIT PRÁCI P24 VLASTNÍM POSTUPEM (A1–A6).

PROČ TENHLE SKRIPT EXISTUJE
---------------------------
Zadání P25 §2.1: záznamy P24 (`HANDOFF.md` §54, kronika řádek 39 + §2.17) psal
**autor, který si je sám ověřoval** — a `AGENTS.md` je v tom jednoznačné:
*„autor není nezávislý reviewer"*. P24 to udělala pro P23; P25 to musí udělat
pro P24. Skript proto **neopisuje** tvrzení z §54 — každý bod měří **jiným
postupem, než jak vznikl**:

  A1  spustí měřidlo P24 (a jeho mutační důkaz), pak **vloží vadu do KOPIE
      tvrzení** a vyžaduje, aby měřidlo spadlo; a **sabotuje samo měřidlo**,
      aby se ukázalo, že i `p24-b-mutace.py` umí ohlásit NÁLEZ (ne OK)
  A2  trvalost značky `roadmap.eskalovano` se čte z **KÓDU** (SQL literály po
      odstranění komentářů) — a predikát se **zmutuje v kopii**, aby se
      ukázalo, že vadu „někdo značku maže" opravdu vidí
  A3  do ŽIVÉHO `conductor/src/index.ts` se vloží **zarážka** (v `try/finally`
      a s ověřením hashe) a měří se, **KTERÉ kontroly testu tiku se zapnou**;
      druhá zarážka je uvnitř handleru (pojistka `cleanup`)
  A4  čísla tvrzená v §54 se **znovu naměří spuštěním** (ne čtením §54)
  A5  historie KRONIKY: `kronika-kontrola` + **smazané řádky session** (i
      v necommitnutém stromě)
  A6  sondy `p24-sonda-*` nejsou brány (ani v `g3`, ani ve `validate-all`)
      a doklady, které měřit mají, v dávce `p20-d` **jsou** — včetně
      negativní kontroly predikátu na syntetické fixtuře

⚠ CO SE NESMÍ ZAMĚNIT: „spadlo" u A1/A2/A3 znamená **chytilo vadu**; když
měřidlo spadne z JINÉHO důvodu (např. přesunutý stav hry), je to **nález
o stavu**, ne důkaz o měřidle. A1b proto každou červenou kontrolu P24
**zařadí** — nepovolená je jakákoli, kterou změna stavu nevysvětluje.

Použití:
    python _analyza/p25-a-overeni.py                 # DÁVKOVÝ režim: A2, A5, A6
    python _analyza/p25-a-overeni.py --plne          # PLNÁ kontrola A1–A6
    python _analyza/p25-a-overeni.py --jen A2,A6     # jen vybrané etapy
    python _analyza/p25-a-overeni.py --plne --bez-a1plne   # bez dlouhého běhu P24
"""

import argparse
import ast
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
GIT = WS / "tools" / "git.cmd"
SRC = WS / "conductor" / "src" / "index.ts"
TEST_TIK = WS / "tools" / "test-tick-offline.mjs"
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
G3 = ANALYZA / "g3-brany.py"
VALIDATE = WS / "tools" / "validate-all.mjs"
P20_D = ANALYZA / "p20-d-doklady.py"
P24_A = ANALYZA / "p24-a-overeni.py"
P24_B = ANALYZA / "p24-b-mutace.py"
SCRATCH = ANALYZA / "p25-scratch"

# Kotva, na které P24 měřila (§54.4) — a kterou dnešní stav už přesáhl.
KOTVA_P24 = "4925f64"
# Stav hry, který P24 naměřila (A8). Dnešní stav se měří zvlášť.
HRA_P24 = "44dd454"
HRA = pathlib.Path(os.environ.get("FORGE_HRA") or (WS.parent / "uo-shadows"))

sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj                                            # noqa: E402

kontrol = 0
chyb = 0
nezmereno = []


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
    """TŘETÍ STAV (`overovani` §7.13): „neměřeno" není nula a není zelená."""
    nezmereno.append(popis)
    print("  NEZMĚŘENO  %s\n          důvod: %s" % (popis, duvod))


def cmd(argumenty, cwd=None, timeout=1800):
    r = subprocess.run(argumenty, cwd=str(cwd or WS), capture_output=True,
                       timeout=timeout)
    return r.returncode, (r.stdout.decode("utf-8", "replace")
                          + r.stderr.decode("utf-8", "replace"))


def git(*argumenty, repo=None, timeout=120):
    """Git přes `tools/git.cmd` (`^` ŽERE cmd.exe → nikdy nepoužívej `sha^`)."""
    prikaz = [str(GIT), "-C", str(repo or WS)] + list(argumenty)
    r = subprocess.run(prikaz, capture_output=True, shell=True, timeout=timeout)
    return r.returncode, (r.stdout.decode("utf-8", "replace")
                          + r.stderr.decode("utf-8", "replace")).strip()


def blob(rev, cesta):
    r = subprocess.run([str(GIT), "-C", str(WS), "show", "%s:%s" % (rev, cesta)],
                       capture_output=True, shell=True, timeout=120)
    return r.stdout if r.returncode == 0 else None


def citac(vystup, vzor=r"(\d+) kontrol, (\d+) chyb"):
    """Poslední výskyt čítače v textu (mutace tiskne `CHYB` velkými)."""
    m = None
    for m in re.finditer(vzor, vystup, re.IGNORECASE):
        pass
    return (int(m.group(1)), int(m.group(2))) if m else None


def chyby_z_vystupu(vystup):
    """Popisy červených kontrol (`  CHYBA <popis>`)."""
    return [l.strip()[len("CHYBA"):].strip() for l in vystup.splitlines()
            if l.strip().startswith("CHYBA")]


def bez_komentaru(s):
    """Odstraní `//` a `/* */` MIMO řetězcové literály (past `overovani` §1)."""
    out, i, n, stav = [], 0, len(s), None
    while i < n:
        c = s[i]
        if stav:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(s[i + 1])
                i += 2
                continue
            if c == stav:
                stav = None
            i += 1
            continue
        if c in "'\"`":
            stav = c
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and s[i + 1] == "/":
            j = s.find("\n", i)
            i = n if j < 0 else j
            continue
        if c == "/" and i + 1 < n and s[i + 1] == "*":
            j = s.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


# ═══════════════════════════════════════════════════════════════════ A1 ═══
def a1_zavady_a_jeho_dukaz():
    print("\n--- A1: měří měřidlo P24 opravdu to, co tvrdí? ---")
    if not P24_A.is_file():
        check("A1 měřidlo P24 existuje (%s)" % P24_A.name, False, True)
        return None
    kontrola = []
    kopie = {}
    for nazev in ("PLAN-ORCHESTRA-AI-AGENTI.md", "PLAN-ROZVOJ-ORCHESTRA.md"):
        cil = SCRATCH / nazev
        shutil.copyfile(WS / nazev, cil)
        kopie[nazev] = cil
    agr = ["--plan-agenti", str(kopie["PLAN-ORCHESTRA-AI-AGENTI.md"]),
           "--plan-rozvoj", str(kopie["PLAN-ROZVOJ-ORCHESTRA.md"])]

    # (a) KONTROLA: nemutované kopie musejí projít — jinak by „spadlo po mutaci"
    #     mohlo znamenat jen to, že je měřidlo rozbité pořád.
    kod, v = cmd(["python", str(P24_A), "--jen-dokumenty"] + agr)
    c = citac(v)
    check("A1a kontrola: měřidlo P24 na nemutovaných kopiích → exit 0", kod, 0)
    # `--jen-dokumenty` měří JEN tvar dokumentů (8 kontrol) — práh proto 8, ne 20.
    check("A1a kontrola: čítač měřidla P24 (v režimu --jen-dokumenty aspoň 8)",
          (c[0] >= 8) if c else False, True)

    # (b) VADA do KOPIE tvrzení: uber řádek `| **B4** |` z plánu rozvoje
    try:
        with mutuj(kopie["PLAN-ROZVOJ-ORCHESTRA.md"], "| **B4** |", "") as m:
            kod, v = cmd(["python", str(P24_A), "--jen-dokumenty"] + agr)
        check("A1b mutace proběhla (hash před != po)",
              m.hash_pred != m.hash_po_mutaci, True)
        check("A1b po UBRÁNÍ řádku B4 měřidlo SPADLO", kod != 0, True)
        check("A1b a důvod je TVRZENÍ O CHYBĚJÍCÍM ŘÁDKU B4",
              any("B4" in l for l in chyby_z_vystupu(v)), True)
    except ValueError as e:
        check("A1b mutace se provedla (%s)" % e, False, True)
    check("A1b kopie je vrácena bajt na bajt",
          hashlib.sha256(kopie["PLAN-ROZVOJ-ORCHESTRA.md"].read_bytes()).hexdigest(),
          hashlib.sha256((WS / "PLAN-ROZVOJ-ORCHESTRA.md").read_bytes()).hexdigest())

    # (c) MŮŽE SÁM MUTAČNÍ DŮKAZ OHLÁSIT NÁLEZ? Sabotuje se MĚŘIDLO (kopie bez
    #     kontroly B4) a spustí se KOPIE `p24-b-mutace.py` proti ní. Kdyby
    #     p24-b umělo jen „vždy OK", jeho 17/0 by nic nedokazovalo.
    oslabene = SCRATCH / "p24-a-oslabene.py"
    sabotaz_b = SCRATCH / "p24-b-sabotaz.py"
    text = P24_A.read_text(encoding="utf-8")
    if '        for b in ("B1", "B2", "B3", "B4", "B5"):' not in text:
        nezmereno_zapis("A1c sabotáž měřidla",
                        "v p24-a-overeni.py není očekávaný řádek s pěti fázemi B")
    else:
        oslabeny = text.replace(
            '        for b in ("B1", "B2", "B3", "B4", "B5"):',
            '        for b in ("B1", "B2", "B3", "B5"):', 1)
        oslabeny = oslabeny.replace(
            'WS = pathlib.Path(__file__).resolve().parents[1]',
            'WS = pathlib.Path(r"%s")' % WS, 1)
        oslabene.write_text(oslabeny, encoding="utf-8", newline="")
        text_b = P24_B.read_text(encoding="utf-8")
        text_b = text_b.replace(
            'WS = pathlib.Path(__file__).resolve().parents[1]',
            'WS = pathlib.Path(r"%s")' % WS, 1)
        # ⚠ KOTVA JE `ANALYZA` (s Y), NE `ANALIZA`: naměřeno 7. 10. 2026, že
        # záměna Y/I tady vypadá jako TICHÁ sabotáž — `replace()` nic nenahradí
        # a test pak hlásí „důkaz prošel" nad NEZMĚNĚNÝM skriptem (`overovani`
        # §7.9). Proto se po patchi POVINNĚ ověřuje, že cesta v kopii JE.
        text_b = text_b.replace(
            'MERIDLO = ANALYZA / "p24-a-overeni.py"',
            'MERIDLO = pathlib.Path(r"%s")' % oslabene, 1)
        text_b = text_b.replace(
            'SCRATCH = ANALYZA / "p24-scratch"',
            'SCRATCH = ANALYZA / "p25-scratch" / "b-scratch"', 1)
        sabotaz_b.write_text(text_b, encoding="utf-8", newline="")
        check("A1c sabotovaný běžec míří na OSLABENÉ měřidlo (patch se provedl)",
              str(oslabene) in text_b, True)
        if str(oslabene) not in text_b:
            print("      → sabotáž se NEPROVEDLA; čítač níž nic nedokazuje")
        kod, v = cmd(["python", str(sabotaz_b)])
        cb = citac(v)
        check("A1c sabotované měřidlo se opravdu uložilo (B4 kontrola pryč)",
              '("B1", "B2", "B3", "B4", "B5")' not in oslabene.read_text(encoding="utf-8"),
              True)
        check("A1c p24-b-mutace.py NAD oslabeným měřidlem SPADLO", kod != 0, True)
        check("A1c a ohlásilo to jako NÁLEZ (ne OK)",
              (cb is not None and cb[1] > 0), True)
        print("      čítač sabotovaného důkazu: %s" % (cb,))

    # (d) KONTROLA POKRYTÍ CELÉHO MĚŘIDLA: plný běh P24 (jen když se nešetří čas)
    return c


def a1_plny_beh(preskocit=False):
    print("\n--- A1d: plný běh měřidla P24 (stavové kontroly se zařazují) ---")
    if preskocit:
        nezmereno_zapis("A1d plný běh p24-a-overeni.py", "--bez-a1plne")
        return None
    kod, v = cmd(["python", str(P24_A)], timeout=3600)
    c = citac(v)
    print("      exit=%d, čítač=%s" % (kod, c))
    cervene = chyby_z_vystupu(v)
    for l in cervene:
        print("        · %s" % l[:110])
    # KAŽDÁ červená musí být vysvětlitelná ZMĚNOU STAVU, ne vadou měřidla.
    # Jediná povolená dnešní změna: hra má jiný HEAD než P24 (A8) — měřeno živě.
    _, hhra = git("rev-parse", "--short", "HEAD", repo=HRA)
    hra_jina = hhra.strip() != HRA_P24
    povolene = [l for l in cervene if l.startswith("A8")]
    nepovolene = [l for l in cervene if not l.startswith("A8")]
    check("A1d hra má dnes JINÝ HEAD než P24 (a to je změna STAVU)",
          hra_jina, True)
    check("A1d všechny červené P24 jdou na vrub změně stavu hry (A8)",
          nepovolene, [])
    if cervene:
        print("      (P24 měřila 99/0 na %s; teď je stav jiný — viz A4)"
              % KOTVA_P24)
    return c


# ═══════════════════════════════════════════════════════════════════ A2 ═══
def a2_zavady(zdroj):
    """Vady v SQL kolem `roadmap.eskalovano`. Prázdný seznam = značka je TRVALÁ.

    PROČ TAKHLE: ptáme se na **zápis**, ne na přítomnost slova. Kdyby někde
    stálo `eskalovano = NULL` (nebo `= ''`), značka by se mazala a kontrola
    „ohlásil něco" by přestala být nastražená.
    """
    v = []
    src = bez_komentaru(zdroj)
    if "ALTER TABLE roadmap ADD COLUMN eskalovano TEXT" not in src:
        v.append("chybí samomigrace `ALTER TABLE roadmap ADD COLUMN eskalovano TEXT`")
    # ⚠ SQL ŽIJE VE VÍCEŘÁDKOVÝCH TEMPLATE LITERÁLECH — jednoduchý vzor bez
    # `\n` kandidátský SELECT VŮBEC NENAŠEL (naměřeno 7. 10. 2026: predikát
    # hlásil „nesklasifikovaný literál" a „nikde není výběr kandidátů" nad
    # SPRÁVNÝM zdrojem = falešný poplach). Berou se proto CELÉ literály.
    literaly = [x for x in (re.findall(r"`([^`]*)`", src, re.S)
                            + re.findall(r'"([^"\n]*)"', src)
                            + re.findall(r"'([^'\n]*)'", src)) if "eskalovano" in x]
    if not literaly:
        v.append("žádný SQL literál se sloupcem `eskalovano`")
    # ⚠ KLASIFIKUJÍ SE JEN SQL LITERÁLY. Sloupec `eskalovano` se v kódu
    # objevuje i v tom, co SQL NENÍ — v hlášce tiku (`, watchdog: ${eskalovano}`)
    # a v log-prefixu (`roadmap.eskalovano: `). Kdo by je počítal jako
    # „nesklasifikovaný zápis", vyrobí falešný poplach nad správným zdrojem
    # (`overovani` §10.1 — naměřeno 7. 10. 2026).
    sql_literaly, mimo_sql = [], 0
    for lit in literaly:
        low = " ".join(lit.split()).lower()
        if re.search(r"\b(select|insert|update|delete|alter)\b", low):
            sql_literaly.append(lit)
        else:
            mimo_sql += 1
    zapisy, cteni, mazani, jine = 0, 0, 0, 0
    for lit in sql_literaly:
        low = " ".join(lit.split()).lower()
        if low.startswith("alter table"):
            continue
        if "set eskalovano" in low:
            if re.search(r"set\s+eskalovano\s*=\s*datetime", low):
                zapisy += 1
            elif re.search(r"set\s+eskalovano\s*=\s*(null|''|0|\?)", low):
                mazani += 1
            else:
                jine += 1
            continue
        if "eskalovano" in low and (" is null" in low or "where" in low
                                    or "select" in low):
            cteni += 1
            continue
        jine += 1
    print("      literálů se `eskalovano`: %d (z toho mimo SQL: %d)"
          % (len(literaly), mimo_sql))
    if zapisy != 1:
        v.append("zápis značky (`SET eskalovano = datetime`) není právě 1× (%d)" % zapisy)
    if cteni < 1:
        v.append("žádný výběr kandidátů nefiltruje `eskalovano IS NULL` (%d)" % cteni)
    if mazani:
        v.append("NĚKDE SE ZNAČKA MAŽE (%d×) — kontrola 'N>0' by nebyla "
                 "nastražená" % mazani)
    if jine:
        v.append("nesklasifikovaný literál se `eskalovano` (%d×)" % jine)
    # Filtr kandidátů musí být ve stejném literálu jako `status <> 'done'`.
    kandidati = [l for l in literaly if "status <> 'done'" in l]
    if not kandidati:
        v.append("nikde není výběr kandidátů (`status <> 'done'`) se značkou")
    elif not any("eskalovano is null" in " ".join(l.split()).lower()
                 for l in kandidati):
        v.append("výběr kandidátů značku `eskalovano` nefiltruje")
    return v


def a2():
    print("\n--- A2: je `N > 0` u watchdogu NASTRAŽENÁ otázka? (vlastní čtení SQL) ---")
    if not SRC.is_file():
        nezmereno_zapis("A2 zdroj conductora", "%s neexistuje" % SRC)
        return
    zdroj = SRC.read_text(encoding="utf-8", errors="replace")
    zavady = a2_zavady(zdroj)
    check("A2 značka `eskalovano` je TRVALÁ (žádný SQL ji nemaže; naměřeno %d vad)"
          % len(zavady), zavady, [])
    # NEGATIVNÍ KONTROLA PREDIKÁTU: kdyby predikát nic neviděl, byl by zelený
    # i nad zdrojem, který značku maže (`overovani` §7.13).
    zmutovany = zdroj.replace(
        'if (path === "/heartbeat" && request.method === "POST") {',
        'await env.DB.prepare("UPDATE roadmap SET eskalovano = NULL WHERE item_id = ?").run();\n'
        '    if (path === "/heartbeat" && request.method === "POST") {', 1)
    check("A2 negativní kontrola: po vložení mazacího UPDATE predikát VADU VIDÍ",
          len(a2_zavady(zmutovany)) > len(zavady), True)
    # DRUHÁ CESTA: prah a strop ze ZDROJE (ne z dokumentu).
    mp = re.search(r'ESCALATE_AFTER[^0-9]{0,40}"(\d+)"', zdroj)
    ms = re.search(r'MAX_ATTEMPTS[^0-9]{0,40}"?(\d+)"?', zdroj)
    prah = int(mp.group(1)) if mp else None
    strop = int(ms.group(1)) if ms else None
    check("A2 prah watchdogu je POD stropem (mělká vada B3a)",
          (prah is not None and strop is not None and prah < strop), True)
    # TŘETÍ CESTA: živá služba. Zdravá služba MUSÍ hlásit 0 — jinak by kontrola
    # `N > 0` shodila SPRÁVNÝ stav (to je celý smysl nálezu P24-F).
    env = {}
    for radek in (WS / ".env").read_text(encoding="utf-8-sig").splitlines():
        radek = radek.strip()
        if radek and not radek.startswith("#") and "=" in radek:
            k, v = radek.split("=", 1)
            env[k.strip()] = v.strip()
    url = env.get("FORGE_URL", "").rstrip("/")
    if not url:
        nezmereno_zapis("A2 živé /tick", "v .env není FORGE_URL")
        return
    HL = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) forge-p25",
          "x-forge-secret": env.get("FORGE_SECRET", "")}
    try:
        req = urllib.request.Request(url + "/tick", method="POST", headers=HL)
        with urllib.request.urlopen(req, timeout=180) as r:
            telo = json.loads(r.read().decode("utf-8"))
        zprava = str(telo.get("message", ""))
        m = re.search(r"watchdog:\s*(\d+)\s*ohlášeno\s*\(prah\s*(\d+)\)", zprava)
        check("A2 živé /tick řeklo větu watchdogu", bool(m), True)
        if m:
            ohl, pzivy = int(m.group(1)), int(m.group(2))
            print("      živě: %d ohlášeno (prah %d; zdroj %s; strop %s)"
                  % (ohl, pzivy, prah, strop))
            check("A2 živá služba hlásí 0 (značka je trvalá) — kontrola `N>0` "
                  "by ji SHODILA", ohl, 0)
            check("A2 prah z /tick = prah ve ZDROJI", pzivy, prah)
    except Exception as e:                                        # noqa: BLE001
        nezmereno_zapis("A2 živé /tick", "%s: %s" % (type(e).__name__, e))


# ═══════════════════════════════════════════════════════════════════ A3 ═══
def popisy_checku():
    src = TEST_TIK.read_text(encoding="utf-8", errors="replace")
    return re.findall(r"check\(\s*'([^']*)'", src) + \
        re.findall(r'check\(\s*"([^"]*)"', src)


def a3_verdikt(reds, ocekavane_red, kontrolni_ne_red):
    """Rozhodnutí A3: zapnula zarážka PRÁVĚ ty kontroly, které má?

    Je to SAMOSTATNÁ funkce schválně — doklad `p25-b-mutace.py` ji ZAVOLÁ nad
    syntetickým výstupem, aby se ukázalo, že umí vrátit NÁLEZ (ne jen OK).
    """
    chybejici = [d for d in ocekavane_red if d not in reds]
    kontrolni_red = [d for d in kontrolni_ne_red if d in reds]
    return chybejici, kontrolni_red


def a3_jeden_stop(popis, kotva, nahrada, ocekavane_red, kontrolni_ne_red):
    """Vloží zarážku do ŽIVÉHO zdroje, spustí test, vrátí (výstup, ok)."""
    puvodni = SRC.read_bytes()
    text = puvodni.decode("utf-8")
    if text.count(kotva) != 1:
        check("A3 %s: kotva je ve zdroji PRÁVĚ 1× (naměřeno %d)"
              % (popis, text.count(kotva)), text.count(kotva), 1)
        return None
    try:
        SRC.write_bytes(text.replace(kotva, nahrada, 1).encode("utf-8"))
        kod, v = cmd(["node", "tools/test-tick-offline.mjs"], timeout=1800)
    finally:
        SRC.write_bytes(puvodni)
        assert SRC.read_bytes() == puvodni, "zdroj nebyl vrácen!"
    # Návrat se ověřuje TŘEMI pohledy (blob, index, disk) — ne okem.
    _, h_disk = git("hash-object", "conductor/src/index.ts")
    _, h_head = git("rev-parse", "HEAD:conductor/src/index.ts")
    check("A3 %s: zdroj je po zarážce zpět (disk == HEAD)" % popis,
          [h_disk, git("diff", "--quiet", "--", "conductor/src/index.ts")[0]],
          [h_head, 0])
    reds = chyby_z_vystupu(v)
    print("      %s: test tiku měl %s kontrol, z toho %d ČERVENÝCH"
          % (popis, citac(v), len(reds)))
    for l in reds:
        print("        · %s" % l[:110])
    chybejici, kontrolni_red = a3_verdikt(reds, ocekavane_red, kontrolni_ne_red)
    check("A3 %s: zarážka ZAPLA kontroly endpointů (%d)" % (popis, len(ocekavane_red)),
          chybejici, [])
    check("A3 %s: kontrolní kontrola zůstala ZELENÁ (test nespadl naslepo)" % popis,
          kontrolni_red, [])
    return v, kod


def a3():
    print("\n--- A3: VOLÁ test tiku ty endpointy doopravdy? ---")
    if not (SRC.is_file() and TEST_TIK.is_file()):
        nezmereno_zapis("A3 zarážka v handleru", "chybí zdroj nebo test tiku")
        return
    _, h_disk = git("hash-object", "conductor/src/index.ts")
    _, h_head = git("rev-parse", "HEAD:conductor/src/index.ts")
    check("A3 PŘED zarážkou je zdroj čistý (disk == HEAD)", h_disk, h_head)
    if h_disk != h_head:
        print("      → nemutuje se; naprav strom")
        return
    desk = popisy_checku()

    def podle(prefix, obsah):
        k = [d for d in desk if d.startswith(prefix) and obsah in d]
        return k[0] if k else None

    pet = [podle(p, "200") for p in ("N: ", "O: ", "P: ", "Q: ", "R: ")]
    check("A3 popisy pěti endpointových kontrol jdou PŘEČÍST z testu",
          [d for d in pet if d is None], [])
    if all(pet):
        kotva = '    const path = url.pathname.replace(/\\/+$/, "") || "/";'
        zarazka = (kotva + "\n"
                   '    if (["/poll", "/claim", "/heartbeat", "/tasks/cleanup", "/roadmap/reset"]\n'
                   '        .includes(path) && request.method === "POST") '
                   'return json({ error: "ZARAZKA" }, 599);')
        a3_jeden_stop("zarážka v routeru (5 endpointů)", kotva, zarazka,
                      pet, [podle("A: ", "200")])
    # Druhá zarážka je UVNITŘ handleru: mění se SMYSL pojistky, ne návrat 503.
    kotva2 = 'return json({ error: "roadmapa se nedá načíst, radši nemažu", hry: hryBezSouboru }, 503);'
    nahrada2 = 'return json({ error: "nemažu", hry: hryBezSouboru }, 503);'
    proc = [d for d in desk if d.startswith("Q2: ") and "PROČ" in d]
    stav503 = [d for d in desk if d.startswith("Q2: ") and "503" in d]
    if proc:
        a3_jeden_stop("zarážka uvnitř handleru /tasks/cleanup", kotva2, nahrada2,
                      proc, stav503)


# ═══════════════════════════════════════════════════════════════════ A4 ═══
def sekce_54():
    t = HANDOFF.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\n## 54\.", t)
    if not m:
        return ""
    zbytek = t[m.start():]
    m2 = re.search(r"\n## 5[5-9]\.", zbytek)
    return zbytek[:m2.start()] if m2 else zbytek


def a4(pocitadlo_p24):
    print("\n--- A4: čísla tvrzená v §54 se znovu NAMĚŘÍ (ne přečtou) ---")
    s54 = sekce_54()
    check("A4 §54 existuje (délka %d znaků)" % len(s54), len(s54) > 2000, True)
    tvrzeni = ["99/0", "17/0", "100/0", "31/0", "48 bran"]
    chybejici = [x for x in tvrzeni if x not in s54]
    check("A4 §54 tvrdí všech 5 čítačů %s" % tvrzeni, chybejici, [])
    dokumenty = {p.name: p.read_text(encoding="utf-8", errors="replace")
                 for p in (HANDOFF, WS / "AGENTS.md") if p.is_file()}

    # (1) měřidlo P24 — čítač z plného běhu (A1d). Když A1 neběžela, pouští se
    #     PLNÝ běh i tady: srovnávat §54 („99/0") s čítačem režimu
    #     `--jen-dokumenty` (8 kontrol) by byl nesmysl — dva různé čítače.
    if pocitadlo_p24 is None:
        kod, v = cmd(["python", str(P24_A)], timeout=3600)
        pocitadlo_p24 = citac(v)
        print("      (plný běh P24 kvůli A4: exit=%d, čítač=%s)"
              % (kod, pocitadlo_p24))
    aktualni = {"p24-a-overeni.py": pocitadlo_p24}
    # (2) jeho mutační důkaz + brána, která má vlastní čítač
    for popis, prikaz in (("p24-b-mutace.py", ["python", str(P24_B)]),
                          ("test-tick-offline.mjs", ["node", "tools/test-tick-offline.mjs"]),
                          ("tick-mutace.py", ["python", "_analyza/tick-mutace.py"])):
        kod, v = cmd(prikaz, timeout=1800)
        c = citac(v)
        aktualni[popis] = c
        check("A4 %s → exit 0 (naměřeno %s/%s)" % (popis, c[0] if c else "?", c[1] if c else "?"),
              kod, 0)
        # Počet VRAT se čte z TOHOHOŽ výstupu (druhý běh by byl jen dražší
        # a mohl by naměřit jiný stav — `overovani` §9.2).
        if popis == "tick-mutace.py":
            # ⚠ DOKLAD POČET VRAT NEVYKAZUJE (tiskne jen `N kontrol, M chyb`),
            # takže se odvozuje DVĚMA nezávislými cestami a ty se musí sejít:
            #   (a) ze ZDROJE: počet položek `MUTATIONS` (AST),
            #   (b) z BĚHU: kontrola na začátku + 2 kontroly na každou mutaci.
            # Kdyby platilo jen jedno, je to nález o měřidle (počet vrat by se
            # nedal ověřit a „15 vrat" by byl opis z dokumentu).
            strom_m = ast.parse((ANALYZA / "tick-mutace.py").read_text(
                encoding="utf-8", errors="replace"))
            vrat = None
            for node in ast.walk(strom_m):
                if isinstance(node, ast.Assign) and any(
                        isinstance(t, ast.Name) and t.id == "MUTATIONS"
                        for t in node.targets) and isinstance(node.value, ast.List):
                    vrat = len(node.value.elts)
            check("A4 tick-mutace: počet vrat jde přečíst ze ZDROJE (naměřeno %s)"
                  % vrat, vrat is not None, True)
            check("A4 tick-mutace: počet vrat ze ZDROJE sedí na BĚH "
                  "(1 + 2×%s = %s)" % (vrat, c[0] if c else "?"),
                  (1 + 2 * vrat) if vrat else None, c[0] if c else None)
            # TŘETÍ CESTA: doklad počítadlo vrat VYKAZUJE (P25 doplnila tisk).
            mv = re.search(r"vrat:\s*(\d+)", v)
            check("A4 tick-mutace: VYKÁZANÝ počet vrat = počet ze ZDROJE",
                  int(mv.group(1)) if mv else None, vrat)
            aktualni["tick-mutace vrat"] = (vrat, 0) if vrat else None
    # (3) g3: počet bran a nenulové exity (autorita je BĚH, ne registr)
    kod, v = cmd(["python", "_analyza/g3-brany.py"], timeout=3600)
    mg = re.search(r"brán celkem:\s*(\d+),\s*s nenulovým exit:\s*(\d+)", v)
    pocet = int(mg.group(1)) if mg else None
    nenulovych = int(mg.group(2)) if mg else None
    print("      g3: exit=%d, brán celkem=%s, s nenulovým exit=%s"
          % (kod, pocet, nenulovych))
    aktualni["g3 bran"] = (pocet, 0) if pocet else None
    mdecl = re.search(r"OCEKAVANE_NENULOVE\s*=\s*\{([^}]*)\}",
                      G3.read_text(encoding="utf-8", errors="replace"))
    check("A4 g3 má deklaraci OCEKAVANE_NENULOVE", bool(mdecl), True)
    jmena = re.findall(r'"([^"]+)"\s*:\s*(\d+)', mdecl.group(1)) if mdecl else []
    print("      deklarované nenulové exity: %s" % (jmena,))
    # ⚠ NENULOVÝ EXIT MŮŽE BÝT NÁLEZ (nedeklarovaná brána) NEBO STAV.
    # „Zastaralý inventář" je STAV: náprava je PŘEGENEROVAT inventář, ne zapsat
    # ho do `OCEKAVANE_NENULOVE` (to by z trvalé vady udělalo „očekávaný" stav).
    # Rozlišuje se podle textu, který g3 u bran zapsal — ne podle jména.
    # ⚠ NÁZEV VÝSTUPU G3 SE NESMÍ HÁDAT: `g3` píše do `_analyza/g3-brany-vystup.txt`
    # (ne `_g3-…`, jak by plynulo z `.gitignore`). Naměřeno 7. 10. 2026: se
    # vzorem `_g3-*.txt` měřidlo otevřelo STARÝ soubor bez textu o zastaralosti
    # → klasifikace neproběhla a hlásilo 3 „nedeklarované" exity nad SPRÁVNÝM
    # stavem (falešný poplach, `overovani` §8.3).
    vystupy = sorted(set(ANALYZA.glob("_g3-*.txt"))
                     | set(ANALYZA.glob("*g3*vystup*.txt")))
    text_g3 = (max(vystupy, key=lambda p: p.stat().st_mtime)
               .read_text(encoding="utf-8", errors="replace")) if vystupy else ""
    print("      výstup g3 pro klasifikaci: %s (%d znaků)"
          % (max(vystupy, key=lambda p: p.stat().st_mtime).name if vystupy
             else "(žádný)", len(text_g3)))
    deklar = [j for j, _ in jmena]
    stavove, nedeklarovane = [], []
    for p, k in re.findall(r"CHYBA\s+(.+?)\s+→\s+exit=(\d+)", v):
        if p.strip() in deklar:
            continue
        if re.search(r"inventar|inventář|N1|validate-all", p) and "ZASTARAL" in text_g3:
            stavove.append("%s (exit=%s)" % (p.strip(), k))
        else:
            nedeklarovane.append("%s (exit=%s)" % (p.strip(), k))
    for s in stavove:
        print("      ⚠ STAV (ne deklarace): %s — náprava je přegenerovat inventář" % s)
    check("A4 g3: každý nenulový exit je DEKLAROVANÝ, nebo pojmenovaný STAV "
          "(zastaralý inventář)", nedeklarovane, [])

    # POROVNÁNÍ: dokud se brány nezměnily, musí číslo SEDĚT na §54. Když se
    # změnilo (jiná session / moje práce), musí být NOVÉ číslo ZAPSANÉ — jinak je
    # to nález o dokumentu, ne o bráně.
    for nazev, par in (("p24-a-overeni.py", ("99", "0")),
                       ("p24-b-mutace.py", ("17", "0")),
                       ("test-tick-offline.mjs", ("100", "0")),
                       ("tick-mutace.py", ("31", "0"))):
        c = aktualni.get(nazev)
        if c is None:
            nezmereno_zapis("A4 %s" % nazev, "nevykázal čítač")
            continue
        text = "%d/%d" % c
        if text == "%s/%s" % par:
            check("A4 %s: naměřeno %s = tvrzeno v §54" % (nazev, text), True, True)
            continue
        zapsano = any(text in t for t in dokumenty.values())
        check("A4 %s: číslo se ZMĚNILO (%s, §54 tvrdí %s/%s) — a nové je ZAPSANÉ"
              % (nazev, text, par[0], par[1]), zapsano, True)
    # Počet VRAT a počet BRAN se v dokumentech píše jako „15 vrat" / „49 bran"
    # (ne jako `x/y`) — proto se dokumentace hledá v TOM tvaru.
    for nazev, hodnota, tvar, tvrzeno in (
            ("tick-mutace vrat", aktualni.get("tick-mutace vrat"),
             "%d vrat", 15),
            ("g3 bran", (pocet, 0) if pocet else None, "%d bran", 48)):
        if hodnota is None:
            nezmereno_zapis("A4 %s" % nazev, "nevykázal čítač")
            continue
        cislo = hodnota[0]
        if cislo == tvrzeno:
            check("A4 %s: naměřeno %s = tvrzeno v §54" % (nazev, tvar % cislo),
                  True, True)
            continue
        text = tvar % cislo
        zapsano = any(text in t for t in dokumenty.values())
        check("A4 %s: číslo se ZMĚNILO (%s, §54 tvrdí %d) — a nové je ZAPSANÉ"
              % (nazev, text, tvrzeno), zapsano, True)


# ═══════════════════════════════════════════════════════════════════ A5 ═══
def _radky_session(diff_text, znak):
    """Id řádků session na jedné straně diffu (`-`/`+`)."""
    out = []
    for radek in diff_text.splitlines():
        if not radek.startswith(znak) or radek.startswith(znak * 3):
            continue
        m = re.match(re.escape(znak) + r"\|\s*\*\*(\d+)\*\*\s*\|", radek)
        if m:
            out.append(m.group(1))
    return out


def _smazane_session(diff_text):
    """Řádky session, které v tomhle diffu SKUTEČNĚ zmizely.

    ⚠ OPRAVA 8. 10. 2026 (P27, nález P27-P): původní verze brala **každý**
    odečtený řádek `-| **N** |` jako smazaný. Když se ale řádek PŘEPÍŠE
    (např. oprava data v řádku 42), `git diff` ukáže `-` i `+` **se stejným id**
    — a brána hlásila „smazal se řádek session" na SPRÁVNÉM dokumentu
    (falešný poplach). Přepsaný řádek je ten, jehož id je i na `+` straně.
    """
    smaz = _radky_session(diff_text, "-")
    prid = set(_radky_session(diff_text, "+"))
    return [i for i in smaz if i not in prid]


def _kontrola_klasifikatoru():
    """NEGATIVNÍ KONTROLA: klasifikátor musí rozlišit PŘEPSANÝ a SMAZANÝ řádek."""
    prepsany = ("-| **42** | **7. 10. 2026** | stary text |\n"
                "+| **42** | **8. 10. 2026** | novy text |\n")
    smazany = "-| **41** | cely radek je pryc |\n"
    return (_smazane_session(prepsany), _smazane_session(smazany))


def a5():
    print("\n--- A5: nepřepsala se historie KRONIKY? ---")
    kod, v = cmd(["python", "_analyza/kronika-kontrola.py"])
    check("A5 kronika-kontrola.py → exit 0", kod, 0)
    check("A5 a řekla SEDÍ (ne jen nespadla)", "SEDÍ" in v.upper(), True)
    # NEGATIVNÍ KONTROLA klasifikátoru (musí projít, jinak brána měří špatně).
    neg = _kontrola_klasifikatoru()
    print("      klasifikátor: přepsaný řádek → %s ; skutečně smazaný → %s"
          % (neg[0], neg[1]))
    if neg != ([], ["41"]):
        print("  CHYBA: klasifikátor smazaných řádků je rozbitý "
              "(přepsaný=%s, smazaný=%s) — brána by hlásila falešný poplach"
              % (neg[0], neg[1]))
        sys.exit(2)
    # SMazané ŘÁDKY SESSION v posledních commitech, které na kroniku sáhly.
    _, revize = git("log", "--format=%H", "-n", "8", "--", "KRONIKA-PROJEKTU.md")
    revize = [x for x in revize.splitlines() if x.strip()]
    nalezy = []
    for rev in revize:
        _, d = git("diff", "%s~1" % rev, rev, "--", "KRONIKA-PROJEKTU.md")
        for i in _smazane_session(d):
            nalezy.append("%s: smazán řádek session %s" % (rev[:7], i))
    check("A5 v %d commitech se nesmazal žádný ŘÁDEK SESSION" % len(revize),
          nalezy, [])
    # NEcommitnutý strom: i ten se měří (P24 psala záznamy před commitem).
    kod, num = git("diff", "--numstat", "--", "KRONIKA-PROJEKTU.md")
    smazano = 0
    if num:
        casti = num.split("\t")
        smazano = int(casti[1]) if len(casti) > 1 and casti[1].isdigit() else 0
    check("A5 necommitnutá změna kroniky nemaže řádky (naměřeno %d)" % smazano,
          smazano, 0)
    # Řádek session P24 musí existovat se SCHVÁLENÝM typem.
    t = KRONIKA.read_text(encoding="utf-8", errors="replace")
    radky = [l for l in t.splitlines() if re.match(r"\|\s*\*\*39\*\*\s*\|", l)]
    check("A5 v kronice je právě 1 řádek session 39", len(radky), 1)
    if radky:
        typy = ("akční", "plánovací", "ověřovací", "analýza", "rozhodovací")
        nalezene = [x for x in typy if x in radky[0]]
        check("A5 typ session 39 je z povolené nabídky (naměřeno %s)" % nalezene,
              bool(nalezene), True)


# ═══════════════════════════════════════════════════════════════════ A6 ═══
def a6_zavady(brany, ocekavane_nenulove, validate_text, preskocit, vzor_test):
    """Vady v tom, CO JE BRÁNA a co jen doklad. Prázdný seznam = v pořádku."""
    v = []
    vsechny = [j for j, _ in brany]
    for j in vsechny:
        if "sonda" in j:
            v.append("v BRANY je SONDa (%s) — sonda se nesmí počítat jako brána" % j)
    if ocekavane_nenulove:
        visute = sorted(set(ocekavane_nenulove) - set(vsechny))
        if visute:
            v.append("deklarovaný nenulový exit u brány, která v BRANY není: %s" % visute)
    klicova = ("test-tick-offline", "test-health-cile", "test-watchdog-granule",
               "test-report-cooldown", "test-listgames", "test-grain-cap",
               "n03-mutace", "b3-mutace", "b2-mutace", "b4-mutace",
               "b3b-mutace", "tick-mutace")
    chybi = [k for k in klicova if k not in validate_text]
    if chybi:
        v.append("ve `validate-all.mjs` nejsou spuštěné brány: %s" % chybi)
    if "sonda" in validate_text:
        v.append("ve `spust()` validate-all je sonda")
    if "p24-sonda-site.py" not in preskocit or "p24-sonda-m2.py" not in preskocit:
        v.append("sondy nejsou v PRESKOCIT dávky `p20-d-doklady.py`")
    for jmeno in ("p24-a-overeni.py", "p24-b-mutace.py"):
        if not vzor_test.match(jmeno):
            v.append("doklad %s NENÍ pokrytý vzorem dávky `p20-d`" % jmeno)
    return v


def a6():
    print("\n--- A6: sondy nejsou brány a doklady nejsou pod kobercem ---")
    strom = ast.parse(G3.read_text(encoding="utf-8", errors="replace"))
    brany, ocek = [], []
    for node in ast.walk(strom):
        if not isinstance(node, ast.Assign):
            continue
        jmena = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "BRANY" in jmena and isinstance(node.value, ast.List):
            for el in node.value.elts:
                if isinstance(el, ast.Tuple) and el.elts and \
                        isinstance(el.elts[0], ast.Constant):
                    brany.append((el.elts[0].value, len(el.elts)))
        if "OCEKAVANE_NENULOVE" in jmena and isinstance(node.value, ast.Dict):
            ocek = [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
    check("A6 z g3 přečten seznam BRANY (naměřeno %d)" % len(brany), len(brany) > 20, True)
    check("A6 z g3 přečten seznam OCEKAVANE_NENULOVE (naměřeno %d)" % len(ocek),
          len(ocek) >= 1, True)
    zdroj_p20 = P20_D.read_text(encoding="utf-8", errors="replace")
    preskocit = []
    for node in ast.walk(ast.parse(zdroj_p20)):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "PRESKOCIT" for t in node.targets):
            if isinstance(node.value, ast.Set):
                preskocit = [e.value for e in node.value.elts
                             if isinstance(e, ast.Constant)]
    vzor_src = re.search(r"VZOR\s*=\s*re\.compile\(\s*r?[\"']([^\"']+)[\"']\s*\)",
                         bez_komentaru(zdroj_p20))
    check("A6 z p20-d přečten PRESKOCIT a VZOR",
          (len(preskocit) > 0 and vzor_src is not None), True)
    vzor = re.compile(vzor_src.group(1)) if vzor_src else None
    validate_text = VALIDATE.read_text(encoding="utf-8", errors="replace")
    zavady = a6_zavady(brany, ocek, validate_text, preskocit, vzor) \
        if vzor is not None else ["VZOR se nepodařilo přečíst"]
    check("A6 sondy nejsou brány a měřidla v dávce JSOU (naměřeno %d vad)"
          % len(zavady), zavady, [])
    print("      BRANY: %d, z toho se 'sonda' v názvu: %d"
          % (len(brany), len([j for j, _ in brany if "sonda" in j])))
    # NEGATIVNÍ KONTROLA: predikát musí na syntetické fixtuře vady NAJÍT.
    fikt = [("p24-sonda-site.py", 3)] + brany
    v2 = a6_zavady(fikt, ocek, validate_text, set(preskocit) - {"p24-sonda-m2.py"}, vzor)
    check("A6 negativní kontrola: nad fixturou se sONdou a chybějícím PRESKOCIT "
          "predikát VADY NAJDE", len(v2) >= 2, True)


# ══════════════════════════════════════════════════════════════════ main ═══
def main() -> int:
    global SRC, KRONIKA, HANDOFF, G3, VALIDATE, P20_D, TEST_TIK, P24_A, P24_B
    ap = argparse.ArgumentParser()
    ap.add_argument("--jen", default=None,
                    help="seznam etap (např. A2,A6); přebíjí výchozí režim")
    ap.add_argument("--plne", action="store_true",
                    help="PLNÁ kontrola A1–A6 (dlouhá: spustí celé měřidlo P24, "
                         "zarážky do živého zdroje a `g3`)")
    ap.add_argument("--bez-a1plne", action="store_true",
                    help="přeskočí dlouhý plný běh měřidla P24 (A1d/A4 čerpá z něj)")
    # ⚠ PŘEPÍNAČE CEST EXISTUJÍ KVŮLI MUTAČNÍMU DŮKAZU: `p25-b-mutace.py` pustí
    # tohle měřidlo nad ZMUTOVANÝMI KOPIEMI a vyžaduje, aby spadlo. Bez nich by
    # se musel mutovat ŽIVÝ strom (a to je past P24-A: přerušený běh nechal
    # v živém zdroji čtyři mutanty).
    ap.add_argument("--zdroj", default=None, help="cesta k conductor/src/index.ts")
    ap.add_argument("--kronika", default=None)
    ap.add_argument("--handoff", default=None)
    ap.add_argument("--g3", default=None)
    ap.add_argument("--validate", default=None)
    ap.add_argument("--p20d", default=None)
    ap.add_argument("--test-tik", default=None)
    ap.add_argument("--p24a", default=None)
    ap.add_argument("--p24b", default=None)
    args = ap.parse_args()
    for jmeno, hodnota in (("SRC", args.zdroj), ("KRONIKA", args.kronika),
                           ("HANDOFF", args.handoff), ("G3", args.g3),
                           ("VALIDATE", args.validate), ("P20_D", args.p20d),
                           ("TEST_TIK", args.test_tik), ("P24_A", args.p24a),
                           ("P24_B", args.p24b)):
        if hodnota:
            globals()[jmeno] = pathlib.Path(hodnota).resolve()
    etapy = {x.strip().upper() for x in
             (args.jen if args.jen else
              ("A1,A2,A3,A4,A5,A6" if args.plne else "A2,A5,A6")).split(",")
             if x.strip()}
    # ⚠ VÝCHOZÍ REŽIM JE ZÁMĚRNĚ „DÁVKOVÝ" (A2,A5,A6): plná kontrola mutuje živý
    # zdroj a pouští `g3` — v dávce `p20-d-doklady.py` by narazila na timeout
    # 1800 s a každá příští session by viděla „červený doklad" (přesně vada,
    # kterou projekt zná: doklad, který měří STAV, ne smlouvu). Že běží jen půlka,
    # se MUSÍ vytisknout — tiché zkrácení by bylo horší než žádná kontrola.
    if not args.plne and not args.jen:
        print("⚠ REŽIM DÁVKY: měří se jen A2, A5, A6 (rychlé a bez mutace živého "
              "stromu).\n  Plná kontrola (A1, A3, A4) se pouští s `--plne`.\n")

    print("=" * 78)
    print("P25/A — PŘEMĚŘENÍ PRÁCE P24 VLASTNÍM POSTUPEM (A1–A6)")
    print("=" * 78)

    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)

    pocitadlo = None
    try:
        if "A1" in etapy:
            a1_zavady_a_jeho_dukaz()
            pocitadlo = a1_plny_beh(args.bez_a1plne)
        if "A2" in etapy:
            a2()
        if "A3" in etapy:
            a3()
        if "A5" in etapy:
            a5()
        if "A6" in etapy:
            a6()
        if "A4" in etapy:
            a4(pocitadlo)
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)

    print()
    print("=" * 78)
    print("NEZMĚŘENO (není nula a není zelená): %d" % len(nezmereno))
    for p in nezmereno:
        print("   · %s" % p)
    print("=" * 78)
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    return 1 if chyb else 0


if __name__ == "__main__":
    # ⚠ Výstup se ukládá PROGRAMEM (UTF-8), ne přes PowerShell `>` — ten píše
    # UTF-16LE a ze záznamu je binárka (`dsh-prostredi` §5b, nález P24-C).
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
        vystup = ANALYZA / "p25-a-overeni-vystup.txt"
        vystup.write_bytes("".join(_tee.buffer).encode("utf-8"))
        print("plný výstup: %s (%d bajtů, UTF-8)"
              % (vystup.name, vystup.stat().st_size))
    sys.exit(_kod)
