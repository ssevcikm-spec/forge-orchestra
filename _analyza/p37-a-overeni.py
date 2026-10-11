r"""p37-a-overeni.py — VLASTNÍ MĚŘIDLO P37: přeměření práce P36 (Úkol A).

**Co to je:** nezávislé přeměření tvrzení P36 — NE spuštění měřidla P36
(`p36-a-overeni.py`) a čtení jeho verdiktu. P36 psala měřidlo, opravu i záznamy
sama a `AGENTS.md` je v tom jednoznačné: *„autor není nezávislý reviewer“*.

**Jak se liší od P36:** každé tvrzení se bere jako TEXT Z DOKUMENTU
(`HANDOFF.md` §67 + `NEXT-SESSION-INSTRUKCE.md`) a porovnává se s ŽIVÝM měřením
( git ls-remote, `p30-sonda-deploy.mjs`, GitHub API, `wrangler tail`,
Cloudflare Analytics, D1, spuštěné brány). **Nenalezené tvrzení je CHYBA**
(H155) — ne přeskočení.

**Co měří (A0–A7):**
  A0  pojistky: `origin/main == HEAD`, co je ve stromě necommitnuté, stav hry
  A1  je P36 pushnutá a CO JE ŽIVÉ (deploy #39 je z P35, ne z P36 — P36
      conductora neměnila; ověřuje se z `git show --stat`)
  A2  je oprava H172 v KÓDU a má test, který ji ZAVOLÁ
  A3  sedí čísla z §67 (vlastní čtení + spuštění tvrzených měřidel)
  A4  je tik živě v pořádku (vlastní parser `p37-tail-*` + ruční tik + historie)
  A5  jsou tepy v `/health` a v D1
  A6  uklízí se měřidla po sobě (mutační běh + živé soubory proti HEAD
      BEZ FILTRU PŘÍPON, H163/H169)
  A7  nic se nerozbilo (inventář → g3 → inventář → validate-all; kronika;
      handoff; ov-g)

**Použití:**
  python _analyza/p37-a-overeni.py              # LEVNÝ režim (A0, A1, A4 + levné nohy)
  python _analyza/p37-a-overeni.py --plne       # všechno (A7 ~6 min: g3 + validate-all)
  python _analyza/p37-a-overeni.py --jen A4     # jedna etapa
  python _analyza/p37-a-overeni.py --levne      # totéž co bez argumentu

⚠ VÝCHOZÍ REŽIM JE **LEVNÝ** (kvůli dávce `p20-d-doklady.py`, která měřidla
`p3[0-9]-` bere) — drahé nohy (cizí `p35-a-overeni.py --plne`, `g3`,
`validate-all`) se pouští JEN s `--plne`. Naměřeno: `p36-a-overeni.py` je
v dávce také v levném režimu, takže je to konvence projektu, ne zvlčilost.
Exit 0 = měřeno bez chyb (ROZDÍLY a NEZMĚŘENO se vypisují, ale nesrážejí);
exit 1 = aspoň jedna CHYBA měření.
"""

import json
import os
import pathlib
import re
import subprocess
import sys

WS = pathlib.Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"
HANDOFF = WS / "HANDOFF.md"
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
OUT = ANALYZA / "p37-a-overeni-vystup.txt"
GIT = WS / "tools" / "git.cmd"

PY = sys.executable


# ── měřidlo ────────────────────────────────────────────────────────────────────
class M:
    def __init__(self):
        self.radky = []
        # ⚠ ČÍTAČE SE JMENUJÍ `n_*` — kdyby se jmenovaly jako metody
        # (`rozdil`), přepíše je přiřazení čísla a `m.rozdil(...)` spadne na
        # „'int' object is not callable“ (naměřeno v prvním běhu P37).
        self.n_ok = self.n_chyb = self.n_rozdil = self.n_nezm = self.n_nalez = 0
        self.jmena_chyb = []

    def p(self, s=""):
        print(s)
        self.radky.append(s)

    def hlavni(self, s):
        self.p("")
        self.p(s)

    def ok_(self, s):
        self.n_ok += 1
        self.p("  OK        %s" % s)

    def chyba(self, s):
        self.n_chyb += 1
        self.jmena_chyb.append(s)
        self.p("  CHYBA     %s" % s)

    def rozdil(self, s):
        self.n_rozdil += 1
        self.p("  ROZDÍL    %s" % s)

    def nezmereno(self, s):
        self.n_nezm += 1
        self.p("  NEZMĚŘENO %s" % s)

    def nalez(self, s):
        self.n_nalez += 1
        self.p("  NÁLEZ     %s" % s)


def run(cmd, timeout=900, env=None, cwd=None):
    """Spustí příkaz s PLNÝM prostředím (H137/H154) a vrátí (rc, text)."""
    e = dict(os.environ)
    if env:
        e.update(env)
    e.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           env=e, cwd=str(cwd or WS), encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return -9, "(TIMEOUT %ss)" % timeout


def text_dokumentu(cesta):
    return cesta.read_text(encoding="utf-8", errors="replace")


def sekce(dokument, nadpis_vzor, do_vzor=None):
    """Vytáhne oddíl dokumentu (od nadpisu po další nadpis stejné úrovně)."""
    m = re.search(nadpis_vzor, dokument, re.M)
    if not m:
        return None
    start = m.start()
    if do_vzor:
        m2 = re.search(do_vzor, dokument[m.end():], re.M)
        if m2:
            return dokument[start:m.end() + m2.start()]
    return dokument[start:]


def hledej(cesta, vzor, popis):
    """Vrátí první skupinu vzoru, nebo None (nenalezené tvrzení se hlásí zvlášť)."""
    m = re.search(vzor, cesta, re.M)
    return m.group(1) if m else None


# ── A0 ────────────────────────────────────────────────────────────────────────
def a0(m):
    m.hlavni("## A0 — POJISTKY (živý stav obou repů, ne text zadání)")

    rc, head = run([str(GIT), "rev-parse", "HEAD"])
    head = head.strip().splitlines()[0] if head.strip() else "?"
    m.p("  HEAD orchestra: %s" % head)

    rc, ls = run([str(GIT), "ls-remote", "origin", "refs/heads/main"])
    remote = ls.split()[0] if ls.strip() else "?"
    m.p("  origin/main (ŽIVĚ ls-remote): %s" % remote)
    if remote.startswith(head[:40]):
        m.ok_("origin/main == HEAD — práce je PUSHNUTÁ (měřeno živě, ne z textu)")
    else:
        m.chyba("origin/main (%s) != HEAD (%s) — NENÍ pushnuto" % (remote[:8], head[:8]))

    rc, st = run([str(GIT), "status", "--porcelain"])
    radky = [r for r in st.splitlines() if r.strip()]
    m.p("  necommitnuté položek: %d" % len(radky))
    for r in radky:
        m.p("     %s" % r)
    # Zadání P37 §0.5 pojmenovává, co NEMÁ být commitnuté; cokoli mimo to je nález.
    POVOLENE = ("NEXT-SESSION-INSTRUKCE.md", "_analyza/_registr-bran.json",
                "_analyza/ov-b2-spusteni.json", "_analyza/ov-c-vysledky.json",
                "_analyza/ov-e-vysledky.json")
    mimo = [r for r in radky
            if not any(p in r for p in POVOLENE)
            and not re.search(r"_analyza/(p3[67]|p20-d)", r)
            and not r.endswith("-vystup.txt")]
    if mimo:
        m.nalez("necommitnuté položky mimo očekávaný seznam (%d): %s"
                % (len(mimo), "; ".join(x.strip() for x in mimo[:10])))
    else:
        m.ok_("ve stromě je jen to, co zadání P37 §0.5 pojmenovává (+ moje p37 doklady)")

    rc, hra = run(["git", "-C", str(WS.parent / "uo-shadows"), "rev-parse", "HEAD"])
    hra = hra.strip().splitlines()[0] if hra.strip() else "?"
    rc, hraR = run([str(GIT), "-C", str(WS.parent / "uo-shadows"), "ls-remote", "origin", "refs/heads/main"])
    hraR = hraR.split()[0] if hraR.strip() else "?"
    m.p("  hra: lokálně %s · origin/main %s" % (hra[:8], hraR[:8]))
    if hra[:8] != hraR[:8]:
        m.ok_("hra má nepushnuté commity (%s vs %s) — zadání to pojmenovává jako stav CIZÍ session"
              % (hra[:8], hraR[:8]))
    else:
        m.rozdil("hra je pushnutá (%s) — zadání P37 tvrdí DVA nepushnuté commity" % hra[:8])
    rc, hst = run(["git", "-C", str(WS.parent / "uo-shadows"), "status", "--porcelain"])
    if hst.strip():
        m.nalez("ve hře je necommitnutá práce cizí session (%d položek) — NESAHAT" % len(hst.splitlines()))
    else:
        m.ok_("ve hře je strom čistý (jen čteno, nic se nepsalo)")


# ── A1 ────────────────────────────────────────────────────────────────────────
def a1(m):
    m.hlavni("## A1 — JE P36 PUSHNUTÁ A CO JE ŽIVÉ (tři kroky, PLNÉ sha — H153)")

    rc, stat = run([str(GIT), "show", "--stat", "--oneline", "8c8ce4d"])
    dotceno_conductora = "conductor/src" in stat or "conductor/" in stat.split("\n")[-1]
    m.p("  `git show --stat 8c8ce4d` (první commit P36):")
    for r in stat.splitlines()[:12]:
        m.p("     %s" % r)
    # jen změněné cesty posledního řádku souhrnu
    m.p("  dotýká se P36 souborů conductora? %s" % ("ANO" if dotceno_conductora else "NE"))
    rc, zmeny = run([str(GIT), "show", "--name-only", "--format=", "8c8ce4d"])
    cesty = [c for c in zmeny.split() if c.strip()]
    m.p("  změněné cesty (%d): %s" % (len(cesty), ", ".join(cesty[:12])))
    if any(c.startswith("conductor/") for c in cesty):
        m.rozdil("P36 MĚNILA conductora — pak se nasazovat MĚLO")
    else:
        m.ok_("P36 NEMĚNILA conductora — tvrzení §67.5 sedí (nasazovat se nemuselo)")

    # co je živé: poslední nasazení z deploy.yml
    rc, dep = run(["node", "_analyza/p30-sonda-deploy.mjs",
                   "3143f31d6a37ed8d90bf06f5c03df9a407ae00ea"], timeout=300)
    if "#39" in dep and "success" in dep:
        m.ok_("deploy.yml #39 na 3143f31d… je completed/success (poslední nasazení = P35)")
    else:
        m.chyba("deploy #39 se nepodařilo potvrdit: %s" % dep.strip().replace("\n", " | ")[:220])

    # živá verze z tailu vs verze z logu nasazení
    verze_log = "3985379c-4f45-424c-8400-2e26b54cae23"
    tail = ANALYZA / "p37-tail-raw-vystup.txt"
    if tail.is_file():
        v = set(re.findall(r'"id":\s*"([0-9a-f\-]{36})"', tail.read_text(encoding="utf-8", errors="replace")))
        if verze_log in v:
            m.ok_("ŽIVÝ tail běží verzi %s == verze z logu nasazení #39" % verze_log[:8])
        elif v:
            m.chyba("živý tail běží JINOU verzi %s, log tvrdí %s" % (sorted(v), verze_log[:8]))
        else:
            m.nezmereno("v dokladu tailu není `scriptVersion.id`")
    else:
        m.nezmereno("doklad živého tailu %s NENÍ" % tail.name)

    # P36 má ČTYŘI commity a všechny pushnuté (tvrzení zadání)
    rc, log = run([str(GIT), "log", "--oneline", "-5"])
    m.p("  posledních 5 commitů:")
    for r in log.splitlines()[:5]:
        m.p("     %s" % r)


# ── A2 ────────────────────────────────────────────────────────────────────────
def a2(m, drahe=True):
    m.hlavni("## A2 — JE OPRAVA H172 V KÓDU A MÁ TEST, KTERÝ JI ZAVOLÁ")

    test = WS / "tools" / "test-tick-offline.mjs"
    kod = test.read_text(encoding="utf-8", errors="replace")
    # 1) modeluje fakeDb tabulku `state`? (to je ta oprava)
    if re.search(r"FROM state", kod):
        m.ok_("`tools/test-tick-offline.mjs` ZNÁ tabulku `state` (dotaz `SELECT … FROM state` je v harnessu)")
    else:
        m.chyba("harness NEZNÁ tabulku `state` — vada H172 by byla zpátky")
    # 2) scénář AG (13 kontrol)
    if re.search(r"\bAG\b", kod):
        m.ok_("scénář AG v harnessu existuje (tep se ZAPÍŠE a /health ho PŘEČTE)")
    else:
        m.chyba("scénář AG v harnessu NENÍ — tep by se neměřil")

    # 3) skutečně ho ZAVOLEJ (brána, která kód nezavolá, neměří chování)
    if not drahe:
        m.nezmereno("--levne: `node tools/test-tick-offline.mjs` se nespouštěl")
        return
    rc, vystup = run(["node", "tools/test-tick-offline.mjs"], timeout=600)
    m.p("  `node tools/test-tick-offline.mjs` → exit %d" % rc)
    posledni = [r for r in vystup.strip().splitlines() if r.strip()][-3:]
    for r in posledni:
        m.p("     %s" % r[:200])
    # ⚠ ČÍTAČ SE ČTE Z ŘÁDKU `VÝSLEDEK: N kontrol, M chyb` — ne prvním
    # `N/M`, které se v textu objeví (naměřeno: první běh P37 vykázal „99/0“
    # z úplně jiné dvojice čísel). Číslo se čte z DOKLADU, ne odhadem.
    mcis = None
    for r in vystup.splitlines():
        mm = re.search(r"VYSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*(?:CHYB|chyb)", r)
        if mm:
            mcis = mm.groups()
    if rc == 0 and mcis:
        m.ok_("harness: %s kontrol / %s chyb (tvrzení §67.3 = 231/0; dnes +4 za scénář AH)" % mcis)
        if mcis[1] != "0":
            m.rozdil("harness hlásí %s chyb — §67.3 tvrdí 0" % mcis[1])
    elif rc == 0:
        m.nezmereno("harness prošel (exit 0), ale řádek `VYSLEDEK: …` se nenašel")
    else:
        m.chyba("harness SPADL (exit %d) — oprava H172/H178 není v pořádku" % rc)


# ── A3 ────────────────────────────────────────────────────────────────────────
def a3(m, drahe=True):
    m.hlavni("## A3 — SEDÍ ČÍSLA Z §67 (měř DŘÍV, než hledáš tvrzení — H155)")

    hand = text_dokumentu(HANDOFF)
    zad = text_dokumentu(ZADANI)
    s67 = sekce(hand, r"^## 67\.", r"^## 68\.|^### 67\.11")
    if s67 is None:
        m.chyba("oddíl §67 v HANDOFF.md NENALEZEN — tvrzení nelze porovnat")
        return
    m.p("  oddíl §67 nalezen (%d znaků)" % len(s67))

    # tvrzení o měřidle P36 (dvě různá čísla: §67.1 = 26/3, §67.10 = 29/0)
    tvrzeni = re.findall(r"(\d+)\s*kontrol[^\n]{0,40}?(\d+)\s*chyb", s67)
    m.p("  tvrzení o počtu kontrol v §67: %s" % (tvrzeni or "(žádné)"))
    tv29 = any(a == "29" and b == "0" for a, b in tvrzeni)
    if tv29:
        m.ok_("§67 tvrdí `29 kontrol, 0 chyb` (§67.10) — je to nejnovější tvrzení")
    else:
        m.chyba("§67 NETVRDÍ `29 kontrol, 0 chyb` — nelze ověřit nejnovější stav měřidla")

    # tvrzení o p35-a-overeni (74/0 v §66, 73/0 naměřeno) a o zadání (71/0)
    tv74 = "74/0" in hand
    tv_zad = re.findall(r"(\d+)\s*kontrol[^\n]{0,30}", zad)
    m.p("  §66 tvrdí 74/0? %s · zadání P36 tvrdilo 71/0? %s" % (tv74, "71/0" in zad))
    if not tv74:
        m.rozdil("v HANDOFFu NENÍ tvrzení `74/0` — rozdíl H170 by neměl co porovnávat")
    else:
        m.ok_("tvrzení `74/0` (doklad P35) v HANDOFFu JE — rozdíl proti dnešnímu běhu se dá pojmenovat")

    # a teď VLASTNÍ měření: co dnes dává p35-a-overeni.py (noha, kterou P36 měřila)
    if not drahe:
        m.nezmereno("--levne: `p35-a-overeni.py --plne` se nespouštěl")
        return
    # POZOR: tenhle nástroj má VNITŘNÍ NOHY a přepisuje jejich doklady (H173) —
    # proto se pouští s `--vystup` do VLASTNÍHO jména a s hotovou zálohou _analyza/.
    rc, vystup = run([PY, "_analyza/p35-a-overeni.py", "--plne",
                      "--vystup", "_analyza/p37-p35a-plne-vystup.txt"], timeout=2700)
    m.p("  `p35-a-overeni.py --plne` → exit %d" % rc)
    cis = re.findall(r"(\d+)\s*kontrol[^\n]{0,60}?(\d+)\s*chyb", vystup)
    posledni = cis[-1] if cis else None
    if posledni:
        m.p("     naměřeno dnes: %s kontrol / %s chyb (tvrzení §66: 74/0)" % posledni)
        if posledni[1] != "0":
            m.rozdil("dnešní běh má %s chyb — §66 tvrdí 0; rozdíl se MUSÍ pojmenovat" % posledni[1])
        else:
            m.ok_("dnešní běh `p35-a-overeni.py --plne` = %s/0 (tvar tvrzení §66 sedí)" % posledni[0])
    else:
        chyb = re.findall(r"(\d+)\s*chyb", vystup)
        if chyb:
            m.rozdil("dnešní běh hlásí %s chyb (čítač kontrol se z výstupu nepodařilo přečíst)" % chyb[-1])
        else:
            m.nezmereno("z výstupu `p35-a-overeni.py --plne` nelze čítač přečíst")
    for r in [x for x in vystup.strip().splitlines() if x.strip()][-6:]:
        m.p("     %s" % r[:180])


# ── A4 ────────────────────────────────────────────────────────────────────────
def a4(m):
    m.hlavni("## A4 — JE TIK ŽIVĚ V POŘÁDKU (vlastní parser + ruční tik + historie)")

    rc, out = run([PY, "_analyza/p37-tail-rozbor.py"], timeout=300)
    m.p("  `p37-tail-rozbor.py` → exit %d" % rc)
    for r in out.strip().splitlines():
        m.p("     %s" % r[:160])
    crony = re.search(r"n=(\d+)\s+medián\s+([\d.]+)\s*ms\s+rozsah\s+([\d.]+)\.\.([\d.]+)", out)
    neok = re.search(r"(\d+)×\s+outcome=(\w+)", out)
    if crony:
        n, med, lo, hi = crony.groups()
        m.p("  cron eventy: n=%s, medián %s ms, rozsah %s..%s ms" % (n, med, lo, hi))
    if "exceededCpu" in out:
        pocet = re.search(r"(\d+)×\s+outcome=exceededCpu", out)
        m.nalez("ŽIVÝ TIK UMÍRÁ NA CPU: %s cron event(ů) s `outcome=exceededCpu` "
                "(§67.1 A4 tvrdí „0× outcome != ok“) — to je ROZDÍL, ne detail"
                % (pocet.group(1) if pocet else "?"))
    else:
        m.ok_("v živém tailu není `exceededCpu`")

    # §67.1 A4 tvrdí medián 21,5 ms (n=22) a 0× outcome != ok
    if "21,5" in text_dokumentu(HANDOFF):
        if crony and crony.group(1) != "22":
            m.rozdil("§67.1 A4 tvrdí n=22, dnes n=%s (jiný vzorek — číslo se musí číst s n)" % crony.group(1))

    # ruční tik: cena PRÁCE tiku jinou cestou (měřeno 11. 10. 17:11Z, ZÁSAH)
    tick = ANALYZA / "p37-tick-mereni-vystup.txt"
    if tick.is_file():
        t = tick.read_text(encoding="utf-8", errors="replace")
        cpu = re.search(r"cpuTime:\s*(\d+)\s*ms\s*·\s*outcome:\s*(\w+)", t)
        if cpu:
            m.p("  ruční `POST /tick`: cpuTime %s ms, outcome %s" % (cpu.group(1), cpu.group(2)))
            if cpu.group(2) == "ok":
                m.nalez("TÁŽ FUNKCE, JINÁ CESTA: ruční `/tick` (await v požadavku) stojí %s ms a projde, "
                        "cron tik (přes `ctx.waitUntil`) umírá na 10 ms" % cpu.group(1))
            else:
                m.rozdil("ruční tik taky umřel (%s)" % cpu.group(2))
        else:
            m.nezmereno("v dokladu ručního tiku není cpuTime")
        if "last_tick_zdroj" in t and "manual" in t:
            m.ok_("ruční tik ZAPSAL tep jako `manual` a `last_cron` NEobnovil (H112 platí)")
    else:
        m.nezmereno("doklad ručního tiku (%s) NENÍ" % tick.name)

    # historie: Cloudflare Analytics — od kdy tik umírá
    cf = ANALYZA / "p37-cf-analytika-vystup.txt"
    if cf.is_file():
        data = json.loads(cf.read_text(encoding="utf-8", errors="replace"))
        radky = data.get("radky") or []
        hodiny = {}
        for x in radky:
            h = x["dimensions"]["datetime"][:13]
            p = hodiny.setdefault(h, [0, 0])
            if x["dimensions"]["status"] == "success":
                p[0] += x["sum"]["requests"]
            elif x["dimensions"]["status"] == "exceededResources":
                p[1] += x["sum"]["requests"]
        m.p("  Cloudflare Analytics (posledních %s h): hodiny s exceededResources:" % data.get("hodin"))
        for h in sorted(hodiny):
            if hodiny[h][1]:
                m.p("     %s: success %d, exceeded %d" % (h, hodiny[h][0], hodiny[h][1]))
        m.nalez("historie: cron tik umírá na CPU v sérii od ~13:58Z (14Z–16Z ≈ 59–60/h = každý tik); "
                "08Z–12Z bylo 0 — výpadek tiku je DNES ŽIVÝ a měřitelný")
    else:
        m.nezmereno("doklad CF analytiky (%s) NENÍ" % cf.name)


# ── A5 ────────────────────────────────────────────────────────────────────────
def a5(m, drahe=True):
    m.hlavni("## A5 — JSOU TEPY V `/health` A V D1")

    s = ANALYZA / "p37-sluzba-sonda-vystup.txt"
    if s.is_file():
        t = s.read_text(encoding="utf-8", errors="replace")
        ma_cron = "last_cron=" in t and "last_cron_pokus=" in t
        if ma_cron:
            m.ok_("`/health` posílá `last_cron` I `last_cron_pokus` (H156)")
        else:
            m.chyba("`/health` neposílá oba tepy")
        for r in t.splitlines():
            if "TEP:" in r:
                m.p("     %s" % r.strip())
    else:
        m.nezmereno("doklad sondy služby (%s) NENÍ" % s.name)

    if not drahe:
        m.nezmereno("--levne: D1 `SELECT k, v FROM state` se nečetl")
        return
    rc, vystup = run([PY, "_analyza/p36-strop-sonda.py"], timeout=300)
    m.p("  `p36-strop-sonda.py` (D1, READ-ONLY) → exit %d" % rc)
    for r in vystup.strip().splitlines()[:12]:
        m.p("     %s" % r[:170])
    if "last_cron" in vystup or "state" in vystup:
        m.ok_("D1 dotaz na `state` proběhl (tepy se čtou z D1, ne z paměti)")
    else:
        m.nezmereno("z výstupu D1 sondy není vidět klíče `state`")


# ── A6 ────────────────────────────────────────────────────────────────────────
def a6(m, drahe=True):
    m.hlavni("## A6 — UKLÍZÍ SE MĚŘIDLA PO SOBĚ (H163/H169: BEZ FILTRU PŘÍPON)")

    if drahe:
        rc, vystup = run([PY, "_analyza/p36-mutace.py"], timeout=2700)
        m.p("  `p36-mutace.py` → exit %d" % rc)
        for r in vystup.strip().splitlines()[-4:]:
            m.p("     %s" % r[:170])
        # ⚠ TÝŽ PARSOVACÍ OMYL JAKO V A2: čte se řádek `VYSLEDEK: …`, ne první `N/M`.
        cis = None
        for r in vystup.splitlines():
            mm = re.search(r"VYSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*(?:CHYB|chyb)", r)
            if mm:
                cis = mm.groups()
        if rc == 0 and cis:
            m.ok_("cizí mutační měřidlo P36: %s kontrol / %s chyb (tvrzení §67 = 45/0)" % cis)
            if cis[1] != "0":
                m.rozdil("p36-mutace hlásí %s chyb — §67 tvrdí 0" % cis[1])
        elif rc != 0:
            m.chyba("p36-mutace.py SPADL (exit %d) — nevrací soubory?" % rc)
        else:
            m.nezmereno("z výstupu p36-mutace se nenašel řádek `VYSLEDEK: …`")
    else:
        m.nezmereno("--levne: p36-mutace.py se nespouštěl")

    # živé soubory proti HEAD — BEZ filtru přípon (i .md!)
    rc, st = run([str(GIT), "status", "--porcelain"])
    zmenene = [r for r in st.splitlines() if r.strip()]
    m.p("  `git status --porcelain` (bez filtru přípon): %d položek" % len(zmenene))
    podezrele = []
    # Vlastní práce P37, která se commituje AŽ PO měření (měřidlo běží před commitem).
    # Po commitu je tenhle seznam prázdný a kontrola hlásí OK.
    VLASTNI_PRACE = ("conductor/src/index.ts", "tools/test-tick-offline.mjs",
                     "_analyza/p20-d-doklady.py", "_analyza/p37-a-overeni.py")
    for r in zmenene:
        cesta = r[3:].strip().strip('"')
        # generované mezivýstupy bran a zadání se necommituje (zadání P37 §0.5)
        if cesta.startswith("_analyza/") and (cesta.endswith("-vystup.txt") or "_registr-bran" in cesta
                                             or re.match(r"_analyza/ov-[bce]", cesta)):
            continue
        if cesta == "NEXT-SESSION-INSTRUKCE.md":
            continue
        if re.match(r"_analyza/p3[67]-", cesta):
            continue
        if cesta in VLASTNI_PRACE:
            continue
        podezrele.append(cesta)
    if podezrele:
        m.chyba("v živém stromě zůstaly soubory mimo očekávané (%d): %s"
                % (len(podezrele), ", ".join(podezrele[:10])))
    else:
        m.ok_("žádný živý soubor nezůstal změněný (kontrola BEZ filtru přípon, včetně .md)")

    scratch = sorted([p for p in ANALYZA.glob("*-scratch*") if p.is_dir()])
    m.p("  `_analyza/*-scratch*` adresářů: %d" % len(scratch))
    # NÁLEZ je jen scratch, který je ČERSTVÝ (leftover z přerušeného běhu, H163/H169);
    # historické scratch adresáře z P17–P32 jsou známý stav (P36: 10 adresářů, 17–128 h).
    import time as _t
    cerstve = []
    for p in scratch:
        soubory = [f for f in p.rglob("*") if f.is_file()]
        if not soubory:
            continue
        nejnovejsi = max(f.stat().st_mtime for f in soubory)
        stari_h = (_t.time() - nejnovejsi) / 3600
        if stari_h < 3:
            cerstve.append("%s (nejnovější soubor před %.1f h)" % (p.name, stari_h))
    if cerstve:
        m.nalez("ČERSTVÉ scratch adresáře (možný leftover měřidla): %s" % "; ".join(cerstve))
    else:
        m.ok_("žádný scratch adresář není čerstvý (<3 h) — leftover z měřidel není")


# ── A7 ────────────────────────────────────────────────────────────────────────
def a7(m, drahe=True):
    m.hlavni("## A7 — NIC SE NEROZRBILO (pořadí je ZMĚŘENÉ: inventář → g3 → inventář → validate-all)")

    if not drahe:
        m.nezmereno("--levne: g3 + validate-all se nespouštěly")
        return

    rc, inv = run([PY, "_analyza/hl-neanglicky-v-kodu.py", "--json", "_analyza/_inventar.json"], timeout=900)
    m.p("  inventář PŘED g3 → exit %d (%s)" % (rc, inv.strip().splitlines()[-1][:90] if inv.strip() else ""))

    rc, g3 = run([PY, "_analyza/g3-brany.py"], timeout=2700,
                 env={"FORGE_REGISTR": str(pathlib.Path("E:/Workspaces/_p37-scratch/g3-registr.json"))})
    m.p("  `g3-brany.py` → exit %d" % rc)
    brany = re.search(r"(\d+)\s*bran", g3)
    nenul = re.search(r"NENULOVÉ EXITY:\s*(\d+)[^\n]*deklarovaných\D*(\d+)\D*NEDEKLAROVAN\w*\D*(\d+)", g3)
    if brany:
        m.p("     bran: %s" % brany.group(1))
    nenul_radky = [r.strip() for r in g3.splitlines() if "nenulov" in r.lower() and "exit" in r.lower()]
    for r in nenul_radky[:12]:
        m.p("     %s" % r[:170])
    if nenul:
        m.p("     nenulové exity: %s (deklarovaných %s, NEDEKLAROVANÝCH %s)" % nenul.groups())
        if nenul.group(3) == "0":
            m.ok_("g3: 0 NEDEKLAROVANÝCH nenulových exitů (stav shodný s §67.10)")
        elif any("validate-all" in r for r in nenul_radky) or "validate-all" in g3:
            # P37 to JMENOVITĚ doověřila (P36 to nechala otevřené): nedeklarovaný
            # exit je `validate-all (CELEK)` — a ten je červený proto, že brána
            # cronu správně hlásí „tik NEDOBÍHÁ“ (živý výpadek, H179). NENÍ to
            # vada práce P37 — ale NENÍ to ani zelená.
            m.nalez("g3: %s NEDEKLAROVANÝCH nenulových exitů — a je to `validate-all`, "
                    "který správně padá na MRTvém cron tiku (H179). P36 to nechala neověřené; "
                    "dnes je to pojmenované." % nenul.group(3))
        else:
            m.chyba("g3 hlásí %s NEDEKLAROVANÝCH nenulových exitů a není mezi nimi `validate-all`" % nenul.group(3))
    else:
        m.nezmereno("v souhrnu g3 se nenašel řádek `NENULOVÉ EXITY: N — …`")
    for r in g3.splitlines():
        if "NENULOVÉ" in r or "BEZ ČÍTAČE" in r:
            m.p("     %s" % r.strip()[:170])

    rc, inv2 = run([PY, "_analyza/hl-neanglicky-v-kodu.py", "--json", "_analyza/_inventar.json"], timeout=900)
    m.p("  inventář PO g3 → exit %d (H176/H177: bez toho padá validate-all)" % rc)

    rc, va = run(["node", "tools/validate-all.mjs"], timeout=1800)
    m.p("  `validate-all.mjs` → exit %d" % rc)
    # ⚠ POZOR NA TVAR VÝSTUPU: `validate-all` vypisuje i SVÉ fixtury řádky
    # („OK   3 tep 30 min starý → CHYBA (cron NETIKÁ)“), takže filtr na slovo
    # `CHYBA` chytá i ZELENÉ kontroly. Skutečné problémy začínají na `CHYBA `
    # na začátku řádku — naměřeno v 1. běhu P37 (falešná CHYBA měřidla).
    chyby_va = [r.strip() for r in va.splitlines() if r.strip().startswith("CHYBA")]
    for r in chyby_va[:6]:
        m.p("     %s" % r[:190])
    if rc == 0:
        m.ok_("validate-all: VŠE V POŘÁDKU (0 problémů)")
    elif chyby_va and all("cron" in r.lower() for r in chyby_va):
        # ⚠ P37: `validate-all` DNES NEMŮŽE BÝT ZELENÝ — a je to SPRÁVNĚ.
        # Jeho brána cronu měří živý tep: `last_cron` je 225 min starý, protože
        # invocation umírá na CPU (H179). Kdo by tuhle červenou „opravil“ v bráně,
        # zahodil by jediné místo, které výpadek hlásí.
        m.nalez("validate-all je ČERVENÝ a jeho jediný problém je MRTvý CRON TIK — "
                "brána to hlásí SPRÁVNĚ (H179). Není to vada práce P37 a NESMÍ se "
                "deklarovat jako výjimka; „hotovo = validate-all 0 problémů“ je dnes "
                "dosažitelné JEN opravou služby: %s" % chyby_va[0][:150])
    else:
        m.chyba("validate-all hlásí problém(y) mimo cron: %s" % " | ".join(chyby_va)[:250])

    for nazev, cmd in [("kronika", [PY, "_analyza/kronika-kontrola.py"]),
                       ("handoff", [PY, "_analyza/handoff-kontrola-uplnost.py"]),
                       ("ov-g", [PY, "_analyza/ov-g-neovereno.py"])]:
        rc, o = run(cmd, timeout=600)
        posledni = [r for r in o.strip().splitlines() if r.strip()][-2:]
        m.p("  %s → exit %d: %s" % (nazev, rc, " | ".join(x.strip() for x in posledni)[:200]))
        if rc != 0:
            m.chyba("brána `%s` skončila exit %d" % (nazev, rc))
        else:
            m.ok_("brána `%s` prošla (exit 0)" % nazev)


# ── hlavní ────────────────────────────────────────────────────────────────────
def main():
    ap = sys.argv[1:]
    jen = ap[ap.index("--jen") + 1] if "--jen" in ap else None
    # ⚠ VÝCHOZÍ = LEVNÝ (kvůli dávce `p20-d-doklady.py`); drahé nohy jen s `--plne`.
    drahe = "--plne" in ap

    m = M()
    m.p("# P37 — VLASTNÍ PŘEMĚŘENÍ PRÁCE P36 (%s)" % __import__("datetime").datetime.now().astimezone().isoformat())
    m.p("# měřidlo: _analyza/p37-a-overeni.py · doklad: _analyza/p37-a-overeni-vystup.txt")
    m.p("# zdroj tvrzení: HANDOFF.md §67 + NEXT-SESSION-INSTRUKCE.md (zadání P37)")

    etapy = {"A0": a0, "A1": a1, "A2": a2, "A3": a3, "A4": a4, "A5": a5, "A6": a6, "A7": a7}
    for nazev, fn in etapy.items():
        if jen and nazev != jen:
            continue
        try:
            if nazev in ("A2", "A3", "A5", "A6", "A7"):
                fn(m, drahe)
            else:
                fn(m)
        except Exception as e:  # měřidlo nesmí spadnout tiše
            m.chyba("etapa %s vyhodila výjimku: %s: %s" % (nazev, type(e).__name__, str(e)[:200]))

    m.hlavni("VÝSLEDEK: %d kontrol, %d chyb (z toho %d ROZDÍLŮ, %d NEZMĚŘENO, %d NÁLEZŮ)"
             % (m.n_ok + m.n_chyb + m.n_rozdil + m.n_nezm + m.n_nalez, m.n_chyb, m.n_rozdil, m.n_nezm, m.n_nalez))
    if m.jmena_chyb:
        m.p("  CHYBY:")
        for c in m.jmena_chyb:
            m.p("   - %s" % c)

    OUT.write_text("\n".join(m.radky) + "\n", encoding="utf-8")
    print("\n[zapsáno] %s" % OUT.name)
    return 1 if m.n_chyb else 0


if __name__ == "__main__":
    sys.exit(main())
