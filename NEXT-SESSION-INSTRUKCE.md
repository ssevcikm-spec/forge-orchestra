# ZADÁNÍ PRO PLÁNOVACÍ (OVĚŘOVACÍ) SESSION — ověř přesun na `E:`

**Zkontrolováno při:** `c3ee946` („P12 — zápis provedení přesunu na E:") · **4. 10. 2026, 21:0x UTC**
**Stav obou repů při psaní:** `forge-orchestra` = `c3ee946` · `uo-shadows` = `869dce8`
**Pushnuto:** **NE** — `origin/main..HEAD = 4` (orchestra) a **1** (hra). Push **jen na vyžádání**.
**⚠ Pracovní stromy jsou ČISTÉ** (zápis P12 je commitnutý v `c3ee946`).
**Kde jsou repa:** `E:\Workspaces\forge-orchestra` · `E:\Workspaces\uo-shadows` (sourozenec) · Godot `E:\Tools\godot\`
**Co je v `HANDOFF.md`:** §29 (provedení přesunu, nová) · **§8q** (omylly 132–137) · §2 (co je otevřené)
**Co je v `PLAN-SEPARACE-WORKSPACE.md`:** **§11 = ZÁZNAM O PROVEDENÍ** (co se stalo, nálezy H40–H47, co zůstává otevřené) · §10 = plán + záznam o validaci (nepřepisuje se)
**Co je v `KRONIKA-PROJEKTU.md`:** řádek **25** (přesun) + nálezy **H40–H47** v §2
**Co tenhle dokument JE:** **zadání pro PLÁNOVACÍ session**, jejímž cílem je **ověřit práci akční session** — ne ji zopakovat ani „dokončit".

---

## 0. ⚠ Tohle je práce AKČNÍ session, kterou je potřeba nezávisle ověřit

Akční session provedla **přesun orchestra a hry na `E:`** (kroky P0–P12). **Sama
sebe prohlásila za hotovou** — a podle `PREDAVANI-SESSION.md` §5 to **není**
důkaz. Tvůj úkol je **zkusit ji vyvrátit**.

**Tvrdí (a musíš to ověřit spuštěním, ne čtením):**

| # | Co akční session tvrdí | Kde to tvrdí |
|---|---|---|
| 1 | Přesun proběhl a **data sedí na bajt** | `PLAN-SEPARACE-WORKSPACE.md` §11.2 |
| 2 | Oba `.git` jsou v pořádku, historie nedotčená | §11.2 |
| 3 | **Žádná junctiona** na staré místo neexistuje | §11.2, `HANDOFF.md` §29.2 |
| 4 | **Cesty v kódu se odvozují**, žádná nevede na `C:\...\orchestra` | §11.3 |
| 5 | **`AGENTS.md` je v obou repech** — a orchestra ho **předtím neměla** | §11.4, `HANDOFF.md` §29.4 |
| 6 | **12 bran je zelených** | `HANDOFF.md` §29.5 |
| 7 | Archivováno **317** jednorázovek, v `_analyza/` zůstalo **50** | `HANDOFF.md` §29 |
| 8 | **`_analyza/_archiv/` je gitignorovaný** a v gitu není | §11.1 |
| 9 | Nálezy **H40–H47** jsou naměřené, ne odhadnuté | kronika §2 |

---

## 1. Cíl (jedna věta)

**Nezávisle ověřit, že přesun na `E:` proběhl tak, jak §11 tvrdí — a najít,
co akční session PŘEHLÉDLA, protože o sobě tvrdila, že je hotová.**

---

## 2. Povinné kroky ověření

### 2.1 Hlavička a živý stav (POVINNĚ PRVNÍ)

1. `git -C E:\Workspaces\forge-orchestra rev-parse HEAD` → musí být **`c3ee946`**
   (nebo novější, pokud session mezitím commitla zápis P12 — pak to **je nález**).
2. `git -C E:\Workspaces\uo-shadows rev-parse HEAD` → **`869dce8`**.
3. Když **nesedí**: strom se pohnul → **přeměř všechna tvrzení** a zapiš to jako
   **nález**. **Nepřepisuj zadání podle sebe** (`PREDAVANI-SESSION.md` §6.2 B).
4. Ověř, že **staré cesty už neexistují**:
   `Test-Path C:\Users\Ssevc\Local-Deepseek\orchestra` → **False**;
   totéž `games\uo-shadows`; `Test-Path E:\Tools\godot\Godot_v4.7.2-stable_win64_console.exe` → **True**.

### 2.2 Ověř aspoň PĚT tvrzení SPUŠTĚNÍM (ne čtením)

Ke každému **spusť příkaz a podívej se na VÝSTUP**, ne na `exit 0`:

| # | Tvrzení | Čím to ověříš |
|---|---|---|
| 1 | **cesty se odvozují** | `grep` na `Local-Deepseek` v kódu obou rep → **musí zbýt jen `install-into-repo.ps1` (2 řádky komentáře)**. Když zbude víc, je to nález |
| 2 | **brány měří z nového místa** | spusť **všech 12** z `HANDOFF.md` §29.5 a u každé si zapiš, **kolik toho otevřela** (past S27: „zelená bez čísla" **není** zelená) |
| 3 | **`AGENTS.md` je v obou repech** | `Test-Path` + **přečti, co v nich je** — musí obsahovat projektová pravidla, ne prázdný soubor |
| 4 | **archiv je gitignorovaný** | `git check-ignore _analyza/_archiv/x.py` → cesta; a `git ls-files _analyza/_archiv` → **0** |
| 5 | **žádná junctiona** | `Test-Path` na obě staré cesty → **False**; `Get-Item` na staré cesty → **neexistuje** (ne jen „LinkType prázdný") |

### 2.3 Ověř, že brány po přesunu měří TOTÉŽ co před ním

**Tohle je jádro ověření a akční session to mohla pokazit:** při přesunu se
**změnil rozsah měření** hned u **dvou** měřidel (nálezy **H43**, **H44**, **H45**).
U každé opravy měřidla se ptej: **měří teď brána totéž co před přesunem — nebo
něco jiného, jen to vypadá lépe?**

Konkrétně prověř (a **mutačním testem**, ne čtením):

| Brána | Co akční session změnila | Na co se ptát |
|---|---|---|
| `tools/kontrola-diakritiky.py` | archivované soubory **přeskakuje** a vypisuje | Není to **oslabení**? Když vrátím soubor z archivu zpět, **otevře ho**? A když do živého souboru vrátím rozbitou diakritiku, **spadne**? |
| `_analyza/ag-over-cisla.py` | měří **jen zdrojový kód** (ne vše na disku) | Nezmizel tím nález, který tam **byl**? Zkus do zdrojového kódu vložit non-ASCII název → **musí** ho najít |
| `_analyza/hl-rizika-jazyka.py` | padá **jen na identifikátorech** | Není to **slepota**? Vlož do kódu **identifikátor** s diakritikou → **musí** spadnout. (Pozor: akční session sama tuhle vadu měla — omyl **137**.) |
| `_analyza/kronika-kontrola.py` | tři kořeny místo jednoho | Nezmizel tím nález? Vlož do kroniky odkaz na **neexistující** soubor → **musí** spadnout |

**Každá z těch změn je „oprava měřidla" — a podle `AGENTS.md` platí: *opravuješ-li
měřidlo, mutačně ověř OPRAVU, ne jen to, že původní vada zmizela.***

### 2.4 Hledej, co v `HANDOFF.md` NENÍ

1. `python _analyza\handoff-kontrola-uplnost.py` → musí být **83/83**.
2. **Projdi §29.7** („co zůstává otevřené") a u **každého** bodu rozhodni:
   *ještě otevřený? má cenu teď? co to blokuje?*
3. **Porovnej §2 a §28 s §29** — akční session tvrdí, že nic nemazala.
   Ověř to **hledáním**, ne dojmem.
4. `python _analyza\kronika-kontrola.py` → `exit 0`; a zkontroluj, že řádek
   **25** a nálezy **H40–H47** v kronice **odpovídají** `HANDOFF.md` §29.

### 2.5 Ověř rozhodnutí D1–D9 — byla DODRŽENA?

Plán §10.3b je **závazný**. U každého rozhodnutí zkontroluj, že se **skutečně
provedlo** (a kde to je vidět):

| # | Rozhodnutí | Čím se to ověří |
|---|---|---|
| **D1** | složky `forge-orchestra` a `uo-shadows` | `Test-Path E:\Workspaces\...` |
| **D2** | dva samostatné workspaces | oba mají `.git` **i** `AGENTS.md` ve svém kořeni |
| **D3** | dokumenty + živé nástroje commitnuté; archiv gitignorovaný | `git ls-files` v repu; `git check-ignore` u archivu |
| **D4** | `FORGE_HRA` + `--hra`, výchozí `..\uo-shadows` | **spusť** `node tools\kontrola-driftu.mjs` → musí najít hru **12 souborů, 1 známý rozdíl** |
| **D4b** | **3** nástroje zapisují do hry | `grep FORGE_HRA` → tři soubory |
| **D5** | archivovat, opravit živé | počet živých vs. archivovaných (a **nález H40**: 18 vs. 29) |
| **D6** | dokumenty stanice zůstaly; brány mají **druhý root `STANICE`** | `grep STANICE` v `kontrola-diakritiky.py` a `over-dokumentaci.py`; **a že to není mrtvá proměnná** |
| **D7** | Godot = obecný nástroj `E:\Tools\godot\` | `Test-Path` + `hra.cmd` **funguje bez** `FORGE_GODOT` (spusť ho a podívej se, že najde Godot) |
| **D8** | `.secrets` jde s orchestrou; ACL se neopraví | `Test-Path E:\Workspaces\forge-orchestra\.secrets`; **a že není v gitu** |
| **D9** | `game-clone` + `idle-realm` = teď NE | jen ověř, že se **neudělalo** nic navíc |

### 2.6 Nové otázky, které akční session otevřela

Rozhodni u každé: **je ještě otevřená? má cenu teď? co to blokuje?**

- **18 vs. 29 živých nástrojů** (nález H40) — má `g3-brany.py` a jeho 29
  spouštěných nástrojů patřit mezi živé? **Rozhodni.**
- **`install-into-repo.ps1` a `test-local.ps1:39`** — opravit, nebo smazat?
  (Jsou mimo provoz **už dnes**, ne kvůli přesunu.)
- **Kritérium „`grep` na `Local-Deepseek` → 0"** ze zadání je **nepřesné**:
  zbývá `install-into-repo.ps1` ve **dvou komentářích**. Je to splněné, nebo ne?
- **`_analyza/_archiv/` není nikde zálohovaný** (jen na `E:`, gitignorovaný) —
  je to riziko?
- **`HANDOFF.md` a `KRONIKA-PROJEKTU.md` se přesunuly do repa** — ale
  `PREDAVANI-SESSION.md` a `MOZNOSTI-AGENTA.md` **zůstaly stanici**. Je to
  správně? (Stanice je používá i pro DSH.)

---

## 3. „Hotovo znamená" pro tuhle session

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | **Každé tvrzení o stavu je ověřené měřením** | s příkazem a výstupem |
| 2 | **Aspoň jedno tvrzení je vyvrácené nebo zpřesněné** | když opravdu nic, **napiš i to** — „nic jsem nevyvrátil" je tvrzení, které se ověřuje |
| 3 | **U KAŽDÉ brány je ověřeno, že soubor otevřela** | vypsaný **počet** zpracovaných souborů/kontrol |
| 4 | **Každá oprava měřidla z §11.3 má mutační test** | je vidět, že s **vrácenou vadou** brána **spadne** |
| 5 | Odpověď na „co zůstalo otevřené" | nová sekce v `HANDOFF.md`; `handoff-kontrola-uplnost.py` → bez újmy |
| 6 | `python _analyza\kronika-kontrola.py` → `exit 0` | a řádek 25 + H40–H47 sedí |
| 7 | **Rozhodnutá D1–D9 ověřena jako DODRŽENÁ** | tabulka §2.5 s výsledkem u každého |
| 8 | V chatu je **prompt pro uživatele** i **stavový řádek** | ke zkopírování, ne odkaz |

---

## 4. Co NEDĚLAT

- **Neopravovat kód.** Jsi **plánovací** session — piš zadání, ne opravy.
  Když najdeš vadu, **zapiš ji jako nález** a navrhni opravu pro akční session.
- **Nepřesouvat nic zpátky.** Přesun je hotový a ověřený; návrat by byl regrese.
- **Nedělat junctionu** na staré místo (záměr, P7).
- **Nepřepisovat historické citace cest** v `ANALYZA-*`, `HANDOFF.md`,
  `KRONIKA-PROJEKTU.md` a `_analyza/_archiv/` — jsou to **záznamy** o tom,
  kde co bylo. (Akční session to **sama respektovala** — nález H47.)
- **Nepřepisovat `HANDOFF.md`** — jen **přidávat** (nic nesmí zmizet).
- **Nemazat `_analyza/_archiv/`** ani `_analyza/zaloha/` — je to cesta zpět.
- **Nepushovat bez vyžádání.** Předem ukázat `git status` a `git diff --stat`.
- **Nezaměňovat `E:\Workspaces\forge-orchestra` a `E:\Workspaces\uo-shadows`** —
  jsou to **dva různé repy** s dvěma různými `AGENTS.md`.

---

## 5. Než začneš (povinné pořadí)

1. **Přečti** `HANDOFF.md` **§29** (provedení), **§2** (co je otevřené) a **§8q**
   (omylly 132–137) — a `PLAN-SEPARACE-WORKSPACE.md` **§11**.
2. **Přečti** `PREDAVANI-SESSION.md` §5 a §6.1 (role plánovací session).
3. Načti skilly **`dsh-prostredi`** a **`overovani`**.
4. **Ověř hlavičku** (§2.1) — a **aspoň pět tvrzení spuštěním** (§2.2).
5. **Když něco nesedí:** zastav se **v tom bodě**, zapiš to jako nález a jdi dál
   na body, které sedí. **Nepřepisuj zadání podle sebe.**

---

## 6. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi PLÁNOVACÍ (ověřovací) session. Repa jsou na E:
  orchestra = E:\Workspaces\forge-orchestra
  hra       = E:\Workspaces\uo-shadows
Zadání pro tebe je v E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md
— přečti ho CELÝ.

Záznam o přesunu je v PLAN-SEPARACE-WORKSPACE.md §11, stav v HANDOFF.md §29
(a §2 = co je otevřené), omyly té session v §8q. Pravidla v AGENTS.md
(orchestra má vlastní, hra má vlastní). Postup předávání v PREDAVANI-SESSION.md
(ten zůstal na stanici: C:\Users\Ssevc\Local-Deepseek).

Tvůj úkol NENÍ přesun dokončit — je ho NEZÁVISLE OVĚŘIT. Akční session
o sobě tvrdí, že je hotová; zkus to vyvrátit.

Než začneš:
1. Ověř hlavičku: git rev-parse HEAD v obou repech proti tomu, co zadání tvrdí.
   Když nesedí, přeměř VŠECHNA tvrzení o stavu a zapiš to jako nález.
2. Ověř aspoň PĚT klíčových tvrzení SPUŠTĚNÍM, ne čtením (tabulka v §2.2).
3. Zvlášť prověř, že opravy měřidel (§2.3) nejsou OSLEBENÍ — mutačním testem.
4. Ověř, že rozhodnutí D1-D9 byla DODRŽENA (§2.5).
5. Když něco nesedí, zastav se v tom bodě a jdi dál na body, které sedí.

Na konci povinně: přepiš NEXT-SESSION-INSTRUKCE.md jako zadání pro AKČNÍ
session, zapiš výsledky a omyly do HANDOFF.md (nic nemazat), doplň řádek do
KRONIKA-PROJEKTU.md (a rozhodni návrhy ve stavu NEOVĚŘENO), a do chatu vlož
prompt pro uživatele i se STAVOVÝM ŘÁDKEM.
```
