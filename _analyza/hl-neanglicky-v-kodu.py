#!/usr/bin/env python
r"""ÚPLNÝ inventář neanglických textů v kódu — a HLAVNĚ podle toho, čím v kódu JSOU.

PROČ TO EXISTUJE — zadání uživatele 1. 10. 2026: „proveď ještě jednu hloubkovou
kontrolu, kde a jak se vyskytují neanglické texty v kódu, aby ses ujistil, že se
nerozbije a nezapomene ani jediné místo."

Na to se NEDÁ odpovědět výčtem od oka. Rozhoduje KONTEXT, ve kterém text stojí:

    komentář / docstring   → bezpečné, nikdo ho nečte za běhu
    text pro uživatele     → bezpečné pro kód, ale vidí ho člověk (fonty, logy)
    LITERÁL V PODMÍNCE     → RIZIKO: rozhraní, které musí volající uhodnout
    IDENTIFIKÁTOR          → RIZIKO: kódování, ASCII-only systémy, nástroje
    HODNOTA V DATECH       → RIZIKO: podle textu se může párovat nebo filtrovat

⚠ TŘI PASTI, KTERÉ TENHLE SKENER ZAVÍRÁ (všechny mě při psaní chytily):

1. **Komentář není nález.** První verze hledala vzory v celém souboru a našla
   30+ „rizik" — všechny to byly komentáře (`/** … */`). `AGENTS.md`: „statická
   kontrola musí číst KÓD, ne komentáře."

2. **Regulární výraz na kód nestačí.** Kdo hledá `"…"` regexem, chytne i apostrof
   uvnitř české věty a rozsype se mu párování uvozovek. Proto se u Pythonu,
   JavaScriptu a GDScriptu používá **AST / pořádný lexer**, ne regex. Kde AST
   není (YAML, JSON, .cfg), čte se formát parserem.

3. **Neznámý soubor NENÍ „čistý soubor".** Když skener formát neumí přečíst,
   musí to říct — jinak „0 nálezů" vypadá jako změřená nula. Proto se každý
   soubor buď zařadí, nebo skončí v sekci NEPOKRYTO.

Použití:
    python _analyza\hl-neanglicky-v-kodu.py                # souhrn
    python _analyza\hl-neanglicky-v-kodu.py --json C:\out.json
    python _analyza\hl-neanglicky-v-kodu.py --plny         # i bezpečné kategorie
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import re
import subprocess
import sys

try:
    import yaml          # PyYAML: pořádný parser místo řádkových regulárních výrazů
except ImportError:      # kdyby chybělo, YAML se čte fallbackem (a je to vidět)
    yaml = None

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
GIT = WS / "orchestra" / "tools" / "git.cmd"

# „Neanglické" = obsahuje znak mimo ASCII. Tím se chytí diakritika i „–" nebo "„".
def neascii(s: str) -> bool:
    return any(ord(c) > 127 for c in s)


CORE_SOUBORY = {
    "conductor/src/index.ts",
    "conductor/schema.sql",
    "conductor/wrangler.toml",
    "tools/git.cmd",
}

# kde se literál v AST vyskytuje → jaké je to riziko
RIZIKO_KONTEXT = {
    "porovnání (== / != / in)": "ROZHODUJE SE PODLE TEXTU",
    "klíč slovníku": "PÁROVÁ SE PODLE TEXTU",
    "hodnota klíče/atributu": "MŮŽE BÝT IDENTIFIKÁTOR",
    "volání funkce (argument)": "ARGUMENT – pozor, když jde o příkaz",
    "přiřazení": "HODNOTA",
    "jiné": "NEZAŘAZENO",
}


def soubory(repo: str) -> list[str]:
    r = subprocess.run([str(GIT), "-C", str(WS / repo), "ls-files"],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit(f"CHYBA: git ls-files v {repo} selhalo: {r.stderr.strip()}")
    return r.stdout.splitlines()


def obsahovy_otisk(seznamy: dict[str, list[str]]) -> dict:
    """Obsahový otisk vstupů: co tenhle skener PŘESNĚ čte.

    PROČ OBSAH A NE ČAS: `mtime` se mění kloněním, checkoutem a přepisem
    identického obsahu, takže by hlásil zastaralost i tam, kde se nic nezměnilo
    (a naopak by ji zmeškal u souboru s podrženým časem). Otisk z OBSAHU řekne
    přesně větu „inventář vznikl z těchto bajtů".

    PROČ NENÍ V `hl-rizika-jazyka.py`: ten nástroj musí zůstat POUZE ČTOUCÍ
    (sekce L validátoru ho jinak odmítne spustit — naměřeno: stačilo slovo
    `write_text` v komentáři). Přepočet otisku umí tenhle skener přes `--otisk`;
    druhá implementace téhož by se s ním jednou rozešla.
    """
    zaznamy = []
    otisk = hashlib.sha256()
    for repo in sorted(seznamy):
        relativni = []
        for f in sorted(seznamy[repo]):
            p = WS / repo / f
            if not p.is_file():
                continue
            data = p.read_bytes()
            relativni.append({"cesta": f, "bajtu": len(data),
                              "sha256": hashlib.sha256(data).hexdigest()[:16]})
        otisk.update(f"{repo}\n".encode("utf-8"))
        for z in relativni:
            otisk.update(f"{z['cesta']}|{z['bajtu']}|{z['sha256']}\n".encode("utf-8"))
        zaznamy.append({"repo": repo, "souboru": len(relativni), "soubory": relativni})
    return {"verze": 1, "sha256": otisk.hexdigest(),
            "souboru": sum(z["souboru"] for z in zaznamy), "repozitare": zaznamy}


# Klíče, jejichž HODNOTA je strojově čitelná (stav, výsledek, druh) – na těch
# stojí logika, takže je to riziko. Ostatní hodnoty jsou popisky pro člověka.
STROJOVE_KLICE = {
    "status", "stav", "state", "result", "vysledek", "výsledek", "type", "typ",
    "kind", "druh", "label", "popisek", "action", "akce", "trigger", "mode",
    "rezim", "režim", "verdict", "verdikt", "decision", "reason", "duvod", "důvod",
    "kategorie", "category", "level", "uroven", "úroveň", "role", "tier",
}


def _je_strojova_hodnota(klic: ast.AST | None) -> bool:
    """True, když hodnota visí pod klíčem, který nese STAV/VÝSLEDEK/DRUH."""
    if isinstance(klic, ast.Constant) and isinstance(klic.value, str):
        return klic.value.strip().lower() in STROJOVE_KLICE
    return False


# ─────────────────────────── Python: AST ──────────────────────────────────────
def python_nalezy(text: str, soubor: str) -> tuple[list[dict], str | None]:
    try:
        strom = ast.parse(text)
    except SyntaxError as e:
        return [], f"SyntaxError: {e.msg} (řádek {e.lineno})"

    tres = []
    for uzel in ast.walk(strom):
        if isinstance(uzel, ast.Compare):
            for op, porovnavac in zip(uzel.ops, uzel.comparators):
                if isinstance(porovnavac, ast.Constant) and isinstance(porovnavac.value, str) \
                        and neascii(porovnavac.value):
                    tres.append((porovnavac, f"porovnání ({type(op).__name__})"))
        elif isinstance(uzel, ast.Dict):
            for k, v in zip(uzel.keys, uzel.values):
                if isinstance(k, ast.Constant) and isinstance(k.value, str) and neascii(k.value):
                    tres.append((k, "klíč slovníku"))
                if isinstance(v, ast.Constant) and isinstance(v.value, str) and neascii(v.value):
                    # ROZDÍL, KTERÝ ROZHODUJE: `{"stav": "hotovo"}` je riziko
                    # (logika se může ptát na hodnotu), `{"popis": "hotovo"}`
                    # je popisek pro člověka. První verze to míchala dohromady
                    # a hlásila 84 „rizik", z nichž většina byla text.
                    ctx = ("STROJOVĚ ČITELNÁ HODNOTA" if _je_strojova_hodnota(k)
                           else "textová hodnota (pro člověka)")
                    tres.append((v, ctx))
        elif isinstance(uzel, ast.Call):
            for a in uzel.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str) and neascii(a.value):
                    tres.append((a, "volání funkce (argument)"))
        elif isinstance(uzel, ast.Assign):
            for t in uzel.targets:
                if isinstance(t, ast.Name) and neascii(t.id):
                    tres.append((t, "IDENTIFIKÁTOR (jméno proměnné)"))
            if isinstance(uzel.value, ast.Constant) and isinstance(uzel.value.value, str) \
                    and neascii(uzel.value.value):
                tres.append((uzel.value, "přiřazení"))
        elif isinstance(uzel, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if neascii(uzel.name):
                tres.append((uzel, "IDENTIFIKÁTOR (jméno funkce/třídy)"))

    out = []
    for uzel, ctx in tres:
        hodnota = uzel.value if isinstance(uzel, ast.Constant) else getattr(uzel, "id", None) or getattr(uzel, "name", "")
        radek = getattr(uzel, "lineno", 0)
        out.append({"soubor": soubor, "radek": radek, "kontext": ctx,
                    "text": str(hodnota)[:160], "jazyk": "python"})
    return out, None


# ─────────────────────────── JS/TS a GDScript: lexer ──────────────────────────
def _muze_byt_regex(text: str, i: int) -> bool:
    """Rozliší `/` jako DĚLENÍ od `/` jako REGULÁRNÍHO VÝRAZU.

    Po `/` NESMÍ stát operátor ani hodnota. Regex naopak začíná tam, kde jazyk
    čeká VÝRAZ: po `(`, `,`, `=`, `:`, `[`, `{`, `!`, `&`, `|`, `?`, `;`,
    `return`, `=>` a na začátku řádku/souboru.

    ⚠ SEZNAM SE MUSÍ TRFIT DO SKUTEČNOSTI. Naměřeno 1. 10. 2026: chyběla
    **čárka**, takže `/tvrdý limit|timeout/i,` na začátku prvku pole vypadal
    jako dělení a česká slova z něj skener vyhlásil za identifikátory.
    Naopak `*`, `+`, `%` v seznamu být NESMÍ — po nich následuje hodnota
    (`a * b / c`), takže tam je `/` dělení.
    """
    j = i - 1
    while j >= 0 and text[j] in " \t":
        j -= 1
    if j < 0 or text[j] == "\n":
        return True                       # začátek souboru nebo řádku → regex
    return text[j] in "=(,:[!&|?{};<>+-"


def _regex_konci(text: str, i: int) -> int:
    """Vrátí index za koncovým `/` regexu začínajícího na `i` (i = znak `/`).

    ⚠ KDY SE MÁ VZDÁT: přechod na nový řádek je nejednoznačný. `x = a / b`
    dělení nový řádek nepřechází (bývá tam `;`), ale regex v poli ano:

        const vzory = [
          /tvrdý limit|timeout/i,      ← `|` je PŘED koncem řádku → je to regex
        ];

    Naměřeno 1. 10. 2026: soubor `tools/analyza-aktualni.mjs` má na `:30`
    **neukončený** regex (`/\\[test\\] (OK|FAIL)/,` — přeskočená závorka), takže
    se dosavadní „vzdej se na konci řádku" zahořilo UPROSTŘED a `tvrdý` z `:31`
    vyhlásilo za identifikátor. Kritérium proto není „narazil jsem na nový
    řádek", ale „narazil jsem na nový řádek a přitom text zatím **nevypadá jako
    regex**".
    """
    j = i + 1
    v_tridе = False
    n = len(text)
    vypada_jako_regex = False
    while j < n:
        c = text[j]
        if c == "\\":
            vypada_jako_regex = True
            j += 2
            continue
        if c in "|([{":
            vypada_jako_regex = True
        if c == "\n":
            if vypada_jako_regex:
                j += 1                 # český vzor v poli přes řádek – jdeme dál
                continue
            return i + 1               # dělení → tohlencto regex nebyl
        if c == "[":
            v_tridе = True
        elif c == "]":
            v_tridе = False
        elif c == "/" and not v_tridе:
            j += 1
            while j < n and text[j].isalpha():   # příznaky g, i, m, s, u, y
                j += 1
            return j
        j += 1
    return i + 1


def js_retezce(text: str, hash_komentar: bool = False) -> tuple[list[tuple[int, str]], list[tuple[int, str]], list[tuple[int, str]]]:
    """Vrátí (komentáře, řetězcové literály, JMÉNA) jako (řádek, obsah).

    Vlastní lexer pro GDScript (a jako záchranná síť pro JS, kde ale platí, že
    skutečný nástroj je `_analyza/js-tokeny.mjs`). Zvládá: // /* */ ' " ` a —
    když `hash_komentar=True` — i `#`, což je komentář **GDScriptu**.

    ⚠ `#` CHYBĚLO (naměřeno 1. 10. 2026): bez něj skener vyhlásil česká slova
    z komentářů v `games/uo-shadows/scripts/game.gd` za identifikátory — 632
    „nálezů" v kategorii, kde mají být jednotky. Komentář není nález.

    ⚠ JMÉNA (identifikátory) se sbírají TAKY — a to je poučení z mutačního testu
    (`test-neanglicky-skener.py`): první verze sbírala jen literály, takže
    `let ohlášeno = 0;` v `conductor/src/index.ts` jí **uniklo**.
    """
    komentare: list[tuple[int, str]] = []
    retezce: list[tuple[int, str]] = []
    jmena: list[tuple[int, str]] = []
    i, radek = 0, 1
    n = len(text)
    while i < n:
        c = text[i]
        if c == "\n":
            radek += 1
            i += 1
            continue
        if hash_komentar and c == "#":
            j = text.find("\n", i)
            j = n if j < 0 else j
            komentare.append((radek, text[i:j]))
            i = j
            continue
        if hash_komentar and text.startswith('"""', i):
            # VÍCEŘÁDKOVÝ ŘETĚZEC v GDScriptu. Bez téhle větve se jeho obsah bral
            # jako jména — naměřeno 1. 10. 2026: 16 falešných „identifikátorů"
            # v `games/uo-shadows/tests/run_tests.gd`.
            j = text.find('"""', i + 3)
            j = n if j < 0 else j + 3
            retezce.append((radek, text[i:j]))
            radek += text[i:j].count("\n")
            i = j
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            j = n if j < 0 else j
            komentare.append((radek, text[i:j]))
            i = j
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            komentare.append((radek, text[i:j]))
            radek += text[i:j].count("\n")
            i = j
            continue
        if c == "/" and _muze_byt_regex(text, i):
            j = _regex_konci(text, i)
            if j > i + 1:                     # našel se konec → byl to regex
                retezce.append((radek, text[i:j]))
                i = j
                continue
            # NEVÍM, jestli je to regex, nebo dělení. Volíme KONZERVATIVNĚ:
            # přeskočíme jen do konce řádku a obsah NEHLÁSÍME jako jména.
            # Důvod: falešný nález nutí „opravovat" správný kód (AGENTS.md),
            # kdežto vynechání je vidět v přiznané mezi. Naměřeno 1. 10. 2026:
            # bez tohohle pravidla hlásil česká slova z regexů jako identifikátory.
            konec = text.find("\n", i)
            konec = n if konec < 0 else konec
            retezce.append((radek, text[i:konec]))
            i = konec
            continue
        if c in "'\"`":
            uvoz = c
            j = i + 1
            buf = []
            while j < n:
                if text[j] == "\\":
                    buf.append(text[j:j + 2])
                    j += 2
                    continue
                if text[j] == uvoz:
                    break
                if text[j] == "\n":
                    radek += 1
                buf.append(text[j])
                j += 1
            retezce.append((radek, "".join(buf)))
            i = j + 1
            continue
        # JMÉNO (identifikátor) — včetně diakritiky. `[^\W\d]` = písmeno nebo _.
        if c == "_" or c.isalpha():
            j = i
            while j < n and (text[j] == "_" or text[j].isalnum()):
                j += 1
            jmeno = text[i:j]
            if neascii(jmeno):
                jmena.append((radek, jmeno))
            i = j
            continue
        i += 1
    return komentare, retezce, jmena


# ─────────────────────────── JS/TS: skutečný parser ──────────────────────────
# POUČENÍ (naměřeno 1. 10. 2026, čtyři kola): ruční lexer na JS/TS je slepá cesta.
# Skener proto pro JS/TS volá `_analyza/js-tokeny.mjs`, což je **parser
# TypeScriptu** (je v `conductor/node_modules`) — jediný nástroj tady, který
# zvládne i typové anotace v `index.ts` a nespadne na vadné syntaxi.
TOKENY_SOUBOR = WS / "_analyza" / "_tokeny.json"
TOKENY_HELPER = WS / "_analyza" / "js-tokeny.mjs"


def nacti_tokeny(cesty: list[str]) -> dict[str, dict]:
    """Spustí Node helper nad danými soubory a vrátí {soubor: {tokeny, chyba}}.

    Dvě pasti, které to muselo obejít (obě naměřené 1. 10. 2026):
      1. `pwsh` v podprocesu NENÍ na PATH (WinError 2) — spouští se proto Node
         přímo, ne přes PowerShell.
      2. `>` v PowerShellu zapisuje **UTF-16LE** (soubor začínal `ff fe`), takže
         se výstup čte s detekcí BOM a zkouší se víc kódování.
    """
    if not cesty:
        return {}
    # Seznam souborů jde do Node SOUBOREM, ne argumenty: 100+ cest by přesáhlo
    # limit příkazové řádky Windows a chyba by vypadala jako „parser nic nevrátil".
    seznam = WS / "_analyza" / "_tokeny-vstup.txt"
    seznam.write_text("\n".join(cesty), encoding="utf-8")
    r = subprocess.run(["node", str(TOKENY_HELPER), "--seznam", str(seznam)],
                       capture_output=True, cwd=str(WS))
    if r.returncode != 0:
        raise SystemExit(f"CHYBA: tokenizér skončil {r.returncode}\n"
                         f"stderr: {r.stderr.decode('utf-8', 'replace')[:400]}")
    surove = r.stdout
    if not surove:
        raise SystemExit("CHYBA: tokenizér nic nevypsal")
    for kodovani in ("utf-8-sig", "utf-16", "utf-8"):
        try:
            data = json.loads(surove.decode(kodovani))
            break
        except Exception:
            continue
    else:
        raise SystemExit("CHYBA: výstup tokenizéru nejde přečíst (kódování?)")
    return {x["soubor"]: x for x in data}


def _predchozi_slovo(text: str, pozice: int) -> str:
    """Vrátí slovo, které stojí v textu před danou pozicí (přeskočí mezery)."""
    j = pozice - 1
    while j >= 0 and text[j] in " \t\r\n":
        j -= 1
    k = j
    while k >= 0 and (text[k].isalnum() or text[k] in "_$."):
        k -= 1
    k += 1
    return text[k:j + 1] if j >= k else ""


def js_nalezy(text: str, soubor: str, jazyk: str) -> tuple[list[dict], str | None]:
    # GDScript má `#` komentáře; JS/TS ne (tam je skutečným nástrojem parser).
    _, retezce, jmena = js_retezce(text, hash_komentar=(jazyk == "gdscript"))
    out = []
    radky = text.splitlines()

    # JMÉNA s diakritikou = identifikátory. TADY se rozhoduje, jestli skener
    # uvidí `let ohlášeno = 0;` (mutační test to odhalil jako slepé místo).
    for radek, jmeno in jmena:
        zdroj = radky[radek - 1] if 0 < radek <= len(radky) else ""
        pozice = zdroj.find(jmeno)
        pred = _predchozi_slovo(zdroj, pozice) if pozice >= 0 else ""
        if pred in ("let", "const", "var", "function", "class", "def", "extends"):
            ctx = "IDENTIFIKÁTOR (deklarace jména)"
        elif pred in ("let", "const", "var") or pred == "":
            ctx = "IDENTIFIKÁTOR (jméno v kódu)"
        else:
            ctx = "IDENTIFIKÁTOR (jméno v kódu)"
        out.append({"soubor": soubor, "radek": radek, "kontext": ctx,
                    "text": jmeno, "jazyk": jazyk})

    for radek, obsah in retezce:
        if not neascii(obsah):
            continue
        # kontext ze zdrojového řádku: co stojí PŘED literálem
        zdroj = radky[radek - 1] if 0 < radek <= len(radky) else ""
        pred = zdroj.split(obsah[:20])[0] if obsah[:20] and obsah[:20] in zdroj else zdroj
        if re.search(r"(===|!==|==|!=|\bin\b)\s*[\"'`]?\s*$", pred):
            ctx = "porovnání (== / != / in)"
        elif re.search(r"[\"'\w\]]\s*:\s*[\"'`]?\s*$", pred) and ":" in pred:
            ctx = "hodnota klíče/atributu"
        elif re.search(r"\b(console\.\w+|print|echo|say|push_error|push_warning|throw)\s*\(?\s*$", pred):
            ctx = "text pro uživatele"
        else:
            ctx = "jiné (nutno dořešit)"
        out.append({"soubor": soubor, "radek": radek, "kontext": ctx,
                    "text": obsah[:160], "jazyk": jazyk})
    return out, None


# ─────────────────────────── YAML, JSON, cfg: parser ──────────────────────────
def json_nalezy(text: str, soubor: str) -> tuple[list[dict], str | None]:
    """Projde JSON a vrátí neanglické KLÍČE a HODNOTY i s cestou, kde leží."""
    try:
        data = json.loads(text)
    except Exception as e:
        return [], f"JSON nejde načíst: {e}"
    out = []

    def projdi(uzel, cesta):
        if isinstance(uzel, dict):
            for k, v in uzel.items():
                if isinstance(k, str) and neascii(k):
                    out.append({"soubor": soubor, "radek": 0, "kontext": "KLÍČ V DATECH",
                                "text": f"{cesta} → klíč „{k}“", "jazyk": "json"})
                projdi(v, f"{cesta}.{k}")
        elif isinstance(uzel, list):
            for i, v in enumerate(uzel):
                projdi(v, f"{cesta}[{i}]")
        elif isinstance(uzel, str) and neascii(uzel):
            # ROZDÍL, KTERÝ ROZHODUJE: hodnota pod klíčem `status`/`stav` je
            # strojově čitelná; pod klíčem `popis`/`poznamka` je text pro člověka.
            posledni = cesta.rsplit(".", 1)[-1].split("[")[0].lower()
            ctx = ("HODNOTA POD STROJOVÝM KLÍČEM" if posledni in STROJOVE_KLICE
                   else "HODNOTA V DATECH")
            out.append({"soubor": soubor, "radek": 0, "kontext": ctx,
                        "text": f"{cesta} = {uzel[:120]}", "jazyk": "json"})

    projdi(data, "$")
    return out, None


def yaml_nalezy(text: str, soubor: str) -> tuple[list[dict], str | None]:
    """YAML parserem: zajímají nás KLÍČE (identifikátory!) a hodnoty bez komentářů.

    POZOR: řádkový fallback (níž) chyboval — za „shell v CI" označil řádek
    s `run:`, což je KLÍČ, ne text. U YAML, kde klíče řídí CI, je to podstatný
    rozdíl. Proto se používá pořádný parser.
    """
    if yaml is None:
        return textove_nalezy(text, soubor, "yaml")
    try:
        data = yaml.safe_load(text)
    except Exception as e:
        return [], f"YAML nejde načíst: {str(e)[:70]}"
    out: list[dict] = []

    def projdi(uzel, cesta):
        if isinstance(uzel, dict):
            for k, v in uzel.items():
                if isinstance(k, str) and neascii(k):
                    out.append({"soubor": soubor, "radek": 0, "kontext": "KLÍČ V YAML",
                                "text": f"{cesta} → „{k}“", "jazyk": "yaml"})
                projdi(v, f"{cesta}.{k}")
        elif isinstance(uzel, list):
            for i, v in enumerate(uzel):
                projdi(v, f"{cesta}[{i}]")
        elif isinstance(uzel, str) and neascii(uzel):
            out.append({"soubor": soubor, "radek": 0, "kontext": "text v YAML",
                        "text": f"{cesta} = {uzel[:150]}", "jazyk": "yaml"})

    projdi(data, "$")
    return out, None


def textove_nalezy(text: str, soubor: str, jazyk: str) -> tuple[list[dict], str | None]:
    """Fallback pro YAML/.cfg: řádek po řádku, s rozeznáním komentáře."""
    out = []
    for i, radek in enumerate(text.splitlines(), 1):
        if not neascii(radek):
            continue
        cisty = radek.split("#", 1)[0] if jazyk == "yaml" else radek
        if not neascii(cisty) or not cisty.strip():
            continue          # diakritika byla jen v komentáři
        if re.match(r"^\s*[;#]", radek) and jazyk != "yaml":
            continue
        m = re.match(r"^\s*([^:=]+?)\s*[:=]", cisty)
        if m and neascii(m.group(1)):
            ctx = "KLÍČ (jméno atributu)"
        elif re.match(r"^\s*-?\s*name\s*[:=]", cisty):
            ctx = "název v konfiguraci (vidí člověk)"
        elif "run:" in cisty or "echo" in cisty:
            ctx = "shell v CI"
        else:
            ctx = "hodnota/text"
        out.append({"soubor": soubor, "radek": i, "kontext": ctx,
                    "text": cisty.strip()[:160], "jazyk": jazyk})
    return out, None


# ─────────────────────────────── hlavní smyčka ────────────────────────────────
PRIPONY = {
    ".py": lambda t, f: python_nalezy(t, f),
    ".gd": lambda t, f: js_nalezy(t, f, "gdscript"),   # GDScript: ruční lexer (přiznaná mez)
    ".json": lambda t, f: json_nalezy(t, f),
    ".yml": lambda t, f: yaml_nalezy(t, f),
    ".yaml": lambda t, f: yaml_nalezy(t, f),
    ".cfg": lambda t, f: textove_nalezy(t, f, "cfg"),
    ".sql": lambda t, f: textove_nalezy(t, f, "sql"),
    ".toml": lambda t, f: textove_nalezy(t, f, "toml"),
    ".ps1": lambda t, f: textove_nalezy(t, f, "powershell"),
    ".cmd": lambda t, f: textove_nalezy(t, f, "cmd"),
}

# JS/TS jde přes skutečný parser TypeScriptu (viz `nacti_tokeny`), ne přes tyhle.
JS_TS_PRIPONY = (".ts", ".mts", ".cts", ".mjs", ".js", ".cjs")

vsechny: list[dict] = []
nepokryto: list[tuple[str, str, str]] = []
zpracovano: dict[str, int] = {}

# Seznam souborů se zjišťuje JEDNOU (dřív se `git ls-files` pouštěl dvakrát pro
# každý repozitář) a schová se i pro obsahový otisk níž.
REPA = ("orchestra", "games/uo-shadows")
seznamy: dict[str, list[str]] = {repo: soubory(repo) for repo in REPA}

# `--otisk`: vypiš JEN otisk vstupů (souhrn, ne celý výčet souborů) a skonči.
# Volá to `hl-rizika-jazyka.py`, který musí zůstat pouze čtoucí — přepočet
# otisku si tak půjčuje odsud, místo aby měl vlastní kopii (dvě implementace
# téhož se jednou rozejdou). Celý výčet je v inventáři pod `otisk_vstupu`.
if "--otisk" in sys.argv:
    o = obsahovy_otisk(seznamy)
    print(json.dumps({"verze": o["verze"], "sha256": o["sha256"],
                      "souboru": o["souboru"],
                      "repozitare": [{"repo": z["repo"], "souboru": z["souboru"]}
                                     for z in o["repozitare"]]}, ensure_ascii=False))
    sys.exit(0)

# Nejdřív jeden hromadný běh parseru nad všemi JS/TS soubory — je to rychlejší
# a hlavně se tím u každého souboru dozvíme, jestli má syntaktické chyby.
js_ts_cesty: list[pathlib.Path] = []
for repo in REPA:
    for f in seznamy[repo]:
        p = WS / repo / f
        if p.is_file() and p.suffix.lower() in JS_TS_PRIPONY:
            js_ts_cesty.append(p)

tokeny_podle_souboru: dict[str, dict] = {}
if js_ts_cesty:
    try:
        tokeny_podle_souboru = nacti_tokeny([str(c) for c in js_ts_cesty])
    except SystemExit as e:
        nepokryto.append(("(všechny JS/TS)", "tokenizér selhal", str(e)[:120]))

for repo in REPA:
    for f in seznamy[repo]:
        p = WS / repo / f
        if not p.is_file():
            continue
        klic = f"{repo}/{f}"
        prip = p.suffix.lower()

        if prip in JS_TS_PRIPONY:
            zaznam = tokeny_podle_souboru.get(str(p))
            if zaznam is None:
                nepokryto.append((klic, "tokenizér soubor nevrátil", "—"))
                continue
            if zaznam.get("chyba"):
                nepokryto.append((klic, "parser to nepřečetl", str(zaznam["chyba"])[:80]))
                continue
            syntax = zaznam.get("syntaxErrors", 0)
            if syntax:
                # Soubor se syntaktickými chybami NENÍ „čistý" — parser u vadných
                # uzlů nevidí dovnitř. Říká se to nahlas, místo aby se mlčelo.
                nepokryto.append((klic, f"syntaktické chyby ({syntax})",
                                  "parser u vadných uzlů nevidí dovnitř"))
            for t in zaznam.get("tokeny", []):
                vsechny.append({"soubor": klic, "radek": t["radek"],
                                "kontext": t["kontext"], "text": t["text"],
                                "jazyk": zaznam.get("jazyk", "js")})
            zpracovano[klic] = len(zaznam.get("tokeny", []))
            continue

        if prip not in PRIPONY:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception as e:
            nepokryto.append((klic, "nejde přečíst", str(e)[:60]))
            continue
        try:
            nalezy, chyba = PRIPONY[prip](text, klic)
        except Exception as e:
            nepokryto.append((klic, "skener spadl", f"{type(e).__name__}: {e}"[:80]))
            continue
        if chyba:
            nepokryto.append((klic, "formát nepřečten", chyba[:80]))
            continue
        zpracovano[klic] = len(nalezy)
        vsechny.extend(nalezy)

# ─────────────────────────────── výstup ───────────────────────────────────────
if "--json" in sys.argv:
    cil = sys.argv[sys.argv.index("--json") + 1] if len(sys.argv) > sys.argv.index("--json") + 1 else None
    data = {"nalezy": vsechny, "nepokryto": nepokryto,
            "souboru_zpracovano": len(zpracovano),
            "otisk_vstupu": obsahovy_otisk(seznamy)}
    if cil:
        pathlib.Path(cil).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"zapsáno: {cil} ({len(vsechny)} nálezů)")
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    sys.exit(0)

print("═" * 84)
print("INVENTÁŘ NEANGLICKÝCH TEXTŮ V KÓDU")
print("═" * 84)
print(f"  souborů zpracováno:  {len(zpracovano)}")
print(f"  nálezů celkem:       {len(vsechny)}")
print(f"  NEPOKRYTO:           {len(nepokryto)}   ← když je to >0, inventář NENÍ úplný")
print()

# 1) RIZIKOVÉ kategorie – tohle je jádro odpovědi
RIZIKOVE = (
    # Python AST
    "porovnání (== / != / in)", "porovnání (Eq)", "porovnání (NotEq)",
    "porovnání (In)", "porovnání (NotIn)", "porovnání (Is)", "porovnání (IsNot)",
    "IDENTIFIKÁTOR (jméno proměnné)", "IDENTIFIKÁTOR (jméno funkce/třídy)",
    "STROJOVĚ ČITELNÁ HODNOTA",
    # datové formáty
    "klíč slovníku", "KLÍČ V DATECH", "KLÍČ V YAML", "KLÍČ (jméno atributu)",
    "HODNOTA POD STROJOVÝM KLÍČEM",
    # kontexty z parseru TypeScriptu (`_analyza/js-tokeny.mjs`) — POZOR, mají
    # VLASTNÍ názvy. Naměřeno 1. 10. 2026: chyběly tu `deklarace proměnné`
    # a `výraz`, takže `let ohlášeno = 0;` v JÁDŘE orchestra se do rizik
    # vůbec nedostalo — a to je přesně nález, kvůli kterému skener vznikl.
    "IDENTIFIKÁTOR (deklarace jména)", "IDENTIFIKÁTOR (jméno v kódu)",
    "deklarace proměnné", "deklarace funkce", "deklarace třídy", "parametr funkce",
    "klíč objektu", "klíč objektu (třída)", "klíč objektu (metoda)",
    "KLÍČ OBJEKTU (může být identifikátor)", "rozbalené jméno",
    "POROVNÁNÍ", "POROVNÁNÍ (case)", "výraz", "návratová hodnota",
)

print("── 1. RIZIKO: text, podle kterého se ROZHODUJE nebo PÁRUJE ────────────────")
rizikove = [n for n in vsechny if n["kontext"] in RIZIKOVE]
print(f"   nálezů: {len(rizikove)}")
po_kontextu: dict[str, list] = {}
for n in rizikove:
    po_kontextu.setdefault(n["kontext"], []).append(n)
for ctx, v in sorted(po_kontextu.items(), key=lambda kv: -len(kv[1])):
    print(f"\n   [{ctx}] — {len(v)}")
    for n in v[:40]:
        print(f"      {n['soubor']}:{n['radek']}  {n['text'][:100]}")
    if len(v) > 40:
        print(f"      … a dalších {len(v) - 40} (viz --json)")
print()

# 2) Text pro uživatele a shell v CI – bezpečné pro kód, vidí to člověk
print("── 2. TEXT PRO UŽIVATELE / SHELL V CI (vidí člověk, kód to nečte) ───────")
uziv = [n for n in vsechny if n["kontext"] in ("text pro uživatele", "shell v CI",
                                               "název v konfiguraci (vidí člověk)",
                                               "text v YAML", "hodnota/text", "přiřazení",
                                               "jiné (nutno dořešit)", "jiné", "volání funkce (argument)")]
print(f"   nálezů: {len(uziv)}")
po_souboru: dict[str, int] = {}
for n in uziv:
    po_souboru[n["soubor"]] = po_souboru.get(n["soubor"], 0) + 1
for s, c in sorted(po_souboru.items(), key=lambda kv: -kv[1])[:15]:
    print(f"      {c:4d}x  {s}")
print()

# 3) HODNOTY V DATECH
print("── 3. HODNOTY V DATECH (JSON) ───────────────────────────────────────────")
data_n = [n for n in vsechny if n["kontext"] in ("HODNOTA V DATECH", "HODNOTA POD STROJOVÝM KLÍČEM")]
print(f"   nálezů: {len(data_n)} (texty, popisy, názvy předmětů – NE identifikátory)")
po_souboru = {}
for n in data_n:
    po_souboru[n["soubor"]] = po_souboru.get(n["soubor"], 0) + 1
for s, c in sorted(po_souboru.items(), key=lambda kv: -kv[1]):
    print(f"      {c:4d}x  {s}")
print()

# 4) NEPOKRYTO – přiznaná mez
print("── 4. NEPOKRYTO (skener to NEUMÍ přečíst → NENÍ to „čisté“) ─────────────")
if nepokryto:
    for f, duvod, detail in nepokryto:
        print(f"      {f}  [{duvod}]  {detail}")
else:
    print("      (nic)")
print()

# 5) JÁDRO vs. NÁSTROJE – co je orchestra za běhu a co je jednorázový nástroj
print("── 5. KDE TO JE: jádro orchestra vs. nástroje ───────────────────────────")
jadro = [n for n in vsechny if n["soubor"] in CORE_SOUBORY or n["soubor"].startswith("orchestra/repo/")]
nastroje = [n for n in vsechny if n["soubor"].startswith("orchestra/tools/")]
hra = [n for n in vsechny if n["soubor"].startswith("games/")]
print(f"   jádro (conductor + šablona repo/): {len(jadro)}")
print(f"   nástroje (orchestra/tools/):       {len(nastroje)}")
print(f"   hra (games/uo-shadows/):           {len(hra)}")
print()
print("   RIZIKOVÉ nálezy v JÁDŘE (tam se to nesmí rozbít):")
for n in jadro:
    if n["kontext"] in RIZIKOVE:
        print(f"      {n['soubor']}:{n['radek']}  [{n['kontext']}]  {n['text'][:90]}")
print()
print("   RIZIKOVÉ nálezy ve HŘE:")
for n in hra:
    if n["kontext"] in RIZIKOVE:
        print(f"      {n['soubor']}:{n['radek']}  [{n['kontext']}]  {n['text'][:90]}")
