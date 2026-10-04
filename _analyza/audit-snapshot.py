r"""ÚKOL 0 z `ZADANI-DOKONCENI-AUDITU.md` — ZMRAZIT SNAPSHOT (dělej první).

PROČ TO EXISTUJE (naměřeno v auditu, 2. 10. 2026): audit dokumentace se v tomhle
workspace NEDÁ dělat na živých datech. Během auditu pracovala v témže workspace
jiná session a `HANDOFF.md`, `AGENTS.md`, `NEXT-SESSION-INSTRUKCE.md`,
`PLAN-DALSI-KROK.md` i dva skilly se mu změnily pod rukama (mtime 17:31–17:38).
Naměřené číslo pak nešlo porovnat s ničím — nebyl snímek "předtím".

CO DĚLÁ
  1. Zkopíruje do `_analyza\snapshot-<RRRRMMDD-HHMM>\`:
       - JÁDRO — 8 dokumentů (stejný seznam jako `audit1-inventar.py:51`)
       - KOŘEN — všechny `.md` v kořeni workspace (dynamicky, ne ruční počet)
       - SKILLY — 12 skillů z `~\.dsh\skills\` (adresář, který má `SKILL.md`)
  2. Zapíše `manifest.json` s **SHA-256, velikostí a mtime** KAŽDÉHO souboru.
  3. Při dalším spuštění VYPÍŠE, co se od minula změnilo (porovnáním hashů).
  4. Skončí `exit 1`, když se některý soubor změnil od posledního snapshotu.

TŘI ROZHODNUTÍ, KTERÁ NEJSOU SAMOZŘEJMÁ (a mají naměřený důvod):

  * **Kořen se bere DYNAMICKY** (`glob("*.md")`), ne ručním počtem 37 ze zadání.
    Naměřeno: zadání tvrdí "všech 37 `.md` v kořeni", živě jich je **38** —
    o 18:09:30 přibyl sám `ZADANI-DOKONCENI-AUDITU.md`. Ruční seznam by tu
    změnu zamlčel; je to táž vada jako S27 (ruční seznam místo projití složky).

  * **Skilly se berou podle `SKILL.md`, ne podle seznamu jmen.** Složka
    `~\.dsh\skills\` obsahuje i `PIL`, `lib`, `__pycache__` a
    `pillow-12.3.0.dist-info` (dohromady ~15 MB). Kdyby se bralo "všechno ve
    složce", snapshot by měl 15 MB vendored knihovny místo 270 kB skutečných
    skillů — a `imagegen\lib\pylibs` by se do snímku dostal jako "změna"
    při každém přeinstalování Pillowu.

  * **`_analyza\snapshot-*\` se NESKENUJE.** Jinak by se každý další snapshot
    stal vstupem toho předchozího a otisk by nikdy nesedl.

CO SNAPSHOT NENÍ: není to brána do `g3-brany.py` — záměrně. Změna dokumentace
je NORMÁLNÍ stav (každá session píše do `HANDOFF.md`), takže brána, která na ni
padá, by byla brána, která nemá jak nespadnout. Je to **měřidlo**, ne kontrola:
říká "co se hnulo", a `exit 1` znamená "hnulo se to", ne "je to špatně".

Spuštění:
  $env:PYTHONIOENCODING='utf-8'
  python _analyza\audit-snapshot.py                    # zmrazí + porovná s posledním
  python _analyza\audit-snapshot.py --proti <slozka>   # porovná s KONKRÉTNÍM snapshotem
  python _analyza\audit-snapshot.py --jen-kontrola     # nic nekopíruje, jen porovná
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"
SKILLS = pathlib.Path.home() / ".dsh" / "skills"

# Jádro = dokumenty, ze kterých se řídí každá session (viz AGENTS.md „Kam pro co").
# Převzato z `audit1-inventar.py:51` — jeden zdroj pravdy, ne druhý opis.
JADRO = ["AGENTS.md", "HANDOFF.md", "PREDAVANI-SESSION.md", "KRONIKA-PROJEKTU.md",
         "PLAN-DALSI-KROK.md", "NEXT-SESSION-INSTRUKCE.md", "MOZNOSTI-AGENTA.md",
         "OTEVRENA-TEMATA.md"]

# Co se uvnitř skillu nekopíruje: vendored knihovny a cache.
VYLUCENE_V_SKILLU = ("__pycache__", "lib", "node_modules", ".git")


def sha256(bajty: bytes) -> str:
    return hashlib.sha256(bajty).hexdigest()


def sesbirej():
    """Vrátí seznam dvojic (klic_v_manifestu, absolutni_cesta, skupina, kam_v_snimku)."""
    polozky = []
    for jmeno in JADRO:
        p = WS / jmeno
        if p.is_file():
            polozky.append(("jadro/%s" % jmeno, p, "jadro", pathlib.Path("jadro") / jmeno))
        else:
            print("  !! CHYBI dokument jadra: %s" % jmeno)

    for p in sorted(WS.glob("*.md")):
        polozky.append(("koren/%s" % p.name, p, "koren", pathlib.Path("koren") / p.name))

    if not SKILLS.is_dir():
        print("  !! CHYBI slozka skillu: %s" % SKILLS)
    else:
        for d in sorted(SKILLS.iterdir()):
            if not d.is_dir() or not (d / "SKILL.md").is_file():
                continue
            for f in sorted(d.rglob("*")):
                if not f.is_file():
                    continue
                if any(cast in f.parts for cast in VYLUCENE_V_SKILLU):
                    continue
                rel = f.relative_to(SKILLS)
                polozky.append(("skill/%s" % rel.as_posix(), f, "skill",
                                pathlib.Path("skill") / rel))
    return polozky


def otisk(polozky):
    """Načte bajty JEDNOU a vrátí (manifest, bajty podle klíče)."""
    soubory = {}
    bajty_podle_klice = {}
    for klic, cesta, skupina, cil in polozky:
        bajty = cesta.read_bytes()
        st = cesta.stat()
        soubory[klic] = {
            "skupina": skupina,
            "zdroj": str(cesta),
            "sha256": sha256(bajty),
            "bajtu": len(bajty),
            "mtime": st.st_mtime,
            "mtime_iso": datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
        }
        bajty_podle_klice[klic] = (bajty, cil)
    return soubory, bajty_podle_klice


def nacti_manifest(slozka: pathlib.Path):
    m = slozka / "manifest.json"
    if not m.is_file():
        return None
    return json.loads(m.read_text(encoding="utf-8"))


def najdi_posledni():
    if not ANALYZA.is_dir():
        return None
    kandidati = [d for d in ANALYZA.glob("snapshot-*")
                 if d.is_dir() and (d / "manifest.json").is_file()]
    if not kandidati:
        return None
    return max(kandidati, key=lambda d: d.name)


def porovnej(stary, novy):
    """Vrátí tři seznamy: (pridane, odebrane, zmenene), kde zmenene je slovník."""
    klice_stare, klice_nove = set(stary), set(novy)
    pridane = sorted(klice_nove - klice_stare)
    odebrane = sorted(klice_stare - klice_nove)
    zmenene = {}
    for k in sorted(klice_nove & klice_stare):
        a, b = stary[k], novy[k]
        if a.get("sha256") != b.get("sha256"):
            zmenene[k] = ("obsah", a, b)
        elif a.get("mtime") != b.get("mtime"):
            zmenene[k] = ("jen mtime", a, b)
    return pridane, odebrane, zmenene


def main():
    ap = argparse.ArgumentParser(description="Zmrazi snapshot dokumentace a porovnej s minulym.")
    ap.add_argument("--proti", metavar="SLOZKA",
                    help="porovnej s timto snapshotem (vychozi: posledni v _analyza)")
    ap.add_argument("--jen-kontrola", action="store_true",
                    help="nekopiruj nic, jen porovnej se stavem na disku")
    args = ap.parse_args()

    ted = datetime.datetime.now()
    print("=" * 92)
    print("SNAPSHOT DOKUMENTACE — %s" % ted.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 92)

    polozky = sesbirej()
    if not polozky:
        print("NEZMERENO: neposbiraly se ZADNE soubory — to neni uspech, to je vada.")
        sys.exit(2)

    skupiny = {}
    for _, _, skupina, _ in polozky:
        skupiny[skupina] = skupiny.get(skupina, 0) + 1

    soubory, bajty_podle_klice = otisk(polozky)

    # ── Kontrola pokrytí: kazdy soubor MUSI mit hash ────────────────────────
    bez_hashe = [k for k, z in soubory.items() if not z.get("sha256")]
    assert not bez_hashe, "soubor bez hashe: %s" % bez_hashe
    print("\n  ZMERENO: souboru=%d  (jadro=%d, koren=%d, skilly=%d)"
          % (len(soubory), skupiny.get("jadro", 0), skupiny.get("koren", 0),
             skupiny.get("skill", 0)))
    print("           bajtu celkem=%d, bez hashe=%d"
          % (sum(z["bajtu"] for z in soubory.values()), len(bez_hashe)))
    print("           skillu (adresaru s SKILL.md)=%d"
          % len({k.split("/")[1] for k in soubory if k.startswith("skill/")}))

    # ── Predchozi snapshot ──────────────────────────────────────────────────
    if args.proti:
        predchozi_slozka = pathlib.Path(args.proti)
        if not predchozi_slozka.is_absolute():
            predchozi_slozka = WS / predchozi_slozka
        if not (predchozi_slozka / "manifest.json").is_file():
            print("  !! --proti %s neobsahuje manifest.json" % predchozi_slozka)
            sys.exit(2)
    else:
        predchozi_slozka = najdi_posledni()

    stary = nacti_manifest(predchozi_slozka) if predchozi_slozka else None

    # ── Zapis noveho snapshotu ──────────────────────────────────────────────
    cilova = None
    if not args.jen_kontrola:
        cilova = ANALYZA / ("snapshot-%s" % ted.strftime("%Y%m%d-%H%M%S"))
        if cilova.exists():
            print("  !! cilova slozka uz existuje: %s" % cilova)
            sys.exit(2)
        for klic, (bajty, cil) in bajty_podle_klice.items():
            kam = cilova / cil
            kam.parent.mkdir(parents=True, exist_ok=True)
            kam.write_bytes(bajty)
        manifest = {
            "vytvoreno": ted.isoformat(timespec="seconds"),
            "pocet_souboru": len(soubory),
            "po_skupinach": skupiny,
            "jadro_seznam": JADRO,
            "zdroj_skillu": str(SKILLS),
            "soubory": soubory,
        }
        (cilova / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8", newline="\n")
        print("\n  ZAPSANO: %s" % cilova.relative_to(WS))
        print("           manifest.json: %d souboru, kazdy s hashem"
              % len(soubory))

    if stary is None:
        print("\n  ZADNY PREDCHOZI SNAPSHOT — neni co porovnat.")
        print("  STAV: NEZMERENO (neni to zelena, je to prvni snimek).")
        print("  Podruhe uz tohle ticho nedostanes: druhy beh ROZDILY VYPISE.")
        sys.exit(0)

    # ── Porovnani ───────────────────────────────────────────────────────────
    pridane, odebrane, zmenene = porovnej(stary["soubory"], soubory)
    obsah = {k: v for k, v in zmenene.items() if v[0] == "obsah"}
    jen_mtime = {k: v for k, v in zmenene.items() if v[0] == "jen mtime"}

    print("\n" + "-" * 92)
    print("POROVNANI s %s (vytvoreno %s)"
          % (predchozi_slozka.name, stary.get("vytvoreno", "?")))
    print("-" * 92)
    print("  souboru tenkrat=%d, ted=%d" % (stary.get("pocet_souboru", -1), len(soubory)))
    print("  zmenenych OBSAHEM=%d · pridanych=%d · odebranych=%d · jen mtime=%d"
          % (len(obsah), len(pridane), len(odebrane), len(jen_mtime)))

    for popis, mnozina in (("ZMENENY OBSAH", obsah), ("PRIDANY", pridane),
                           ("ODEBRANY", odebrane), ("JEN MTIME", jen_mtime)):
        if not mnozina:
            continue
        print("\n  %s (%d):" % (popis, len(mnozina)))
        for k in sorted(mnozina):
            if k in obsah or k in jen_mtime:
                a, b = zmenene[k][1], zmenene[k][2]
                print("    %-52s %d B -> %d B   %s -> %s"
                      % (k, a["bajtu"], b["bajtu"], a["mtime_iso"], b["mtime_iso"]))
            else:
                print("    %s" % k)

    zmeneno_celkem = len(obsah) + len(pridane) + len(odebrane)
    print()
    if zmeneno_celkem:
        print("VYSLEDEK: dokumentace se od posledniho snapshotu ZMENILA "
              "(%d souboru) -> exit 1." % zmeneno_celkem)
        print("          Pozor na vyklad: tohle NENI nalez o vade. Je to mereni")
        print("          'hnulo se to' — kdo pise do HANDOFF.md, meni ho vzdy.")
        sys.exit(1)
    print("VYSLEDEK: zadny soubor se nezmenil (%d souboru, vsechny hashe shodne)."
          % len(soubory))
    sys.exit(0)


if __name__ == "__main__":
    main()
