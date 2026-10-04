"""Doplní do skillu `dsh-prostredi` pasti naměřené 2. 10. 2026.

Skill leží MIMO workspace (`~\.dsh\skills\`), takže zápis potřebuje oprávnění.
Každý vzor musí sednout PRÁVĚ JEDNOU, jinak skript nic nezapíše.
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CESTA = Path(r"C:\Users\Ssevc\.dsh\skills\dsh-prostredi\SKILL.md")

STAREJ_6 = """Godot **není v PATH** a bez `--user-data-dir` padá na `Could not open 'user://'`.

```powershell
$godot = 'orchestra\\tools\\godot\\Godot_v4.7.2-stable_win64_console.exe'

# testy
& $godot --headless --path games\\uo-shadows --script res://tests/run_tests.gd

# snímek hry (pak se na něj PODÍVEJ přes read_image)
& $godot --path games\\uo-shadows --user-data-dir "$env:TEMP\\uo-shadows-hrani" `
         --rendering-driver opengl3 --resolution 960x540 `
         --write-movie <out>\\frame.png --quit-after 5
```

Ve složce hry je launcher `hra.cmd`, který to má vyřešené."""

NOVY_6 = """Godot **není v PATH**.

> ⚠ **`--user-data-dir` tenhle build IGNORUJE** — naměřeno 2. 10. 2026 na
> `Godot_v4.7.2-stable_win64_console.exe`: v `--help` vůbec není a **tři různé
> způsoby volání** (s `--path` před i za, i s `=`) skončily pořád na
> `C:/Users/<uzivatel>/AppData/Roaming/Godot/app_userdata/<projekt>/`.
> **Důsledek v sandboxu:** `user://` míří **mimo workspace** → zápis je
> zablokovaný, ale **nástroj nespadne**:
> `ERROR: Could not create directory: 'user://logs'` a `ConfigFile.save()`
> vrátí chybu 7 (`File not found`). Vypadá to jako vada kódu, který ukládá —
> a je to prostředí. **Řešení: přepiš `APPDATA` do workspace** (ověřeno, že to
> `user://` přesune):

```powershell
$godot = 'orchestra\\tools\\godot\\Godot_v4.7.2-stable_win64_console.exe'
$env:APPDATA = "$PWD\\_analyza\\godot-appdata"   # user:// zůstane ve workspace

# testy
& $godot --headless --path games\\uo-shadows --script res://tests/run_tests.gd

# snímek hry (pak se na něj PODÍVEJ přes read_image)
& $godot --path games\\uo-shadows `
         --rendering-driver opengl3 --resolution 960x540 `
         --write-movie <out>\\frame.png --quit-after 5
```

**Cestu k `user://` si ověř, ne předpokládej:**
`print(ProjectSettings.globalize_path("user://"))`. Když to vypadá, že „se nic
neuložilo", první otázka je **kam** se to mělo uložit.

**A pozor na `hra.cmd`:** posílá `--user-data-dir`, ale ten se ignoruje, takže
hra píše do `%APPDATA%`. Mimo sandbox to vyjde (Roaming je zapisovatelný),
**uvnitř sandboxu ne.**

**Když Godot spouštíš přes `--script`:** skript, který `extends SceneTree`,
musí pracovat v `_process()`, **ne v `_initialize()`** — v `_initialize()` ještě
není strom, takže `get_tree()` vrací `null` a měříš něco jiného, než co se děje
ve hře (naměřeno 2. 10. 2026: `save()` vracelo `false`, protože `get_tree()`
bylo null — a vypadalo to jako vada ukládání)."""

STAREJ_4 = """3. **Nezapisuj „testy projdou" do dokumentace, dokud víš, že projdou jen
   s rozšířeným oprávněním** — jinak příští běh vypadá jako regrese."""

NOVY_4 = STAREJ_4 + """

### 4b. `git clone` v sandboxu nejde — použij `git worktree`

**Naměřeno 2. 10. 2026:** `git clone --shared <klon> <cíl>` spadl na

```
sh.exe: *** fatal error - couldn't create signal pipe, Win32 error 5
fatal: Could not read from remote repository.
```

Je to **tatáž hranice jako EPERM výš** (programy nesmí otevírat pojmenované
roury), ale vypadá to jako „rozbitý git" nebo „nečitelný repozitář" — `git clone`
pouští `sh` a ten rouru potřebuje. **Řešení: `git worktree`** (žádný transport,
jen metadata v `.git/worktrees/`):

```powershell
& orchestra\\tools\\git.cmd -C games\\uo-shadows worktree add --detach "$PWD\\_analyza\\scratch" origin/main
# … práce v odděleném stromu, hlavní klon se nemění …
& orchestra\\tools\\git.cmd -C games\\uo-shadows worktree remove --force "$PWD\\_analyza\\scratch"
```

**Dvě výhody, které to má navíc:**
- Do klonu uživatele se **nesahá** — jeho necommitnuté změny zůstanou být
  (měřeno: `git status` po celou dobu práce stejný).
- Větev vytvořená uprostřed (`git branch -f <jmeno> HEAD`) **v klonu zůstane**,
  i když worktree zrušíš — to je čistý způsob, jak něco „připravit k review"
  bez pushnutí."""

text = CESTA.read_text(encoding="utf-8")
chyby = 0
for stary, novy, popis in [
    (STAREJ_6, NOVY_6, "§6: --user-data-dir se ignoruje + APPDATA + SceneTree/_process"),
    (STAREJ_4, NOVY_4, "§4b: git clone v sandboxu nejde → worktree"),
]:
    pocet = text.count(stary)
    if pocet != 1:
        print(f"CHYBA: {popis} — vzor nalezen {pocet}× (musí být 1×), NIC SE NEMĚNÍ")
        chyby += 1
        continue
    text = text.replace(stary, novy)
    print(f"OK    {popis}")

if chyby:
    sys.exit(1)

CESTA.write_bytes(text.encode("utf-8"))
print(f"\nZapsáno: {CESTA} ({len(text.encode('utf-8'))} B)")
