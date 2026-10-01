# Assety z free zdrojů (P0 + P1)

Jak se do her orchestra dostávají assety z **free zdrojů** – odkud, pod jakou
licencí a jak se to ověří. Vzniklo 30. 9. 2026 jako odpověď na otázku „můžeš
zakomponovat free databáze assetů?".

## Co je hotové a co ne

| Vrstva | Stav |
|---|---|
| Registr zdrojů (`assets/asset-registry.json`) | **hotovo** – 4 zdroje, 2 ověřené assety |
| Fetch z Poly Haven (CC0, md5 z API) | **hotovo a ověřeno živým stažením** |
| Fetch z Kenney (CC0, sha256 pin + výběr souborů ze ZIPu) | **hotovo a ověřeno živým stažením** |
| Evidence ručních zdrojů (Freesound, OpenGameArt, Mixamo) | **hotovo** – `--registruj` |
| Brána na licence a původ (`tools/check-licence.py`) | **hotovo** – 9 scénářů testu |
| Zapojení do pipeline (aby to orchestra dělala sama) | **NE** – viz `ASSETY-PLAN.md` (P2) |

> **Nic z tohohle zatím neběží v produkci.** Žádný soubor v šabloně ani ve hře
> se nezměnil a conductor je nedotčený. Je to nástroj, který se pouští ručně.

## Rychlý start

```powershell
# co je v registru k dispozici
node orchestra\tools\asset-fetch.mjs --seznam

# stažení assetu do hry (Poly Haven: md5 se ověří proti API)
node orchestra\tools\asset-fetch.mjs --pak polyhaven/coast_sand_rocks_02

# z balíčku se vybírají JEDNOTLIVÉ soubory (ne celý balík)
node orchestra\tools\asset-fetch.mjs --pak kenney/interface-sounds --extract "Audio/click_001.ogg"

# co je v balíčku (bez --extract se jen vypíše obsah)
node orchestra\tools\asset-fetch.mjs --pak kenney/interface-sounds

# ověření, že soubory v projektu pořád odpovídají locku
node orchestra\tools\asset-fetch.mjs --overit

# brána na licence a původ (spouští se i v CI, až bude zapojená)
python orchestra\tools\check-licence.py games\uo-shadows
```

Hra se pozná sama (jediný klon pod `games/` s `.forge/roadmap.json`); když jich
je víc, řekne to a chce `--projekt`.

## Dvě vrstvy záznamu

```
orchestra/assets/asset-registry.json      ← ODKUD se smí brát (zdroje, licence, hash)
<hra>/assets/asset-lock.json              ← CO hra konkrétně použila (pin + původ)
<hra>/assets/CREDITS.md                   ← GENEROVANÝ z locku (kvůli CC-BY)
```

- **Registr** je jeden pro všechny hry. Přidání zdroje je jedna položka a všechny
  hry ji vidí – stejná logika jako u `providers.json`.
- **Lock** je v repu hry, protože tam patří provenance: kdo hru otevře, vidí
  odkud každý soubor je. Obsahuje hash a velikost, takže se dá kdykoli ověřit.
- **CREDITS.md se needituje ručně** – generuje ho fetch a brána porovnává, že
  text odpovídá locku. U CC-BY je atribuce podmínka licence, a ruční soubor se
  dřív nebo později rozešel s realitou.

## Licence

Povolené: `cc0`, `cc-by`, `ofl`, `mit`, `public-domain`.
**Zakázaná je `cc-by-sa`** – vynucuje stejnou licenci na celou hru, což u
uzavřené hry nejde.

„MIT" u assetů neexistuje (MIT je softwarová licence). CC0 je slabší podmínka
než MIT, takže je bezpečná; u CC-BY se hlídá uvedení autora v `CREDITS.md`.

## Které zdroje jsou strojově dostupné

| Zdroj | Licence | Strojově | Poznámka |
|---|---|---|---|
| **Poly Haven** | CC0 | **ano** | API dává k souboru `url`, `md5` i velikost – dá se ověřit bez hádání |
| **Kenney** | CC0 | **ano** | přímý odkaz na ZIP; hash v URL je otisk stránky, ne souboru, takže sha256 počítáme jednou a pinujeme |
| **Google Fonts** | OFL | **ano** | git repo, cesty jsou pinnutelné commitem |
| OpenGameArt, Freesound, Incompetech, Mixamo, itch.io | různé | **ne** | stáhne člověk, do locku se zapíše přes `--registruj` |

Mixamo vyžaduje účet Adobe a jeho podmínky automatizaci nedovolují – animace
postav se odtud tahají ručně, nebo se generují Blenderem (což projekt už umí).

## Jak zaevidovat ruční asset

```powershell
node orchestra\tools\asset-fetch.mjs --registruj --soubor assets/audio/ui/coin.wav `
  --licence cc-by --autor "Jméno Autora" --url "https://freesound.org/s/123456/"
```

Brána pak u toho assetu vyžaduje autora v `CREDITS.md` – a protože se CREDITS
generuje z locku, stačí ho nechat přegenerovat (dělá to i `--registruj`).

## Co brána kontroluje

1. každý soubor v `assets/` (kromě `.import`, `.uid`, dat a specu) má záznam v locku,
2. licence je v povoleném seznamu,
3. u `cc-by` je autor v `CREDITS.md`,
4. hash a velikost souhlasí se souborem na disku (pozná přepsaný asset),
5. `CREDITS.md` odpovídá tomu, co by se vygenerovalo z locku.

Když lock neexistuje, brána **projde s poznámkou** – hra bez stažených assetů
žádný mít nemusí a brána nemá blokovat práci, která s licencemi nesouvisí.
Aktivuje se prvním staženým assetem. Ověřeno na skutečném klonu `uo-shadows`:
exit 0, beze změny chování.

## Pasti, na které se narazilo

- **Limit auto-merge je 60 řádků** a počítá se z `gh pr view --json files`.
  Binárky (`.png`, `.jpg`, `.ogg`, `.wav` – viz `.gitattributes`) hlásí GitHub
  jako 0/0, takže limit **nespotřebují**. `asset-lock.json` je ale text a počítá
  se celý: dva assety = 38 řádků, tedy ~10 assetů se do jednoho PR nevejde.
  Proto se nestahují celé balíky a proto je lock kompaktní.
- **`files-to-edit.mjs` filtruje jen `.gd|json|md|cfg|tscn|tres|godot`** – binárky
  se do aideru nedostanou. Fetch tedy nemá smysl posílat modelu; což je dobře,
  protože stahování není rozhodování.
- **Balík se nevybaluje celý.** První verze registru měla `extract: ["Audio/*.ogg"]`
  a vybalila 100 souborů, které hra nikdy nenačte. Teď je `extract` prázdný
  a vybírá se jednotlivě.
- **`tempfile` v testech nefunguje** – sandbox DSH nepustí zápis do systémového
  tempu. Testy proto používají `orchestra/.tmp/` (je v `.gitignore`).
- **Podproces s pipovaným stdio spadne na `spawn EPERM`** (sandbox DSH). Všechna
  volání podprocesů v orchestra proto používají `stdio: 'inherit'`.

## Jak je to otestované

```powershell
python orchestra\tools\test-licence.py     # 9 scénářů
node orchestra\tools\validate-all.mjs      # sekce J
```

Devět scénářů: bez locku projde · v pořádku projde · soubor bez záznamu odmítne ·
`cc-by-sa` odmítne · `cc-by` bez autora odmítne · přepsaný soubor odmítne ·
změněný `CREDITS.md` odmítne · **živý P1 fixture projde** · **skutečný klon hry
beze změny chování**.

Živě ověřeno i stahování: Poly Haven textura 839 184 B s md5 proti API, Kenney
balíček 834 536 B se sha256 pinem a vybalením jednoho `.ogg` (5 kB) včetně
kontroly velikosti z ZIP adresáře.

## Kde to je

| Soubor | Co |
|---|---|
| `orchestra/assets/asset-registry.json` | registr zdrojů a assetů |
| `orchestra/tools/asset-fetch.mjs` | stahování, výběr ze ZIPu, lock, CREDITS |
| `orchestra/tools/check-licence.py` | brána na licence a původ |
| `orchestra/tools/test-licence.py` | 9 scénářů brány |
| `orchestra/ASSETY-PLAN.md` | plán P2 (zapojení do pipeline) |
