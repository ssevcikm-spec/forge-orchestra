# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
"""N8: ověří, která tvrzení ANALYZA-HLOUBKOVA-ORCHESTRA-2.md UŽ NEPLATÍ.

PROČ TOHLE EXISTUJE
-------------------
Analýza druheho kola vznikla 2. 10. 2026 v 06:10 UTC a popisuje STAV KÓDU
v tom čase. Ve 08:38-08:52 téhož dne provedla jiná session plán A1-A4
(IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md) a kód ZMĚNILA.

Tím vzniklo přesně to, o čem analýza je: **dokument si hlásí stav, který se
rozešel se stavem, který je vidět v kódu.** Nikdo to neporovnává.

Tenhle skript to porovnává: u klíčových tvrzení analýzy se ptá KÓDU, jestli
ještě platí. Není to náhrada analýzy - je to její DATUM SPOTŘEBY.

POZOR na past: hledat v kódu řetězec nestačí - najde se i v KOMENTÁŘI, který
vadu popisuje (přesně to se stalo u A1, kde komentář cituje `if (ok)`).
Proto se komentáře odstraňují PŘED hledáním.
"""

import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
ANALYZA = WS / "ANALYZA-HLOUBKOVA-ORCHESTRA-2.md"
INDEX = WS / "conductor" / "src" / "index.ts"
AGENT_SABLONA = WS / "repo" / ".github" / "workflows" / "agent.yml"
AGENT_HRA = _HRA / ".github" / "workflows" / "agent.yml"


def bez_komentaru(s: str) -> str:
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"^\s*//.*$", "", s, flags=re.M)
    s = re.sub(r"^\s*#.*$", "", s, flags=re.M)
    return s


if not INDEX.is_file():
    print(f"CHYBA: {INDEX} neexistuje")
    sys.exit(2)

index_kod = bez_komentaru(INDEX.read_text(encoding="utf-8"))
agent_kod = bez_komentaru(AGENT_SABLONA.read_text(encoding="utf-8"))
analyza = ANALYZA.read_text(encoding="utf-8") if ANALYZA.is_file() else ""


# ── POMOCNÉ KONTROLY DOPLNĚNÉ 2. 10. 2026 (nález V3) ─────────────────────────
# Proč: původní tvrzení se ptala na PŘÍTOMNOST SLOVA, ne na to, co kód DĚLÁ.
# Naměřeno mutačním testem (`_analyza\n8-mutace.py`) — dvě slepá místa:
#   (a) přejmenování `UPDATE tasks SET status='awaiting_human'` na jiný stav
#       prošlo, protože slovo `awaiting_human` zůstalo v komentáři a v zápisu
#       do roadmapy → skript tvrdil „zastaralé", i když stav v D1 zmizel;
#   (b) přejmenování FUNKCE (deklarace) při zachování volání = rozbitý kód,
#       ale skript hledal jen jméno, takže rozdíl neviděl.
# Platí, že se ptáme na KÓD (komentáře jsou odstraněné) a na to, co dělá.
def zapsane_stavy_D1() -> set[str]:
    """Které stavy se SKUTEČNĚ zapisují do `tasks` (ne co se o nich píše).

    POZOR (naměřeno 2. 10. 2026, druhá verze téhle kontroly): první verze
    brala jen PRVNÍ výskyt (`re.search`) — a ten je `status='done'`. Tvrzení
    o `awaiting_human` tím pádem vyšlo jako AKTUÁLNÍ, i když stav v kódu je.
    V `index.ts` je **17 zápisů stavu**, takže se musí projít VŠECHNY.
    """
    return set(re.findall(r"UPDATE\s+tasks\s+SET\s+status='(\w+)'", index_kod))


def funkce_je_volana(jmeno: str) -> bool:
    """Je funkce DEKLAROVANÁ **a** VOLANÁ? Když chybí jedno, kód je rozbitý —
    a to je nález, ne „tvrzení je aktuální"."""
    deklarovana = bool(re.search(rf"(?:async\s+)?function\s+{re.escape(jmeno)}\s*\(", index_kod))
    volana = bool(re.search(rf"(?<![\w.]){re.escape(jmeno)}\s*\(", index_kod))
    return deklarovana and volana

# (popis tvrzení v analýze, test, vysvětlení)
# KONTRAKT: test vrací True, když TVRZENÍ ANALÝZY JEŠTĚ PLATÍ (kód mu odpovídá).
# POZOR — první verze tohohle skriptu měla podmínku OBRÁCENĚ a hlásila
# „0 zastaralých" u kódu, který jsem sám změnil. Odhalilo se to jen tím, že
# jsem znal SPRÁVNÝ výsledek (A1-A4 kód změnily) — což je přesně ten
# „známý chybný případ", který AGENTS.md u metrik vyžaduje.
TVRZENI = [
    ("§3.1/⑪: `tasks.status='done'` není ukotveno — rozhoduje `run.conclusion`",
     lambda: not re.search(r"if\s*\(\s*ok\s*&&\s*merged\s*\)", index_kod),
     "A1: `done` teď závisí na `ok && merged` → tvrzení NEPLATÍ"),

    ("§3.2: `auto-merge` při neúspěchu skončí zeleně (`exit 0` + komentář)",
     lambda: not re.search(r'gh pr comment.*?exit 1', agent_kod, re.S),
     "A3: za krokem je `exit 1` → tvrzení NEPLATÍ"),

    ("§⑪/2: `roadmap.status='done'` se neověřuje proti `origin/main`",
     lambda: not funkce_je_volana("filesInOriginMain"),
     "A2: ověřuje se proti stromu `origin/main` → tvrzení NEPLATÍ. "
     "POZOR: ptáme se na DEKLARACI I VOLÁNÍ — dokud se hledalo jen jméno, "
     "prošlo i přejmenování funkce, po kterém kód volá neexistující funkci"),

    ("§⑪/15: „PR sloučen\" se bere z `conclusion` (S33 — mrtvá hodnota `merged`)",
     lambda: "awaiting_human" not in zapsane_stavy_D1(),
     "A1/S33: do D1 se zapisuje stav `awaiting_human` → tvrzení NEPLATÍ. "
     "POZOR: ptáme se na ZAPSANÝ STAV (procházejí se VŠECHNY zápisy), "
     "ne na slovo v kódu — pouhá zmínka nestačí"),

    ("§3.2: gate — `size_lines` chybí u 13/18 a lint to nehlásí",
     lambda: "GRANULE BEZ 'size_lines'" not in (WS / "tools" / "lint-roadmapa.py").read_text(encoding="utf-8"),
     "A4a: lint to hlásí → tvrzení NEPLATÍ"),

    # ── KONTROLNÍ VZORKY: tvrzení, která A1-A4 NEZMĚNILY ─────────────────────
    # Kdyby tu byly jen „zastaralé" položky, skript by mohl být slepý (vracet
    # pořád totéž) a nikdo by to nepoznal. Tyhle dvě MUSTÍ vyjít jako aktuální —
    # je to týž princip jako „metriku ověř na známém správném i chybném případu".
    ("§⑪/4: `done_note` je mrtvé pole (0 čtenářů v kódu)",
     lambda: not any("done_note" in p.read_text(encoding="utf-8", errors="replace")
                     for p in (WS).rglob("*")
                     if p.is_file() and p.suffix in (".ts", ".mjs", ".js", ".py")
                     and "node_modules" not in str(p)),
     "kontrolní vzorek — A1-A4 se ho nedotkly, má vyjít jako AKTUÁLNÍ"),

    ("§⑪/9: `runs.artifacts` je mrtvý sloupec (zapisuje se, nikdo nečte)",
     lambda: not re.search(r"SELECT[^;]*artifacts", index_kod, re.I | re.S),
     "kontrolní vzorek — sloupec se pořád jen zapisuje"),
]

print("=" * 78)
print("N8 — JE ANALÝZA JEŠTĚ PLATNÁ? (porovnání s kódem, ne s dokumentem)")
print("=" * 78)
print(f"  analyzovaný dokument: {ANALYZA.name}  ({len(analyza)} znaků)")
print()

zastarale = 0
for popis, plati, vysvetleni in TVRZENI:
    try:
        # `plati()` == True  → tvrzení analýzy kódu ještě odpovídá
        # `plati()` == False → kód se rozešel s analýzou = ZASTARALÉ
        jeste_plati = plati()
    except Exception as e:  # soubor může chybět
        print(f"  ?  {popis}\n     (nepodařilo se ověřit: {e})")
        continue
    if jeste_plati:
        print(f"  OK (aktuální): {popis}")
    else:
        zastarale += 1
        print(f"  ⚠ ZASTARALÉ: {popis}\n     → {vysvetleni}")

print()
print(f"  zastaralých tvrzení: {zastarale} z {len(TVRZENI)}")
print()
if zastarale:
    print("ZÁVĚR: analýza je SNAPSHOT k 2. 10. 2026 06:10 UTC a v některých")
    print("tvrzeních se rozešla s kódem. Kdo ji čte jako POPIS SOUČASNOSTI,")
    print("čte jiný stav, než jaký je. Proto má u sebe datum a odkaz na to,")
    print("co z ní bylo provedeno (A1-A4 = IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md).")
    sys.exit(0)  # není to vada kódu, je to nález o dokumentu
print("ZÁVĚR: všechna kontrolovaná tvrzení analýzy kódu ještě odpovídají.")
sys.exit(0)
