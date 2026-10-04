r"""Podpůrné měření k N3 a k rozhodnutí o nástrojích.

Dvě věci:
  1) Předává krok „Spusť agenta" v HERnÍM repu FORGE_ATTEMPT dál (přes
     `nacti_poskytovatele`/`spust_agenta`, `GITHUB_ENV`, …)? Když ne, je
     rotace modelů podle pokusu v herním repu MRTVÁ.
  2) Struktura `validate-all.mjs` (sekce) a přítomnost absolutní cesty
     v obou repech — podklad pro rozhodnutí, co tam patří.

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\n3-a-struktura-nastroju.py
"""
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")

print("=" * 78)
print("1) PŘEDÁVÁ KROK „Spusť agenta“ V HERNÍM REPU `FORGE_ATTEMPT` DÁL?")
print("=" * 78)

try:
    import yaml
except ImportError:
    print("chybí PyYAML")
    sys.exit(2)

for jmeno, cesta in [
    ("šablona", WS / "orchestra/repo/.github/workflows/agent.yml"),
    ("hra", WS / "games/uo-shadows/.github/workflows/agent.yml"),
]:
    d = yaml.safe_load(cesta.read_text(encoding="utf-8"))
    kroky = d["jobs"]["agent"]["steps"]
    krok = [s for s in kroky if s.get("name", "").startswith("Spusť agenta")]
    print(f"\n--- {jmeno}: kroků „Spusť agenta“ = {len(krok)}")
    if not krok:
        print("    CHYBA: krok nenalezen")
        continue
    run = str(krok[0].get("run", ""))
    env = krok[0].get("env") or {}
    print(f"    FORGE_ATTEMPT v env kroku: {'FORGE_ATTEMPT' in env}")
    # Cesty, kterymi by se hodnota mohla prenest i bez env:
    zpusoby = {
        "zápis do $GITHUB_ENV": "GITHUB_ENV" in run,
        "export FORGE_ATTEMPT": re.search(r"export\s+FORGE_ATTEMPT", run) is not None,
        "předání jako argument": "FORGE_ATTEMPT" in run,
    }
    for k, v in zpusoby.items():
        print(f"    {k}: {v}")
    if not ("FORGE_ATTEMPT" in env) and not any(zpusoby.values()):
        print("    → FORGE_ATTEMPT se do kroku NEDOSTANE: rotace podle pokusu je MRTVÁ")
    elif "FORGE_ATTEMPT" in env:
        print("    → hodnota je v env kroku: rotace funguje")

print("\n" + "=" * 78)
print("2) `validate-all.mjs` — STRUKTURA A VAZBA NA STANICI")
print("=" * 78)
va = WS / "orchestra/tools/validate-all.mjs"
text = va.read_text(encoding="utf-8")
sekce = re.findall(r"console\.log\('\\n?═+ ?([A-Z]\. [^═]+?) ?═+", text)
print(f"  soubor: {va.relative_to(WS)}  ({len(text.splitlines())} řádků)")
print(f"  sekce ({len(sekce)}): " + " · ".join(s.strip() for s in sekce))
print(f"  test() volání: {text.count('test(')}")
print(f"  spust() volání (podprocesy): {text.count('spust(')}")

print("\n  Absolutní cesty na této stanici uvnitř validate-all.mjs:")
for m in sorted(set(re.findall(r"C:/Users/[^'\"`\s]+", text))):
    print(f"    {m}")
print("  → nástroj je vázaný na stanici: v CI na GitHubu nemá PAT, .env ani klon hry")

print("\n" + "=" * 78)
print("3) OSMIČKA NOVÝCH NÁSTROJŮ — CO DĚLAJÍ SE SOUBORY")
print("=" * 78)
OSM = [
    "a1-a2-over.py", "a1-a2-mutace.py", "a3-over.py", "a3-mutace.py",
    "n8-zastarala-analyza.py", "n8-mutace.py", "b5-over-tvrzeni.py",
    "n1-over-inventar.py", "ag-over-cisla.py", "ag-mutace.py",
    "hl2-kostra-test.py", "hl2-kostra-kalibrace.py",
]
print(f"  {'nástroj':30} {'zapisuje?':10} {'podprocesy':11} absolutní cesty")
for nazev in OSM:
    p = WS / "_analyza" / nazev
    if not p.is_file():
        print(f"  {nazev:30} NEEXISTUJE")
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    # zapisuje: write_text / write_bytes / shutil.copy / writeFileSync
    zapis = bool(re.search(r"write_text|write_bytes|copyfile|copy2|writeFileSync", t))
    podprocesy = bool(re.search(r"subprocess\.|spawnSync|execFileSync", t))
    cesty = len(set(re.findall(r"[Cc]:[\\/]Users[\\/]", t)))
    print(f"  {nazev:30} {'ANO' if zapis else 'ne':10} {'ANO' if podprocesy else 'ne':11} {cesty}x")
