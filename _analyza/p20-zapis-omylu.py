# -*- coding: utf-8 -*-
r"""P20 — PŘÍPRAVA ZÁZNAMU: soupis omylů téhle session (podklad pro HANDOFF §8z).

PROČ ZVLÁŠŤ: blok omylů se čte `kronika-kontrola.py` (hledá nadpisy v dokumentu)
a `handoff-kontrola-uplnost.py`; počet omylů v součtu musí odpovídat tomu, co je
v HANDOFF.mdskutečně napsané. Ruční přepisování čísel je přesně to, co v projektu
už dvakrát selhalo (H74: souhrnný řádek zůstal zastaralý o 3 bloky).

Tenhle skript je ZDROJ PRAVDY pro ten seznam: vypíše omyly a jejich počet, aby
se do dokumentu opsalo ČÍSLO, ne dojem.

Použití: python _analyza/p20-zapis-omylu.py
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ⚠ KAŽDÝ OMYL MUSÍ MÍT: co se stalo, jak se to poznalo a co to způsobilo.
# Bez „jak se to poznalo“ je to historka, ne záznam.
OMYLY = [
    ("195",
     "Do měřidla jsem napsal PŘEDPOKLAD místo měření: `zk(chyba_ast is None, "
     "„ast.parse BOM PŘIJME“)`. Ve skutečnosti `ast.parse()` BOM **ODMÍTNE** "
     "stejně jako `compile()` — obě jdou přes týž tokenizér.",
     "Spadla mi vlastní kontrola ve `p20-b-bom-mereni.py` (1 chyba z 9).",
     "Kdybych ji nechal projít (nebo ji „opravil“ podle předpokladu), zapsal "
     "bych do projektu NEPRAVDU o chování Pythonu — a příští session by podle "
     "ní hledala rozdíl mezi branami NA32 a H79 na špatném místě."),

    ("196",
     "Kontrola, která NEMÁ JAK PROJÍT: `„*-scratch“ in zmineno`, kde `zmineno` "
     "byl SEZNAM (`[l for l in ... if ...]`). Test na prvek seznamu místo na "
     "podřetězec řádku.",
     "Výstup testu hlásil CHYBU u kontroly, která měla být zelená — a souhrn "
     "přitom `*-scratch 25/0` VYKAZOVAL.",
     "Je to táž třída jako „brána, která nemá jak selhat“ (S27), jen obráceně: "
     "kontrola, která nemá jak projít, vypadá jako nález o správném kódu."),

    ("197",
     "Fixturu jsem skládal v `python -c` uvnitř PowerShellu a ZPĚTNÝ APOSTROF "
     "je v PowerShellu ESCAPE znak — z `` `forge-orchestra` `` se stalo "
     "`orge-orchestra`.",
     "Brána `zadání kontrola` SPRÁVNĚ hlásila „zadání netvrdí žádný commit“ — "
     "a vypadalo to jako vada brány.",
     "Dvě kola jsem hledal vadu v bráně, která fungovala. Řešení je v pravidlech "
     "prostředí (`dsh-prostredi`): skript piš do SOUBORU, ne do `-c`."),

    ("198",
     "V RAW řetězci jsem escapoval zpětný apostrof: `r\"\\`\"`. Zpětný apostrof "
     "žádnou escape sekvenci NEMÁ, takže v řetězci zůstaly DVA znaky (lomítko "
     "a apostrof) a vzor hledal text, který v zadání není.",
     "`re.search` nenašel nic a nahrazení „prošlo“ jen zdánlivě (text se "
     "nezměnil). Odhalila to až kontrola, že se mutace SKUTEČNĚ provedla.",
     "Tichá nula: kdybych kontrolu mutace neměl, měřil bych ORIGINÁL a tvrdil, "
     "že měřím kopii."),

    ("199",
     "Fixturu jsem měnil jen na PRVNÍM výskytu kotvy na řádku — ale ten řádek "
     "nese i `origin/main` = **`19a2195`**. Vzniklo zadání s DVĚMA ROZCHÁZEJÍCÍMI "
     "SE TVRZENÍMI a brána správně varovala.",
     "Test hlásil „kotva = ŽIVÝ HEAD → exit 1“ místo očekávané 0.",
     "Opět bych „opravoval“ bránu, která měřila správně. Fixtura musí být CELÁ "
     "a vlastní, ne záplatovaná."),

    ("200",
     "V testu `g3` jsem fixturami nahradil CELÝ blok `BRANY`, ale deklaraci "
     "`OCEKAVANE_NENULOVE` s `zadání kontrola` jsem nechal — ta se tím stala "
     "VISUTOU a `g3` správně skončil `exit 1`.",
     "Zdravý stav hlásil `exit=1` a text viny byl „VISUTÉ záznamy“.",
     "`exit 1` ze špatného důvodu (`overovani` §10.1) — test by tvrdil, že měří "
     "něco jiného, než měřil. Opraveno v `p20-a-kontroly.py` i v obou dokladech P19."),

    ("201",
     "Do SVÉHO nového verdiktu nad červenými jsem započítal i brány, které jsou "
     "DEKLAROVANÉ jako „běžela bez čítače“ (`OCEKAVANE_BEZ_CITACE`) — `selhalo` "
     "je totiž KAŽDÝ nenulový exit.",
     "Odhalil to doklad P19 `p19-d-kontroly.py` (případ 4): deklarovaná brána "
     "správně vracela `exit 0`, ale `g3` padal.",
     "Vlastní vada v produkčním kódu — a našel ji STARŠÍ doklad, ne můj nový "
     "test. To je přesně důvod, proč se doklady nemažou."),

    ("202",
     "Jméno brány pro deklaraci jsem do dokladu OPSAL ručně místo abych ho vzal "
     "ze stejného literálu, který jde do `BRANY`.",
     "Deklarace tiše neseděla a `g3` hlásil totéž, jako by tam nebyla — dva "
     "řetězce vypadaly stejně a stejné nebyly.",
     "Strávil jsem tím dvě kola. Řešení: klíč se vytahuje PROGRAMOVĚ z téhož "
     "literálu a porovnává se po kódových bodech, ne očima."),

    ("203",
     "Do `.py` jsem málem zapsal úpravu přes `Set-Content -Encoding utf8` — "
     "tedy PŘESNĚ omyl 189 z P19 (přidá BOM a vyrobí „nekompilovatelný živý "
     "soubor“).",
     "Zastavil jsem se na tom, že zadání to výslovně zakazuje; zápis jsem "
     "provedl `edit` toolem.",
     "Je to omyl „v poslední chvíli“ — a je zapsaný proto, že pravidlo nebylo "
     "v hlavě, ale v zadání. To je jeho smysl."),

    ("204",
     "V `p20-d-doklady.py` jsem čítač kontrol četl vzorem, který neodpovídá "
     "formátu dokladů (`VÝSLEDEK: N kontrol, M chyb` vs. `VÝSLEDEK D: kontrol "
     "39, chyb 0`), takže sloupec „kontroly“ vyšel u všech jako `—`.",
     "Souhrn tvrdil „19 dokladů“ a u žádného neukázal číslo — což je nápadné, "
     "ale jen díky tomu, že tam sloupec je.",
     "Metrika, která tiše nic neměří, vypadá jako naměřená nula. Číslo kontroly "
     "se proto bere z POSLEDNÍHO výskytu kteréhokoli ze známých tvarů."),

    ("205",
     "Dočasnou sondu `p20-sonda-klicu.py` jsem musel dvakrát přepsat, protože "
     "jsem v ní POROVNÁVAL ŘETĚZCE OČIMA (`print(repr(...))` vedle sebe).",
     "Teprve výpis kódových bodů (`U+%04X`) ukázal, že klíče jsou SHODNÉ — a že "
     "vada je jinde (v `selhalo`).",
     "„Vypadá to stejně“ není měření. Porovnání řetězců patří programátorovi, "
     "ne oku."),

    ("206",
     "Do kroniky jsem vkládal řádek 34 s KOTVOU NA ŘÁDEK 33 — a ten se mi do "
     "kontextu načetl **ZKRÁCENÝ** (2000 znaků). Nahradil jsem tedy CELÝ řádek "
     "zkráceným textem a „vrácením“ do něj vložil DRUHÝ výskyt téhož (4286 → "
     "6149 znaků).",
     "Vlastní kontrola `git status` ukázala, že soubor je po dvou úspěšných "
     "editacích BEZ ZMĚNY — a `sha256` proti blobu v `HEAD` to potvrdil.",
     "**Táž třída jako P19 `194` a P18 `183`.** Oprava: řádek vzít **z blobu "
     "v `HEAD`** a vložit **programově** (`p20-oprav-kroniku.py`) — a to je "
     "poučení: **kotva nesmí být řádek delší, než se vejde do kontextu.**"),

    ("207",
     "V opravném skriptu jsem na řádek 33 sahal INDEXEM (`head_lines[32]`) podle "
     "„řádek 33 = session 33“.",
     "Assert uvnitř skriptu to zastavil: `head_lines[32]` byla **session 2**.",
     "**Číslo session NENÍ číslo řádku** — táž třída jako „různé čítače nesou "
     "stejné jméno“ (`dsh-prostredi` §5). Oprava: hledá se **podle OBSAHU**."),

    ("208",
     "V opravném skriptu jsem po vložení řádku porovnával `soucasne[i]` s `po[i]` "
     "a hlásil, že se změnilo **650 řádků**.",
     "Řádky nebyly změněné — byly **POSUNUTÉ** o vložený řádek; indexové srovnání "
     "je mimo o jedna.",
     "**Hromadné „poškození dokumentu“, které neexistuje** — a kdybych mu "
     "uvěřil, „opravoval“ bych zdravou kroniku. Oprava: srovnávat se SPRÁVNÝM "
     "posunem."),

    ("209",
     "Do dokladu `p20-a-kody-bran.py` jsem napsal kotvu zadání **NATVRDO** "
     "(`19a2195`).",
     "Když jsem zadání přepsal na nový živý `HEAD` (`b781c84`), doklad spadl "
     "**na správně aktualizovaném dokumentu**.",
     "**Táž třída jako H102** (doklad tvrdící zastaralé číslo). Oprava: kotva se "
     "**VYTAHUJE Z DOKUMENTU**, neopisuje."),

    ("210",
     "Po přepisu zadání jsem dokument opravil, ale **nezaregistroval, že se tím "
     "změnil i vstup dokladu** — a `p20-d-doklady.py` pak hlásil **2 červené** "
     "místo 1.",
     "Souhrn dokladů: `21 dokladů, 2 s nenulovým exit` — a druhý byl **můj "
     "vlastní**, ne H103.",
     "Doklad, který je závislý na STAVU dokumentu, **zastará s ním** — a to se "
     "musí čekat, ne „opravovat“ dokument zpátky."),
]

print("=" * 78)
print("P20 — omyly téhle session (podklad pro HANDOFF §8z a KRONIKU)")
print("=" * 78)
for c, co, jak, dopad in OMYLY:
    print(f"\n{c}. {co}")
    print(f"    Jak se to poznalo: {jak}")
    print(f"    Co to způsobilo:   {dopad}")

print("\n" + "=" * 78)
print(f"OMYLŮ CELKEM: {len(OMYLY)}")
print("=" * 78)
# Rozdělení podle toho, čeho se omyl týkal — do kroniky patří i tenhle rozpočet.
meridla = [c for c, co, _, _ in OMYLY if any(
    k in co.lower() for k in ("kontrol", "měřid", "vzor", "fixtur", "čítač",
                              "test", "deklarac", "porovn"))]
print(f"  z toho vad MĚŘIDLA (kontrola/test/fixtura/čítač): {len(meridla)} "
      f"→ {', '.join(meridla)}")
print(f"  z toho PŘEDPOKLAD místo měření: 195")
print(f"  z toho vad zápisu/prostředí:    197, 203")
sys.exit(0)
