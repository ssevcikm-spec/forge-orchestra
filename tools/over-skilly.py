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
# ⚠ PŘEPIS PRO MUTAČNÍ TEST (`_analyza\test-over-skilly-delegovane.py`): cesty ke
# skillům oddělené `;`. Test měří část o DELEGOVANÝCH DOKUMENTECH — a bez tohohle
# přepisu by jeho „zdravá fixtura → exit 0" padalo kvůli **cizímu** skillu
# (naměřeno 8. 10. 2026 v P27: nový skill `dialog-s-uzivatelem` měl neplatný YAML
# a test kvůli tomu hlásil 2 chyby, i když s delegovanými cestami neměl nic
# společného). Test tak měří SVOU věc, ne stav cizích skillů.
_over_s = os.environ.get("FORGE_SKILLS")
if _over_s:
    SKILLS = pathlib.Path(_over_s)

# Kořeny, proti kterým se cesta k nástroji zkouší (projekt orchestra a hra).
# `HRA` je sestra tohohle repa (vzor z `g3-brany.py`), takže se odvozuje odsud.
#
# ⚠ ROZŠÍŘENO 8. 10. 2026 (P27 — nález P27-R, rozhodnutí **B5**): skilly jsou
# **STANIČNÍ** (učí agenta napříč projekty), takže cesta v nich může patřit
# **JINÉMU projektu** než orchestra. Naměřeno: skill `game-developer` (přepsaný
# cizí session) odkazuje na `tools/plan-status.py` a `tools/roadmap-gen.py` —
# ty existují v sourozenci `E:\Workspaces\game-clone` — a brána je hlásila jako
# **MRTVÉ**, protože znala jen orchestra + hru. To je **falešný poplach**, a ten
# se hledá hůř než slepé místo: nutil „opravovat" správný text a shazoval `g3`.
# **Rozhodnutí:** cesta se uzná, když existuje v orchestře, ve hře, **nebo
# v některém sourozeneckém projektu** (adresář v `REPO.parent`, který má `.git`).
# **Skutečně mrtvá cesta (nikde v projektech) bránu SHODÍ dál** — o to tu jde.
# A co se našlo mimo orchestra/hru, se **vypíše jako poznámka** (rozsah musí být
# VIDĚT; tiché rozšíření rozsahu by bylo přesně ta vada, kterou P25-K popisuje).
REPO = pathlib.Path(__file__).resolve().parents[1]
HRA = REPO.parent / "uo-shadows"


def _projekty() -> list:
    """Projekty, proti kterým se cesty zkouší: orchestra, hra + sourozenci s `.git`."""
    koreny = [REPO, HRA]
    try:
        for d in sorted(REPO.parent.iterdir()):
            if d.is_dir() and (d / ".git").exists() and d not in koreny:
                koreny.append(d)
    except OSError:
        pass
    return koreny


KORENY = _projekty()
# ⚠ PŘEPIS PRO MUTAČNÍ TEST (stejný vzor jako `FORGE_NAVAZANE`): `FORGE_KORENY`
# = kořeny oddělené `;`, aby test měřil na FIXTURÁCH a nesahal na živé projekty.
_over_k = os.environ.get("FORGE_KORENY")
if _over_k:
    KORENY = [pathlib.Path(x) for x in _over_k.split(";") if x.strip()]

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

# Cesty k nástrojům projektu (např. `_analyza\g3-brany.py`, `tools\over-skilly.py`).
#
# ⚠ ROZŠÍŘENO 8. 10. 2026 (P28, nález **§51.3** — „brána měří jiný TVAR cest, než
# dokumenty používají“). Do té doby se cesta hledala **POUZE hned za backtickem**.
# Naměřeno sondou `_analyza/p28-sonda-cesty.py`: v týchž dokumentech je **80
# zmínek**, brána jich viděla **65** — **15 jí unikalo** (cesty v ``` bloku,
# za `python `/`node `, v `--json …`, s `.\`). **„0 mrtvých cest“ proto NEBYLO
# důkaz.** Cesta se teď hledá **KDEKOLIV na řádku**; backtick není podmínka.
VZOR_CESTY = re.compile(r"(?<![\w\\./-])((?:_analyza|tools)[\\/][A-Za-z0-9_\-\\/.]+)")

# ⚠ DEKLAROVANÉ VÝJIMKY: cesty, které v textu být MOHOU, i když soubor neexistuje.
# Každá má důvod; NOVÁ mrtvá cesta bránu SHODÍ (to je smysl kontroly).
OCEKAVANE = {
    # ⚠ P28/B5 (8. 10. 2026): skill `vision` učí postup pro projekt, který má
    # `.python` a `tools\vision.py` — a skill to ŘÍKÁ SLOVEM ("vygeneruj si
    # testovací obrázek V REPU"). Ty cesty na TÉHLE stanici nikde nejsou; patří
    # projektu, který tu není (bot má svůj python). Je to tedy **legitimní
    # šablona, ne mrtvá cesta** — bez výjimky by je rozšířený vzor hlásil jako
    # vadu a nutil "opravovat" správný text (přesně ta past, před kterou varuje
    # hlavička tohohle souboru). Klíč je (jméno skillu, cesta) — výjimka platí
    # JEN pro ten skill; táž cesta v jiném skillu bránu pořád shodí.
    ("vision", "tools\\make_vision_test_shot.py"):
        "šablona pro projekt s vlastním .python (skill to říká slovem: „v repu“)",
    ("vision", "tools\\vision.py"):
        "šablona pro projekt s vlastním .python (skill to říká slovem: „v repu“)",
    ("vision", "tools\\vision-test-shot.png"):
        "výstup toho nástroje (testovací obrázek), ne cesta k nástroji projektu",
}

# ⚠ DEKLAROVANÉ VÝJIMKY pro DELEGOVANÉ dokumenty (stejný smysl jako `OCEKAVANE`;
# klíč je taky `(jméno dokumentu, cesta)`).
# Historické zmínky se odchytávají slovem v řádku ("neexistuje", "už není",
# "smazán", "~~"); sem patří jen cesty, které slovem odchytit nelze.
# Každá výjimka musí mít důvod — nová mrtvá cesta bránu SHODÍ.
OCEKAVANE_DELEGOVANE = {
    # (zatím prázdné — oba dokumenty mají mrtvé cesty jen v historických
    #  zmínkách, a ty jsou označené slovem)
}
vsech_cest = 0
mimo_backticku = 0      # kolik zmínek se našlo v TVARU, který brána dřív neviděla
mrtvych = 0
podezrele = []
mimo_repo = []          # cesty, které se našly v JINÉM projektu (rozsah musí být vidět)
chyb = 0


def cesty_v_textu(radky):
    """Najde cesty k nástrojům na řádcích — KDEKOLIV, ne jen za backtickem.

    Vrací `(číslo_řádku, cesta, z_backticku)`. Zástupné znaky (`*`, `?`) nejsou
    cesta: `tools/blender/sprites/body_d0_f*.png` je VZOR, ne odkaz — proto se
    zahazuje i cesta, za kterou `*`/`?` následuje (jinak by se z ní uřízl
    prefix a vypadala jako mrtvá).
    """
    nalezene = []
    for i, radek in enumerate(radky, 1):
        for mm in VZOR_CESTY.finditer(radek):
            cesta = mm.group(1).rstrip(".,;:)`")
            if "*" in cesta or "?" in cesta:
                continue
            if mm.end() < len(radek) and radek[mm.end()] in "*?":
                continue
            z_backticku = mm.start() > 0 and radek[mm.start() - 1] == "`"
            nalezene.append((i, cesta, z_backticku))
    return nalezene


def posud_cesty(radky, jmeno, ocekavane):
    """(mrtve, mimo) — táž pravidla pro skilly i delegované dokumenty.

    * cesta se uzná, když existuje v orchestře, ve hře **nebo v sourozenci**;
    * co se našlo jinde, se vrací jako `mimo` (rozsah musí být VIDĚT);
    * zmínka, kterou text SÁM přiznává, není vada;
    * deklarovaná výjimka má vždy důvod.
    """
    global vsech_cest, mimo_backticku
    mrtve, mimo = [], []
    for i, cesta, z_backticku in cesty_v_textu(radky):
        vsech_cest += 1
        if not z_backticku:
            mimo_backticku += 1
        if (jmeno, cesta) in ocekavane:
            continue
        najd = next((k for k in KORENY if (k / cesta).exists()), None)
        if najd is not None:
            if najd not in (REPO, HRA):
                mimo.append((jmeno, cesta, najd.name))
            continue
        if re.search(r"neexistuje|už není|smazán|odstraněn|~~", radky[i - 1], re.I):
            continue
        mrtve.append((i, cesta))
    return mrtve, mimo
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

    # --- PRAVDIVOST CEST (nové, P22; rozsah tvarů rozšířen P28/B5) -------------
    mrtve_tady, mimo_tady = posud_cesty(t.splitlines(), d.name, OCEKAVANE)
    mimo_repo.extend(mimo_tady)
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
    mrtve_tady, mimo_tady = posud_cesty(p.read_text(encoding="utf-8").splitlines(),
                                        p.name, OCEKAVANE_DELEGOVANE)
    mimo_repo.extend(mimo_tady)
    if mrtve_tady:
        mrtvych += len(mrtve_tady)
        chyb += 1
        print(f"  CHYBA {p.name}: odkazuje na {len(mrtve_tady)} cest, které NEEXISTUJÍ:")
        for i, cesta in mrtve_tady:
            print(f"        ř. {i}: {cesta}")
    else:
        print(f"  OK   {p.name:22} (delegovaný dokument, cesty v pořádku)")

if mimo_repo:
    projekty = sorted({x[2] for x in mimo_repo})
    print()
    print(f"  POZNÁMKA: {len(mimo_repo)} cest se našlo MIMO orchestra a hru "
          f"(skill je STANIČNÍ — patří projektu {', '.join(projekty)}):")
    for jm, cesta, projekt in mimo_repo[:12]:
        print(f"    · {jm}: `{cesta}` → `{projekt}`")
    print("    (rozsah brány je VIDĚT; skutečně mrtvá cesta by bránu shodila)")

print()
print(f"Skillů: {len([x for x in SKILLS.iterdir() if x.is_dir()])}, chyb: {chyb}")
print(f"Cesty k nástrojům: {vsech_cest} zmínek, {mrtvych} mrtvých")
# ⚠ ROZSAH MUSÍ BÝT VIDĚT (P28/B5): kdyby brána mlčela o tom, KTERÝ TVAR cest
# viděla, „0 mrtvých“ by znovu nebylo důkaz — přesně to byl nález §51.3
# (brána viděla 65 z 80 zmínek a hlásila zelenou).
if mimo_backticku:
    print(f"  (z toho {mimo_backticku} zmínek MIMO backticky — tvar, který brána"
          f" do 8. 10. 2026 NEVIDĚLA; dřív by se do čítače vůbec nedostaly)")
print("VŠE OK" if chyb == 0 else "NALEZENY CHYBY")
sys.exit(0 if chyb == 0 else 1)
