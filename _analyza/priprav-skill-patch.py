"""Připraví záplaty skillů jako OVĚŘENÉ kopie ve workspace (needituje skilly).

Skilly leží mimo workspace (`C:\\Users\\Ssevc\\.dsh\\skills`) a sandbox tam zápis
odmítá i po eskalaci. Tenhle skript proto záplaty **neaplikuje naostro** —
vytvoří kopie v `_analyza\\patch\\` a tím doloží čtyři věci, které by jinak byly
jen tvrzení:

  1. každý anchor se v cílovém souboru vyskytuje **právě jednou** (jinak skončí),
  2. frontmatter zůstane **bajt na bajt** stejný (`description`/`whenToUse` se
     nesmí měnit) a `name` sedí na jméno složky,
  3. **konce řádků se zachovají** — `game-developer` je CRLF, `dsh-prostredi` LF;
     `read_text()` bez `newline=""` by CRLF tiše převedl na LF v celém souboru,
  4. kolik řádků se přidá a že v těle nic nezmizelo.

Výstup je tedy měřený, ne odhadnutý. Aplikaci naostro dělá až
`aplikuj-skill-patch.py` (spouští se s širším oprávněním).
"""

import hashlib
import pathlib
import re
import sys

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKILLS = pathlib.Path(r"C:\Users\Ssevc\.dsh\skills")
OUT = pathlib.Path(__file__).with_name("patch")
BOM = bytes([0xEF, 0xBB, 0xBF])

# ---------------------------------------------------------------------------
# ÚKOL A — game-developer: dvě nové pasti do sekce o kontraktech/ověřování
# ---------------------------------------------------------------------------

A_OLD = "## 4. Granule (atomická pracovní jednotka)"

A_NEW = """### Past: dvě jména téhož pole = tichá ztráta dat

**Naměřeno 1. 10. 2026 v projektu orchestra.** Šablona psala do konfiguračního
souboru klíč `popis_stylu`, ale kód `vision.mjs` četl **POUZE** `styl_popis`:

| Kdo | Jméno klíče |
|---|---|
| šablona (zápis) | `popis_stylu` |
| `vision.mjs` (čtení) | `styl_popis` |

Hra, která by použila nové jméno, by o svůj styl vizuální kontroly **tiše**
přišla — žádná chyba, žádné varování, jen kontroly, které běží bez stylu.
Rozdíl se neprojeví u zápisu, ale až u otázky „proč ta kontrola nefunguje?".

**Oprava:** kód čte **obě** jména (staré i nové) a **pro každé z nich existuje
test**. Obecné pravidlo:

> **Když měníš jméno klíče v konfiguraci, kód musí číst obě jména a pro každé
> musí existovat test** — jinak je přejmenování tichá ztráta dat.

**Navazující pravidlo: než z konfigurace něco SMAŽEŠ, najdi všechna místa, kde
se to čte.** Smazaný klíč, na který ještě někdo sahá, je tatáž tichá ztráta
z opačné strany — a hůř se hledá, protože po něm nezůstane ani stopa.

### Past: statická metrika, která nic nespustí, je slepá

**Naměřeno 1. 10. 2026.** Čtenář dokumentu chtěl ověřit tvrzení „testy 36/36"
a **staticky spočítal volání `test(` ve zdrojáku** → vyšlo **42**, tedy
„dokument lže". Po skutečném **SPUŠTĚNÍ** testů vyšlo **36/36** — dokument měl
pravdu do puntíku.

Počet testů nesedí na počet vzorů v souboru: testy se sdružují do skupin,
používají pomocné funkce a jiné názvy, než jaké vzor hledá.

| Metrika | Co naměřila | Závěr, který z toho plyne |
|---|---|---|
| spočítaná volání `test(` ve zdrojáku | **42** | „dokument lže" — špatný |
| výstup skutečného **běhu** testů | **36/36** | dokument měl pravdu |

> **Počet testů a výsledky se čtou z VÝSTUPU BĚHU, ne z počtu vzorů ve
> zdrojáku.**

Statická metrika je stejně slabá jako kontrola, která čte komentáře — a navíc
**svádí k „opravě" správného dokumentu**, což je horší než nic: správné číslo se
přepíše špatným a zmizí tím i důkaz.

**Platí to i pro ověřování cizích tvrzení.** Než něčí číslo označíš za
nepravdivé, **zopakuj ho TÝMŽ postupem, jakým vzniklo** — a když postup neznáš,
nemáš co vyvracet, jen jinou metriku, která odpovídá na jinou otázku.

## 4. Granule (atomická pracovní jednotka)"""

# ---------------------------------------------------------------------------
# ÚKOL B — dsh-prostredi
# ---------------------------------------------------------------------------

B1_OLD = """**Každý test musí mít assert i nenulový exit kód** — a ideálně **mutační test**
(vrať vadu a podívej se, že opravdu spadne).

## 2. Skripty padají na VLASTNÍM výstupu (cp1252)"""

B1_NEW = r"""**Každý test musí mít assert i nenulový exit kód** — a ideálně **mutační test**
(vrať vadu a podívej se, že opravdu spadne).

**A čtvrtá věc téhož druhu: `git show <soubor> | Measure-Object -Line`
NEDOPOČÍTÁ poslední řádek.** Naměřeno 1. 10. 2026: u `ci.yml` hlásil **166**
řádků, správně je **182** — protože soubor **nekončí newline**. Vypadá to jako
necommitnutá změna, která neexistuje (a `git diff` byl přitom **prázdný**, tedy
nic nechybělo).

| Měření | Výsledek |
|---|---|
| `git show HEAD:ci.yml \| Measure-Object -Line` | **166** — poslední řádek chybí |
| skutečný počet řádků souboru | **182** |
| `git diff` | **prázdný** — žádná necommitnutá změna |

**Autorita je `git diff` a velikost blobu** — ne přepočítaný výstup:

```powershell
git cat-file -s HEAD:ci.yml     # velikost blobu v commitu
(Get-Item ci.yml).Length        # velikost téhož souboru na disku
```

**Když se velikost blobu a velikost na disku rovnají, rozpor je vyřešený
okamžitě** — je to týž obsah a žádná změna nechybí. Počítat řádky znovu je jen
další metrika, která odpovídá na jinou otázku.

## 2. Skripty padají na VLASTNÍM výstupu (cp1252)"""

B2_OLD = r"""**Zdroj pravdy o repech a Pages:** `node orchestra\tools\zjisti-pages.mjs`
(GitHub API). Ptej se jeho, ne paměti ani dokumentace.

## 6. Godot hra bez editoru"""

B2_NEW = r"""**Zdroj pravdy o repech a Pages:** `node orchestra\tools\zjisti-pages.mjs`
(GitHub API). Ptej se jeho, ne paměti ani dokumentace.

### Různé čítače nesou stejné jméno

**Naměřeno 1. 10. 2026.** Dokument tvrdil „běhy #355–#362", ale `run_number`
v GitHub API ukazoval **#235–#241**. A totéž jinde: dokument psal „20 běhů
celkem", `total_count` v API hlásil **241**.

| Dokument | GitHub API | Co to je |
|---|---|---|
| „běhy #355–#362" | `run_number` = **#235–#241** | jiný čítač téhož jména |
| „20 běhů celkem" | `total_count` = **241** | jiný rozsah, jiný endpoint |

Nikdo nelhal — jen se sečetly **různé čítače, které se jmenují stejně** („běh").
Číslo bez endpointu se nedá ověřit ani vyvrátit.

**A přiřazení je taky tvrzení, které se ověřuje.** Dokument tvrdil, že
**„PR se sloučily samy"** (auto-merge). `merged_by` v GitHub API to **vyvrátil**
— sloučil je uživatel, ne automat.

**Pravidlo: u každého čísla o bězích/PR si napiš, ODKUD je (který endpoint)** —
a slova jako „samo", „automaticky" nebo „nikdo to nepotvrdil" ber jako tvrzení,
které se ověřuje (`merged_by`, `conclusion`, `event`), ne jako popis.

## 6. Godot hra bez editoru"""

B3_OLD = """5. **Není to jen falešný poplach po opravě?** (statická kontrola musí číst
   kód, ne komentáře)"""

B3_NEW = """5. **Není to jen falešný poplach po opravě?** (statická kontrola musí číst
   kód, ne komentáře)

### Dvě pasti při ověřování cizích čísel

1. **`Measure-Object -Line` nad `git show` nedopočítá poslední řádek** bez
   koncového newline (166 vs. 182) — autorita je `git diff` a velikost blobu
   (`git cat-file -s HEAD:<soubor>`).
2. **Různé čítače nesou stejné jméno** — „běh #355" proti `run_number` #241
   a „20 běhů" proti `total_count` 241; u každého čísla si napiš, ze kterého
   endpointu je."""

ZAPLATY = {
    "game-developer": [(A_OLD, A_NEW)],
    "dsh-prostredi": [(B1_OLD, B1_NEW), (B2_OLD, B2_NEW), (B3_OLD, B3_NEW)],
}

FM = re.compile(r"^---\n(.*?)\n---\n", re.S)


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def styl_koncu(blob: bytes) -> str:
    """Vrátí dominantní styl konců řádků v souboru ('\\r\\n' nebo '\\n')."""
    crlf = blob.count(b"\r\n")
    lf = blob.count(b"\n") - crlf
    return "\r\n" if crlf > lf else "\n"


def zaplat(blob: bytes, zmeny) -> bytes:
    """Aplikuje záplaty na bajty a vrátí nové bajty (konce řádků zachová)."""
    if blob[:3] == BOM:
        raise SystemExit("CHYBA: soubor má UTF-8 BOM, tenhle skript s ním nepočítá")
    styl = styl_koncu(blob)
    text = blob.decode("utf-8")

    for i, (stare, nove) in enumerate(zmeny, 1):
        stare_s = stare.replace("\n", styl)
        nove_s = nove.replace("\n", styl)
        pocet = text.count(stare_s)
        if pocet != 1:
            raise SystemExit(f"CHYBA: anchor {i} nalezen {pocet}x (musí být 1x)")
        text = text.replace(stare_s, nove_s, 1)

    novy = text.encode("utf-8")
    if styl_koncu(novy) != styl:
        raise SystemExit("CHYBA: změnil se styl konců řádků")
    # Do souboru nesmí přibýt ani jeden konec řádku OPAČNÉHO stylu.
    if styl == "\r\n":
        pred = blob.count(b"\n") - blob.count(b"\r\n")
        po = novy.count(b"\n") - novy.count(b"\r\n")
        if pred != po:
            raise SystemExit(f"CHYBA: do CRLF souboru přibylo {po - pred} LF konců")
    elif novy.count(b"\r\n") != blob.count(b"\r\n"):
        raise SystemExit("CHYBA: do LF souboru přibyly CRLF konce")
    return novy


def zkontroluj(jmeno: str, puvodni: bytes, novy: bytes) -> None:
    # Normalizace konců řádků je tady SCHVÁLNĚ: `read_text()` v over-skilly.py
    # i `yaml` pracují s `\n`. Kontrolu konců řádků dělá `zaplat()` nad bajty.
    t_p = puvodni.decode("utf-8").replace("\r\n", "\n")
    t_n = novy.decode("utf-8").replace("\r\n", "\n")
    fm_p = yaml.safe_load(FM.match(t_p).group(1))
    fm_n = yaml.safe_load(FM.match(t_n).group(1))

    if sha(FM.match(t_p).group(1)) != sha(FM.match(t_n).group(1)):
        raise SystemExit(f"CHYBA {jmeno}: frontmatter se změnil")
    if fm_n.get("name") != jmeno or fm_n.get("name") != fm_p.get("name"):
        raise SystemExit(f"CHYBA {jmeno}: name v frontmatteru nesedí")
    for klic in ("description", "whenToUse"):
        if fm_n.get(klic) != fm_p.get(klic):
            raise SystemExit(f"CHYBA {jmeno}: {klic} se změnil!")

    telo_p = t_p.split("---\n", 2)[2]
    telo_n = t_n.split("---\n", 2)[2]
    for radek in telo_p.splitlines():
        if radek.strip() and radek not in telo_n:
            raise SystemExit(f"CHYBA {jmeno}: v novém těle chybí řádek {radek[:60]!r}")


def main() -> int:
    chyb = 0
    for jmeno, zmeny in ZAPLATY.items():
        puvodni = (SKILLS / jmeno / "SKILL.md").read_bytes()
        radu_p = len(puvodni.decode("utf-8").splitlines())
        styl = styl_koncu(puvodni)
        novy = zaplat(puvodni, zmeny)
        zkontroluj(jmeno, puvodni, novy)
        radu_n = len(novy.decode("utf-8").splitlines())

        cil = OUT / jmeno / "SKILL.md"
        cil.parent.mkdir(parents=True, exist_ok=True)
        cil.write_bytes(novy)

        print(
            f"  OK   {jmeno:16} řádků {radu_p} → {radu_n} (+{radu_n - radu_p})  "
            f"konce={styl.encode('unicode_escape').decode()}  "
            f"frontmatter shodný  anchors=1x  bajtů {len(puvodni)} → {len(novy)}"
        )

    print()
    print(f"Záplat: {sum(len(z) for z in ZAPLATY.values())}, chyb: {chyb}")
    print("VŠE OK" if chyb == 0 else "NALEZENY CHYBY")
    return 0 if chyb == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
