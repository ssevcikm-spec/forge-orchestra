# ZADÁNÍ PRO AKČNÍ SESSION — dodělat opravu měřidel

**Zkontrolováno při:** `orchestra` = **`d1cde9b`** · `uo-shadows` = **`279f584`**
**Stav obou repů při psaní:** `orchestra` = `d1cde9b` (`M tools/kontrola-diakritiky.py`) ·
`uo-shadows` = `279f584` (čistý) · **2. 10. 2026, 20:5x UTC**
**Pushnuto:** **oba ANO** — `origin/main..HEAD = 0` v obou repech
**Co je v `HANDOFF.md`:** **§25** (výsledky téhle session) · **§8m** (vlastní omyly
**105–112**) · **§2** (co je otevřené)
**Co tenhle dokument JE:** zadání pro **akční** session, která přijde.
Není to stav (ten je v `HANDOFF.md`) ani plán (ten je v `PLAN-DALSI-KROK.md`).
**Předchozí zadání:** `ZADANI-OPRAVA-MERIDEL.md` — **splněno z větší části**,
stav a odchylky: `HANDOFF.md` **§25.1**.

> ## ⚠ PŘEČTI TYHLE DVĚ VĚCI PRVNÍ
>
> **1. `NEXT-SESSION-INSTRUKCE.md` NENÍ tvoje zadání.** Patří **souběžné
> session** a jeho obsah se **nezměnil ani o bajt** (SHA-256
> `9c05c6b434d5d026…`, 17 841 B) — i když se `mtime` pohnul (hnuly jím mutační
> testy této session; je to **třetí a čtvrtý výskyt nálezu H28 v jedné
> session**). **Tvoje zadání je tenhle soubor.**
>
> **2. Zadání, které jsi právě dostal, tvrdí čísla — a ta ZESTÁRNOU.**
> Naměřeno v této session: `ZADANI-OPRAVA-MERIDEL.md` tvrdilo u Úkolu 1
> „rozchodů **31**, z toho **25 falešných**"; ve skutečnosti bylo **30**,
> a z 30 bylo falešných **21** — **jinak rozdělených**, než zadání tvrdilo
> (`kontrol` 15, ne 19). **Tvůj první úkol je ověřovat, ne věřit.**

---

## 1. Než začneš (povinné)

1. Přečti `AGENTS.md`, `HANDOFF.md` **§25**, **§8l** a **§8m**,
   `PLAN-DALSI-KROK.md`.
2. Načti skilly **`dsh-prostredi`** a **`overovani`** `skill` toolem.
3. **Ověř, že tohle zadání sedí na skutečnost** (jinak se v tom bodě zastav
   a zapiš to jako nález):
   ```powershell
   $env:PYTHONIOENCODING='utf-8'
   & orchestra\tools\git.cmd -C orchestra rev-parse HEAD        # d1cde9b
   & orchestra\tools\git.cmd -C games\uo-shadows rev-parse HEAD # 279f584
   python _analyza\audit2b-cisla-proti-zdroji.py                # rozchodů <= 14
   python _analyza\audit1-inventar.py                           # bez hlavičky <= 20
   python _analyza\audit6-brany-mutace.py                       # BEZ důkazu: 7
   python _analyza\s24-meridla-over.py                          # exit 0
   ```

---

## 2. Naměřená fakta, na kterých zadání stojí (s příkazy)

| # | Fakt | Příkaz | Co vyjde |
|---|---|---|---|
| **G1** | `audit2b` hlásí **9 rozchodů** (bylo 30) | `python _analyza\audit2b-cisla-proti-zdroji.py` | `ROZCHODŮ: 9`; u každého **zdroj** |
| **G2** | z toho **2 jsou TÁŽ čísla na živých místech** `HANDOFF.md` | tamtéž | `KRONIKA-PROJEKTU.md:340` tvrdí 39 · `:341` tvrdí 0 |
| **G3** | `g3` u `validate-all` vypisuje **`—`** | `python _analyza\g3-brany.py` | `otevřela: — (brána nemá čítač)` |
| **G4** | `kronika-kontrola.py` zná **12 bloků / 99 omylů** | `python _analyza\kronika-kontrola.py` | `bloků omylů v tomto součtu: 12` |
| **G5** | `handoff-mutace.py` → **82/83** | `python _analyza\handoff-mutace.py` | `exit 0`, mutace chycena |
| **G6** | `over-dokumentaci-mutace.py` → **exit 1** | `python _analyza\over-dokumentaci-mutace.py` | `exit 0`, mutace chycena |
| **G7** | `b5-mutace.py` → **4 z 5** | `python _analyza\b5-mutace.py` | `exit 0`, mutace chycena |
| **G8** | hlavičky: **14 z 111** bez hlavičky (bylo 80) | `python _analyza\audit1-inventar.py` | `bez hlavičky: 14` — **všech 14 jsou zálohy/kopie/skilly** |
| **G9** | bran bez důkazu **7 z 30** (bylo 10) | `python _analyza\audit6-brany-mutace.py` | `Brány BEZ jakéhokoli důkazu: 7` |

---

## 3. ÚKOLY (v tomto pořadí — pořadí je závazné)

### Úkol 1 — zbylé rozchody `audit2b` (9 → ≤ 6)

**9 zbylých rozchodů a co s nimi (naměřeno, `G1`):**

| # | Kde | Co to je | Co udělat |
|---|---|---|---|
| 1 | `HANDOFF.md:590` | `dokumentů` tvrdí **8**, řádek mluví o **„8 dokumentů"** z věty o tabulce | **Rozhodnout:** buď doplnit 4. zdroj („8 řádků tabulky" není počet), nebo přiznat v docstringu, že tenhle tvar guard **neumí** odlišit od „8 dokumentů". Dnes ho guard **propustí** — a to je falešný rozchod |
| 2 | `KRONIKA-PROJEKTU.md:340` | `kontrol` tvrdí **39** — „3 PR prošla zeleným CI (39 kontrol, 0 selhání)" | **Datovaný záznam** z 2. 10. → patří mezi ZÁZNAMY. Dnes ho tam nezařadí, protože **nadpis §5 „Poučení" není v `ZNAKY_ODDILU`** — ale je to **tabulkový řádek**, kde `blok()` bere jen ten řádek a datum v něm není. **Pravidlo „tabulkový řádek = jen ten řádek" je správné, ale u kroniky (append-only) je moc úzké** — zvaž a změř |
| 3 | `KRONIKA-PROJEKTU.md:341` | `kontrol` tvrdí **0** — „`test-check-schema.py` **0 kontrol v sandboxu**" | ⚠ **Tohle je ZPRÁVA O STAVU, ne počitatelné číslo.** Je to **třetí stav** (`overovani` §7.13, „neproběhlo — prostředí"). **Musí se to zařadit jako záznam**, ne jako rozchod — a je to **nová třída**: *„číslo, které je 0 z důvodu NEZMĚŘENO"*. Zapiš ji do `overovani` |
| 4 | `PLAN-DALSI-KROK.md:135` | `bran` tvrdí **10** — „3 z 10 bran bez mutačního testu" | **Tenhle řádek je dnes NEPLATNÝ**, ne falešný: `audit6` hlásí **7** (G9). Opravit číslo **a přidat datum** (A2) |
| 5 | `PLAN-DALSI-KROK.md:175` | `dokumentů` tvrdí **57** — „ruční seznam 57 dokumentů" | ⚠ **Ten seznam UŽ NEEXISTUJE** (`kontrola-diakritiky.py` prochází složku — nález NA15). Řádek je **záznam o stavu před opravou** → označit datem, nebo přeformulovat |
| 6 | `PLAN-DALSI-KROK.md:104` | `omylů` tvrdí **75** — popis nálezu NA17 | **Historické číslo** → označit „ve svém čase správné" (A2). Dnes je 99 (`G4`) |
| 7–8 | `NEXT-SESSION-INSTRUKCE.md:16` a `:92` | `omylů` tvrdí **6** — „udělala 6 omylů", „5 z 6 omylů" | ⚠ **NENÍ to rozchod o celkovém počtu** — je to **počet omylů JEDNÉ session**. Stejná třída jako `kontrol`: **jeden název, dva čítače.** Buď pravidlo („N omylů" je vždy celkem), nebo nový zdroj `omylů:<session>`. **Změř a rozhodni** |
| 9 | `OTEVRENA-TEMATA.md:128` | `kontrol` tvrdí **40** — „Tarifní logika indikátoru + test — 40 kontrol" | Čítač **jiného projektu** (bundle tarifního indikátoru), ne brány tohohle workspace. **Buď zaregistrovat, nebo přiznat mezeru** |

**Hotovo znamená:** `audit2b` → **rozchodů ≤ 6**, u každého zbylého **řádek + zdroj**;
a u **každého** ze čtyř rozhodnutí (1, 2, 3, 7–8) je v docstringu **napsáno, co nástroj
neumí** — ne zamlčeno.

### Úkol 2 — `KRONIKA-PROJEKTU.md` a `NEXT-SESSION-INSTRUKCE.md` mají zastaralá čísla

**Naměřeno (`G4`):** kronika §3 má po opravě **12 bloků / 99 omylů**, ale
**řádky o omylech 102–104** (blok `8l`) přibyly téhle session — zkontroluj, že
**§3 i §4** je mají, a že `NEXT-SESSION-INSTRUKCE.md` (který **NEPATŘÍ téhle
session**, ale má zastaralá čísla) je označený jako **zadání souběžné session**.

**Hotovo:** `kronika-kontrola.py` → `exit 0` a **žádný dokument nemluví o počtu
omylů bez data**.

### Úkol 3 — pět zbylých bran bez mutačního testu (`G9`: 7 → méně)

Zbývá (naměřeno `audit6-brany-mutace.py`): `C1: a3-kontrola` · `C1: důkaz selhání`
· `over-skilly` · `f2 over cooldown` · `deploy B1` · `validate-all (CELEK)` · `tsc`.
**Napiš aspoň dva** a zapiš, které zůstávají a proč (u `tsc` je odpověď „kompilátor —
mutace nedává smysl", u `validate-all` „agregátor, měří se jeho děti").

### Úkol 4 — opatření 3 (krytí tvrzení o `schema.sql`)

**Zadání `ZADANI-OPRAVA-MERIDEL.md` to žádalo v Úkolu 5b a NEBYLO to doděláno.**
`ag-over-cisla.py` čte **jen některé** řádky svého dokumentu; `audit2a-schema.py`
čte tvrzení v próze. **Dolož měřením**, která tvrzení o sloupcích zůstávají
**nekrytá oběma** nástroji, a napiš to do `AGENTS.md`.

**Hotovo:** existuje výpis „tvrzení o `schema.sql` / kryté `ag-over-cisla` /
kryté `audit2a` / **nekryté**" a u nekrytých je rozhodnutí (doplnit / zamítnout
s důvodem).

### Úkol 5 — tabulka pokrytí brány diakritiky

**Taky NEBYLO doděláno** (Úkol 6 předchozího zadání). Zapiš **měřenou mez**:
kolik dokumentů která brána **otevře**, které **ne**, a **čím je to kryté**
(`g1-diakritika-novych.py` je v `g3`). Zdůvodni, proč to dnes **není** vada S27.
**Naměřený vstup:** `kontrola-diakritiky.py` hlásí `celkem ke kontrole 333`.

**Hotovo:** v `HANDOFF.md` je tabulka „brána → kolik souborů otevřela → co
neotevřela" **s příkazem** u každého řádku.

---

## 4. HOTOVO ZNAMENÁ (měřitelné — celá session)

- [ ] **Úkol 1:** `audit2b` rozchodů **≤ 6**, každý se zdrojem; 4 rozhodnutí zapsaná v docstringu
- [ ] **Úkol 2:** `kronika-kontrola.py` → **`exit 0`**; žádné číslo o omylech bez data
- [ ] **Úkol 3:** bran bez důkazu **< 7**, každý nový test **s počtem** ve výstupu
- [ ] **Úkol 4:** výpis krytí/nekrytí pro `schema.sql` + rozhodnutí
- [ ] **Úkol 5:** tabulka pokrytí diakritiky **s příkazem**
- [ ] `python _analyza\s24-meridla-over.py` → **`exit 0`**
- [ ] `python _analyza\handoff-kontrola-uplnost.py` → **83/83**
- [ ] `python _analyza\kronika-kontrola.py` → **`exit 0`**
- [ ] `python _analyza\g1-diakritika-novych.py` → **`exit 0`**
- [ ] `python _analyza\audit1-inventar.py` → `bez hlavičky` **≤ 20**
- [ ] Nový/změněný dokument → **do seznamu v `kontrola-diakritiky.py`**
- [ ] `_analyza\_inventar.json` **přegenerovaný** (`python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json`)
- [ ] `HANDOFF.md` — nová sekce s výsledky, **vlastní omyly do §8**, nic nezmizelo
- [ ] `KRONIKA-PROJEKTU.md` — **řádek**; návrhy **NA17–NA23** rozhodnuté
- [ ] Před commitem/pushem **ukázáno `git status` + `git diff --stat`** a **čekáno**

---

## 5. CO NEDĚLAT

- **NEPŘEPISUJ `NEXT-SESSION-INSTRUKCE.md`** — patří souběžné session
  (hash `9c05c6b4…` se nezměnil; `mtime` se pohnul, ale to **není** změna obsahu).
  Zadání pro další session napiš do **nového souboru**.
- **NEPŘESOUVEJ `HANDOFF.md` §10–§22 do kroniky** (opatření 5) — je to
  **samostatná session C** s nejvyšším rizikem.
- **NEZAVÁDĚJ git pro kořen workspace** (opatření 8) — rozhodnutí uživatele.
- **NEMAŽ `_analyza\hlavicky-zaloha*`** ani `_analyza\_zaloha-*` — jsou to zálohy
  a mají se poznat **jako zálohy** (nález NA21).
- **NEPŘEPISUJ historická čísla** (A2) — rozdíl je **čas**, ne nepravda.
  `HANDOFF.md` a `KRONIKA-PROJEKTU.md` jsou **append-only**.
- **NEOPRAVUJ `validate-all`** kvůli `exit 1` — naměřeno: je to
  **neproběhlo (prostředí)**, třetí stav (`overovani` §7.13). Není to regrese.
- **NEDÁVEJ hlavičky zálohám** — naměřeno: `audit1-inventar.py` má **14**
  bez hlavičky a **všech 14 jsou zálohy/kopie/skilly**. To je **správný stav**.
- **NEPUSHUJ bez vyžádání** — nejdřív `git status` a `git diff --stat` a **čekej**.

---

## 6. NÁSTROJE, KTERÉ TA SESSION PŘIDALA (ať je nemusíš hledat)

| Soubor | Co dělá |
|---|---|
| `_analyza\_registr-bran.py` | **živě změří**, kolik kontrol hlásí která brána → `_registr-bran.json`. Bez něj `audit2b` u `kontrol` řekne `NEZMĚŘENO` |
| `_analyza\handoff-mutace.py` | mutační test brány úplnosti handoffu (fixtura, ne živý soubor) |
| `_analyza\over-dokumentaci-mutace.py` | mutační test `over-dokumentaci.py` (rozříznutý výraz) |
| `_analyza\b5-mutace.py` | mutační test `b5-over-tvrzeni.py` (přejmenovaný identifikátor) |
| `_analyza\hlavicky-dopln.py` | doplnění hlaviček (suchý běh i `--zapsat`) — **zálohuje kopií** |
| `_analyza\_s25-*.py` | sondy té session (doklady měření, **nemaž**) |
