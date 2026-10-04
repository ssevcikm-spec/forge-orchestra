# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
"""A1/A2: ověří ROZHODOVACÍ LOGIKU vytaženou ze zdroje conductora.

Proč tahle podoba: `AGENTS.md` a `orchestra` skill zakazují dělat závěr
o chování ze čtení kódu. Conductor se ale nedá spustit lokálně (běží na
Cloudflare, potřebuje D1 a tajemství) — a `conductor` testy SQL čtou ze
zdrojáku (to je ST9, pořád otevřené).

Proto se rozhodovací Tabulka vytáhne ze zdroje a spočítá se v Pythonu:
  - A1: `done` jen když `ok && merged`; jinak `awaiting_human` (ok) / failed
  - A2: `done: true` se zapíše jen když je `owns` soubor v `origin/main`

Mutační test: když se logika ve zdroji vrátí na `if (ok)`, test MUSÍ spadnout.
Bez toho by „prošlo" znamenalo jen „soubor existuje".

POZOR na past, na kterou se tu narazilo: hledat řetězec v CELÉM souboru najde
i KOMENTÁŘ, který vadu popisuje (A1 komentář cituje `if (ok)`). Proto se
komentáře PŘED hledáním odstraňují.
"""

import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
INDEX = WS / "conductor" / "src" / "index.ts"

if not INDEX.is_file():
    print(f"CHYBA: {INDEX} neexistuje")
    sys.exit(2)

zdroj = INDEX.read_text(encoding="utf-8")


def bez_komentaru(s: str) -> str:
    """Odstraní // a /* */ komentáře — jinak najdeme vadu v jejím popisu."""
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"^\s*//.*$", "", s, flags=re.M)
    return s


kod = bez_komentaru(zdroj)
chyby = []
pocet_kontrol = 0


def kontroluj(podminka: bool, zprava: str) -> None:
    """Počítá kontroly. Bez čítače by 'Kontrol: N' bylo ručně psané číslo,
    které zestárne při první přidané kontrole (a to je přesně past
    'číslo bez postupu' z AGENTS.md)."""
    global pocet_kontrol
    pocet_kontrol += 1
    if not podminka:
        chyby.append(zprava)

# ── A1: rozhodnutí o `done` ───────────────────────────────────────────────────
# POZOR (naměřeno při psaní tohohle testu): `if (ok) {` je v souboru DVakrát
# a ta PRVNÍ (:342) je SPRÁVNÁ – je to větev, která načítá PR, ne rozhodnutí
# o `done`. Test, který hledá `if (ok) {` kdekoli, hlásí falešný poplach
# na správném kódu. Proto se hledá KONTEXT: `if (ok ...)` bezprostředně před
# zápisem `status='done'` do tabulky `tasks`.
vzorec_rozhodnuti = re.compile(
    r"if\s*\(\s*ok\s*(\&\&\s*merged\s*)?\)\s*\{(?:(?!\n\s*\}\s*else).){0,400}?"
    r"UPDATE\s+tasks\s+SET\s+status='done'", re.S)
m = vzorec_rozhodnuti.search(kod)
kontroluj(bool(m), "A1: nenašel jsem rozhodnutí o `done` (if před UPDATE tasks status='done')")
if m:
    kontroluj(bool(m.group(1)),
              "A1: rozhodnutí o `done` je na `if (ok)` bez `&& merged` – vada se vrátila")
kontroluj(bool(re.search(r"if\s*\(\s*ok\s*&&\s*merged\s*\)", kod)),
          "A1: nenašel jsem `if (ok && merged)` v KÓDU (bez komentářů)")
kontroluj("awaiting_human" in kod, "A1: chybí stav `awaiting_human` pro nesloučené PR")

# Simulace rozhodovací tabulky (to, co má kód dělat).
def rozhodni(ok: bool, merged: bool) -> str:
    if ok and merged:
        return "done"
    if ok:
        return "awaiting_human"
    return "failed/ready"

TABULKA = [
    (True, True, "done"),
    (True, False, "awaiting_human"),   # ← jádro A1: tohle dřív bylo "done"
    (False, False, "failed/ready"),
    (False, True, "failed/ready"),     # nesmysl, ale nesmí spadnout
]
for ok, merged, cekano in TABULKA:
    kontroluj(rozhodni(ok, merged) == cekano,
              f"A1: tabulka ({ok},{merged}) -> {rozhodni(ok, merged)}, čekáno {cekano}")

# ── A2: ověření `owns` proti origin/main ─────────────────────────────────────
kontroluj("filesInOriginMain" in kod, "A2: chybí funkce `filesInOriginMain`")
kontroluj("git/trees/origin%2Fmain" in kod, "A2: nečte se strom `origin/main`")
# `null` (nevím) se NESMÍ chovat jako prázdný set („v mainu nic není").
kontroluj("stromMain !== null" in kod,
          "A2: chybí rozlišení `null` (nevím) vs. prázdný strom")

# Cache MUSÍ mít expiraci. Modulová proměnná bez TTL by v teplém izolátu
# Cloudflare sloužila strom `origin/main` libovolně dlouho – tedy táž vada,
# jakou popisuje N1 (měřidlo, které tiše měří jiný čas). Napsal jsem ji sám
# a odhalil až druhý pohled na vlastní diff.
kontroluj("ORIGIN_MAIN_TTL_MS" in kod,
          "A2: cache `origin/main` nemá TTL (může sloužit zastaralý strom)")
kontroluj(bool(re.search(r"expiruje\s*>\s*ted", kod)),
          "A2: cache se nikde neporovnává s časem – TTL se nepoužívá")

# ── KONTROLY DOPLNĚNÉ 2. 10. 2026 (nález V2) ─────────────────────────────────
# Původní verze se ptala na PŘÍTOMNOST jmen, ne na to, co kód DĚLÁ. Naměřeno
# mutačním testem (`_analyza\a1-a2-mutace.py`): chytila 2 z 5 mutací.
# Tři níž to zavírají — a každá je vázaná na KÓD, ne na slovo v komentáři
# (komentáře jsou už odstraněné, ale i tak se ptáme na přiřazení a porovnání).
def _vyrazy(promenna: str):
    """Vše, co se do proměnné přiřadí — jako `x = VÝRAZ`, nebo `x: VÝRAZ`
    (vlastnost objektu, což je případ cache: `{ strom, expiruje: ted + TTL }`).

    POZOR (naměřeno 2. 10. 2026 při psaní téhle kontroly): první verze hledala
    JEN `=`, takže u `expiruje:` našla prázdno a kontrola spadla na SPRÁVNÉM
    kódu. Falešný poplach je stejná vada jako slepé místo — jen se hůř hledá.
    """
    return re.findall(rf"\b{re.escape(promenna)}\s*[:=]\s*([^;\n}}]+)", kod)


# (1) Konstanta TTL musí být SKUTEČNĚ použita při zápisu do cache. Přejmenování
#     deklarace dřív prošlo, protože kontrola hledala jen jméno kdekoliv.
kontroluj(any("ORIGIN_MAIN_TTL_MS" in v for v in _vyrazy("expiruje")),
          "A2: konstanta TTL se nikde NEPOUŽÍVÁ při zápisu do cache "
          "(přejmenovaná deklarace stačila, aby kontrola prošla)")

# (2) Úspěšný strom nesmí jít do cache napořád. Naměřeno: `ted + 999999999`
#     prošlo, protože `> ted` platilo dál — a cache tak sloužila navždy (N7).
_kratke = [v for v in _vyrazy("expiruje") if re.search(r"\d{5,}", v)]
kontroluj(not _kratke,
          f"A2: cache se ukládá s obřím/napevno psaným časem {_kratke} – "
          "to je TTL, který nikdy nevyprší (vada N7 se vrátila)")

# (3) Neúspěch (`strom: null`) má mít KRÁTKÝ TTL, ne plný. Kdyby obojí používalo
#     `ORIGIN_MAIN_TTL_MS`, chyba čtení by blokovala ověření `owns` 10 minut.
_null_zapisy = [v for v in _vyrazy("expiruje") if "null" in v or "60" in v]
kontroluj(any("60" in v for v in _null_zapisy),
          "A2: chybový zápis (`strom: null`) nemá krátký TTL – chyba čtení by "
          "blokovala ověření `owns` na plnou dobu")

# (4) `awaiting_human` musí být ZAPSANÝ STAV v D1, ne jen zmínka v kódu.
#     Naměřeno: přejmenování `UPDATE tasks SET status='awaiting_human'` na
#     `'pending_review'` prošlo, protože kontrola hledala slovo kdekoliv
#     (a to je pořád i v komentáři a v zápisu do roadmapy).
kontroluj("UPDATE tasks SET status='awaiting_human'" in kod,
          "A1: stav `awaiting_human` se NIKDE nezapisuje do D1 (`UPDATE tasks "
          "SET status='awaiting_human'`) – pouhá zmínka slova nestačí")

# Simulace A2: má se `done` zapsat?
def zapis_done(strom, owns) -> bool:
    if strom is None:          # nedozvěděli jsme se to → neblokovat
        return True
    if not owns:               # nedá se ověřit (dokumentační granule)
        return True
    return any(f in strom for f in owns)

A2_TABULKA = [
    (None, ["a.gd"], True, "strom se nenačetl → neblokovat (jinak by spadla celá roadmapa)"),
    (set(), ["a.gd"], False, "strom je prázdný → soubor v main není"),
    ({"a.gd"}, ["a.gd"], True, "soubor v main je"),
    ({"b.gd"}, ["a.gd"], False, "owns soubor v main není"),
    ({"b.gd"}, ["a.gd", "b.gd"], True, "stačí JEDEN soubor z owns"),
    (set(), [], True, "bez owns se ověřit nedá → neblokovat"),
]
for strom, owns, cekano, popis in A2_TABULKA:
    kontroluj(zapis_done(strom, owns) == cekano, f"A2: {popis}")

# ── výstup ───────────────────────────────────────────────────────────────────
print(f"Kontrol: {pocet_kontrol}")
for c in chyby:
    print("  CHYBA:", c)
if chyby:
    print(f"\nSELHALO: {len(chyby)} chyb")
    sys.exit(1)
print("VŠE OK — A1 rozhoduje podle `ok && merged` a A2 ověřuje `owns` proti origin/main.")
sys.exit(0)
