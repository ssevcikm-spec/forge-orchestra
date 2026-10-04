# ZADÁNÍ PRO AKČNÍ SESSION — opravit, co ověření přesunu našlo

**Zkontrolováno při:** `dea6f5c` („P8b: jednorázová sonda p8-sonda-vzor.py do _archiv")
**Zapsáno:** 4. 10. 2026, plánovací (ověřovací) session
**Stav obou repů při psaní:** `forge-orchestra` = `dea6f5c` (strom čistý) · `uo-shadows` = `869dce8` (strom čistý)
**Pushnuto:** **NE** — `origin/main..HEAD = 6` (orchestra) a **1** (hra). Push **jen na vyžádání**.
**Co je v `HANDOFF.md`:** **§30 = OVĚŘENÍ PŘESUNU** (výsledky, nálezy H48–H56, omyly **138–142**) · §29 = záznam akční session · §2 = co je otevřené
**Co je v `KRONIKA-PROJEKTU.md`:** řádek **26** (ověření) · nálezy **H48–H56** v §2 · rozhodnuté návrhy **NA24–NA26** v §6
**Co tenhle dokument JE:** **zadání pro AKČNÍ session**, které má **opravit vady nalezené ověřením** přesunu na `E:`.

> **⚠ Hlavička zadání je ZÁMĚRNĚ přepsaná celá.** Předchozí verze tvrdila `c3ee946`
> a byla **zastaralá** (HEAD se mezitím posunul o 2 commity) — a nástroj
> `_analyza/zadani-kontrola.py`, který to má hlídat, je **slepý na orchestra**
> (nález **H53**). Proto se hlavička odteď měří, ne odhaduje.

---

## 0. Co je hotové a co NE (stav po ověření)

Ověření **potvrdilo jádro přesunu**: data jsou na místě, historie nedotčená,
žádná junctiona, archiv gitignorovaný, `.secrets` v gitu není, `hra.cmd`
funguje bez `FORGE_GODOT` (spuštěno, Godot naběhl).

**Ale našlo čtyři vady, které přesun zanechal — a všechny jsou v MĚŘIDLE, ne v datech.**
To je konzistentní se vzorem projektu (76 % omylů vzniká v měřidle):

| # | Vada | Nález |
|---|---|---|
| 1 | **`_analyza/g3-brany.py` spouští 15 z 29 bran po STARÝCH cestách** → ty brány **vůbec neběží** a `exit=2` se čte jako „červená" | **H48** |
| 2 | **`tools/test-gitignore-tajemstvi.py` je po přesunu ROZBITÝ** (`STANICE` nedefinovaná → `NameError`) a **žádná brána ho nespouští** | **H49** |
| 3 | **`tools/verify-setup.py` má pevnou cestu na starý kořen** → hlásí 6× CHYBI; **také ho nic nespouští** | **H50** |
| 4 | **`_analyza/zadani-kontrola.py` je SLEPÝ na orchestra** (hledá klíč `orchestra`, repo se jmenuje `forge-orchestra`) | **H53** |

**A jeden nález o pokrytí, který je důležitější než všechny čtyři:**

| # | Vada | Nález |
|---|---|---|
| 5 | **Skener `hl-neanglicky-v-kodu.py` čte JEN soubory z gitu** (`git ls-files`) → **necommitnutý nový kód je pro jazykovou bránu neviditelný** | **H52** |

---

## 1. Cíl (jedna věta)

**Opravit pět měřidel rozbitých přesunem — a každou opravu doložit mutačním
testem, protože u čtyř z pěti jde právě o to, že brána tiše neměří.**

---

## 2. Úkoly (v tomto pořadí — první je nejdůležitější)

### 2.1 Úkol A — `g3-brany.py`: 15 bran neběží (nález H48)

**Naměřeno:** `WS = pathlib.Path(__file__).resolve().parent.parent` = **kořen repa**
(`E:\Workspaces\forge-orchestra`), ale seznam `BRANY` má **11 literálů starých cest**:

```
["python", "orchestra/tools/kontrola-diakritiky.py"]      <- orchestra/ uz neexistuje
["python", "orchestra/repo/.forge/check-schema.py", "games/uo-shadows"]
GODOT = WS / "orchestra" / "tools" / "godot" / "...console.exe"   <- Godot je v E:\Tools\godot
zdroj_godot = WS / "games" / "uo-shadows" / ".godot"              <- hra je sourozenec
```

**Důkaz, že brány neběží** (ne že jsou červené):
```
### diakritika (brána)   (exit=2)
python: can't open file 'E:\Workspaces\forge-orchestra\orchestra\tools\kontrola-diakritiky.py':
[Errno 2] No such file or directory
```

**Co ověřit v `g3-brany-vystup.txt`: 15 sekcí `exit=2` s `can't open file`.**

**Jak opravit:** cesty **odvodit** (`WS / "tools" / ...`), ne přepsat na novou
absolutní — jinak se vada vrátí při dalším přesunu (to je celý princip P8):

| Starý literál | Správně |
|---|---|
| `orchestra/tools/X` | `WS / "tools" / "X"` |
| `orchestra/repo/.forge/X` | `WS / "repo" / ".forge" / "X"` |
| `games/uo-shadows` | `WS.parent / "uo-shadows"` |
| `WS / "orchestra" / "tools" / "godot"` | `E:\Tools\godot` (nebo `FORGE_GODOT`) |
| `WS / "games" / "uo-shadows"` | `WS.parent / "uo-shadows"` |

**Hotovo znamená:** `g3` vypíše u **všech** bran reálný `exit` a `otevřela:` —
a **počet bran s `can't open file` je 0**. Zapiš obě čísla (kolik bran, kolik
jich neběželo před opravou a po ní).

### 2.2 Úkol B — `test-gitignore-tajemstvi.py`: `NameError` (nález H49)

**Naměřeno spuštěním:**
```
File "E:\Workspaces\forge-orchestra\tools\test-gitignore-tajemstvi.py", line 43, in <module>
  WS = pathlib.Path(STANICE)
NameError: name 'STANICE' is not defined
```

Soubor má na řádku 5 `_PARENT = _pl.Path(__file__).resolve().parents[1]`
(ta je **správně odvozená a nikde se nepoužívá**) a na řádku 43 `STANICE` —
**která nikde definovaná není**. Původní kód měl `STANICE` z hlavičky, kterou
P8 nahradil za `_PARENT`; **použití se přejmenovat zapomnělo.**

Navíc cesty níž jsou ještě ve **starém tvaru struktury**:
```python
GENERATOR = WS / "orchestra" / "install-into-repo.ps1"   # orchestra/ neexistuje
HRA       = WS / "games" / "uo-shadows"                  # hra je sourozenec
```

**Hotovo znamená:** `python tools\test-gitignore-tajemstvi.py` → **`VÝSLEDEK: N kontrol, 0 chyb`**
s **nenulovým počtem kontrol** (vypiš to číslo — „0 kontrol, 0 chyb" není zelená).

### 2.3 Úkol C — `verify-setup.py`: pevná cesta na starý kořen (nález H50)

**Naměřeno spuštěním:** `W = r"C:\Users\Ssevc\Local-Deepseek"` a očekávané
složky `orchestra`, `games`, `games/uo-shadows` → **`CHYBI`**; dále
`HANDOFF.md`, `orchestra/README.md`, `.forge/roadmap.json` → **`No such file`**.

**Pozor, tenhle nástroj už byl jednou zapsaný jako otevřený bod:** `HANDOFF.md`
§2.6 (N8) říká *„`verify-setup.py:11-12` vyžaduje 9 sourozeneckých složek —
dnes `VSE OK`, ale po separaci by hlásil 6× CHYBI"*. **Po přesunu to nastalo** —
a je to **poprvé, co se to proměřilo spuštěním**.

**Rozhodni: opravit, nebo smazat?** Nástroj kontroluje **strukturu staré stanice**
(9 sourozeneckých složek rootu), která **už neexistuje**. Buď ho přepiš na
**dnešní strukturu** (dva repy + stanice), nebo ho **zařaď mezi archivované
jednorázovky** (D5) — a v obou případech **napiš, co bylo důvodem**. Nenech ho
ležet: nástroj, který po přesunu hlásí 6 chyb a nikdo ho nespouští, je
**nastražený**.

### 2.4 Úkol D — `zadani-kontrola.py`: slepý na orchestra (nález H53)

**Naměřeno:** skript si postaví slovník z hlavičky **správně** —
`{'forge-orchestra': 'c3ee946', 'uo-shadows': '869dce8'}` — ale srovnává ho
s klíčem **`orchestra`** (`REPA = [("orchestra", WS), ("uo-shadows", _HRA)]`).
`tvrzene_head.get("orchestra")` → **`None`** → vypíše
`? orchestra: zadání netvrdí žádný commit` a **orchestra se vůbec neporovná**.

**Důsledek, který se nesmí splést:** skript skončil `exit 1` a jeho verdikt
(„zadání je zastaralé") byl **náhodou správný** — ale **ne z toho důvodu, kvůli
kterému existuje**. Kdyby zadání tvrdilo `dea6f5c` (správně), spadl by stejně.
Tohle je přesně past z `overovani` §10.1: **`exit 1` ze špatného důvodu.**

**Jak opravit:** `REPA` musí znát **skutečná jména repů** (`forge-orchestra`,
`uo-shadows`) — a vedle toho musí umět **přečíst jméno z hlavičky**, aby ho
nezapisoval napevno (jinak se vada vrátí při dalším přejmenování).

**Hotovo znamená:** se **správnou** hlavičkou (`dea6f5c`) → `exit 0`; s
**vrácenou vadou** (`c3ee946`) → `exit 1`. **Mutačně dolož obojí.**

### 2.5 Úkol E — skener čte jen git (nález H52)

**Naměřeno:** `seznamy = {repo: soubory(repo) for repo in REPA}`, kde
`soubory()` je `git ls-files`. **Netrackovaný soubor tedy skener nikdy nevidí** —
doloženo: dočasný soubor s `def změř(...)` v kořeni repa dal **0 nálezů**
(v inventáři se neobjevil vůbec).

**Proč to je vada a ne vlastnost:** `hl-rizika-jazyka.py` se používá jako
**brána před commitem** (přesně to dělá `g3` a `validate-all`). Jenže **to, co
se má zkontrolovat, bývá právě to necommitnuté** — nový nástroj, nová funkce.
Brána, která kontroluje jen to, co je už v gitu, **nemůže zabránit commitnutí vady**.
Naměřeno na vlastním omylu akční session: **omyl 137** (`def změř`) našla brána
**až poté, co byl soubor v gitu**.

**Rozhodni a zapiš:** má skener číst **i netrackované** soubory (a vyloučit
artefakty podle `ARTEFAKTY`), nebo má být v docstringu **přiznané**, že měří jen
git? Druhá varianta je přípustná — ale **musí být vidět ve výstupu**
(„ZMĚŘENO: N souborů z gitu; netrackované NEZMĚŘENY").

### 2.6 Úkol F — dočistit `Local-Deepseek` v živém kódu

**Naměřeno (git-trackovaný kód, mimo `_archiv`, oba repy):** **15 souborů**.
Klasifikace:

| Druh | Soubory | Co s tím |
|---|---|---|
| **LEGITIMNÍ (D6)** — kořen stanice | `tools/kontrola-diakritiky.py`, `tools/over-dokumentaci.py`, `_analyza/kronika-kontrola.py`, `_analyza/zadani-kontrola.py`, `_analyza/p9-presun-dokumentu.py` | **nechat** — je to `STANICE` (dokumenty zůstaly stanici) |
| **JEDNORÁZOVKY P8** — pracují na starém stromě | `_analyza/p1-kdo-chybi.py`, `p1-rozdil-mnozin.py`, `p1-rozdil-proti-planu.py`, `p5-presun.py`, `p8-oprava-cest.py`, `p8b-oprava-analyza.py`, `p8b-zjisti-zive.py`, `p8d-oprava-skladanych-cest.py` | **archivovat** (D5) — přesun je hotový, nemají co dělat |
| **KOMENTÁŘE (doložené)** | `install-into-repo.ps1` (2 řádky, příklady použití) | **nechat** — §29.7 to už správně popisuje |
| **VADA** | `tools/verify-setup.py` | **Úkol C** |

**Pozor na dvě věci:** (1) `_analyza/p1-inventura-cest.py` a `p1b-odvozene-cesty.py`
obsahují `Local-Deepseek` **jen jako vzorek (regex)** — to je správně, **nemazat**.
(2) **Starý tvar `orchestra/` je horší než `Local-Deepseek`** — najdi i ten
(`grep` na `"orchestra/` v kódu, ne v dokumentech; v `g3` jich bylo 10).

---

## 3. „Hotovo znamená" pro tuhle session

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | **`g3` spustí všech 29 bran** | v `g3-brany-vystup.txt` je **0** sekcí `can't open file` |
| 2 | **`test-gitignore-tajemstvi.py` projde** | `N kontrol, 0 chyb`, **N > 0** |
| 3 | **`verify-setup.py` je opravený NEBO archivovaný** | a je **napsáno proč** |
| 4 | **`zadani-kontrola.py` sedí na správnou i vrácenou hlavičku** | mutačně: `dea6f5c` → 0, `c3ee946` → 1 |
| 5 | **U skeneru je rozhodnuto o netrackovaných souborech** | a je to **vidět ve výstupu** |
| 6 | **Každá oprava má mutační test** | s vrácenou vadou brána **spadne** |
| 7 | `python _analyza\kronika-kontrola.py` → `exit 0` | řádek 26 + H48–H56 sedí |
| 8 | `python _analyza\handoff-kontrola-uplnost.py` → `83/83` (nebo víc) | bez újmy |
| 9 | V chatu je **prompt pro uživatele** i **stavový řádek** | ke zkopírování |

---

## 4. Co NEDĚLAT

- **Nepřesouvat nic zpátky.** Přesun je ověřený; návrat by byl regrese.
- **Nedělat junctionu** na staré místo (záměr, P7).
- **Nepřepisovat historické citace cest** v `ANALYZA-*`, `HANDOFF.md`,
  `KRONIKA-PROJEKTU.md` a `_analyza/_archiv/` — jsou to **záznamy**.
- **Nepřepisovat `HANDOFF.md`** — jen **přidávat** (nic nesmí zmizet).
- **Nemazat `_analyza/_archiv/`** ani `_analyza/zaloha/`.
- **Neopravovat cesty přepsáním na novou absolutní** — **odvozuj** je
  (`__file__` / `import.meta.url` / `WS.parent`). To je princip P8.
- **Nepushovat bez vyžádání.** Předem ukázat `git status` a `git diff --stat`.
- **Nezaměňovat `E:\Workspaces\forge-orchestra` a `E:\Workspaces\uo-shadows`.**
- **Nespouštět `Get-PSDrive` jako důkaz o místě na disku** (nález **H56**).

---

## 5. Naměřená východiska (aby se nemusela měřit znovu)

```
# hlavička
git -C E:\Workspaces\forge-orchestra rev-parse --short HEAD   -> dea6f5c
git -C E:\Workspaces\uo-shadows      rev-parse --short HEAD   -> 869dce8
git -C E:\Workspaces\forge-orchestra rev-list --count origin/main..HEAD  -> 6
git -C E:\Workspaces\uo-shadows      rev-list --count origin/main..HEAD  -> 1

# brány (spuštěno 4. 10. 2026 plánovací session, plné oprávnění)
python tools\over-dokumentaci.py        -> 67 kontrol, 0 chyb, exit 0
python tools\kontrola-diakritiky.py     -> otevřeno 149 z 193 (archivováno 44), exit 0
python tools\over-skilly.py             -> 13 skillů, 0 chyb, exit 0
python _analyza\hl-rizika-jazyka.py     -> 0 vrácených, 11 textových, exit 0
python _analyza\ag-over-cisla.py        -> 5 v pořádku, 2 historická, 0 rozchodů, exit 0
python _analyza\kronika-kontrola.py     -> 132 omylů, 47 nálezů, 24 sessions, exit 0
python _analyza\handoff-kontrola-uplnost.py -> 83/83, exit 0
python _analyza\hl2-kontrola.py         -> 10/10, exit 0
python _analyza\a3-over.py              -> 23 kontrol, exit 0
python _analyza\a1-a2-over.py           -> 23 kontrol, exit 0
python _analyza\ag-mutace.py            -> mutační (2/2), exit 1 = SPRÁVNĚ
python _analyza\n1-over-inventar.py     -> mutační, exit 1 = SPRÁVNĚ
node tools\kontrola-driftu.mjs          -> 12 souborů, 1 rozdíl, exit 1

# g3 (přehled) — POZOR: tohle je soubor, který je potřeba opravit
python _analyza\g3-brany.py   -> brán celkem 30, s nenulovým exit 21,
                                 15 z nich "can't open file" (neběžely)

# struktura
_analyza/_archiv:        333 souborů   (git ls-files -> 0, gitignore řádek 74)
_analyza (soubory):      191           z toho .py: 46
tools (soubory):          69           z toho .py: 26
git ls-files: orchestra 335 + hra 670 = 1005
```

---

## 6. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi AKČNÍ session. Repa jsou na E:
  orchestra = E:\Workspaces\forge-orchestra
  hra       = E:\Workspaces\uo-shadows

Zadání pro tebe je v E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md
— přečti ho CELÝ.

Kontext: plánovací session NEZÁVISLE OVĚŘILA přesun na E: (HANDOFF.md §30,
nálezy H48–H56, KRONIKA řádek 26). Jádro přesunu obstálo — data sedí, historie
nedotčená, žádná junctiona. Ale našla PĚT rozbitých měřidel a tvůj úkol je
opravit je. Hlavní je Úkol A: _analyza/g3-brany.py spouští 15 z 29 bran po
STARÝCH cestách (orchestra/tools/...), takže ty brány VŮBEC NEBĚŽÍ a jejich
exit=2 se čte jako "červená".

Pořadí: A (g3) → B (test-gitignore) → C (verify-setup) → D (zadani-kontrola)
→ E (skener) → F (dočistit cesty). Každou opravu dolož MUTAČNÍM TESTEM —
u čtyř z pěti jde právě o to, že brána tiše neměří.

Cesty ODVOZUJ (__file__ / WS.parent), nepřepisuj na novou absolutní.
Nepřepisuj HANDOFF.md (jen přidávej), nemaž _analyza/_archiv/, nepoushej
bez vyžádání.

Na konci povinně: přepiš NEXT-SESSION-INSTRUKCE.md pro další session, zapiš
výsledky a omyly do HANDOFF.md, doplň řádek do KRONIKA-PROJEKTU.md
(a rozhodni návrhy ve stavu NEOVĚŘENO), a do chatu vlož prompt pro uživatele
i se STAVOVÝM ŘÁDKEM.
```
