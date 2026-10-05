#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Test pro NÁLEZ H79 — neplatné escape sekvence a `filename` v `ast.parse`.

CO BYLO VADNÉ (naměřeno P14 5. 10. 2026)
----------------------------------------
Tři soubory v `_analyza/` měly v řetězci **neplatnou escape sekvenci**:

    _analyza/p1-inventura-cest.py:21   invalid escape sequence '\`'
    _analyza/ps1-bom-crlf.py:7         invalid escape sequence '\p'
    _analyza/sken-vazeb.py:15          invalid escape sequence '\.'

Python 3.12 to hlásí jako `SyntaxWarning` a **příští verze z toho udělá chybu**.
**A skener to hlásil BEZ JMÉNA SOUBORU** (`ast.parse(text)` bez `filename` →
`<unknown>:21`), takže se to nedalo dohledat.

JAK SE TO MĚŘÍ
--------------
  1. **POZITIVNÍ KONTROLA** (známý chybný případ): do stromu se na dobu běhu
     položí sonda s neplatnou sekvencí → skener `h79-escape-sken.py` ji MUSÍ
     najít **i se jménem souboru**. Bez toho by „0 varování" mohlo znamenat
     „skener nic nevidí".
  2. **0 varování** nad oběma repy (to je kritérium zadání).
  3. **OBSAH SE NEZMĚNIL**: parsované řetězcové konstanty s zpětným lomítkem se
     porovnají proti `git show HEAD:<soubor>` — `raw string` nesmí změnit text.
  4. **`filename` v `ast.parse`**: ze ŽIVÉHO zdroje skeneru se vytáhne funkce
     `python_nalezy` (AST + `exec`) a **zavolá se** nad textem s vadnou sekvencí;
     varování musí mít **jméno souboru**, které jsme předali.
  5. **MUTACE 4**: ze zdroje se `filename=soubor` odebere → varování je
     `<unknown>` → test by ZČERVENAL. (Mutuje se **text v paměti**, ne soubor.)

Použití:  python _analyza\test-h79-escape.py
"""
from __future__ import annotations

import ast
import os
import pathlib
import shutil
import subprocess
import sys
import warnings

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(os.environ.get("FORGE_WS") or pathlib.Path(__file__).resolve().parents[1])
ANALYZA = WS / "_analyza"
GIT = WS / "tools" / "git.cmd"
SKENER_ESCAPE = ANALYZA / "h79-escape-sken.py"
SKENER = ANALYZA / "hl-neanglicky-v-kodu.py"
PY = sys.executable
DOTCENE = ["_analyza/p1-inventura-cest.py", "_analyza/ps1-bom-crlf.py",
           "_analyza/sken-vazeb.py"]
SONDA = ANALYZA / "_h79-sonda-escape.py"

kontrol = 0
chyb = 0


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if not ok:
        chyb += 1
    print(f"  {'OK   ' if ok else 'CHYBA'} {popis}")
    if not ok and detail:
        for r in str(detail).splitlines()[:16]:
            print(f"        {r}")


def spust(prikaz: list[str]) -> tuple[int, str]:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run(prikaz, cwd=str(WS), capture_output=True, env=env)
    return r.returncode, (r.stdout.decode("utf-8", "replace")
                          + r.stderr.decode("utf-8", "replace"))


def konstanty_s_lomitem(zdroj: str, jmeno: str = "<komparace>") -> list[str]:
    """Řetězcové konstanty obsahující zpětný apostrof — v pořadí výskytu.

    `filename` se předává i tady: bez něj by test sám vyráběl varování
    `<unknown>` a mátl výstup (přesně vada, kterou H79 popisuje).
    Varování se ale **potlačují** — obsah z `HEAD` je **stav PŘED opravou**
    a neplatné sekvence v něm jsou očekávané; hlásí je krok 2 (skener).
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        strom = ast.parse(zdroj, filename=jmeno)
    return [n.value for n in ast.walk(strom)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and "\\" in n.value]


# Text s NEPLATNOU escape sekvencí, která je VAROVÁNÍ (ne chyba).
# ⚠ `\U` by vyrobilo `SyntaxError: truncated \UXXXXXXXX escape` — a to by
# měřilo něco jiného než H79 (`\s`, `\p`, `\.` a `\`` jsou varování).
VADNY_TEXT = 'CESTA = "C:\\neco\\soubor.txt"\n'


print("=" * 92)
print("NÁLEZ H79 — neplatné escape sekvence a `filename` v `ast.parse`")
print("=" * 92)
print(f"  skener = {SKENER_ESCAPE}")
print(f"  WS     = {WS}")
print()

# ── 1) POZITIVNÍ KONTROLA: skener vadu VIDÍ a pojmenuje soubor ──────────────
print("── 1) POZITIVNÍ KONTROLA: sonda s vadnou sekvencí ─────────────────────")
zkontroluj("sonda před testem neexistuje", not SONDA.exists(), str(SONDA))
try:
    SONDA.write_text('# -*- coding: utf-8 -*-\n' + VADNY_TEXT,
                     encoding="utf-8", newline="")
    kod_p, v_p = spust([PY, str(SKENER_ESCAPE)])
    print(f"      se sondou: exit={kod_p}")
    zkontroluj("se sondou skener skončí nenulově (vadu VIDÍ)", kod_p != 0, v_p[-800:])
    # ⚠ POZOR: NESMÍ se testovat „`<unknown>` tam není" — skener sám ve svém
    # vysvětlujícím textu `<unknown>` **má** („dřív je hlásil jako `<unknown>`").
    # To je past `overovani` §10.1 (brána čte vlastní citaci); měří se proto
    # PŘÍTOMNOST `jméno_souboru:řádek`, ne nepřítomnost cizího slova.
    zkontroluj(f"a vypíše ji jako `{SONDA.name}:2` (jméno souboru I řádek)",
               f"{SONDA.name}:2" in v_p, v_p[-900:])
finally:
    if SONDA.exists():
        SONDA.unlink()
    zkontroluj("sonda uklizena", not SONDA.exists())

# ── 2) CELÝ STROM: 0 varování ──────────────────────────────────────────────
print()
print("── 2) OBA REPY: 0 neplatných escape sekvencí ─────────────────────────")
kod0, v0 = spust([PY, str(SKENER_ESCAPE)])
print(f"      exit={kod0}")
for radek in v0.splitlines():
    if "ZMĚŘENO" in radek or "prošlé soubory" in radek:
        print(f"      | {radek.rstrip()}")
zkontroluj("skener nad oběma repy: exit 0 (žádná vada)", kod0 == 0, v0[-900:])
zkontroluj("a vykáže to čítačem (`ZMĚŘENO: 0 …`)",
           "ZMĚŘENO: 0 neplatných escape sekvencí" in v0, v0[-900:])

# ── 3) OBSAH SE NEZMĚNIL (proti `git show HEAD:`) ──────────────────────────
print()
print("── 3) OBSAH SE NEZMĚNIL: konstanty proti `git show HEAD:` ─────────────")
for rel in DOTCENE:
    r = subprocess.run([str(GIT), "-C", str(WS), "show", f"HEAD:{rel}"],
                       capture_output=True, shell=True)
    hlavni = (r.stdout or b"").decode("utf-8", "replace")
    zkontroluj(f"{rel}: `git show HEAD:` vrátil obsah", bool(hlavni.strip()),
               (r.stderr or b"").decode("utf-8", "replace")[-300:])
    pred = konstanty_s_lomitem(hlavni, f"HEAD:{rel}")
    po = konstanty_s_lomitem((WS / rel).read_text(encoding="utf-8"), rel)
    stejne = pred == po
    zkontroluj(f"{rel}: {len(pred)} řetězců se zpětným lomítkem je SHODNÝCH "
               f"s `HEAD` (raw string obsah nezměnil)", stejne,
               f"před: {pred[:3]}…\npo:   {po[:3]}…")
    if not stejne:
        for i, (a, b) in enumerate(zip(pred, po)):
            if a != b:
                print(f"        PRVNÍ ROZDÍL (index {i}):\n          před: {a[:120]!r}\n          po:   {b[:120]!r}")
                break

# ── 4) `filename` v `ast.parse`: zavolá se ŽIVÁ funkce skeneru ─────────────
print()
print("── 4) `filename` v `ast.parse` — volá se funkce ze ŽIVÉHO skeneru ──────")
zdroj_skeneru = SKENER.read_text(encoding="utf-8")
strom = ast.parse(zdroj_skeneru)
uzel = next((n for n in strom.body
             if isinstance(n, ast.FunctionDef) and n.name == "python_nalezy"), None)
zkontroluj("ve skeneru je funkce `python_nalezy` (dá se vyjmout a zavolat)",
           uzel is not None)
if uzel is None:
    sys.exit(1)
snippet = ast.get_source_segment(zdroj_skeneru, uzel)
zkontroluj("podařilo se vyjmout její zdroj (AST → segment)", bool(snippet))


def zavolej_python_nalezy(kod_funkce: str) -> list:
    ns = {"ast": ast,
          "python_nalezy_ze_stromu": lambda *a, **k: ([], None)}
    exec(compile(kod_funkce, "<test-h79>", "exec"), ns)  # noqa: S102
    with warnings.catch_warnings(record=True) as z:
        warnings.simplefilter("always")
        ns["python_nalezy"](VADNY_TEXT, "fixtura-h79.py")
    return [w for w in z if issubclass(w.category, SyntaxWarning)]


zaznamy = zavolej_python_nalezy(snippet)
print(f"      varování ze živé funkce: {len(zaznamy)}")
zkontroluj("živá funkce na vadném textu vyrobí `SyntaxWarning`", len(zaznamy) >= 1,
           str(zaznamy))
zkontroluj("a varování má JMÉNO SOUBORU, které jsme předali (`fixtura-h79.py`)",
           any(w.filename == "fixtura-h79.py" for w in zaznamy),
           "\n".join(f"{w.filename}:{w.lineno}: {w.message}" for w in zaznamy))

# ── 5) MUTACE: `filename=soubor` se odebere ────────────────────────────────
print()
print("── 5) MUTACE: ze zdroje funkce se odebere `filename=soubor` ───────────")
mut = snippet.replace(", filename=soubor", "")
zkontroluj("mutace se provedla v TEXTU (nový tvar v mutantu není)",
           mut != snippet and "filename=soubor" not in mut)
zaznamy_m = zavolej_python_nalezy(mut)
print(f"      varování z mutantu: {[f'{w.filename}' for w in zaznamy_m]}")
zkontroluj("MUTACE: varování je BEZ jména souboru (`<unknown>`) — přesně to byl "
           "H79 a test by ZČERVENAL",
           any(str(w.filename).startswith("<") for w in zaznamy_m)
           and not any(w.filename == "fixtura-h79.py" for w in zaznamy_m),
           "\n".join(f"{w.filename}:{w.lineno}: {w.message}" for w in zaznamy_m))

print()
print("=" * 92)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
if chyb:
    print(f"CHYBA: {chyb} — H79 NENÍ dokázané")
    sys.exit(1)
print("H79 JE OPRAVENO A DOKÁZÁNO: 0 varování, obsah shodný s `HEAD`, "
      "varování má jméno souboru.")
sys.exit(0)
