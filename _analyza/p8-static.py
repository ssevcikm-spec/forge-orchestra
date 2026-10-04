r"""P8 — statické kontroly k 11 tvrzením zadání (měření, ne čtení dojmem).

Ptá se na věci, které zadání TVRDÍ, ale které se dají ověřit jen pohledem do
kódu — a u každé vypíše, čím to změřilo (aby se dalo opakovat).

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\p8-static.py
"""
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
HRA = WS / "games" / "uo-shadows"
ORCH = WS / "orchestra"


def read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def bez_komentaru_gd(t: str) -> str:
    """GDScript: pryč s # komentáři (jinak komentář popisující vadu vypadá jako vada)."""
    out = []
    for line in t.splitlines():
        i = line.find("#")
        out.append(line if i < 0 else line[:i])
    return "\n".join(out)


print("═══ 1. `.has(` v herním repu — kolik je vada a kolik je Dictionary/Array ═══")
vse = []
for p in sorted(HRA.glob("scripts/*.gd")):
    for i, line in enumerate(read(p).splitlines(), 1):
        if ".has(" in line:
            vse.append((p.name, i, line.strip(), "#" in line.split(".has(")[0]))
print(f"  výskytů `.has(` v scripts/*.gd: {len(vse)}")
for n, i, l, kom in vse:
    print(f"    {n}:{i}  {'(komentář) ' if kom else ''}{l[:88]}")

print("\n═══ 2. Kdo volá `combat`? (tvzení: v game.gd není instancovaný) ═══")
hits = [(p.name, i, l.strip()) for p in sorted(HRA.glob("scripts/*.gd"))
        for i, l in enumerate(read(p).splitlines(), 1) if "combat" in l.lower()]
for h in hits:
    print(f"    {h[0]}:{h[1]}  {h[2][:88]}")
print(f"  celkem zmínek 'combat' v scripts/: {len(hits)}")

print("\n═══ 3. `world.gd` — je v main, nebo v _retired? ═══")
print(f"    scripts/world.gd existuje: {(HRA / 'scripts/world.gd').is_file()}")
print(f"    _retired/world.gd existuje: {(HRA / '_retired/world.gd').is_file()}")

print("\n═══ 4. `main.json` — kolik markerů a jakých ═══")
mj = HRA / "assets" / "levels" / "main.json"
if mj.is_file():
    d = json.loads(read(mj))
    markery = d.get("markers") or d.get("objekty") or []
    print(f"    klíče: {list(d.keys())}")
    print(f"    markerů: {len(markery)}")
    for m in markery:
        print(f"      {json.dumps(m, ensure_ascii=False)[:100]}")

print("\n═══ 5. `player.gd` — které metody má (tvrzení: move/hp/die nejsou) ═══")
pg = HRA / "scripts" / "player.gd"
if pg.is_file():
    t = read(pg)
    metody = re.findall(r"^func\s+(\w+)", t, re.M)
    print(f"    {pg.name}: {len(t)} znaků, metody: {metody}")
    for jmeno in ("move", "hp", "max_hp", "mana", "inventory", "die", "snapshot", "restore"):
        print(f"      obsahuje `{jmeno}`: {jmeno in t}")

print("\n═══ 6. Testy — volají `snapshot`/`restore`/`die`/`hp`/`inventory`? ═══")
rt = HRA / "tests" / "run_tests.gd"
if rt.is_file():
    t = bez_komentaru_gd(read(rt))
    for jmeno in ("snapshot", "restore", "die(", "hp", "inventory", "move", "gather"):
        print(f"    `{jmeno}` v KÓDU testů: {t.count(jmeno)}x")
    print(f"    `has_method` v KÓDU testů: {t.count('has_method')}x")
    print(f"    `iso_position` v KÓDU testů: {t.count('iso_position')}x")
    for i, l in enumerate(t.splitlines(), 1):
        if "iso_position" in l:
            print(f"      run_tests.gd:{i}  {l.strip()[:88]}")
    # je blok podmíněný has_method("move")?
    for i, l in enumerate(read(rt).splitlines(), 1):
        if 'has_method("move")' in l:
            print(f"    PODMÍNKA run_tests.gd:{i}  {l.strip()[:88]}")

print("\n═══ 7. `player.gd:40` — který řádek zakazuje test ═══")
if pg.is_file():
    radky = read(pg).splitlines()
    for i in (38, 39, 40, 41, 42):
        if i <= len(radky):
            print(f"      player.gd:{i}  {radky[i-1].strip()[:88]}")

print("\n═══ 8. Kolik nástrojů v `_analyza` ZAPISUJE (pojistka sekce L) ═══")
vzor = re.compile(r"write_text|write_bytes|copyfile|copy2|writeFileSync")
zap, ctou = [], []
for p in sorted(WS.glob("_analyza/*.py")) + sorted(WS.glob("_analyza/*.mjs")):
    (zap if vzor.search(read(p)) else ctou).append(p.name)
print(f"    zapisujících: {len(zap)} -> {zap}")
print(f"    čtoucích:     {len(ctou)}")

print("\n═══ 9. `AGENTS.md` — kolik řádků s číslem (nález N9: 80 / 16 s jednotkou) ═══")
ag = read(WS / "AGENTS.md").splitlines()
císlo = [l for l in ag if re.search(r"\d", l)]
jednotka = [l for l in ag if re.search(r"\d+\s*(%|sloupc|řádk|soubor|míst|znak|B\b|kB|h\b|min|kontrol|test)", l)]
print(f"    řádků celkem: {len(ag)}, s číslicí: {len(císlo)}, s číslem i jednotkou: {len(jednotka)}")

print("\n═══ 10. Je `_analyza` verzovaná? (git v kořeni workspace) ═══")
print(f"    orchestra/.git: {(ORCH / '.git').exists()}, hra/.git: {(HRA / '.git').exists()}, "
      f"workspace/.git: {(WS / '.git').exists()}")
