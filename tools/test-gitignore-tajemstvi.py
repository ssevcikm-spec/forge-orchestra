r"""Kontraktní test: `.gitignore`, který orchestra vnucuje hrám, chrání tajemství.

PROČ TENHLE TEST EXISTUJE
-------------------------
`install-into-repo.ps1` kopíruje do herního repa `.env` s REÁLNÝM
`FORGE_SECRET` (zdroj: `repo\.forge\node\.env`). Generovaný `.gitignore`
ale `.env` **neobsahoval** – naměřeno 1. 10. 2026:

    git -C games/uo-shadows check-ignore .forge/node/.env   ->  nic (exit 1)

Agent v CI dělá `git add -A`, takže by tajemství poslalo do patche i do PR.
Že k úniku nedošlo, je jen tím, že ten soubor v herním repu ještě není –
tedy **štěstí, ne ochrana**. Nález je v analýze jako S7/L5 a v plánu jako F0.6.

CO TESTUJE (kontrakt mezi DVĚMA kopiemi, ne dvě kontroly zvlášť)
----------------------------------------------------------------
Tenhle projekt má na dvou místech totéž pravidlo a ta se musí shodovat:

  1. GENERÁTOR   – blok `@'...'@` v `orchestra\\install-into-repo.ps1`
                   (co orchestra zapíše nové hře)
  2. SKUTEČNOST  – `games\\uo-shadows\\.gitignore` (co ta hra opravdu má)

Kontroluje se **shoda mezi nimi**, ne každá zvlášť. Kdyby se kontrolovala
každá sama, rozejití by uniklo – a to je přesně vzor z analýzy (§1.4).

Navíc test ověří, že pravidla **skutečně platí** – ne jen že jsou v souboru
napsaná. To je rozdíl mezi „dokumentace tvrdí" a „git to vymáhá".
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
GENERATOR = WS / "orchestra" / "install-into-repo.ps1"
HRA = WS / "games" / "uo-shadows"

# Co musí `.gitignore` hry ignorovat. První dva jsou BEZPEČNOSTNÍ (tajemství),
# zbytek je hygiena, která se taky osvědčila jako drahá (cache v patchi a PR).
POVINNE = {
    ".env": "tajemství – `install-into-repo.ps1` ho do hry kopíruje s FORGE_SECRET",
    ".forge/node/.env": "tajemství – konkrétní cesta, kterou kopírování používá",
    "__pycache__/": "Python cache po lokálním spuštění bran",
    "*.pyc": "Python cache (jednotlivé soubory)",
    ".forge/provider.env": "volba poskytovatele pro shell (nese klíč)",
}

kontrol = 0
chyb = 0


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if ok:
        print(f"  OK    {popis}")
    else:
        chyb += 1
        print(f"  CHYBA {popis}")
        if detail:
            for radek in detail.splitlines():
                print(f"        {radek}")


def blok_generatoru() -> str:
    """Vytáhne z .ps1 text mezi @' a '@ – tedy co se zapíše do .gitignore.

    POZOR: soubor je UTF-8 **s BOM** (jinak ho PowerShell přečte jako cp1252
    a parser spadne). Čte se proto `utf-8-sig`; bez toho by první řádek
    začínal BOM a porovnání by tiše nesedělo.
    """
    text = GENERATOR.read_text(encoding="utf-8-sig")
    m = re.search(r"@'\r?\n(.*?)\r?\n'@", text, re.S)
    if not m:
        raise SystemExit("CHYBA: v install-into-repo.ps1 jsem nenašel blok @'...'@")
    return m.group(1)


def radky(gitignore_text: str) -> set[str]:
    """Jen skutečná pravidla – bez komentářů a prázdných řádků."""
    return {
        r.strip()
        for r in gitignore_text.splitlines()
        if r.strip() and not r.strip().startswith("#")
    }


def main() -> int:
    print(f"=== generátor: {GENERATOR} ===")
    print(f"=== skutečnost: {HRA / '.gitignore'} ===")
    print()

    if not GENERATOR.is_file():
        print(f"CHYBA: {GENERATOR} neexistuje")
        return 1
    if not (HRA / ".gitignore").is_file():
        print(f"CHYBA: {(HRA / '.gitignore')} neexistuje")
        return 1

    gen = radky(blok_generatoru())
    skut = radky((HRA / ".gitignore").read_text(encoding="utf-8"))

    print("--- 1) generátor obsahuje povinná pravidla ---")
    for pravidlo, proc in POVINNE.items():
        zkontroluj(f"generátor: {pravidlo!r}  ({proc})", pravidlo in gen)

    print()
    print("--- 2) herní .gitignore obsahuje totéž ---")
    for pravidlo, proc in POVINNE.items():
        zkontroluj(f"hra: {pravidlo!r}", pravidlo in skut)

    print()
    print("--- 3) KONTRAKT: obě kopie se shodují v bezpečnostních pravidlech ---")
    bezpecnostni = [".env", ".forge/node/.env", ".forge/provider.env"]
    chybejici_v_generatoru = [p for p in bezpecnostni if p in skut and p not in gen]
    chybejici_ve_hre = [p for p in bezpecnostni if p in gen and p not in skut]
    zkontroluj(
        "co generátor vnucuje, to hra má (a naopak)",
        not chybejici_v_generatoru and not chybejici_ve_hre,
        "\n".join(
            [f"v generátoru chybí: {chybejici_v_generatoru}"] * bool(chybejici_v_generatoru)
            + [f"ve hře chybí: {chybejici_ve_hre}"] * bool(chybejici_ve_hre)
        ),
    )

    print()
    print("--- 4) pravidla SKUTEČNĚ platí (ne jen že jsou napsaná) ---")
    for cesta, proc in [
        (".forge/node/.env", "tajemství"),
        (".env", "tajemství"),
        (".forge/provider.env", "klíč poskytovatele"),
    ]:
        r = subprocess.run(
            ["git", "-C", str(HRA), "check-ignore", "-v", cesta],
            capture_output=True, text=True,
        )
        zkontroluj(
            f"git check-ignore {cesta!r} ({proc})",
            r.returncode == 0,
            f"git ten soubor NEIGNORUJE (exit {r.returncode}) – pravidlo je jen text.\n"
            f"stdout={r.stdout.strip()!r} stderr={r.stderr.strip()!r}",
        )

    print()
    print("--- 5) negativní kontrola: běžný soubor ignorovaný NENÍ ---")
    # Kdyby .gitignore ignoroval všechno, test výš by prošel a nic by nedokázal.
    r = subprocess.run(
        ["git", "-C", str(HRA), "check-ignore", "-v", "scripts/player.gd"],
        capture_output=True, text=True,
    )
    zkontroluj(
        "'scripts/player.gd' ignorovaný NENÍ (test umí i opak)",
        r.returncode != 0,
        f"herní skript se hlásí jako ignorovaný ({r.stdout.strip()!r}) –\n"
        f".gitignore je příliš široký a test v části 4 by nic nedokazoval.",
    )

    print()
    if chyb:
        print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} CHYB")
        return 1
    print(f"VÝSLEDEK: {kontrol} kontrol, 0 chyb")
    return 0


if __name__ == "__main__":
    sys.exit(main())
