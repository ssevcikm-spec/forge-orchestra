"""Offline test záplat skillů — známý SPRÁVNÝ i známý CHYBNÝ případ.

Testuje se na KOPIÍCH ve workspace (`_analyza\\patch-test\\`), takže se nikdy
nezapisuje mimo workspace. Ověřuje se:

  1. připravená záplata (`_analyza\\patch\\`) odpovídá tomu, co generátor
     spočítá z originálu — jinak by se aplikoval jiný text, než se ověřil,
  2. aplikace na čistou kopii projde a výsledek je **bajt na bajt** jako záplata,
  3. druhé spuštění je **idempotentní** („už aplikováno", soubor se nemění),
  4. **rozbitý anchor** (známý chybný případ) aplikaci ZASTAVÍ a nic nezapíše —
     ani u skillu, který je v pořádku (žádný částečný zápis),
  5. `description` a `whenToUse` zůstanou shodné s originálem.

Bez chybných případů by test nic neměřil — „prošlo to" samo o sobě neznamená nic.
"""

import contextlib
import hashlib
import importlib.util
import io
import os
import pathlib
import shutil
import sys

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TADY = pathlib.Path(__file__).resolve().parent
SKILLS = pathlib.Path(r"C:\Users\Ssevc\.dsh\skills")
FIX = TADY / "patch-test"
GOLDEN = TADY / "patch"
SKILLY = ["game-developer", "dsh-prostredi"]
FM = r"^---\n(.*?)\n---\n"


def nacti(nazev, cesta):
    spec = importlib.util.spec_from_file_location(nazev, cesta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


priprava = nacti("priprava", TADY / "priprav-skill-patch.py")
aplikace = nacti("aplikace", TADY / "aplikuj-skill-patch.py")

chyb = 0


def test(nazev, ok, detail=""):
    global chyb
    print(f"  {'OK   ' if ok else 'CHYBA'} {nazev}{(' — ' + detail) if detail else ''}")
    if not ok:
        chyb += 1


def hash_b(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:16]


def konce(b: bytes):
    """Vrátí (dominantní styl, počet konců OPAČNÉHO stylu)."""
    crlf = b.count(b"\r\n")
    lf = b.count(b"\n") - crlf
    return ("CRLF" if crlf > lf else "LF"), (lf if crlf > lf else crlf)


def frontmatter(cesta: pathlib.Path):
    import re

    t = cesta.read_bytes().decode("utf-8").replace("\r\n", "\n")
    return yaml.safe_load(re.match(FM, t, re.S).group(1))


def fixture(cesta: pathlib.Path, rozbit=None):
    """Vytvoří kopii obou skillů; `rozbit` = jméno skillu, kterému se zničí anchor."""
    if cesta.exists():
        shutil.rmtree(cesta)
    for jmeno in SKILLY:
        cil = cesta / jmeno
        cil.mkdir(parents=True)
        b = (SKILLS / jmeno / "SKILL.md").read_bytes()
        if jmeno == rozbit:
            b = b.replace(b"## 4. Granule (atomick", b"## 4. Granule (POKAZENE")
        (cil / "SKILL.md").write_bytes(b)


def spust(root: pathlib.Path):
    os.environ["SKILLS_ROOT"] = str(root)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = aplikace.main()
    finally:
        os.environ.pop("SKILLS_ROOT", None)
    return rc, buf.getvalue()


print("1) Připravená záplata odpovídá tomu, co spočítá generátor z originálu")
for jmeno in SKILLY:
    puvodni = (SKILLS / jmeno / "SKILL.md").read_bytes()
    spocitane = priprava.zaplat(puvodni, priprava.ZAPLATY[jmeno])
    ulozene = (GOLDEN / jmeno / "SKILL.md").read_bytes()
    test(
        f"{jmeno}: záplata == přepočet",
        spocitane == ulozene,
        f"{hash_b(spocitane)} vs {hash_b(ulozene)}",
    )

print("\n2) Aplikace na čistou kopii")
fixture(FIX / "cista")
rc, out = spust(FIX / "cista")
test("návratový kód 0", rc == 0, f"rc={rc}")
test("výstup hlásí ZAPSÁNO", "ZAPSÁNO" in out)
for jmeno in SKILLY:
    zapsane = (FIX / "cista" / jmeno / "SKILL.md").read_bytes()
    test(
        f"{jmeno}: výsledek == záplata (bajt na bajt)",
        zapsane == (GOLDEN / jmeno / "SKILL.md").read_bytes(),
    )
    orig = (SKILLS / jmeno / "SKILL.md").read_bytes()
    styl_o, opacny_o = konce(orig)
    styl_n, opacny_n = konce(zapsane)
    test(
        f"{jmeno}: konce řádků zůstaly stejným stylem ({styl_o})",
        styl_n == styl_o and opacny_n == opacny_o,
        f"styl {styl_o}→{styl_n}, opačných konců {opacny_o}→{opacny_n}",
    )
    test(
        f"{jmeno}: počet řádků sedí na počet konců řádků",
        zapsane.count(b"\n") == len(zapsane.decode("utf-8").splitlines()),
    )
    fm_o = frontmatter(SKILLS / jmeno / "SKILL.md")
    fm_n = frontmatter(FIX / "cista" / jmeno / "SKILL.md")
    test(
        f"{jmeno}: description+whenToUse beze změny",
        fm_n["description"] == fm_o["description"]
        and fm_n["whenToUse"] == fm_o["whenToUse"]
        and fm_n["name"] == jmeno,
    )

print("\n3) Druhé spuštění je idempotentní")
pred = {j: (FIX / "cista" / j / "SKILL.md").read_bytes() for j in SKILLY}
rc, out = spust(FIX / "cista")
test("návratový kód 0", rc == 0, f"rc={rc}")
test("hlásí 'už aplikováno'", "už aplikováno" in out)
test("nic se nepřepsalo", all((FIX / "cista" / j / "SKILL.md").read_bytes() == pred[j] for j in SKILLY))

print("\n4) Rozbitý anchor (známý chybný případ) — musí zastavit a nic nezapsat")
fixture(FIX / "rozbito", rozbit="game-developer")
pred = {j: (FIX / "rozbito" / j / "SKILL.md").read_bytes() for j in SKILLY}
rc, out = spust(FIX / "rozbito")
test("návratový kód NENÍ 0", rc != 0, f"rc={rc}")
test("hlásí CHYBA", "CHYBA" in out)
test(
    "rozbitý skill zůstal nedotčen",
    (FIX / "rozbito" / "game-developer" / "SKILL.md").read_bytes() == pred["game-developer"],
)
test(
    "ani zdravý skill se nezačal zapisovat (žádný částečný zápis)",
    (FIX / "rozbito" / "dsh-prostredi" / "SKILL.md").read_bytes() == pred["dsh-prostredi"],
)

print()
print(f"Chyb: {chyb}")
print("VŠE OK" if chyb == 0 else "NALEZENY CHYBY")
sys.exit(0 if chyb == 0 else 1)
