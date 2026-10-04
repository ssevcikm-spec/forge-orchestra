
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
### 8e. Omyly AKČNÍ session 2. 10. 2026 (11:0x–12:0x UTC) — Úkoly A–D a B1

> **Devět z deseti** omylů vzniklo v **měřidle nebo ve mně**, ne v měřeném kódu —
> a **čtyři z nich vypadaly jako nález o cizím kódu**. Dva mě málem přivedly
> k „opravě" správné věci. **Plný popis s příkazy je v §16.8**; tady je tabulka
> ve stejném tvaru jako 8b–8d.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **40** | „Opravený test spadne, protože jsem ho blbě vložil" | **Patcher zapisoval literální `\t` místo tabulátoru** → Godot `Parse Error: Unexpected "extends" in class body`, testy **nedoběhly vůbec**. Nález o **patcheru**, ne o testu | GDScript bloky jsem měl v **Python literálech**; `\\t` v nich zůstalo dvěma znaky. Opraveno: bloky leží v `_analyza\*.gd` a čtou se **bajt na bajt** |
| **41** | „Kontrola se tiše přeskakuje" | **Přeskakovala se, ale ne tiše** — moje poznámka se **nevypisovala**, protože ji minul **filtr výpisu**, kterým jsem hledal. Chyba byla ve filtru | Hledal jsem v cizím výstupu podle vzoru a neověřil, že vzor odpovídá tomu, co jsem sám psal |
| **42** | „`move()` přes úroveň test nechytí" (podezření na slepou bránu) | **Chytí** — a **starý test taky** (`60 kontrol, 1 selhání`). Rozdíl je v tom, že starý hledá **text**, nový **chování** | Chtěl jsem dokázat, že nový test je lepší; pravda je, že **oba** tuhle vadu chytí a nový je lepší jen tím, že nezakazuje legitimní kód |
| **43** | „Po B1 je `test-cooldown` červený v opačném směru — přepíšu očekávání" | **Byla v něm i VADA FIXTURE:** `vloz()` plnil `naposledy_selhalo` přes `datetime('now', ?)`, jenže `?` je tam **argumentem funkce**, ne hodnotou sloupce → SQLite uložil **doslovný řetězec** `'-10 minutes'`, který se v `>` chová jako **0**. Scénář „v cooldownu" vycházel jako „má se vydat" a **vypadalo to jako vada guardu** | Do B1 se sloupec **nečetl**, takže vada fixture byla **neviditelná**. Odhalila ji až sonda `_analyza\f2-sonda-cooldown.py`, ne čtení testu |
| **44** | „`test-cooldown.py` je červený → B1 není hotové" | Test hlásil **2 chyby**: jedna byla ta fixture (43), druhá **skutečná** (guard v **dispatch smyčce**, který jsem opravil taky). **Nebyly to jeden problém, ale dva** | Spojil jsem „test je červený" s „oprava je špatná", místo abych si přečetl **které scénáře** a proč |
| **45** | „Registr `component()` v `game.gd` existuje" (převzato z promptu granule) | **Neexistuje** — `scripts/` ji **nikde nedeklaruje**, ale `hud.gd`, `mining.gd` a `save.gd` ji **volají**. Ověřil jsem to **až poté**, co jsem na tom postavil úvahu o „cestě přes `world`" | Vzal jsem tvrzení z **promptu granule** (popisuje cílový stav) jako popis **dneška** — přesně to, před čím varuje `AGENTS.md` |
| **46** | „V `_analyza\a-ukol-scratch` dám stejné testy jako v hlavním klonu" | **`57 kontrol, 3 selhání`** — v čerstvém `git worktree` **chybí `.godot/`** (je v `.gitignore`), takže se nenačtou assety. Vypadalo to jako **regrese kódu** | Neuvědomil jsem si, že import cache není v gitu. Řešení: zkopírovat `.godot` (574 souborů) → **59/0** |
| **47** | „Ve výpisu validátoru jsou dvě `CHYBA`, tedy dva problémy" | Souhrn hlásil **1 PROBLÉM** — jedna z těch dvou `CHYBA` je **očekávaný výstup běžícího testu** (scénář, který má být `False`) | Počítal jsem **řádky** ve výstupu místo **souhrnu**; táž past jako „různé čítače nesou stejné jméno" |
| **48** | „Mutace se provedla" (u ověření patcheru pro C2) | Patcher prošel, ale výsledný soubor měl **rozbitou českou uvozovku** (zavírací se zapsala jako ASCII) → `SyntaxError: '(' was never closed` na řádku, který vypadal správně | **Tatáž past, před kterou sám varuju** (skill `dsh-prostredi` §3d). Odhalil to až `ast.parse`; textová kontrola by ji minula |
| **49** | „Filtruju komentáře, takže komentář popisující vadu nezpůsobí falešný poplach" | Filtr `startswith('#')` **nestačí** — vada byla popsaná i v **docstringu**, a ten **není komentář**. Pojistka hlásila falešný poplach na **dokumentaci** | Znal jsem pravidlo „statická kontrola musí číst KÓD, ne komentáře" a implementoval ho **polovičně**. Opraveno přes `ast` |

**Vzor:** **devět z deseti** omylů vzniklo v **měřidle** (patcher, filtr, sonda,
fixture) — a **čtyři** vypadaly jako nález o cizím kódu (41 „tiše se
přeskakuje", 43 „guard je vadný", 46 „regrese kódu", 48 „Python neumí české
uvozovky"). Ani jeden z těch čtyř **nebyl** nález o cizím kódu.

**A jeden omyl, který se NEPOVEDLO napravit:** schválené **pozastavení úlohy
#146** jsem neprovedl, protože na to conductor **nemá endpoint** a do D1 se
odsud zapsat nedá (údaje k Cloudflare jsou v GitHub Secrets). Není to
opomenutí, je to **nález** — a je zapsaný v §16.7 i s rizikem, které z toho
plyne (worker si #146 vzal **před** opravou testu).

