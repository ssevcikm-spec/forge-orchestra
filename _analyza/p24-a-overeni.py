# -*- coding: utf-8 -*-
r"""P24 — ÚKOL A: NEZÁVISLE PŘEMĚŘIT NASAZENÍ A ZÁZNAMY (A1–A8).

PROČ TENHLE SKRIPT EXISTUJE
---------------------------
Zadání P24 §1: záznamy **§52/§53** i řádek kroniky psal **autor téže session,
která práci i nasazovala** — a `AGENTS.md` je v tom jednoznačné: *„autor není
nezávislý reviewer"*. Do živé služby šlo **355 řádků `index.ts`** a **6 nových
bran**; „nic se nerozbilo" se u toho **dokazuje měřením, ne pamětí**.

Skript proto **neměří nic z dokumentů** — každý bod A1–A8 měří **jiným
postupem**, než jak vznikl:

  A1  živá služba × poslední úspěšný deploy × blob nasazovacího commitu
  A2  `/tick` (chování) + prah ze ZDROJE + stav v D1 (nebo přiznané NEZMĚŘENO)
  A3  MUTANTY V COMMITECH: měří se **bloby** (HEAD, index, oba commity P23),
      ne pracovní strom — přesně past M8 z §53.3
  A4  6 mutačních důkazů se SPUSTÍ a pak jedna mutace MIMO knihovnu
  A5  nic nezmizelo: handoff 83/83 + KRONIKA jen PŘIDÁVÁ (obecně, ne dobově)
  A6  čísla v plánech se přeměří SPUŠTĚNÍM bran, ne čtením planých tvrzení
  A7  souběh: commity se nesmí překrývat v souborech
  A8  hra a její CI nedotčené

⚠ DOBOVÉ vs. TRVALÉ: body A5c/A7b/A8 měří **konkrétní commity P23**. Jsou
vypsané jako `DOBOVÉ`, ale pořád **tvrdě** — kdyby zmizely, je to nález.

Použití:
    python _analyza/p24-a-overeni.py                    # plná kontrola
    python _analyza/p24-a-overeni.py --jen-dokumenty    # jen A6 (bez sítě a gitu)
    python _analyza/p24-a-overeni.py --plan-rozvoj <cesta> --plan-agenti <cesta>
"""

import argparse
import ast
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os

WS = pathlib.Path(__file__).resolve().parents[1]
GIT = WS / "tools" / "git.cmd"
# ⚠ HRA = SOUROZENEC repa, ne zapečená cesta. P24 sem 7. 10. 2026 napsala
# `pathlib.Path(r"E:\Workspaces\uo-shadows")` — a to je REGRESE: před
# generalizací cest bylo v živých nástrojích vad 0, po ní 1 (měřidlo
# `_tools/over-nastroje.py` ji hlásí jako `VADA`). Vzor, na kterém se repa už
# sjednotilo (46 souborů v `HEAD`), je `REPO.parent / "uo-shadows"` — hra leží
# VEDLE repa, ne v něm (`_analyza/a3-mutace.py:8`, `tools/verify-setup.py:65`,
# `_analyza/g3-brany.py:55`). `FORGE_HRA` je override pro případ, že hra leží
# jinde (jiný disk se odvodit nedá) — stejný tvar jako v `g3`.
HRA = pathlib.Path(os.environ.get("FORGE_HRA") or (WS.parent / "uo-shadows"))

# Kotvy P23 (zadání NEXT-SESSION-INSTRUKCE.md §0.1 a §5).
NAS_DEPLOY = "598e207"          # commit fáze B + N0.3 (spustil deploy)
NAS_DOKUMENTY = "7f0b2f8"       # commit dokumentace (kronika + plány)
CIZI_COMMIT = "f8595de"         # commit SOUBĚŽNÉ session (generalizace)

# Soubory, které mutační důkazy vrací jako vady. Odvozeno NÍŽ ze skriptů,
# tady je jen to, co se z těch skriptů nedá přečíst (cílový soubor mutace).
KANDIDATI_SOUBORU = ("conductor/src/index.ts", "conductor/wrangler.toml",
                     "AGENTS.md", "conductor/schema.sql")

SEST_MUTACI = ["_analyza/n03-mutace.py", "_analyza/b3-mutace.py",
               "_analyza/b2-mutace.py", "_analyza/b4-mutace.py",
               "_analyza/b3b-mutace.py", "_analyza/tick-mutace.py"]

# ŠEST BRAN fáze B/N0.3 (dvanáct běhů: brána + její mutační důkaz) a DOKUMENT,
# který o každé tvrdí naměřený čítač. Tvrzení se NEOPISUJE — skládá se
# z VÝSLEDKU BĚHU, takže když se čítač změní, hledaný text v dokumentu není.
# ⚠ Čítače testu tiku jsou tvrzené v `HANDOFF.md` (§52.1 řádek 7), ne v plánu —
# kdybych je hledal v plánu, brána by spadla na SPRÁVNÉM dokumentu („nastražená
# brána“ je horší než slepá).
BRANY_A_TVRZENI = [
    ("N0.3: test-health-cile.mjs", ["node", "tools/test-health-cile.mjs"],
     "PLAN-ORCHESTRA-AI-AGENTI.md"),
    ("N0.3: n03-mutace.py", ["python", "_analyza/n03-mutace.py"],
     "PLAN-ORCHESTRA-AI-AGENTI.md"),
    ("B3a: test-watchdog-granule.py", ["python", "tools/test-watchdog-granule.py"],
     "PLAN-ROZVOJ-ORCHESTRA.md"),
    ("B3a: b3-mutace.py", ["python", "_analyza/b3-mutace.py"],
     "PLAN-ROZVOJ-ORCHESTRA.md"),
    ("B2: test-report-cooldown.py", ["python", "tools/test-report-cooldown.py"],
     "PLAN-ROZVOJ-ORCHESTRA.md"),
    ("B2: b2-mutace.py", ["python", "_analyza/b2-mutace.py"],
     "PLAN-ROZVOJ-ORCHESTRA.md"),
    ("B4: test-listgames.py", ["python", "tools/test-listgames.py"],
     "PLAN-ROZVOJ-ORCHESTRA.md"),
    ("B4: b4-mutace.py", ["python", "_analyza/b4-mutace.py"],
     "PLAN-ROZVOJ-ORCHESTRA.md"),
    ("B3b: test-grain-cap.py", ["python", "tools/test-grain-cap.py"],
     "PLAN-ROZVOJ-ORCHESTRA.md"),
    ("B3b: b3b-mutace.py", ["python", "_analyza/b3b-mutace.py"],
     "PLAN-ROZVOJ-ORCHESTRA.md"),
    ("tik offline: test-tick-offline.mjs", ["node", "tools/test-tick-offline.mjs"],
     "HANDOFF.md"),
    ("tik offline: tick-mutace.py", ["python", "_analyza/tick-mutace.py"],
     "HANDOFF.md"),
]

kontrol = 0
chyb = 0
nezmereno = []
dobove = []


def check(popis, zjisteno, ocekavano, *, dobovy=False):
    """Jedna kontrola. `dobovy=True` ji navíc zapíše do seznamu dobových měření."""
    global kontrol, chyb
    kontrol += 1
    if dobovy:
        dobove.append(popis)
    if zjisteno == ocekavano:
        print("  OK    %s" % popis)
        return True
    chyb += 1
    print("  CHYBA %s\n          čekáno: %r\n          dáno:   %r"
          % (popis, ocekavano, zjisteno))
    return False


def nezmereno_zapis(popis, duvod):
    """TŘETÍ STAV (`overovani` §7.13): „nezměřeno" NENÍ nula a NENÍ zelená."""
    nezmereno.append(popis)
    print("  NEZMĚŘENO  %s\n          důvod: %s" % (popis, duvod))


def cmd(argumenty, cwd=None, timeout=1200):
    """Spustí příkaz a vrátí (exit, výstup). Bez `shell` — `git.cmd` jde zvlášť."""
    r = subprocess.run(argumenty, cwd=str(cwd or WS), capture_output=True,
                       timeout=timeout)
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    return r.returncode, v


def git(*argumenty, repo=None, timeout=120):
    """Git přes `tools/git.cmd` (OpenSSL backend; schannel na téhle stanici padá).

    ⚠ `shell=True` je POVINNÉ — `git.cmd` je batch (`dsh-prostredi` §5b).
    ⚠ NIKDY nepoužívej `^` v revizi: `cmd.exe` ji spolkne a `git show <sha>^`
    vrátí SÁM SEBE (`dsh-prostredi` §5c). Proto všude `~1`.
    """
    prikaz = [str(GIT), "-C", str(repo or WS)] + list(argumenty)
    r = subprocess.run(prikaz, capture_output=True, shell=True, timeout=timeout)
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    return r.returncode, v.strip()


def blob(rev, cesta, repo=None):
    """Bajty blobu z gitu (autorita je blob, ne soubor na disku)."""
    r = subprocess.run([str(GIT), "-C", str(repo or WS), "show",
                        "%s:%s" % (rev, cesta)],
                       capture_output=True, shell=True, timeout=120)
    if r.returncode != 0:
        return None
    return r.stdout


def blob_hash(rev, cesta, repo=None):
    kod, v = git("rev-parse", "%s:%s" % (rev, cesta), repo=repo)
    return v if kod == 0 else None


def zmenene_soubory(rev):
    """Soubory, které commit změnil (jména, bez statistik)."""
    kod, v = git("show", "--name-only", "--format=", rev)
    if kod != 0:
        return None
    return [l.strip() for l in v.splitlines() if l.strip()]


def http_json(url, hlavicky, timeout=30):
    req = urllib.request.Request(url, headers=hlavicky)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode("utf-8"))


def env_soubor(p):
    out = {}
    for radek in p.read_text(encoding="utf-8-sig").splitlines():
        radek = radek.strip()
        if radek and not radek.startswith("#") and "=" in radek:
            k, v = radek.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def mutace_ze_skriptu(cesta):
    """Vytáhne z mutačního skriptu trojice (popis, kotva, vada) — ČTE SKRIPT.

    PROČ: tabulka markerů napsaná v měřidle **zestará**, jakmile se přidá mutace
    (přesně to se stalo dvakrát: „počet vrat“ v názvu brány 3 → 6 → 8). Když se
    seznam čte ze skriptu, nová mutace je pokrytá sama.

    ⚠ TVARY SE LIŠÍ A REGEX NA NĚ NESTAČÍ (naměřeno 7. 10. 2026: z pěti ze šesti
    skriptů vytěžil **0** mutací — a kontrola to správně ohlásila jako chybu):
      * `("popis", "stary", "novy")`                       — n03
      * `("popis", CONDUCTOR, "stary", "novy")`             — b3/b2/b4/b3b/tick
        (druhý prvek je PROMĚNNÁ s cílovým souborem, ne řetězec)
      * `{"popis": …, "najdi": …, "nahrad": …}`              — b-mutace
    Kotva a vada jsou proto **poslední dva ŘETĚZCE** v trojici, ne prvky 1 a 2.

    ⚠ CO STATICKY PŘEČÍST NELZE: kotva složená ZA BĚHU (např. `'…' + PROMENNA`
    v `b4-mutace.py` M3). Taková mutace se **vypíše jako nepokrytá** — tichý
    přesun by tvrdil pokrytí, které neexistuje (`overovani` §7.13).

    Vrací `(dvojice, neprectene)`; `neprectene` jsou popisy, které skončily
    jen proto, že jejich kotva není literál.
    """
    try:
        strom = ast.parse(cesta.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return [], []
    dvojice, neprectene = [], []
    for node in ast.walk(strom):
        if not isinstance(node, ast.Assign):
            continue
        jmena = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if not any(j.upper().startswith(("MUTATION", "MUTACE")) for j in jmena):
            continue
        prvky = node.value.elts if isinstance(node.value, (ast.List, ast.Tuple)) else []
        for el in prvky:
            if isinstance(el, ast.Tuple):
                r = [e.value for e in el.elts
                     if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                if len(r) >= 3:
                    dvojice.append((r[0], r[-2], r[-1]))
                else:
                    popis = r[0] if r else "(bez popisu)"
                    neprectene.append(popis)
            elif isinstance(el, ast.Dict):
                d = {}
                for k, v in zip(el.keys, el.values):
                    if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
                        d[k.value] = v.value
                if "najdi" in d and "nahrad" in d:
                    dvojice.append((d.get("popis", ""), d["najdi"], d["nahrad"]))
                else:
                    neprectene.append(str(d.get("popis", "(bez popisu)")))
    return dvojice, neprectene


def strom_cisty(*soubory):
    """Je soubor na disku TOTÉŽ co v INDEXU a v HEAD?

    ⚠ NESMÍ se to měřit `hash-object` proti blobu: `core.autocrlf` dělá z téhož
    obsahu na disku CRLF a v blobu LF (naměřeno 7. 10. 2026: 88 462 B vs
    86 719 B u téhož souboru, `git status` Přitom ČISTÝ). Autorita je `git diff`
    (`dsh-prostredi` §1 a §5b) — ptá se na OBSAH po normalizaci, ne na bajty.
    """
    for s in soubory:
        if git("diff", "--quiet", "--", s)[0] != 0:
            return False, "%s: disk != index" % s
        if git("diff", "--cached", "--quiet", "--", s)[0] != 0:
            return False, "%s: index != HEAD" % s
    return True, ""


# ═══════════════════════════════════════════════════════════════════════════
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jen-dokumenty", action="store_true",
                    help="přeskočí síť, git a běh bran (jen tvar A6) — pro mutační test")
    ap.add_argument("--jen-a6", action="store_true",
                    help="přeskočí všechno kromě A6 VČETNĚ spuštění bran — pro "
                         "mutaci ČÍSLA v dokumentu (druhá polovina důkazu, že "
                         "kontrola čísel není prázdná)")
    ap.add_argument("--jen-brana", default=None,
                    help="s '--jen-a6' spustí jen brány, jejichž popis obsahuje "
                         "tenhle podřetězec (jinak by mutace čísla běžela 12×)")
    ap.add_argument("--plan-rozvoj", default="PLAN-ROZVOJ-ORCHESTRA.md")
    ap.add_argument("--plan-agenti", default="PLAN-ORCHESTRA-AI-AGENTI.md")
    args = ap.parse_args()

    print("=" * 78)
    print("P24/A — NEZÁVISLÉ PŘEMĚŘENÍ NASAZENÍ A ZÁZNAMŮ")
    print("=" * 78)

    plan_cesty = {"PLAN-ORCHESTRA-AI-AGENTI.md": WS / args.plan_agenti,
                  "PLAN-ROZVOJ-ORCHESTRA.md": WS / args.plan_rozvoj}

    # ── A6 se dělá VŽDY (i v režimu --jen-dokumenty) ────────────────────────
    print("\n--- A6: čísla v plánech sedí na KÓD (a plány mají správný tvar) ---")
    texty = {}
    for nazev, cesta in plan_cesty.items():
        if not cesta.is_file():
            check("A6 plán existuje: %s" % nazev, False, True)
            continue
        texty[nazev] = cesta.read_text(encoding="utf-8", errors="replace")

    # Tvar dokumentu: bez těchhle kotev se nedá tvrdit NIC o číslech v něm
    # (a je to přesně to, co mutační test maže, aby skript musel spadnout).
    if "PLAN-ORCHESTRA-AI-AGENTI.md" in texty:
        t = texty["PLAN-ORCHESTRA-AI-AGENTI.md"]
        check("A6 tvar: plán agentů má kotvu '| **N0.3** |'", "| **N0.3** |" in t, True)
        check("A6 tvar: N0.3 je označeno HOTOVO", "HOTOVO A NASAZENO" in t, True)
    if "PLAN-ROZVOJ-ORCHESTRA.md" in texty:
        t = texty["PLAN-ROZVOJ-ORCHESTRA.md"]
        # ⚠ KOTVA JE CELÝ NADPIS, NE FRÁZE „Fáze B“: ta je v dokumentu dvakrát
        # (nadpis oddílu + věta „Fáze B znamená deploy conductora“), takže
        # kontrola by zelenala i nad dokumentem, kterému oddíl zmizel.
        # Odhalil to až mutační test `p24-b-mutace.py` (případ 2) — přesně past
        # „ptej se, KTERÝ výskyt vzor trefí“ (`overovani` §10.1).
        check("A6 tvar: plán rozvoje má NADPIS '### Fáze B'",
              "### Fáze B" in t, True)
        for b in ("B1", "B2", "B3", "B4", "B5"):
            check("A6 tvar: řádek '| **%s** |' v plánu" % b, "| **%s** |" % b in t,
                  True)

    # Vlastní měření: bran se SPUSTÍ a čítač se PŘEČTE Z BĚHU.
    if not args.jen_dokumenty:
        # Texty dokumentů, o kterých se tvrdí čísla (plány + HANDOFF).
        tvrzeni_texty = dict(texty)
        if "HANDOFF.md" not in tvrzeni_texty and (WS / "HANDOFF.md").is_file():
            tvrzeni_texty["HANDOFF.md"] = (WS / "HANDOFF.md").read_text(
                encoding="utf-8", errors="replace")
        for popis, prikaz, dokument in BRANY_A_TVRZENI:
            if args.jen_brana and args.jen_brana not in popis:
                continue
            kod, v = cmd(prikaz)
            m = None
            # ⚠ VZOR MUSÍ BÝT CASE-INSENSITIVE: mutační doklady tisknou při
            # ÚSPĚCHU `0 chyb`, ale při NÁLEZU `1 CHYB` (velkými). Kdo hledá
            # jen malá písmena, u červeného dokladu čítač nenajde — a vykáže
            # „nevykázal čítač“ místo skutečného nálezu (naměřeno 7. 10. 2026).
            for m in re.finditer(r"(\d+) kontrol, (\d+) chyb", v, re.IGNORECASE):
                pass
            if not m:
                check("A6 %s → vykázala čítač" % popis, False, True)
                print("          poslední řádky: %s"
                      % " | ".join(x for x in v.strip().splitlines()[-3:]))
                continue
            vysledek = (int(m.group(1)), int(m.group(2)))
            check("A6 %s → exit 0 (naměřeno %d/%d)" % (popis, *vysledek), kod, 0)
            check("A6 %s → 0 chyb" % popis, vysledek[1], 0)
            # Tvrzení se SKLÁDÁ Z BĚHU a hledá se v TEXTU dokumentu — kdyby tam
            # číslo nebylo, je to nález o DOKUMENTU, ne o bráně.
            tvrzeni = "%d/%d" % vysledek
            t = tvrzeni_texty.get(dokument, "")
            check("A6 %s: dokument '%s' tvrdí naměřené %s"
                  % (popis, dokument, tvrzeni), tvrzeni in t, True)
            if popis.startswith("tik offline: test-tick"):
                check("A6 %s: dokument tvrdí i počet KONTROL (%d kontrol)"
                      % (popis, vysledek[0]),
                      ("%d kontrol" % vysledek[0]) in t, True)

    # B5: komentáře o `MAX_ATTEMPTS` („mrtvý kód") — měří se grepem nad ZDROJEM.
    if not args.jen_dokumenty:
        src = (WS / "conductor" / "src" / "index.ts").read_text(
            encoding="utf-8", errors="replace")
        pocet = len(re.findall(r"mrtvý kód", src))
        check("A6 B5: 'mrtvý kód' ve zdroji conductora → 0 (naměřeno %d)" % pocet,
              pocet, 0)

    if args.jen_dokumenty or args.jen_a6:
        rezim = ("--jen-dokumenty: A1–A5, A7, A8 se neměřily"
                 if args.jen_dokumenty else
                 "--jen-a6: měřilo se jen A6 (tvar dokumentu + čítače bran)")
        print()
        print("VÝSLEDEK: %d kontrol, %d chyb   (režim %s)" % (kontrol, chyb, rezim))
        return 1 if chyb else 0

    # ── A1: živá služba na tvrzeném commitu ─────────────────────────────────
    print("\n--- A1: živá služba běží na commitu, který se tvrdí ---")
    _, head = git("rev-parse", "HEAD")
    _, nasazovaci = git("log", "-1", "--format=%H", "--", "conductor/")
    nasazovaci = nasazovaci.strip()
    print("  HEAD: %s   poslední změna conductor/: %s"
          % (head[:7], nasazovaci[:7]))

    pat = (WS / ".secrets" / "github_pat.txt").read_text(encoding="utf-8").strip()
    H = {"Authorization": "Bearer %s" % pat,
         "Accept": "application/vnd.github+json",
         "User-Agent": "forge-p24-overeni"}
    deploy_sha, deploy_cislo = None, None
    try:
        _, d = http_json("https://api.github.com/repos/ssevcikm-spec/"
                         "forge-orchestra/actions/workflows/deploy.yml/runs"
                         "?per_page=20", H)
        for r in d.get("workflow_runs", []):
            if r.get("conclusion") == "success":
                deploy_sha, deploy_cislo = r["head_sha"], r["run_number"]
                break
            print("  (přeskočen neúspěšný deploy #%s: %s/%s)"
                  % (r["run_number"], r["status"], r.get("conclusion")))
    except Exception as e:                                        # noqa: BLE001
        nezmereno_zapis("A1 poslední úspěšný deploy.yml", "%s: %s" % (type(e).__name__, e))

    if deploy_sha:
        check("A1 poslední úspěšný deploy (#%s) běžel na poslední změně "
              "conductor/** (%s)" % (deploy_cislo, nasazovaci[:7]),
              deploy_sha, nasazovaci, dobovy=True)
        # DRUHÁ, NEZÁVISLÁ CESTA: obsah. Kdyby se blob nasazovacího commitu
        # rozešel s HEAD, je nasazený jiný kód, i kdyby sha „sedělo".
        check("A1 blob conductor/src/index.ts je v nasazovacím commitu i v HEAD "
              "TOTÉŽ", blob_hash(deploy_sha, "conductor/src/index.ts"),
              blob_hash("HEAD", "conductor/src/index.ts"), dobovy=True)
        check("A1 blob conductor/wrangler.toml je TOTÉŽ",
              blob_hash(deploy_sha, "conductor/wrangler.toml"),
              blob_hash("HEAD", "conductor/wrangler.toml"), dobovy=True)

    env = env_soubor(WS / ".env")
    url = env.get("FORGE_URL", "").rstrip("/")
    # ⚠ Cloudflare vrací 403 `error code: 1010` na `Python-urllib/3.x` — je to
    # BLOKACE PODLE User-Agenta, ne vada služby (naměřeno sondou p24-sonda-site).
    HL = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) forge-p24"}
    health = None
    try:
        _, health = http_json(url + "/health", HL)
    except Exception as e:                                        # noqa: BLE001
        nezmereno_zapis("A1 živé /health", "%s: %s" % (type(e).__name__, e))

    if health is not None:
        check("A1 živé /health vrací klíč 'targets' (umí JEN kód z 598e207)",
              "targets" in health, True, dobovy=True)
        cile = health.get("targets") or []
        check("A1 /health.targets je neprázdné (naměřeno %d)" % len(cile),
              len(cile) > 0, True, dobovy=True)
        if cile:
            t0 = cile[0]
            print("      targets[0]: repo=%s main_ci=%s forge.ok=%s "
                  "selhani_v_rade=%s" % (t0.get("repo"), t0.get("main_ci"),
                                         (t0.get("forge") or {}).get("ok"),
                                         (t0.get("forge") or {}).get("selhani_v_rade")))
            check("A1 targets[0].main_ci je ZMĚŘENO (ne null)",
                  t0.get("main_ci") is not None, True, dobovy=True)
        print("      /health: ok=%s ready=%s running=%s games=%s"
              % (health.get("ok"), health.get("ready"), health.get("running"),
                 health.get("games")))

    # ── A2: watchdog eskaluje (dvě cesty) ───────────────────────────────────
    print("\n--- A2: watchdog opravdu eskaluje ---")
    sekret = env.get("FORGE_SECRET", "")
    HL2 = dict(HL)
    HL2["x-forge-secret"] = sekret
    tick = None
    try:
        req = urllib.request.Request(url + "/tick", method="POST", headers=HL2)
        with urllib.request.urlopen(req, timeout=120) as r:
            tick = json.loads(r.read().decode("utf-8"))
    except Exception as e:                                        # noqa: BLE001
        nezmereno_zapis("A2 POST /tick", "%s: %s" % (type(e).__name__, e))

    if tick:
        zprava = tick.get("message", "")
        m = re.search(r"watchdog:\s*(\d+)\s*ohlášeno\s*\(prah\s*(\d+)\)", zprava)
        check("A2 /tick řekl větu 'watchdog: N ohlášeno (prah P)'", bool(m), True,
              dobovy=True)
        if m:
            ohlased, prah = int(m.group(1)), int(m.group(2))
            print("      /tick: watchdog %d ohlášeno, prah %d" % (ohlased, prah))
            # DRUHÁ CESTA: prah se čte ze ZDROJE, ne z dokumentu.
            src = (WS / "conductor" / "src" / "index.ts").read_text(
                encoding="utf-8", errors="replace")
            mp = re.search(r'ESCALATE_AFTER[^0-9]{0,40}"(\d+)"', src)
            if mp:
                check("A2 prah z /tick (%d) = prah ve ZDROJI (%s)"
                      % (prah, mp.group(1)), str(prah), mp.group(1), dobovy=True)
            # ⚠ VLASTNÍ VADA B3a BYLA: prah 8 > strop 5 → watchdog se NIKDY
            # nespustil. Kontrola proto měří právě TOHLE: prah musí být POD
            # stropem. (Původně tu stálo „N > 0“ — a to je ŠPATNÁ OTÁZKA:
            # značka `eskalovano` je TRVALÁ, takže po prvním ohlášení je N
            # navždy 0 a správná služba by bránu shodila. Naměřeno 7. 10. 2026:
            # záznam §53 tvrdil `2 ohlášeno`, dnes `0` — a to je PŘESNĚ ono.)
            ms = re.search(r'MAX_ATTEMPTS[^0-9]{0,40}"?(\d+)"?', src)
            if ms:
                check("A2 prah %d je POD stropem MAX_ATTEMPTS=%s (to byla vada B3a)"
                      % (prah, ms.group(1)), prah < int(ms.group(1)), True,
                      dobovy=True)
            print("      (záznam §53 tvrdil 2 ohlášeno při prvním tiku — dnes %d; "
                  "značka je TRVALÁ, takže 0 = už ohlášeno, ne „nespustilo se“)"
                  % ohlased)

    # TŘETÍ CESTA: stav v D1. `roadmap.eskalovano` se NIKAM neposílá — a to se
    # musí říct, ne zamlčet („nezměřeno ≠ 0").
    zdroj_ts = (WS / "conductor" / "src" / "index.ts").read_text(
        encoding="utf-8", errors="replace")
    if 'if (path === "/roadmap")' not in zdroj_ts:
        nezmereno_zapis("A2 stav granul v D1",
                        "ve zdroji není handler `/roadmap` — není se na co ptát")
    else:
        # Vytáhne SELECT z handleru `/roadmap` a ptá se, jestli vrací sloupec
        # `eskalovano`. Když ne, D1 stav změřit NELZE (endpoint ho neposílá
        # a D1 přes REST nejde — skill `orchestra`, invariant 7).
        telo = zdroj_ts.split('if (path === "/roadmap")', 1)[1].split("if (path ===", 1)[0]
        if "eskalovano" not in telo:
            nezmereno_zapis(
                "A2 stav granul s `roadmap.eskalovano` v D1",
                "conductor nemá endpoint, který by sloupec vracel (ověřeno "
                "čtením SELECTu handleru `/roadmap` ve ZDROJI); D1 přes REST "
                "nejde (skill `orchestra`, invariant 7). NEZMĚŘENO — není to "
                "nula a není to zelená.")
        else:
            try:
                _, rm = http_json(url + "/roadmap", HL2)
                esc = [x for x in rm.get("roadmap", []) if x.get("eskalovano")]
                check("A2 v D1 je označena aspoň jedna granule (naměřeno %d)"
                      % len(esc), len(esc) > 0, True, dobovy=True)
            except Exception as e:                                # noqa: BLE001
                nezmereno_zapis("A2 stav granul v D1",
                                "%s: %s" % (type(e).__name__, e))

    # ── A3: v commitech nejsou mutanty (BLOBY, ne strom) ────────────────────
    print("\n--- A3: v commitech (a v INDEXU) nejsou mutanty ---")
    # Mutace se čtou ze SKRIPTŮ, ne z tabulky v tomhle měřidle. Berou se
    # VŠECHNY mutační skripty `_analyza/` — ne jen šest z A4 — protože A3 se
    # ptá na každý soubor, „který mutační testy mutují“ (zadání §2.1).
    skripty_mutaci = sorted((WS / "_analyza").glob("*mutace*.py"))
    mutace = []
    neprectene = []
    for p in skripty_mutaci:
        d, n = mutace_ze_skriptu(p)
        mutace += [(p.name, *x) for x in d]
        neprectene += [(p.name, x) for x in n]
    check("A3 z %d mutačních skriptů přečteny kotvy (naměřeno %d)"
          % (len(skripty_mutaci), len(mutace)), len(mutace) > 0, True)
    # Každý z šesti dokladů A4 musí dát aspoň jednu kotvu — jinak by A3
    # neměřila to, o čem A4 tvrdí, že to umí shodit.
    for rel in SEST_MUTACI:
        d, _n = mutace_ze_skriptu(WS / rel)
        check("A3 z %s přečteny mutace (naměřeno %d)"
              % (pathlib.Path(rel).name, len(d)), len(d) > 0, True)
    # ⚠ NEPŘEČTENÉ SE VYPÍŠOU. Kdyby se tiše přeskočily, A3 by tvrdila pokrytí,
    # které nemá — a to je horší než přiznaná díra (`overovani` §7.13).
    if neprectene:
        print("      ⚠ kotva složená ZA BĚHU (staticky nepřečtená, kryje ji A4):")
        for skript, popis in neprectene:
            print("         %s: %s" % (skript, popis[:60]))
    print("      kotev mutací celkem: %d, nepřečtených: %d"
          % (len(mutace), len(neprectene)))

    # (1) NEJSILNĚJŠÍ KONTROLA: disk == index == HEAD u každého mutovaného
    #     souboru. Přesně tahle třída odhalila M8 (§53.3): `git diff` byl
    #     prázdný, protože disk byl správně, ale INDEX nesl `if (false) {`.
    #     ⚠ NEMĚŘÍ SE `hash-object` PROTI BLOBU: `core.autocrlf` dělá z téhož
    #     obsahu na disku CRLF a v blobu LF (naměřeno 7. 10. 2026: 88 462 B vs
    #     86 719 B u téhož souboru a `git status` PŘITOM čistý). Autorita je
    #     `git diff` — ptá se na obsah po normalizaci (`dsh-prostredi` §1, §5b).
    kontrolovane_soubory = [s for s in KANDIDATI_SOUBORU if (WS / s).is_file()]
    zive_texty = {s: (WS / s).read_bytes().decode("utf-8", "replace")
                  for s in kontrolovane_soubory}
    cisto, duvod = strom_cisty(*kontrolovane_soubory)
    check("A3 všechny mutované soubory: disk == index == HEAD", cisto, True)
    if not cisto:
        print("          %s" % duvod)
    # (2) KOTVY: každá kotva, která je v živém souboru, musí být i v blobu
    #     commitu. Kdyby byla mutace zapečená, kotva by v blobu CHYBĚLA.
    for rev, popis in ((NAS_DEPLOY, "598e207"), (NAS_DOKUMENTY, "7f0b2f8"),
                       ("HEAD", "HEAD")):
        chybejici = []
        overeno = 0
        for rel, jmeno, kotva, vada in mutace:
            for s in kontrolovane_soubory:
                if kotva not in zive_texty[s]:
                    continue        # kotva do TOHOHLE souboru nepatří
                overeno += 1
                b = blob(rev, s)
                if b is None:
                    chybejici.append("%s (blob %s:%s nejde přečíst)" % (jmeno, popis, s))
                    continue
                if kotva not in b.decode("utf-8", "replace"):
                    chybejici.append("%s → %s" % (jmeno, s))
        # ⚠ KDYBY NESEDLA ANI JEDNA KOTVA, BYLA BY KONTROLA PRÁZDNÁ a zelená by
        # neznamenala nic (`overovani` §7.13). Proto je nula NÁLEZ, ne ticho.
        if overeno == 0:
            chybejici.append("NEMĚŘENO — žádná kotva nesedla na žádný soubor")
        check("A3 %s: všech %d kotv je v blobu (žádná mutace není zapečená)"
              % (popis, overeno), chybejici, [], dobovy=(rev != "HEAD"))

    # (3) Dobové: co P23 commity vůbec změnily.
    for rev in (NAS_DEPLOY, NAS_DOKUMENTY):
        z = zmenene_soubory(rev)
        check("A3 %s: seznam změněných souborů jde přečíst (naměřeno %s)"
              % (rev, len(z) if z is not None else None),
              z is not None and len(z) > 0, True, dobovy=True)

    # ── A4: brány umí selhat i po nasazení ──────────────────────────────────
    print("\n--- A4: 6 mutačních důkazů + jedna mutace MIMO knihovnu ---")
    # ⚠ PŘEDBĚŽNÁ PODMÍNKA, BEZ KTERÉ SE NEMUTUJE (naměřeno 7. 10. 2026 v P24):
    # první běh tohohle měřidla byl PŘERUŠEN uprostřed mutačního testu a nechal
    # v ŽIVÉM ZDROJI **čtyři mutanty** (`expiruje: 0`, `merged = true`, requeue
    # bez stropu, `if (false) break;`). Další běh je pak „neměřil“ — kotvy byly
    # pryč a skripty padaly na `kotva v souboru NENÍ`. Proto: strom musí být
    # čistý PŘED mutováním, a po KAŽDÉM skriptu se ověří, že se vrátil.
    cisto, duvod = strom_cisty(*kontrolovane_soubory)
    check("A4 PŘED mutacemi je strom čistý (jinak by mutace měřila na cizí vadě)",
          cisto, True)
    if not cisto:
        print("          %s" % duvod)
        print("          → mutace se NESPOUŠTÍ; naprav strom (`git checkout HEAD -- <soubor>`)")

    for rel in SEST_MUTACI:
        if not cisto:
            break
        kod, v = cmd(["python", rel])
        m = None
        # Case-insensitive kvůli `1 CHYB` (viz vysvětlení u A6).
        for m in re.finditer(r"(\d+) kontrol, (\d+) chyb", v, re.IGNORECASE):
            pass
        if not m:
            check("A4 %s vykázal čítač" % rel, False, True)
            print("          poslední řádky: %s"
                  % " | ".join(x for x in v.strip().splitlines()[-3:]))
            continue
        check("A4 %s → exit 0 (naměřeno %s/%s)"
              % (rel, m.group(1), m.group(2)), kod, 0)
        # PO KAŽDÉM SKRIPTU: vrátil se soubor? Když ne, je to nález o TOM skriptu
        # (a strom se musí napravit, než poběží další).
        cisto_po, duvod_po = strom_cisty(*kontrolovane_soubory)
        check("A4 po %s je strom zpět (disk == index == HEAD)" % rel,
              cisto_po, True)
        if not cisto_po:
            print("          %s" % duvod_po)

    cisto, duvod = strom_cisty(*kontrolovane_soubory)
    check("A4 po všech mutačních důkazech je strom čistý", cisto, True)

    # MUTACE MIMO KNIHOVNU: kdyby knihovna `_mutace.mutuj` byla ta, kdo „měří",
    # muselo by to spadnout i s ručním `replace`.
    cil = WS / "conductor" / "src" / "index.ts"
    kotva = "selhani_v_rade: vRade,"
    vada = "selhani_v_rade: 0,"
    puvodni = cil.read_bytes()
    try:
        text = puvodni.decode("utf-8")
        check("A4 ruční mutace: kotva je ve zdroji PRÁVĚ 1× (naměřeno %d)"
              % text.count(kotva), text.count(kotva), 1)
        cil.write_bytes(text.replace(kotva, vada, 1).encode("utf-8"))
        kod, v = cmd(["node", "tools/test-health-cile.mjs"])
        check("A4 ruční mutace MIMO knihovnu → brána SPADLA (exit=%d)" % kod,
              kod != 0, True, dobovy=True)
    finally:
        cil.write_bytes(puvodni)
    cisto, duvod = strom_cisty("conductor/src/index.ts")
    check("A4 po ruční mutaci je index.ts zpět (disk == index == HEAD)",
          cisto, True)

    # ── A5: nic nezmizelo ───────────────────────────────────────────────────
    print("\n--- A5: nic nezmizelo ---")
    kod, v = cmd(["python", "_analyza/handoff-kontrola-uplnost.py"])
    m = re.search(r"kontrolovaných klíčů:\s+(\d+)", v)
    mch = re.search(r"CHYBÍ:\s+(\d+)", v)
    check("A5 handoff úplnost: kontrolovaných klíčů = 83", 
          int(m.group(1)) if m else None, 83)
    check("A5 handoff úplnost: CHYBÍ = 0", int(mch.group(1)) if mch else None, 0)
    check("A5 handoff úplnost → exit 0", kod, 0)

    # OBECNĚ: KRONIKA se NIKDY nepřepisuje, jen doplňuje. Měří se proto
    # SMAZANÉ ŘÁDKY, ne předpona: řádek session 38 se vkládá DOPROSTŘED tabulky
    # §1, takže „starý obsah je předponou nového“ NEPLATÍ, i když se nic
    # neztratilo. (Naměřeno 7. 10. 2026: tahle verze kontroly hlásila 5 přepisů
    # u commitů, které jen vložily řádek nebo přepsaly SOUHRNNÝ řádek.)
    # Co se přepsat SMÍ: souhrny (`| **celkem** |`, `| **1–N** |`) — to je stav.
    # Co se přepsat NESMÍ: řádek session `| **<číslo>** | …` v §1.
    kod, v = git("log", "--format=%H", "-n", "6", "--", "KRONIKA-PROJEKTU.md")
    revize = [x for x in v.splitlines() if x.strip()]
    porad = []
    for rev in revize:
        kod_n, num = git("diff", "--numstat", "%s~1" % rev, rev,
                         "--", "KRONIKA-PROJEKTU.md")
        if kod_n != 0 or not num:
            porad.append("%s (numstat nejde přečíst)" % rev[:7])
            continue
        casti = num.split("\t")
        smazano = int(casti[1]) if len(casti) >= 2 and casti[1].isdigit() else None
        if smazano is None:
            porad.append("%s (numstat nemá číslo)" % rev[:7])
            continue
        if smazano == 0:
            continue
        # Když se mazalo, smí to být JEN souhrnný řádek.
        # ⚠ OPRAVA 8. 10. 2026 (P27, nález P27-P): PŘEPSANÝ řádek (např. oprava
        # data v řádku session) ukáže `git diff` jako `-` **i** `+` se STEJNÝM
        # id — a původní verze to hlásila jako „SMAZAL ŘÁDEK SESSION“ na
        # správném dokumentu (falešný poplach). Za smazaný se počítá jen id,
        # které na `+` straně diffu NENÍ.
        _, d = git("diff", "%s~1" % rev, rev, "--", "KRONIKA-PROJEKTU.md")
        smaz, prid = [], set()
        for radek in d.splitlines():
            m = re.match(r"-\|\s*\*\*(\d+)\*\*\s*\|", radek)
            if m:
                smaz.append((m.group(1), radek))
                continue
            m = re.match(r"\+\|\s*\*\*(\d+)\*\*\s*\|", radek)
            if m:
                prid.add(m.group(1))
        for ident, radek in smaz:
            if ident not in prid:
                porad.append("%s SMAZAL ŘÁDEK SESSION %s: %s"
                             % (rev[:7], ident, radek[:70]))
    check("A5 KRONIKA: v %d posledních commitech se neSmazal žádný ŘÁDEK SESSION"
          % len(revize), porad, [])
    # Dobové (zadání §2.1 A5): P23 přidával, nemazal.
    kod_n, num = git("diff", "--numstat", "%s~1" % NAS_DEPLOY, NAS_DOKUMENTY,
                     "--", "KRONIKA-PROJEKTU.md")
    smaz = num.split("\t")[1] if num and "\t" in num else None
    check("A5 KRONIKA v rozsahu %s~1..%s: smazaných řádků = 0"
          % (NAS_DEPLOY, NAS_DOKUMENTY), smaz, "0", dobovy=True)

    # ── A7: tvrzení o souběhu je dnešní ─────────────────────────────────────
    print("\n--- A7: souběh se souběžnou session ---")
    kod, v = git("status", "--porcelain")
    radky = [l for l in v.splitlines() if l.strip()]
    print("      git status --porcelain: %d řádků" % len(radky))
    for l in radky[:12]:
        print("        %s" % l)

    soub_p23 = set(zmenene_soubory(NAS_DEPLOY) or [])
    soub_p23d = set(zmenene_soubory(NAS_DOKUMENTY) or [])
    soub_cizi = set(zmenene_soubory(CIZI_COMMIT) or [])
    # ⚠ OTÁZKA NENÍ „protínají se množiny?“, ale „KDO BYL PRVNÍ?“ (naměřeno
    # 7. 10. 2026: průnik jsou 2 soubory — `_analyza/_registr-bran.json`
    # a `tools/validate-all.mjs` — a PŘESTO v commitu P23 nic cizího není:
    # souběžná session na ně sáhla POZDĚJI, protože `f8595de` je POTOMEK
    # `598e207`). Kdo se ptá jen na průnik, hlásí falešný nález o správném
    # commitu — a to je horší než slepé místo (`overovani` §10.1).
    je_potom = git("merge-base", "--is-ancestor", NAS_DEPLOY, CIZI_COMMIT)[0] == 0
    check("A7 %s je PŘEDCHŮDCE %s (souběžná session commitovala později)"
          % (NAS_DEPLOY, CIZI_COMMIT), je_potom, True, dobovy=True)
    print("      průnik souborů P23 × souběžná session: %d %s"
          % (len(sorted(soub_p23 & soub_cizi)), sorted(soub_p23 & soub_cizi)))
    check("A7 průnik souborů je VYSVĚTLENÝ pořadím commitů (ne tichý)",
          bool(soub_p23 & soub_cizi) == je_potom or not (soub_p23 & soub_cizi),
          True, dobovy=True)
    check("A7 dokumentační commit (%s) neobsahuje soubory souběžné session"
          % NAS_DOKUMENTY, sorted(soub_p23d & soub_cizi), [], dobovy=True)
    check("A7 %s změnil aspoň 20 souborů (naměřeno %d)" % (NAS_DEPLOY, len(soub_p23)),
          len(soub_p23) >= 20, True, dobovy=True)

    kod, v = git("rev-list", "--count", "origin/main..HEAD")
    print("      nepushnutých commitů: %s" % v)
    check("A7 nepushnuté commity jdou změřit (ne odhadnout)", v.isdigit(), True)

    # ── A8: hra a její CI nejsou dotčené ────────────────────────────────────
    print("\n--- A8: hra a její CI nejsou dotčené ---")
    if not (HRA / ".git").exists():
        nezmereno_zapis("A8 hra uo-shadows", "klon %s neexistuje" % HRA)
    else:
        _, hhra = git("rev-parse", "--short", "HEAD", repo=HRA)
        kod, stav = git("status", "--porcelain", repo=HRA)
        check("A8 uo-shadows HEAD = 44dd454 (naměřeno %s)" % hhra.strip(),
              hhra.strip(), "44dd454", dobovy=True)
        check("A8 strom hry je ČISTÝ", [l for l in stav.splitlines() if l.strip()],
              [], dobovy=True)
        _, pred_hra = git("rev-parse", "HEAD", repo=HRA)
        _, po_hra = git("rev-parse", "origin/main", repo=HRA)
        check("A8 hra nemá nepushnuté commity", pred_hra, po_hra, dobovy=True)

    kod, v = git("diff", "--name-only", "%s~1" % NAS_DEPLOY, NAS_DOKUMENTY)
    dotcene = [l for l in v.splitlines() if l.strip()]
    do_hry = [l for l in dotcene
              if l.startswith("games/") or l.startswith("../uo-shadows")
              or "uo-shadows" in l]
    check("A8 rozsah %s~1..%s neobsahuje NIC z cesty do hry (naměřeno %d souborů)"
          % (NAS_DEPLOY, NAS_DOKUMENTY, len(dotcene)), do_hry, [], dobovy=True)

    # ── souhrn ──────────────────────────────────────────────────────────────
    print()
    print("=" * 78)
    print("DOBOVÁ MĚŘENÍ (commity P23 — platí o nich, ne o dnešku): %d" % len(dobove))
    print("NEZMĚŘENO (není nula a není zelená): %d" % len(nezmereno))
    for p in nezmereno:
        print("   · %s" % p)
    print("=" * 78)
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    return 1 if chyb else 0


if __name__ == "__main__":
    # ⚠ VÝSTUP SE UKLÁDÁ TADY, NE PŘES POWERSELL. `python skript.py > soubor`
    # v PowerShellu vyrobí **UTF-16LE** (naměřeno 7. 10. 2026: první bajty
    # `FF FE`), takže z evidenčního souboru je binárka a `read` tool ho odmítne
    # přečíst — a někdo ho pak „cituje“ z výpisu konzole (`dsh-prostredi` §5b).
    # Tohle je táž past jako `git show > soubor`, jen u BĚŽNÉHO programu.
    _trida = type("T", (), {"buffer": []})()
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
        vystup = WS / "_analyza" / "p24-a-overeni-vystup.txt"
        vystup.write_bytes("".join(_tee.buffer).encode("utf-8"))
        print("plný výstup: %s (%d bajtů, UTF-8)"
              % (vystup.name, vystup.stat().st_size))
    sys.exit(_kod)
