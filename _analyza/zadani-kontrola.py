# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
# Dokumenty, ktere zustaly STANICI (D6): na ty se saha absolutne.
_STANICE_DOKUMENTY = _pl.Path(r"C:\Users\Ssevc\Local-Deepseek")
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
REPA = [("orchestra", WS), ("uo-shadows", HRA)]


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
# Čte se proto KONKRÉTNÍ řádek „Stav obou repů při psaní:" a z něj dvojice
# `repo = <sha>`. Když řádek chybí, je to varování — ne ticho.
hlavicka = "\n".join(radky[:30])
tvrzene_head = {}
radek_stavu = ""
for l in radky[:30]:
    if "Stav obou repů" in l or "Stav obou repu" in l:
        radek_stavu = l
        break
if radek_stavu:
    for jmeno, sha in re.findall(r"`?([A-Za-z0-9_-]+)`?\s*=\s*`?([0-9a-f]{7,40})`?", radek_stavu):
        tvrzene_head[jmeno.lower()] = sha
vsechny_sha = set(re.findall(r"\b([0-9a-f]{7,40})\b", text))
tvrzene_casy = re.findall(r"(\d{1,2}\.\s*\d{1,2}\.\s*\d{4}[^\n]{0,12}UTC)", text)

print("\n--- HLAVIČKA: co zadání tvrdí -------------------------------------")
print(f"  řádek se stavem repů: {'NALEZEN' if radek_stavu else 'CHYBÍ (varování)'}")
print(f"  tvrzené commity: {tvrzene_head or '(žádné — hlavička podle §3 chybí)'}")
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
if not radek_stavu:
    print("  ⚠    hlavička podle `PREDAVANI-SESSION.md` §3 chybí — zadání si nese")
    print("       jen text, ne to, PROTI ČEMU bylo měřeno. Doplň ji.")
    varovani += 1
for jmeno, s in zivy.items():
    tvrz = tvrzene_head.get(jmeno.lower())
    if not tvrz:
        print(f"  ?    {jmeno}: zadání netvrdí žádný commit")
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
    sys.exit(1)
print("VÝSLEDEK: zadání je použitelné — tvrzené commity sedí na živý stav.")
print("  → Stejně ověř aspoň TŘI klíčová tvrzení spuštěním (shodný commit")
print("    neznamená, že tvrzení bylo správné už při zápisu — nález N9).")
sys.exit(0)
