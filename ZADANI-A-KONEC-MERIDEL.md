# ZADÁNÍ A — KONEC MĚŘIDEL, PRÁCE NA HŘE

**Zkontrolováno při:** `orchestra` = **`d1cde9b`** · `uo-shadows` = **`279f584`**
**Stav obou repů při psaní:** `orchestra` = `d1cde9b` (`M tools/kontrola-diakritiky.py`) ·
`uo-shadows` = `279f584` (čistý) · **3. 10. 2026, 20:3x UTC**
**Pushnuto:** **oba ANO** — `origin/main..HEAD = 0`
**Co je v `HANDOFF.md`:** **§25** (výsledky předchozí session) · **§8m** (omyly 105–112)
**Co tenhle dokument JE:** **zadání pro akční session typu A** — *„konec měřidel"*.
Není to stav (ten je v `HANDOFF.md`) ani plán (ten je v `PLAN-DALSI-KROK.md`).

> **⚠ ZADÁNÍ BYLO PŘEPSÁNO PO OVĚŘENÍ — a je to jeho poučení.**
> První verze tvrdila, že **pohyb hráče je „1:1 diamant" proti „2:1 mapě"**
> a že je to hlavní vada. **Naměřeno: NENÍ.** Ověřeno výpočtem:
> osa dlaždic (1,0) = posun `(48, 24)` → `|dy/dx| = 0,50`;
> hráč „vpravo" = `(0,894; 0,447)` → `|dy/dx| = 0,50`. **Sklon i znaménka sedí.**
> Kdyby session plnila první verzi, **opravovala by správný kód** — přesně ta
> past, před kterou varuje `AGENTS.md`. **Tohle je třetí vyvrácená domněnka
> v jednom dni;** všechny tři jsou zapsané v §2.1, aby se nehonily znovu.

---

## 0. PROČ TENHLE TYP SESSION EXISTUJE (a co se jím měří)

Předchozí session naměřila: **73 % bran nechrání nic, co se dostane k uživateli**,
a **omylů je plochých 7,8 na session**, ať se dělá cokoli — z toho **84 % v měřidle**.

**Hypotéza, kterou má tahle session otestovat:**

> Když session **nepostaví ani jedno nové měřidlo** a dá všechno úsilí do
> **dodávaného artefaktu**, vznikne **0–2 omyly** místo 7,8 — protože **není co zpackat**.

**To je hlavní výstup.** Kdyby vyšlo 7,8 i tady, hypotéza padá a víš, že ta
úroveň je vlastnost **procesu**, ne problému. **Oba výsledky jsou cenné —
zapiš je tak, jak vyjdou (Úkol 4).**

---

## 1. Než začneš (povinné)

1. Přečti `AGENTS.md`, `HANDOFF.md` **§25** a **§8m**.
2. Načti skilly **`dsh-prostredi`** (pasti prostředí) a **`game-developer`**.
   **`overovani` načti taky** — ne kvůli stavění měřidel, ale abys poznal
   **mrtvou větev**, až na ni narazíš (§3 Úkol 2 je jedna doložená).
3. **Ověř, že tohle zadání sedí** (jinak se v tom bodě zastav a zapiš nález):
   ```powershell
   $env:PYTHONIOENCODING='utf-8'
   & orchestra\tools\git.cmd -C orchestra rev-parse --short HEAD        # d1cde9b
   & orchestra\tools\git.cmd -C games\uo-shadows rev-parse --short HEAD # 279f584
   $env:APPDATA = "$PWD\_analyza\a-godot-user"
   & orchestra\tools\godot\Godot_v4.7.2-stable_win64_console.exe --headless `
       --path games\uo-shadows --script res://tests/run_tests.gd
   # → "[test] 65 kontrol, 0 selhání"
   ```

---

## 2. Naměřená fakta, na kterých zadání stojí (s příkazy)

| # | Fakt | Příkaz | Co vyjde |
|---|---|---|---|
| **A1** | Hra je **v `main` a živá** — save, HUD i mining **tam JSOU** | `& orchestra\tools\git.cmd -C games\uo-shadows ls-tree -r --name-only origin/main -- scripts` | `save.gd`, `hud.gd`, `mining.gd` v seznamu |
| **A2** | Živá hra má **65 kontrol, 0 selhání** | Godot `run_tests.gd` (viz §1) | `[test] 65 kontrol, 0 selhání` |
| **A3** | Web **je nasazený a živý** | `node -e "const r=await fetch('https://ssevcikm-spec.github.io/uo-shadows/index.png',{method:'HEAD'});console.log(r.status,r.headers.get('last-modified'))"` | `200` + datum **po** posledním pushi |
| **A4** | **`player.gd` NEMÁ `hp`, `max_hp`, `mana`, `max_mana`** | `& orchestra\tools\git.cmd -C games\uo-shadows show origin/main:scripts/player.gd` | V souboru **nejsou** (ověřeno hledáním všech pěti klíčů) |
| **A5** | **`assist.gd` je ČTE** → spadne na `Invalid get index 'hp'` | `& orchestra\tools\git.cmd -C games\uo-shadows show origin/main:scripts/assist.gd` | `player.hp < player.max_hp * 0.3`, `player.mana`, `player.target.hp` |
| **A6** | **`hud.gd` na to má OBEJÍTKU** → HP se **tiše neukáže** | tamtéž (`hud.gd:40–43`) | `if _player.has_method("get_hp") … elif "hp" in _player:` — jinak `hp = 0` |
| **A7** | **Kontrola izo projekce HRÁČE se NEMĚŘÍ** — mrtvá větev | Godot testy (A2) | `[test] player: move() v player.gd není – kontrola izo projekce se NEMĚŘÍ` |
| **A8** | **Pohyb hráče izometrii ODPOVÍDÁ** (není vada!) | výpočet: osa dlaždic `(48,24)` vs. hráč `(0,894; 0,447)` | obojí `\|dy/dx\| = 0,50` — **sedí** |
| **A9** | **`monsters.json` NIKDO NEČTE** — kostlivec ve hře není | `python` walk: hledej `monsters` v `scripts/*.gd` | jen `roadmap.json`; **žádný skript** |
| **A10** | Roadmapa má granuli **`entity.enemy`** (kostlivec) a **`entity.player`**, obojí **není v `done`** | `.forge/roadmap.json` | `depends_on: ["entity.item","sim.combat"]`, prompt na `scripts/enemy.gd` |
| **A11** | Roadmapa hlásí **22 granul, 0 `done`**, 13 bez `size_lines` | tamtéž | `done: 0` — **a přitom práce v repu je** (A1) |

### 2.1 Tři domněnky, které se **NEPOTVRDILY** (zapsané, aby se nehonily znovu)

(`AGENTS.md`: *„Neopravovat nástroj dřív, než je jasné, co je špatně"* — a to
platí i na **předpoklad zadání**.)

| Domněnka | Naměřeno | Verdikt |
|---|---|---|
| „`_step()` posílá `is_walkable_at` obrazovkové souřadnice, ale ta chce buňky" | `is_walkable_at(pos)` volá **`cell_at(pos)`** → chce **pixely**. Hráč i dlaždice jsou v témž prostoru (`cell_center` s offsetem) | **NENÍ VADA** |
| „`player.gd` nemá `move()`, takže se hráč nehýbe" | Hráč **se hýbe** — `_physics_process()` čte klávesy přímo. `move()` opravdu není | **Pohyb JE, měření NENÍ** (A7) |
| „pohyb hráče je 1:1 diamant proti 2:1 mapě" | Sklon i znaménka **sedí** (A8) | **NENÍ VADA** — první verze zadání mířila vedle |

---

## 3. ÚKOLY (v tomto pořadí — pořadí je závazné)

### Úkol 1 — Doplnit stav hráče, který jiné komponenty **už volají** (A4–A6)

**Co je špatně (naměřeno spuštěním, ne čtením):** `assist.gd:11–15` čte
`player.hp`, `player.max_hp`, `player.mana`, `player.max_mana`, `player.target.hp`.
**`player.gd` ani jedno z toho nemá** (A4).

**Důkaz je hotový — použij tenhle soubor: `games/uo-shadows/tests/_dukaz-assist.gd`**
(spuštění: `$env:APPDATA="$PWD\_analyza\a-godot-user"` a Godot `--script res://tests/_dukaz-assist.gd`).
Jeho dnešní výstup (zkopírováno z běhu 3. 10. 2026):

```
[dukaz] hrac ma 'hp'?          false
[dukaz] hrac ma 'max_hp'?      false
[dukaz] hrac ma 'mana'?        false
[dukaz] hrac ma 'max_mana'?    false
[dukaz] CHYBI KLICE: ["hp", "max_hp", "mana", "max_mana"]
SCRIPT ERROR: Invalid access to property or key 'hp' on a base object of type 'Area2D (player.gd)'.
   at: evaluate (res://scripts/assist.gd:11)
```

**⚠ A VŠIMNI SI, CO SE PŘITOM NESTALO — to je jádro vady:**
`evaluate()` **nespadne**. Vypíše `SCRIPT ERROR` do konzole a **vrátí `[]`**.
Takže za běhu nastane tohle:

| Kdo | Co udělá | Co to znamená |
|---|---|---|
| `assist.gd` | vrátí `[]` (prázdno) | **asistence tiše nic nedělá** — a hráč to nepozná |
| `hud.gd` | obejde to přes `has_method` (A6) | **HP: 0** — a nikdo neví, že to je „neměřeno", ne nula |
| testy hry | ptají se jen `has_method("evaluate")` | **zeleň** — brána o chování netvrdí nic |

**Tohle je táž třída, kterou má `AGENTS.md` popsanou u `done`** (*„Jiné
komponenty to API **už volají**"*) — a **druhý** výskyt v projektu.

**Co udělat:**
1. **Použij `_dukaz-assist.gd`** — dnes končí `exit 1`; po opravě musí skončit `exit 0`.
2. Doplň do `player.gd` **stav**, který kontrakt žádá: `hp`, `max_hp`, `mana`,
   `max_mana`, `target` — s **výchozími hodnotami** a **jedním** místem, kde se mění.
3. **Nezaváděj při tom nové měřidlo.** Doplň jen to, co je potřeba.
4. Až to bude fungovat, **odstraň z `hud.gd` obejití** (A6) — má čít `hp` přímo.
   **Tím se vada přestane schovávat.**
5. `_dukaz-assist.gd` **nevracej do `done`** — je to vstup, ne měřidlo.
   Po splnění ho buď přesuň k testům, nebo smaž (a napiš proč).

**Hotovo znamená:** `_dukaz-assist.gd` → **`exit 0`** (výstup ukázán)
a **HUD zobrazuje HP**. Obojí doložené **spuštěním**.

> **⚠ OMYL, KTERÝ VZNIKL PŘI PSANÍ TOHOHLE DŮKAZU (a je poučný) — přečti si ho:**
> První verze `_dukaz-assist.gd` vypsala **„evaluate() PROBESLO => vada NENI"**
> **vždy** — protože se ptala na **návratovou hodnotu**, ne na **měřenou
> podmínku**. Byla to **táž vada, jakou celý den opravuji**: skript hlásil
> úspěch tam, kde byla vada (`test-cooldown.py`, který vypsal CHYBA a skončil
> `exit 0`). **Pravidlo: assert musí být na PODMÍNCE, ne na tom, že něco proběhlo.**
> Kdybys na tuhle past narazil znovu, **zapiš ji** — je to kandidát na `overovani` §10.

### Úkol 2 — Oživit mrtvou kontrolu nad hráčem (A7)

**Co je špatně:** test má blok pro hráče podmíněný `has_method("move")`.
`move()` v `player.gd` **není** → blok se **tiše přeskočí** a vypíše jen
poznámku. **Brána o hráči netvrdí nic** a `exit 0` to nerozliší.

**Co udělat:**
1. **Rozhodni smlouvu a zapiš ji do `docs/ARCHITEKTURA.md`:** má hráč API
   `move(dir)`, nebo je smlouvou `_physics_process()`?
   **Pozor:** roadmapa v promptu pro `entity.player` **`move(dir)` žádá**
   (A10) — takže dnešní stav je **nedodaná smlouva**, ne „jiný návrh".
2. Podle rozhodnutí buď `move()` **zaveď jako skutečné API** (a `_physics_process`
   ho **volá**), nebo přepiš kontrolu tak, aby měřila **skutečnou cestu**.
3. **Kontrola musí umět spadnout:** vrať do kódu vadu (např. vyhoď izometrický
   přepočet a nech jen `dir`) a **ukaž, že test spadne.**

**Hotovo znamená:** ve výstupu **NENÍ** řádek „kontrola izo projekce se NEMĚŘÍ";
počet kontrol **vzrostl** (≥ 66); s vrácenou vadou test **spadne** — **ukaž obojí**.

### Úkol 3 — Uvést `roadmap.json` do souladu s repem (A11)

**Co je špatně:** roadmapa hlásí **0 `done` z 22**, ale práce **v repu je**
(A1). To je přesně vada, kterou měla oprava A1 zabránit — jen obráceně:
`done` se nesmí zapsat, když práce v `main` není, **ale nesmí chybět, když tam JE.**

**Co udělat:**
1. U **každé** granule ověř, jestli její práce **je v `origin/main`**.
   **A nezapomeň na `AGENTS.md`:** *„najdi její soubor v `main` a ZAVOLEJ to,
   co od ní voláš."* Pouhý výskyt souboru **není** důkaz — dnes to máš
   doložené právě na `assist.gd` (soubor je, API chybí).
2. Zapiš **skutečný** stav; kde `size_lines` chybí (**13 z 22**), doplň ho.
3. **Nepiš `done` podle dojmu** — u každé změny uveď **soubor v `main`**, který to doloží.

**Hotovo znamená:** roadmapa a rep **souhlasí** a u každé změny je doložený soubor.

### Úkol 4 — Změřit hypotézu z §0 a zapsat výsledek

**Co udělat:** na konci **spočítej vlastní omyly** této session a zapiš je do
`HANDOFF.md` **§8** jako nový blok — **a porovnej s 7,8**.

**Ptej se u každého omylu, jestli vznikl v měřidle, nebo v práci.** Když vyjde
**0–2**, máš důkaz, že ta úroveň je vlastnost **procesu**. Když vyjde **7,8**,
hypotéza padá — a to je **stejně cenné**, protože to znamená, že únava není
z měřidel.

**Hotovo znamená:** v `HANDOFF.md` je **číslo** a **srovnání**, ne dojem.

---

## 4. HOTOVO ZNAMENÁ (měřitelné — celá session)

- [ ] **Úkol 1:** `_dukaz-assist.gd` → **`exit 0`** (dnes `exit 1`) — výstup ukázán
- [ ] **Úkol 1:** **HUD zobrazuje HP**; obejití v `hud.gd` odstraněno
- [ ] **Úkol 1:** `player.gd` má `hp`, `max_hp`, `mana`, `max_mana`, `target`
- [ ] **Úkol 2:** živá hra má **≥ 66 kontrol** (dnes 65) a **0 selhání**
- [ ] **Úkol 2:** ve výstupu **NENÍ** „kontrola izo projekce se NEMĚŘÍ"
- [ ] **Úkol 2:** s **vrácenou vadou** test **spadne** — výstup ukázán
- [ ] **Úkol 3:** `roadmap.json` souhlasí s `origin/main`; `size_lines` doplněny
- [ ] **Úkol 4:** počet vlastních omylů **změřen a srovnán s 7,8**
- [ ] **VZHLED:** hra ověřená **pohledem** — `read_image` snímku
      (`AGENTS.md`: „vizuální změnu ověř pohledem, ne jen testy")
- [ ] `HANDOFF.md` — nová sekce s výsledky, **vlastní omyly do §8**
- [ ] `KRONIKA-PROJEKTU.md` — **řádek** o této session
- [ ] nové zadání pro další session v **novém souboru** —
      **`NEXT-SESSION-INSTRUKCE.md` NEPŘEPISOVAT**
- [ ] před commitem/pushem **ukázáno `git status` + `git diff --stat`** a čekáno

---

## 5. CO NEDĚLAT (tohle je jádro typu A)

- **⚠ NEPOSTAV ANI JEDNO NOVÉ MĚŘIDLO.** Žádná nová brána, žádný nový
  `audit*.py`, žádná nová kontrola dokumentace. Když na něco takového narazíš,
  **zapiš to do `HANDOFF.md` §2 jako otevřené** a jdi dál.
  **Tohle jediné pravidlo dělá z téhle session experiment.**
- **⚠ NEOPRAVUJ MĚŘIDLA, NA KTERÁ NARAZÍŠ** — ani `audit2b`, ani kroniku, ani
  diakritiku. I když budou hlásit falešný nález. **Zapiš a jdi dál.**
  *Jediná výjimka:* kdyby brána **padala na tvojí legitimní změně hry**, oprav ji —
  ale **zapiš to jako omyl procesu**.
- **NEPŘEPISUJ `NEXT-SESSION-INSTRUKCE.md`** — patří souběžné session
  (hash `9c05c6b434d5d026…`, 17 841 B, **neměnit**).
- **NEPŘESOUVEJ `HANDOFF.md` §10–§22 do kroniky** (opatření 5) — samostatná
  session s nejvyšším rizikem.
- **NEZAVÁDĚJ git pro kořen workspace** — rozhodnutí uživatele.
- **NEPŘEPISUJ historická čísla** (A2) — `HANDOFF.md` a `KRONIKA` jsou append-only.
- **NEDOPLŇUJ hlavičky** dalším dokumentům ani seznamy v branách.
- **NEOPRAVUJ `validate-all`** kvůli `exit 1` — je to **neproběhlo (prostředí)**.
- **NEZAHRNUJ `entity.enemy` (kostlivec)** — je to **samostatná granule**
  (A9/A10) a v téhle session by rozšířila záběr. **Zapiš ji jako další krok.**
- **NEPUSHUJ bez vyžádání** — nejdřív `git status` + `git diff --stat` a **čekej**.

---

## 6. PROČ PRÁVĚ TYHLE ÚKOLY (a ne jiné)

Jediné kritérium: **projde to testem „vznikne to bez tebe?"**

| Úkol | Proč patří do A |
|---|---|
| **1** stav hráče | **Jiné komponenty to volají už dnes** → je to rozbité **teď**, ne „chybějící funkce" |
| **2** mrtvá kontrola | Je to **naměřená vada brány**, ale opravuje se **kvůli hře** — a zavře díru, kterou vada 105 otevřela |
| **3** roadmapa vs. rep | `done` **rozhoduje, co se staví dál** — lež v něm zastaví vývoj (a jednou už zastavila) |
| **4** hypotéza | Bez toho by session nebyla experiment, jen práce |

**Co v zadání záměrně NENÍ** (a patří do typu **B**, ne sem): opatření 3 a 6
z předchozího zadání (krytí `schema.sql`, tabulka pokrytí diakritiky) — obě jsou
**měřidla**. Zůstávají otevřená v `ZADANI-DODELAT-MERIDLA.md`.
