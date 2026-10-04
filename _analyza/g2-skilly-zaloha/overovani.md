---
name: overovani
description: Jak ověřit, že brána (test, kontrola, validátor) SKUTEČNĚ měří — místo aby jen nevypadala rozbitá. A jak poznat měření, které odpovídá na JINOU otázku (jedna vlastnost s víc významy, falešný poplach i falešné „v pořádku"). Obsahuje spustitelný sabotér, nástroj na výrobu vady, checklist pro psaní brány a katalog typů bran. Použij, když píšeš nebo opravuješ test/bránu/kontrolu, když chceš vědět, jestli zelený výsledek něco znamená, nebo než podle měření PŘEPÍŠEŠ data.
whenToUse: Když píšeš nový test, bránu nebo validátor; když tvrdíš „testy prošly" a potřebuješ to doložit; když brána hlásí zelenou a máš podezření, že neměří; když někdo řekne „ověřeno" nebo „hotovo" u něčeho, co se měří; když upravuješ existující bránu a nechceš ji rozbít na slepou; a před každou destruktivní operací řízenou měřením (mazání, přepis, migrace), protože tam jeden zdroj pravdy nestačí. Use when writing or verifying a gate/test, and before any destructive operation driven by a measurement.
---

# Ověřování bran — jak poznat, že zelená něco znamená

**Proč tenhle skill existuje.** Systém, kde brána tiše přestane měřit, je
**horší než systém bez brány** — bez brány člověk ví, že nic neví; se slepou
bránou si myslí, že ví. Naměřeno opakovaně:

| Co se stalo | Jak se to poznalo |
|---|---|
| `check-schema.py` hledal `var cell := 16`, kód měl `const CELL_W_DEFAULT := 96` → regexy nenašly nic, cyklus proběhl nad prázdným seznamem, **zelená** | až ruční pohled na řádek `výchozí cell=[], fallback=[]` |
| `test-cooldown.py` vypsal `CHYBA` a **skončil `exit 0`** (neměl `assert`) | spuštěním a porovnáním exit kódu |
| nový test hledal řetězec v celém souboru a našel ho **v komentáři, který vadu popisuje** → prošel i s vrácenou vadou | **mutačním testem** |
| `check-wiring.py` na projektu bez `.gd` souborů hlásí „Vše v pořádku" nad **nulou** souborů | čtením kódu brány |

**Jedno pravidlo nad vším:** *„prošlo to" bez odpovědi na „umí to spadnout?"
neznamená nic.*

---

## 1. Dvě otázky, které se musíš naučit ptát

| Špatná otázka | Správná otázka |
|---|---|
| „Neprotestovala brána?" | **„Proběhla brána a kolik toho změřila?"** |
| „Prošel test?" | **„Umí ten test spadnout?"** |
| „Co mi to měření řeklo?" | **„Je ta veličina vůbec schopná odpovědět na moji otázku?"** |

První je o **pokrytí** (měřila brána vůbec něco?), druhá o **síle**
(chytila by vadu?), třetí o **platnosti** (měří to, na co se ptám?).
Jsou to různé vady a každá potřebuje jiný nástroj.

### 1.1 Třetí past: jedna vlastnost, dva významy

**Naměřeno 1. 10. 2026** — stojí to za samostatnou sekci, protože mě to
přivedlo k **přepsání 14 souborů**. Šlo o `Target` (PowerShell) neboli
`readlinkSync` (Node):

| Na čem se ptám | Co to vrátí | Co z toho plyne |
|---|---|---|
| junctiona | **cíl vazby** | „kam vede" — správný význam |
| hardlink | **cestu souboru samotného** | „kam vede" je **nesmysl** — hardlink žádný cíl nemá |
| obyčejný soubor | prázdno / cestu | zase něco jiného |

**Všechno to vypadá jako odpověď.** Kód, který se ptá „kam vede tento cíl?",
dostane u hardlinku **cestu k sobě** — a když podle ní přepíše soubor,
**zničí data**. Přesně to se stalo: `mklink /J` zapsal junctionu na místo
skutečného souboru a obsah zůstal jen v karanténě.

**Pravidlo: než použiješ výsledek měření k ZÁPISU, ověř, že ta veličina
na tvou otázku vůbec umí odpovědět.** U souborových systémů to znamená
rozlišit `lstat` (nesleduje odkaz) od `stat` (sleduje) a junctionu od
hardlinku — a nespoléhat na jednu vlastnost, která má víc významů.

**A odvozené pravidlo pro destruktivní operace:** *„oprava" je taky zásah
do dat.* Než přepíšeš cokoli, co může být skutečný soubor, ověř **dvěma
nezávislými způsoby**, co to je. Jeden zdroj pravdy stačí na čtení, na
mazání a přepisování nestačí.

### 1.2 Když měření lže oběma směry

Tatáž veličina může dát **falešně pozitivní i falešně negativní** výsledek —
a to je nejhorší kombinace, protože se nedá jednostranně kalibrovat:

| Veličina | Falešný poplach | Falešné „v pořádku" |
|---|---|---|
| `Test-Path "$link\soubor"` u junctiony **na soubor** | `False` i když vazba funguje | — |
| `existsSync()` u **smyčky** junctionů | — | — (vrací `ELOOP`, tedy chybu) |
| `Target` u **hardlinku** | — | cesta vypadá jako platný cíl, ale je to soubor sám |

**Důsledek:** „ověřeno měřením" není totéž jako „ověřeno". U netriviálního
měření si nejdřív ujasni, **jak by vypadal správný a jak chybný výsledek** —
a když oba vypadají stejně, měření nic neříká.

---

## 2. Nástroje (spustitelné, v tomto skillu)

### 2.1 `sabotuj.mjs` — ověří, že brána umí spadnout

Udělá tři běhy a porovná je: brána na **zdravém** kódu musí projít, po
**vložení vady** musí spadnout, pak se stav vrátí.

```powershell
# 1) záloha souboru, který budeš sabotovat (NE `git checkout` — viz past níž)
Copy-Item cesta\k\souboru.ts $env:TEMP\zaloha.ts -Force

# 2) vada do JSON (jediná cesta, jak přežít uvozovky a závorky)
'{ "najdi": "<přesný text>", "nahrad": "<vada>", "pocet": 1 }' |
  Set-Content -Encoding UTF8 vada.json

# 3) spusť
node "$env:USERPROFILE\.dsh\skills\overovani\sabotuj.mjs" `
  --popis  "co brána hlídá" `
  --soubor "cesta/k/souboru.ts" `
  --sabotaz "python `"$env:USERPROFILE\.dsh\skills\overovani\zmen.py`" cesta/k/souboru.ts --json vada.json --tise" `
  --uklid  "node -e `"require('fs').copyFileSync(process.env.TEMP+'/zaloha.ts','cesta/k/souboru.ts')`"" `
  --brana  "<příkaz, který bránu spustí>"
```

Výstup: `VÝSLEDEK: brána PROŠLA na zdravém kódu a SPADLA na vrácené vadě → měří.`
(exit 0) — nebo rozlišená diagnóza, co je špatně.

**Sabotér rozlišuje tři různé vady** (a to je jeho hlavní hodnota):
1. brána neprojde ani na zdravém kódu → **sprav bránu**;
2. sabotáž se neuloží → **sprav sabotáž** (výsledek kroku 3 pak nic neznamená);
3. brána projde i s vadou → **brána je slepá**.

Bez toho rozlišení se „brána prošla" snadno splete s „vada se neuložila".

> ⚠️ **Past s `--uklid`:** `git checkout -- <soubor>` vrátí soubor do **commitu**,
> ne do stavu před sabotáží. Když jsou v souboru **necommitnuté změny, smaže
> je.** Naměřeno 1. 10. 2026: takhle jsem ztratil hotovou opravu conductora
> (našel se až tím, že soubor zmizel z `git status`). **Zálohuj kopií souboru,
> ne prevencí gitu — a před sabotáží commitni.**

### 2.2 `zmen.py` — výroba vady (a cesta zpět)

```powershell
# přes JSON (doporučeno — uvozovky a závorky přežijí)
python zmen.py <soubor> --json vada.json

# nebo přímo (jen pro jednoduché texty bez uvozovek)
python zmen.py <soubor> --najdi "<text>" --nahrad "<text>"
```

Je **doslovný** (žádné regexy — ty by tiše trefily víc míst, než jsi chtěl),
**ověří počet výskytů** a když text nenajde, **skončí nenulově místo tichého
nic**. Konce řádků zachová (binární režim), a JSON čte jako `utf-8-sig`, protože
PowerShell píše UTF-8 **s BOM**.

### 2.3 Kontrola pokrytí — „kolik toho brána změřila"

Tohle se nedá zobecnit do nástroje, protože záleží na bráně. **Princip:**
brána má vypsat **strojově čitelný počet** toho, co změřila.

```
ZMERENO: soubory=57 funkce=57 pouzite=57
ZMERENO: sprity=16 animace=0        <- nula je VIDĚT (a je to nález, ne ticho)
```

Nadřazený validátor (`validate-all.mjs`, CI) pak **padne, když některá brána
řádek nevykáže** — protože to znamená, že se nespustila nebo přestala měřit.
**Prázdný seznam, který se tiše proiteruje, je nejhorší varianta: vypadá jako
naměřená nula.**

---

## 3. Checklist při psaní brány

1. **Má `assert` a nenulový exit kód?** Bez toho je „zelená" jen text na
   obrazovce. (`print` + `return` nestačí — ověřeno.)
2. **Čte KÓD, ne komentáře?** Před hledáním vzorců odstraň `//`, `/* */`.
   Jinak **komentář popisující vadu vypadá jako vada** a oprava se nedá
   dokázat. A naopak: hledáš-li v celém souboru, najdeš i text v komentáři,
   který vadu popisuje → brána projde i s vracenou vadou.
3. **Rozlišuje „nejsou data" od „naměřena nula"?** Když soubor chybí nebo
   regex nic nenašel, patří to jako **vada nebo pojmenovaná poznámka** — nikdy
   jako ticho a nikdy jako úspěch.
4. **Je známý i chybný případ?** Offline test brány musí mít **fixturu, kde
   musí hlásit vadu**, a fixturu, kde nesmí. „Prošlo to" bez toho neznamená nic.
5. **Nehlásí falešný poplach na legitimní stav?** U inkrementálního vývoje je
   funkce často „API pro příští úlohu" — to má být **poznámka**, ne vada.
6. **Pojmenuje mrtvou větev?** Když soubor zmizí, větve, které na něj sahají,
   se už nikdy nespustí. Brána to má říct, ne mlčet.
7. **Je ověřená sabotérem?** (viz §2.1) — jinak nevíš, že umí spadnout.

---

## 4. Katalog čtyř typů bran

Různé brány selhávají různě. Tohle je mapa, co u které hledat:

| Typ | Co dělá | Jak tiše selže | Jak to ověřit |
|---|---|---|---|
| **Měření** | počítá veličinu (velikost, počet, IoU) | měří **prázdný** vstup → vrací 0/`[]` | spustit na vstupu, kde **musí** něco naměřit, a zkontrolovat, že číslo není 0 |
| **Statická kontrola** | hledá vzorce v kódu | vzorec se změní (refaktor) → nenađe nic | fixtura se **známým** správným i chybným kódem |
| **Kontraktní** | porovnává **dvě kopie** téhož | kopie se rozejdou a každá se testuje zvlášť | testovat **shodu** (hash/obsah), ne každou zvlášť |
| **Tvrdá (blokující)** | zastaví tok při nálezu | nenulový výsledek s **exit 0** | porovnat **exit kód**, ne výstup na obrazovce |

**Kontraktní brána je nejcennější vzor** tam, kde existují dvě implementace
téhož (šablona a projekt, dvě kopie skriptu): netestuj každou zvlášť, testuj
**shodu mezi nimi**. Jinak ti rozejití unikne, i když obě „projdou".

---

## 5. Anti-vzory (každý naměřený)

| Anti-vzor | Proč to je vada |
|---|---|
| `print("CHYBA")` bez `sys.exit(1)` | brána hlásí vadu a **skončí úspěchem**; v CI zelená |
| hledat vzorec v **celém** souboru včetně komentářů | komentář popisující vadu bránu uspokojí |
| `for x in nalezené:` nad prázdným seznamem | „prošlo" znamená „nebylo co kontrolovat" |
| brána, která **nespadne** při nenalezení vstupu | přestane měřit a tváří se spokojeně |
| `exit 0` na konci funkce `main()` bez ohledu na výsledek | nenulový výsledek s nulovým exit kódem je **sám nález** |
| kontrolovat jen výstup, ne exit kód | výstup se čte očima, exit kód čte automat |
| brána, jejíž závislost (knihovna) se v CI nenainstaluje | spadne **vždy**, a vypadá to jako vada měřeného projektu (naměřeno: `PIL`) |
| **opravovat podle JEDNÉ vlastnosti**, která má víc významů | `Target` u hardlinku vrátí cestu souboru → „oprava" **přepíše data** (naměřeno: 14 souborů) |
| **operace pokračuje po částečném selhání** | obnovila 1 z 15 vazeb, zbytek vypsala jako chybu a jela dál — pak ohlásila „HOTOVO" |

---

## 6. Jak to zapadá do zbytku

- **`game-developer`** — metodika granulí a bran ve vývoji hry; tenhle skill
  je o tom, **jak bránu ověřit**, ne jak ji navrhnout.
- **`dsh-prostredi`** — pasti prostředí, které bránu rozbijí (kódování,
  sandbox, tiché přeskakování souborů).
- **`orchestra`** — konkrétní brány orchestra a jejich naměřená slepá místa.

**Poslední pravidlo:** když brána projde, ale ty neumíš říct, co změřila,
**nemáš zelenou — máš jen ticho.** A ticho se od zelené nedá rozeznat.

---

## 7. Sedm pastí naměřených 1. 10. 2026 (u hloubkové analýzy orchestra)

*(Všechny se staly jedné session a mají stejný podpis: **nástroj řekl něco
jiného, než co se stalo**.)*

### 7.1 `git show` v PowerShellu zapíše UTF-16LE a změní první bajty

```powershell
git show HEAD:soubor.gd > out.txt     # PowerShell přepíše výstup na UTF-16LE
```

Když pak v `out.txt` hledáš BOM, dostaneš **jiný výsledek než ve skutečném
blobu** — a „BOM se nezměnil" je falešný závěr. Naměřeno: blob v `HEAD`
začínal `EF BB BF`, přes PowerShell vypsaný soubor `FF FE`.
**Řešení:** čti výstup gitu **v Pythonu s `shell=True`** (git.cmd je batch,
bez shellu se nespustí) a vyhodnocuj **bajty**, ne text.

### 7.2 Zápis textu zahodí BOM a přepíše LF na CRLF

U souborů, které projekt drží na `text eol=lf` (`.py`, `.mjs`, `.gd`), tím
vznikne **pracovní strom jiný než zbytek repa** — a příští session to čte jako
„necommitnutou změnu", která neexistuje. Naměřeno: čtyři soubory, u jednoho
zmizel BOM, u tří se LF změnilo na CRLF.
**Ověřuj dvěma nezávislými pohledy** (blob v `HEAD`, index, disk) a opravuj
**zápisem bajtů** (`write_bytes`), ne textu.

### 7.3 Nástroj, který „jen přidá řádky", umí rozvrátit soubor

Skript vkládající pole do JSONu hledal „konec objektu" jako první řádek `}` —
a **přepsal soubor na 211 řádků místo 195** (neplatné JSON). Všimlo se to jen
proto, že po zápisu **znovu parsoval**.
**Pravidla:** (1) před zápisem **záloha kopií** (ne spoléhání na git),
(2) po každé dílčí změně **znovu parsuj** a při chybě **nezapisuj**,
(3) vkládej na **jednoznačné místo**, ne „na konec objektu",
(4) po zápisu zkontroluj i **obsah** (počty, očekávané hodnoty).

### 7.4 Dva endpointy, stejné jméno pole, různá odpověď

`GET /pulls?state=closed` vrátí u sloučeného PR `merged_by: null`;
`GET /pulls/<n>` vrátí `merged_by: ssevcikm-spec`. Kdo měří seznamem, udělá
závěr „sloučil to robot"; kdo detailem, vidí člověka.
**Pravidlo:** u pole, které rozhoduje o závěru, si ověř **endpoint** — a když
se dva zdroje rozcházejí, hledej, **čím se liší**, ne který „je správný".

### 7.5 Ukázka rozbitého kódování v dokumentu = falešný poplach brány

Dokument, který kontroluje diakritika, **nesmí obsahovat doslovné znaky
rozbitého kódování** — ani jako příklad. Naměřeno: kapitola, která je
vyjmenovávala, **shodila sama sebe**.
**Piš to slovy** („tři znaky, které vzniknou dvojím kódováním UTF-8 přes
Windows-1250") a seznam si **načti z brány**, neopisuj.

### 7.6 Brána, která kontroluje SEZNAM, ne strom

`kontrola-diakritiky.py` má **pevný seznam 22 souborů**. Nový dokument v něm
není → **brána projde zeleně nad dokumentem, který nikdy neotevřela**.
A ironie: **komentář v té bráně tuhle past přesně popisuje** — znalost tam je,
mechanismus ne.
**Pravidlo:** po vytvoření souboru, který má brána kontrolovat, se **nejdřív
zeptej, jestli ho vůbec vidí.** Když ne, ověř ho ručně **týmž vzorem**
a napiš to.

### 7.7 Dvě měření v různých časech = dvě pravdy (a obě správné)

Soubor se mezi měřeními změnil (jiná session) → totéž tvrzení mělo dvě čísla
(5× vs. 0×). **Není to chyba měření, je to chyba zápisu bez času.**
**Ke každému tvrzení o STAVU patří čas** — a k dokumentu odstavec „co se
v průběhu měnilo".

### 7.8 Test, který je červený, protože našel vadu — to je úspěch

Po opravě brány může být **správně červená**: nový test změřil skutečnou vadu
produkčního kódu. Kdo ji „uklidí" vypnutím testu, **vrátí ticho**.
**Pravidlo:** rozlišuj „test je rozbitý" od „test našel vadu". První se opravuje,
druhé se **nechá červené a pojmenuje se, co ji opraví** (u orchestra: krok B1).

### 7.9 MUTACE, KTERÁ SE TICHE NEPROVEDE, VYPADÁ JAKO ÚSPĚCH

**Naměřeno 2. 10. 2026 (druhé kolo analýzy).** Napsal jsem kontrolu
`_analyza\hl2-kontrola.py`, která ověřuje 9 bodů „Hotovo znamená" ze zadání.
Abych dokázal, že **umí spadnout**, udělal jsem mutaci — v PowerShellu:

```powershell
$zmut = $orig -replace '### S36 —[^\n]*', '### (smazano mutaci)'
```

Test **prošel** (exit 0). Vypadalo to jako „kontrola je slepá". **Nebyla.**
Vzor obsahoval **em-dash `—`**, ten se cestou konzolí (cp1252) rozpadl, takže
`-replace` **nenahradil nic** — a kontrola samozřejmě prošla, protože dokument
zůstal neporušený.

| co jsem dělal | co se stalo | jak to vypadalo |
|---|---|---|
| mutace v PowerShellu `-replace` s českou pomlčkou | **neprovedla se** | „kontrola je slepá" |
| táž mutace v Pythonu (`read_text`/`write_text`, `utf-8`) | provedla se | správně `exit 1` |

**Pravidlo:** **mutuj tam, kde umíš zaručit kódování** — soubor načti i zapiš
s `encoding='utf-8'`, ne přes shellovou pipeline. A **vždy ověř, že mutace
skutečně proběhla** (např. `assert 'S36' not in zmutovany_text`), jinak
testuješ nezměněný soubor a „zelená" nic neznamená.

**Zobecnění (platí i mimo PowerShell):** každý krok, který „něco nahradí nebo
smaže", se musí **ověřit na výstupu** — ne na vstupu. Je to táž past jako
„brána, která nemá jak selhat", jen o vrstvu výš: **mutační test, který se
neprovede, tvrdí totéž co mutační test, který projde.**

### 7.10 Brána je zelená nad dokumentem, který NIKDY neotevřela

**Naměřeno 2. 10. 2026.** `kontrola-diakritiky.py` má **pevný seznam** cest.
Napsal jsem dva nové dokumenty (`ANALYZA-HLOUBKOVA-ORCHESTRA-2.md`,
`_analyza\HLOUBKOVA-MERENI-3.md`) a brána hlásila **„VŠE OK, exit 0"** —
**ani jeden z nich neměla v seznamu** (naměřeno: `grep` na
`ANALYZA-HLOUBKOVA` v bráně našel jen předchozí dokument a zadání).

**Pravidlo:** po vytvoření **nového** souboru, který má brána kontrolovat,
**ověř, že ho brána vidí** (`grep` na jeho název ve zdroji brány, nebo
`--vypis`). Jinak je zelená od brány, která soubor nikdy neotevřela — a je to
**horší než červená**, protože vypadá jako hotovo. (Tatáž past jako S27 z 1. kola;
tady se potvrdila na vlastním výstupu.)

### 7.11 KONTROLA, KTERÁ HLEDÁ „PRVNÍ VÝSKYT", MĚŘÍ NĚCO JINÉHO

**Naměřeno 2. 10. 2026.** Napsal jsem `zadani-kontrola.py`, který ověřuje, že
zadání pro příští session **není zastaralé** — porovnává commit, proti kterému
bylo měřeno, s živým `HEAD`. Vzor hledal **první sha v hlavičce dokumentu**:

```python
m = re.search(rf"{jmeno}[^\n]{{0,40}}?`?\b([0-9a-f]{{7,40}})\b`?", hlavicka, re.I)
```

Hlavička má ale **dvě** místa s commitem — `Zkontrolováno při:` a
`Stav obou repů při psaní:`. Když jsem v mutaci změnil **tvrzený stav repů**,
skript našel sha z **druhého** řádku (který zůstal) a **hlásil `exit 0` nad
zastaralým zadáním**. Vypadalo to jako funkční kontrola.

**Řešení:** neptej se na „první výskyt vzoru v dokumentu", ale **na konkrétní
řádek, který to tvrdí**:

```python
radek_stavu = next((l for l in radky if "Stav obou repů" in l), "")
for jmeno, sha in re.findall(r"([A-Za-z0-9_-]+)\s*=\s*`?([0-9a-f]{7,40})`?", radek_stavu):
    ...
```

**Zobecnění (a je to už třetí varianta téže pasti v tomhle projektu):**
`re.search` na „první výskyt v celém souboru" **není** to, co chceš, kdykoli je
v souboru víc míst se stejným tvarem. Patří sem i dřívější nálezy:
`re.search` vrátil `done` místo `awaiting_human` (17 zápisů stavu),
`if (ok) {` se našlo 2× (jedna správná, jedna vrácená vada). **Vždy vymez
místo, kde to tvrzení JE** — řádkem, sekcí nebo kontextem, ne pořadím výskytu.

### 7.12 MUTACE SE TICHE NEPROVEDE — PODRUHÉ A JINAK (zpětné apostrofy)

**Naměřeno 2. 10. 2026, hodinu po §7.9.** Tentokrát nešlo o diakritiku, ale
o **zpětné apostrofy uvnitř `python -c` v PowerShellu**: PowerShell je bere jako
**escape znak**, text se rozbije, `replace()` **nenahradí nic** — a test hlásí
`exit 0` na **nemutovaném** souboru. Vypadá to jako „kontrola je slepá".
**Nebyla.**

**Co to zachytilo:** `assert t2 != t, 'MUTACE NEPROBĚHLA'` — přesně proto patří
**assert, že se text změnil**, do každé mutace.

**Pravidlo (platí pro obě varianty, §7.9 i §7.12):** mutaci piš **do souboru**
(`python _analyza\*.py`), ne do `python -c` — a měj **dvě** ověření:
(1) `assert novy != puvodni`, (2) po zápisu **přečti soubor z disku** a porovnej
s původním. Když se mutace neprovede, **není to nález o bráně** — je to nález
o testu. A totéž platí pro vstup: **když vzor v souboru není, test nesmí tiše
pokračovat** (můj `mutuj()` to hlásí jako `CHYBA` a vrací `False`).
