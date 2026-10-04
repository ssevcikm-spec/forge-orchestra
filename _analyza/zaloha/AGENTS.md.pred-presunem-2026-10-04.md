# Pravidla pro agenty v tomto workspace

**Co je tenhle soubor:** trvalá pravidla, která platí **napříč session**.
`HANDOFF.md` je něco jiného — ten popisuje **stav jedné session** a při každém
předání se přepisuje. Pravidla se nemají ztrácet v handoffu.

**Ověřeno měřením 1. 10. 2026.** Každé pravidlo níž vzniklo z konkrétní
chyby, která něco stála. Když si nejsi jistý, jdi po důkazu — ne po znění.

---

## Než začneš

- Přečti `HANDOFF.md` (**stav**) a tenhle soubor (**pravidla**).
- **Tvrdíš-li, že něco umíš nebo neumíš, OVĚŘ to.** Zdroj pravdy o
  schopnostech je `MOZNOSTI-AGENTA.md`; je měřený, ne odhadovaný.
  Dokumentace, která popírá vlastní nástroje, je **horší než žádná** —
  aktivně brání správnému postupu.
- Než začneš psát nebo spouštět skripty, načti skill **`dsh-prostredi`**.

## Prostředí (pasti, které vypadají jako chyba logiky)

Všechny mají stejný podpis: vypadají jako vada logiky, ale jsou to vlastnosti
nástroje, kódování nebo sandboxu. Detail a postupy: skill `dsh-prostredi`.

- **Hledej `grep` toolem, ne PowerShellem.** `Select-String -SimpleMatch`
  **tiše přeskočí soubory** → falešný negativ („nikde to není", přitom 2×).
  **A ani `grep` tool není vševědoucí:** z rodičovské složky **tiše přeskočí
  skryté složky** (`.forge`, `.github`). Naměřeno 1. 10. 2026: `grep` nad
  `orchestra/` → **0** absolutních cest, **Python walk → 80 v 59 souborech**.
  **Na plošné skeny („kolik výskytů je v celém stromě") použij Python walk** —
  hotový vzor je `_analyza\sken-vazeb.py`.
- **Ověřovací skripty spouštěj s `$env:PYTHONIOENCODING='utf-8'`** — jinak
  padají na vlastním výstupu (`UnicodeEncodeError`, konzole cp1252).
- **Do `.ps1` zapisuj bajty:** UTF-8 BOM + jednotné CRLF. Nástroj:
  `python orchestra\tools\oprav-ps1-kodovani.py`. Po každé editaci ověř
  parserem (`Parser::ParseFile`, prázdné `$err` = OK).
- **TLS z PowerShellu nefunguje** (schannel) → na síť **Node `fetch`**.
  Git přes `orchestra\tools\git.cmd`.
- **Na GitHub jen přes PAT** ze `orchestra\.secrets\` — nikdy ho nevypisuj
  ani ho nepiš do historie příkazů.
- **Sandbox `workspace-write` blokuje podprocesy s piped stdio** (`EPERM`) a
  zápis do přesměrovaného tempu (`PermissionError WinError 5`). Testy, které
  tím spadnou, **nejsou rozbité** — potřebují širší oprávnění.
- **Zapisuj do workspace, ne do tempu — i u nástrojů, které „ukládají
  do souboru".** Naměřeno: Godot `--write-movie` nezapsal framy do
  `$env:TEMP` a **nespadl při tom**; po přesměrování výstupu do workspace
  fungoval. Když nástroj tvrdí, že soubor zapsal, **ověř, že existuje** —
  v přesměrovaném tempu se může ztratit bez chyby.
- **Skilly leží mimo workspace** (`~\.dsh\skills\`) → zápis potřebuje
  oprávnění. Skill, který se nedá aktualizovat, je časovaná bomba.
- **`git show <soubor> | Measure-Object -Line` nedopočítá poslední řádek**
  bez koncového newline. Naměřeno 1. 10. 2026: u `ci.yml` hlásil **166**,
  správně je **182**. Vypadá to jako necommitnutá změna, která neexistuje.
  **Autorita je `git diff` a velikost blobu** (`git cat-file -s HEAD:<soubor>`),
  ne přepočítaný výstup.

## Jak ověřovat

- **⚠ I TRVALÁ PRAVIDLA MAJÍ ČÍSLA — a ta se musí PERIODICKY PŘEMĚŘIT.**
  Tohle je jediné pravidlo, které platí **samo na sebe**. Naměřeno 2. 10. 2026:
  `AGENTS.md` tvrdil u `conductor/schema.sql` **„32 sloupců"**, správně je
  **39** (stav před B1; dnes **40**) — a schéma se přitom od 30. 9.
  **nezměnilo**, takže číslo bylo chybné **už při zápisu**, ne zestaralé.
  Přes **šest session** si toho nikdo nevšiml, protože se **nečetlo proti
  zdroji** (nález **N9**).
  **Nástroj: `python _analyza\ag-over-cisla.py`** — přečte tvrzení
  **z dokumentu** a porovná je se **zdrojem** (`schema.sql`, bloby v `HEAD`,
  Python walk). Vrací `exit 1`, když se něco rozešlo. **Mutačně ověřeno:
  5/5 mutací chyceno** (včetně přeformulované věty).
  **Proč je chyba tady dražší než jinde:** podle `AGENTS.md` se rozhoduje ve
  **všech** session. Chyba v autoritě se **neprojeví jako chyba** — projeví se
  jako důsledek na pěti jiných místech (např. procenta jazykového inventáře
  počítaná ze špatného základu).
  **Historická čísla se NEPŘEPISUJÍ** — označí se jako „ve svém čase správná"
  (např. „10 míst s českým identifikátorem" je dnes 0, protože je Z1–Z8
  přejmenovaly; rozdíl je **čas**, ne nepravda).
- **Metriku ověř na známém správném i známém chybném případu.** „Prošlo to"
  bez toho neznamená nic. Když testy při psaní nic nenajdou, testy jsou slabé.
  **A tohle platí i na NÁSTROJ, který dokument kontroluje:** první verze
  `ag-over-cisla.py` měla tvrzená čísla **NAPSANÁ NAPEVNO**, takže měřila
  zdroj a porovnávala ho **sám se sebou**; vrácená vada v dokumentu
  (39 → 32) jí **prošla** (`exit 0`). Odhalil to až **mutační test**.
  **Tvrzení musí být PŘEČTENO Z DOKUMENTU** — jinak je brána zelená nad
  dokumentem, který nikdy neotevřela (S27).
  **A druhá past téhož skriptu:** `split("\n")` dalo u `ci.yml` **183** řádků
  místo **182** (soubor končí newline → prázdný prvek na konci). Je to
  **tatáž past**, před kterou varuje odstavec o `Measure-Object -Line` níž —
  a spadl jsem do ní znovu. **Používej `splitlines()`.**
- **Nula a „nezměřeno" nejsou úspěch.** Když se nic nezměřilo, musí to být
  vidět (`None`/`NaN`, pojmenovaná poznámka). Prázdný seznam, který se tiše
  proiteruje, je nejhorší varianta — vypadá jako naměřená nula.
- **⚠ KDO MĚNÍ KÓD, PŘEGENERUJE `_analyza\_inventar.json` — a možná víckrát.**
  Inventář je **generovaný a necommitovaný meziprodukt** (`N1`), a
  `hl-rizika-jazyka.py` (v sekci L validátoru) **pozná, že zestaral** → skončí
  `exit 1` s hláškou „INVENTÁŘ JE ZASTARALÝ / NEZMĚŘENÝ". **To je správné
  chování, ne vada nástroje** — naměřeno 2. 10. 2026: po editaci
  `kontrola-diakritiky.py` a `~\.dsh\skills\overovani\SKILL.md` spadly **dvě**
  brány na `exit 2` (`c2-mutace.py`, `n1-over-inventar.py`). Náprava:
  ```
  python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
  ```
  **Počítej s tím víckrát za session** — naměřeno: **dvakrát v jedné session**
  (otisk vstupů se posunul `8b63136727b0194d` → `4f3d76c133c4d9c6`), protože
  vstupem skeneru je **i ta brána sama a každý skill, do kterého píšeš**.
  **Kontrolu nevypínej** — je to jediná obrana proti tomu, aby se „0 vrácených"
  četlo jako měření, a už jednou zachránila skutečný nález (7 vad, které už
  byly opravené).
- **U brány se ptej „proběhla?", ne jen „neprotestovala?".** Naměřeno:
  `check-schema.py` tiše přestal měřit výchozí buňku a hlásil zelenou;
  `check-assets.py` hledá animaci tam, kde 0 souborů je.
- **Statická kontrola musí číst KÓD, ne komentáře.** Komentář popisující vadu
  nemá vypadat jako vada (falešný poplach nutí „opravovat" správný kód).
  **A pozor na opačný případ:** hledáš-li v celém souboru řetězec, najdeš ho
  i **v komentáři, který vadu popisuje** — kontrola pak projde i s vrácenou
  vadou. Naměřeno 1. 10. 2026: odhalil to až **mutační test**.
  Před hledáním vzorců **odstraň komentáře**; vzor
  `orchestra\tools\test-zamek-owns.py` (`bez_komentaru()`).
- **Test bez `assert` a bez `sys.exit` není test.** Naměřeno 1. 10. 2026:
  `tools\test-cooldown.py` vypsal `CHYBA` a **skončil `exit 0`** — na pohled
  i v CI zelený. Každý test musí mít assert **i nenulový exit kód**.
- **Napsal jsi test? Vrať do kódu vadu a podívej se, že spadne.** Mutační test
  je jediný důkaz, že test měří. Když s vrácenou vadou projde, je slabý —
  **není to zelená, je to slepá.** (Dnes to odhalilo dvě vady v mém vlastním
  testu, které by jinak odešly jako „hotové".)
- **Vizuální změnu ověř pohledem** (`read_image`), ne jen testy. Naměřeno:
  při izometrické migraci byl hráč překrytý dlaždicemi — testy, schéma i assety
  zelené, chybu našel až snímek.
- **Mrtvá větev je taky slepé místo.** Když soubor zmizí ze `scripts/`
  (u `uo-shadows` se `world.gd` **přesunul** do `_retired/` — naměřeno
  2. 10. 2026: `git show --stat c651368`), kontroly, které na něj sahají,
  se už nikdy nespustí.
- **Nefunkční metriku smazat, ne nechat ležet** — budí důvěru.
- **Brána, která nemá jak selhat, není brána.** Vzorec ze **tří** nezávislých
  případů: `check-schema.py` hledal vzorec, který v kódu nebyl → regexy nenašly
  nic → cyklus nad prázdným seznamem → **zelená**; `test-cooldown.py` vypsal
  `CHYBA` a **skončil `exit 0`**; statická kontrola našla vadu **v komentáři**.
  A brána, která čeká na vstup, jenž nikdy nepřijde, je **horší než žádná** —
  vypadá jako rozdělaná práce (LGTM: 272× `schvalil: agent-init`; role
  `worker`/`judge`, kterou kód nikde nečte).
  **Čtvrtý případ, naměřeno 2. 10. 2026:** nástroj na otevřená témata
  (`dsh-plugins\temata\kontrola-temat.mjs`) **tiše vynechával text** položek
  (lepil pokračovací řádky jen když byly odsazené; v ledgeru jich je **15**
  na nulovém odsazení) → report **tvrdil něco jiného než soubor**
  a jeho test to nechytil, protože fixture měla jen odsazené pokračování.
  **Pravidlo:** nástroj, který má předat stav, je **měřidlo** — a měřidlo,
  které tiše vynechá vstup, je stejná vada jako brána bez možnosti selhat.
  Kdo ho použije jako jediný zdroj pravdy, **přečte si jiný stav, než jaký je**.
- **⚠ BRÁNA MŮŽE ČÍST CITACI MÍSTO TVRZENÍ — a pak má `exit 1` ze špatného
  důvodu.** Naměřeno 2. 10. 2026 (audit dokumentace, nález **R1**):
  `audit2a-schema.py` hledal `(\d+)\s+sloupc`, takže v `AGENTS.md:62` zabral na
  **„32 sloupců"** — což je **citace dřívějšího chybného tvrzení** — a skutečné
  tvrzení („správně je **39**") **neměřil vůbec**, protože u něj jednotka
  nestojí. Brána hlásila 6 „rozchodů" a **ani jeden nebyl tvrzení o dnešku**.
  **Pravidlo: ptej se, KTERÝ výskyt vzor trefí** — „vzor něco našel" a „vzor
  našel to, co hledám" jsou dvě věty. U každého nálezu **vypiš kontext**.
  **A druhá polovina téhož (naměřeno tamtéž):** rozhoduje-li měřidlo, je-li
  číslo „záznam", nebo „tvrzení", **vypisuj velikost okna, které použilo** —
  první verze mé opravy brala „souvislý blok neprázdných řádků" a v `AGENTS.md`
  to byl **blok o 5 441 znacích se sedmi daty**, takže jedno datum kdekoli v něm
  umlčelo **celá** oddíl. Zúžení na jednu odrážku (824 znaků) **zvýšilo**
  pokrytí. **Velkorysé okno není opatrnost, je to slepota.**
  **A třetí (naměřeno tamtéž):** nástroj umí tisknout **jiný čítač, než jak se
  jmenuje** — `ag-mutace.py` tiskl `m.group(2)` (`ROZEŠLO SE`) pod popiskem
  „historických", a to číslo si vzal i audit do nálezu R5. **Používej
  pojmenované skupiny** (`m.group("hist")`), ne pořadové.
  → Detail osmi naměřených pastí: skill `overovani` **§10**.
- **Statická metrika, která nic nespustí, je stejně slabá jako čtení
  komentářů — a svádí k „opravě" správného dokumentu.** Naměřeno 1. 10. 2026:
  počet volání `test(` v souboru (**42**) dal falešný poplach, že handoff lže
  o počtu testů (**36/36**). Po **spuštění** vyšlo 36/36 — handoff měl pravdu
  do puntíku. **Počet testů se čte z výstupu běhu, ne z počtu vzorů
  v souboru.** Než označíš cizí číslo za nepravdivé, zkus ho zopakovat **týmž
  postupem**, jakým vzniklo.
- **Před smazáním kódu ověř, že jeho znalost je zapečená — v obou kopiích.**
  Nástroj se smí smazat, jen když jeho práce **už je** v šabloně i ve hře;
  jinak se smaže znalost, kterou si má budoucí hra dovézt. Naměřeno při F0.5
  (8 jednorázových záplat): u každé se ověřilo, že je hotová a idempotentní.
  Živý nástroj, na který odkazuje dokumentace (`oprav-ps1-kodovani.py`), se
  **nemaže**.
- **„Není to vada" je taky výsledek — ale dolož ho.** Když něco vypadá jako
  rozpor a měření ukáže, že neškodí (naměřeno: `--resolution 480x270` v CI
  proti viewportu 960×540 — Godot v movie režimu natáčí ve velikosti viewportu
  projektu, dva běhy daly **bit po bitu stejné framy**), zapiš to jako
  *neškodné, ale matoucí*. **Nesrovnávej podle dojmu** a nezamlčuj to.

- **⚠ `done` JE TVRZENÍ, NE DŮKAZ — a staví se na něm celý DAG.** Naměřeno
  2. 10. 2026 na `uo-shadows`: `world.map` i `entity.player` byly `done`
  v roadmapě **i v D1**, ale jejich práce v repu nebyla — `scripts/world.gd`
  je přesunutý v `_retired/` a granule `entity.player` dodala jen
  `project.godot` (`git log --all -S"func move"` je prázdný). Jiné komponenty
  to API **už volají** (`assist.gd` čte `hp/max_hp/mana/max_mana/target`,
  `economy.gd` volá `add_item/remove_item`). **Před stavbou na cizí granuli
  najdi její soubor v `main` a ZAVOLEJ to, co od ní voláš.**
- **⚠ BRÁNA, KTERÁ SE PTÁ NA PŘÍTOMNOST, NEMĚŘÍ CHOVÁNÍ.** `has_method("save")`
  projde i nad souborem, který v `_ready()` spadne; a `if load(...) != null:`
  **tiše přeskočí** soubor, který se vůbec nenačetl. Naměřeno 2. 10. 2026: tři
  PR prošla zeleným CI (`39 kontrol, 0 selhání`) a přitom `save()` uložil
  35 B a vrátil `true`, `hud.gd` se kvůli `margin_left` vůbec nepřidal
  a `mining.gd` spadl na `node.has()`. **Test musí kód ZAVOLAT** a ověřit
  výsledek; soubor, který součástí hry být MÁ, musí při nenačtení **SELHAT**.
  **Hotovo = soubor je v `main` A brána jeho funkci zavolala.**
  **A co je „zavolala", se musí DOKÁZAT — ne přečíst.** Naměřeno 2. 10. 2026
  (`_analyza\a3-brany-novych-granuli.md`): testy hry hlásily **`59 kontrol,
  0 selhání`**, ale blok pro hráče se **tiše přeskakoval** (byl podmíněný
  `has_method("move")`). Do **kopie** hry se vložil **třířádkový `move()`**
  a testy přešly na **`60 kontrol, 1 selhání`** — jediná nová kontrola je
  přitom **falešný poplach na legitimním kódu**. **Metoda:** vlož do kopie
  minimální artefakt (třeba jen jméno metody) a sleduj, **které kontroly se
  tím zapnou a co u toho řeknou.** Když se jich zapne nula, brána o té
  smlouvě netvrdí nic — a `exit 0` to nerozliší.
- **⚠ BRÁNA MŮŽE BÝT NASTRAŽENÁ — a to je horší než slepá.** Slepá brána mlčí;
  nastražená **vyrobí falešný nález o správném kódu**, a kdo jí věří, „opraví"
  fungující věc. Naměřeno 2. 10. 2026 (**čtvrtý** případ téhož druhu):
  `tests/run_tests.gd:836–840` **zakazuje řetězec**, který
  `scripts/player.gd:40` obsahuje **odjakživa** — a `level.gd` metodu
  `iso_position` **vůbec nemá**, takže ta větev je **mrtvá**. Test tedy
  netvrdí nic o izometrii; měří **přítomnost textu**. Do 2. 10. to nikomu
  nevadilo, protože byl **podmíněný** (`if player.has_method("move")`)
  a `move()` v repu nikdy nebylo. **Pravidlo platí i pro brány, které se
  právě teď zelenají: ptej se, co by brána řekla, KDYBY se její podmínka
  splnila — nejen jestli mlčí.**
  **Druhá past téhož druhu (naměřeno 2. 10. 2026):** `kontrola-driftu.mjs`
  porovnával `env` jako **jeden plochý seznam klíčů**. Obě kopie měly
  **33 výskytů, 16 unikátních klíčů — množiny SHODNÉ**, ale `FORGE_ATTEMPT`
  byl v herním repu na **jiném kroku** než v šabloně. Protože `env:` na
  úrovni kroku platí **jen pro ten krok**, čte ho `pick-provider.mjs:129,132`
  jen v šabloně → **rotace modelů podle pokusu byla v herním repu mrtvá**
  a drift hlásil `OK (struktura)`. **Pravidlo: u porovnání dvou kopií se
  neptej „je ten klíč někde?", ale „je na TOM MÍSTĚ?".** Porovnání podle
  **pozice** selže, jakmile mají kopie různý počet kroků (21 vs. 20) —
  proto se porovnává **mapa „klíč → na kterém kroku je"**.
- **⚠ `git log --diff-filter=D` HLÁSÍ I PŘESUNY.** Naměřeno 2. 10. 2026:
  `scripts/world.gd` se tvářil jako smazaný, ale commit `c651368` ho
  **přesunul** (`{scripts => _retired}/world.gd`). Do dokumentace se tak zapsalo
  „smazáno“ a ztratilo se, že kód existuje a je použitelný jako základ.
  **Autorita je `git show --stat` (s `-M`), ne filtr `D`.**

## Jak ověřit nasazení na GitHub Pages (důkaz, ne dojem)

HTTP 200 **není** důkaz, že se nasadila nová verze — starý web odpovídá 200 taky.
Po pushi proto ověř **všechny tři** věci:

1. **Push dorazil:** `git rev-list --count origin/main..HEAD` → `0`.
2. **Workflow na správném commitu:** `node orchestra\tools\zjisti-pages.mjs`
   → poslední `release.yml` má `head:<nový commit>` a `completed/success`.
3. **Server posílá nový build:** `last-modified` v HTTP hlavičkách je
   **po** pushi. (Node `fetch` s `method: 'HEAD'` — z PowerShellu TLS nejde.)
   ```powershell
   node -e "const r = await fetch('https://ssevcikm-spec.github.io/uo-shadows/index.png',{method:'HEAD'}); console.log(r.status, r.headers.get('last-modified'));"
   ```
   HTML stránky je jen shell s canvasem — **z HTML se verze nepozná.**

## Jak dokumentovat

- **Analytický dokument, ze kterého se něco PROVEDLO, musí ve své hlavičce
  říct DATUM SPOTŘEBY a co z něj bylo provedeno.** Jinak se za dvě hodiny čte
  jako popis dneška. **Naměřeno 2. 10. 2026:** `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md`
  vznikla v **05:45 UTC**, v **08:38–08:52** se podle ní provedly kroky A1–A4 —
  a **5 jejích tvrzení přestalo platit** (`tasks.status` „není ukotveno" →
  je; `auto-merge` „skončí zeleně" → `exit 1`; …). Naměřeno spuštěním
  `_analyza\n8-zastarala-analyza.py`. **Ironie je poučení:** analýza
  *„stavu, který si systém hlásí sám"* se **sama stala takovým stavem**.
  → Hlavička musí odpovídat na *„co z toho ještě platí?"*, ne jen *„kdy to
  vzniklo?"*. **A kdo dokument přepisuje, musí do hlavičky též uvést, čím
  ten dokument JE** (zadání / snapshot / záznam o provedení) — jinak se
  v workspace sejde pět dokumentů, každý s jiným „dnešním stavem".
- **Odkaz na projekt se odvozuje z názvu repa**, nikdy se neopisuje
  z historie. Naměřeno: v `release.yml` byl odkaz na `forge-quest`, tedy na
  **jinou živou hru** — kdo ho otevřel, hrál něco jiného.
- **Šablona nesmí tvrdit nic o konkrétním projektu.** Testovací otázka:
  *„Platí to i pro projekt, který ještě neexistuje?"* Když ne, patří to do
  projektu, ne do šablony. Naměřeno 1. 10. 2026: roadmapa šablony nesla
  **31 granul smazané hry** a `vision-profile.json` natvrdo `"hra":
  "uo-shadows"` — a instalátor to kopíroval do **každé** nové hry. Přesně tak
  se „pozůstatky staré hry" šíří dál. Obecnost šablony je **vlastnost, kterou
  je potřeba hlídat**, ne stav, který se jednou zařídí.
  **Druhé kolo téhož, naměřeno 1. 10. 2026 (večer):** šablona nesla **12 zmínek
  o `uo-shadows`** i v **komentářích brány** (`check-schema.py`) — a protože
  test hlídá **shodný hash obou kopií**, musely se změnit **obě naráz**.
  → **Opraveno na 0×**; konkrétní důkaz dostal v kódu vlastní odstavec
  („patří hře, ne sem").
- **ALE pozor: skill není šablona.** Skill (`~\.dsh\skills\`) je pro **tebe**,
  ne pro cizí projekt — a **konkrétní příklady mít MÁ**, jen **oddělené** od
  obecného postupu. Skill bez příkladů je nepoužitelný; skill s příklady
  promíchanými do pravidel plete dvě věci dohromady.
  **Vzor:** `hlouchkova-analyza` — sekce 1–5 obecně, **sekce 6 „Příklady
  z našeho projektu" (záměrně oddělená)**, sekce 7 návod k použití.
- **Znalost patří k naměřenému příkladu, ne k pravidlu.** „Ověřuj" nikoho nic
  nenaučí; **past s číslem, souborem a datem ano.** Proto mají skilly
  (`overovani` §7, `dsh-prostredi`) u každé pasti konkrétní měření — a proto se
  do nich po každé session doplňuje, co se naměřilo. Když narazíš na past,
  která v žádném skillu není, **doplň ji tam** i s příkladem.
- **Ke každému číslu v dokumentu patří postup, kterým vzniklo.** „36/36" bez
  toho, co se spustilo, se nedá ověřit ani vyvrátit — a čtenář ho buď uvěří,
  nebo ho „opraví" špatně. **U čítačů a běhů vždy napiš, odkud jsou** (kód?
  jiný systém? který endpoint?), protože **různé čítače nesou stejné jméno**:
  naměřeno 1. 10. 2026 — „běh #355" v dokumentu vs. `run_number` **#241**
  v GitHub API. A **přiřčení je taky tvrzení**: „PR se sloučily samy" vyvrátí
  `merged_by` v API (byl to uživatel).
- **Web staví jen to, co je na `main`.** Necommitnutá práce v klonu se
  v prohlížeči nikdy neobjeví.
- **Zdroj pravdy o repech a Pages** je `node orchestra\tools\zjisti-pages.mjs`
  (GitHub API), ne paměť a ne starý zápis.
- **Tvrdíš-li v dokumentaci něco o STAVU („není pushnuto", „uzel běží", „fronta
  je prázdná"), ověř to živě — ne z předchozího handoffu.** Naměřeno 1. 10. 2026:
  handoff tvrdil, že dva commity **nejsou pushnuté**; GitHub API vrátilo jeden
  z nich jako **HEAD repa**. Nepravdivé tvrzení o stavu se čte jako fakt a
  **plánuje se podle něj** — přišlo to na dvě session.
- **Zelený řídicí systém není důkaz, že práce probíhá.** Naměřeno 1. 10. 2026:
  conductor hlásil `/health` → `ok: true`, `ready: 7`, a `/failed` **prázdné** —
  a přitom 7,5 h nevydal ani granuli, protože `main` cílové hry měl **červené
  CI**. **Ptej se i na stav cíle, ne jen na stav řídicího systému.**
- **Přepisuješ-li `HANDOFF.md`, nic nesmí zmizet.** Handoff je jediné místo,
  kde žijí otevřené body — jejich ztráta je nejdražší chyba předání.
  Po přepisu **vypiš, které body zůstaly**, a ověř je (hledáním klíčových slov),
  ne pamětí. Co už není otevřené, přesuň do „Co už otevřené NENÍ" — **nemaž**.
- **Zapíšeš-li do dokumentace ukázku rozbitého kódování, kontrola diakritiky
  to nahlásí jako vadu dokumentu.** Popisuj je **slovem**.
- **Design dokument, ze kterého se vydávají granule, musí u každé smlouvy nést
  TVAR DAT a PŘIJÍMACÍ KRITÉRIUM — jinak agent dostane jméno API bez obsahu.**
  Naměřeno 2. 10. 2026: kontrakt `Hráč → move(), inventář, die()` nedefinoval
  ani typy, ani kdo to volá → granule `entity.player` dodala jen `project.godot`
  a byla zapsaná jako `done`. Slovo `acceptance` se v designu hry nevyskytovalo
  **0×**, přitom roadmapa ho používá u každé granule.
  **Metodika (a co v ní ještě chybí): `JAK-PSAT-DESIGN-A-PLANOVAT-VYVOJ.md`** —
  rostoucí dokument, do kterého každá session doplňuje **naměřené** případy; je
  to příprava pro revizi skillu `game-developer` a pro přepis designu
  `uo-shadows`. Kdo v designu nebo plánování najde naměřenou vadu, **patří tam**.
- Dokumenty, které se kontrolují: `kontrola-diakritiky.py`,
  `over-dokumentaci.py`, `over-skilly.py` — po každé editaci je spusť.

## Kdy práce patří do nové session

Není to o tokenech. Je to o **nezávislosti pohledu**:

- **Analýza, audit nebo rozhodnutí o něčem, co jsem sám psal** → nová session.
  Autor není nezávislý reviewer. Naměřeno 1. 10. 2026: analýza architektury
  orchestra šla do nové session právě proto, že tuhle session psala její
  dokumentaci i jednu z bran.
- **Co má nová session dělat, patří do zadání** (`*ZADANI.md`): cíl, naměřená
  fakta, konkrétní otázky, required výstup a co **nedělat**. Zadání se píše
  v session, která kontext **má** — nová session ho nemá a začala by čtením
  README, tedy popisem místo analýzy.
- **Dokončit a ověřit vlastní práci** naopak patří do session, která ji dělala:
  má kontext, ví, co se změnilo a proč.

## Jazyk: kde česky a kde ne (změřeno 1. 10. 2026)

**Odpověď na otázku „neškodí ta čeština technicky?" je: v dokumentaci ne,
v deseti místech kódu ano.** Změřeno inventářem `_analyza\hl-neanglicky-v-kodu.py`
nad **161 soubory** (2 002 nálezů, **0 nepokrytých**):

| Vrstva | Naměřeno | Verdikt |
|---|---|---|
| Názvy souborů a cest (orchestra) | 113 souborů, non-ASCII v názvu: **0** | bez rizika |
| Názvy sloupců D1 (`conductor/schema.sql`) | 5 tabulek, **40 sloupců, českých 0** | serverová vrstva čistá |
| Klíče a identifikátory CI | `task_id`, `run_key`, `FORGE_*` — ASCII | bez rizika |
| Diakritika v `.md` orchestra | 2 533 znaků ze 44 781 = **5,7 %** | zbytek je ASCII kód a cesty |
| Čeština jako IDENTIFIKÁTOR | **10 míst** (viz níž) | **riziko → má být ASCII** |

**Pravidlo (napsané proto, aby se to příště nemuselo měřit):**

- **Identifikátory, klíče, názvy sloupců, cesty a literály ROZHRANÍ = ASCII
  anglicky.** Nikdy `ohlášeno`, nikdy `"cíl mrtev"`.
- **Dokumentace, komentáře a texty pro uživatele = česky** (klidně
  s diakritikou; UTF-8 v souborech je standard a nic nekazí).
- **Výstup nástroje pro člověka = česky; hodnota, kterou čte jiný PROGRAM =
  anglicky.** To je jediná hranice, na které opravdu záleží.

**Naměřené příklady (každý z kódu, ne z dojmu):**

> **⚠ DATUM SPOTŘEBY (doplněno 2. 10. 2026):** příklady níž jsou **naměřené
> důkazy pravidla, ne popis dnešního kódu.** Všechny uvedené identifikátory
> byly **2. 10. 2026 přejmenovány** (plán Z1–Z8). Kdo je půjde hledat do kódu,
> **nenajde je** — a to je správně. **Nemažou se:** bez nich by pravidlo
> nebylo doložené. Nový stav: `hl-rizika-jazyka.py` → **0 očekávaných,
> 11 přejednaných, 0 vrácených**.

- `orchestra/conductor/src/index.ts:247` → `let ohlášeno = 0;` — jediný český
  identifikátor v jádře orchestra (ASCII varianta: **0 souborů**). Drží
  konzistentně i v patchi `tools/pridej-eskalaci.py:50`.
  **→ přejmenováno na `notified`** (Z1).
- `games/uo-shadows/scripts/assist.gd:11–15` — **veřejné rozhraní
  `add_rule(trigger, action)` míchá jazyky**: `"hp < X"` a `"mana < X"`
  anglicky, ale `"cíl mrtev"` česky s diakritikou. Volající musí uhodnout jazyk.
- `orchestra/tools/analyza-modelu.mjs:58` → `poz === '—'` — **porovnává se
  s pomlčkou, kterou si tentýž skript sám vykreslil jako prázdnou hodnotu.**
- `orchestra/repo/.forge/check-schema.py:392` **a** `games/uo-shadows/.forge/check-schema.py:392`
  → `nesedí = []`; `make_iso_tiles.py:261` → `pás`; **a taky
  `.forge/vision.mjs:42,47`** → `function vezmiPrepínac(...)`. **Táž past jako
  u `.gitattributes`:** soubory existují ve **dvou kopiích** (šablona + hra)
  a drift test hlídá shodný hash → přejmenovat se musí **obě naráz**.
- `orchestra/tools/sjednot-sablonu.py:111` →
  `if s.get("name") == "Spusť agenta"` — **skript si z cizího `agent.yml`
  vyfiltruje krok podle DOSLOVNÉHO českého názvu.** Ověřeno 1. 10. 2026: název
  (`agent.yml:116`, resp. `:121`) **sedí**, takže dnes to funguje. Ale selhání je
  tiché: po přejmenování je `kroky` prázdný list → `env_ok = False` → skript to
  **vypíše a stejně skončí úspěšně**. „Brána, která nemá jak selhat."
- `games/uo-shadows/assets/spec.json` → klíč `styl.zmenšování` je **jen v lidském
  popisu** (0 čtenářů v kódu) → **nechat být**; není to identifikátor.

**Dvě pasti, které měření mezi jazykem a kódem má (obě mě chytily):**

1. **Kdo měří na DISKU, najde vady, které neexistují.** `core.autocrlf=true` na
   checkoutu přidá `\r`: soubor hry měl 820 B, šablona 787 B — a přitom **bloby
   byly shodné** (`f508e781e6005d0e`). Autorita je blob, ne velikost souboru.
2. **Kdo se ptá na `orchestra\.gitattributes`, ptá se na špatné místo.** Šablona
   je `orchestra\repo\`; kořen orchestra `.gitattributes` **nemá** — a `git status`
   navíc hlásí **jen jeden** repozitář (jsou dva: `orchestra\` a `games\uo-shadows\`).

## Co nikdy

- **⚠ `E:\DSH` UŽ NEEXISTUJE — datový adresář se přestěhoval (1. 10. 2026).**
  Co platilo do té doby: `E:\DSH\data` **nebyl** pozůstatek, ale živý
  `DSH_HOME` běžící aplikace (API klíče, sessions, skilly, profily) — přes
  junction `C:\Users\Ssevc\.dsh`. Smazat se směl **jen po migraci**.
  **Teď:** `C:\Users\Ssevc\.dsh` → **`E:\DeepSeekHarness-data`**; stará data
  i `roaming` jsou v `E:\DSH-quarantine\20261001-144747\` (**to je rollback,
  nemaž ho, dokud nejsi spokojený**). Postup, měření a pasti:
  `POZOR-E-DSH-NEMAZAT.md`. Migrační skript:
  `dsh-consolidation\cleanup\migrate-dsh-data.ps1` (+ `test-migrace.ps1`).
  **Poučení, které platí dál:** co vypadá jako „stará složka", může být živý
  datový adresář; a cesta k datům patří do `DSH_HOME`, ne jako konstanta
  do skriptu (v 16 skriptech byla `E:\DSH\data\sessions` natvrdo).
- **Nepushovat bez vyžádání.** Předem ukázat `git status` a `git diff --stat`.
- **Nemazat cizí repozitáře ani jejich Pages.** `forge-quest` je živá hra.
- **Nepřebírat tvrzení o schopnostech** z dokumentace bez ověření.
- **Neopravovat nástroj dřív, než je jasné, co je špatně** — nástroj, nebo
  předpoklad testu.

## Kam pro co

| Soubor | Co v něm je |
|---|---|
| `HANDOFF.md` | stav poslední session, „pick up here" |
| `KRONIKA-PROJEKTU.md` | **celý příběh projektu** — session po sessioni, nálezy (N/H/S/V/P), **omyly a jejich trend**, poučení s naměřenými případy, **návrhy se stavem** (`NEOVĚŘENO` → `APLIKOVÁNO`/`ZAMÍTNUTO`/`ODLOŽENO`). **Nikdy se nepřepisuje, jen doplňuje** — je to jediné místo, kde přežije historie. Ověřuje `python _analyza\kronika-kontrola.py`. **Návrh na zlepšení zapíše session hned, ale rozhodne o něm až ta příští** (`PREDAVANI-SESSION.md` §2.2) — autor není nezávislý reviewer. |
| `PREDAVANI-SESSION.md` | **jak volat další session** — dva kroky (plánovací → akční), šablony promptů ke zkopírování, „Hotovo znamená" pro každou session a naměřené pasti předávání. **Tenhle soubor říká JAK předávat; stav je v `HANDOFF.md`.** |
| `AGENTS.md` | tenhle soubor — trvalá pravidla |
| `MOZNOSTI-AGENTA.md` | co agent umí (měřené důkazy) a co ne |
| `JAK-PSAT-DESIGN-A-PLANOVAT-VYVOJ.md` | **jak psát design dokumenty a plánovat vývoj pro AI pipeline** — rostoucí podklad pro revizi skillu `game-developer` a pro přepis designu UO-Shadows; **každá session do něj doplňuje naměřené případy** |
| `NEXT-SESSION-INSTRUKCE.md` | **zadání pro PŘÍŠTÍ session** — přepisuje ho vždy ta session, která končí (`PREDAVANI-SESSION.md` §3). **Není to stav ani plán:** stav je v `HANDOFF.md`, plán v `PLAN-DALSI-KROK.md`. Kdo ho čte, **ověří hlavičku** (`rev-parse HEAD` v obou repech) — když nesedí, přeměří **všechna** tvrzení o stavu. |
| `PLAN-DALSI-KROK.md` | **plán dalších kroků** — co dělat, v jakém pořadí a co **NE**. Píše ho **plánovací** session po ověření (nebo akční, když mění pořadí). Má **hlavičku s datem spotřeby**: analytický dokument, ze kterého se něco provedlo, musí říct, **co z něj ještě platí** — jinak se čte jako popis dneška. |
| `PLAN-ROZVOJ-ORCHESTRA.md` | plán: architektura a kontrakt — fáze F0–F5, **§3.5 implementační plán (fáze A–D)**, otázky O1–O10 |
| `PLAN-ORCHESTRA-AI-AGENTI.md` | plán: provoz s AI agenty (N0–N5, otázky R1–R15) |
| `PLAN-SEPARACE-WORKSPACE.md` | plán: separace orchestra z tohoto workspace (G0–G5, S1–S9) |
| `ANALYZA-ARCHITEKTURY-ORCHESTRA.md` | analýza architektury (16 tříd selhání S1–S16 + §8 dodatek se S17/S18) |
| `ORCHESTRA-STAV-A-ANALYZA.md` | **stav doporučení L1–L17 / ST1–ST10** (co je hotové a co ne, měřeno) + kde se plán a analýza rozcházejí v pořadí; nález `NAZEV-REPA` |
| `FORGE-ORCHESTRA-MOZNOSTI.md` | nálezy a návrhy pro orchestra |
| `PLAN-VISION-ORCHESTRA.md` | schválený plán vizuální kontroly |
| `SKILLY-AKTUALIZACE.md` | historie změn skillů a dokumentace |
| `POZOR-E-DSH-NEMAZAT.md` | **migrace dat z `E:\DSH` — vyřešeno 1. 10. 2026** (co bylo živé, co selhalo, kde je karanténa) |
| `ARCHITEKTURA-ANALYZA-ZADANI.md` | zadání pro analýzu architektury orchestra (vzor, jak psát zadání pro novou session) |
| `ANALYZA-HLOUBKOVA-ZADANI.md` | **zadání pro hloubkovou analýzu a návrh architektury orchestra** — metodika (značky, tři úrovně důkazu, pět pastí), devět optik návrhu, struktura výstupu a 10 dosud nezodpovězených otázek |
| `ANALYZA-HLOUBKOVA-ORCHESTRA.md` | **výsledek hloubkové analýzy (1. 10. 2026)** — 12 oddílů, třídy selhání **S19–S30**, 9 z 10 otázek, 2 varianty návrhu, vlastní omyly |
| `ANALYZA-HLOUBKOVA-2-ZADANI.md` | **zadání pro DRUHÉ kolo** — téma „stav, který si systém hlásí sám". **✅ SPLNĚNO 2. 10. 2026** (9/9 bodů, `_analyza\hl2-kontrola.py`); **neplnit znovu**, ale je to **vzor zadání pro novou session**. Zákaz „neměnit kód" v něm **neplatí** (mandát: `HANDOFF.md` §8.2) |
| `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` | **výsledek DRUHÉHO kola (2. 10. 2026, 05:45 UTC)** — **⚠ SNAPSHOT, ne popis dneška**: A1–A4 (08:38–08:52) změnily kód a **5 jeho tvrzení tím zastaralo**. Sekce S31–S37, tabulka „tvrzení systému o sobě → čím je ukotveno", 2 varianty. **Ověřeno `_analyza\n8-zastarala-analyza.py`** |
| `IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md` | **✅ ZÁZNAM O PROVEDENÍ A1–A4** (2. 10. 2026) — původně zadání; teď doklad, co a proč se změnilo. Drženo **závazné pořadí** (A3 před A1 = smyčka) |
| `IMPLEMENTACE-HRANICE-JAZYKA.md` | **✅ ZÁZNAM O PROVEDENÍ Z1–Z8** (2. 10. 2026) — hranice jazyka v kódu; 11 míst přejmenováno, obě kopie se shodným hashem |
| `IMPLEMENTACE-NOVE-NALEZY-Z-UKOTVENI.md` | **N1–N8 + plán (neprovedený)** — nálezy z provádění A1–A4/Z1–Z8, každý doložený spuštěním. **N1** zastaralý inventář · **N3** nová třída (kontrola projde z různých důvodů) · **N8** analýza se rozešla s kódem. **Odkud pokračovat.** |
| `PROMPT-NOVA-SESSION.md` | **prompt pro nový chat (2. 10. 2026)** — **výzva k ověření práce** předchozí session (10 měřitelných bodů, u každého příkaz) + co dál. Vznikl při sjednocení zdrojů po souběhu **tří** session |
| `SOUBEH-SESSION-NALEZY.md` | **co proklouzlo, když dvě session psaly tytéž soubory** (2. 10. 2026) — co se neztratilo a čím je to ověřené, co chybí v rejstříku, vlastní falešný poplach |
| `DEPLOY-VYLEPSENI.md` | **rozcestník nasazení** (1. 10. 2026) — 11 opatření s vyčíslenou úsporou (cíl −79 %), co je hotové a co **není nasazené** |
| `sdxl-comfyui-2d-game-assets-research.md` | rešerše **lokálního generování 2D grafiky** (SDXL + ComfyUI na RX 6600) — podklad ke skillu `imagegen-local`, 46 kB |
| `token-saving-tools-dsh-evaluation.md` | hodnocení **10 nástrojů na šetření tokenů** vůči DSH — podklad k nákladovým rozhodnutím a `PLAN-*`, 54 kB |
| `_analyza\HLOUBKOVA-MERENI.md`, `-2.md`, `-3.md` | surová naměřená čísla ke hloubkové analýze (**tři kola, tři časy**) + skripty `_analyza\hl-*` a `hl2-*` |
| `_analyza\hl2-soubeh.py`, `hl2-casova-osa.py`, `hl2-nic-nezmizelo.py` | **detekce souběhu session** — které soubory psaly dvě session, v jakém pořadí a co mohlo zmizet |
| `_analyza\hl2-rozbal-session2.mjs` | rozbalí session log (zstd s **1081 rámci**; `zstdDecompressSync` přečte jen první) |
| `_analyza\hl-neanglicky-v-kodu.py` | **inventář neanglických textů v kódu** obou rep — čte AST/parser, třídí podle kontextu (komentář ≠ hláška ≠ klíč ≠ identifikátor). `--json <cesta>` pro strojový výstup |
| `_analyza\hl-rizika-jazyka.py` | **finální seznam rizik** jazyka v kódu + kontrola úplnosti; vstup si vygeneruje sám. Projde = `exit 0` |
| `_analyza\test-neanglicky-skener.py` | **mutační test** toho skeneru (23 kontrol). Bez něj „0 nálezů" nic neznamená |
| `_analyza\js-tokeny.mjs` | parser JS/TS pro skener (bere `typescript` z `conductor/node_modules`) |
| `_analyza\a1-a2-over.py` | **brána na A1/A2** (**23 kontrol** od 2. 10. 2026): rozhoduje `done` podle `ok && merged`? ověřuje se `owns` proti `origin/main`? Používá se TTL konstanta **skutečně**, nemůže cache sloužit navždy a je `awaiting_human` **zapsaný v D1**? **Mutačně ověřeno 4/4** (`a1-a2-mutace.py`). *(Dřív 19 kontrol a chytila jen 2 z 5 — nález **V2**.)* |
| `_analyza\a3-over.py` | **brána na A3** — ověří `exit 1` v kroku „Když pravidla neprošla" v **obou** `agent.yml`, **na řádku** (v souboru je `exit 1` 6×) |
| `_analyza\n8-zastarala-analyza.py` | **datum spotřeby analýzy** — porovnává tvrzení `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` s **kódem**; **5 zastaralých + 2 kontrolní vzorky**. Ptá se na **zapsaný stav v D1** (všech 17 zápisů, ne první) a na **funkci** (deklarace **i** volání). **Mutačně ověřeno 3/3** (`n8-mutace.py`, porovnává **množinu**, ne počet). *(Dřív hledal slovo a jméno — nález **V3**.)* |
| `_analyza\z8-probe.py` | kde je krok s `FORGE_ATTEMPT` v obou `agent.yml` (odhalil, že v herním repu je to **jiný krok**) |
| `_analyza\handoff-kontrola-uplnost.py` | **nic nezmizelo z `HANDOFF.md`** — 83 klíčových bodů; spouštěj po každém přepisu handoffu |
| `_analyza\hl2-kontrola.py`, `hl2-mutace-kontrola.py` | **brána na „Hotovo znamená"** 2. kola — **10 bodů** (9 ze zadání + **obsahová kontrola**), **mutační test 6/6**. Obsahová kontrola (doplněna 2. 10. 2026, nález **V1**): každá ze 12 sekcí musí mít **≥ 4 řádky a ≥ 200 znaků** — dřív brána prošla nad **12,5 % dokumentu** s `\| **Cena** \| X \|` místo obsahu |
| `_analyza\hl2-kostra-test.py`, `hl2-kostra-kalibrace.py` | **kalibrace té brány** — vyrobí z dokumentu „kostru" (nadpisy + markery) a ověří, že **spadne**. Bez kalibrace by se z prvního skriptu dalo myslet, že brána obsah měří |
| `_analyza\ag-over-cisla.py` | **PŘEMĚŘENÍ ČÍSEL V `AGENTS.md`** — čte tvrzení **z dokumentu** a porovná se zdrojem (`schema.sql`, bloby v `HEAD`, walk). `exit 1` při rozchodu. **Mutačně ověřeno 5/5** (`ag-mutace.py`). Spouštěj po každé editaci `AGENTS.md`. ⚠ **Pokrývá 5 + 2 z 80 řádků s číslem** — částečný nástroj (nález **N9**) |
| `_analyza\ag-mutace.py` | mutační test `ag-over-cisla.py` — vada **40→32** (kotva `39 sloupců` v dokumentu **není**, nález **R5**) **i přeformulované tvrzení**; měří i pokrytí. **Od 2. 10. 2026 je v `BRANY` v `g3-brany.py`** — do té doby jeho `exit 1` nikdo nečetl. Vypisuje `ZMĚŘENO: mutací=2, chyceno=N` |
| `_analyza\audit-snapshot.py` | **zmrazení snapshotu dokumentace** (Úkol 0) — jádro + kořen + skilly, `manifest.json` s SHA-256/velikostí/mtime; druhý běh **vypíše rozdíly** a skončí `exit 1`. **Není v `g3-brany.py` záměrně** — změna dokumentace je normální stav, brána by neměla jak nespadnout. Ověřuje `audit-snapshot-over.py` |
| `_analyza\audit2a-mutace.py` | **mutační test `audit2a-schema.py`** — 4 mutace, 4 chyceny (vč. vrácení `39` **bez značky času**, což je vada R1, kterou původní brána **nikdy neviděla**) |
| `_analyza\audit2b-over.py` | **brána na opravu `audit2b`** (Úkol 4) — `granulí` 0 rozchodů, řádek 1143 zařadil **nadpis oddílu**, 2 mutace, `HANDOFF.md` bit po bitu shodný se snapshotem |
| `_analyza\audit3-hlavicky-over.py` | **brána na Úkol 3** — oba „neproběhnuvší" testy mají hlavičku, **pořád padají týmž důvodem** a nezměřily ani jeden běh |
| `_analyza\a1-a2-mutace.py` | **mutační test `a1-a2-over.py` na ŽIVÉM `index.ts`** — **4 mutace, 4 chyceny**. Zálohuje **kopií**, ne `git checkout` (soubor má necommitnuté změny). Obsahuje jen **skutečné vady** — sémanticky neutrální přejmenování tam nepatří (nález z 2. 10. 2026) |
| `_analyza\a3-mutace.py` | mutační test `a3-over.py` — vada v **herní** kopii `agent.yml` (šablona zůstává nedotčená) |
| `_analyza\n8-mutace.py` | mutační test `n8-zastarala-analyza.py` — vrací vady A1/A3 **a** hledá slepá místa (nález **V3**) |
| `_analyza\b5-over-tvrzeni.py` | **5 tvrzení analýzy ověřených NEZÁVISLE** na `n8-*` (jiné měřidlo, s úryvky kódu) |
| `_analyza\n1-over-inventar.py` | **N1** — měří, že nástroj **pozná zastaralý inventář** a skončí nenulově (4 běhy: zdravý 0, přepsaný otisk 1, bez otisku 1, návrat 0). ⚠ **Původní verze byla obrácená** (zelená = „N1 JE PRAVDA"); po opravě C2 se musela přepsat — správné chování v ní vypadalo jako nález |
| `_analyza\sken-vazeb.py` | sken vazeb projektu na okolí (Python walk; `grep` tool tu selhal 80 ku 0) |
| `_analyza\dsh-session-prehled.mjs` | **čí je která session** (titulek, první zpráva, hloubka 0 = session / 1 = podagent). Pro orientaci, když v jednom workspace pracuje víc session současně. `--vsechny`, `--hledej TEXT` |
| `_analyza\over-okno.mjs` | `contextWindow` podle modelu z `request/context` v session lozích — **spusť po každé změně modelu**, `dsh-usage\report.mjs` má okno 1M natvrdo |
| `~\.dsh\skills\` | skilly (`dsh-prostredi`, `orchestra`, `game-developer`, `game-assets`, `vision`, …) |
