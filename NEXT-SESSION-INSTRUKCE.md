# ZADÁNÍ PRO AKČNÍ (PROVÁDĚCÍ) SESSION — přesun orchestra a hry na `E:`

**Zkontrolováno při:** `c2f730f` (`roadmapa: entity.player hotová (DAG bez world.map) + smlouva`) · **4. 10. 2026, 20:1x UTC**
**Stav obou repů při psaní:** `orchestra` = `c2f730f` · `uo-shadows` = `0fdc784`
**Pushnuto:** **oba ANO** — `origin/main..HEAD = 0` (naměřeno). ⚠ Pracovní strom **orchestra má 2 změněné** soubory (`tools/over-dokumentaci.py`, `tools/kontrola-diakritiky.py` — přepojení bran ze 4. 10., **necommitnuto**); hra **čistá**.
**Co je v `HANDOFF.md`:** §28 (výsledky validace, nová sekce) · §2 (co je otevřené)
**Co je v `PLAN-SEPARACE-WORKSPACE.md`:** **§10.3b = ROZHODNUTÍ D1–D9 (závazná)** · **§10.2b = přeměřená císla** · **§10.7 = záznam o validaci**
**Co je v `KRONIKA-PROJEKTU.md`:** řádek **24** (přesun obecných pravidel + validace)
**Co tenhle dokument JE:** **zadání pro AKČNÍ session**, která přesun **provede**. Není to stav (`HANDOFF.md`) ani plán (`PLAN-SEPARACE-WORKSPACE.md` §10).

> **⚠ Přečti nejdřív tohle:** plán prošel **validací** (4. 10. 2026, devět bodů
> V1–V9 spuštěním). Validace **opravila 8 tvrzení** plánu — a **kdo bude číst
> §10.1–§10.6 bez §10.2b a §10.3b, bude pracovat se zastaralými čísly.**
> Rozhodnutí D1–D9 **už padla** — **nerozehravuj je znovu**, jen je prováděj.

---

## 0. Rozhodnutí, která už PADLA (nerozhoduj znovu, jen prováděj)

| # | Rozhodnutí | Závazné pro krok |
|---|---|---|
| **D1** | Složky **`forge-orchestra`** a **`uo-shadows`** (shodné s názvy rep) | P5 |
| **D2** | **DVA samostatné workspaces**, každý = kořen svého repa | P10, P9 |
| **D3** | Dokumenty **+ 18 živých nástrojů** do repa a **COMMITNOUT**; archiv 99 **gitignorovat** | P8b, P9, P8c |
| **D4** | `FORGE_HRA` (env) + `--hra`, výchozí **`..\uo-shadows`** (sourozenec) | P8 |
| **D4b** | **3** nástroje zapisují do hry (ne 4) → **3× schvalování** při zápisu mimo workspace | P8, P11 |
| **D5** | **Archivovat 99** do `_analyza\_archiv\`, opravit **18 živých** + `_analyza\cesty.py` | P8b |
| **D6** | Dokumenty stanice **zůstávají stanici**; brány orchestra dostanou **druhý root `STANICE`** | P8 |
| **D7** | Godot = **obecný nástroj** → `E:\Tools\godot\`; `hra.cmd` dostane **funkční fallback** + `FORGE_GODOT` override | P5, P8 |
| **D8** | `.secrets` jde s orchestrou; **ACL se neopravuje** (samostatný nález S9) | — |
| **D9** | `game-clone` + `idle-realm` = **samostatný úkol, teď NE** | — |

---

## 1. Cíl (jedna věta)

**Přesunout `orchestra` a `games\uo-shadows` na `E:` podle §10 plánu tak, aby
žádná cesta nezůstala tiše fungovat — a aby se po přesunu dalo měřením říct,
co se rozbilo přesunem a co bylo rozbité už před ním.**

**Hlavní riziko (naměřené, ne dohad):** pracovní jednotka je **176 souborů**
s pevnou cestou (ne „208 výskytů") — a **`install-into-repo.ps1` dokazuje, že
existují i cesty ODVOZENÉ** (`Split-Path $PSScriptRoot -Parent`), které sken
přímých cest **nevidí**. Kdo opraví jen to, co sken našel, nechá tiše fungovat
odvozené cesty.

---

## 2. Co je naměřeno (s příkazem) — a co se MUSÍ přeměřit

**Validace proběhla 4. 10. 2026 19:5x–20:1x UTC. Devět bodů V1–V9 je v
`PLAN-SEPARACE-WORKSPACE.md` §10.7 — i s tím, co vyvrátily.** Tady je jen to,
co akční session potřebuje při ruce:

| Co | Příkaz | Naměřeno 20:0x |
|---|---|---|
| Živý stav repů | `git -C <repo> rev-parse HEAD` + `status --porcelain` | orchestra `c2f730f` + **2 M** · hra `0fdc784` čistá |
| Push | `git -C <repo> rev-list --count origin/main..HEAD` | **0 / 0** |
| Pages | `node orchestra\tools\zjisti-pages.mjs` | `release.yml` **#76 completed/success** na `0fdc784` |
| Cena přesunu | `python _analyza\sken-cest-celek.py` | **KÓD 208** · DOKUMENTY 128 · **176 souborů** (§10.2b) |
| Kdo píše do hry | `python _analyza\skryte-vazby-na-hru.py` | 13 kandidátů, **3 živé** (§10.7) |
| Cíle | `Test-Path` + `Get-ChildItem -Force` | obě složky **existují, prázdné** |
| Disk `E:` | `New-Object System.IO.DriveInfo('E')` | **810,8 GB** volných ⚠ **ne** `Get-PSDrive` (hlásí 0) |
| Velikosti (P3) | Python walk | orchestra **5 447 / 1 176,4 MB** · hra **1 787 / 16,1 MB** |
| `.git` / `AGENTS.md` | `Test-Path` | `.git` True/True · `AGENTS.md` **False/False** |

> **⚠ Povinně přeměř hlavičku a živý stav, než sáhneš na cokoli.** Když
> `git rev-parse HEAD` nesedí na `c2f730f`/`0fdc784`, **strom se pohnul** →
> přeměř **všechna** čísla výš a zapiš to jako nález. **Nepřepisuj zadání
> podle sebe** — ztratila by se informace, že zadání bylo vadné
> (`PREDAVANI-SESSION.md` §6.2 B).

---

## 3. Kroky P0–P12 (pořadí je závazné) — s „Hotovo znamená"

### P0 — PŘEDPOKLAD: čisté pracovní stromy ✋ **POTŘEBUJE SOUHLAS UŽIVATELE**

| Co | Hotovo znamená |
|---|---|
| Ukázat `git status` a `git diff --stat` v orchestra a **počkat na vyžádání** | Uživatel viděl oba výstupy |
| Po souhlasu commitnout **2 soubory** (`tools/over-dokumentaci.py`, `tools/kontrola-diakritiky.py`) — přepojení bran ze 4. 10. | `git -C orchestra status --porcelain` → **prázdné** v **obou** repech |

**Proč první:** přesun s necommitnutou prací je hazard — po přesunu se nedá
rozlišit, co rozbil přesun a co bylo rozdělané.

### P1 — Inventura cest **po SOUBORECH** (ne po výskytech)

| Co | Hotovo znamená |
|---|---|
| Zapsat seznam **176 souborů** (117 `_analyza/`, 51 `orchestra/`, 5 root, 2 stanice, 1 hra) s rozhodnutím `opravit` / `archivovat` u každého | Soubor existuje; počty sedí na `sken-cest-celek.py` **a** na rozpad v §10.2b |

### P1b — **NOVÝ KROK:** dohledat ODVOZENÉ cesty

| Co | Hotovo znamená |
|---|---|
| Najít soubory, které cestu **odvozují** (`PSScriptRoot`, `Split-Path … -Parent`, `import.meta.url`, `__file__`, `parents[1]`) a **vysvětlit, kam odvozují** | Seznam existuje; u každého je řečeno, jestli po přesunu odvodí **správně**, nebo tiše jinam |

**Proč:** `install-into-repo.ps1:34` bere `$ProjDir` z **rodiče repa** → dnes
hledá `…\Local-Deepseek\projects\` (neexistuje, nástroj **neběží**). Po přesunu
bude hledat `E:\Workspaces\projects\` — **jinam, a pořád tiše.**

### P2 — Rozhodnutí D1–D9 ✅ **HOTOVO** (viz §0 a plán §10.3b)

| Co | Hotovo znamená |
|---|---|
| Nic nerozhodovat znovu; jen ověřit, že §10.3b v plánu odpovídá tomu, co děláš | U každého kroku je dohledatelné, které rozhodnutí ho zdůvodňuje |

### P3 — Změřit a zapsat velikosti **PŘED** přesunem

| Co | Hotovo znamená |
|---|---|
| Počet souborů + velikost obou stromů | Čísla zapsaná; **před** přesunem naměřeno orchestra **5 447 / 1 176,4 MB**, hra **1 787 / 16,1 MB** (P3 v §10.4 má zastaralá čísla) |

### P4 — Ověřit cílové cesty a volné místo

| Co | Hotovo znamená |
|---|---|
| `Resolve-Path` na obě cílové složky; volné místo přes `System.IO.DriveInfo` | Obě cesty **jsou prázdné adresáře**; `E:` **≥ 2 GB** (naměřeno 810,8 GB) |

### P5 — Přesun

| Co | Hotovo znamená |
|---|---|
| **Nejdřív** vyndat `orchestra\tools\godot\` (172 MB) do `E:\Tools\godot\` (D7) | `Test-Path E:\Tools\godot\Godot_v4.7.2-stable_win64_console.exe` → **True**; v orchestra `tools\godot` **už není** |
| Pak `robocopy /MOVE /XJ /E` pro **oba** stromy (orchestra → `E:\Workspaces\forge-orchestra`, hra → `E:\Workspaces\uo-shadows`) | Počet souborů a velikost **po** = čísla z P3 **minus Godot** u orchestra (zapiš obojí!) |

### P6 — Ověřit oba `.git`

| Co | Hotovo znamená |
|---|---|
| `git rev-parse --show-toplevel` v obou nových cestách | Ukazuje **na novou** cestu |
| `git status --porcelain` | **Stejný počet řádků** jako před přesunem (po P0 tedy 0/0) |
| `git log -1 --format=%h` | **`c2f730f`** a **`0fdc784`** — historie nedotčená |

### P7 — ŽÁDNÁ junctiona na staré místo (záměr)

| Co | Hotovo znamená |
|---|---|
| Zkontrolovat, že na starém místě nic nevede | `Test-Path C:\Users\Ssevc\Local-Deepseek\orchestra` → **False**; totéž hra |

**Proč schválně:** junctiona by **tiše skryla** každou nepřepsanou cestu.
Chceme, aby cesty **spadly nahlas** — ne aby fungovaly dál a rozbily se jindy.

### P8 — Opravit cesty (tady se to musí rozbít nahlas)

| Co | Hotovo znamená |
|---|---|
| Opravit podle P1 (jen `opravit`): `__file__` / `import.meta.url` místo literálů | **`grep` na `Local-Deepseek` v kódu obou rep → 0** (kromě archivovaných) |
| `FORGE_HRA` + `--hra` s výchozí **`..\uo-shadows`** v **3 živých** nástrojích | Nástroje jdou spustit z jiné složky i pro jinou hru |
| `FORGE_GODOT` do `test-local.ps1:54–56`, `validate-all.mjs:118`, `verify-setup.py:37`, **`hra.cmd:13`** | `hra.cmd` **funguje i bez** nastavené proměnné (fallback na `E:\Tools\godot\…`); `grep` na `..\..\orchestra` ve hře → **0** |
| **Druhý root `STANICE`** do `kontrola-diakritiky.py` a `over-dokumentaci.py` (D6) | Obě brány po přesunu **otevřou** dokumenty stanice — a **vypíšou, kolik jich otevřely** |
| `verify-setup.py` přepsat (seznam 9 sourozenců) | Skončí **OK** a kontroluje jen to, co orchestře patří |
| Smazat mrtvé cesty na `gameforge/` | `grep` → 0; `validate-all.mjs` se nerozbil |

### P8b — **NOVÝ KROK:** archivace `_analyza\` (D5)

| Co | Hotovo znamená |
|---|---|
| Přesunout **99** souborů nezmíněných v `AGENTS.md` do `_analyza\_archiv\` | V `_analyza\` zůstane **18 živých**; archiv má **99** souborů; **seznam archivovaného je zapsaný** (co, odkud, proč) |
| Z zavést `_analyza\cesty.py` (env → config → odvození) pro živé | Živé nástroje berou cesty z jednoho místa; `grep` na `Local-Deepseek` v živých → **0** |

### P8c — **NOVÝ KROK:** `.gitignore` pro `_analyza\` (D3)

| Co | Hotovo znamená |
|---|---|
| Přidat: `_inventar.json`, `snapshot-*`, `ci-rozbal*`, `tmp-*`, `*-scratch/`, `_zaloha*`, `handoff-pred-*`, `*vystup.txt`, `_archiv/` | `git status --porcelain` v novém repu **neukazuje** ani jeden z nich; `git check-ignore` u každého vzoru potvrdí |

**Proč:** do **veřejného** repa by se jinak commitly CI logy, snapshoty
dokumentace a zálohy handoffu (naměřeno: `a-ukol-scratch\.forge\vision\baseline.json`
má **272** šedesátičtyřznakových hashů, `_inventar.json` je generovaný meziprodukt).

### P9 — `AGENTS.md` do obou repů + commit dokumentů

| Co | Hotovo znamená |
|---|---|
| `E:\Workspaces\forge-orchestra\AGENTS.md` = **projektová pravidla** z rootu `Local-Deepseek` (**přesun, ne kopie** — z rootu se ta část **odstraní**) | Soubor existuje **a je načtený** (ověřeno v nové session!) |
| `E:\Workspaces\uo-shadows\AGENTS.md` = nová, **malá** pravidla hry (design, smlouvy, brány hry) | Soubor existuje a je načtený |
| Dokumenty + **18 živých** nástrojů **commitnout**; archiv **gitignorovat** (D3) | `git log` v orchestra má nový commit s dokumenty; `_analyza\_archiv\` v gitu **není** |

**⚠ Tohle je nejsnazší krok na pokažení:** `orchestra\` má `.git` a **NEMÁ**
`AGENTS.md`. Když se session otevře s cwd v repu **dřív**, než tam `AGENTS.md`
je, DSH najde projektový root v repu a **root `AGENTS.md` přestane načítat** →
agent nedostane **žádná** projektová pravidla. Naměřeno: `.git` True,
`AGENTS.md` **False**.

### P10 — Zaregistrovat **DVA** workspaces (D2)

| Co | Hotovo znamená |
|---|---|
| Zaregistrovat `E:\Workspaces\forge-orchestra` a `E:\Workspaces\uo-shadows` a otevřít v nich **nové** session | Nová session vidí **správná** pravidla (ověř **výpisem**, ne dojmem) |
| Staré session **nechat být** | Dokumentace: *„a session from another directory cannot be moved in"* — přesunout je **nelze** |

### P11 — Spustit brány z nového místa

| Co | Hotovo znamená |
|---|---|
| Spustit brány z `HANDOFF.md` §6 a porovnat s referencí | Čísla sedí; **co nesedí, je regrese přesunu** a musí být **pojmenované** |
| U **každé** brány ověřit, že **soubor otevřela** (kolik jich zpracovala) | U každé je vypsaný počet; „zelená bez čísla" **není** zelená |
| Ověřit, že **3 nástroje zapisující do hry** fungují (a že si vyžádají schválení) | Zápis proběhl **po** schválení, ne tiše |

### P12 — Zapsat provedení

| Co | Hotovo znamená |
|---|---|
| Nový oddíl `§11` v `PLAN-SEPARACE-WORKSPACE.md` + řádek v `KRONIKA-PROJEKTU.md` + nová sekce v `HANDOFF.md` | Všechny tři existují; z `HANDOFF.md` **nic nezmizelo** (`handoff-kontrola-uplnost.py`) |

---

## 4. Co NEDĚLAT (tvrdé zákazy)

- **Nepřesouvat po částech.** Přesun s polovinou opravených cest je **horší**
  než nepřesunuté — nedá se rozlišit, co rozbil přesun.
- **Nedělat junctionu** na staré místo (P7) — je to záměr, ne opomenutí.
- **Nepřepisovat historické citace cest** v `ANALYZA-*`, `HANDOFF.md`,
  `KRONIKA-PROJEKTU.md` a `_analyza\_archiv\` — jsou to **záznamy** o tom, kde
  co bylo. Kdo je „opraví", maže důkazy.
- **Nerozhodovat znovu D1–D9.** Jsou rozhodnutá (§0); akční session je **provádí**.
- **Nemazat `_analyza\_archiv\`** ani `_analyza\zaloha\` (včetně
  `AGENTS.md.pred-presunem-2026-10-04.md`) — je to **cesta zpět**.
- **Nepushovat bez vyžádání.** Předem ukázat `git status` a `git diff --stat`.
- **Neměnit jen jednu ze dvou kopií** (`orchestra\repo\` vs. hra) — drift test
  hlídá shodný hash.
- **Necommitovat `.secrets`, `.env` ani `_analyza\_archiv\`** do **veřejného** repa.
- **Neopravovat `install-into-repo.ps1` „mimochodem"** — je mimo provoz už dnes
  a jeho oprava je **samostatné rozhodnutí** (P1b ho jen **zdokumentuje**).

---

## 5. „Hotovo znamená" pro CELOU session (bez toho session neskončila)

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | Přesun **proběhl**, ne „začal" | Počty souborů **po** = **před** (P3), oba `.git` v pořádku (P6) |
| 2 | **Nula junction** na stará místa | `Test-Path` na obě staré cesty → **False** |
| 3 | **`grep` na `Local-Deepseek` v kódu obou rep → 0** | Spuštěno a vypsáno (kromě `_archiv`) |
| 4 | **176 souborů** má rozhodnutí `opravit`/`archivovat` | Inventura existuje, počty sedí |
| 5 | **Odvozené cesty** dohledané (P1b) | Seznam existuje; u každé je řečeno, kam odvodí **po** přesunu |
| 6 | Brány zelené **a je vidět, co změřily** | U každé **počet** zpracovaných souborů/kontrol |
| 7 | **`AGENTS.md` je v obou repech a je NAČTENÝ** | Ověřeno v **nové** session, ne odhadem |
| 8 | Odpověď na „co zůstalo otevřené" | Nová sekce v `HANDOFF.md`; `handoff-kontrola-uplnost.py` → bez újmy |
| 9 | `python _analyza\kronika-kontrola.py` → `exit 0` | Řádek v kronice je |
| 10 | V chatu je **prompt pro uživatele** i **stavový řádek** | Ke zkopírování, ne odkaz |

---

## 6. Než začneš (povinné pořadí)

1. **Ověř hlavičku:** `python _analyza\zadani-kontrola.py`. Když hlásí `exit 1`,
   **všechna tvrzení o stavu se přeměřují** — a je to **nález**, ne důvod zadání zahodit.
2. Přečti `PREDAVANI-SESSION.md` **§3, §5, §6.2** (role akční session), `AGENTS.md`,
   `HANDOFF.md` **§28**, `PLAN-SEPARACE-WORKSPACE.md` **§10.2b, §10.3b, §10.4, §10.7**.
3. Načti skilly **`dsh-prostredi`** a **`overovani`**.
4. **Ověř aspoň tři klíčová tvrzení spuštěním** (tabulka v §2) — ne čtením.
5. **P0 vyžaduje souhlas uživatele.** Bez něj nepokračuj na P1.

**Když něco nesedí:** zastav se **v tom bodě**, zapiš to jako nález a jdi dál
na body, které sedí. **Nepřepisuj zadání podle sebe.**

---

## 7. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi AKČNÍ (prováděcí) session ve workspace C:\Users\Ssevc\Local-Deepseek.

Zadání pro tebe je v NEXT-SESSION-INSTRUKCE.md — přečti ho CELÝ.
Plán přesunu je v PLAN-SEPARACE-WORKSPACE.md §10 — a POVINNĚ čti i §10.2b
(přeměřená císla) a §10.3b (ROZHODNUTÍ D1-D9, závazná); §10.1-§10.6 samotné
jsou z 19:5x a validace v nich opravila 8 tvrzení.
Záznam o validaci (co se naměřilo a co to vyvrátilo) je v §10.7.
Postup předávání je v PREDAVANI-SESSION.md, pravidla v AGENTS.md,
stav v HANDOFF.md §28 (a §2 = co je otevřené).

Než začneš cokoli dělat, proveď kontrolu zadání:
1. Ověř hlavičku: git rev-parse HEAD v obou repech proti tomu, co zadání tvrdí
   (python _analyza\zadani-kontrola.py). Když se liší, PŘEMĚŘ všechna tvrzení
   o stavu a zapiš to jako nález — zadání se nezahazuje.
2. Ověř aspoň tři klíčová tvrzení SPUŠTĚNÍM, ne čtením (tabulka v §2 zadání).
3. Když něco nesedí, zastav se v tom bodě a jdi dál na body, které sedí.

Cíl: přesunout orchestra a games\uo-shadows na E: podle plánu tak, aby žádná
cesta nezůstala tiše fungovat — a aby se po přesunu dalo měřením říct,
co rozbil přesun a co bylo rozbité už před ním.

Hlavní riziko: pracovní jednotka je 176 SOUBORŮ s pevnou cestou (ne 208
výskytů) — a existují i cesty ODVOZENÉ (Split-Path $PSScriptRoot -Parent),
které sken přímých cest nevidí. Proto je v zadání nový krok P1b.

Rozhodnutí D1-D9 UŽ PADLA (plán §10.3b) — nerozhoduj je znovu, prováděj je.
P0 (commit 2 změněných souborů v orchestra) vyžaduje můj souhlas: ukaž
git status a git diff --stat a počkej.

NEPŘESOUVEJ po částech. Nedělej junctionu na staré místo. Nepřepisuj
historické citace cest v ANALYZA-*, HANDOFF.md a KRONIKA-PROJEKTU.md.
Nepushuj bez vyžádání. Nemaž _analyza\_archiv ani _analyza\zaloha.

Na konci povinně: zapiš provedení do PLAN-SEPARACE-WORKSPACE.md (§11), novou
sekci do HANDOFF.md (nic nemazat) a řádek do KRONIKA-PROJEKTU.md; přepiš
NEXT-SESSION-INSTRUKCE.md jako zadání pro PLÁNOVACÍ (ověřovací) session
s hlavičkou podle §3; a do chatu vlož prompt pro uživatele i se STAVOVÝM
ŘÁDKEM podle §2.1.
```
