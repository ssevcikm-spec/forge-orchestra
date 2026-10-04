# -*- coding: utf-8 -*-
r"""Doplní `KRONIKA-PROJEKTU.md` o session #17 a o nálezy/omyly/návrhy z ní.

CO SE DOPLŇUJE (kronika se NIKDY nepřepisuje, jen přidává):
  1. řádek session **#17** do přehledové tabulky §1,
  2. nálezy **H14–H17** do §2.2 + rozšíření rozsahu v tabulce předpon,
  3. přepočítané počty omylů v §3 (nový blok **8h**, celkem **74**),
  4. nová poučení **L15–L17** do §4,
  5. **ROZHODNUTÍ** návrhů NA13–NA16 v §5 (druhá session rozhoduje, ne autor),
  6. přečíslování sekcí §3–§7 → §4–§8 (vkládá se nová sekce „Počty omylů").

PROČ SKRIPTEM A S TEXTY V SOUBORECH: český text v Python literálu uvnitř
shellového příkazu se v tomhle projektu už mnohokrát rozbil (past
`dsh-prostredi` §3d). Tady jsou literály PŘÍMO v `.py` souboru (ne v `-c`),
takže je to bezpečné — a každá náhrada má `assert`, že se provedla.

Použití:  python _analyza\k21-kronika.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
ZALOHA = WS / "_analyza" / "kronika-pred-k21.md"
ZAPIS = "--zapis" in sys.argv

text = KRONIKA.read_text(encoding="utf-8")
puvodni = text


def nahrad(stary: str, novy: str, popis: str, kolik: int = 1) -> None:
    """Dosadí text a OVĚŘÍ, že se to provedlo (past `overovani` §7.9).

    Pozor na kritérium: u VKLÁDÁNÍ text se `stary` v souboru po náhradě klidně
    objeví dál (vkládaný text ho obsahuje) — takže „zmizel vzor" NENÍ správná
    kontrola. Správná je **změna počtu výskytů**: musí stoupnout přesně o `kolik`.
    """
    global text
    pred = text.count(stary)
    assert pred == kolik, "%s: vzor je v souboru %dx, čekal jsem %dx" % (popis, pred, kolik)
    novy_text = text.replace(stary, novy, kolik)
    assert novy_text != text, "%s: NÁHRADA NEPROBĚHLA" % popis
    po = novy_text.count(stary)
    assert po == pred - kolik + novy.count(stary), \
        "%s: počet výskytů nesedí (%d -> %d, čekal jsem %d)" % (popis, pred, po, pred - kolik + novy.count(stary))
    text = novy_text
    print("  OK  %s" % popis)


# ---------------------------------------------------------------- přečíslování
# Vkládá se nová sekce „Počty omylů" jako §3, takže dosavadní §3–§7 jdou o jedna
# výš. Dělá se to ODZADU, aby se nepřepsaly dřív, než se na ně hledá.
print("PŘEČÍSLOVÁNÍ SEKCÍ (odzadu):")
nahrad("## 7. Jak kroniku udržovat", "## 8. Jak kroniku udržovat", "§7 -> §8")
nahrad("## 6. Kam se zapisuje co", "## 7. Kam se zapisuje co", "§6 -> §7")
nahrad("## 5. Návrhy na zlepšení", "## 6. Návrhy na zlepšení", "§5 -> §6")
nahrad("## 4. Poučení (lessons learned)", "## 5. Poučení (lessons learned)", "§4 -> §5")
# Pozor: „## 3. Evidence omylů" se přejmenovává, ne jen čísluje — část A brány
# čte PRÁVĚ TENHLE nadpis jako kotvu konce tabulky omylů.
nahrad("## 3. Evidence omylů — nejcennější část kroniky",
       "## 4. Evidence omylů — nejcennější část kroniky", "§3 -> §4 (evidence omylů)")

# -------------------------------------------------------- 1) nová sekce Počty
NOVA_SEKCE = """## 3. Počty omylů — jediné místo, kde je vidět TREND

**Proč to tu je zvlášť:** `AGENTS.md` říká *„počítej, že i tvoje první číslo bude
někde mimo."* Tahle sekce to **dokládá čísly** — a je to jediné místo, kde je
vidět, **jestli se podíl vad měřidla zlepšuje**.

| Co | Naměřeno | Odkud |
|---|---|---|
| **omylů celkem** | **74** | `python _analyza\\kronika-kontrola.py` — počítá řádky tabulek omylů v `HANDOFF.md` §8, 8b–8h |
| **z toho vad MĚŘIDLA** | **58 = 78 %** | ruční klasifikace u každého omylu (sloupec „Jak to vzniklo") |
| **z toho vypadalo jako nález o CIZÍM kódu** | **31** | tamtéž |
| **bloků omylů** | **8** (1–13, 8b–8h) | tamtéž |

> **⚠ POČTY SE POČÍTAJÍ, NEODHADUJÍ.** Naměřeno 2. 10. 2026 (omyl **60**):
> první verze tabulky níž měla u bloků **8d** a **8e** čísla **5** a **10** —
> byla to **špatná čísla**, protože je session napsala **odhadem z přečteného
> textu**. Odhalila to až **kontrola kroniky**, ne pozornost. Nástroj na
> přepočet: `python _analyza\\s18-prepocitej-omyly.py --zapis`.

**Podrobná tabulka po blocích** (číslování bloků odpovídá `HANDOFF.md` §8, 8b–8h):

| Blok | Session | Počet | Z toho vad MĚŘIDLA | Z toho vypadalo jako nález o CIZÍM kódu |
|---|---|---|---|---|
| 1–13 | 30. 9. – 1. 10. | 13 | **9** | — |
| **8b** | ověřovací 1. 10. | **10** | **6** | **5** |
| **8c** | akční 2. 10. 11:3x | **5** | **4** | **2** |
| **8d** | plánovací 2. 10. 10:1x | **6** | **5** | **2** |
| **8e** | akční 2. 10. 11:0x | **11** | **9** | **5** |
| **8f** | plánovací 2. 10. 12:1x | **10** | **9** | **4** |
| **8g** | plánovací 2. 10. 13:0x | **11** | **8** | **3** |
| **8h** | akční 2. 10. 16:1x | **8** | **8** | **4** |
| **celkem** | | **74** | **58 = 78 %** | **31** |

> **⚠ TREND, KTERÝ JE VIDĚT A JE NEPŘÍJEMNÝ:** podíl omylů **v měřidle**
> **neklesá** — drží se kolem **80 %**, a blok **8h** má dokonce **8 z 8**
> (100 %). To **není** náhodný šum: znamená to, že **nejrizikovější část práce
> není „napsat opravu", ale „změřit, že oprava funguje"**. A že se to
> **opakuje i po 74 zaznamenaných omylech** — tedy že **znalost pasti sama
> nestačí** (nejlépe to dokládají omyly 72–74: **tři kola** hledání správného
> kritéria na jednom souboru).
>
> **Co z toho plyne pro proces:** investovat do **měřidel**, ne do varování.
> Konkrétně: každá brána má mít **mutační test**, každé porovnání **hash**,
> každá mutace **`assert`, že se provedla**.

**Tři nejdražší omyly celého projektu** (každý stál data nebo falešný nález):

| # | Co se stalo | Cena |
|---|---|---|
| **14 souborů** (1. 10.) | „Oprava" podle `Target` u hardlinku → junctiony místo souborů | obnoveno **jen z karantény**; pravidlo do skillu |
| **omyl 50** (2. 10.) | Úkol B aplikován **jen do pracovního stromu**, hlášen jako hotový | málem se ztratila celá práce; zachránil ji **assert v runneru**, ne pozornost |
| **omyl 51** (2. 10.) | Vzor `.has(` bez kontextu → „kód má Godot 3 API" | málem „oprava" **správného** `combat.gd`; chytilo se to **dřív, než se zapsalo** |

---

"""

nahrad("## 4. Evidence omylů", NOVA_SEKCE + "## 4. Evidence omylů", "vložena nová sekce §3 Počty omylů")

# ------------------------------------------- 2) nová stará tabulka omylů v §4
STARA_TABULKA = """| Blok | Session | Počet | Z toho vad MĚŘIDLA | Z toho vypadalo jako nález o CIZÍM kódu |
|---|---|---|---|---|
| 1–13 | 30. 9. – 1. 10. | 13 | **9** | — |
| **8b** | ověřovací 1. 10. | **10** | **6** | **5** |
| **8c** | akční 2. 10. 11:3x | **5** | **4** | **2** |
| **8d** | plánovací 2. 10. 10:1x | **6** | **5** | **2** |
| **8e** | akční 2. 10. 11:0x | **11** | **9** | **5** |
| **8f** | plánovací 2. 10. 12:1x | **10** | **9** | **4** |
| **8g** | plánovací 2. 10. 13:0x | **11** | **8** | **3** |
| **celkem** | | **66** | **50 = 76 %** | — |

"""
NAHRADA_TABULKA = """> **⚠ Proč je tabulka s počty omylů ve zvláštní sekci §3:**
> je to **jediné místo, které se musí přepočítat po KAŽDÉ session**, a když
> leželo tady uprostřed, snadno se zapomnělo. Počítá ho nástroj, ne člověk.

> **⚠ PŘESNOST TOHOHLE ČÍSLA — a proč je to poučení samo o sobě:**
> první verze kroniky tvrdila u **8d „5"** a u **8e „10"**. Bylo to **špatně**
> (správně **6** a **11**) a **odhalila to až kontrola kroniky**
> (`_analyza\\kronika-kontrola.py`), ne moje pozornost — čísla jsem napsal
> **odhadem z přečteného textu**, místo abych je **spočítal**.
> Je to **omyl č. 60** (viz `HANDOFF.md` §8f) a je to **tentýž vzor** jako
> všechno ostatní v týhle tabulce: **vada měření, ne nález o projektu.**

"""
nahrad(STARA_TABULKA, NAHRADA_TABULKA, "§4: tabulka počtů přesunuta do §3")

# --------------------------------------------------------- 3) řádek session 17
RADEK_17 = """| **17** | 2. 10. 2026 16:1x | **akční** | **Granule `tests.harness`** (rozhodnutí uživatele) + lék na **H12**: atrapa v rozporu → **M3 chycena**; ruční seznamy nahrazeny **projitím složky**; úklid worktree | M3 s vrácenou vadou: **65/2** (dřív **nechycena**); projití složky **405 souborů** (dřív 127 ze seznamu); skilly **12 z 12** (dřív 5); roadmapa **22 granul**, lint beze změny (**14 problémů**) | **72–79** |

"""
nahrad("**Jak číst tabulku:**", RADEK_17 + "**Jak číst tabulku:**", "řádek session #17 do §1")

# ------------------------------------------------- 4) nálezy H14–H17 do §2.2
NALEZY = """| **H14** | **Dvě brány měly v docstringu DOSLOVNOU ukázku rozbitého kódování** — a `AGENTS.md` to zakazuje (pravidlo vzniklo právě kvůli tomu). `oprav-ps1-kodovani.py` ji měl v hlášce, `over-dokumentaci.py` v docstringu | **OPRAVENO** — ukázky popsané **slovem** („z jednoho písmene s diakritikou se stanou dva znaky"). Našlo to **projití složky** v `g1-diakritika-novych.py` | hotovo |
| **H15** | **Brána diakritiky kontrolovala 5 z 12 skillů** — ruční seznam cest. Chyběl i `overovani`, do kterého táž session psala | **OPRAVENO** — skilly se procházejí (`~/.dsh/skills/*/SKILL.md`); **naměřeno 12 na disku = 12 otevřených** | hotovo |
| **H16** | **Mutační test kroniky neměl fixturu s tabulkou NÁLEZŮ** — testoval jen živý dokument, a ten ten tvar v době testu neměl → vada (54 omylů místo 10) **prošla testem** | **OPRAVENO** — `_analyza\\t3-kronika-mutace.py`: fixtura má obě tabulky, **6 případů** (2 kontrolní + 3 vady + tvar); navíc našel **dvě další vady brány** (viz H17) | hotovo |
| **H17** | **`kronika-kontrola.py` měřila NULU tam, kde neměřila nic:** chybějící nadpis bloku → `blok()` vrátí `""` → `pocet_omylu("")` vrátí **0**, a to se vypsalo jako „skutečný počet omylů: 0". A blok, který v kronice **řádek nemá**, se tiše přeskakoval (`continue`) | **OPRAVENO** — tři stavy: chybějící **nadpis** i **koncová kotva** = `NEZMĚŘENO`; blok v `HANDOFF.md`, který v kronice chybí, je **ROZCHOD**. `%d` na `None` už neshazuje bránu tracebackem | hotovo |
"""
nahrad("| **H13** | **`providers.json` má o Groqu číslo",
       NALEZY + "| **H13** | **`providers.json` má o Groqu číslo", "nálezy H14–H17 do §2.2")
nahrad("### 2.2 Nálezy H8–H12 (z ověření práce `df1cbb23` — druhé kolo, 2. 10. 13:xx)",
       "### 2.2 Nálezy H8–H17 (z ověřování 2. 10., dvě kola: 13:xx a 16:xx)",
       "nadpis §2.2: rozsah H8–H17")
nahrad("| **H8–H12** | nálezy dalšího kola ověřování (2. 10. 13:xx) | `HANDOFF.md` **§18.11** | H8 **opraveno**, H9–H12 **otevřené / zpřesněné** |",
       "| **H8–H17** | nálezy dalších kol ověřování a provádění (2. 10. 13:xx a 16:xx) | `HANDOFF.md` **§18.11** a **§21** | H8, **H12, H14–H17 opraveny**; H9, H11, H13 **uzavřeny**; H10 **otevřeno** (blokuje NA14) |",
       "tabulka předpon: rozsah H8–H17")

# ------------------------------------------------------- 5) poučení L15–L17
print()
print("DOPLNĚNÍ POUČENÍ A NÁVRHŮ:")
POUCENI = """| **L15** | **Nula a „nezměřeno" nejsou úspěch — a v bráně to musí být VIDĚT** | naměřeno 2. 10. 2026 (omyl **78**, nález **H17**): `kronika-kontrola.py` vypsala u bloku bez nadpisu „skutečný počet omylů: **0**" — tedy **naměřenou nulu**. Přitom neměřila nic; a protože kronika tvrdila 6, rozdíl vypadal jako **nález o datech**. Druhá polovina téhož: blok, který v kronice **řádek nemá**, se tiše přeskakoval (`continue`) — a ne zapsaný omyl se ztratí navždy. **Opraveno:** chybějící nadpis i koncová kotva = `NEZMĚŘENO`, chybějící řádek v kronice = **ROZCHOD** | `HANDOFF.md` §21.4, `_analyza\\kronika-kontrola.py` |
| **L16** | **Když brána sama obsahuje VZOREK hledané vady, musí se odlišit VÝZNAMEM, ne TVAREM** | naměřeno 2. 10. 2026 (omyl **72–74**): projití složky ohlásilo rozbitou diakritiku ve **třech správných branách** — ty mají vzorek rozbitých znaků **jako literál** (musí, jinak by neměly co hledat). Kritérium „dva znaky po sobě" selhalo (hlásilo i hlášku ve správném souboru) a půlparser `bez_komentaru()` selhal na **jednoznakových uvozovkách** (uvozovka u jednoho znaku je sama literál, takže se spárovaly špatně). Opravilo to až **významové** kritérium: rozbité znaky smí být jen na řádku, který vzorek **definuje nebo používá**. **Čtvrtá variace téže pasti** jako `overovani` §8.3 | `overovani` §8.3, `_analyza\\g1-diakritika-novych.py` |
| **L17** | **Mutační test bez fixtury ve TVARU, který vadu způsobil, je slepý** | naměřeno 2. 10. 2026 (nález **H16**): `h17-kronika-mutace.py` testoval bránu **jen na živé kronice**, a ta v době testu neměla ve výřezu **tabulku nálezů** → vada (54 omylů místo 10) **testem prošla** a projevila se až v praxi. Fixtura, která ten tvar vyrobí **řízeně** (`t3-kronika-mutace.py`), našla **dvě další vady brány** (H17). **Obecně: test na živém dokumentu měří dnešní podobu dokumentu, ne odolnost brány** | `HANDOFF.md` §21.4, `_analyza\\t3-kronika-mutace.py` |
"""
nahrad("| **L14** | **Filtr, který dostane KRÁTKÝ sha", POUCENI + "| **L14** | **Filtr, který dostane KRÁTKÝ sha",
       "poučení L15–L17 do §5")

# ------------------------------------------- 6) ROZHODNUTÍ návrhů NA13–NA16
ROZHODNUTI = """| **NA13** | **Přidat do conductora endpoint na změnu stavu úlohy** (`POST /task/state`) | §16.7 + §18.10: výčet endpointů z kódu i z živého rozcestníku — `pause`/`block task` tam **není** | **`ZAMÍTNUTO`** — **3. 10. 2026 (akční session).** Důvod **není** „nejde to", ale **„už to není potřeba"**: jediný konkrétní důvod pozastavení (**#146**) **zanikl** — Úkol A ten test opravil a opravený test projde i bez `move()` (naměřeno **64/0**, dnes **65/0**), takže **není co pozastavovat**. Zavádět do živého conductora **nový stavový endpoint** bez jediného případu použití by bylo **riziko bez užitku** (`PLAN-DALSI-KROK.md` §4 zákaz č. 6). **Kdyby vyvstal konkrétní případ, návrh se vrací** — naměřená fakta (které endpointy nejsou a co dělají ty stávající) zůstávají v §18.10 | akční session 2. 10. 2026 |
| **NA14** | **Doplnit do `providers.json` změřené TPM limity** | H10: v `providers.json` **žádné TPM není**; jediné změřené (Groq 8 000) je z logu běhu | **`ODLOŽENO` — a je to ZÁVAZNÉ, ne dobrovolné.** Dva důvody, každý měřený: (1) **Doplnit se dnes dá JEDINÉ Groqovo číslo** — u mistralu, cerebrasu, gemini a openrouteru **TPM nikdo nezměřil** a v repu není (§18.12, „co se ověřit NEDALO"); doplnit `?` do živého konfigurace by znamenalo **zapsat nezměřené jako změřené**. (2) **`providers.json` je konfigurace conductora** a uživatel 2. 10. 2026 rozhodl, že se **nemění** („Groq ODLOŽEN", `HANDOFF.md` §20). **Návrh platí, ale je zablokovaný měřením, ne rozhodnutím** — otevře se spolu s NA16, až bude potřeba | akční session 2. 10. 2026 |
| **NA15** | **Nahradit ruční seznam v `kronika-kontrola.py` / `kontrola-diakritiky.py` za projití složky** a **zavést pro ně mutační test s fixturou, ve které je i tabulka nálezů** | §18.15: kontrola kroniky minula **dvakrát** (54 místo 10) a tři opravy téhož selhaly (dvě vrátily **0 omylů**) | **`APLIKOVÁNO`** — **3. 10. 2026 (akční session), celé:** (1) `g1-diakritika-novych.py` **prochází složku** — seznam **190 cest zrušen**, naměřeno **405 souborů, 5 binárních přeskočeno (vypsáno), vad 0**; (2) `kontrola-diakritiky.py` **prochází `~/.dsh/skills/*/SKILL.md`** — **12 z 12** (dřív 5 ručních, chyběl i `overovani`); (3) nový **`_analyza\\t3-kronika-mutace.py`** — fixtura s **tabulkou nálezů** i **tabulkou omylů**, **6 případů** (2 kontrolní + 3 vady + kritérium tvaru), `exit 0`. **A našel dvě další vady brány (H17).** Cena: **tři kola** hledání správného kritéria (omyly 72–74) | akční session 2. 10. 2026 |
"""
nahrad("| **NA13** | **Přidat do conductora endpoint", ROZHODNUTI + "| **NA13** | **Přidat do conductora endpoint",
       "rozhodnutí NA13–NA15 vložena PŘED původní řádky (staré se pak smažou)")

# Původní řádky NA13–NA15 měly stav `NEOVĚŘENO` a `—` u „Rozhodl". Nahrazují
# se CELÉ (jinak by v tabulce zůstaly dva řádky téhož návrhu — jeden rozhodnutý
# a jeden čekající, což je horší než žádný). **Nic se nemaže:** zdroj i naměřený
# důvod jsou v nových řádcích výš, jen s verdiktem.
STARE_NA = [
    '| **NA13** | **Přidat do conductora endpoint na změnu stavu úlohy** (`POST /task/state`), aby „pozastav úlohu" byl proveditelný úkon | §16.7 + §18.10: **výčet endpointů z kódu i z živého rozcestníku** — `pause`/`block task` tam **není**; `/tasks/cleanup` maže jen osiřelé a `/roadmap/reset` smaže cache celé hry (vynuluje i `attempts` u #142) | `NEOVĚŘENO` | — |\n',
    '| **NA14** | **Doplnit do `providers.json` změřené TPM limity** (dnes tam nejsou žádné) | H10: zadání chtělo „porovnej s limity v `providers.json`" a **ten je nemá**; jediné změřené TPM (Groq 8 000) je z logu běhu | `NEOVĚŘENO` | — |\n',
    '| **NA15** | **Nahradit ruční seznam v `kronika-kontrola.py` / `kontrola-diakritiky.py` za projití složky** a **zavést pro ně mutační test s fixturou, ve které je i tabulka nálezů (řádky začínající `H`)** | §18.15: kontrola kroniky dnes **minula dvakrát** (blok `8f` počítal **54 místo 10**, protože chytala tabulku nálezů z §18.11) a **tři opravy téhož selhaly** — poslední dvě vrátily **0 omylů**, protože buňky tabulky obsahují znak svislítka **uvnitř kódu** (řádek omylu 50 jich má 5) | `NEOVĚŘENO` | — |\n',
]
for stary in STARE_NA:
    assert stary in text, "původní řádek návrhu se nenašel: %s" % stary[:60]
    text = text.replace(stary, "", 1)
print("  OK  původní řádky NA13–NA15 nahrazeny rozhodnutými (nic se neztratilo)")

# NA16 zůstává `ODLOŽENO` — uživatel rozhodl; jen se k němu doplní, že to
# potvrdila i tahle session (a že se na něm nic nedělalo).
nahrad("| `ODLOŽENO` (rozhodl uživatel) | uživatel |",
       "| `ODLOŽENO` (rozhodl uživatel) | uživatel — **potvrzeno 2. 10. 2026 i akční session: s Groqem se NEDĚLALO NIC** (neměnil se `CONVENTIONS.md` ani `agent.yml`, Groq zůstal v rotaci) |",
       "NA16: potvrzeno, že se s tím nic nedělalo")

KRONIKA.write_text(text, encoding="utf-8")
print("PŘED: %d B, %d řádků" % (len(puvodni.encode("utf-8")), len(puvodni.splitlines())))
print("PO:   %d B, %d řádků" % (len(text.encode("utf-8")), len(text.splitlines())))
for k in ("## 3. Počty omylů", "## 4. Evidence omylů", "| **H14** |", "| **H17** |", "| **17** | 2. 10. 2026 16:1x"):
    print("  kotva %-40s %dx" % (k, text.count(k)))

if ZAPIS:
    ZALOHA.write_bytes(puvodni.encode("utf-8"))
    print("  záloha: %s" % ZALOHA.name)
    zpet = KRONIKA.read_text(encoding="utf-8")
    assert zpet == text, "zapsaný obsah nesedí"
    print("  ZAPSÁNO a ověřeno čtením z disku.")
else:
    KRONIKA.write_bytes(puvodni.encode("utf-8"))   # vrátit (dry-run)
    print("  (dry-run — soubor vrácen do původního stavu; spusť s --zapis)")
