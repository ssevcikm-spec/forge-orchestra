r"""N3 — celý tok `FORGE_ATTEMPT` v obou kopiích `agent.yml`, řádek po řádku.

Proč: hrubý počet výskytů nestačí. Hodnota se může předávat i přes `$GITHUB_ENV`
(což je zápis do souboru, ne `env:` v YAML) — a pak rozhoduje POŘADÍ: skript,
který hodnotu čte, ji musí dostat dřív, než ji potřebuje.

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\n3-tok-attempt.py
"""
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
KOPIE = [
    ("šablona", WS / "orchestra/repo/.github/workflows/agent.yml"),
    ("hra", WS / "games/uo-shadows/.github/workflows/agent.yml"),
]

for jmeno, cesta in KOPIE:
    text = cesta.read_text(encoding="utf-8")
    radky = text.splitlines()
    print("=" * 78)
    print(f"{jmeno}: {cesta.relative_to(WS)}   ({len(radky)} řádků)")
    print("=" * 78)
    for i, radek in enumerate(radky, 1):
        if "ATTEMPT" in radek.upper():
            print(f"  {i:4} | {radek.rstrip()}")
    print(f"  výskytů 'FORGE_ATTEMPT': {text.count('FORGE_ATTEMPT')}")
    print(f"  výskytů 'GITHUB_ENV':    {text.count('GITHUB_ENV')}")
    # Kdo pise do GITHUB_ENV a co
    for i, radek in enumerate(radky, 1):
        if "GITHUB_ENV" in radek:
            for j in range(max(0, i - 4), min(len(radky), i + 2)):
                print(f"       kontext {j+1:4} | {radky[j].rstrip()[:100]}")
            print("       ---")
