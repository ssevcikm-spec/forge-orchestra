---
name: dsh-prostredi
description: Prostředí této stanice (Windows + DSH) a jeho pasti, které vypadají jako chyba logiky, ale jsou to chyby nástroje, kódování nebo sandboxu — tiché přeskakování souborů (Select-String i grep nad skrytými složkami), rozbitá diakritika a zdvojené konce řádků v .ps1, EPERM/PermissionError ze sandboxu, cp1252 konzole, TLS z PowerShellu, Godot bez --user-data-dir. Načti, než začneš psát nebo spouštět skripty a než začneš diagnostikovat „proč to nefunguje".
whenToUse: Když píšeš nebo upravuješ .ps1/.py skript, když hledáš text v souborech (a vyšla ti nula), když ověřovací nebo testovací skript spadne (EPERM, PermissionError, UnicodeEncodeError, „Missing closing '}'"), když něco vypadá jako chyba logiky, ale logika je v pořádku, když potřebuješ na síť nebo na GitHub, nebo když spouštíš Godot hru bez editoru.
---

# Prostředí DSH na Windows — pasti, které vypadají jako chyba logiky

**Proč tenhle skill existuje:** tyhle věci se našly **čtyřikrát** v jedné
session a pokaždé stály desítky minut. Všechny mají stejný podpis: **vypadají
jako chyba v logice, ale jsou to vlastnosti nástroje, kódování nebo sandboxu.**
Diagnóza „logika je špatně" je potom slepá ulička.

**Pravidlo:** než začneš „opravovat" kód, ověř, že nástroj dělá to, co si
myslíš, že dělá. Naměřeno: **nula a prázdný výsledek nejsou úspěch.**

## 1. Tiché přeskakování souborů (falešný negativ)

| Past | Projev |
|---|---|
| `Select-String -SimpleMatch` | **tiše přeskočí soubory** → „nikde to není", přitom to bylo 2× |
| PowerShell jako takový | čte soubory jinak než grep (kódování, binárky, dlouhé řádky) |
| **`grep` tool nad rodičovskou složkou** | **tiše přeskočí SKRYTÉ složky** (`.forge`, `.github`) → „nikde to není", přitom to tam je |

**Řešení: hledej `grep` toolem, ne PowerShellem.** Na hledání textu v souborech
nikdy nepoužívej `Select-String` — u falešného negativu nemáš jak poznat, že
selhal.

**ALE pozor: ani `grep` tool není vševědoucí.** Naměřeno 1. 10. 2026 —
když hledáš z **rodičovského** adresáře, skryté složky **přeskočí**:

| hledání | výsledek |
|---|---|
| `grep "FORGE_CMD"` nad `orchestra/` | **0 nálezů** |
| `grep "FORGE_CMD"` nad `orchestra/repo/` | **0 nálezů** |
| `grep "FORGE_CMD"` nad `orchestra/repo/.forge/` | **5 nálezů** |
| `Test-Path orchestra/repo/.forge/node/worker.mjs` | **True** |

Totéž pro `.github` (`grep "actions/checkout"` nad `orchestra/repo/` → 0;
nad `orchestra/repo/.github/` → 5). **Důsledek:** celá orchestra bydlí
v `.forge/` a `.github/`, takže **nejdůležitější soubory projektu jsou pro
hledání z rodiče neviditelné** — a vypadá to jako „ta funkce nikde není".

**Pravidlo: hledej nad KONKRÉTNÍ složkou (i skrytou), nebo soubor přečti celý.**
Když ti vyjde nula a máš podezření, že by tam něco být mělo, **změň cílovou
složku**, ne hledaný výraz — a ověř existenci souboru `Test-Path`.

**Naměřeno 1. 10. 2026 — jak velký ten falešný negativ umí být: 80 ku 0.**

| hledání | výsledek |
|---|---|
| `grep` tool nad `orchestra/` (vzor `C:[\\/]Users[\\/]…`) | **0 nálezů** absol. cest |
| Python walk téhož stromu, stejný vzor | **80 výskytů v 59 souborech** |

**Rozdíl mezi „nikde to není" a „je to v 59 souborech".** Kdyby se podle grepu
plánoval přesun projektu, plán by tvrdil, že se nic neopraví.

**Pravidlo pro plošné skeny:** na „kolik výskytů je v CELÉM stromě" použij
**Python walk**, ne `grep` tool ani `Select-String`. Hotový vzor je
`_analyza\sken-vazeb.py` (chová se ke skrytým složkám stejně jako k ostatním).

**A druhá polovina téže pasti: statická kontrola musí číst KÓD, ne KOMENTÁŘE.**
Naměřeno 1. 10. 2026: test hledal v `index.ts` řetězec `locked.add(lockKeys(...))`
— a **našel ho v komentáři, který vadu popisuje**. Test tedy prošel i s vrácenou
vadou (odhalil to až **mutační test**). Pravidlo: **před hledáním vzorců odstraň
komentáře** (`//`, `/* */`) a teprve pak hledej. Když kontrola čte komentáře,
**komentář popisující vadu vypadá jako vada** a oprava se nedá dokázat.
Vzor: `orchestra\tools\test-zamek-owns.py` (`bez_komentaru()`).

**A třetí věc, která patří k témuž: test bez `assert` a bez `sys.exit` není
test.** Naměřeno 1. 10. 2026: `orchestra\tools\test-cooldown.py` vypsal
`CHYBA` u jednoho scénáře a **skončil `exit 0`** — „zelený" v CI i na pohled.
**Každý test musí mít assert i nenulový exit kód** — a ideálně **mutační test**
(vrať vadu a podívej se, že opravdu spadne).

## 2. Skripty padají na VLASTNÍM výstupu (cp1252)

Konzole je `cp1252`, ale skripty tisknou česky (`řádků`, `chyb`):

```
UnicodeEncodeError: 'charmap' codec can't encode character ...
```

Vypadá to jako vada skriptu — je to vada konzole. **Řešení bez zásahu do
skriptu:**

```powershell
$env:PYTHONIOENCODING='utf-8'
python orchestra\tools\over-skilly.py
```

Do skriptu, který má běžet i jinde, patří i ošetření:

```python
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
```

## 3. `.ps1` soubory: BOM a konce řádků

Dvě chyby, které parser ohlásí jako chybu logiky:

| Problém | Projev | Oprava |
|---|---|---|
| Chybí **UTF-8 BOM** | PowerShell čte soubor jako cp1252, české znaky se rozbijí, parser hlásí `Missing closing '}'` nebo `Unexpected token` s popleteným jménem | BOM na začátek |
| **Zdvojené konce řádků** (dvoje `\r`) | soubor má 2× víc řádků; parser hlásí chybu na řádku, který **v souboru není** (naměřeno: 167 v souboru o 110 řádcích); prázdné řádky navíc **přeruší pokračování backtickem** | sjednotit na CRLF |

**Proč to vzniká:** Python `write_text()` bez `newline=''` přeloží `\n` na
`\r\n`, takže v textu, který už `\r\n` měl, zůstane **dvoje `\r`**.
→ **Zapisuj bajty** (`write_bytes`), ne text.

**Nástroj na opravu:** `python orchestra\tools\oprav-ps1-kodovani.py`
(UTF-8 BOM + jednotné CRLF, ověřeno parserem).

**Po KAŽDÉ editaci `.ps1` ověř parser:**

```powershell
[void][System.Management.Automation.Language.Parser]::ParseFile($f,[ref]$null,[ref]$err)
# prázdné $err = syntakticky v pořádku
```

## 3b. Junctiony: `Target` a `LinkType` LHOU, cestu ověřuj `realpathSync`

**Naměřeno 1. 10. 2026.** PowerShell u junctionů na této stanici podává **tři
různé druhy nepravdivých informací** — a každá vypadá jako jasný důkaz:

| Co PowerShell řekne | Příklad ze měření | Pravda |
|---|---|---|
| `Target` na **neexistující** cestu | `~\.dsh\skills` → `C:\DSH\data\skills` | obsah se čte normálně; `Test-Path C:\DSH` = **False** |
| `LinkType` **prázdný** (tváří se jako obyčejná složka) | `~\.dsh\sessions`, `~\.dsh\profiles` | jsou to junctiony |
| `LinkType` **vyplněný** | `...\node_modules\@local\dsh-tarif-indikator` → správná cesta | správně |

**Důsledek, který má zuby:** dva zdánlivě různé adresáře jsou **tentýž**.
`C:\Users\Ssevc\.dsh\sessions` a `E:\DSH\data\sessions` vypadají jako dvě cesty
a mají shodný obsah — **jsou to tytéž soubory**. Skript, který prochází oba
rooty bez deduplikace, počítá **každou session dvakrát**.

**Řešení — nevěř `Target` ani `LinkType`, sáhni po realpath:**

```js
import { realpathSync } from 'node:fs'
realpathSync('C:\\Users\\Ssevc\\.dsh\\sessions')  // → 'E:\\DSH\\data\\sessions'
```

Deduplikuj **podle `realpath`**, ne podle zapsané cesty (tak to dělá
`~\.dsh\skills\dsh-usage\report.mjs`). Když dva rooty dají po `realpath`
shodný řetězec, projdi jen jeden.

**A pozor na opačný omyl:** „cesta v `Target` neexistuje" **není** důkaz, že je
junction visutá. Visutou poznáš jen tím, že se cesta nedá přečíst
(`Get-ChildItem` vyhodí `ItemNotFoundException`) — ne z `Target`.

**Pravidlo:** na otázku „je to tentýž adresář?" volej `realpathSync`. Výpis
vlastností je na téhle stanici nespolehlivý v **obou** směrech.

### Ověřování junction: `stat` je SLEDUJE, `lstat` ne

**Naměřeno 1. 10. 2026** (migrace datového adresáře). `existsSync()` v Node
i `statSync()` junctiony **sledují** — takže v `attachments`, kde je smyčka
(`file-objects` ↔ `files`), vrátí **`ELOOP`** a **funkční junctiona vypadá
jako rozbitá**. PowerShell `Test-Path -LiteralPath` se chová správně.

| Chceš zjistit | Použij |
|---|---|
| existuje **cíl** junctiony | `lstatSync(cil)` — nesleduje link |
| kam junctiona míří | `readlinkSync(link)` |
| je soubor **dostupný přes** junctionu | `statSync` — ale u smyčky spadne na `ELOOP` |

**A ještě jedna past téhož druhu:** junctiona na **SOUBOR** se nedá ověřit
přes `Test-Path "$link\soubor"` — vrací `False` i u funkční junctiony (Windows
se pod junctionou na soubor neprochází jako pod adresářem). Ověřuj
`Test-Path $link` **a shodu `Target`**.

**Pravidlo:** než označíš junctionu za rozbitou, ověř **čím** jsi to měřil.
Sledování smyčky i neschůdnost junctiony na soubor vypadají obě jako „cíl
neexistuje" — a obě jsou to vlastnosti nástroje, ne stavu.

**A při migraci se junctiony musí PŘEBASOVAT** na nové umístění. Když je
necháš mířit do zdroje, vypadají zdravě, dokud zdroj existuje — a zhasnou
teprve ve chvíli, kdy ho přesuneš. Ověřuj to **po** přesunu, ne před ním.

### ⚠ `Target` u HARDLINKU vrací CESTU SOUBORU SAMOTNÉHO

**Tohle je past, která stojí data** — naměřeno 1. 10. 2026: **14 souborů
přepsáno junctionami**. `Target` / `readlinkSync` má **různý význam podle
typu objektu**:

| Objekt | Co `Target` vrátí |
|---|---|
| junctiona | **cíl vazby** („kam vede") |
| **hardlink** | **cestu souboru samotného** — hardlink žádný cíl nemá |
| obyčejný soubor | prázdno nebo vlastní cestu |

Kód, který se ptá „kam vede tento cíl?", dostane u hardlinku **cestu k sobě**.
Když podle ní objekt přepíše (`mklink /J`), **zničí skutečný soubor** a vznikne
smyčka. Přesně tak zmizelo 14 souborů v `attachments` — naštěstí byly
v karanténě, takže se daly vrátit a ověřit hash.

**Pravidlo:** před **zápisem** ověř dvěma nezávislými způsoby, co objekt je —
a přepisuj jen to, co je **skutečná junctiona na adresář** (cíl existuje,
není totožný s odkazem a je to adresář). Cokoli jiného přeskoč.

**A obecněji:** *„oprava" je taky zásah do dat.* Jeden zdroj pravdy stačí
na čtení; na mazání a přepisování nestačí. Širší pravidlo o měření, které
odpovídá na jinou otázku, je ve skillu `overovani` §1.1.

## 3c. Dvě pasti nástrojů, které vypadají jako chyba kódu

**a) `skill` v presetu `cordis` nic nenačte — a není to vada instalace.**
Naměřeno 1. 10. 2026: `skill("dsh-usage")` i `skill("<nově nainstalovaný>")`
vrací `unknown or no longer available`, protože `@deepseek-ai/dsh-skill-filesystem`
je v tom presetu `inactive`. **Ověř to na skillu, který na disku leží od dřív** —
když selže i ten, chyba je v presetu, ne v instalaci. Existenci a formát skillu
ověř jinak (`over-skilly.py`, SHA-256 proti zdroji).

**b) Vnořený JS v argumentu `pwsh` rozbije PowerShell parser.**
`node -e "... [regex] ..."` skončí na `Missing type name after '['` — PowerShell
si argument parsuje sám. **Piš skript do souboru** (`_analyza\*.mjs`) a volej
`node soubor.mjs`. Ušetří to i quoting pro `$()`, `@{}` a `\"`.

## 4. Sandbox: EPERM a PermissionError, které vypadají jako vada nástroje

V režimu `workspace-write` (na Windows) platí, že **programy nemohou otevřít
pojmenované roury**. Důsledek: nástroj, který spouští podproces s **piped
stdio**, spadne:

```
EPERM: spawn ...
```

Stejně tak padá zápis do **přesměrovaného tempu** sandboxu:

```
PermissionError: [WinError 5] Access is denied:
  C:\Users\...\AppData\Local\Temp\dsh-XXXX\...\.forge
```

**Horší varianta téhož: nástroj do tempu zapíše a NIC NEŘEKNE.** Naměřeno
1. 10. 2026: Godot `--write-movie "$env:TEMP\snimky\frame.png"` doběhl
s úspěchem, ale **žádné soubory nevznikly** — po přesměrování výstupu do
workspace fungoval bez další změny. **Pravidlo: výstup nástrojů posílej do
workspace, i když „jen ukládají do souboru" — a když tvrdí, že zapsaly, ověř,
že soubor existuje.** Dočasnou složku pak ukliď.

**Naměřeno 1. 10. 2026:** `orchestra\repo\.forge\baseline.py testy` a
`repo\.forge\node\vision.test.mjs` padaly v sandboxu, ale se širším oprávněním
projdou (24/24 a 34/34). Chyba byla v **prostředí**, ne v testech.

**Co dělat:**

1. Rozliš to od vady nástroje — spusť to samé s plným přístupem; projde-li to,
   je to sandbox.
2. Jinak nasměruj temp do workspace: `$env:TMP = "$PWD\.tmp"`.
3. **Nezapisuj „testy projdou" do dokumentace, dokud víš, že projdou jen
   s rozšířeným oprávněním** — jinak příští běh vypadá jako regrese.

## 5. Síť a GitHub

| Past | Řešení |
|---|---|
| **TLS z PowerShellu nefunguje** (schannel) | na síť jdi **Node `fetch`**, ne `Invoke-RestMethod` ani `curl.exe` |
| Git přes schannel padá (`SEC_E_NO_CREDENTIALS`) | volej `orchestra\tools\git.cmd` (OpenSSL backend) |
| Push s PAT | `git -c http.extraHeader="AUTHORIZATION: basic <b64>"` — **PAT čti ze souboru** (`orchestra\.secrets\github_pat.txt`), nikdy ho nepiš do historie příkazů ani do výpisu |

**Zdroj pravdy o repech a Pages:** `node orchestra\tools\zjisti-pages.mjs`
(GitHub API). Ptej se jeho, ne paměti ani dokumentace.

## 6. Godot hra bez editoru

Godot **není v PATH** a bez `--user-data-dir` padá na `Could not open 'user://'`.

```powershell
$godot = 'orchestra\tools\godot\Godot_v4.7.2-stable_win64_console.exe'

# testy
& $godot --headless --path games\uo-shadows --script res://tests/run_tests.gd

# snímek hry (pak se na něj PODÍVEJ přes read_image)
& $godot --path games\uo-shadows --user-data-dir "$env:TEMP\uo-shadows-hrani" `
         --rendering-driver opengl3 --resolution 960x540 `
         --write-movie <out>\frame.png --quit-after 5
```

Ve složce hry je launcher `hra.cmd`, který to má vyřešené.

**Pozor:** `--headless` testy mohou vypsat `[test] N kontrol, 0 selhání`
a **přesto** skončit nenulovým kódem s GDScript backtrace na stderr (úklidové
volání). Čti **výsledek testů**, ne jen exit kód — a naopak: samotný výstup
testů bez exit kódu taky nestačí.

## 7. Dokumentace, která popírá vlastní nástroje

Když do dokumentace zapíšeš **ukázku rozbitého kódování** (např. české slovo
přečtené jako UTF-8 a vypsané ve Windows-1250), kontrola diakritiky to nahlásí
jako vadu **dokumentu** — protože hledá právě tyhle sekvence. Popisuj je
**slovem**, ne doslovnými znaky. (Tenhle skill to tak má schválně; první verze
na tom spadla.)

**Obecné pravidlo:** schopnost se **ověřuje měřením**, nikdy se nepřebírá
z dokumentace. Zastaralý text není neutrální — aktivně brání správnému postupu.
Když někdo tvrdí „agent tohle neumí", je první krok to zkusit
(viz `MOZNOSTI-AGENTA.md`).

**Táž past u oprávnění — a dražší, protože jde o bezpečnost.** Ověřeno
1. 10. 2026 z oficiálních zdrojů: **DSH nemá model oprávnění pro pluginy.**
Manifest pluginu oprávnění deklarovat **neumí** (zná jen `dsh.bundle.patch`)
a nic je nevynucuje. **Sandbox je „filesystem effects only" a platí na tool
cally, ne na JS pluginů** — plugin běží v procesu a smí `node:fs`
i `node:child_process` přímo. `SAFETY.md` to přiznává sám a diskuze
„How should plugins disclose and manage permissions?" je **otevřená otázka**,
ne funkce.

**Praktický důsledek:** otázka u cizího pluginu není „jak mu omezím práva",
ale **„důvěřuji zdroji, nebo ho neinstaluju"**. Co reálně jde: přečíst
`package.json` (řekne o schopnostech **nic**), `cordis.patch.yml`, `inject`
seznam hostové části a grepnout `node:fs|node:child_process|process.env|fetch|
webServer.register|ctx.loader`. Dál **pinovat commit** (`github:…/plugin#<sha>`)
a zkoušet v **samostatném profilu** (izoluje závislosti, není to runtime sandbox).
A pozor: **„Usage & Billing" registr je neoficiální** — jeho odznak znamená jen,
že CI plugin nainstaloval a nastartoval, ne že auditoval, co umí.

**A ještě jedna oprava téhož druhu:** `plugin_manager` **není** jen v Creator
módu. Naměřeno 1. 10. 2026 — `install_bundle` i `cordis_inspect_query`
fungovaly v běžné session. Co je potřeba, je **schválení** (`danger-full-access`),
ne jiný preset.

## Kontrolní seznam při podivné chybě

1. **Hledám to grep toolem?** (ne `Select-String`)
2. **Je to kódování?** (`$env:PYTHONIOENCODING='utf-8'`, BOM, CRLF)
3. **Je to sandbox?** (EPERM, `PermissionError` na tempu → zkus s plným přístupem)
4. **Proběhla kontrola vůbec?** (nula a prázdno nejsou úspěch)
5. **Není to jen falešný poplach po opravě?** (statická kontrola musí číst
   kód, ne komentáře)
