# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   _HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
# Dokumenty, ktere zustaly STANICI (D6): na ty se saha absolutne.
# ⚠ Kořen stanice je JINÝ DISK, takže se odvodit nedá — bere se z prostředí
# s dokumentovanou výchozí hodnotou (vzor z `tools/verify-setup.py:69`).
import os as _os
_STANICE_DOKUMENTY = _pl.Path(_os.environ.get(
    "FORGE_STANICE", r"C:\Users\Ssevc\Local-Deepseek"))
r"""Kontrola zadání: je `NEXT-SESSION-INSTRUKCE.md` ještě použitelné?

PROČ TO EXISTUJE (naměřeno 2. 10. 2026): zadání pro druhý krok řetězu vznikalo
dřív, než první krok skončil — a zastaralo **během hodiny**. Dokument tvrdil
„pushnuto `525d45b..be41964`", a skutečný `HEAD` byl o **tři commity** dál.
Zadání mělo **6 přeškrtnutých** (už neplatných) odstavců.

Řešení není „psát aktuálněji" (to nejde — text vždy vzniká dřív, než ho někdo
čte), ale **nést v zadání, PROTI ČEMU bylo měřeno**, a tuhle kontrolu udělat
prvním krokem. Skript proto:

  1. přečte z hlavičky zadání tvrzený commit a čas,
  2. porovná ho s ŽIVÝM stavem obou repů,
  3. změří, jak je zadání staré a kolik commitů od té doby přibylo,
  4. spočítá „historické" pasáže (přeškrtnuté), které jsou signálem stáří.

Nic nemění a nic nepushuje. `exit 0` = zadání je použitelné (i s poznámkami);
`exit 1` = zadání je zastaralé a **tvrzení o stavu se musí přeměřit**.

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\zadani-kontrola.py
"""
import datetime as dt
import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
GIT = str(WS / "tools" / "git.cmd")
# ⚠ OD 2. 10. 2026 (nález H28) MŮŽE BÝT ZADÁNÍ VE VÍC SOUBORECH.
# Do té doby tu byla konstanta `NEXT-SESSION-INSTRUKCE.md` — a to je **ruční
# seznam o jednom prvku**: jakmile vzniklo zadání mimo něj (`ZADANI-PO-AUDITU.md`,
# protože `NEXT-SESSION-INSTRUKCE.md` patří souběžné session), začala tahle
# kontrola **měřit jiný soubor, než jaký session čte** — a hlásila `exit 0`.
# Je to táž vada, před kterou varuje `overovani` §7.10: brána je zelená nad
# dokumentem, který nikdy neotevřela. Proto se soubor dá předat přepínačem;
# bez něj se chová jako dřív (zpětná kompatibilita).
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
if "--soubor" in sys.argv:
    _i = sys.argv.index("--soubor")
    ZADANI = pathlib.Path(sys.argv[_i + 1])
    if not ZADANI.is_absolute():
        ZADANI = WS / ZADANI
# ⚠ NÁLEZ H53 (4. 10. 2026, P13c): tady stálo `("orchestra", WS)` — tedy klíč,
# který se **jmenoval jinak než repo**. Zadání píše `forge-orchestra = <sha>`
# (podle NÁZVU REPA), ale skript se ptal na klíč `orchestra` →
# `tvrzene_head.get("orchestra")` vrátil `None` → vypsal
# „? orchestra: zadání netvrdí žádný commit" a **orchestra se vůbec neporovnala**.
#
# Důsledek, který se nesmí splést: skript skončil `exit 1` a jeho verdikt
# („zadání je zastaralé") byl **náhodou správný** — ale **ne z toho důvodu,
# kvůli kterému existuje**. Kdyby zadání tvrdilo správný commit, spadl by
# stejně. Je to past z `overovani` §10.1: `exit 1` ze špatného důvodu.
#
# Odteď: (1) zobrazované jméno je **jméno adresáře repa** (odvozené, ne literál),
# (2) ke každému repu se hledá klíč **podle VÍC možných jmen** — jméno složky,
# jméno s předponou `forge-`, a hodnota z hlavičky, (3) nespárované tvrzení
# z hlavičky se **vypíše jako varování** (nesmí tiše zmizet).
REPA = [(WS.name, WS), (_HRA.name, _HRA)]
# Jak se repo může v hlavičce jmenovat. `{d}` = jméno složky.
_ALIASY = ("{d}", "forge-{d}", "forge_orchestra", "{d}-repo")


def _mozna_jmena(jmeno: str) -> list[str]:
    return [v.format(d=jmeno).lower() for v in _ALIASY]


def _najdi_tvrzene(jmeno: str) -> str:
    """Najde tvrzený commit pro repo podle VŠECH možných jmen z hlavičky."""
    for kandidat in _mozna_jmena(jmeno):
        if tvrzene_head.get(kandidat):
            return tvrzene_head[kandidat]
    # Poslední záchrana: shoda podle podřetězce (např. `forge-orchestra` vs.
    # `orchestra`) — ale jen když je kandidát JEDNOZNAČNÝ.
    shody = [v for k, v in tvrzene_head.items() if jmeno.lower() in k or k in jmeno.lower()]
    if len(shody) == 1:
        return shody[0]
    return ""


def git(repo: pathlib.Path, *args: str) -> str:
    r = subprocess.run([GIT, "-C", str(repo), *args],
                       capture_output=True, shell=True)
    return (r.stdout or b"").decode("utf-8", "replace").strip()


def zivy_stav() -> dict:
    stav = {}
    for jmeno, cesta in REPA:
        stav[jmeno] = {
            "head": git(cesta, "rev-parse", "HEAD"),
            "pred": git(cesta, "rev-list", "--count", "origin/main..HEAD"),
            "zmenene": len([l for l in git(cesta, "status", "--porcelain").splitlines() if l.strip()]),
            "cas": git(cesta, "log", "-1", "--format=%cI"),
        }
    return stav


print("=" * 78)
print(f"KONTROLA ZADÁNÍ — je `{ZADANI.name}` ještě použitelné?")
print("=" * 78)

if not ZADANI.is_file():
    print(f"CHYBA: {ZADANI.name} neexistuje — řetěz předávání je přerušený.")
    sys.exit(2)

text = ZADANI.read_text(encoding="utf-8")
radky = text.splitlines()
stari_dnu = (dt.datetime.now().timestamp() - ZADANI.stat().st_mtime)
stari_hodin = stari_dnu / 3600
zmeneno = dt.datetime.fromtimestamp(ZADANI.stat().st_mtime).strftime("%Y-%m-%d %H:%M")

print(f"\n  soubor: {ZADANI.name}  ({len(radky)} řádků, {len(text)} znaků)")
print(f"  naposledy zapsán: {zmeneno}  (před {stari_hodin:.1f} h)")

# ── 1) HLAVIČKA: co zadání TVRDÍ ────────────────────────────────────────────
# POZOR (naměřeno 2. 10. 2026): vzorec se NESMÍ ptát na „první sha v hlavičce".
# První verze tohohle skriptu to dělala — a když se v hlavičce změnil tvrzený
# commit, našla sha z ŘÁDKU „Zkontrolováno při:" (který zůstal) a hlásila
# `exit 0` NAD ZASTARALÝM ZADÁNÍM. Odhalil to až mutační test.
# Čte se proto řádek s klíčem „Stav obou repů při psaní:".
#
# ⚠ A DRUHÁ POLOVINA TÉHOŽ (nález H189, naměřeno P38/P39, opraveno P40): číst
# dvojice JEN Z TOHO JEDNOHO ŘÁDKU znamenalo, že **zalomená hlavička se
# neporovnala VŮBEC** — na řádku s klíčem zůstalo jen `` `forge-orchestra` = … ``
# a `` `uo-shadows` = … `` skončilo na dalším řádku. Naměřeno P38: `dvojic = 1`
# a **tvrzení o HŘE se nezměřilo**. Bylo to nejstarší nezaplacené slepé místo
# brány — a `g3` ho měl v `OCEKAVANE_NENULOVE = {"zadání kontrola": 1}`, tedy
# „deklarovaně červené", takže se to jako vada NIKDY neprojevilo.
# ── TVAR HLAVIČKY: dvojice se čtou z CELÉHO BLOKU HLAVIČKY (H189) ──────────
# ⚠ ZVÝRAZNĚNÍ `**` MUSÍ VZOR PŘEŽÍT: v dokumentech stanice se píše
# `` `forge-orchestra` = **`c87db93`** ``. Vzor, který zvýraznění nezná, hlásí
# vadu na SPRÁVNÉM dokumentu — a falešný poplach se hledá hůř než slepé místo
# (naměřeno 7. 10. 2026 v šabloně měřidel, past E4).
VZOR_DVOJICE = re.compile(
    r"\*{0,2}`?([A-Za-z0-9_-]+)`?\*{0,2}\s*=\s*\*{0,2}`?([0-9a-f]{7,40})`?\*{0,2}")

# Klíč se HLEDÁ v prvních tolika řádcích (okno hledání klíče se touhle opravou
# nemění — mění se jen to, ODKUD se čtou dvojice).
HLAVICKA_RADKU = 30
# ⚠ TVRDÝ STROP BLOKU + JEHO VYKÁZÁNÍ (H189): bez stropu by se „blok" mohl
# roztéct přes celý dokument, kdyby v něm chyběl prázdný řádek i ukončovací
# řádek. Projekt má naměřeno, že **velkorysé okno není opatrnost, je to
# slepota** (blok o 5 441 znacích umlčel celý oddíl) — proto strop existuje,
# je POJMENOVANÝ a když se použije, výstup to ŘEKNE.
MAX_BLOK = 40
# ⚠ UKONČENÍ BLOKU — KONZERVATIVNÍ, a proč právě takhle:
#   * PRÁZDNÝ ŘÁDEK = konec odstavce hlavičky. Hlavička je jeden odstavec;
#     co je za prázdným řádkem, už k ní nepatří.
#   * „Zkontrolováno při:" a „Kotva pro měření" = POZDĚJŠÍ řádky, které nesou
#     JINÉ tvrzení (čas měření / kotva pro měřidla). Mají sice TÝŽ TVAR
#     `<repo> = <sha>`, ale kdyby se do bloku připletly, dvojice by se přečetly
#     DVAKRÁT a pozdější (třeba stará) hodnota by tu první **přebila** — přesně
#     to, před čím H189 varuje. Proto blok končí PRVNÍM z nich.
#   * ASCII varianty jsou tu proto, že brána už u klíče variantu bez diakritiky
#     přijímá („Stav obou repu") a hlavička se opisuje ručně.
UKONCENI_BLOKU = ("Zkontrolováno při", "Zkontrolovano pri",
                  "Kotva pro měření", "Kotva pro mereni")


def _je_ukonceni(radek: str) -> bool:
    """Je řádek ukončením bloku hlavičky? (Zvýraznění `**` se ignoruje.)"""
    return radek.strip().lstrip("*").startswith(UKONCENI_BLOKU)


tvrzene_head = {}
radek_stavu = ""
cislo_stavu = 0
for cislo, l in enumerate(radky[:HLAVICKA_RADKU], start=1):
    if "Stav obou repů" in l or "Stav obou repu" in l:
        radek_stavu = l
        cislo_stavu = cislo
        break

# ── BLOK HLAVIČKY (H189): od řádku s klíčem dál, dokud nenarazí ukončení ────
# První řádek bloku je VŽDY řádek s klíčem (ukončením být nemůže — nese klíč).
blok: list = []
strop_dosazen = False
if radek_stavu:
    for l in radky[cislo_stavu - 1:]:
        if blok and (not l.strip() or _je_ukonceni(l)):
            break
        blok.append(l)
        if len(blok) >= MAX_BLOK:
            strop_dosazen = True
            break
text_bloku = "\n".join(blok)

# Dvojice na ŘÁDKU S KLÍČEM (to je TVAR — a zůstává i kvůli zpětné
# kompatibilitě výstupu a testu `_analyza/test-hlavicka-tvar.py`)
# a dvojice v CELÉM BLOKU (to je ta oprava H189).
dvojice = VZOR_DVOJICE.findall(radek_stavu) if radek_stavu else []
dvojice_bloku = VZOR_DVOJICE.findall(text_bloku)

# ⚠ KONFLIKT SE MUSÍ POVÍDAT (H189): kdyby se táž dvojice v bloku objevila
# dvakrát s RŮZNOU sha, čtení z bloku by ji „přebilo" — a tichý přepis je horší
# než hlasitá vada. Konflikty se proto sbírají a vypisují jako varování.
konflikty = []
for jmeno, sha in dvojice_bloku:
    klic = jmeno.lower()
    if klic in tvrzene_head and tvrzene_head[klic] != sha:
        konflikty.append((klic, tvrzene_head[klic], sha))
    tvrzene_head[klic] = sha
vsechny_sha = set(re.findall(r"\b([0-9a-f]{7,40})\b", text))
tvrzene_casy = re.findall(r"(\d{1,2}\.\s*\d{1,2}\.\s*\d{4}[^\n]{0,12}UTC)", text)

# ⚠ TVAR JE SAMOSTATNÁ KONTROLA (naměřeno 6. 10. 2026 archivovaným nástrojem
# `zadani-hlavicka-tvar.py`): když je popis na jednom řádku a dvojice na
# DVOU, kontrola níž vypíše „zadání netvrdí žádný commit" — a to **vypadá jako
# vada brány**, ale je to **vada ZÁPISU**. Tenhle stav se musí pojmenovat, ne
# schovat do dvou otazníků u repů: kdo hledá vadu, hledá ji pak v gitu, kde není.
#
# ⚠ POZOR (H189): TVAR se i po opravě měří na ŘÁDKU S KLÍČEM, ne na bloku.
# Je to záměr: zalamovaná hlavička je vada ZÁPISU — ale dvojice se už čtou
# z CELÉHO BLOKU, takže se POROVNAJÍ i tehdy, když je zápis zalomený.
# Vada zápisu a slepota brány jsou DVĚ RŮZNÉ VĚCI a výstup je musí rozlišit.
vada_tvaru = ""
if not radek_stavu:
    vada_tvaru = "hlavička NEMÁ řádek s klíčem „Stav obou repů“"
elif not dvojice:
    vada_tvaru = ("řádek se stavem repů NETVRDÍ žádný commit `<repo>` = `<sha>` "
                  "(dvojic na něm: 0)")

print("\n--- HLAVIČKA: co zadání tvrdí -------------------------------------")
print(f"  řádek se stavem repů: "
      f"{'NALEZEN (ř. ' + str(cislo_stavu) + ')' if radek_stavu else 'CHYBÍ'}")
print(f"  dvojic `<repo>` = `<sha>` na tom řádku: {len(dvojice)}")
# ⚠ VELIKOST OKNA SE MUSÍ VYKÁZAT (H189): „velkorysé okno není opatrnost, je to
# slepota" — ale okno, jehož velikost NIKDO NEVIDÍ, je slepota taky. Proto se
# vypisuje rozsah řádků, počet řádků i znaků a případné uříznutí stropem.
# (Formulace `řádků {n}` je záměrná: `g3` čte čítač brány vzorem
# `(\d+) řádků` a bere POSLEDNÍ výskyt — kdyby tu stálo „7 řádků", začal by
# `g3` u téhle brány vykazovat velikost okna místo velikosti dokumentu.)
if radek_stavu:
    print(f"  OKNO HLAVIČKY (blok pro dvojice): ř. {cislo_stavu}–"
          f"{cislo_stavu + len(blok) - 1} · velikost okna: řádků {len(blok)},"
          f" znaků {len(text_bloku)}"
          + (f"  ⚠ STROP OKNA ({MAX_BLOK} ř.) DOSAŽEN — blok je uříznutý!"
             if strop_dosazen else ""))
else:
    print("  OKNO HLAVIČKY (blok pro dvojice): klíč se nenašel"
          " · velikost okna: řádků 0, znaků 0")
print(f"  dvojic `<repo>` = `<sha>` v CELÉM BLOKU: {len(dvojice_bloku)}")
print(f"  TVAR HLAVIČKY: {'OK' if not vada_tvaru else 'VADA — ' + vada_tvaru}")
print(f"  tvrzené commity: {tvrzene_head or '(žádné — viz TVAR výš)'}")
print(f"  různých sha v celém dokumentu:    {len(vsechny_sha)}")
print(f"  tvrzených časů měření:            {len(tvrzene_casy)}")

# ── 2) ŽIVÝ STAV ───────────────────────────────────────────────────────────
zivy = zivy_stav()
print("\n--- ŽIVÝ STAV obou repů ------------------------------------------")
for jmeno, s in zivy.items():
    print(f"  {jmeno:11} HEAD {s['head'][:9]}  origin/main..HEAD={s['pred']}  "
          f"změněných={s['zmenene']}  poslední commit {s['cas']}")

# ── 3) POROVNÁNÍ: sedí tvrzení na skutečnost? ──────────────────────────────
print("\n--- SEDÍ ZADÁNÍ NA SKUTEČNOST? -----------------------------------")
varovani = 0
if vada_tvaru:
    # ⚠ JEDNA příčina = JEDNO varování: kdyby se počítalo i za každý repo níž,
    # vyšlo by „3 varování" z jediné vady ZÁPISU — a to číslo mate.
    print(f"  ⚠    TVAR HLAVIČKY: {vada_tvaru}")
    print("       (dvojice se čtou z CELÉHO BLOKU HLAVIČKY — jeho rozsah a"
          " velikost hlásí řádek OKNO HLAVIČKY výš)")
    varovani += 1
for klic, puvodni, nova in konflikty:
    # H189: táž dvojice dvakrát s různou sha = tichý přepis. Pojmenovat.
    print(f"  ⚠    {klic}: v bloku hlavičky je DVAKRÁT s různou sha "
          f"({puvodni[:9]} → {nova[:9]}) — platí POSLEDNÍ; zkontroluj, že se"
          f" dvojice nečte znovu (např. z řádku „Kotva pro měření“)")
    varovani += 1
for jmeno, s in zivy.items():
    tvrz = _najdi_tvrzene(jmeno)
    if not tvrz:
        if vada_tvaru:
            print(f"  ?    {jmeno}: commit se neporovnal — PŘÍČINA JE TVAR HLAVIČKY výš")
        else:
            print(f"  ?    {jmeno}: zadání netvrdí žádný commit")
            print(f"       (hledáno pod jmény: {', '.join(_mozna_jmena(jmeno))})")
            varovani += 1
        continue
    if s["head"].startswith(tvrz) or tvrz.startswith(s["head"][:len(tvrz)]):
        print(f"  OK   {jmeno}: tvrzený {tvrz[:9]} = skutečný HEAD")
        continue
    # kolik commitů od tvrzeného přibylo?
    cesta_repa = dict(REPA)[jmeno]
    kolik = git(cesta_repa, "rev-list", "--count", f"{tvrz}..HEAD")
    print(f"  ⚠    {jmeno}: zadání tvrdí {tvrz[:9]}, skutečný HEAD je {s['head'][:9]}"
          f"  → přibylo commitů: {kolik or '?'}")
    varovani += 1

# ── 3b) TVRZENÍ, KTERÁ SE NEPODAŘILO PŘIŘADIT ────────────────────────────────
# Když hlavička tvrdí commit k repu, které skript nezná, je to NÁLEZ: buď se
# repo přejmenovalo, nebo je v hlavičce jiné jméno, než jaké má adresař.
# Ticho by znamenalo „porovnal jsem všechno" — a přitom se část neporovnala.
prirazene = set()
for jmeno, _ in zivy.items():
    for kandidat in _mozna_jmena(jmeno):
        if tvrzene_head.get(kandidat):
            prirazene.add(kandidat)
nenalezene = {k: v for k, v in tvrzene_head.items() if k not in prirazene}
# ⚠ NÁLEZ H70 (5. 10. 2026, P14): tady stálo `for j, _ in zivy` — a `zivy` je
# **slovník** (klíč → stav repa), takže iterace dává **řetězce** (klíče), ne
# dvojice. `ValueError: too many values to unpack (expected 2)`.
# Ve zdravém stavu se větev **nikdy nezavolá** (`nenalezene` je prázdné), takže
# ji **žádný test neměl** — a při prvním skutečném použití spadla MÍSTO toho,
# aby poruchu vypsala (`overovani` §7.10 obráceně: červená, ale nic neřekne).
# Oprava: iteruje se přes KLÍČE (`for j in zivy`), protože `j` je jméno repa.
# Dokázáno mutačně: `_analyza/test-h70-vetev.py` tuhle větev ZAVOLÁ (fixturou
# s neznámým jménem repa) a s vrácenou vadou **zčervená** (traceback místo hlášení).
nenalezene = {k: v for k, v in nenalezene.items()
              if not any(k in _mozna_jmena(j) or j in k for j in zivy)}
if nenalezene:
    print("  ⚠    tvrzení z hlavičky, která se nepodařilo přiřadit k repu:")
    for k, v in nenalezene.items():
        # ⚠ DRUHÝ VÝSKYT TÉŽE VADY (nalezen testem `test-h70-vetev.py`,
        # 5. 10. 2026): i tady se iterovalo `for j, _ in zivy` nad slovníkem.
        # Zadání ani P14 o něm nevěděly (H70 popisoval jen řádek 196) — a to je
        # přesně to, co znamená „test musí tu větev ZAVOLAT": jeden běh na
        # fixtuře našel oba výskyty, čtení kódu jen jeden.
        print(f"       {k} = {v[:9]}  (známá jména repů: "
              f"{', '.join(j for j in zivy)})")
    varovani += 1

# ── 4) ZNÁMKY STÁRÍ V TEXTU ────────────────────────────────────────────────
preskrtane = text.count("~~") // 2
print("\n--- ZNÁMKY STÁRÍ -------------------------------------------------")
print(f"  přeškrtnutých (už neplatných) pasáží: {preskrtane}")
print(f"  výskytů „ještě ne“ / „čeká“:          "
      f"{len(re.findall(r'ještě ne|čeká|nez[aá]čat', text, re.I))}")
if preskrtane > 3:
    print("  ⚠  víc než 3 přeškrtnuté pasáže = zadání se přepisovalo po částech;")
    print("     zvaž, jestli nemá být přepsané CELÉ (starý text mate čtenáře).")
    varovani += 1

# ── 5) NÁVRATOVÝ KÓD ──────────────────────────────────────────────────────
print("\n" + "=" * 78)
if varovani:
    print(f"VÝSLEDEK: zadání je ZASTARALÉ NEBO NEPOUŽITELNÉ ({varovani} varování).")
    print("  → Než podle něj začneš pracovat, PŘEMĚŘ všechny údaje o stavu")
    print("    a zapiš to jako nález. Zadání se NEZAHOZUJE — jen se ověří.")
    if vada_tvaru:
        print("  → A JE TO VADA ZÁPISU, NE NESHODA COMMITŮ: na řádku s klíčem")
        print("    chybí dvojice `<repo>` = `<sha>` — oprav HLAVIČKU, ne zadání.")
    sys.exit(1)
print("VÝSLEDEK: zadání je použitelné — tvrzené commity sedí na živý stav.")
print("  → Stejně ověř aspoň TŘI klíčová tvrzení spuštěním (shodný commit")
print("    neznamená, že tvrzení bylo správné už při zápisu — nález N9).")
sys.exit(0)
