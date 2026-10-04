#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Doplní do skillů pasti naměřené 2. 10. 2026 (akční session, Úkoly A–D a B1).

`AGENTS.md`: „Když narazíš na past, která v žádném skillu není, doplň ji tam
i s příkladem." Doplňuje se proto:

* `dsh-prostredi` — (a) `.godot/` v git worktree, (b) česká uvozovka v patcheru
* `overovani`     — (a) brána, která neproběhla, (b) mutace, která nedosáhne
                       toho, aby měřená PODMÍNKA přestala platit

Skilly leží mimo workspace (`~\.dsh\skills\`), takže zápis potřebuje oprávnění.

Použití:
    python _analyza/g2-dopln-skilly.py
    python _analyza/g2-dopln-skilly.py --zpet
"""

import hashlib
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKILLS = pathlib.Path.home() / ".dsh" / "skills"
DSH = SKILLS / "dsh-prostredi" / "SKILL.md"
OVR = SKILLS / "overovani" / "SKILL.md"
ZALOHA = pathlib.Path(__file__).resolve().parent / "g2-skilly-zaloha"

# ────────────────────────────────────────────── dsh-prostredi: .godot ────────
DSH_KOTVA = "## 5. Síť a GitHub"
DSH_NOVY = '''### 4c. `.godot/` NENÍ v gitu — v `git worktree` proto testy „regresují"

**Naměřeno 2. 10. 2026.** Testy hry v **čerstvém** pracovním stromu:

```
$ python _analyza\\a-mutace-run.py zaklad        # nad git worktree
[test] FAIL všechny assety jdou načíst (3 OK, 16 chybí)
[test] FAIL mapa má dlaždici pro každé políčko (0)
[test] FAIL dlaždicové pozadí je ve scéně
[test] 57 kontrol, 3 selhání
```

Vypadá to jako **regrese kódu** — a není. `.godot/` je v `.gitignore`, takže
se do worktree **nezkopíruje import cache** a Godot v režimu `--script` assety
**neimportuje**. V hlavním klonu je proto **59 kontrol, 0 selhání**.

**Řešení (ověřeno):**

```powershell
Copy-Item <hlavni-klon>\\.godot <worktree>\\.godot -Recurse -Force   # 574 souborů
```

**Pravidlo:** než označíš výsledek testů v worktree za regresi, **zeptej se,
které soubory v tom stromu vůbec jsou** — a porovnej s hlavním klonem.
Stejná třída jako „měřím nezměřený strom" (skill `overovani` §7.13).

### 4d. Česká uvozovka v patcheru vypadá jako syntaktická chyba Pythonu

**Naměřeno 2. 10. 2026.** Patcher zapisoval do `hl-rizika-jazyka.py` text
s **otevírací** českou uvozovkou a **zavírací obyčejnou** (ta se při autorství
nahradila). Uvnitř f-stringu to řetězec ukončí, závorka zůstane otevřená a
Python ohlásí:

```
SyntaxError: '(' was never closed        (na řádku, který vypadá správně)
```

**Není to vada Pythonu** — ověřeno sondou: české uvozovky uvnitř f-stringu
fungují (Python 3.12). Vada je **v zápisu znaku**.

**Pravidlo:** po každém zápisu, který vkládá český text do kódu, spusť
`ast.parse` (Python) / parser (`.gd`, `.ps1`). **Textová kontrola to minula** —
odhalil to až parser. A když hledáš, kde je v souboru rozbitá uvozovka, hledej
**nevyvážené** řádky (`počet otevíracích > počet zavíracích`), ne „první výskyt".

'''

# ────────────────────────────────────── overovani: neproběhlo + mutace ───────
OVR_KOTVA = "### 7.9 MUTACE, KTERÁ SE TICHE NEPROVEDE, VYPADÁ JAKO ÚSPĚCH"
OVR_NOVY = '''### 7.13 BRÁNA, KTERÁ NEPROBĚHLA, NENÍ ČERVENÁ — JE NEZMĚŘENÁ

**Naměřeno 2. 10. 2026.** Dvě brány projektu hlásily „červená" (byly vedené
v seznamu známých vad) — a **neproběhla v nich ani jedna kontrola**:

| Brána | V sandboxu | Mimo sandbox |
|---|---|---|
| `orchestra\\tools\\test-check-schema.py` | `PermissionError WinError 5` **před první kontrolou** | **17 kontrol, `exit 0`** |
| `orchestra\\repo\\.forge\\node\\vision.test.mjs` | `Error: spawn EPERM` (`execFile`) → **0 kontrol** | **36 kontrol, `exit 0`** |

**Důsledek pro rozhodování:** kdyby se podle těch „červených" opravoval kód,
opravovalo by se **něco, co nikdo neměřil** — a to je horší než nezměřená
zelená, protože to vypadá jako znalost.

**Jak to poznat (tři otázky, v tomhle pořadí):**

1. **Proběhla vůbec?** Hledej ve výstupu počet kontrol / testů. Když tam žádný
   není, brána se nespustila — `exit 1` pak neznamená „našla vadu".
2. **Není to prostředí?** Spusť **totéž** s širším oprávněním (nebo v čistém
   stromu). Když projde, byl to sandbox, ne kód.
3. **Nezapisuj to jako vadu.** „Neproběhlo (prostředí)" je **třetí stav** vedle
   zelené a červené — a patří do zápisu i do seznamu bran.

**A v seznamu známých červených se to musí přejmenovat**, ne nechat. Brána
v tom seznamu tvrdí něco, co se nikdy neměřilo.

### 7.14 MUTACE, KTERÁ ZMĚNÍ SOUBOR, ALE NE PODMÍNKU

**Naměřeno 2. 10. 2026** (sebekontrola brány diakritiky). Rozbil jsem v souboru
české slovo, které brána hledá — a **brána prošla**. Vypadalo to jako slepá
brána. Nebyla. Byly to **tři různé vady mé mutace**, každá o vrstvu výš:

| # | Co jsem udělal | Proč to nic nezměnilo |
|---|---|---|
| 1 | rozbil jsem slovo **v seznamu**, který se hledá | seznam tím přišel o položku — měřil jsem něco jiného |
| 2 | rozbil jsem **jeden** výskyt ze **sedmi** | podmínka `slovo in text` platila dál |
| 3 | rozbil jsem **všech sedm** výskytů | seznam hledaných slov je **v tomtéž souboru** — našel si své |

**Pravidlo (zobecnění §7.9):** mutace musí dosáhnout toho, aby **měřená
PODMÍNKA přestala platit** — ne jen aby se soubor změnil. Před spuštěním si
napiš, **která podmínka** se má obrátit, a ověř ji **zvlášť**:

```python
assert zmut != orig                 # soubor se změnil
assert "<měřená podmínka>" not in zmut   # A PODMÍNKA UŽ NEPLATÍ  ← tohle chybělo
```

**A ještě jeden následek, který stojí za zapamatování:** když brána kontroluje
soubor, **ve kterém je její vlastní kontrolní seznam**, nemůže se kontrolovat
stejně jako ostatní (našla by v sobě vzorek). Musí mít **vlastní, jiný důkaz** —
a ten se taky musí mutačně ověřit.

'''

CIL_S = [(DSH, DSH_KOTVA, DSH_NOVY, "dsh-prostredi"),
         (OVR, OVR_KOTVA, OVR_NOVY, "overovani")]


def main() -> int:
    zpet = "--zpet" in sys.argv
    ZALOHA.mkdir(exist_ok=True)

    if zpet:
        for cesta, _, _, jmeno in CIL_S:
            z = ZALOHA / (jmeno + ".md")
            if not z.is_file():
                print("CHYBA: záloha %s není" % z)
                return 2
            cesta.write_bytes(z.read_bytes())
            print("vráceno: %s" % cesta)
        return 0

    for cesta, kotva, novy, jmeno in CIL_S:
        if not cesta.is_file():
            print("CHYBA: %s neexistuje" % cesta)
            return 2
        t = cesta.read_text(encoding="utf-8")
        if novy.strip()[:80] in t:
            print("OK: %s už doplněk má" % jmeno)
            continue
        if t.count(kotva) != 1:
            print("CHYBA: kotva %r v %s nalezena %d×" % (kotva, jmeno, t.count(kotva)))
            return 2
        z = ZALOHA / (jmeno + ".md")
        if not z.is_file():
            z.write_bytes(t.encode("utf-8"))
        novy_text = t.replace(kotva, novy + kotva, 1)
        assert novy_text != t, "MUTACE NEPROBĚHLA u %s" % jmeno
        cesta.write_bytes(novy_text.encode("utf-8"))
        z5 = cesta.read_text(encoding="utf-8")
        assert z5 == novy_text, "zápis nesedí u %s" % jmeno
        assert kotva in z5, "kotva po zápisu zmizela u %s" % jmeno
        print("OK: %-14s %d → %d znaků  (sha %s)"
              % (jmeno, len(t), len(z5),
                 hashlib.sha256(z5.encode("utf-8")).hexdigest()[:12]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
