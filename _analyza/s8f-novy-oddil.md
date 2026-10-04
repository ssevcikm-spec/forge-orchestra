
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
---

### 8f. Omyly PLÁNOVACÍ (ověřovací) session 2. 10. 2026 (11:4x–12:4x UTC)

> **Šest ze sedmi** omylů vzniklo v **měřidle nebo ve mně** — a **čtyři z nich
> vypadaly jako nález o cizím kódu**. Dva mě málem přivedly k „opravě" správné
> věci (jednou k opravě `run_tests.gd`, jednou k opravě `combat.gd`).
> **Plný popis s příkazy je v §17**; tady je tabulka ve stejném tvaru jako 8b–8e.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **51** | **„Úkol B má v `combat.gd` pořád Godot 3 API"** — můj skript `h17-kontrola-klonu.py` hlásil `CHYBA: STARÉ Godot 3 API .has( v combat.gd` | **Nebyla to vada.** Vzor `.has(` chytil **`Dictionary.has()`** (řádky 80 a 113), což je **platné Godot 4 API**. Vada by byla jen `Object.has()` na **uzlu** | Hledal jsem **textový vzor bez kontextu** — přesně ta past, před kterou varuje `AGENTS.md`. Opraveno na kontextové vzory (`attacker.has(`, `"armor_rating" in defender`) |
| **52** | **„Oprava testu se do klonu nepropsala"** — běh 2 mých mutací dal `60 kontrol, 1 selhání` místo očekávaných `60/0` | **Bylo to jinak:** v čistém worktree je **původní `combat.gd`** (z `origin/main`), a ten při **prvním zásahu** spadne na `has()`. Test tedy **správně** hlásil vadu — jen to nebyla vada testu Úkolu A, ale **chybějící synchronizace `combat.gd`** | **Tatáž past jako omyl 46** u akční session („chybí `.godot/`") — **měřil jsem neúplný strom a číslo jsem připsal jiné příčině.** Po dosynchronizování `combat.gd` z klonu: `64/0` |
| **53** | **„Čísla 60/61/64 z §16.1 musím naměřit stejně"** | **Nemusím a nemohu:** akční session měřila nad **scratchem**, kde je z Úkolu B jen `combat.gd` a **ne** blok v testech. Já jsem měřil **celý soubor testů z klonu** — proto **64/65** místo 60/61. **Obě čísla jsou správná**, protože odpovídají na jinou otázku | Opsal jsem **očekávaná čísla z cizího zadání** místo abych si nejdřív **vysvětlil rozdíl**. Zachytil to až `assert` v mém vlastním runneru (9 rozchodů) |
| **54** | **„Řádek s `izo projekce` znamená, že se kontrola Úkolu A spustila"** | **Neznamená** — `izo projekce 2:1` je **jiná, legitimní kontrola** (`level.gd`). Detektor proto hlásil nález i tam, kde žádný není | Hledal jsem **krátký podřetězec**, který je i v jiné kontrole. Opraveno na přesnou větu `nebere izo projekci z úrovně` |
| **55** | **„Mutace M3 (vypuštění větve `hodnota()`) je jen práce navíc, kterou test nemusí krýt"** — málem jsem ji zapsal jako „zbytečná složitost v `combat.gd`" | **Je to NÁLEZ o bráně, ne o kódu:** M3 **není chycena** (0 selhání), ačkoli se větev **volá** (2×). Obě větve vracejí totéž číslo, takže test **nedokáže rozlišit pořadí** | Chtěl jsem odpovědět na otázku ze zadání („je dvojí tvar práce navíc?") **dojmem z kódu**. Odpověď dala až **sonda s čítači** (`h17-sonda-vetve.py`) — a je opačná |
| **56** | **„`zmena=false` v mém souhrnu běhů znamená, že agent nic nezměnil"** | U **pěti ze šesti** běhů to bylo **pravda i nepravda zároveň**: hledaný řetězec je i v `echo` kroku, který se do logu **vypisuje** → skript hlásil `true` i tam, kde se na ten krok vůbec nedošlo | Hledal jsem text, který se v logu vyskytuje **dvakrát z různých důvodů**. Opraveno na `##[error]` + hledaný text |
| **57** | **„Do souboru pro Node zapíšu český text přes `Set-Content`"** | **Brána diakritiky to ohlásila jako vadu** — z českého písmene se stal **náhradní znak** a soubor `h17-vsechny-behy.mjs` měl „rozbito: ANO" | Znal jsem pravidlo (`dsh-prostredi` §3d: „piš skript do souboru") a **přesto** jsem here-string poslal přes PowerShell. Odhalila to až brána — a to je zároveň **doklad, že ten soubor opravdu otevřela** |
| **58** | **„Oddíl §17.11 už mám zapsaný"** — soubor jsem pojmenoval `s17b-doplneni.md`, ale v `python -c` jsem ho hledal jako `s17b-doplněni.md` (s diakritikou) | `FileNotFoundError`. **Nic se nezapsalo** — a to je dobře: kdyby skript pokračoval dál, vložil by do `HANDOFF.md` **prázdný oddíl** | **Tatáž past jako omyl 57** (kódování a diakritika v příkazu) a **znovu v jednom kroku**: český text v `python -c`. Opraveno **skriptem v souboru** (`s17b-zapis-handoff.py`) — což je přesně ten postup, který jsem předtím **dvakrát** poradil a **jednou sám nedodržel** |
| **59** | **„Inventář jazyka je v pořádku, vždyť jsem ho nechal být"** — po editaci `kontrola-diakritiky.py` a `~\.dsh\skills\overovani\SKILL.md` jsem čekal `g3-brany.py` zelené | **Dvě brány spadly na `exit 2`** (`c2-mutace.py` → „ZDRAVÝ INVENTÁŘ … CHYBA: INVENTÁŘ JE ZASTARALÝ"; `n1-over-inventar.py`). **Bylo to SPRÁVNĚ** — oba soubory jsou vstupy skeneru | **Nebyl to omyl měření, ale omyl OČEKÁVÁNÍ:** zapomněl jsem, že **edituju i soubory, které skener čte**, ne jen ty, které „jsou kód“. Opraveno přegenerováním (`--json _analyza\_inventar.json` → 2 075 nálezů) a **zapsáno jako §17.11/1** — je to totiž **nejlepší argument pro pravidlo do `AGENTS.md`** (§17.9/5) |

**Vzor ze sedmi:** **šest** vzniklo v **měřidle** (vzor bez kontextu, neúplný
strom, opsaná očekávání, krátký podřetězec, text dvakrát, kódování)
a **čtyři vypadaly jako nález o cizím kódu** (51 „kód má Godot 3 API",
52 „oprava není v klonu", 54 „kontrola proběhla", 56 „agent nic nezměnil").
**Ani jeden z těch čtyř nebyl nález o cizím kódu.** Je to týž vzor jako 8b–8e,
jen o kolo dál — a potvrzuje, co predikuje `AGENTS.md`: *„počítej, že i tvoje
první číslo bude někde mimo."*

**Vzor z devíti (po doplnění 58 a 59):** **osm z devíti** vzniklo v **měřidle
nebo ve mně** a **čtyři vypadaly jako nález o cizím kódu**. Navíc **57 a 58
jsou TÁŽ past dvakrát za sebou v jednom kroku** (český text v příkazu místo
v souboru) — což je nejlepší doklad toho, že **znalost pasti nestačí**;
rozhoduje **postup**.

**A jeden nález, který se NEPOVEDLO uzavřít:** `HANDOFF.md` §16.11 a
`_analyza\g1-diakritika-novych.py` odkazovaly na `_analyza\c2-sonda-uvozovky.py`,
který **na disku nebyl** (nález **H1**, §17.8). Soubor jsem **obnovil**
a ověřil vlastním spuštěním — ale **nevím, jestli byl smazaný omylem, nebo
úmyslně**; kdyby úmyslně, je jeho obnova zásahem proti rozhodnutí, které
jsem nenašel. Zapsáno jako otevřený bod.

