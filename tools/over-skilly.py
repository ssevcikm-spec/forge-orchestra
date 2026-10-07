r"""Ověří, že se všechny skilly načítají: frontmatter je platný YAML a má name+description.

⚠ ROZŠÍŘENO 6. 10. 2026 (P22) — PRAVDIVOST CEST. Do té doby brána měřila jen
front-matter, počet řádků a délku description, a proto byla ZELENÁ nad skilly,
ve kterých **23 cest v 10 ze 17 souborů neexistovalo** (audit KB, `_tools\over-cesty-v-kb.mjs`):
např. `orchestra\tools\godot\` (Godot je `E:\Tools\godot\`), `_analyza\hl-bom.py`
(přesunut do `_analyza\_archiv\`), `E:\DSH\data\sessions` (dnes `E:\DeepSeekHarness-data\`).
Skill, který má učit pasti prostředí a sám posílá agenta k nástroji, který není,
vyrábí falešný závěr „nástroj neexistuje".

⚠ KONTROLUJÍ SE JEN CESTY K NÁSTROJŮM PROJEKTU (`_analyza\…`, `tools\…`) — a to
záměrně: systémové cesty a **historické zmínky** („cesta X už neexistuje",
přeškrtnuté) jsou legitimní a jejich plošná kontrola vyrábí **falešné poplachy**,
které nutí „opravovat" správný text. Naměřeno: plošný sken hlásil 45 „mrtvých"
cest, z toho po filtraci zůstalo 7 a **všechny byly legitimní**.
"""

import os
import pathlib
import re
import sys

import yaml

# ⚠ CESTY SE ODVOZUJÍ, NEZAPEKAJÍ (generalizace, 7. 10. 2026). Dřív tu byly
# literály `C:\Users\Ssevc\…`, takže nástroj šel použít jen na téhle stanici.
# Hodnoty jsou tu SHODNÉ s dřívějšími literály — mění se jen přenositelnost.
REPO = pathlib.Path(__file__).resolve().parents[1]
DSH = pathlib.Path(os.environ.get("DSH_HOME") or pathlib.Path.home() / ".dsh")
SKILLS = DSH / "skills"

# Kořeny, proti kterým se cesta k nástroji zkouší (projekt orchestra a hra).
# `HRA` je sestra tohohle repa (vzor z `g3-brany.py`), takže se odvozuje odsud.
KORENY = [REPO, REPO.parent / "uo-shadows"]
HRA = REPO.parent / "uo-shadows"

# ⚠ PŘIDÁNO 7. 10. 2026 (optimalizace KB, Úkoly A+B): skilly `orchestra` a
# `game-developer` část znalosti **přesunuly** do projektových dokumentů
# (místo aby ji nosily v sobě). Tím by ale ta znalost **vypadla z týhle
# kontroly** — cesty k nástrojům by se přestaly ověřovat, protože kontrola
# dosud skenovala jen `SKILL.md`. Naměřeno: ve skillu `orchestra` bylo
# 40+ odkazů na nástroje; po přesunu by kontrola měřila 26 a **mlčela by
# o zbytku**. Kontrola se proto rozšiřuje na dokumenty, na které skilly
# odkazují — a jejich **existence je sama kontrolou** (když dokument zmizí,
# skill posílá agenta nikam).
NAVAZANE = [
    REPO / "PROVOZ-ORCHESTRA.md",
    HRA / "docs" / "BRANY-HRY.md",
]
# ⚠ PŘEPIS PRO MUTAČNÍ TEST (`_analyza\test-over-skilly-delegovane.py`):
# `FORGE_NAVAZANE` = cesty oddělené `;`. Test tak měří na FIXTURÁCH a **nesahá
# na živé dokumenty** — naměřeno 7. 10. 2026 (P24): přerušený mutační běh nad
# živým souborem nechal v kódu čtyři mutanty a `git status` byl přitom čistý.
_over = os.environ.get("FORGE_NAVAZANE")
if _over:
    NAVAZANE = [pathlib.Path(x) for x in _over.split(";") if x.strip()]

# Cesty k nástrojům projektu v backticích (např. `_analyza\g3-brany.py`, `tools\over-skilly.py`).
VZOR_CESTY = re.compile(r"`((?:_analyza|tools)[\\/][^\s`\"']+)`")

# ⚠ DEKLAROVANÉ VÝJIMKY: cesty, které v textu být MOHOU, i když soubor neexistuje.
# Každá má důvod; NOVÁ mrtvá cesta bránu SHODÍ (to je smysl kontroly).
OCEKAVANE = {
    # příklad: (jmeno_skillu, "cesta"): "důvod",
}

# ⚠ DEKLAROVANÉ VÝJIMKY pro DELEGOVANÉ dokumenty (stejný smysl jako `OCEKAVANE`).
# Historické zmínky se odchytávají slovem v řádku („neexistuje", „už není",
# „smazán", „~~"); sem patří jen cesty, které slovem odchytit nelze.
# Každá výjimka musí mít důvod — nová mrtvá cesta bránu SHODÍ.
OCEKAVANE_DELEGOVANE = {
    # (zatím prázdné — oba dokumenty mají mrtvé cesty jen v historických
    #  zmínkách, a ty jsou označené slovem)
}
vsech_cest = 0
mrtvych = 0
podezrele = []

chyb = 0
for d in sorted(SKILLS.iterdir()):
    if not d.is_dir():
        continue
    p = d / "SKILL.md"
    if not p.exists():
        print(f"  CHYBA {d.name}: SKILL.md chybí")
        chyb += 1
        continue
    t = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        print(f"  CHYBA {d.name}: frontmatter nenalezen")
        chyb += 1
        continue
    try:
        fm = yaml.safe_load(m.group(1))
    except Exception as e:
        print(f"  CHYBA {d.name}: frontmatter není platný YAML – {e}")
        chyb += 1
        continue
    name = fm.get("name")
    desc = str(fm.get("description", ""))
    telo = len(t.splitlines())
    if name != d.name:
        print(f"  CHYBA {d.name}: name v frontmatteru je '{name}' (má být '{d.name}')")
        chyb += 1
        continue
    if not desc:
        print(f"  CHYBA {d.name}: chybí description")
        chyb += 1
        continue

    # --- PRAVDIVOST CEST (nové, P22) ------------------------------------------
    radky = t.splitlines()
    mrtve_tady = []
    for i, radek in enumerate(radky, 1):
        for mm in VZOR_CESTY.finditer(radek):
            cesta = mm.group(1).rstrip(".,;:")
            # Vzory s `*` nejsou cesty (např. `tools/blender/sprites/body_d0_f*.png`).
            if "*" in cesta or "?" in cesta:
                continue
            vsech_cest += 1
            if (d.name, cesta) in OCEKAVANE:
                continue
            if any((k / cesta).exists() for k in KORENY):
                continue
            # Zmínka o neexistující cestě, kterou text SÁM přiznává, není vada.
            if re.search(r"neexistuje|už není|smazán|odstraněn|~~", radek, re.I):
                continue
            mrtve_tady.append((i, cesta))
    if mrtve_tady:
        mrtvych += len(mrtve_tady)
        podezrele.append((d.name, mrtve_tady))
        chyb += 1

    stav = "" if not mrtve_tady else f"  ⚠ MRTVÝCH CEST: {len(mrtve_tady)}"
    print(f"  OK   {d.name:16} řádků={telo:4} description={len(desc)} znaků{stav}")

for jmeno, mrtve in podezrele:
    print(f"  CHYBA {jmeno}: odkazuje na {len(mrtve)} cest, které NEEXISTUJÍ:")
    for i, cesta in mrtve:
        print(f"        ř. {i}: {cesta}")

# --- PRAVDIVOST CEST V DOKUMENTECH, NA KTERÉ SKILLY ODKAZUJÍ (7. 10. 2026) ----
# Stejná pravidla jako u skillů; mění se jen zdroj textu. Cesty se počítají do
# týchž čítačů, takže pokrytí přesunem NEKLESLO.
for p in NAVAZANE:
    if not p.exists():
        print(f"  CHYBA delegovaný dokument NEEXISTUJE: {p}")
        chyb += 1
        continue
    mrtve_tady = []
    for i, radek in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        for mm in VZOR_CESTY.finditer(radek):
            cesta = mm.group(1).rstrip(".,;:")
            if "*" in cesta or "?" in cesta:
                continue
            vsech_cest += 1
            if cesta in OCEKAVANE_DELEGOVANE:
                continue
            if any((k / cesta).exists() for k in KORENY):
                continue
            if re.search(r"neexistuje|už není|smazán|odstraněn|~~", radek, re.I):
                continue
            mrtve_tady.append((i, cesta))
    if mrtve_tady:
        mrtvych += len(mrtve_tady)
        chyb += 1
        print(f"  CHYBA {p.name}: odkazuje na {len(mrtve_tady)} cest, které NEEXISTUJÍ:")
        for i, cesta in mrtve_tady:
            print(f"        ř. {i}: {cesta}")
    else:
        print(f"  OK   {p.name:22} (delegovaný dokument, cesty v pořádku)")

print()
print(f"Skillů: {len([x for x in SKILLS.iterdir() if x.is_dir()])}, chyb: {chyb}")
print(f"Cesty k nástrojům: {vsech_cest} zmínek, {mrtvych} mrtvých")
print("VŠE OK" if chyb == 0 else "NALEZENY CHYBY")
sys.exit(0 if chyb == 0 else 1)
