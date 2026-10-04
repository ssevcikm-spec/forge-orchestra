"""Doplní skill `game-developer` o naměřené poučky a o pokyn k jeho revizi.

Skill leží MIMO workspace (`~\\.dsh\\skills\\`), takže zápis potřebuje oprávnění.
Zapisuje se bajty — soubor se jen rozšíří, kódování se nemění.
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CESTA = Path(r"C:\Users\Ssevc\.dsh\skills\game-developer\SKILL.md")
bajty = CESTA.read_bytes()
bom = bajty[:3] == b"\xef\xbb\xbf"
text = bajty.decode("utf-8-sig" if bom else "utf-8")
konce = "\r\n" if text.count("\r\n") > text.count("\n") - text.count("\r\n") else "\n"
print(f"BOM={bom}  konce řádků={'CRLF' if konce == chr(13) + chr(10) else 'LF'}  {len(bajty)} B")

N = lambda s: s.replace("\n", konce)

ODKAZ_U_SMLOUVY = N("""## 2. Smlouva první (contract-first)

> **⚠ DOPLNĚNO 2. 10. 2026 — k revizi tohohle skillu:** smlouva musí nést
> **TVAR DAT** a **přijímací kritérium**, ne jen jméno API. Naměřeno na
> `uo-shadows`: kontrakt „Hráč → `move()`, inventář, `die()`“ nedefinoval typy
> ani volajícího → granule dodala jen `project.godot` a byla zapsaná jako
> `done`; slovo `acceptance` se v designu hry nevyskytovalo **0×**. A co víc:
> **jiné komponenty to API už volaly** (`assist.gd` čte `hp/mana/target`,
> `economy.gd` volá `add_item/remove_item`) — smlouva byla jen v kódu jednoho
> agenta. Podrobně (a co v metodice ještě chybí):
> **`JAK-PSAT-DESIGN-A-PLANOVAT-VYVOJ.md`** v session workspace, oddíly 2 a 3.
""")

NOVY_ODDIL = N("""

---

## Příprava na revizi tohoto skillu (založeno 2. 10. 2026)

**Tenhle oddíl je zadání pro budoucí sessiony, ne hotová metodika.** Vznikl
z konkrétního měření: tři PR prošla zeleným CI a **nemohla fungovat**, protože
granule dostaly jméno API bez tvaru dat a brány měřily přítomnost metod.

### Co je naměřeno (2. 10. 2026, `uo-shadows`, Godot 4.7.2)

| Co se stalo | Čím to bylo |
|---|---|
| `hud.gd` se v `_ready()` rozbil (`margin_left` — Godot 3 API) a **label se nikdy nepřidal** | test se ptal jen `has_method("update")` |
| `save.gd` uložil **35 B** (jen pozici hráče) a **vrátil `true`** | služby hledal ve skupinách, které nikdo nezakládá; test se ptal jen `has_method("save")` |
| `mining.gd` spadl na `node.has()` (Godot 3 API) a na `/root/Skills` | totéž + chybějící autoload |
| `world.map` a `entity.player` byly `done`, ale jejich práce v repu nebyla | `world.gd` přesunut do `_retired/` (druhé číslo mřížky) a `entity.player` dodal jen `project.godot` |

### Co z toho plyne pro metodiku (kandidáti na přepis skillu)

1. **Hotovo = soubor je v `main` A brána jeho funkci ZAVOLALA.** „PR sloučeno“
   ani `done` v roadmapě není důkaz (D1 i soubor můžou tvrdit hotovo a práce
   nikde není). Do DAG se staví jen na granuli, jejíž soubor **v `main` je**
   a jejíž API **jde zavolat**.
2. **Design dokument musí u každé smlouvy nést tvar dat a přijímací kritérium** —
   jinak si agent vymyslí rozhraní (a vymyslí ho jinak než sousední granule).
3. **Zadání granule je taky dokument** a musí se udržovat: naměřeno, že zadání
   `engine.shell` odkazovalo na `world.iso_position`, tedy na API, které bylo
   přesunuté do `_retired/` (izometrie je dnes v `level.gd`).
4. **Podmíněný test je tiše zelený** — `if load(...) != null:` přeskočí soubor,
   který se vůbec nenačetl. Soubor, který součástí hry být MÁ, musí **selhat**.
5. **Než sloučíš PR od agenta, spusť to** (Godot `--headless --script` se
   zkušební kostrou komponent) a **vrať vadu do kódu** — když test nespadne,
   netestuje.
6. **Uzly a entity mají mít smlouvu na jednom místě.** Když si ji jeden agent
   vymyslí v kódu (`resource_id`/`difficulty`/`cell` u uzlu suroviny), ostatní
   granule na tom začnou stavět, aniž by to bylo kdekoliv deklarované.

### Pokyn pro další sessiony (co má vzniknout)

- **Rostoucí podklad:** `JAK-PSAT-DESIGN-A-PLANOVAT-VYVOJ.md` v session
  workspace. **Každá session, která najde naměřenou vadu designu nebo
  plánování, do něj přidá případ** (oddíl 4) a podle potřeby upraví oddíly 2–3.
  Bez měření (soubor + číslo + datum) tam nic nepatří.
- **Druhá práce:** přepsat design `uo-shadows` podle oddílu 5.1 dokumentu
  (smlouvy s tvarem dat, datové formáty, přijímací kritéria, definice hotovo) —
  **v session, která zároveň neopravuje kód**.
- **Až se oddíly 2–3 dokumentu ustálí** (tj. nezmění se při dalších dvou
  případech), přepiš tenhle skill tak, aby **odkazoval do dokumentu**, a sem
  nechal jen stabilní postup. Konkrétní příklady přitom patří do **oddělené**
  sekce (vzor: skill `hlouchkova-analyza`), aby se metodika nepletla s historií
  jednoho projektu.
- **Testovací otázka na každou větu v tomhle skillu:** *„Platí to i pro projekt,
  který ještě neexistuje?“* Když ne, patří to do projektu, ne do skillu.
""")

chyby = 0
if text.count("## 2. Smlouva první (contract-first)") != 1:
    print("CHYBA: nadpis '## 2. Smlouva první (contract-first)' nenalezen 1×")
    chyby += 1
else:
    text = text.replace("## 2. Smlouva první (contract-first)", ODKAZ_U_SMLOUVY.rstrip("\r\n"))
    print("OK    odkaz u §2 Smlouva první")

if "Příprava na revizi tohoto skillu" in text:
    print("POZOR: oddíl už v skillu je, nepřidávám znovu")
else:
    text = text.rstrip("\r\n") + NOVY_ODDIL
    print("OK    nový oddíl 'Příprava na revizi tohoto skillu' na konec")

if chyby:
    print("NIC SE NEZAPSALO")
    sys.exit(1)

vysledek = text.encode("utf-8")
if bom:
    vysledek = b"\xef\xbb\xbf" + vysledek
CESTA.write_bytes(vysledek)
print(f"\nZapsáno: {CESTA} ({len(vysledek)} B, bylo {len(bajty)} B)")
