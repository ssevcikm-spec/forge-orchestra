r"""Podpůrné měření k N3: co je v jobu `agent` v obou kopiích `agent.yml`.

Vypíše kroky, jejich `env` a `run` (zkráceně), a kdo FORGE_ATTEMPT nastavuje.
Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\n3-kroky.py
"""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("CHYBA: chybí PyYAML")
    sys.exit(2)

KOPIE = [
    ("šablona", "orchestra/repo/.github/workflows/agent.yml"),
    ("hra", "games/uo-shadows/.github/workflows/agent.yml"),
]

for jmeno, cesta in KOPIE:
    d = yaml.safe_load(open(cesta, encoding="utf-8"))
    print("=" * 76)
    print(f"{jmeno}: {cesta}")
    print("=" * 76)
    for jn, job in d["jobs"].items():
        kroky = job.get("steps") or []
        print(f"\n  job {jn!r}  ({len(kroky)} kroků)")
        for i, s in enumerate(kroky):
            e = s.get("env") or {}
            nazev = s.get("name", "?")
            if jn == "agent":
                print(f"    {i:2} {nazev!r}")
                if e:
                    print(f"        env: {sorted(e.keys())}")
                run = str(s.get("run", ""))
                if run:
                    prvni = [l.strip() for l in run.splitlines() if l.strip()][:2]
                    print(f"        run: {' | '.join(prvni)[:110]}")
            elif "FORGE_ATTEMPT" in e:
                print(f"    {i:2} {nazev!r}  <-- FORGE_ATTEMPT")

# Kdo ve hře nastavuje FORGE_*}
print("\n" + "=" * 76)
print("KDY A JAK SE FORGE_ATTEMPT PŘEDÁVÁ DÁL (hledá se v obou kopiích)")
print("=" * 76)
for jmeno, cesta in KOPIE:
    text = open(cesta, encoding="utf-8").read()
    print(f"\n{jmeno}: `FORGE_ATTEMPT` v souboru {text.count('FORGE_ATTEMPT')}x")
    for i, radek in enumerate(text.splitlines(), 1):
        if "FORGE_ATTEMPT" in radek:
            print(f"  {i:4} {radek.rstrip()}")
