
---

## 10. Sedmnáctá až dvacátá čtvrtá past — naměřené 2. 10. 2026 (audit dokumentace)

*Osm pastí níž vzniklo jedné session při **opravě měřidel podle auditu**
dokumentace. Pět z nich **přežilo první verzi opravy** a odhalil je až
**mutační test** — ne čtení kódu. Všechny mají stejný podpis jako předchozí
sekce: **měřidlo odpovídalo na jinou otázku, než jsem si myslel.***

### 10.1 BRÁNA MŮŽE ČÍST **CITACI** MÍSTO **TVRZENÍ** — a mít pravdu z jiného důvodu

**Naměřeno 2. 10. 2026.** `audit2a-schema.py` kontroloval počet sloupců schématu
vzorem `(\d+)\s+sloupc` (číslo + slovo „sloupců"). V `AGENTS.md` ale stojí:

```
`AGENTS.md` tvrdil u `conductor/schema.sql` **„32 sloupců"**, správně je
**39** — a schéma se přitom od 30. 9. **nezměnilo** …
```

Vzor zabral na **„32 sloupců"** — což je **citace dřívějšího chybného tvrzení**,
ne tvrzení o dnešku. Skutečné tvrzení (`správně je **39**`) vzoru **neuniklo
proto, že je špatné, ale protože u něj nestojí jednotka** — „39" a „sloupců"
nejsou vedle sebe.

| Co brána hlásila | Co to znamenalo |
|---|---|
| `AGENTS.md:62 tvrdí 32 → ROZCHOD` | čte **citaci**, ne tvrzení |
| `exit 1` | **správný výsledek ze špatného důvodu** |
| tvrzení „je 39, ne 40" | **vůbec se neměřilo** |

**Pravidlo: ptej se, KTERÝ výskyt vzor trefí — a jestli je to ten, kvůli
kterému brána existuje.** „Vzor něco našel" a „vzor našel to, co hledám" jsou
dvě různé věty. Pozná se to tak, že se u každého nálezu **vypíše kontext**
(85 znaků před a 45 za) — ne jen počet.

### 10.2 ČÍSLO BEZ JEDNOTKY JE PRO VZOR NEVIDITELNÉ → přidej tvrzení v PRÓZE

Důsledek 10.1: když dokument tvrdí hodnotu **větou** („správně je **39**",
„dnes **40**"), vzor vázaný na jednotku ji mine. Náprava, která se osvědčila —
hledat **dvěma vzory** a sloučit nálezy:

```python
VZOR_SLOVU  = re.compile(r"(\d+)\s+sloupc")            # „40 sloupců"
VZOR_TVRZENI = re.compile(r"(?:správně je|dnes|nyní|aktuálně|má)\s+\**(\d+)\**")
# …a tvrzení v próze ber jen na ŘÁDCÍCH, které o jednotce mluví

> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
radky_s_jednotkou = {s[:m.start()].count("\n") for m in VZOR_SLOVU.finditer(s)}
```

**Ověřeno mutačně:** 4 mutace, 4 chyceny — včetně té, kdy se do dokumentu vrátí
`39` **bez** značky času (to je přesně vada, kvůli které brána vznikla a kterou
předtím **nikdy neviděla**).

### 10.3 ZNAČKA ČASU SE PŘILEPÍ OD SOUSEDNÍHO TVRZENÍ

**Naměřeno 2. 10. 2026 — a je to nejcennější past téhle sekce, protože ji našel
až mutační test (M2), ne čtení kódu.** První verze hledala značku času
(„stav před…", „dříve") **kdekoliv v okně ±60 znaků**. V dokumentu ale stojí:

```
**„32 sloupců"**, správně je **39** (stav před B1; dnes **40**)
```

Číslo **32** dostalo značku „stav před" **od třicetidevítky** — a brána ho
vyhodnotila jako `[záznam]`. **Byla pak slepá přesně k tomu, co má hlídat.**

**Pravidlo: značka musí být k číslu PŘIPOJENÁ** — mezi číslem a značkou nesmí
být **jiné číslo**:

```python
po = text[j:j + 60]
for z in ZNAKY_CASU:
    k = po.find(z)
    if k >= 0 and not any(ch.isdigit() for ch in po[:k]):
        return z            # značka patří TOMUHLE číslu, ne sousedovi
```

### 10.4 „JE TO ZÁZNAM, NEBO TVRZENÍ?" — A JAK ŠIROKÉ OKNO POUŽÍT

Nález **R3** (stažený falešný nález o „21 granul"): `HANDOFF.md` je **append-only
záznam**, takže stará čísla v něm jsou **správně**. Rozhoduje **kontext**:

| Úroveň | Příklad |
|---|---|
| **řádek** | slova „tvrdil", „dříve", „bylo" |
| **nadpis oddílu** | `## 14. Provedeno 2. 10. 2026 …` ← **nejsilnější znak minulosti** |
| **blok výskytu** | datum o dva řádky výš, uvnitř téže odrážky |

**⚠ A tady je past, kterou jsem sám vyrobil:** první verze brala „blok" jako
**souvislý běh neprázdných řádků**. V `AGENTS.md` je oddíl „## Jak dokumentovat"
**jeden takový blok o 5 441 znacích se sedmi daty** — jediné datum kdekoli v něm
by tedy umlčelo **všechna** čísla oddílu, i skutečné tvrzení o dnešku.
Odhalil to mutační test, protože **vypisoval velikost okna** (5 441 znaků).

**Pravidla:**
1. **Vypisuj velikost okna**, které měřidlo použilo. Okno, jehož velikost
   nevidíš, se nedá posoudit.
2. **Okno zastav na začátku dalšího celku** (odrážka, tabulkový řádek, nadpis):
   ```python
   ZACATEK = re.compile(r"^\s*(?:[-*+]\s|\d+\.\s|\||#)")
   ```
3. **Tabulkový řádek ber jako okno JEN ten řádek** — tabulka v `HANDOFF.md` §8
   má stovky řádků a jediné datum v ní by umlčelo celou tabulku.
4. Zúžení okna **zvyšuje** pokrytí: 5 441 → 824 znaků vrátilo jeden rozchod
   zpátky (26 → 27). „Velkorysé okno" **není** opatrnost, je to slepota.

### 10.5 OVĚŘOVATEL MUSÍ MĚŘIT **TÝMŽ OKNEM** JAKO NÁSTROJ

Tatáž past jako §9.2, ale o vrstvu níž: **můj ověřovací skript** počítal blok
jako „souvislé neprázdné řádky" (5 441 znaků), kdežto **nástroj už používal
jednu odrážku** (824 znaků). Výpis ověřovatele tedy ukazoval **čísla z jiného
okna, než jaké se měřilo** — a vypadal přitom jako důkaz.

**Pravidlo: když ověřovatel reimplementuje logiku nástroje, musí to být
řádek po řádku táž logika** — a patří k tomu komentář „MUSÍ BÝT SHODNÉ S …".
Když se to nedá zaručit, je lepší **vytáhnout okno z nástroje** (import,
podproces s `--json`) než je opisovat.

### 10.6 MUTAČNÍ SKRIPT, KTERÝ SPADNE MEZI ZÁPISEM A NÁVRATEM, NECHÁ DOKUMENT ZMUTOVANÝ

**Naměřeno 2. 10. 2026 (těsně to minulo škodu).** Můj `audit2b-over.py` mutoval
`HANDOFF.md` (282 kB, append-only záznam) a spadl na **přehnaně přísném
assertu** — `assert "Provedeno 2. 10. 2026" not in zmut`. Tenhle řetězec je
v dokumentu **i v jiných oddílech** (§16, §21), takže assert spadl **na správné
mutaci**. Škoda nevznikla jen náhodou: assert byl **před** zápisem.

**Dvě pravidla, obě povinná:**
1. **Každou mutaci obal `try/finally`**, které soubor vrátí — i při výpadku
   uprostřed:
   ```python
   try:
       cil.write_text(zmut, encoding="utf-8", newline="")
       … spusť bránu …
   finally:
       cil.write_bytes(orig)
       assert cil.read_bytes() == orig, "soubor nevracen!"
   ```
2. **Assert o „podmínka přestala platit" musí být ZÚŽENÝ na měřenou jednotku**,
   ne na celý soubor: kontroluj **ten řádek / ten nadpis**, ne dokument:
   ```python
   h14 = [l for l in zmut.splitlines() if l.startswith("## 14.")]
   assert not DATUM_RE.search(h14[0]), "nadpis pořád nese znak minulosti!"
   ```

**A ještě jedna věc téhož druhu:** mutace, která **neodstraní všechny** znaky
minulosti z okna, nic nedokazuje. První verze M2 smazala **jedno** datum ze
dvou — výskyt se mezi rozchody nevrátil a vypadalo to jako vada brány.
**Před během assertuj, že měřená podmínka opravdu přestala platit** (§7.14).

### 10.7 NÁSTROJ UMÍ TISKNOUT **JINÝ ČÍTAČ, NEŽ JAK SE JMENUJE**

**Naměřeno 2. 10. 2026.** `ag-mutace.py` měl vzor se **třemi číselnými
skupinami** a tisknul `m.group(2)` pod popiskem **„historických"** — jenže
`group(2)` bylo **`ROZEŠLO SE`**. Výstup tedy tvrdil
`5 v pořádku + 0 historických`, ačkoli historická byla **2**.

**A to číslo si vzal i audit do svého nálezu R5** — odtud se „0 historických"
šířilo dál jako fakt.

**Pravidlo: u výstupu s více čísly použij POJMENOVANÉ skupiny** — záměna pořadí
se pak nemůže zopakovat:

```python
m = re.search(r"v pořádku:\s*(?P<ok>\d+) \| historická[^|]*:\s*(?P<hist>\d+)"
              r" \| ROZEŠLO SE:\s*(?P<rozeslo>\d+)", vystup)
print(m.group("hist"))     # ne m.group(2)
```

**A obecně: popisek musí odpovídat čítači.** Je to táž vada jako „různé čítače
nesou stejné jméno", jen obráceně — **jeden čítač nese jiné jméno.**

### 10.8 BRÁNA, KTERÁ NIKDY NESKONČÍ NENULOVĚ, JE **PŘEHLED**, NE BRÁNA

**Naměřeno 2. 10. 2026.** `g3-brany.py` spouští 29 bran, vypisuje u každé
`exit=` a `otevřela:`, spočítá `s bránou s nenulovým exit: N` — a **nemá
`sys.exit`**. Vždy skončí `exit 0`.

**Důsledek, který se nesmí splést:** přidat test do jeho seznamu `BRANY`
znamená, že se jeho stav **objeví v přehledu** — **ne** že něco spadne.
„Nikdo to nevidí" se tím zlepší, „automat to zastaví" **ne**.

**A je to tak správně:** dva jeho řádky končí nenulově **oprávněně**
(`mutace A: pres-level` je červená správně, `validate-all (CELEK)` je
„neproběhlo — prostředí"). Brána, která by na ně padala, by **neměla jak
nespadnout** — tedy taky nic nehlídá. Kdyby se měl `g3` stát blokujícím,
musel by znát **baseline očekávaných nenulových exitů**, ne jen jejich počet.

### 10.9 `Get-Content | Measure-Object -Line` PODPOČÍTÁ **PRÁZDNÉ ŘÁDKY**

Tatáž past jako `git show | Measure-Object -Line` (kap. 1), ale jinde:
`Measure-Object -Line` nad **polem řádků** nepočítá **prázdné** řetězce.

| Měření | Výsledek |
|---|---|
| `(Get-Content _analyza\AUDIT-DOKUMENTACE.md \| Measure-Object -Line).Lines` | **513** |
| skutečnost (`len(splitlines())`) | **651** |

Rozdíl **138 řádků** = počet prázdných řádků. Vypadá to jako „dokument má
513 řádků" a přitom v něm `grep` najde řádek 617.

**Pravidlo: počet řádků se čte v Pythonu** (`len(text.splitlines())`), ne
z PowerShellu. A když už PowerShell, tak `(Get-Content x).Count` — to prázdné
řádky počítá.
