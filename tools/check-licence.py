#!/usr/bin/env python
r"""Hlídá, že každý asset ve hře má evidovaný původ a povolenou licenci.

PROČ TO EXISTUJE:
Hra umí přidat asset, ale nikde nebylo, ODKUD je. U CC0 to nikoho nezajímá,
u CC-BY je uvedení autora PODMÍNKOU použití – a hra bez atribuce je právní
vada, kterou nikdo nepozná, protože se nikde neměří. Přesně to je případ
„mince 30 px vs truhla 45 px": chyba, která projde vším, protože se neměří.

CO KONTROLUJE (všechno musí projít):
  1) `assets/asset-lock.json` je čitelný a každý soubor v `assets/`, který
     nevznikl v projektu, má v něm záznam (jinak asset „přitekl" bez původu),
  2) licence je v povoleném seznamu – `cc-by-sa` je ZAKÁZANÁ (vynucuje stejnou
     licenci na celou hru, což u uzavřené hry nejde),
  3) u `cc-by` je autor uvedený v `assets/CREDITS.md`,
  4) hash v locku SOUHLASÍ se souborem na disku (pozná přepsaný/poškozený asset),
  5) `assets/CREDITS.md` odpovídá tomu, co by se vygenerovalo z locku
     (ruční editace se tím za chvíli rozešla s realitou – a u atribuce to vadí).

JAK SE CHOVÁ, KDYŽ LOCK NENÍ:
  Projde s poznámkou. Hra bez stažených assetů žádný lock mít nemusí a brána
  nemá blokovat práci, která s licencemi nemá co dělat. Aktivuje se prvním
  staženým assetem.

Použití:
    python .forge/check-licence.py <projekt nebo repo> [--json]
Návratový kód: 0 = v pořádku (i když lock chybí), 1 = nalezené vady.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Windows konzole umí cp1252 a na české výpisy by spadla na UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Co se v `assets/` neeviduje: Godot si k assetům píše .import/.uid sám a data
# jsou součástí projektu (nemají „původ" v cizím zdroji).
POMIJENE_PRIPONY = {".import", ".uid"}


def _nacti_lock(projekt: Path) -> dict | None:
    cesta = projekt / "assets" / "asset-lock.json"
    if not cesta.is_file():
        return None
    try:
        return json.loads(cesta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"assets/asset-lock.json není platný JSON: {e}") from e


def _hash_souboru(cesta: Path, algoritmus: str) -> str:
    h = hashlib.new(algoritmus)
    with cesta.open("rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def _ocekavane_credits(lock: dict) -> str:
    """Stejný text, jaký generuje orchestra/tools/asset-fetch.mjs.

    Držet generátor na dvou místech je ošklivé, ale nutné: lock i CREDITS
    vznikají v Node (fetch) a brána běží v Pythonu (CI runner nemá Node jistý).
    Aby se obě strany nemohly rozejít, brána text POROVNÁVÁ – kdyby se změnil
    generátor a ne tenhle přepis, začne to hlásit rozdíl, což je vidět.
    """
    podle_zdroje: dict[str, list[dict]] = {}
    for s in lock.get("soubory") or []:
        klic = f"{s.get('zdroj', '?')}|{s.get('licence', '?')}|{s.get('autor') or 'neuveden'}"
        podle_zdroje.setdefault(klic, []).append(s)

    radky = [
        "<!-- GENEROVÁNO: orchestra/tools/asset-fetch.mjs – needituj ručně -->",
        "# Poděkování a licence assetů",
        "",
        "Assety třetích stran použité v tomto projektu. U licencí CC-BY je uvedení",
        "autora PODMÍNKOU použití, proto tenhle soubor není dobrovolný.",
        "",
    ]
    for klic in sorted(podle_zdroje):
        zdroj, licence, autor = klic.split("|")
        soubory = podle_zdroje[klic]
        radky += [f"## {zdroj} — {licence.upper()}", "", f"- Autor: {autor}"]
        if soubory[0].get("url"):
            radky.append(f"- Zdroj: {soubory[0]['url']}")
        if soubory[0].get("web"):
            radky.append(f"- Web: {soubory[0]['web']}")
        radky.append(f"- Soubory ({len(soubory)}):")
        for jmeno in sorted(s.get("soubor", "?") for s in soubory):
            radky.append(f"  - `{jmeno}`")
        radky.append("")
    radky += [
        "## Vlastní a vygenerované assety",
        "",
        "Assety vzniklé v projektu (Blender, SDXL/ComfyUI, Gemini) jsou uvedené",
        "v `asset-lock.json` se zdrojem `vlastni` a licencí projektu.",
        "",
    ]
    return "\n".join(radky)


def zkontroluj(projekt: Path) -> tuple[list[str], list[str]]:
    """Vrátí (vady, poznámky). Prázdné vady = v pořádku."""
    vady: list[str] = []
    poznamky: list[str] = []

    lock = _nacti_lock(projekt)
    if lock is None:
        return [], ["assets/asset-lock.json není – hra zatím žádné stažené assety nemá (brána se aktivuje prvním)."]

    if lock.get("verze") != 1:
        vady.append(f"asset-lock.json má verzi {lock.get('verze')!r}, čekám 1")

    povolene = {str(x).lower() for x in (lock.get("povolene_licence") or [])}
    if not povolene:
        vady.append("lock nemá `povolene_licence` – bez nich se licence nedá posoudit")
    for zakazana in ("cc-by-sa", "gpl", "proprietary"):
        if zakazana in povolene:
            vady.append(f"licence {zakazana} je v povoleném seznamu – u uzavřené hry ji použít nelze")

    soubory = lock.get("soubory")
    if not isinstance(soubory, list) or not soubory:
        vady.append("lock nemá žádné záznamy v `soubory`")
        return vady, poznamky

    # 1) + 2) + 3) záznamy
    evidovane: set[str] = set()
    for z in soubory:
        jmeno = str(z.get("soubor") or "").replace("\\", "/")
        if not jmeno:
            vady.append("záznam bez `soubor`")
            continue
        evidovane.add(jmeno)
        licence = str(z.get("licence") or "").lower()
        if not licence:
            vady.append(f"{jmeno}: chybí licence")
        elif licence not in povolene:
            vady.append(f"{jmeno}: licence {licence!r} není v povoleném seznamu ({', '.join(sorted(povolene))})")
        if licence == "cc-by" and not (z.get("autor") and z["autor"] != "neuveden"):
            vady.append(f"{jmeno}: CC-BY vyžaduje autora (uvedení autora je podmínka licence)")
        if not z.get("overeno"):
            poznamky.append(f"{jmeno}: v registru je označený jako neověřený (hash nikdo neporovnal se zdrojem)")

    # 4) hashe proti souborům na disku
    for z in soubory:
        jmeno = str(z.get("soubor") or "").replace("\\", "/")
        if not jmeno:
            continue
        cesta = projekt / jmeno
        if not cesta.is_file():
            vady.append(f"{jmeno}: je v locku, ale na disku není")
            continue
        algoritmus = str(z.get("algoritmus") or "sha256")
        try:
            skutecny = _hash_souboru(cesta, algoritmus)
        except ValueError:
            vady.append(f"{jmeno}: lock uvádí neznámý algoritmus {algoritmus!r}")
            continue
        if z.get("hash") and skutecny != z["hash"]:
            vady.append(
                f"{jmeno}: hash nesouhlasí (v locku {str(z['hash'])[:12]}…, na disku {skutecny[:12]}…) "
                "– soubor byl přepsán nebo poškozen"
            )
        velikost = z.get("velikost")
        if velikost and cesta.stat().st_size != velikost:
            vady.append(f"{jmeno}: velikost nesouhlasí (lock {velikost} B, disk {cesta.stat().st_size} B)")

    # 1b) něco v assets/ bez záznamu = asset bez původu
    assets = projekt / "assets"
    if assets.is_dir():
        for cesta in sorted(assets.rglob("*")):
            if not cesta.is_file() or cesta.suffix.lower() in POMIJENE_PRIPONY:
                continue
            relativni = cesta.relative_to(projekt).as_posix()
            if relativni in evidovane or relativni == "assets/asset-lock.json" or relativni == "assets/CREDITS.md":
                continue
            # Data projektu (json) a spec jsou součást hry, ne cizí asset.
            if cesta.suffix.lower() in {".json", ".md", ".txt"} and "/data/" in f"/{relativni}":
                continue
            if relativni == "assets/spec.json":
                continue
            vady.append(f"{relativni}: v assets/ je, ale v asset-lock.json chybí (odkud je a pod jakou licencí?)")

    # 5) CREDITS.md musí odpovídat locku
    credits = projekt / "assets" / "CREDITS.md"
    if not credits.is_file():
        vady.append("assets/CREDITS.md chybí – vygeneruj ho (asset-fetch.mjs ho píše sám)")
    else:
        ocekavane = _ocekavane_credits(lock)
        skutecne = credits.read_text(encoding="utf-8")
        if skutecne.replace("\r\n", "\n").rstrip("\n") != ocekavane.rstrip("\n"):
            vady.append(
                "assets/CREDITS.md neodpovídá asset-lock.json "
                "(ruční editace, nebo se změnil generátor) – nech ho přegenerovat"
            )
        for z in soubory:
            if str(z.get("licence") or "").lower() == "cc-by":
                autor = str(z.get("autor") or "")
                if autor and autor not in skutecne:
                    vady.append(f"CC-BY asset {z.get('soubor')}: autor {autor!r} v CREDITS.md není")

    return vady, poznamky


def main() -> int:
    p = argparse.ArgumentParser(description="Kontrola licencí a původu assetů")
    p.add_argument("projekt", nargs="?", default=".", help="projekt nebo repo hry")
    p.add_argument("--json", action="store_true", help="výstup jako JSON")
    args = p.parse_args()

    projekt = Path(args.projekt).resolve()
    if not projekt.is_dir():
        print(f"CHYBA: {projekt} není složka")
        return 1

    try:
        vady, poznamky = zkontroluj(projekt)
    except ValueError as e:
        vady, poznamky = [str(e)], []

    if args.json:
        print(json.dumps({"ok": not vady, "vady": vady, "poznamky": poznamky}, ensure_ascii=False, indent=2))
        return 1 if vady else 0

    for poznamka in poznamky:
        print(f"  poznámka: {poznamka}")
    if vady:
        print(f"\nNALEZENO {len(vady)} vad:")
        for vada in vady:
            print(f"  !! {vada}")
        print(
            "\nCo s tím: soubor dohledej ve zdroji a zaeviduj ho\n"
            "  node orchestra/tools/asset-fetch.mjs --registruj --soubor <cesta> --licence <lic> --autor <kdo>\n"
            "nebo ho z projektu smaž, pokud ho hra nepoužívá."
        )
        return 1

    print("licence a původ assetů: v pořádku")
    return 0


if __name__ == "__main__":
    sys.exit(main())
