r"""N3 — kde je FORGE_ATTEMPT v obou kopiích `agent.yml` a co z toho plyne.

Nález N3 zněl: „v herním repu je FORGE_ATTEMPT v JINÉM KROKU než v šabloně."
Otázka, kterou je potřeba dořešit: je to vada, nebo jen jiný název téhož kroku?
Rozhoduje ROZSAH PLATNOSTI — `env` na úrovni JOBU platí pro všechny kroky,
`env` na úrovni KROKU jen pro ten jeden.

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\n3-kde-je-forge-attempt.py
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

print("=" * 78)
print("N3 — ROZSAH PLATNOSTI `FORGE_ATTEMPT` V OBOU KOPIÍCH `agent.yml`")
print("=" * 78)

verdikt = {}
for jmeno, cesta in KOPIE:
    d = yaml.safe_load(open(cesta, encoding="utf-8"))
    print(f"\n--- {jmeno}: {cesta}")
    for jn, job in d["jobs"].items():
        jen = job.get("env") or {}
        ma_na_jobu = "FORGE_ATTEMPT" in jen
        kroky_s_env = []
        kroky_s_run = []
        for i, s in enumerate(job.get("steps") or []):
            nazev = s.get("name", f"(krok {i})")
            if "FORGE_ATTEMPT" in (s.get("env") or {}):
                kroky_s_env.append((i, nazev))
            if "FORGE_ATTEMPT" in str(s.get("run", "")):
                kroky_s_run.append((i, nazev))
        print(f"  job {jn!r}")
        print(f"    env JOBU obsahuje FORGE_ATTEMPT: {ma_na_jobu}"
              + (f"  (= {jen['FORGE_ATTEMPT']!r})" if ma_na_jobu else ""))
        print(f"    kroků s `env: FORGE_ATTEMPT`: {[n for _, n in kroky_s_env]}")
        print(f"    kroků, které ho čtou v `run`: {[n for _, n in kroky_s_run]}")
        citlivy = [n for i, n in kroky_s_run if "Model" in n or "model" in n]
        if citlivy:
            print(f"    POZOR: čte ho modelový krok: {citlivy}")
        # Rozhodující: existuje cesta, jak se hodnota dostane až k běhu modelu?
        verdikt.setdefault(jmeno, {})[jn] = {
            "na_jobu": ma_na_jobu,
            "v_kroku": [n for _, n in kroky_s_env],
            "cte_v_run": [n for _, n in kroky_s_run],
        }

print("\n" + "=" * 78)
print("CO Z TOHO PLYNE PRO N3")
print("=" * 78)
sablona, hra = verdikt["šablona"], verdikt["hra"]
for jn in sorted(set(sablona) | set(hra)):
    s, h = sablona.get(jn), hra.get(jn)
    if not s or not h:
        continue
    if s == h:
        print(f"  job {jn!r}: OBĚ KOPIE SHODNÉ — {s}")
        continue
    print(f"  job {jn!r}: ROZDÍL")
    print(f"    šablona: na_jobu={s['na_jobu']} krok={s['v_kroku']} čte={s['cte_v_run']}")
    print(f"    hra:     na_jobu={h['na_jobu']} krok={h['v_kroku']} čte={h['cte_v_run']}")
    if s["na_jobu"] and h["na_jobu"]:
        print("    → ROZSAH JE SHODNÝ (env na úrovni jobu platí pro VŠECHNY kroky).")
        print("      Rozdíl je jen v tom, KTERÝ krok má hodnotu v `env:` navíc —")
        print("      a to je NÁLEZ O NÁSTROJI (sonda hledá krok podle jména),")
        print("      ne vada workflow. Sonda musí číst ROZSAH, ne jméno kroku.")
    else:
        print("    → POZOR: rozsah platnosti se LIŠÍ — tohle je skutečná vada.")

print("\nSouhrn pro rozhodnutí:")
for jmeno in ("šablona", "hra"):
    v = verdikt[jmeno]
    for jn, x in v.items():
        print(f"  {jmeno:8} job {jn!r}: env na jobu = {x['na_jobu']}, "
              f"kroky s hodnotou v env = {x['v_kroku']}")
