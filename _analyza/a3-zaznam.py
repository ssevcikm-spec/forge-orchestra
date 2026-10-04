r"""Zapíše surový záznam A3 — co brány udělají s novými granulemi.

Dělá DVĚ měření na kopii hry (klon uživatele se nemění):
  1) testy na `main` tak, jak jsou,
  2) testy po vložení třířádkového `move()` (mutation) — tím se zapne
     podmíněný blok kontrol v `tests/run_tests.gd`.

Výsledek jde do `_analyza\a3-brany-novych-granuli.md`.

PROČ PYTHONEM A NE V POWERSHELLU: PowerShell v tomhle volání rozbil
diakritiku („vubec nem?" místo „vůbec nemá") a here-string s `$()` navíc
rozbíjí parser. Je to past z `dsh-prostredi` §2/§3c.

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\a3-zaznam.py
"""
import os
import pathlib
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
GODOT = WS / "orchestra/tools/godot/Godot_v4.7.2-stable_win64_console.exe"
KOPIE = WS / "_analyza/scratch-a3z"
VYSTUP = WS / "_analyza/a3-brany-novych-granuli.md"

SENTINEL = (
    "\n\nfunc move(dir: Vector2) -> void:"
    "\n\t# SENTINEL pro A3 — NENÍ to implementace smlouvy (žádné hp, inventory,"
    "\n\t# die()). Jen nejmenší možná metoda se správným jménem, aby se blok"
    "\n\t# kontrol v tests/run_tests.gd vůbec ZAPNUL."
    "\n\tposition = _step(position + dir)\n"
)


def spust_testy(projekt: pathlib.Path) -> tuple:
    env = dict(os.environ)
    env["APPDATA"] = str(WS / "_analyza/godot-appdata")
    (WS / "_analyza/godot-appdata").mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [str(GODOT), "--headless", "--path", str(projekt),
         "--script", "res://tests/run_tests.gd"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
    )
    vystup = (r.stdout or "") + (r.stderr or "")
    radky = [l.strip() for l in vystup.splitlines()
             if "kontrol," in l or "[test] FAIL" in l]
    return r.returncode, radky


print("=== 1) testy na main (bez nových granul) ===")
kod1, radky1 = spust_testy(WS / "games/uo-shadows")
for l in radky1:
    print("   ", l)
print(f"    exit={kod1}")

print("\n=== 2) příprava kopie + vložení sentinelu `move()` ===")
if KOPIE.exists():
    shutil.rmtree(KOPIE)
subprocess.run(["robocopy", str(WS / "games/uo-shadows"), str(KOPIE),
                "/E", "/XD", ".git", "/NFL", "/NDL", "/NJH", "/NJS", "/NP"],
               capture_output=True, shell=True)
p = KOPIE / "scripts/player.gd"
t = p.read_text(encoding="utf-8")
if "func move(" in t:
    print("CHYBA: v kopii už `move()` je — klon se mezitím změnil")
    sys.exit(2)
t2 = t.replace("\nfunc flash() -> void:", SENTINEL + "\nfunc flash() -> void:", 1)
if t2 == t:
    print("CHYBA: vložení sentinelu neproběhlo (kotva 'func flash()' nenalezena)")
    sys.exit(2)
p.write_text(t2, encoding="utf-8", newline="")
print(f"    vloženo; {p.name}: {len(t.splitlines())} → {len(t2.splitlines())} řádků")

print("\n=== 3) testy na kopii SE sentinelem ===")
kod2, radky2 = spust_testy(KOPIE)
for l in radky2:
    print("   ", l)
print(f"    exit={kod2}")

# ── ZÁZNAM ──────────────────────────────────────────────────────────────────
z = []
z.append("# A3 — CO BRÁNY UDĚLAJÍ S NOVÝMI GRANULEMI (surový záznam z měření)\n")
z.append("**Co tenhle dokument JE:** surový záznam měření k Úkolu A3 ze")
z.append("`NEXT-SESSION-INSTRUKCE.md`. **Co NENÍ:** analýza ani návrh.\n")
z.append("**Datum měření:** 2. 10. 2026 · **kód hry:** `main` = `194735d`\n")
z.append("Reprodukce (měřeno na kopii, klon uživatele se nemění):\n")
z.append("```powershell")
z.append('$env:APPDATA = "$PWD\\_analyza\\godot-appdata"')
z.append("& orchestra\\tools\\godot\\Godot_v4.7.2-stable_win64_console.exe "
         "--headless --path <projekt> --script res://tests/run_tests.gd")
z.append("```\n")
z.append("## 1) `main` tak, jak je\n")
z.append("```")
for l in radky1:
    z.append(l)
z.append(f"(exit={kod1})")
z.append("```\n")
z.append("## 2) `main` + třířádkový `move()` (nic jiného se nezměnilo)\n")
z.append("Vložený kód **není** implementace smlouvy — nemá `hp`, `inventory` ani")
z.append("`die()`. Je to nejmenší metoda se správným jménem, která zapne")
z.append("podmíněný blok v `tests/run_tests.gd` (`if player.has_method(\"move\")`).\n")
z.append("```")
for l in radky2:
    z.append(l)
z.append(f"(exit={kod2})")
z.append("```\n")
z.append("## Co z toho plyne\n")
z.append("- Rozdíl **59/0 → 60/1** je jediná kontrola, která se dřív vůbec")
z.append("  nespustila. Blok se **tiše přeskakoval** — a `59 kontrol, 0 selhání`")
z.append("  vypadá stejně jako naměřená nula.")
z.append("- Ta kontrola je **falešný poplach na legitimním kódu**: zakazuje")
z.append("  řetězec `level.iso_position`, který `scripts/player.gd:40` obsahuje")
z.append("  odjakživa — a `level.gd` `iso_position` vůbec nemá, takže větev je")
z.append("  mrtvá. Test tedy netvrdí nic o izometrii; měří přítomnost řetězce.")
z.append("- **Žádná** kontrola nevolá `hp`, `inventory`, `die()`, `snapshot()` ani")
z.append("  `restore()` — brána tyhle smlouvy vůbec neotevře.")
z.append("- `world.gd` v `main` **není** (přesunut do `_retired/`); `TestsSvet`")
z.append("  v testech je **atrapa**, která `gather()` jen počítá. Reálný")
z.append("  `world.gd` tedy nezavolá nic.")

VYSTUP.write_text("\n".join(z) + "\n", encoding="utf-8")
print(f"\nzapsáno: {VYSTUP.relative_to(WS)}  ({VYSTUP.stat().st_size} B)")

if KOPIE.exists():
    shutil.rmtree(KOPIE)
    print("kopie uklizena")
