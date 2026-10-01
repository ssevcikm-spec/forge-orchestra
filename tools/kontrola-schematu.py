#!/usr/bin/env python
r"""Kontrola, že si hra neodporuje ve vizuálním schématu.

PROČ TO EXISTUJE — naměřeno 30. 9. 2026 na `uo-shadows`, kde se rozešly ČTYŘI
zdroje pravdy a každý tvrdil jiné číslo:

    deklarace   assets/spec.json          96×48 dlaždice, viewport 960×540
    vykreslení  scripts/level.gd          16px buňka, osově zarovnaný čtverec
    dlaždice    assets/tiles/*.png        32×32 (a tiles/manifest.json: 32)
    logika      scripts/world.gd          32px buňka + izometrická projekce

Důsledek: `spec.json` slibuje izometrii 2:1, ale `level.gd` kreslí osově
zarovnané čtverce – takže izometrický pohled nemůže vzniknout, ať se sebevíc
ladí sprity. Nikdo si toho nevšiml, protože se to NIKDE neporovnávalo.

PROČ PER-GAME: schéma není globální konstanta. Izometrická hra má jiné dlaždice
než side-scroller nebo top-down. Zdroj pravdy je proto `assets/spec.json`
KAŽDÉ hry; tenhle nástroj ho jen čte a porovnává se skutečností. Nepředepisuje
žádné konkrétní číslo – jen to, že všechny vrstvy musí říkat totéž.

Použití:
    python orchestra/tools/kontrola-schematu.py <cesta k repu hry>
    python orchestra/tools/kontrola-schematu.py games/uo-shadows --json
Návratový kód: 0 = v pořádku, 1 = rozpory, 2 = chybí spec (nedá se měřit).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _nacti_json(cesta: Path):
    try:
        # `utf-8-sig` odstraňuje BOM. PowerShell (`Set-Content -Encoding UTF8`)
        # i některé editory na Windows ho přidávají na začátek souboru a
        # `json.loads` na něm spadne s nesrozumitelnou hláškou. Stejná past už
        # jednou potkala `orchestra/.env` (viz orchestra/README.md).
        return json.loads(cesta.read_text(encoding="utf-8-sig"))
    except Exception as e:
        return {"_chyba": str(e)}


def _cisla_z_gd(text: str, vzor: str) -> list[int]:
    """Vytáhne čísla z deklarace v GDScriptu (např. `var cell := 16`)."""
    out = []
    for m in re.finditer(vzor, text):
        try:
            out.append(int(m.group(1)))
        except (TypeError, ValueError):
            pass
    return out


def zkontroluj(repo: Path) -> tuple[list[str], list[str], list[str], dict]:
    """Vrátí (vady, varování, poznámky, naměřeno)."""
    vady: list[str] = []
    varovani: list[str] = []
    poznamky: list[str] = []
    data: dict = {}

    # ---------------------------------------------------------- deklarace ----
    spec_cesta = repo / "assets" / "spec.json"
    if not spec_cesta.is_file():
        return ([f"chybí {spec_cesta} – bez specu se schéma měřit nedá"], [], [], {})
    spec = _nacti_json(spec_cesta)
    if "_chyba" in spec:
        return ([f"{spec_cesta} není platné JSON: {spec['_chyba']}"], [], [], {})

    # Schéma může být zapsané dvěma způsoby – bere se, co hra má:
    #   A) `tile: {sirka, vyska}` + `viewport`   (uo-shadows)
    #   B) `projekce: {...}`                      (obecnější, pro jiné hry)
    proj = spec.get("projekce", {})
    tile = spec.get("tile", {})
    projekce = str(proj.get("typ") or spec.get("projekce_typ") or "").lower()
    if not projekce:
        # odvození z dlaždice: 2:1 znamená izometrii, 1:1 čtverec
        sirka, vyska = tile.get("sirka"), tile.get("vyska")
        if sirka and vyska:
            projekce = "izometricka" if int(sirka) != int(vyska) else "ctvercova"
    tile_w = proj.get("dlazdice_sirka") or tile.get("sirka")
    tile_h = proj.get("dlazdice_vyska") or tile.get("vyska")
    viewport = proj.get("viewport") or spec.get("viewport")

    data["deklarace"] = {"projekce": projekce, "dlazdice": [tile_w, tile_h],
                         "viewport": viewport}

    if not tile_w or not tile_h:
        vady.append("spec.json nedeklaruje velikost dlaždice (tile.sirka/vyska "
                    "nebo projekce.dlazdice_sirka/vyska) – není co porovnávat")
    if projekce not in ("izometricka", "izometrická", "iso", "ctvercova", "čtvercová", "square"):
        varovani.append(f"neznámý typ projekce '{projekce}' – porovnávám jen čísla")

    # ------------------------------------------------------------ mapy -------
    urovne = sorted((repo / "assets" / "levels").glob("*.json"))
    urovne = [p for p in urovne if p.name != "manifest.json"]
    data["urovne"] = {}
    for u in urovne:
        d = _nacti_json(u)
        if "_chyba" in d:
            vady.append(f"{u.name} není platné JSON: {d['_chyba']}")
            continue
        cell = d.get("cell")
        data["urovne"][u.name] = {"cell": cell, "viewport": d.get("viewport"),
                                  "velikost": [d.get("width"), d.get("height")]}
        if cell is None:
            vady.append(f"{u.name}: chybí 'cell' – mapa neurčuje velikost buňky")
            continue
        # TADY se láme izometrie: buňka mapy musí odpovídat dlaždici ze specu.
        if tile_w and int(cell) != int(tile_w):
            vady.append(
                f"{u.name}: buňka mapy je {cell}px, ale spec.json deklaruje dlaždici "
                f"{tile_w}px – hra by kreslila jiné měřítko, než je schválené")
        if d.get("viewport") and viewport and list(d["viewport"]) != list(viewport):
            varovani.append(
                f"{u.name}: viewport {d['viewport']} vs. spec {viewport}")
    if not urovne:
        poznamky.append("v assets/levels nejsou žádné mapy – kontrola map přeskočena")

    # --------------------------------------------------------- vykreslení ----
    lg = repo / "scripts" / "level.gd"
    wg = repo / "scripts" / "world.gd"   # potřeba i v izometrické kontrole níž
    if lg.is_file():
        t = lg.read_text(encoding="utf-8", errors="replace")
        # KOMENTÁŘE SE ODSTRANÍ, NEŽ SE HLEDAJÍ VZORCE. Soubor v hlavičce cituje
        # STARÝ chybný vzorec jako historii – a statická kontrola ho pak najde
        # a hlásí vadu i po opravě (přesně to se stalo). Komentář popisující
        # vadu nesmí vypadat jako vada.
        t = "\n".join(radek.split("#", 1)[0] for radek in t.splitlines())
        data["level_gd"] = {}
        # `var cell := 16` = výchozí buňka; `data.get("cell", 16)` = fallback.
        vychozi = _cisla_z_gd(t, r"var\s+cell\s*:?=?\s*:?\s*int\s*:?=?\s*(\d+)")
        if not vychozi:
            vychozi = _cisla_z_gd(t, r"var\s+cell\s*:?=\s*(\d+)")
        fallback = _cisla_z_gd(t, r'get\(\s*"cell"\s*,\s*(\d+)\s*\)')
        data["level_gd"]["vychozi_cell"] = vychozi
        data["level_gd"]["fallback_cell"] = fallback
        for c in set(vychozi + fallback):
            if tile_w and c != int(tile_w):
                vady.append(
                    f"scripts/level.gd má zabudovanou buňku {c}px, spec deklaruje "
                    f"{tile_w}px – při chybějícím 'cell' v datech se hra potichu "
                    f"překreslí na jiné měřítko")
        # Izometrie se v datech pozná tak, že buňka má různou šířku a výšku.
        # Čtvercová buňka + deklarovaná izometrie = izometrie nemůže vzniknout.
        if projekce.startswith("izo") and tile_w and tile_h and int(tile_w) == int(tile_h):
            poznamky.append("spec deklaruje izometrii se čtvercovou dlaždicí – "
                            "ovzorkování je na specu, ne na téhle kontrole")
        if projekce.startswith("izo") and tile_w and tile_h and int(tile_w) != int(tile_h):
            # Izometrie se ověřuje TŘEMI nezávislými znaky, protože hledat
            # jeden konkrétní vzorec je křehké: kontrola pak hlásí vadu i po
            # opravě (přesně to se stalo – `level.gd` se přepsal na izometrii
            # a kontrola dál tvrdila, že kreslí čtvercově, protože hledala
            # starý text). Falešný poplach nutí „opravovat" správný kód.
            stary_ctverec = bool(re.search(r"Vector2\(\s*\w+\s*\*\s*cell\s*,", t))
            cte_spec = bool(re.search(r"SPEC_PATH|spec\.json|projekce", t))
            ma_iso_metodu = bool(re.search(r"je_izometricka|iso_position|iso_z", t))
            if stary_ctverec:
                vady.append(
                    "spec.json deklaruje IZOMETRICKOU projekci (dlaždice "
                    f"{tile_w}×{tile_h}), ale scripts/level.gd staví dlaždice osově "
                    "zarovnaně (Vector2(x * cell, y * cell)) – izometrický pohled "
                    "takto nemůže vzniknout, ať se sprity ladí jakkoli")
            elif not cte_spec and not ma_iso_metodu:
                # „NEDÁ SE POSOUDIT" NENÍ VADA. Když kód neumíme přečíst, řekne
                # se to jako poznámka – vymyslet z toho vadu by bylo horší.
                poznamky.append(
                    "level.gd nevypadá ani čtvercově, ani izometricky – projekci "
                    "nejde z kódu posoudit (zkontroluj to očima)")
            if not ma_iso_metodu:
                wg_txt = ""
                if wg.is_file():
                    wg_txt = wg.read_text(encoding="utf-8", errors="replace")
                if re.search(r"iso_position", wg_txt):
                    vady.append(
                        "izometrická projekce je jen v scripts/world.gd (iso_position), "
                        "ale level.gd ji nepoužívá – izometrie tedy v projektu NENÍ, "
                        "jen v komentáři")
    else:
        poznamky.append("scripts/level.gd není – kontrola vykreslování přeskočena")

    # ------------------------------------------- druhá logika (riziko dvou) --
    if wg.is_file():
        t = wg.read_text(encoding="utf-8", errors="replace")
        wcell = _cisla_z_gd(t, r"const\s+cell\s*:?\s*int\s*:?=\s*(\d+)")
        ma_iso = bool(re.search(r"iso_position", t))
        data["world_gd"] = {"cell": wcell, "iso": ma_iso}
        for c in wcell:
            if tile_w and c != int(tile_w):
                vady.append(
                    f"scripts/world.gd má cell={c}px, spec deklaruje {tile_w}px "
                    f"– DVĚ různé představy o mřížce v jednom projektu")
        if ma_iso and tile_w:
            if int(tile_w) % 4 != 0:
                vady.append(
                    f"izometrický vzorec v world.gd dělí cell/4; {tile_w} není "
                    f"dělitelné 4 → celočíselné dělení potichu zkreslí projekci")
            poznamky.append(
                "world.gd nese izometrickou projekci, ale level.gd kreslí čtvercově "
                "– ověř, který z nich je skutečně zapojený (dnes se zdá, že level.gd)")

    # ----------------------------------------------------------- dlaždice ----
    tm = repo / "assets" / "tiles" / "manifest.json"
    if tm.is_file():
        d = _nacti_json(tm)
        ts = d.get("tile_size")
        data["tiles_manifest"] = {"tile_size": ts}
        # `tile_size` může být ČÍSLO (čtvercová dlaždice: 32) i SEZNAM
        # (kosočtverec: [96, 48]). První verze kontroly počítala jen s číslem
        # a na seznam spadla na TypeError – což je něco jiného než „našla vadu".
        if isinstance(ts, (list, tuple)):
            ts_w = int(ts[0]) if len(ts) > 0 else None
            ts_h = int(ts[1]) if len(ts) > 1 else ts_w
        elif ts is not None:
            ts_w = ts_h = int(ts)
        else:
            ts_w = ts_h = None
        if ts_w and tile_w and tile_h:
            if ts_w != int(tile_w) or ts_h != int(tile_h):
                vady.append(
                    f"assets/tiles/manifest.json: tile_size {ts_w}×{ts_h}, spec "
                    f"deklaruje {tile_w}×{tile_h} – dlaždice se ve hře škálují")
    else:
        poznamky.append("assets/tiles/manifest.json není – dlaždice nelze ověřit")

    # ------------------------------------------------------------ sprity -----
    role = spec.get("role", {})
    sp = repo / "assets" / "sprites"
    if role and sp.is_dir():
        from PIL import Image  # lokální import: bez spritů není potřeba
        nesedí = []
        for jmeno, pozadovano in role.items():
            f = sp / f"{jmeno}.png"
            if not f.is_file():
                continue
            canvas = pozadovano.get("canvas")
            if not canvas:
                continue
            w, h = Image.open(f).size
            if w != int(canvas) or h != int(canvas):
                nesedí.append(f"{jmeno}.png je {w}×{h}, spec chce plátno {canvas}×{canvas}")
        data["sprity"] = {"zkontrolovano": len(role), "nesedi": nesedí}
        vady += nesedí

    return vady, varovani, poznamky, data


def main() -> int:
    ap = argparse.ArgumentParser(description="Kontrola vizuálního schématu hry")
    ap.add_argument("repo", nargs="?", default=".",
                    help="cesta k repu hry (výchozí: aktuální složka)")
    ap.add_argument("--json", action="store_true", help="vypsat i naměřená data")
    args = ap.parse_args()

    repo = Path(args.repo)
    if not repo.is_dir():
        print(f"CHYBA: {repo} není složka")
        return 2

    vady, varovani, poznamky, data = zkontroluj(repo)

    d = data.get("deklarace", {})
    print(f"Kontrola schématu: {repo}")
    print(f"  spec.json deklaruje: projekce={d.get('projekce') or '?'}, "
          f"dlaždice={d.get('dlazdice')}, viewport={d.get('viewport')}")
    for jmeno, m in data.get("urovne", {}).items():
        print(f"  mapa {jmeno:14s} cell={m['cell']}  viewport={m['viewport']}  "
              f"mřížka={m['velikost']}")
    if data.get("level_gd"):
        print(f"  level.gd: výchozí cell={data['level_gd']['vychozi_cell']}, "
              f"fallback={data['level_gd']['fallback_cell']}")
    if data.get("world_gd"):
        print(f"  world.gd: cell={data['world_gd']['cell']}, "
              f"izometrie={'ano' if data['world_gd']['iso'] else 'ne'}")
    if data.get("tiles_manifest"):
        print(f"  tiles/manifest.json: tile_size={data['tiles_manifest']['tile_size']}")
    if data.get("sprity"):
        print(f"  sprity: zkontrolováno {data['sprity']['zkontrolovano']}, "
              f"nesedí {len(data['sprity']['nesedi'])}")

    for p in poznamky:
        print(f"  poznámka: {p}")
    for v in varovani:
        print(f"  VAROVÁNÍ: {v}")
    if vady:
        print(f"\nROZPORY ({len(vady)}):")
        for v in vady:
            print(f"  - {v}")
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))

    if vady:
        print("\nSCHÉMA SI ODPORUJE – vizuální kontroly nemají proti čemu měřit.")
        return 1
    print("\nSchéma je v souladu: deklarace, mapy, vykreslení i dlaždice říkají totéž.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
