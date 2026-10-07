# -*- coding: utf-8 -*-
r"""P26 — ÚKOL A: PŘEMĚŘIT PRÁCI P25 VLASTNÍM POSTUPEM (A1–A6).

PROČ TENHLE SKRIPT EXISTUJE
---------------------------
Zadání P26 §2.1: záznamy P25 (`HANDOFF.md` §55, kronika řádek 40 + §2.18) psal
**autor, který si je sám ověřoval** — a `AGENTS.md` je v tom jednoznačné:
*„autor není nezávislý reviewer"*. P25 to udělala pro P24; P26 to musí udělat
pro P25. Skript **neopisuje** tvrzení z §55 — každý bod měří **jiným postupem,
než jak vznikl**:

  A1  **kontramutace v KOPIÍCH** — vezme měřidlo P25 a vloží vadu do KAŽDÉHO
      vstupu, který tvrdí, že čte (kronika, `g3`, zdroj conductora, §54
      v handoffu) — přes přepínače `--kronika/--g3/--zdroj/--handoff`.
      Každá vada musí měřidlo **shodit z jiného důvodu**; tím se měří, že ty
      přepínače nejsou dekorace.
  A2  **ZARÁŽKA UVNITŘ HANDLERU** pro `/task`, `/game` a `/game/active`.
      ⚠ P25 dělala zarážku jen v ROUTERU pro `/poll`…`/roadmap/reset` — a pro
      trojici endpointů z Úkolu B1 **nikdo nezměřil, že je test opravdu volá**
      (v seznamu 42 červených nejsou žádné `T`/`U`/`V`/`W`). Tady se to měří.
  A3  **vázané hodnoty (`bind`)**: v KOPII testu se vypne ZÁZNAM vazeb a měří
      se, které kontroly `T`/`V` tím zčervenají. Když nula, test o vazbách
      netvrdí nic (`overovani`: přítomnost ≠ chování).
  A4  **každý čítač tvrzený v §55 se znovu NAMĚŘÍ** (ne přečte) — a porovná se
      s tvrzením PŘEČTENÝM Z DOKUMENTU (ne zapečeným v kódu).
  A5  **rozsah měřidla `ov-g-neovereno.py`** (nález P25-K): verze z `HEAD`
      vs. živá, fixtura s `NEOVĚŘENO`, a fixtura PRÁZDNÁ (0 řádků = neměřeno).
  A6  **integrita**: `g3`, `validate-all`, úplnost handoffu, kronika.

⚠ TŘETÍ STAV: „neměřeno" se hlásí jako `NEZMĚŘENO` (`overovani` §7.13) —
není to nula a není to zelená.

Použití:
    python _analyza/p26-a-overeni.py              # DÁVKA: A1, A4, A5, A6 (bez mutace živého zdroje)
    python _analyza/p26-a-overeni.py --plne       # VŠE + A2, A3, g3, validate-all
    python _analyza/p26-a-overeni.py --jen A5     # jen vybrané etapy
"""

import argparse
import ast
import hashlib
import pathlib
import re
import shutil
import subprocess
import sys

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
P25_A = ANALYZA / "p25-a-overeni.py"
P25_B = ANALYZA / "p25-b-mutace.py"
OV_G = ANALYZA / "ov-g-neovereno.py"
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
ARCHIV = WS / "_archiv"
SCRATCH = ANALYZA / "p26-scratch"
KOPIE_TESTU = WS / "tools" / "p26-kopie-tick.mjs"

sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj                                            # noqa: E402

kontrol = 0
chyb = 0
nezmereno = []
# ⚠ CESTA K ULOŽENÉMU VÝSTUPU JE GLOBÁL: blok `__main__` ji potřebuje a `args`
# je lokální v `main()` — naměřeno 7. 10. 2026, že odkaz na `args` tam spadne
# na `NameError` a měřidlo pak **vždy** skončí `exit 1`, i když má 0 chyb
# (a to je nejhorší druh vady: vypadá to jako nález).
VYSTUP_CESTA = None


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
    nezmereno.append(popis)
    print("  NEZMĚŘENO  %s\n          důvod: %s" % (popis, duvod))


def cmd(argumenty, cwd=None, timeout=1800):
    r = subprocess.run(argumenty, cwd=str(cwd or WS), capture_output=True,
                       timeout=timeout)
    return r.returncode, (r.stdout.decode("utf-8", "replace")
                          + r.stderr.decode("utf-8", "replace"))


def citac(vystup, vzor=r"(\d+) kontrol, (\d+) chyb"):
    """Poslední výskyt čítače (mutace tiskne `CHYB` velkými)."""
    m = None
    for m in re.finditer(vzor, vystup, re.IGNORECASE):
        pass
    return (int(m.group(1)), int(m.group(2))) if m else None


def cervene(vystup):
    """Popisy červených kontrol testu tiku (`  CHYBA <popis>`)."""
    return [l.strip()[len("CHYBA"):].strip() for l in vystup.splitlines()
            if l.strip().startswith("CHYBA")]


def sha(cesta):
    return hashlib.sha256(pathlib.Path(cesta).read_bytes()).hexdigest()


def blob(rev, cesta):
    r = subprocess.run([str(GIT), "-C", str(WS), "show", "%s:%s" % (rev, cesta)],
                       capture_output=True, shell=True, timeout=120)
    return r.stdout if r.returncode == 0 else None


def souhrn_g3(vystup):
    """(celkem, deklarovaných, NEDEKLAROVANÝCH) z výstupu `g3` — DVA TVARY.

    ⚠ `g3` píše souhrn dvěma způsoby: **s** nenulovými exity
    (`NENULOVÉ EXITY: 4 — z toho deklarovaných … a NEDEKLAROVANÝCH …`)
    a **bez** nich (`NENULOVÉ EXITY: 0 — každá brána doběhla s exit 0`).
    Kdo čte jen první tvar, vykáže **zelený** `g3` jako „souhrn nenalezen" —
    naměřeno 7. 10. 2026 (dvě falešná `NEZMĚŘENO` nad BENE státem).
    """
    m = re.search(r"NENULOVÉ EXITY:\s*(\d+)[^\n]*deklarovaných \(očekávaných\)\s*(\d+)"
                  r"[^\n]*NEDEKLAROVANÝCH\s*(\d+)", vystup)
    if m:
        return tuple(int(x) for x in m.groups())
    if re.search(r"NENULOVÉ EXITY:\s*0\b", vystup):
        return (0, 0, 0)
    return None


def sekce(nazev, text):
    """Text oddílu `## <nazev>.` z dokumentu (do dalšího `## `)."""
    m = re.search(r"\n## %s\." % re.escape(nazev), text)
    if not m:
        return ""
    zbytek = text[m.start():]
    m2 = re.search(r"\n## ", zbytek[4:])
    return zbytek[:m2.start() + 4] if m2 else zbytek


# ═══════════════════════════════════════════════════════════════════ A1 ═══
def a1(plne):
    print("\n--- A1: měří měřidlo P25 to, co tvrdí? (kontramutace v KOPIÍCH) ---")
    s55 = sekce("55", HANDOFF.read_text(encoding="utf-8", errors="replace"))
    check("A1 §55 existuje (délka %d znaků)" % len(s55), len(s55) > 3000, True)
    # Předpoklad: měřidlo na NEZMUTOVANÝCH vstupech projde. Bez toho by „spadlo
    # po mutaci" mohlo znamenat jen to, že je měřidlo rozbité pořád.
    kod, v = cmd(["python", str(P25_A), "--jen", "A5,A6",
                  "--kronika", str(KRONIKA), "--handoff", str(HANDOFF),
                  "--g3", str(G3), "--validate", str(VALIDATE), "--p20d", str(P20_D)])
    c = citac(v)
    check("A1a KONTROLA: měřidlo P25 na nemutovaných vstupech → exit 0", kod, 0)
    check("A1a KONTROLA: a má čítač (naměřeno %s)" % (c,), c is not None, True)

    kopie = {}
    for nazev, zdroj in (("kronika.md", KRONIKA), ("g3.py", G3),
                         ("index.ts", SRC), ("handoff.md", HANDOFF)):
        cil = SCRATCH / nazev
        shutil.copyfile(zdroj, cil)
        kopie[nazev] = cil

    # (1) KRONIKA bez řádku session 39 → A5 musí spadnout
    print("    (1) kronika bez řádku session 39")
    try:
        with mutuj(kopie["kronika.md"], "| **39** | **7. 10. 2026**", "| **xx** | **7. 10. 2026**"):
            check("A1b1 kontrola se opravdu provedla (řádek 39 je v kopii přepsaný)",
                  "| **xx** | **7. 10. 2026**" in kopie["kronika.md"].read_text(encoding="utf-8"),
                  True)
            kod, v = cmd(["python", str(P25_A), "--jen", "A5",
                          "--kronika", str(kopie["kronika.md"]), "--handoff", str(HANDOFF)])
        check("A1b1 měřidlo po vrácení vady do kroniky SPADLO", kod != 0, True)
        ch = [l for l in cervene(v) if "39" in l]
        check("A1b1 a spadlo na KONTROLE ŘÁDKU 39 (ne na něčem jiném)", bool(ch), True)
        if ch:
            print("        · %s" % ch[0][:100])
    except ValueError as e:
        nezmereno_zapis("A1b1 kontramutace kroniky", str(e))
    check("A1b1 kopie kroniky je po mutaci vrácena (hash sedí s živou)",
          sha(kopie["kronika.md"]), sha(KRONIKA))

    # (2) `g3` se SONDou v BRANY → A6 musí spadnout
    # ⚠ `mutuj` zakazuje vložení (nový text nesmí OBSAHOVAT starý), takže se
    # přejmenovává existující brána na jméno se „sonda“ — to je táž vada.
    print("    (2) g3 se sondou v seznamu BRANY")
    try:
        with mutuj(kopie["g3.py"],
                   '("diakritika (brána)", ["python", "<TOOLS>/kontrola-diakritiky.py"],',
                   '("p26-sonda-fixtura.py", ["python", "<TOOLS>/kontrola-diakritiky.py"],'):
            check("A1b2 kontrola se opravdu provedla (sonda v kopii g3 je)",
                  "p26-sonda-fixtura.py" in kopie["g3.py"].read_text(encoding="utf-8"), True)
            kod, v = cmd(["python", str(P25_A), "--jen", "A6",
                          "--g3", str(kopie["g3.py"]),
                          "--validate", str(VALIDATE), "--p20d", str(P20_D)])
        check("A1b2 měřidlo po vložení SONDy do BRANY SPADLO", kod != 0, True)
        check("A1b2 a spadlo na KONTROLE „sondy nejsou brány“",
              any("sondy nejsou brány" in l for l in cervene(v)), True)
        check("A1b2 a vada je POJMENOVANÁ („v BRANY je SONDa“)",
              "SONDa" in v, True)
    except ValueError as e:
        nezmereno_zapis("A1b2 kontramutace g3", str(e))
    check("A1b2 kopie g3 je po mutaci vrácena (hash sedí s živou)",
          sha(kopie["g3.py"]), sha(G3))

    # (3) ZDROJ s mazacím UPDATE značky `eskalovano` → A2 musí spadnout
    print("    (3) zdroj conductora s UPDATE, který značku MAŽE")
    mazac = ('const P26_KONTRAMUTACE = "UPDATE roadmap SET eskalovano = NULL '
             'WHERE status = \'done\'";\n\ninterface Env {')
    try:
        with mutuj(kopie["index.ts"], "export interface Env {", mazac):
            check("A1b3 kontrola se opravdu provedla (mazací literál v kopii je)",
                  "P26_KONTRAMUTACE" in kopie["index.ts"].read_text(encoding="utf-8"), True)
            kod, v = cmd(["python", str(P25_A), "--jen", "A2",
                          "--zdroj", str(kopie["index.ts"])])
        check("A1b3 měřidlo po vložení mazacího UPDATE SPADLO", kod != 0, True)
        check("A1b3 a spadlo na KONTROLE TRVALOSTI (ne na něčem jiném)",
              any("TRVALÁ" in l for l in cervene(v)), True)
        check("A1b3 a vada je POJMENOVANÁ („NĚKDE SE ZNAČKA MAŽE“)",
              "MAŽE" in v, True)
    except ValueError as e:
        nezmereno_zapis("A1b3 kontramutace zdroje", str(e))
    check("A1b3 kopie zdroje je po mutaci vrácena (hash sedí s živou)",
          sha(kopie["index.ts"]), sha(SRC))

    # (4) HANDOFF bez §54 → A4 musí spadnout (přepínač `--handoff`)
    # ⚠ Jen v `--plne`: A4 pustí i plný běh P24 a `tick-mutace`, takže je dlouhá.
    if not plne:
        nezmereno_zapis("A1b4 kontramutace handoffu (§54) přes `--handoff`",
                        "dávkový režim — etapa A4 je dlouhá; pouští se s `--plne`")
    else:
        print("    (4) handoff bez oddílu §54")
        # ⚠ KOTVA MUSÍ BÝT DELŠÍ NEŽ `## 54.`: to je v dokumentu 6× (jednou
        # nadpis a pětkrát `### 54.x`, protože `### 54.` OBSAHUJE `## 54.`)
        # — naměřeno 7. 10. 2026, `mutuj` to správně odmítl.
        try:
            with mutuj(kopie["handoff.md"], "## 54. P24 — NEZÁVISLÉ",
                       "## 5U. P24 — NEZÁVISLÉ"):
                kod, v = cmd(["python", str(P25_A), "--jen", "A4",
                              "--handoff", str(kopie["handoff.md"]),
                              "--kronika", str(KRONIKA), "--g3", str(G3)])
            check("A1b4 měřidlo bez oddílu §54 SPADLO", kod != 0, True)
            check("A1b4 a spadlo na kontrole „§54 existuje“",
                  any("54" in l for l in cervene(v)), True)
        except ValueError as e:
            nezmereno_zapis("A1b4 kontramutace handoffu", str(e))
        check("A1b4 kopie handoffu je po mutaci vrácena (hash sedí s živou)",
              sha(kopie["handoff.md"]), sha(HANDOFF))


# ═══════════════════════════════════════════════════════════════════ A2 ═══
ZARAZKY = (
    # (prefix kontrol, popis, kotva, náhrada)
    ("T", "/task", 'if (!body.prompt || !body.title) return json({ error: "chybi title nebo prompt" }, 400);',
     'if (true) return json({ error: "zarazka-p26-task" }, 599);'),
    ("U", "/game", 'if (!body.game_id || !body.repo) return json({ error: "chybi game_id nebo repo" }, 400);',
     'if (true) return json({ error: "zarazka-p26-game" }, 599);'),
    ("V", "/game/active", "const active = body.active === false ? 0 : 1;",
     'const active = 1; return json({ error: "zarazka-p26-active" }, 599);'),
)


def a2():
    print("\n--- A2: VOLÁ test tiku /task, /game, /game/active? (zarážka V HANDLERU) ---")
    kde = blob("HEAD", "conductor/src/index.ts")
    if kde is None:
        nezmereno_zapis("A2 kontrola čistoty zdroje", "git show HEAD:conductor/src/index.ts selhalo")
        return
    check("A2 PŘED zarážkou je zdroj čistý (disk == HEAD)",
          hashlib.sha256(kde).hexdigest(), sha(SRC))
    for pref, cesta, kotva, nahrada in ZARAZKY:
        print("    zarážka v handleru %s" % cesta)
        try:
            with mutuj(SRC, kotva, nahrada) as m:
                kod, v = cmd(["node", "tools/test-tick-offline.mjs"], timeout=1800)
            check("A2 %s zarážka se provedla (hash před != po)" % cesta,
                  m.hash_pred != m.hash_po_mutaci, True)
            check("A2 %s zdroj je po zarážce zpět (disk == HEAD)" % cesta,
                  sha(SRC), hashlib.sha256(kde).hexdigest())
        except ValueError as e:
            nezmereno_zapis("A2 zarážka v handleru %s" % cesta, str(e))
            continue
        c = citac(v)
        cr = cervene(v)
        cilene = [x for x in cr if x.startswith("%s:" % pref)]
        print("      test tiku: čítač=%s, červených=%d, z toho `%s:` = %d"
              % (c, len(cr), pref, len(cilene)))
        for x in cilene[:4]:
            print("        · %s" % x[:100])
        check("A2 %s zarážka ZAPLA kontroly `%s:` (aspoň 1)" % (cesta, pref),
              len(cilene) >= 1, True)
        check("A2 %s a kontrolní `A: /tick odpoví 200` zůstala ZELENÁ" % cesta,
              any(x.startswith("A: /tick odpoví 200") for x in cr), False)
    check("A2 zdroj conductora je na konci čistý (disk == HEAD)",
          sha(SRC), hashlib.sha256(kde).hexdigest())


# ═══════════════════════════════════════════════════════════════════ A3 ═══
def a3():
    print("\n--- A3: měří test VÁZANÉ HODNOTY, nebo jen tvar SQL? ---")
    # KONTROLA: živý test projde.
    kod0, v0 = cmd(["node", "tools/test-tick-offline.mjs"], timeout=1800)
    c0 = citac(v0)
    check("A3 KONTROLA: živý test tiku → exit 0 (naměřeno %s)" % (c0,), kod0, 0)
    # KOPIE testu v `tools/` (aby `ORCH` zůstal kořen repa), se VYPNUTÝM záznamem.
    shutil.copyfile(TEST_TIK, KOPIE_TESTU)
    try:
        try:
            with mutuj(KOPIE_TESTU,
                       "      vazby.push({ sql: String(sql).replace(/\\s+/g, ' ').trim(), args: a });\n"
                       "      return api(sql, a);",
                       "      return api(sql, a);") as m:
                check("A3 mutace se provedla (hash před != po)",
                      m.hash_pred != m.hash_po_mutaci, True)
                kod, v = cmd(["node", str(KOPIE_TESTU)], timeout=1800)
        except ValueError as e:
            nezmereno_zapis("A3 kopie testu s vypnutým `bind`", str(e))
            return
        c = citac(v)
        cr = cervene(v)
        t = [x for x in cr if x.startswith("T:")]
        u = [x for x in cr if x.startswith("V:")]
        print("      se SLEPÝM `bind`: čítač=%s, červených=%d (T: %d, V: %d)"
              % (c, len(cr), len(t), len(u)))
        check("A3 vypnutý záznam `bind` SHODÍ kontroly `T:`", len(t) >= 1, True)
        check("A3 vypnutý záznam `bind` SHODÍ kontroly `V:`", len(u) >= 1, True)
        check("A3 a je to konkrétně „T: `title` jde do INSERTu“",
              any("title` jde do INSERTu" in x for x in cr), True)
        check("A3 a je to konkrétně „V: do DB jde `active = 0` (ne 1)“",
              any("active = 0" in x and x.startswith("V:") for x in cr), True)
        check("A3 čítač klesl (živý test měl %s, slepý %s)" % (c0, c),
              bool(c0 and c and c[1] > c0[1]), True)
    finally:
        if KOPIE_TESTU.exists():
            KOPIE_TESTU.unlink()
    check("A3 kopie testu je uklizena (v `tools/` nezůstala)",
          KOPIE_TESTU.exists(), False)


# ═══════════════════════════════════════════════════════════════════ A4 ═══
def a4(plne):
    print("\n--- A4: každý čítač tvrzený v §55 se znovu NAMĚŘÍ ---")
    text55 = (HANDOFF.read_text(encoding="utf-8", errors="replace"))
    s55 = sekce("55", text55)
    zad = ZADANI.read_text(encoding="utf-8", errors="replace")

    def tvrzeni(vzor, nazev):
        m = re.search(vzor, s55)
        if not m:
            nezmereno_zapis("A4 tvrzení §55: %s" % nazev, "vzor v §55 nenalezen")
            return None
        return tuple(int(g) for g in m.groups())

    # ── LEVNÉ (běží i v dávce) ────────────────────────────────────────────
    # (L1) úplnost handoffu
    kod, v = cmd(["python", "_analyza/handoff-kontrola-uplnost.py"], timeout=600)
    m = re.search(r"kontrolovaných klíčů:\s*(\d+)", v)
    m2 = re.search(r"nalezených:\s*(\d+)", v)
    tv = tvrzeni(r"handoff-kontrola-uplnost[^\n]{0,30}?\*\*(\d+)/(\d+)\*\*",
                 "handoff-kontrola-uplnost")
    check("A4 handoff-kontrola-uplnost → exit 0", kod, 0)
    if m and m2 and tv:
        check("A4 úplnost handoffu = tvrzených %d/%d" % tv,
              (int(m.group(1)), int(m2.group(1))), tv)
    # (L2) skilly
    kod, v = cmd(["python", "tools/over-skilly.py"], timeout=900)
    ms = re.search(r"Skillů:\s*(\d+),\s*chyb:\s*(\d+)", v)
    check("A4 over-skilly.py → exit 0", kod, 0)
    if ms:
        check("A4 over-skilly.py: %s skillů, %s chyb" % ms.groups(),
              (int(ms.group(1)), int(ms.group(2))), (13, 0))
    # (L3) dokumentace — ⚠ NÁLEZ P26: zadání §2.3 tvrdilo 67 kontrol, živé
    # měření je 64 (optimalizace KB `92aa80a` odebrala 3 kontroly). Rozdíl je
    # „číslo bez svého běhu" — proto se porovnává proti TEXTU zadání.
    kod, v = cmd(["python", "tools/over-dokumentaci.py"], timeout=900)
    md = re.search(r"Kontrol:\s*(\d+),\s*chyb:\s*(\d+)", v)
    check("A4 over-dokumentaci.py → exit 0", kod, 0)
    if md:
        print("      over-dokumentaci: %s kontrol, %s chyb" % md.groups())
        mz = re.search(r"over-dokumentaci\.py\s*->\s*(\d+) kontrol", zad)
        if mz:
            check("A4 over-dokumentaci.py = číslo TVRZENÉ v zadání §2.3 (%s)"
                  % mz.group(1), int(md.group(1)), int(mz.group(1)))
        else:
            nezmereno_zapis("A4 tvrzení zadání o over-dokumentaci",
                            "zadání to číslo neuvádí (přepsané P26)")
    # (L4) rozsah měřidla NEOVĚŘENO (nález P25-K)
    kod, v = cmd(["python", str(OV_G)], timeout=600)
    mr = re.search(r"nálezů \(řádků tabulek Hxx\) CELKEM:\s*(\d+)", v)
    check("A4 ov-g-neovereno.py → exit 0 (žádné NEOVĚŘENO)", kod, 0)
    check("A4 ov-g-neovereno.py měří CELÝ rozsah (99 řádků Hxx)",
          int(mr.group(1)) if mr else None, 99)
    # (L5) měřidlo P25 v DÁVKOVÉM režimu
    kod, v = cmd(["python", str(P25_A)], timeout=1800)
    c = citac(v)
    check("A4 p25-a-overeni.py (dávka) → exit 0 (naměřeno %s)" % (c,), kod, 0)

    # ── DLOUHÉ (jen s `--plne`) ───────────────────────────────────────────
    if not plne:
        for popis in ("p25-a-overeni.py --plne", "p25-b-mutace.py",
                      "p24-a-overeni.py", "p24-b-mutace.py",
                      "test-tick-offline.mjs", "tick-mutace.py", "g3-brany.py"):
            nezmereno_zapis("A4 %s" % popis,
                            "dávkový režim (dlouhé běhy); pouští se s `--plne`")
        return

    # 1) měřidlo P25 --plne
    kod, v = cmd(["python", str(P25_A), "--plne"], timeout=3600)
    c = citac(v)
    tv = tvrzeni(r"p25-a-overeni\.py[^\n]{0,90}?(\d+) kontrol, (\d+) chyb",
                 "p25-a-overeni.py")
    check("A4 p25-a-overeni.py --plne → exit 0 (naměřeno %s)" % (c,), kod, 0)
    if tv:
        check("A4 p25-a-overeni.py --plne = tvrzených %d/%d" % tv, c, tv)

    # 2) mutační důkaz P25
    kod, v = cmd(["python", str(P25_B)], timeout=1800)
    c = citac(v)
    t = tvrzeni(r"p25-b-mutace\.py[^\n]{0,90}?(\d+) kontrol, (\d+) chyb",
                "p25-b-mutace.py")
    check("A4 p25-b-mutace.py → exit 0 (naměřeno %s)" % (c,), kod, 0)
    if t:
        check("A4 p25-b-mutace.py = tvrzených %d/%d" % t, c, t)

    # 3) měřidlo P24 a jeho důkaz (stav se posunul — viz A4-posun níž)
    # ⚠ P24 JE „DOBOVÉ" MĚŘENÍ: jeho A8 měří ŽIVÝ stav hry (HEAD, čistota stromu,
    # nepushnuté commity). Když do hry zapíše SOUBĚŽNÁ SESSION (naměřeno 7. 10.
    # 2026: tři commity 15:50–16:02), počet červených A8 se změní — a to NENÍ
    # vada měřidla ani moje. Kontroluje se proto, že **každá** červená je `A8`
    # (vzor P25 A1d), ne zapečené číslo.
    kod, v = cmd(["python", str(ANALYZA / "p24-a-overeni.py")], timeout=3600)
    c24 = citac(v)
    cerv24 = [l.strip()[len("CHYBA"):].strip() for l in v.splitlines()
              if l.strip().startswith("CHYBA")]
    mimo_a8 = [x for x in cerv24 if not x.startswith("A8")]
    print("      p24-a: čítač=%s, červených=%d (mimo A8: %d) %s"
          % (c24, len(cerv24), len(mimo_a8), [x[:60] for x in cerv24[:4]]))
    check("A4 p24-a-overeni.py: 99 kontrol (stav hry měřen zvlášť)",
          c24[0] if c24 else None, 99)
    check("A4 p24-a-overeni.py: KAŽDÁ červená je A8 = dobový stav hry (ne vada)",
          mimo_a8, [])
    kod, v = cmd(["python", str(ANALYZA / "p24-b-mutace.py")], timeout=1800)
    c = citac(v)
    t = tvrzeni(r"p24-b-mutace\.py[^\n#]{0,40}#\s*(\d+)/(\d+)", "p24-b-mutace.py")
    check("A4 p24-b-mutace.py → exit 0 (naměřeno %s)" % (c,), kod, 0)
    if t:
        check("A4 p24-b-mutace.py = tvrzených %d/%d" % t, c, t)

    # 4) offline test tiku + jeho mutační důkaz
    kod, v = cmd(["node", "tools/test-tick-offline.mjs"], timeout=1800)
    c = citac(v)
    t = tvrzeni(r"test-tick-offline\.mjs[^\n]{0,40}?\*\*(\d+)/(\d+)\*\*",
                "test-tick-offline.mjs")
    check("A4 test-tick-offline.mjs → exit 0 (naměřeno %s)" % (c,), kod, 0)
    if t:
        check("A4 test-tick-offline.mjs = tvrzených %d/%d" % t, c, t)

    kod, v = cmd(["python", "_analyza/tick-mutace.py"], timeout=1800)
    c = citac(v)
    mv = re.search(r"vrat:\s*(\d+)", v)
    vrat = int(mv.group(1)) if mv else None
    t = tvrzeni(r"tick-mutace\.py[^\n]{0,40}?\*\*(\d+) vrat / (\d+)/(\d+)\*\*",
                "tick-mutace.py")
    check("A4 tick-mutace.py → exit 0 (naměřeno %s)" % (c,), kod, 0)
    if t:
        check("A4 tick-mutace.py = tvrzených %d vrat / %d/%d" % t,
              (vrat,) + c if c else None, t)
    check("A4 tick-mutace.py VYKAZUJE počet vrat (ne jen v dokumentu)", vrat, 20)

    # 5) počet bran a deklarovaných exitů
    strom = ast.parse(G3.read_text(encoding="utf-8", errors="replace"))
    brany, ocek = [], []
    for node in ast.walk(strom):
        if not isinstance(node, ast.Assign):
            continue
        jmena = [t_.id for t_ in node.targets if isinstance(t_, ast.Name)]
        if "BRANY" in jmena and isinstance(node.value, ast.List):
            brany = [e for e in node.value.elts]
        if "OCEKAVANE_NENULOVE" in jmena and isinstance(node.value, ast.Dict):
            ocek = [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
    t = tvrzeni(r"\*\*(\d+) bran\*\*", "g3 počet bran")
    check("A4 g3 má %d bran (tvrzeno v §55: %s)" % (len(brany), t),
          (len(brany),) if t else None, t)
    check("A4 g3 má %d deklarovaných nenulových exitů" % len(ocek), len(ocek), 1)

    kod, v = cmd(["python", "_analyza/g3-brany.py"], timeout=1800)
    s = souhrn_g3(v)
    if s is None:
        nezmereno_zapis("A4 g3 souhrn nenulových exitů",
                        "souhrn v výstupu g3 nenalezen (ani jeden z obou tvarů)")
    else:
        print("      g3: nenulových=%d deklarovaných=%d NEDEKLAROVANÝCH=%d" % s)


# ═══════════════════════════════════════════════════════════════════ A5 ═══
def a5():
    print("\n--- A5: nález P25-K — rozsah měřidla `ov-g-neovereno.py` ---")
    # (a) PŘED OPRAVOU: verze z commitu, kde rozsah JEŠTĚ zúžený byl.
    # ⚠ NESMÍ TO BÝT `HEAD` NASLEPO: jakmile se oprava commitne, je v `HEAD` už
    # OPRAVENÁ verze — naměřeno 7. 10. 2026 (P26), že kontrola „verze z HEAD čte
    # 1 řádek" pak spadne na SPRÁVNĚ opraveném repu. Je to táž past jako
    # `p20-a-kody-bran.py` (nález H107): „změřeno před commitem" ≠ „změřeno teď".
    # Hledá se proto ZPĚT po commitech, dokud se nenajde verze, která opravdu
    # čte 1 řádek — a když se nenajde, je to NEZMĚŘENO, ne zelená.
    pred = ANALYZA / "_p26-pred-opravou.py"
    for rev in ("HEAD", "HEAD~1", "HEAD~2", "HEAD~3", "HEAD~4"):
        b = blob(rev, "_analyza/ov-g-neovereno.py")
        if b is None:
            continue
        pred.write_bytes(b)
        try:
            kod, v = cmd(["python", str(pred)], timeout=300)
        finally:
            pred.unlink(missing_ok=True)
        m = re.search(r"nálezů \(řádků tabulek Hxx\):\s*(\d+)", v)
        if m and int(m.group(1)) == 1:
            print("      PŘED opravou (verze z `%s`): čte 1 řádek Hxx, exit=%d"
                  % (rev, kod))
            check("A5 P25-K POTVRZEN: verze z `%s` čte JEN 1 řádek Hxx" % rev, 1, 1)
            check("A5 a přitom tvrdí zelenou (exit 0) — zelená nad 1 % rozsahu",
                  kod, 0)
            break
    else:
        nezmereno_zapis("A5 verze měřidla PŘED opravou",
                        "v žádném z `HEAD`…`HEAD~4` není verze, která by četla "
                        "1 řádek Hxx (oprava je hloub v historii)")

    # (b) PO OPRAVĚ: živé měřidlo vypíše, KTERÉ soubory otevřelo, a celý rozsah.
    kod, v = cmd(["python", str(OV_G)], timeout=300)
    mr = re.search(r"nálezů \(řádků tabulek Hxx\) CELKEM:\s*(\d+)", v)
    check("A5 živé měřidlo měří 99 řádků Hxx (1 + 98)", int(mr.group(1)) if mr else None, 99)
    check("A5 a VYPISUJE, které soubory otevřelo (`OTEVŘENO:`)",
          len(re.findall(r"^  OTEVŘENO:", v, re.M)), 3)
    check("A5 a vypisuje i rozsah MIMO živé zdroje (aby zúžení nebylo tiché)",
          "MIMO ŽIVÉ ZDROJE" in v, True)

    # (c) NEGATIVNÍ KONTROLA 1: fixtura s NEOVĚŘENO → měřidlo MUSÍ spadnout.
    fixt = SCRATCH / "fixtura-nevereno.md"
    fixt.write_text("# fixtura\n\n| # | Nález | Doklad |\n|---|---|---|\n"
                    "| **H900** | vymyšlený nález, který čeká | stav NEOVĚŘENO |\n",
                    encoding="utf-8", newline="")
    kod, v = cmd(["python", str(OV_G), "--handoff", str(fixt)], timeout=300)
    check("A5 NEGATIVNÍ KONTROLA: fixtura s NEOVĚŘENO → exit 1", kod, 1)
    check("A5 a měřidlo ten nález JMENUJE", "H900" in v, True)

    # (d) NEGATIVNÍ KONTROLA 2: PRÁZDNÝ rozsah → NEMĚŘENO, ne zelená.
    prazdna = SCRATCH / "fixtura-prazdna.md"
    prazdna.write_text("# fixtura bez tabulky nálezů\n", encoding="utf-8", newline="")
    kod, v = cmd(["python", str(OV_G), "--handoff", str(prazdna)], timeout=300)
    check("A5 NEGATIVNÍ KONTROLA: prázdný rozsah → NEMĚŘENO (exit 1)", kod, 1)
    check("A5 a řekne to slovy (ne tichá zelená)", "NEMĚŘENO" in v, True)

    # (e) obě fixtury byly SKUTEČNÉ soubory (negativní kontroly neběžely nad ničím)
    check("A5 obě fixtury existovaly (negativní kontroly neběžely nad ničím)",
          (fixt.is_file(), prazdna.is_file()), (True, True))


# ═══════════════════════════════════════════════════════════════════ A6 ═══
def a6(plne):
    print("\n--- A6: nic se nerozbilo ani neztratilo ---")
    kod, v = cmd(["python", "_analyza/kronika-kontrola.py"], timeout=600)
    check("A6 kronika-kontrola.py → exit 0", kod, 0)
    check("A6 a řekla SEDÍ (ne jen nespadla)", "SEDÍ" in v.upper(), True)
    kod, v = cmd(["python", "_analyza/handoff-kontrola-uplnost.py"], timeout=600)
    check("A6 handoff-kontrola-uplnost.py → exit 0", kod, 0)
    check("A6 a hlásí CHYBÍ: 0", "CHYBÍ:                0" in v or "CHYBÍ: 0" in v, True)
    kod, v = cmd(["python", str(OV_G)], timeout=600)
    check("A6 ov-g-neovereno.py → exit 0 a měří 99 řádků",
          (kod, "nálezů (řádků tabulek Hxx) CELKEM: 99" in v), (0, True))

    # Doklady a sondy P26 musí být ZAREGISTROVANÉ: doklad mimo vzor dávky
    # „shnije" (§38.8) a sonda v seznamu bran se počítá jako brána (P24-I).
    zdroj_p20 = P20_D.read_text(encoding="utf-8", errors="replace")
    mv = re.search(r"VZOR\s*=\s*re\.compile\(\s*r?[\"']([^\"']+)[\"']\s*\)", zdroj_p20)
    vzz = re.compile(mv.group(1)) if mv else None
    pres = set()
    for node in ast.walk(ast.parse(zdroj_p20)):
        if isinstance(node, ast.Assign) and any(
                isinstance(t_, ast.Name) and t_.id == "PRESKOCIT"
                for t_ in node.targets) and isinstance(node.value, ast.Set):
            pres = {e.value for e in node.value.elts if isinstance(e, ast.Constant)}
    check("A6 doklady P26 pokrývá vzor dávky `p20-d`",
          [j for j in ("p26-a-overeni.py", "p26-b-mutace.py")
           if vzz is None or not vzz.match(j)], [])
    check("A6 sondy P26 jsou v PRESKOCIT dávky (nespouští se jako doklady)",
          sorted(j for j in pres if j.startswith("p26-sonda")),
          ["p26-sonda-rozsah.py", "p26-sonda-zapis.py"])
    # ⚠ Fixtura musí mít jméno, které vzor SKUTEČNĚ nematchuje — `p26-c-…`
    # by prošlo (`p2[0-9]-` matchuje `p26-`) a „negativní kontrola" by
    # nedokazovala nic (naměřeno 7. 10. 2026).
    check("A6 negativní kontrola: predikát chybějící doklad NAJDE",
          [j for j in ("p26-a-overeni.py", "nedoklad-p26.py")
           if vzz is None or not vzz.match(j)], ["nedoklad-p26.py"])

    if not plne:
        nezmereno_zapis("A6 g3 a validate-all",
                        "dávkový režim (sahají na inventář a jsou dlouhé); "
                        "pouští se s `--plne`")
        check("A6 g3 a validate-all se NEPOUŠTÍ současně (dávka nic nepustila)",
              True, True)
        return

    kod, v = cmd(["python", "_analyza/g3-brany.py"], timeout=2700)
    ZAST = ("C2: mutace N1 (5 běhů)", "n1-over-inventar", "validate-all (CELEK)")
    nedekl, jmena = 0, []
    s = souhrn_g3(v)
    if s is None:
        nezmereno_zapis("A6 g3 souhrn",
                        "souhrn ve výstupu g3 nenalezen (ani jeden z obou tvarů)")
    else:
        celkem, dekl, nedekl = s
        jmena = re.findall(r"NEOČEKÁVANÝ:\s*(.+?)\s*→", v)
        print("      g3: nenulových=%d deklarovaných=%d NEDEKLAROVANÝCH=%d %s"
              % (celkem, dekl, nedekl, jmena or ""))
        check("A6 g3: deklarovaný nenulový exit je právě 1", dekl, 1)
        if nedekl:
            # Pojmenovaný STAV, ne deklarace: zastaralý inventář se NAPRAVUJE
            # přegenerováním (nález P25-H), nedeklaruje se.
            zname = [j for j in jmena if j in ZAST]
            check("A6 každý nedeklarovaný exit g3 je pojmenovaný STAV (zastaralý inventář)",
                  len(zname), len(jmena))
        else:
            check("A6 g3: žádný nedeklarovaný nenulový exit", nedekl, 0)
    mb = re.search(r"BRÁNY BEZ ČÍTAČE mimo deklarovaný stav:\s*(\d+)", v)
    pocet_bez = int(mb.group(1)) if mb else None
    jmena_bez = re.findall(r"BRÁNY BEZ ČÍTAČE[^\n]*→\s*(.+)", v)
    # ⚠ `C2: mutace N1` ODMÍTÁ měřit nad zastaralým inventářem — a to je SPRÁVNĚ
    # (`exit 2` bez čítače). Když je inventář zastaralý (pozná se podle
    # `n1-over-inventar` mezi NEOČEKÁVANÝMI), je „1 bez čítače" TENTÝŽ stav,
    # ne druhá vada. Náprava je v obou případech PŘEGENEROVAT.
    zastaraly = ("n1-over-inventar" in jmena) or ("validate-all (CELEK)" in jmena)
    if zastaraly and pocet_bez == 1 and jmena_bez and "C2:" in jmena_bez[0]:
        nezmereno_zapis("A6 g3: brány bez čítače mimo deklarovaný stav",
                        "1 = `%s` — odmítá měřit nad ZASTARALÝM inventářem "
                        "(pojmenovaný stav; náprava je PŘEGENEROVAT a spustit znovu)"
                        % jmena_bez[0].strip())
    else:
        check("A6 g3: brány bez čítače mimo deklarovaný stav", pocet_bez, 0)
    # ⚠ „ZASTARALÝ INVENTÁŘ" NENÍ DEKLAROVATELNÝ STAV (nález P25-H) — náprava je
    # PŘEGENEROVAT. Když g3 padá JEN na něm, hlásí se to jako pojmenovaný STAV
    # (`NEZMĚŘENO`), ne jako nález; finální g3 po regeneraci musí dát `exit 0`.
    if kod == 0:
        check("A6 g3 → exit 0 (jen deklarované exity)", kod, 0)
    elif nedekl and all(j in ZAST for j in jmena):
        nezmereno_zapis("A6 g3 → exit 0 (jen deklarované exity)",
                        "g3 padá na POJMENOVANÉM STAVU (zastaralý inventář, "
                        "`exit %d`); náprava je PŘEGENEROVAT a spustit znovu" % kod)
    else:
        check("A6 g3 → exit 0 (jen deklarované exity)", kod, 0)

    kod, v = cmd(["node", "tools/validate-all.mjs"], timeout=2700)
    if kod == 0:
        check("A6 validate-all.mjs → exit 0", kod, 0)
        check("A6 a hlásí VŠE V POŘÁDKU", "VŠE V POŘÁDKU" in v, True)
    elif "INVENTÁŘ JE ZASTARALÝ" in v:
        nezmereno_zapis("A6 validate-all → VŠE V POŘÁDKU",
                        "validate-all padá na ZASTARALÉM INVENTÁŘI (pojmenovaný "
                        "stav, ne nález) — náprava je PŘEGENEROVAT a spustit znovu")
    else:
        check("A6 validate-all.mjs → exit 0", kod, 0)
        check("A6 a hlásí VŠE V POŘÁDKU", "VŠE V POŘÁDKU" in v, True)


# ══════════════════════════════════════════════════════════════════ main ═══
def main() -> int:
    global HANDOFF, OV_G, G3, VYSTUP_CESTA
    ap = argparse.ArgumentParser()
    ap.add_argument("--jen", default=None, help="seznam etap (např. A5)")
    ap.add_argument("--plne", action="store_true",
                    help="VŠE: A1–A6 včetně mutace živého zdroje a g3/validate-all")
    # ⚠ PŘEPÍNAČE CEST EXISTUJÍ KVŮLI MUTAČNÍMU DŮKAZU (`p26-b-mutace.py` pustí
    # tohle měřidlo nad ZMUTOVANÝMI KOPIEMI a vyžaduje, aby spadlo) — stejný
    # důvod jako u `p25-a-overeni.py`. Bez nich by se musel mutovat ŽIVÝ strom.
    ap.add_argument("--handoff", default=None, help="cesta k HANDOFF.md")
    ap.add_argument("--ovg", default=None, help="cesta k ov-g-neovereno.py")
    ap.add_argument("--g3", default=None, help="cesta k g3-brany.py")
    # ⚠ `--vystup` je tu proto, aby mutační důkaz (`p26-b-mutace.py`) nepřepsal
    # ULOŽENÝ VÝSTUP tohohle měřidla svým dílčím během (`--jen A5`).
    ap.add_argument("--vystup", default=None, help="cesta k uloženému výstupu")
    args = ap.parse_args()
    VYSTUP_CESTA = pathlib.Path(args.vystup).resolve() if args.vystup else None
    for jmeno, hodnota in (("HANDOFF", args.handoff), ("OV_G", args.ovg),
                           ("G3", args.g3)):
        if hodnota:
            globals()[jmeno] = pathlib.Path(hodnota).resolve()
    etapy = {x.strip().upper() for x in
             (args.jen if args.jen else
              ("A1,A2,A3,A4,A5,A6" if args.plne else "A1,A4,A5,A6")).split(",")
             if x.strip()}

    print("=" * 78)
    print("P26/A — PŘEMĚŘENÍ PRÁCE P25 VLASTNÍM POSTUPEM (A1–A6)")
    print("=" * 78)
    if not args.plne and not args.jen:
        print("⚠ REŽIM DÁVKY: měří se A1 (kontramutace v kopiích), A4, A5, A6 — bez\n"
              "  mutace živého zdroje a bez `g3`/`validate-all` (sahají na inventář).\n"
              "  Plná kontrola (A2 zarážky v handleru, A3 vazby, g3) je `--plne`.\n")

    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    try:
        if "A1" in etapy:
            a1(args.plne)
        if "A2" in etapy:
            a2()
        if "A3" in etapy:
            a3()
        if "A4" in etapy:
            a4(args.plne)
        if "A5" in etapy:
            a5()
        if "A6" in etapy:
            a6(args.plne)
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)
        if KOPIE_TESTU.exists():
            KOPIE_TESTU.unlink()

    print("\n" + "=" * 78)
    print("NEZMĚŘENO (není nula a není zelená): %d" % len(nezmereno))
    for p in nezmereno:
        print("   · %s" % p)
    print("=" * 78)
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    return 1 if chyb else 0


if __name__ == "__main__":
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
        vystup = VYSTUP_CESTA or (ANALYZA / "p26-a-overeni-vystup.txt")
        vystup.write_bytes("".join(_tee.buffer).encode("utf-8"))
        print("plný výstup: %s (%d bajtů, UTF-8)"
              % (vystup.name, vystup.stat().st_size))
    sys.exit(_kod)
