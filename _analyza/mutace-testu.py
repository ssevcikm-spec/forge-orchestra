"""⚠ TENTO TEST DNES NEPROBĚHNE — `exit 1` ODSUD NENÍ NÁLEZ O KÓDU.

Zařazeno 2. 10. 2026 (Úkol 3 zadání `ZADANI-DOKONCENI-AUDITU.md`, nález **R6**).
Je to **třetí stav** podle skillu `overovani` §7.13: není zelená a **není ani
červená** — je to **NEPROBĚHLO**. Kdo ho povede v seznamu jako „červený",
tvrdí o něm něco, co se nikdy neměřilo.

CO JE TO ZA TEST
  Vrací do kódu **VADNÉ verze** tří souborů (`save.gd`, `hud.gd`, `mining.gd`)
  z přesně určených commitů a ověřuje, že se tím soubor opravdu změnil
  (hash PŘED a PO). Je to **příprava** pro druhou polovinu — teprve po něm
  musí testy hry spadnout. Sám o sobě **nic neměří**; měří se výsledkem testů.

PROČ DNES NEPROBĚHNE (naměřeno 2. 10. 2026, 18:2x)
  ```
  $ python _analyza\\mutace-testu.py       → exit 1
  CHYBA: 9efbb0763fa7c2f3cf0c98de08029e20ae8c3018:scripts/save.gd
         nejde přečíst (rc=128) — MUTACE NEPROBĚHLA
  ```
  **PŘÍČINA JE JINDE, NE V TECH COMMITECH** — a to je důležité, protože `rc=128`
  vypadá jako „ten commit v repu není". **Je tam.** Naměřeno zvlášť:
  ```
  git -C games\\uo-shadows cat-file -t 9efbb076…   → commit   (všechny 3 SHA existují)
  git -C games\\uo-shadows show 9efbb076…:scripts/save.gd   → VYPÍŠE OBSAH, rc=0
  ```
  Skript ale pouští git nad **`_analyza\\merge-scratch`** (řádek 17 a 29:
  `GIT, "-C", str(SCRATCH)`), a ta složka **neexistuje** (`Test-Path` → `False`).
  Proto:
  ```
  git -C _analyza\\merge-scratch show …   → rc=128
  fatal: cannot change to '_analyza\\merge-scratch': No such file or directory
  ```
  Test tedy spadne na **prvním souboru**, dřív než nasadí jedinou vadu.
  **Nula provedených mutací.** (A je to táž past jako u `h17-mutace-a.py`:
  `exit 1`, který nikdo nečte, protože skript není v `BRANY` v `g3-brany.py`.)

CO BY HO ZPROVOZNILO (návrh — `NEOVĚŘENO`, sám jsem to nespouštěl)
  Založit ten pracovní strom **z `origin/main`** v herním klonu:
  ```powershell
  & orchestra\\tools\\git.cmd -C games\\uo-shadows worktree add --detach `
      "$PWD\\_analyza\\merge-scratch" origin/main
  ```
  Tím se `git -C _analyza\\merge-scratch` stane platným voláním. **Ověřeno
  předem:** všechny tři commity s vadnými verzemi v klonu **jsou**
  (`9efbb076…`, `7c45e2d…`, `d72bf4d…`) a `git show` z klonu je přečte ✓.
  **Neověřeno:** jestli po nasazení vad testy hry skutečně spadnou — to je až
  druhý krok a ten jsem nespouštěl.

⚠ PROČ SE TO NEMÁ SMAZAT (A1, A7): skript je **hotový nástroj** a zná **přesná
SHA** vadných verzí — to je znalost, kterou by nikdo znovu nedohledával.

---

Mutační test nových kontrol: vrátí do kódu VADNÉ verze souborů.

Bez tohohle by „59 kontrol, 0 selhání" nebyl důkaz, že kontroly měří —
jen že něco proběhlo (past z `overovani` §7.9: mutace, která se tiše neprovede,
tvrdí totéž co úspěšná). Proto se u každého souboru vypíše hash PŘED a PO
a ověří se, že se liší.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(r"C:\Users\Ssevc\Local-Deepseek")
GIT = str(WS / "orchestra" / "tools" / "git.cmd")
SCRATCH = WS / "_analyza" / "merge-scratch"

# soubor → (commit s VADNOU verzí, cesta v repu)
# POZOR: větve `forge/task-139` a `-140` už obsahují OPRAVU (pushnul jsem ji
# tam před sloučením) — vadná verze je o commit níž, proto se bere přesné SHA.
MUTACE = {
    "scripts/save.gd": ("9efbb0763fa7c2f3cf0c98de08029e20ae8c3018", "scripts/save.gd"),
    "scripts/hud.gd": ("7c45e2d3dde1c03ffc6ce60fe18636d0d60b2b61", "scripts/hud.gd"),
    "scripts/mining.gd": ("d72bf4df2f06923264990394822bdab8c3480f4d", "scripts/mining.gd"),
}

for cil, (ref, cesta) in MUTACE.items():
    p = subprocess.run([GIT, "-C", str(SCRATCH), "show", f"{ref}:{cesta}"], capture_output=True, shell=True)
    if p.returncode != 0 or not p.stdout:
        print(f"CHYBA: {ref}:{cesta} nejde přečíst (rc={p.returncode}) — MUTACE NEPROBĚHLA")
        sys.exit(1)
    soubor = SCRATCH / cil
    pred = soubor.read_bytes()
    soubor.write_bytes(p.stdout)
    po = soubor.read_bytes()
    h = lambda b: hashlib.sha256(b).hexdigest()[:12]
    stav = "ZMĚNĚNO" if pred != po else "NEZMĚNĚNO (mutace se neprovedla!)"
    print(f"{cil:22} {h(pred)} → {h(po)}  {stav}")
    if pred == po:
        sys.exit(1)
print("\nVadné verze nasazeny — teď musí testy SPADNOUT.")
