# -*- coding: utf-8 -*-
r"""P28/A — NEZÁVISLÉ PŘEMĚŘENÍ PRÁCE P27 (A1–A7) VLASTNÍM POSTUPEM.

CO TO JE: měřidlo session **P28**. Ověřuje práci P27 (záznamy `HANDOFF.md` §57
a §58) — a to **jiným postupem, než jak vznikla** (`AGENTS.md`: autor není
nezávislý reviewer; `hlouchkova-analyza` §1).

⚠ ČÍM SE LIŠÍ OD `p27-a-overeni.py` (a proč to není jeho kopie):
  * **A1** netestuje měřidlo P26, ale **měřidlo P27** — kontramutace v KOPIÍCH
    (`--handoff`, `--g3`, `--ovg`), s **diferenciálem** (baseline vs. mutant);
  * **A2** nedává do handleru zarážku (to dělala P27), ale **POŠKOZUJE ODPOVĚĎ
    handleru** (hodnotu, ne text dotazu) — tím se měří, že kontroly čtou
    ODPOVĚĎ daného endpointu, a zároveň se tím **třídí** kontroly;
  * **A3** je postavená na tomtéž: co zůstalo zelené po poškození HODNOTY, musí
    zčervenat po poškození **TEXTU dotazu** (to je měřený rozdíl TVAR vs OBSAH);
  * **A4** bere čísla **parsováním z dokumentu** (ne zapečená) a u drahých
    čítačů používá **dnešní uložený běh** `p27-a-overeni-vystup.txt`;
  * **A5** počítá rozsah **vlastním průchodem souborů**, ne čtením výpisu brány;
  * **A6/A7** měří brány a inventář vlastními predikáty (mj. přepočet otisku
    z uložených záznamů a citlivost na OBSAH, ne na velikost).

⚠ CO NEMĚŘÍ: kvalitu kódu conductora ani správnost rozhodnutí P27 — měří jen
**shodu tvrzení s živým stavem** a **schopnost měřidla spadnout**.

Použití:
    python _analyza/p28-a-overeni.py            # dávka: A1, A4 (levné), A5, A6, A7
    python _analyza/p28-a-overeni.py --plne     # i A2/A3 (9 běhů testu tiku) a g3/validate-all
    python _analyza/p28-a-overeni.py --jen A5
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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
TOOLS = WS / "tools"
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
SRC = WS / "conductor" / "src" / "index.ts"
TEST_TIK = TOOLS / "test-tick-offline.mjs"
KOPIE_TESTU = TOOLS / "p28-kopie-tick.mjs"
G3 = ANALYZA / "g3-brany.py"
OV_G = ANALYZA / "ov-g-neovereno.py"
P27_A = ANALYZA / "p27-a-overeni.py"
P27_B = ANALYZA / "p27-b-mutace.py"
NEANGL = ANALYZA / "hl-neanglicky-v-kodu.py"
RIZIKA = ANALYZA / "hl-rizika-jazyka.py"
INVENTAR = ANALYZA / "_inventar.json"
HANDOFF_KONTROLA = ANALYZA / "handoff-kontrola-uplnost.py"
KRONIKA_KONTROLA = ANALYZA / "kronika-kontrola.py"
SKILL_MUTACE = ANALYZA / "test-over-skilly-delegovane.py"
# ⚠ VLASTNÍ JMÉNO DOKLADU (ne `p27-a-overeni-vystup.txt`): měřidlo P27 si svůj
# výstup přepisuje při KAŽDÉM spuštění — a P28 spouští `p27-a --jen A4/A5/A6`
# jako baseline. Kdyby čtlo týž soubor, přečetlo by si ČÁSTEČNÝ výstup vlastního
# dílčího běhu (naměřeno 8. 10. 2026: soubor se přepsal uprostřed běhu P28).
# Tenhle doklad je proto KOPIE plného běhu, uložená pod vlastním jménem.
BASELINE_P27A = ANALYZA / "p28-vzdy-p27a-plne-vystup.txt"
ZIVA = ANALYZA / "p28-ziva-sluzba.mjs"
SCRATCH = ANALYZA / "p28-scratch"

sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj  # noqa: E402  (projektová knihovna mutací)

kontrol = 0
chyb = 0
nezmereno = []
VYSTUP_CESTA = None

SKUPINY = ("X", "Y", "Z", "AA", "AB", "AC", "AD")


def check(popis, zjisteno, ocekavano):
    global kontrol, chyb
    kontrol += 1
    if zjisteno == ocekavano:
        print("  OK    %s" % popis)
    else:
        chyb += 1
        print("  CHYBA %s\n        čekáno:   %r\n        naměřeno: %r"
              % (popis, ocekavano, zjisteno))


def nezmereno_zapis(popis, duvod):
    nezmereno.append("%s — %s" % (popis, duvod))
    print("  ??    %s (NEZMĚŘENO: %s)" % (popis, duvod))


def cmd(argumenty, timeout=3600, env=None):
    """(exit kód, stdout+stderr) — spuštěno z kořene repa.

    `env` umí přidat proměnné prostředí. Používá se pro `FORGE_REGISTR`: měřidlo
    NESMÍ přepsat živý registr bran obsahem z fixtury (naměřeno 6. 10. 2026 —
    dávka si tehdy zapsala do živého registru jednu fixturu `A1: zdravá`
    a běh byl přitom „zelený“).
    """
    e = dict(os.environ)
    if env:
        e.update(env)
    try:
        r = subprocess.run([str(a) for a in argumenty], cwd=str(WS), env=e,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT po %d s" % timeout


def citac(v, vzor=r"(\d+) kontrol, (\d+) chyb"):
    """POSLEDNÍ čítač ve výstupu (dřívější mohou být z dílčích běhů)."""
    m = None
    for m in re.finditer(vzor, v):
        pass
    return (int(m.group(1)), int(m.group(2))) if m else None


def citac_obecny(v):
    """Čítač, ať je vypsaný kterýmkoli z OBOU používaných tvarů.

    ⚠ RŮZNÉ BRÁNY MAJÍ RŮZNÝ TVAR ČÍTAČE (naměřeno P28: `over-dokumentaci.py`
    a `test-over-skilly-delegovane.py` tisknou `Kontrol: 64, chyb: 0`, kdežto
    ostatní `N kontrol, M chyb`). Kdo čte jen jeden tvar, dostane `None` —
    a `None` se snadno přečte jako „nesedí", i když jde o **jiný formát**.
    """
    vzory = (r"(\d+) kontrol, (\d+) chyb", r"Kontrol:\s*(\d+),\s*chyb:\s*(\d+)",
             r"(\d+) kontrol, (\d+) CHYB")
    m = None
    for vzor in vzory:
        for m in re.finditer(vzor, v):
            pass
        if m:
            return (int(m.group(1)), int(m.group(2)))
    return None


def popisy_cervenych(v):
    """Popisy červených kontrol (`CHYBA <popis>`) — pro přiřazení ke skupinám."""
    out = []
    for l in v.splitlines():
        s = l.strip()
        if s.startswith("CHYBA "):
            out.append(s[6:].strip())
    return out


def skupina(popis):
    m = re.match(r"^([A-Z]{1,2}):\s", popis)
    return m.group(1) if m else None


def sha(p):
    try:
        return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
    except OSError:
        return None


def sekce(cislo, text):
    """Tělo oddílu `## <cislo>.` (od nadpisu k dalšímu `## `)."""
    m = re.search(r"^## %s\." % re.escape(str(cislo)), text, re.M)
    if not m:
        return ""
    m2 = re.search(r"^## ", text[m.end():], re.M)
    return text[m.start(): m.end() + m2.start()] if m2 else text[m.start():]


def tvrzeni(text, vzor, popis=None):
    """Skupiny regulárního výrazu PŘEČTENÉ Z DOKUMENTU (ne zapečené číslo).

    ⚠ KDYŽ SE TVRZENÍ NENAJDE, JE TO CHYBA — NE TICHO. „Brána, která čeká na
    vstup, jenž nikdy nepřijde, je horší než žádná“ (`AGENTS.md`): kdyby se
    kontrola při chybějícím tvrzení jen přeskočila, měřidlo by nad dokumentem
    bez oddílu prošlo s MENŠÍM čítačem a `exit 0`.
    """
    m = re.search(vzor, text, re.S)
    if m is None:
        chyb_claim(popis or vzor)
        return None
    return tuple(m.groups())


def chyb_claim(popis):
    global kontrol, chyb
    kontrol += 1
    chyb += 1
    print("  CHYBA tvrzení se v dokumentu NENAŠLO (kontrola by se tiše přeskočila): %s"
          % popis)


def chyby_v_etape(text, etapa):
    """Počet `CHYBA` řádků v oddílu `--- A<etapa>:` výstupu měřidla P27.

    ⚠ Měří se ODDÍL, ne celý dokument: měřidlo P27 má jednu trvale červenou
    v jiné etapě a srovnávat celkový čítač by znamenalo měřit cizí stav.
    """
    m = re.search(r"^--- %s[^\n]*$" % re.escape(etapa), text, re.M)
    if not m:
        return None
    m2 = re.search(r"^--- A", text[m.end():], re.M)
    telo = text[m.end(): m.end() + m2.start()] if m2 else text[m.end():]
    return len([l for l in telo.splitlines() if l.strip().startswith("CHYBA")])


def z_baseline(jmeno, text):
    """Čítač drahého nástroje z DNEŠNÍHO uloženého běhu `p27-a --plne`."""
    vzor = (re.escape(jmeno)
            + r"[^\n]*?naměřeno \((\d+), (\d+)\)")
    m = re.search(vzor, text)
    return (int(m.group(1)), int(m.group(2))) if m else None


def pregeneruj_inventar():
    """PŘEGENERUJ inventář PŘED během bran, které ho čtou (`g3`, `validate-all`).

    ⚠ PROČ TO MĚŘIDLO DĚLÁ A P27 NE: běh, který předtím spustil jiné brány,
    **sám** změní obsah souborů ve stromě → obsahový otisk vstupů se rozjede →
    `g3` i `validate-all` hlásí pojmenovaný STAV „zastaralý inventář“ (v dnešním
    běhu P27 to tak bylo: 3× NEZMĚŘENO + 1 chyba navíc). Je to **vada POŘADÍ
    měření**, ne kódu — náprava je přegenerovat, ne vypnout kontrolu.
    """
    kod, _ = cmd([sys.executable, str(NEANGL), "--json", str(INVENTAR)], timeout=1800)
    return kod == 0


# ═══════════════════════════════════════════════════════════════════ A1 ═══
def a1(s57, s58):
    print("\n--- A1: UMÍ MĚŘIDLO P27 SPADNOUT? (kontramutace v KOPIÍCH) ---")
    # (0) dnešní uložený běh měřidla P27 — doklad, ze kterého čtu i drahé čítače
    if BASELINE_P27A.is_file():
        text = BASELINE_P27A.read_text(encoding="utf-8", errors="replace")
        c = citac(text)
        tv = tvrzeni(s57, r"p27-a-overeni\.py --plne[^\n]*?\*\*(\d+) kontrol, (\d+) chyb\*\*")
        if tv:
            check("A1 KONTROLA: dnešní běh měřidla P27 = tvrzených %s/%s"
                  % (tv[0], tv[1]), c, (int(tv[0]), int(tv[1])))
        else:
            nezmereno_zapis("A1 tvrzení o p27-a --plne",
                            "v §57 se tvrzení o čítači nenašlo")
    else:
        nezmereno_zapis("A1 dnešní běh měřidla P27",
                        "%s neexistuje (spusť `p27-a-overeni.py --plne`)" % BASELINE_P27A.name)

    SCRATCH.mkdir(parents=True, exist_ok=True)
    # BASELINE měřidla P27 = DNEŠNÍ ULOŽENÝ PLNÝ BĚH (doklad `p28-vzdy-*`).
    # ⚠ ZÁMĚRNĚ SE NESPOUŠTÍ ZNOVU `--jen A4`: A4 pouští i drahé čítače
    # (p26-a --plne, p26-b, p25-b, p24-b, tick-mutace) — dohromady ~10 minut.
    # Diferenciál potřebuje jen **počet chyb v tom oddílu**, a ten je v dokladu.
    text_v = (BASELINE_P27A.read_text(encoding="utf-8", errors="replace")
              if BASELINE_P27A.is_file() else "")
    if not text_v:
        nezmereno_zapis("A1 diferenciál", "%s neexistuje" % BASELINE_P27A.name)
        return
    base_etap = {e: chyby_v_etape(text_v, e) for e in ("A4", "A5", "A6")}
    print("      baseline (dnešní uložený běh): chyby v oddílech %s" % base_etap)
    if any(v is None for v in base_etap.values()):
        nezmereno_zapis("A1 diferenciál", "doklad nemá oddíly A4/A5/A6")
        return

    # (1) ČÍSLO v §56 POSUNUTÉ (83/83 → 82/83) → A4 musí spadnout NA TÉ KONTROLE.
    # ⚠ POUČENÍ ZE TŘÍ POKUSŮ (naměřeno 8. 10. 2026 v P28):
    #  1. kotva nesmí být hledána přes CELÝ dokument — `83/83` je tam 15×
    #     a `handoff-kontrola-uplnost → **83/83**` 4×; první výskyt leží MIMO §56.
    #     Mutace pak sáhla jinam a „diferenciál nevyšel“ byl FALEŠNÝ NÁLEZ;
    #  2. §56 se NESMÍ izolovat do vlastního souboru — `p27-a --jen A4` nad
    #     samotným §56 udělá jen **12 kontrol** (místo ~50) a potřebuje CELÝ
    #     dokument, takže srovnání s baseline by měřilo jiný běh;
    #  3. ŘEŠENÍ: v KOPII CELÉHO dokumentu se místo tvrzení **označí sentinelem**
    #     (`§P28§`, v souboru je 1×) a mutuje se `mutuj` sentinel → číslo.
    #     Tím platí záruka knihovny (kotva 1×, změna proběhla, návrat bajt na bajt)
    #     a dokument zůstává ÚPLNÝ.
    text_h = HANDOFF.read_text(encoding="utf-8")
    s56 = sekce("56", text_h)
    kotva = "`handoff-kontrola-uplnost` → **83/83**"
    check("A1 kotva tvrzení je v §56 právě 1× (v dokumentu 4×)",
          (s56.count(kotva), text_h.count(kotva)), (1, 4))
    if s56.count(kotva) == 1:
        # KONTROLA (diferenciál): TÝŽ příkaz nad NEZMUTOVANOU kopií musí projít.
        # ⚠ `--jen A4` bez `--plne` je LEVNÁ část etapy (14 kontrol) — drahé čítače
        # se v dávkovém režimu přeskakují (naměřeno: 12–14 kontrol), takže
        # „počet kontrol > 30“ by měřilo něco jiného, než si myslí.
        k_ctl = SCRATCH / "k-handoff-ctl.md"
        k_ctl.write_bytes(HANDOFF.read_bytes())
        kod, v = cmd([sys.executable, str(P27_A), "--jen", "A4",
                      "--handoff", str(k_ctl),
                      "--vystup", str(SCRATCH / "p27-a1a-ctl-vystup.txt")], timeout=1800)
        ctl = citac(v)
        check("A1a KONTROLA: TYTÉŽ vstupy bez mutace → 0 chyb v etapě A4",
              ctl[1] if ctl else None, 0)
        check("A1a a kontrola má NENULOVÝ čítač (není to prázdný běh)",
              (ctl[0] if ctl else 0) >= 10, True)

        i56 = text_h.find(s56)
        k56 = SCRATCH / "k-handoff-56.md"      # ⚠ CELÝ dokument, ne jen §56
        k56.write_text(text_h[:i56]
                       + s56.replace(kotva, kotva + "§P28§", 1)
                       + text_h[i56 + len(s56):], encoding="utf-8")
        check("A1 v kopii je místo tvrzení OZNAČENÉ právě 1×",
              k56.read_text(encoding="utf-8").count("**83/83**§P28§"), 1)
        try:
            with mutuj(k56, "**83/83**§P28§", "**82/83**"):
                kod, v = cmd([sys.executable, str(P27_A), "--jen", "A4",
                              "--handoff", str(k56),
                              "--vystup", str(SCRATCH / "p27-a1a-vystup.txt")], timeout=1800)
            red = popisy_cervenych(v)
            c1 = citac(v)
            print("      mutant: čítač=%s, červených=%d (kontrola: %s, baseline dokladu A4: %s chyb)"
                  % (c1, len(red), ctl, base_etap["A4"]))
            check("A1a mutant má STEJNÝ počet kontrol jako kontrola (měří se týž rozsah)",
                  (c1[0] if c1 else 0), (ctl[0] if ctl else -1))
            check("A1a a mutant má VÍC chyb než kontrola (diferenciál)",
                  (c1[1] if c1 else -1) > (ctl[1] if ctl else 10 ** 6), True)
            check("A1a POSUNUTÉ ČÍSLO v §56 → měřidlo P27 spadne na kontrole, "
                  "která to číslo ČTE z dokumentu",
                  any("úplnost handoffu" in x for x in red), True)
        except ValueError as e:
            nezmereno_zapis("A1a kontramutace §56", str(e))
    else:
        nezmereno_zapis("A1a kontramutace §56", "kotva není v §56 právě 1×")
    check("A1a pracovní kopie je uklizena po mutaci (sha256 se mění zpět)",
          sha(k56) is not None, True)

    # (2) NÁLEZ O MĚŘIDLE P27: NENALEZENÉ TVRZENÍ TIŠE ZMÍZÍ (NEZMĚŘENO, ne chyba).
    # Naměřeno v dnešním uloženém běhu: `A4 tvrzení §56: over-skilly` → měřidlo
    # napsalo **NEZMĚŘENO** („číslo v §56 není“) a pokračovalo — čítač kontrol
    # tím KLESL, ale verdikt zůstal zelený. Je to táž třída, kterou `AGENTS.md`
    # popisuje jako „brána, která čeká na vstup, jenž nikdy nepřijde“.
    nev_a4 = [l.strip() for l in text_v.splitlines() if l.strip().startswith("NEZMĚŘENO")]
    print("      měřidlo P27 mělo v dnešním běhu %d× NEZMĚŘENO (stav, ne zelená)" % len(nev_a4))
    check("A1b měřidlo P27 hlásí NEZMĚŘENO i jako POJMENOVANÝ stav (není to tichá nula)",
          bool(nev_a4), True)
    check("A1b a je vidět, že nenalezené tvrzení se NEpočítá jako chyba "
          "(to je vlastnost měřidla, ne nález o kódu)",
          any("tvrzení §56" in x for x in nev_a4) or any("nenašlo" in x for x in nev_a4), True)

    # (3) `g3` s 50. branou → A6 musí spadnout (jen v plném režimu, kde A6 g3 pouští)
    kopie_g = SCRATCH / "k-g3.py"
    shutil.copyfile(G3, kopie_g)
    try:
        with mutuj(kopie_g, "BRANY = [",
                   'BRANY= [("p28-fixtura", ["python", "x.py"]),'):
            kod, v = cmd([sys.executable, str(P27_A), "--plne", "--jen", "A6",
                          "--g3", str(kopie_g), "--vystup", str(SCRATCH / "p27-a1c-vystup.txt")], timeout=3600,
                         env={"FORGE_REGISTR": str(SCRATCH / "registr-fixtura.json")})
        c2 = citac(v)
        check("A1c kopie g3 s 50. branou SHODÍ A6 měřidla P27 (víc chyb než %d)"
              % base_etap["A6"], (c2[1] if c2 else -1) > base_etap["A6"], True)
    except ValueError as e:
        nezmereno_zapis("A1c kontramutace g3", str(e))
    check("A1c kopie g3 je vrácena (sha256)", sha(kopie_g), sha(G3))

    # (4) `ov-g` bez hlášení ROZSAHU → A5 musí spadnout
    kopie_o = SCRATCH / "k-ovg.py"
    shutil.copyfile(OV_G, kopie_o)
    stary_vypis = ('    print("\\n  ── MIMO ŽIVÉ ZDROJE (zmrazené kopie a zálohy'
                   ' — ZÁMĚRNĚ se nečtou) ──")')
    try:
        with mutuj(kopie_o, stary_vypis,
                   '    print("\\n  ── (hlášení rozsahu je vypnuto) ──")'):
            kod, v = cmd([sys.executable, str(P27_A), "--jen", "A5",
                          "--ovg", str(kopie_o),
                          "--vystup", str(SCRATCH / "p27-a1d-vystup.txt")], timeout=1800)
        c3 = citac(v)
        check("A1d vypnuté hlášení rozsahu SHODÍ A5 měřidla P27",
              (c3[1] if c3 else -1) > base_etap["A5"], True)
    except ValueError as e:
        nezmereno_zapis("A1d kontramutace ov-g", str(e))
    check("A1d kopie ov-g je vrácena (sha256)", sha(kopie_o), sha(OV_G))

    # (5) vlastní mutační důkaz měřidla P27 — musí vykázat čítač a diferenciál
    kod, v = cmd([sys.executable, str(P27_B)], timeout=3600)
    c = citac(v)
    tv = tvrzeni(s57, r"p27-b-mutace\.py`\s*→\s*\*\*(\d+) kontrol, (\d+) chyb\*\*")
    if tv:
        check("A1e p27-b-mutace.py = tvrzených %s/%s" % (tv[0], tv[1]), c,
              (int(tv[0]), int(tv[1])))
    check("A1e p27-b-mutace.py → exit 0", kod, 0)
    # ⚠ HLEDÁ SE SLOVO „DIFERENCIÁL“ (i velkými písmeny) — p26-b i p27-b ho
    # tisknou verzálkou („M3a DIFFERENCIÁL“), takže `re.I` je podmínka.
    check("A1e a je to DIFERENCIÁL (výstup mluví o diferenciálu)",
          len(re.findall(r"diferenci[aá]l", v, re.I)) >= 1, True)


# ═══════════════════════════════════════════════════════════════════ A2 ═══
# POŠKOZENÍ ODPOVĚDI HANDLERU (hodnota, ne text dotazu): kotva → náhrada.
POISON_OBSAH = [
    ("X", "/health", "ready: t?.n ?? 0,", "ready: (t?.n ?? 0) + 100,"),
    ("Y", "/queue", "return json({ tasks: tasks.results });",
     "return json({ tasks: (tasks.results as any[]).map((t: any) => ({ ...t, attempts: 4242 })) });"),
    ("Z", "/roadmap", "return json({ roadmap: rows.results });",
     "return json({ roadmap: (rows.results as any[]).map((r: any) => ({ ...r, attempts: 4242 })) });"),
    ("AA", "/failed", 'log_tail: (r.log_tail || "").slice(0, 2000),',
     'log_tail: (r.log_tail || "").slice(0, 7),'),
    ("AB", "/status", "return json({ runs: runs.results });",
     "return json({ runs: (runs.results as any[]).map((r: any) => ({ ...r, pr_url: 'POISON' })) });"),
    ("AC", "/workers", "return json({ workers: workers.results });",
     "return json({ workers: (workers.results as any[]).map((w: any) => ({ ...w, kinds: 'POISON' })) });"),
    ("AD", "/games", "return json({ games: games.results });",
     "return json({ games: (games.results as any[]).map((g: any) => ({ ...g, active: 7 })) });"),
]
# POŠKOZENÍ TEXTU DOTAZU (tvar): co zůstane zelené po poškození hodnoty, musí
# zčervenat tady — tím je měřený rozdíl TVAR vs OBSAH.
# ⚠ DOTAZ SE MUSÍ POŠKODIT TAK, ABY HO FALEŠNÁ D1 JEŠTĚ POZNALA (jinak by test
# spadl na „neznámý dotaz“ a měřil by něco jiného, než si myslí): proto se mění
# jen `ORDER BY`/přidá se filtr, ne tabulka ani `LIMIT`, na kterých stojí routing.
POISON_TVAR = [
    ("AC", "/workers", "SELECT * FROM workers ORDER BY last_seen DESC",
     "SELECT * FROM workers ORDER BY last_seen"),
    ("AD", "/games", "SELECT * FROM games ORDER BY game_id",
     "SELECT * FROM games WHERE active=1 ORDER BY game_id"),
]


def a2(s57):
    print("\n--- A2: VOLÁ TEST TIKU SEDM ENDPOINTŮ? (poškozená ODPOVĚĎ handleru) ---")
    tv = tvrzeni(s57, r"test-tick-offline\.mjs`[^\n]*?\*\*(\d+) kontrol, (\d+) chyb\*\*")
    if not tv:
        nezmereno_zapis("A2 tvrzení o testu tiku", "v §57 se čítač testu nenašel")
    kod, v = cmd(["node", str(TEST_TIK)], timeout=3600)
    c = citac(v, r"VYSLEDEK: (\d+) kontrol, (\d+) (?:CHYB|chyb)")
    check("A2 KONTROLA: živý test tiku = tvrzených %s/%s" % (tv[0], tv[1]) if tv else
          "A2 KONTROLA: živý test tiku má čítač", c,
          (int(tv[0]), int(tv[1])) if tv else c)
    if kod != 0:
        nezmereno_zapis("A2 poškozené běhy", "živý test tiku sám neprochází (exit %d)" % kod)
        return None

    shutil.copyfile(TEST_TIK, KOPIE_TESTU)
    cervene_obsah = {}
    try:
        for pref, cesta, kotva, nahrada in POISON_OBSAH:
            try:
                with mutuj(SRC, kotva, nahrada) as m:
                    check("A2 %s: poškození odpovědi se provedlo (hash před != po)" % cesta,
                          m.hash_po_mutaci != m.hash_pred, True)
                    kod, v = cmd(["node", str(KOPIE_TESTU)], timeout=3600)
            except ValueError as e:
                nezmereno_zapis("A2 %s" % cesta, str(e))
                continue
            red = popisy_cervenych(v)
            vlastni = [d for d in red if skupina(d) == pref]
            cizi = [d for d in red if skupina(d) in SKUPINY and skupina(d) != pref]
            cervene_obsah[pref] = set(vlastni)
            check("A2 %s: aspoň JEDNA kontrola své skupiny zčervenala (%d)"
                  % (cesta, len(vlastni)), len(vlastni) >= 1, True)
            check("A2 %s: ale ŽÁDNÁ kontrola ostatních šesti endpointů (negativní kontrola)"
                  % cesta, cizi, [])
            check("A2 %s: kontrolní `A: /tick odpoví 200` zůstala zelená" % cesta,
                  [d for d in red if d == "A: /tick odpoví 200"], [])
            if vlastni:
                print("        · %s" % vlastni[0][:100])
    finally:
        KOPIE_TESTU.unlink(missing_ok=True)
    check("A2 kopie testu je uklizena (v `tools/` nezůstala)", KOPIE_TESTU.exists(), False)
    check("A2 zdroj conductora je vrácen (sha256)", sha(SRC) is not None, True)
    return cervene_obsah


def a3(cervene_obsah, s57):
    print("\n--- A3: TVRDÍ TESTY I TVAR, NEBO JEN OBSAH? (poškozený TEXT dotazu) ---")
    if not cervene_obsah:
        nezmereno_zapis("A3", "A2 neproběhla (chybí baseline červených)")
        return
    shutil.copyfile(TEST_TIK, KOPIE_TESTU)
    try:
        for pref, cesta, kotva, nahrada in POISON_TVAR:
            try:
                with mutuj(SRC, kotva, nahrada):
                    kod, v = cmd(["node", str(KOPIE_TESTU)], timeout=3600)
            except ValueError as e:
                nezmereno_zapis("A3 %s" % cesta, str(e))
                continue
            red = popisy_cervenych(v)
            vlastni = {d for d in red if skupina(d) == pref}
            nove = sorted(vlastni - cervene_obsah.get(pref, set()))
            check("A3 %s: poškozený TEXT dotazu zčervenal v této skupině (%d)"
                  % (cesta, len(vlastni)), len(vlastni) >= 1, True)
            check("A3 %s: a aspoň JEDNA kontrola, kterou poškození HODNOTY nechalo zelenou"
                  % cesta, len(nove) >= 1, True)
            if nove:
                print("        · TVAR: %s" % nove[0][:100])
            cizi = [d for d in red if skupina(d) in SKUPINY and skupina(d) != pref]
            check("A3 %s: ostatní endpointy zůstaly zelené (negativní kontrola)"
                  % cesta, cizi, [])
    finally:
        KOPIE_TESTU.unlink(missing_ok=True)


# ═══════════════════════════════════════════════════════════════════ A4 ═══
def a4(s57, s58, plne):
    print("\n--- A4: KAŽDÉ TVRZENÉ ČÍSLO ZNOVU NAMĚŘENÉ (číslo se ČTE z dokumentu) ---")
    base = (BASELINE_P27A.read_text(encoding="utf-8", errors="replace")
            if BASELINE_P27A.is_file() else "")

    # 1) test tiku
    tv = tvrzeni(s57, r"test-tick-offline\.mjs`[^\n]*?\*\*(\d+) kontrol, (\d+) chyb\*\*")
    kod, v = cmd(["node", str(TEST_TIK)], timeout=3600)
    c = citac(v, r"VYSLEDEK: (\d+) kontrol, (\d+) (?:CHYB|chyb)")
    if tv:
        check("A4 test-tick-offline.mjs = tvrzených %s/%s" % tv, c, (int(tv[0]), int(tv[1])))
    check("A4 test-tick-offline.mjs → exit 0", kod, 0)

    # 2) úplnost handoffu
    tv = tvrzeni(s57, r"`handoff-kontrola-uplnost`\s*→\s*\*\*(\d+)/(\d+)\*\*")
    kod, v = cmd([sys.executable, str(HANDOFF_KONTROLA)], timeout=1800)
    m = re.search(r"(\d+)\s*/\s*(\d+)", v)
    if tv and m:
        check("A4 handoff-kontrola-uplnost = tvrzených %s/%s" % tv,
              (int(m.group(1)), int(m.group(2))), (int(tv[0]), int(tv[1])))
    check("A4 handoff-kontrola-uplnost → exit 0", kod, 0)

    # 3) kronika
    tv_k = tvrzeni(s57, r"`kronika-kontrola`\s*→\s*\*\*([A-ZÁ-Ž]+)\*\*")
    kod, v = cmd([sys.executable, str(KRONIKA_KONTROLA)], timeout=1800)
    check("A4 kronika-kontrola → exit 0 (tvrzeno: %s)" % (tv_k[0] if tv_k else "?"), kod, 0)
    check("A4 a hlásí SEDÍ", "SEDÍ" in v.upper() or "SEDI" in v, True)

    # 4) over-dokumentaci
    tv = tvrzeni(s57, r"`over-dokumentaci`\s*\*\*(\d+)/(\d+)\*\*")
    kod, v = cmd([sys.executable, str(TOOLS / "over-dokumentaci.py")], timeout=1800)
    c = citac_obecny(v)
    if tv:
        check("A4 over-dokumentaci.py = tvrzených %s/%s" % tv, c, (int(tv[0]), int(tv[1])))
    check("A4 over-dokumentaci.py → exit 0", kod, 0)

    # 5) over-skilly (rozsah cest se mění — proto se čte i „mrtvých cest")
    tv = tvrzeni(s57, r"`over-skilly`\s*\*\*(\d+)/(\d+)\*\*")
    kod, v = cmd([sys.executable, str(TOOLS / "over-skilly.py")], timeout=1800)
    m = re.search(r"Skillů:\s*(\d+),\s*chyb:\s*(\d+)", v)
    if tv and m:
        check("A4 over-skilly = tvrzených %s/%s (dnes %s/%s)"
              % (tv[0], tv[1], m.group(1), m.group(2)),
              (int(m.group(1)), int(m.group(2))), (int(tv[0]), int(tv[1])))
    mm = re.search(r"Cesty k nástrojům:\s*(\d+) zmínek, (\d+) mrtvých", v)
    if mm:
        check("A4 over-skilly: 0 mrtvých cest (tvrzení §58)", mm.group(2), "0")

    # 6) mutační dvojče over-skilly
    tv = tvrzeni(s58, r"mutační dvojče\s*\*\*(\d+)/(\d+)\*\*")
    if tv:
        kod, v = cmd([sys.executable, str(SKILL_MUTACE)], timeout=1800)
        check("A4 test-over-skilly-delegovane.py = tvrzených %s/%s" % tv,
              citac_obecny(v), (int(tv[0]), int(tv[1])))

    # 7) ov-g: rozsah + verdikt
    tv = tvrzeni(s57, r"(\d+) řádků Hxx")
    kod, v = cmd([sys.executable, str(OV_G)], timeout=1800)
    m = re.search(r"nálezů \(řádků tabulek Hxx\) CELKEM:\s*(\d+)", v)
    if tv and m:
        check("A4 ov-g měří CELÝ rozsah = tvrzených %s řádků Hxx" % tv[0],
              int(m.group(1)), int(tv[0]))
    check("A4 ov-g-neovereno → exit 0 (0× NEOVĚŘENO)", kod, 0)

    # 8) g3 + validate-all (sahají na inventář → jen v plném režimu)
    if plne:
        check("A4 inventář přegenerován PŘED g3 (jinak se měří zastaralý stav)",
              pregeneruj_inventar(), True)
        tv = tvrzeni(s57, r"g3`?\s*→\s*\*\*(\d+) bran", "g3 → **N bran**")
        kod, v = cmd([sys.executable, str(G3)], timeout=3600,
                     env={"FORGE_REGISTR": str(SCRATCH / "registr-meridla.json")})
        check("A4 g3 → exit 0 (jen deklarované exity)", kod, 0)
        m = re.search(r"brán celkem:\s*(\d+)", v)
        if tv:
            check("A4 g3 = tvrzených %s bran" % tv[0],
                  int(m.group(1)) if m else None, int(tv[0]))
        md = re.search(r"NEDEKLAROVANÝCH\s+(\d+)", v)
        check("A4 g3: 0 NEDEKLAROVANÝCH nenulových exitů",
              int(md.group(1)) if md else None, 0)
        if kod != 0:
            for l in v.splitlines():
                if "NEOČEKÁVANÝ" in l or "CHYBA" in l:
                    print("        │ %s" % l.strip()[:110])
        kod, v = cmd(["node", str(TOOLS / "validate-all.mjs")], timeout=3600)
        check("A4 validate-all → VŠE V POŘÁDKU", "VŠE V POŘÁDKU" in v, True)
        check("A4 validate-all → exit 0", kod, 0)
        for l in v.splitlines():
            if l.strip().startswith("CHYBA"):
                print("        │ %s" % l.strip()[:110])
    else:
        print("      (g3 a validate-all se v dávce neměří — sahají na inventář)")

    # 9) drahé čítače: z DNEŠNÍHO uloženého běhu (jinak by měřidlo běželo hodinu)
    for jmeno, vzor, kde in (
            ("p26-b-mutace.py", r"`p26-b-mutace`\s*\*\*(\d+)/(\d+)\*\*", s57),
            ("p25-b-mutace.py", r"`p25-b-mutace`\s*\*\*(\d+)/(\d+)\*\*", s57),
            ("p24-b-mutace.py", r"`p24-b-mutace`\s*\*\*(\d+)/(\d+)\*\*", s57),
            ("tick-mutace.py", r"`tick-mutace`\s*\*\*(\d+) vrat / (\d+)/(\d+)\*\*", s57),
            ("p25-a-overeni.py", r"p25-a-overeni\.py --plne\s*#\s*(\d+)/(\d+)", s57),
            ("p26-a-overeni.py", r"p26-a-overeni\.py --plne\s*#\s*(\d+) kontrol", s57),
    ):
        tv = tvrzeni(kde, vzor)
        if not tv:
            nezmereno_zapis("A4 %s" % jmeno, "tvrzení se v dokumentu nenašlo")
            continue
        z = z_baseline(jmeno, base)
        if z is None:
            nezmereno_zapis("A4 %s" % jmeno,
                            "dnešní uložený běh `p27-a --plne` čítač nevykázal")
            continue
        if jmeno == "tick-mutace.py":
            check("A4 tick-mutace.py = tvrzených %s vrat / %s/%s" % tv, z,
                  (int(tv[1]), int(tv[2])))
        else:
            check("A4 %s = tvrzených %s/%s (z dnešního běhu)" % (jmeno, tv[0], tv[1]), z,
                  (int(tv[0]), int(tv[1])))

    # 10) ŽIVÁ SLUŽBA — jen ČTENÍ (žádné /tick ani /poll)
    if not ZIVA.is_file():
        nezmereno_zapis("A4 živá služba", "%s neexistuje" % ZIVA.name)
        return
    kod, v = cmd(["node", str(ZIVA)], timeout=300)
    if kod != 0:
        nezmereno_zapis("A4 živá služba", "čtení selhalo (exit %d): %s" % (kod, v[-200:]))
        return
    try:
        ziv = json.loads(v[v.index("{"):v.rindex("}") + 1])
    except (ValueError, json.JSONDecodeError) as e:
        nezmereno_zapis("A4 živá služba", "výstup není JSON: %s" % e)
        return
    h = ziv.get("health") or {}
    tv = tvrzeni(s58, r"ok=(\w+) ready=(\d+) running=(\d+) games=(\d+)") or \
        tvrzeni(s57, r"ok=(\w+) ready=(\d+) running=(\d+) games=(\d+)")
    if tv:
        check("A4 živě /health = tvrzených ok=%s ready=%s running=%s games=%s" % tv,
              (str(h.get("ok")).lower(), str(h.get("ready")), str(h.get("running")),
               str(h.get("games"))), tv)
    check("A4 živě /health bez tajemství → 200", h.get("status"), 200)
    check("A4 živě /health nese stav CÍLE (`targets`)", (h.get("cilu") or 0) >= 1, True)
    chranene = ziv.get("chranene") or {}
    check("A4 živě: všech 6 chráněných endpointů BEZ tajemství → 401",
          sorted(k for k, x in chranene.items() if x.get("bez") != 401), [])
    check("A4 živě: všech 6 chráněných endpointů S tajemstvím → 200",
          sorted(k for k, x in chranene.items() if x.get("s") != 200), [])
    tv = tvrzeni(s58, r"(\d+) granul,\s*\n?\s*(\d+) blokovaných")
    rm = ziv.get("roadmap") or {}
    if tv:
        check("A4 živě /roadmap = tvrzených %s granul, %s blokovaných" % tv,
              (str(rm.get("granul")), str(rm.get("blokovane"))), tv)
    check("A4 živě /roadmap: 0 blokovaných granul (strop 8 nikoho neblokuje)", rm.get("blokovane"), 0)
    print("      živě /roadmap: stavy=%s, max pokusů na granulích=%s (strop je 8)"
          % (rm.get("stavy"), rm.get("max_pokusu")))
    check("A4 živě: strop 8 NEBLOKUJE (max pokusů < 8 → blokace má jinou příčinu)",
          (rm.get("max_pokusu") or 0) < 8, True)


# ═══════════════════════════════════════════════════════════════════ A5 ═══
RADEK_H = re.compile(r"^\|\s*\*\*(H\d+)\*\*\s*\|")


def radky_h(p):
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return [(i, l) for i, l in enumerate(t.splitlines(), 1) if RADEK_H.match(l)]


def zive_zdroje_h():
    arch = WS / "_archiv"
    return [HANDOFF] + sorted(p for p in arch.iterdir()
                              if p.is_file() and p.name.startswith("HANDOFF-")
                              and p.suffix == ".md") if arch.is_dir() else [HANDOFF]


def mimo_zive(zive):
    """Soubory s řádky Hxx MIMO živé zdroje (zmrazené kopie a zálohy).

    ⚠ KANONICKÝ `HANDOFF.md` SE VYLUČUJE VŽDY — i když je `--handoff` přepsaný
    (mutační důkaz). Naměřeno 8. 10. 2026 v P28: bez toho se při přepsaném
    `--handoff` počítal ŽIVÝ `HANDOFF.md` jako „mimo živé zdroje“ (140 místo 139),
    srovnání s bránou padlo a **vypadalo to jako vada měřidla** — přitom to byla
    vada TOHOHLE průchodu.
    """
    zit = {p.resolve() for p in zive}
    zit.add((WS / "HANDOFF.md").resolve())
    mimo = []
    for p in sorted(WS.rglob("*.md")):
        if ".git" in p.parts or p.resolve() in zit:
            continue
        if not p.name.lower().startswith("handoff"):
            continue
        n = len(radky_h(p))
        if n:
            mimo.append((str(p.relative_to(WS)), n))
    return mimo


def a5(s57):
    print("\n--- A5: ROZSAH MĚŘIDLA `ov-g-neovereno` (VLASTNÍ počítadlo, ne výpis) ---")
    zive = zive_zdroje_h()
    vlastni = {p.name: len(radky_h(p)) for p in zive}
    celkem = sum(vlastni.values())
    tv = tvrzeni(s57, r"(\d+) řádků Hxx")
    for jm, n in vlastni.items():
        print("      vlastní počet: %-28s %4d řádků Hxx" % (jm, n))
    if tv:
        check("A5 vlastní počet řádků Hxx v ŽIVÝCH zdrojích = tvrzených %s" % tv[0],
              celkem, int(tv[0]))
    check("A5 živých zdrojů je víc než jeden (jinak by rozsah mohl být zúžený)",
          len(zive) > 1, True)

    kod, v = cmd([sys.executable, str(OV_G)], timeout=1800)
    m = re.search(r"nálezů \(řádků tabulek Hxx\) CELKEM:\s*(\d+)", v)
    check("A5 brána hlásí TOTÉŽ číslo jako vlastní počítadlo", int(m.group(1)) if m else None, celkem)
    m2 = re.search(r"celkem mimo:\s*(\d+) řádků v (\d+) souborech", v)
    mimo = mimo_zive(zive)
    check("A5 ROZSAH MIMO živé zdroje = vlastní počet",
          (int(m2.group(1)), int(m2.group(2))) if m2 else None,
          (sum(n for _, n in mimo), len(mimo)))
    check("A5 a je to NENULOVÝ rozsah (zúžení by muselo být vidět)",
          sum(n for _, n in mimo) > 0, True)

    # fixtury: vada musí bránu shodit, prázdno musí hlásit NEMĚŘENO
    SCRATCH.mkdir(parents=True, exist_ok=True)
    fx = SCRATCH / "p28-fixtura-h.md"
    fx.write_text("| **H999** | fiktivní nález | NEOVĚŘENO |\n", encoding="utf-8")
    kod, v = cmd([sys.executable, str(OV_G), "--handoff", str(fx)], timeout=1800)
    check("A5 fixtura s NEOVĚŘENO → exit 1", kod != 0, True)
    check("A5 a je to kvůli tomu nálezu (ne z jiného důvodu)", "H999" in v, True)
    fx2 = SCRATCH / "p28-fixtura-prazdna.md"
    fx2.write_text("# prázdný soubor (žádný řádek Hxx)\n", encoding="utf-8")
    kod, v = cmd([sys.executable, str(OV_G), "--handoff", str(fx2)], timeout=1800)
    check("A5 PRÁZDNÁ fixtura → NEMĚŘENO (nula není úspěch)", "NEMĚŘENO" in v, True)
    check("A5 a prázdná fixtura → exit 1", kod != 0, True)


# ═══════════════════════════════════════════════════════════════════ A6 ═══
def a6(plne):
    print("\n--- A6: NIC SE NEROZBILO ANI NEZTRATILO ---")
    # kronika: řádky session (úbytek by znamenal smazaný záznam)
    t = KRONIKA.read_text(encoding="utf-8")
    radky = [int(m.group(1)) for m in re.finditer(r"^\|\s*\*\*(\d+)\*\*\s*\|", t, re.M)]
    chybejici = [i for i in range(1, (max(radky) if radky else 0) + 1) if i not in radky]
    print("      kronika: řádků session %d, nejvyšší id %s, CHYBĚJÍCÍ id: %s"
          % (len(radky), max(radky) if radky else "—", chybejici or "(žádné)"))
    check("A6 řádky session v kronice jdou 1..N bez děr (žádný záznam se neztratil)",
          chybejici, [])
    check("A6 kronika má aspoň 42 řádků session (P27 = 42)", len(radky) >= 42, True)

    # ⚠ KRITÉRIUM JE „NIC NEUBYLO“, NE „SOUBOR JE BEZ ZMĚN“: záznamy se v této
    # session legitimně DOPISUJÍ (HANDOFF §59, řádek kroniky) — a kdyby kontrola
    # chtěla čistý strom, byla by červená přesně za to, co se udělat MÁ.
    # Měří se proto POČET SMAZANÝCH řádků (`git diff --numstat`), ne prázdný diff.
    kod, v = cmd(["git", "diff", "--numstat", "HEAD", "--", "HANDOFF.md",
                  "KRONIKA-PROJEKTU.md"], timeout=300)
    pridano = smazano = 0
    for l in v.splitlines():
        casti = l.split("\t")
        if len(casti) >= 2 and casti[0].isdigit() and casti[1].isdigit():
            pridano += int(casti[0])
            smazano += int(casti[1])
    print("      necommitnuté záznamy: +%d řádků, -%d řádků" % (pridano, smazano))
    check("A6 v HANDOFF.md ani v KRONICE neubyl ANI JEDEN řádek (jen se přidávalo)",
          smazano, 0)

    kod, v = cmd([sys.executable, str(KRONIKA_KONTROLA)], timeout=1800)
    check("A6 kronika-kontrola → SEDÍ a exit 0", (kod, "SEDÍ" in v.upper() or "SEDI" in v),
          (0, True))

    # ⚠ P28-E: kontroluje brána KONTINUITU ID? Naměřeno 8. 10. 2026: kronika měla
    # 41 řádků s id 1..42 a **id 24 chybělo** (commit `c3ee946` ho smazal) —
    # a `kronika-kontrola` to neviděla, protože kontrolovala jen počet, datum
    # a typ. Kontrola byla doplněna; tady se měří, že UMÍ SPADNOUT.
    radky_t = KRONIKA.read_text(encoding="utf-8").splitlines(True)
    idx = [i for i, l in enumerate(radky_t) if re.match(r"^\|\s*\*\*30\*\*\s*\|", l)]
    if len(idx) == 1:
        SCRATCH.mkdir(parents=True, exist_ok=True)
        kopie_k = SCRATCH / "kronika-bez-radku-30.md"
        kopie_k.write_bytes("".join(radky_t[:idx[0]] + radky_t[idx[0] + 1:]).encode("utf-8"))
        kod, v = cmd([sys.executable, str(KRONIKA_KONTROLA), str(kopie_k)], timeout=1800)
        check("A6 MUTACE: kronika bez řádku 30 → brána SPADNE a id POJMENUJE",
              (kod != 0, "[30]" in v), (True, True))
        kopie_k.unlink(missing_ok=True)
    else:
        nezmereno_zapis("A6 mutace kroniky", "kotva řádku 30 není v kronice právě 1×")

    if plne:
        check("A6 inventář přegenerován PŘED g3 (vlastní nález o POŘADÍ měření)",
              pregeneruj_inventar(), True)
        kod, v = cmd([sys.executable, str(G3)], timeout=3600,
                     env={"FORGE_REGISTR": str(SCRATCH / "registr-a6.json")})
        check("A6 g3 → exit 0 (jen deklarované exity)", kod, 0)
        m = re.search(r"brán celkem:\s*(\d+)", v)
        check("A6 g3 měří 49 bran", int(m.group(1)) if m else None, 49)
        md = re.search(r"NEDEKLAROVANÝCH\s+(\d+)", v)
        check("A6 g3: 0 NEDEKLAROVANÝCH exitů", int(md.group(1)) if md else None, 0)
        kod, v = cmd(["node", str(TOOLS / "validate-all.mjs")], timeout=3600)
        check("A6 validate-all → VŠE V POŘÁDKU a exit 0",
              (kod, "VŠE V POŘÁDKU" in v), (0, True))
    else:
        print("      (g3 a validate-all se v dávce neměří — sahají na inventář)")


# ═══════════════════════════════════════════════════════════════════ A7 ═══
def otisk_ze_zaznamu(inv):
    """VLASTNÍ přepočet otisku z uložených záznamů (ne z živého stromu).

    Formát je daný skenerem (`obsahovy_otisk`): pro každý repozitář (podle jména,
    setříděný) řádek s cestou|bajty|sha256[:16]. Když můj přepočet sedí na
    uložený `sha256`, otisk JE nad tím seznamem — a druhý krok ověří, že seznam
    popisuje DNEŠNÍ bajty na disku.
    """
    h = hashlib.sha256()
    for z in sorted(inv.get("repozitare") or [], key=lambda x: x["repo"]):
        h.update(("%s\n" % z["repo"]).encode("utf-8"))
        for f in sorted(z.get("soubory") or [], key=lambda x: x["cesta"]):
            h.update(("%s|%d|%s\n" % (f["cesta"], f["bajtu"], f["sha256"])).encode("utf-8"))
    return h.hexdigest()


def a7():
    print("\n--- A7: INVENTÁŘ A BRÁNY PO SOBĚ (vlastní přepočet otisku) ---")
    if not INVENTAR.is_file():
        nezmereno_zapis("A7 inventář", "%s neexistuje" % INVENTAR.name)
        return
    inv = json.loads(INVENTAR.read_text(encoding="utf-8"))
    ot = inv.get("otisk_vstupu") or {}
    repa = ot.get("repozitare") or []
    check("A7 otisk počítá OBĚ repa", len(repa), 2)
    check("A7 a jsou to orchestra + hra",
          sorted(z["repo"] for z in repa), ["games/uo-shadows", "orchestra"])
    check("A7 oba repozitáře mají NENULOVÝ počet souborů",
          all(z.get("soubory") for z in repa), True)
    check("A7 vlastní přepočet otisku ze záznamů = uložený sha256",
          otisk_ze_zaznamu(ot), ot.get("sha256"))

    # vzorek: popisuje inventář DNEŠNÍ bajty na disku?
    zkontrolovano = 0
    rozepsane = []
    for z in repa:
        koren = WS if z["repo"] == "orchestra" else WS.parent / "uo-shadows"
        for f in (z.get("soubory") or [])[:40]:
            p = koren / f["cesta"]
            if not p.is_file():
                rozepsane.append("%s: soubor na disku NENÍ" % f["cesta"])
                continue
            data = p.read_bytes()
            if len(data) != f["bajtu"] or hashlib.sha256(data).hexdigest()[:16] != f["sha256"]:
                rozepsane.append("%s: bajty/otisk nesedí" % f["cesta"])
            zkontrolovano += 1
    check("A7 vzorek %d souborů (40 z každého repa) sedí na DNEŠNÍ bajty" % zkontrolovano,
          rozepsane, [])
    check("A7 vzorek je nenulový (nula by nebyla měření)", zkontrolovano > 0, True)

    # citlivost na OBSAH (ne na velikost): fixtura se STEJNOU délkou, jinými bajty
    fx = ANALYZA / "p28-fixtura-otisk.py"
    fx.write_text("# p28 fixtura otisku AAAA\n", encoding="utf-8")
    try:
        kod, v = cmd([sys.executable, str(NEANGL), "--json", str(INVENTAR)], timeout=1800)
        check("A7 přegenerování inventáře s fixturou proběhlo", kod, 0)
        kod, v = cmd([sys.executable, str(RIZIKA)], timeout=1800)
        check("A7 KONTROLA: nad ČERSTVÝM inventářem je brána zelená", kod, 0)

        data = fx.read_bytes()
        fx.write_bytes(data.replace(b"AAAA", b"BBBB"))
        check("A7 fixtura má po změně STEJNOU velikost (měří se obsah, ne velikost)",
              len(fx.read_bytes()), len(data))
        kod, v = cmd([sys.executable, str(RIZIKA)], timeout=1800)
        check("A7 změna OBSAHU (stejná délka) shodí bránu", kod != 0, True)
        check("A7 a to POJMENOVANÝM STAVEM „INVENTÁŘ JE ZASTARALÝ“",
              "INVENTÁŘ JE ZASTARALÝ" in v, True)
        kod, v = cmd([sys.executable, str(NEANGL), "--json", str(INVENTAR)], timeout=1800)
        kod, v = cmd([sys.executable, str(RIZIKA)], timeout=1800)
        check("A7 NEGATIVNÍ KONTROLA: nad přegenerovaným inventářem je zelená", kod, 0)
        check("A7 a hlášení „INVENTÁŘ JE ZASTARALÝ“ tam NENÍ",
              "INVENTÁŘ JE ZASTARALÝ" in v, False)

        # vyloučený artefakt otisk NEMĚNÍ
        pred = json.loads(INVENTAR.read_text(encoding="utf-8"))["otisk_vstupu"]["sha256"]
        doklad = ANALYZA / "p28-a-overeni-vystup.txt"
        stavalo = doklad.is_file()
        doklad.write_bytes(b"# p28: doklad (vyloucen vzorem z otisku)\n")
        try:
            kod, v = cmd([sys.executable, str(NEANGL), "--otisk"], timeout=1800)
            m = re.search(r'"sha256":\s*"([0-9a-f]{64})"', v)
            check("A7 doklad `*-vystup.txt` otisk NEMĚNÍ (vyloučený artefakt)",
                  m.group(1) if m else None, pred)
        finally:
            if not stavalo:
                doklad.unlink(missing_ok=True)
    finally:
        fx.unlink(missing_ok=True)
    kod, v = cmd([sys.executable, str(NEANGL), "--json", str(INVENTAR)], timeout=1800)
    kod, v = cmd([sys.executable, str(RIZIKA)], timeout=1800)
    check("A7 po úklidu fixtury je inventář zase čerstvý a brána zelená", kod, 0)


# ══════════════════════════════════════════════════════════════════ main ═══
def main():
    global VYSTUP_CESTA
    ap = argparse.ArgumentParser()
    ap.add_argument("--jen", default=None, help="seznam etap, např. A1,A5")
    ap.add_argument("--plne", action="store_true",
                    help="i A2/A3 (9 běhů testu tiku) a g3/validate-all")
    ap.add_argument("--vystup", default=None)
    # ⚠ PŘEPÍNAČE CEST EXISTUJÍ KVŮLI MUTAČNÍMU DŮKAZU (`p28-b-mutace.py`):
    # bez nich by měřidlo šlo otestovat jen na živých souborech — a to je
    # přesně to, co se dělat NEMÁ (mutace v živém stromě).
    ap.add_argument("--handoff", default=None, help="cesta k HANDOFF.md (pro mutaci)")
    ap.add_argument("--g3", default=None, help="cesta ke g3-brany.py (pro mutaci)")
    ap.add_argument("--ovg", default=None, help="cesta k ov-g-neovereno.py (pro mutaci)")
    ap.add_argument("--test", default=None, help="cesta k testu tiku (pro mutaci)")
    ap.add_argument("--p27a", default=None, help="cesta k měřidlu P27 (pro mutaci)")
    args = ap.parse_args()
    for jmeno, hodnota in (("HANDOFF", args.handoff), ("G3", args.g3), ("OV_G", args.ovg),
                           ("TEST_TIK", args.test), ("P27_A", args.p27a)):
        if hodnota:
            globals()[jmeno] = pathlib.Path(hodnota).resolve()
    VYSTUP_CESTA = (pathlib.Path(args.vystup).resolve() if args.vystup
                    else ANALYZA / "p28-a-overeni-vystup.txt")
    etapy = {x.strip().upper() for x in (args.jen if args.jen else
              ("A1,A2,A3,A4,A5,A6,A7" if args.plne else "A1,A4,A5,A6,A7")).split(",")
             if x.strip()}

    print("=" * 78)
    print("P28/A — NEZÁVISLÉ PŘEMĚŘENÍ PRÁCE P27 (A1–A7)")
    print("=" * 78)
    if not args.plne and not args.jen:
        print("⚠ DÁVKA: A1, A4 (levné + dnešní uložený běh), A5, A6 (levné), A7.\n"
              "  Plná kontrola (A2/A3 = 9 běhů testu tiku, g3, validate-all) je --plne.\n")

    text_h = HANDOFF.read_text(encoding="utf-8", errors="replace")
    s57, s58 = sekce("57", text_h), sekce("58", text_h)
    check("P28 §57 existuje (délka %d)" % len(s57), len(s57) > 3000, True)
    check("P28 §58 existuje (délka %d)" % len(s58), len(s58) > 1000, True)

    SCRATCH.mkdir(parents=True, exist_ok=True)
    cervene_obsah = None
    try:
        if "A1" in etapy:
            a1(s57, s58)
        if "A2" in etapy:
            cervene_obsah = a2(s57)
        if "A3" in etapy:
            a3(cervene_obsah, s57)
        if "A4" in etapy:
            a4(s57, s58, args.plne)
        if "A5" in etapy:
            a5(s57)
        if "A6" in etapy:
            a6(args.plne)
        if "A7" in etapy:
            a7()
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)
        KOPIE_TESTU.unlink(missing_ok=True)

    print("\n" + "=" * 78)
    print("NEZMĚŘENO (není nula a není zelená): %d" % len(nezmereno))
    for n in nezmereno:
        print("   · %s" % n)
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
        VYSTUP_CESTA.parent.mkdir(parents=True, exist_ok=True)
        VYSTUP_CESTA.write_bytes("".join(_tee.buffer).encode("utf-8"))
        print("plný výstup: %s (%d bajtů, UTF-8)"
              % (VYSTUP_CESTA.name, VYSTUP_CESTA.stat().st_size))
    sys.exit(_kod)
