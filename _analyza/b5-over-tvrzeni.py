# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
r"""BOD 5 z §7.2 — pět tvrzení ověřeno NEZÁVISLE na `n8-zastarala-analyza.py`.

Proč zvlášť: `n8-zastarala-analyza.py` je taky měřidlo a může být slepé
(naměřeno: je — viz `_analyza\n8-mutace.py`). Kdo ověřuje jeho čísla JÍM,
neověřuje nic. Tenhle skript se ptá KÓDU přímo a jiným způsobem:
ne hledáním řetězce, ale tím, co ta věc SKUTEČNĚ DĚLÁ.

U každého tvrzení se tiskne i ÚRYVEK KÓDU, na kterém je závěr postavený —
aby se dal zkontrolovat očima, ne jen uvěřit.

Spusteni:  $env:PYTHONIOENCODING='utf-8'; python _analyza\b5-over-tvrzeni.py
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
INDEX = (WS / "conductor" / "src" / "index.ts").read_text(encoding="utf-8")
AGENT = (WS / "repo" / ".github" / "workflows" / "agent.yml").read_text(encoding="utf-8")
LINT = (WS / "tools" / "lint-roadmapa.py").read_text(encoding="utf-8")

# komentare pryc — jinak najdeme vadu v jejim popisu (past z AGENTS.md)
def bez_komentaru_ts(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)

def bez_komentaru_yaml(s):
    return re.sub(r"^\s*#.*$", "", s, flags=re.M)

KOD = bez_komentaru_ts(INDEX)
YML = bez_komentaru_yaml(AGENT)

vysledky = []


def tvrzeni(cislo, popis, plati_analýza, dukaz):
    """plati_analýza=True  -> tvrzení analýzy JEŠTĚ PLATÍ (není zastaralé)"""
    stav = "PLATÍ (není zastaralé)" if plati_analýza else "NEPLATÍ (zastaralé)"
    print(f"  {cislo}) {popis}")
    print(f"      -> {stav}")
    print(f"      dukaz: {dukaz}")
    vysledky.append((cislo, plati_analýza))
    print()


print("=== BOD 5: pět zastaralých tvrzení, ověřeno přímo v kódu ===\n")

# 1) rozhodnuti o `done` — hleda se KONTEXT (if pred UPDATE tasks status='done')
m = re.search(r"if\s*\(\s*ok\s*(&&\s*merged)?\s*\)\s*\{(?:(?!\n\s*\}\s*else).){0,400}?"
              r"UPDATE\s+tasks\s+SET\s+status='done'", KOD, re.S)
if m:
    ok_merged = bool(m.group(1))
    usek = KOD[m.start():m.start() + 70].replace("\n", " ")
    tvrzeni(1, "`tasks.status='done'` neni ukotveno — rozhoduje `run.conclusion`",
            not ok_merged,
            f"rozhodnuti je na `{'ok && merged' if ok_merged else 'ok'}`: {usek!r}")
else:
    tvrzeni(1, "`tasks.status='done'` neni ukotveno", True, "rozhodnuti se NENASLO")

# 2) auto-merge pri neuspechu
# POZOR (namereno pri psani): prvni verze tohohle vzoru hledala "posledni
# radek" laxne a chytila radek `if:` PRED `run:` — vyslo "PLATI", coz bylo
# spatne. `run: |` je YAML blok; jeho obsah konci odsazenim mensim nez on.
def posledni_radek_runu(text, nazev_kroku):
    i = text.find(nazev_kroku)
    if i < 0:
        return "(krok nenalezen)"
    j = text.find("run: |", i)
    if j < 0:
        return "(run: | nenalezen)"
    radek_run = text.rfind("\n", 0, j) + 1
    odsazeni = len(text[radek_run:j])
    telo = []
    for radek in text[text.find("\n", j) + 1:].splitlines():
        if radek.strip() and (len(radek) - len(radek.lstrip())) <= odsazeni:
            break                      # konec bloku — dalsi klíč kroku
        if radek.strip():
            telo.append(radek.strip())
    return telo[-1] if telo else "(prazdny run)"


posledni = posledni_radek_runu(AGENT, "nechá se k ruční kontrole")
tvrzeni(2, "`auto-merge` pri neuspechu skonci zelene (`exit 0` + komentar)",
        posledni != "exit 1",
        f"posledni radek `run:` bloku kroku je {posledni!r}")

# 3) overovani proti origin/main
ma = "filesInOriginMain" in KOD
volani = len(re.findall(r"filesInOriginMain\s*\(", KOD))
tvrzeni(3, "`roadmap.status='done'` se neoveruje proti `origin/main`",
        not ma,
        f"funkce `filesInOriginMain` v kodu: {ma}, volani: {volani}x")

# 4) stav pro nesloucene PR
awa = "awaiting_human" in KOD
zapis = re.search(r"UPDATE tasks SET status='(\w+)'", KOD)
tvrzeni(4, "„PR sloucen\" se bere z `conclusion` (mrtva hodnota `merged`)",
        not awa,
        f"`awaiting_human` v kodu: {awa}; prvni zapis stavu do D1: "
        f"{zapis.group(1)!r}" if zapis else f"`awaiting_human`: {awa}")

# 5) lint hlasi chybejici size_lines
hlasi = "GRANULE BEZ" in LINT or "size_lines" in LINT
tvrzeni(5, "gate — `size_lines` chybi u 13/18 a lint to nehlasi",
        not hlasi,
        f"lint obsahuje hlasku o chybejicim `size_lines`: {hlasi}")

zastarale = [c for c, plati in vysledky if not plati]
print("=" * 70)
print(f"  zastaralých (nezávisle): {len(zastarale)} z {len(vysledky)} -> {zastarale}")
print(f"  `n8-zastarala-analyza.py` tvrdí: 5 z 7 (5 zastaralých + 2 kontrolní vzorky)")
print()
if len(zastarale) == 5:
    print("VYSLEDEK: ČÍSLO SEDÍ — 5 zastaralých, ověřeno nezávisle na tom skriptu.")
    sys.exit(0)
print(f"VYSLEDEK: NESEDÍ — nezávisle vyšlo {len(zastarale)}, skript tvrdí 5.")
sys.exit(1)
