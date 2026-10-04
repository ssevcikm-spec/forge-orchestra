"""Ověří, že dokumentační změny sedí: frontmatter, diakritika, nové sekce.

Kontroluje se i to, že v souborech nezůstalo dvojité kódování češtiny
(UTF-8 přečtené jako Windows-1250 — z jednoho písmene s diakritikou se stanou
dva znaky) – přesně to jednou vzniklo, když se do souboru psalo
PowerShellem místo Pythonu. Ukázku sem ZÁMĚRNĚ nepíšu doslovnými znaky:
zakazuje to `AGENTS.md` a `g1-diakritika-novych.py` to hlásí jako vadu
souboru (naměřeno 2. 10. 2026).
"""

import pathlib
import re
import sys

SKILLS = pathlib.Path(r"C:\Users\Ssevc\.dsh\skills")
# Obecná pravidla stanice (DSH_HOME; `~\.dsh` je junction na E:\DeepSeekHarness-data).
# OD 4. 10. 2026 sem patří obecné části trvalých pravidel — projektové AGENTS.md
# je už nenese, aby se nezdvojovaly (viz PLAN-SEPARACE-WORKSPACE.md).
OBECNA = pathlib.Path(r"C:\Users\Ssevc\.dsh\AGENTS.md")
README = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\orchestra\README.md")

# Typické znaky dvojitého kódování (UTF-8 přečtené jako Windows-1250)
ROZBITE = ["Ã", "Ä", "Å", "Å¡", "Ä›", "Ã¡", "Ã­", "Ã©"]

kontrol = 0
chyb = 0


def zkontroluj(cesta: pathlib.Path, pozadovane: list[str], popis: str) -> None:
    global kontrol, chyb
    if not cesta.exists():
        print(f"  CHYBA {popis}: soubor neexistuje ({cesta})")
        chyb += 1
        return
    text = cesta.read_text(encoding="utf-8")

    # 1) dvojité kódování
    nalezeno = [z for z in ROZBITE if z in text]
    if nalezeno:
        print(f"  CHYBA {popis}: rozbitá diakritika ({', '.join(nalezeno[:3])})")
        chyb += 1
    else:
        print(f"  OK   {popis}: diakritika v pořádku")
    kontrol += 1

    # 2) požadované texty
    chybejici = [p for p in pozadovane if p not in text]
    if chybejici:
        for p in chybejici:
            print(f"  CHYBA {popis}: chybí text {p[:60]!r}")
        chyb += 1
    else:
        print(f"  OK   {popis}: všech {len(pozadovane)} hledaných textů na místě")
    kontrol += 1

    # 3) YAML frontmatter u skillů
    if "skills" in str(cesta):
        if text.startswith("---"):
            konec = text.find("\n---", 3)
            if konec > 0:
                fm = text[3:konec]
                ma_name = bool(re.search(r"^name:\s*\S", fm, re.M))
                ma_desc = bool(re.search(r"^description:", fm, re.M))
                print(f"  {'OK  ' if ma_name and ma_desc else 'CHYBA'} {popis}: "
                      f"frontmatter (name={ma_name}, description={ma_desc})")
                if not (ma_name and ma_desc):
                    chyb += 1
            else:
                print(f"  CHYBA {popis}: frontmatter nekončí")
                chyb += 1
        else:
            print(f"  CHYBA {popis}: nezačíná frontmatterem")
            chyb += 1
        kontrol += 1


print("=== orchestra/README.md ===")
zkontroluj(README, [
    "Jak agent dostane soubory",
    "Opakované pokusy: každý zkusí jiný model",
    "Nástroje pro analýzu",
    "files-to-edit.mjs",
    "ESCALATE_AFTER",
    "--map-tokens 0",
    "watchdog: 0 ohlášeno (prah 8)",
    # 1. 10. 2026: README musí přiznat, že cooldown má dvě díry a že návod na
    # úklid je s dnešním kódem nebezpečný. Kdyby to tam nebylo, README by
    # radilo postup, který smaže cache roadmapy (S12/S13, S11).
    "Nová granule se 3 h nevydá",
    "tenhle postup je v dnešním kódu NEBEZPEČNÝ",
    "Stav obálky k 1. 10. 2026",
], "README")

print("=== orchestra/SKILL.md ===")
zkontroluj(SKILLS / "orchestra" / "SKILL.md", [
    "Analýza a diagnostika",
    "(**3 h**)",
    "Cooldown se vynucuje ČASEM",
    # 1. 10. 2026: text „MAX_ATTEMPTS` je mrtvý kód" BYL v skillu a byla to
    # NEPRAVDA — analýza architektury naměřila, že se MAX_ATTEMPTS čte na pěti
    # místech conductora a rozhoduje o návratu do fronty. Kontrola se proto
    # přesměrovala na nové (pravdivé) znění, ne na staré. Kdyby zůstala na
    # starém, bránila by opravě — přesně to je past „dokumentace, která popírá
    # vlastní nástroje".
    "MAX_ATTEMPTS` NENÍ mrtvý kód",
    "soubor v EDITOVATELNÉM chatu",
    # 1. 10. 2026: naměřené vady conductoru (invarianty 15–18).
    "Nová granule se `RETRY_HOURS` (3 h) NEVYDÁ",
    "Cooldown se u selhání přes `/report` OBCHÁZÍ",
    # 1. 10. 2026 (odpoledne): zámek BYL rozbitý a skill to tak měl zapsané
    # („neblokuje nic"). Oprava je hotová a otestovaná, takže kontrola míří na
    # nové znění — kdyby zůstala na starém, hlídala by vadu.
    # Past „dokumentace, která brání opravě" se tímhle opakuje už podruhé
    # (poprvé u MAX_ATTEMPTS výše); je to nejčastější forma téhle chyby.
    "Zámek souborů v dispatch smyčce neblokoval nic — OPRAVENO",
    "test-zamek-owns.py",
    "`listGames` fallback je nebezpečný",
    # Nový invariant 19: brána si musí dovézt svoje závislosti (Pillow/PIL).
    "ModuleNotFoundError: No module named 'PIL'",
], "orchestra skill")

print("=== game-developer/SKILL.md ===")
zkontroluj(SKILLS / "game-developer" / "SKILL.md", [
    "tiše zelený",
    "extends Node",
    "_instantiate",
    "stejný počet",
    # 30. 9. 2026: brány měří, ale nevidí – na obsah se musí podívat.
    "Brány měří, ale nevidí",
], "game-developer skill")

print("=== vision/SKILL.md (nové možnosti) ===")
zkontroluj(SKILLS / "vision" / "SKILL.md", [
    # Skill musí sám říkat, že je ZÁLOHA – dřív tvrdil, že agent nevidí.
    "Nejdřív zkuste `read_image`",
    "does not declare image input",
    "MOZNOSTI-AGENTA.md",
], "vision skill")

print("=== imagegen + imagegen-local (read_image) ===")
zkontroluj(SKILLS / "imagegen" / "SKILL.md", [
    "read_image` v této session funguje",
], "imagegen skill")
zkontroluj(SKILLS / "imagegen-local" / "SKILL.md", [
    "Podívej se na to sám",
], "imagegen-local skill")

print("=== game-assets/SKILL.md (Blender, mrtvé cesty) ===")
zkontroluj(SKILLS / "game-assets" / "SKILL.md", [
    "Blender 5.2.1 LTS",
    "headless",
    # GameForge cesty jsou mrtvé a skill to musí přiznat, ne je používat.
    "neexistují",
    "Podívej se na to vlastníma očima",
], "game-assets skill")

print("=== orchestra/SKILL.md (assety a oči) ===")
zkontroluj(SKILLS / "orchestra" / "SKILL.md", [
    "Assety a „oči\" orchestra",
    "vision.mjs",
    "check-assets.py",
    # 30. 9. 2026: brána animace se nikdy neuplatní – chůze leží jinde.
    "Animace se neměří",
    "brána se na to nedívá",
    # 30. 9. 2026: schéma je per-game a kontrola je před vision.
    "check-schema.py",
    "vision-profile.json",
    "Tvrdá brána vs. poradní kontrola",
    # 30. 9. 2026: baseline + LGTM cache.
    "baseline.py",
    "LGTM",
], "orchestra skill assety")

print("=== game-assets: slepé místo brány ===")
zkontroluj(SKILLS / "game-assets" / "SKILL.md", [
    "zelená od brány neznamená, že kontrola proběhla",
], "game-assets slepé místo")

print("=== workspace: MOZNOSTI-AGENTA.md + FORGE-ORCHESTRA-MOZNOSTI.md ===")
WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
zkontroluj(WS / "MOZNOSTI-AGENTA.md", [
    "read_image",
    "Blender 5.2.1 LTS",
    "gameforge\\tools\\venv\\Scripts\\python.exe` **neexistuje**",
    "does not declare image input",
    # 30. 9. 2026: brána je slepá na soubory, které neleží tam, kam čeká.
    "brána se na to nedívá",
], "MOZNOSTI-AGENTA")
zkontroluj(WS / "FORGE-ORCHESTRA-MOZNOSTI.md", [
    "vision.mjs",
    '"target": "lan"',
    "kontaktni-arch.py",
    "kind` dnes nic neřídí",
    # nález: kontrola IoU se nikdy neuplatní
    "Brána animace nikdy nic nezkontroluje",
], "FORGE-ORCHESTRA-MOZNOSTI")

print("=== PLAN-VISION-ORCHESTRA.md ===")
zkontroluj(WS / "PLAN-VISION-ORCHESTRA.md", [
    # metoda volání – jádro plánu
    "neposílat hodnocení, posílat očekávání",
    "self-consistency",
    # kdo to čte
    "DeepSeek jako dělník",
    # cache a schvalování
    "Co není v baseline, nesmí do hry",
    "phash",
    # rizika
    "Goodhart",
    # nález: rozpor v zadání projektu a jeho řešení
    "Schéma je PER-GAME",
    "16×16",
    # hotové fáze
    "Co je HOTOVÉ",
    "check-schema.py",
], "PLAN-VISION-ORCHESTRA")

print("=== dsh-prostredi/SKILL.md (NOVÝ, 1. 10. 2026) ===")
zkontroluj(SKILLS / "dsh-prostredi" / "SKILL.md", [
    # Pasti, které vypadají jako chyba logiky. Každá se našla měřením.
    "Select-String",
    "PYTHONIOENCODING",
    "BOM",
    "CRLF",
    # Sandbox: podprocesy s piped stdio a přesměrované tempo.
    "EPERM",
    "PermissionError",
    # Godot bez --user-data-dir.
    "--user-data-dir",
    # Pravidlo, které drží celý soubor pohromadě.
    "nejsou úspěch",
], "dsh-prostredi skill")

print("=== game-developer: brána, která neproběhne ===")
zkontroluj(SKILLS / "game-developer" / "SKILL.md", [
    # 1. 10. 2026: brána schématu tiše přestala měřit (level.gd se přepsal).
    "Brána, která neproběhne, není brána",
    # Pozor: hledané texty se NESMÍ zalamovat přes řádek – dokumenty jsou
    # zalamované, takže delší věta se v nich nikdy nenajde jako jeden kus.
    "u každé brány se ptej",
    "nejsou úspěch",
    # Vizuální změna: zelené testy nestačí, hráč nebyl vidět.
    "Vizuální změna se neověřuje testy",
    # Statická kontrola musí číst kód, ne komentáře.
    "číst KÓD, ne komentáře",
    # Schéma je tvrdá brána a je v tabulce bran.
    "check-schema.py",
], "game-developer brány")

print("=== game-assets: hash, metrika, izodlaždice ===")
zkontroluj(SKILLS / "game-assets" / "SKILL.md", [
    # Dvě mezery phash – bez nich projde přebarvený asset jako nezměněný.
    "hash není důkaz",
    "barevný podpis",
    "sha256",
    # Metrika, která měří něco jiného (4 verze metriky švu).
    "metrika, která měří něco jiného",
    "0,00 pro všechno",
    # Izometrické dlaždice ze spec.json.
    "make_iso_tiles.py",
    "Směr světla je konvence",
], "game-assets hash a dlaždice")

print("=== vision: režimy, self-consistency, cache ===")
zkontroluj(SKILLS / "vision" / "SKILL.md", [
    # Režimy, které má vision.mjs v orchestra (a tenhle skill je dřív neměl).
    "--mode presence",
    "--mode diff",
    # Neshoda dvou běhů je signál nejistoty, ne chyba.
    "Self-consistency",
    "signál nejistoty",
    # Cache: schválené se neposílá, --force to obejde.
    "--force",
    "z_cache",
    # Pravidlo o promptu: očekávání se počítá z dat hry.
    "neposílat hodnocení, posílat očekávání",
    "POČÍTÁ Z DAT HRY",
], "vision režimy a cache")

# ⚠ ROZDĚLENO 4. 10. 2026 (přesun obecných pravidel do DSH_HOME).
# PROČ DVA BLOKY: obecná pravidla (prostředí, ověřování, dokumentace, jazyk,
# nasazení) už v projektovém AGENTS.md NEJSOU — bydlí v `~/.dsh/AGENTS.md`, aby
# je dostala každá session v každém workspace. Kdyby je kontrola hledala dál
# v projektu, hlásila by po přesunu 13 chyb u souboru, který je v pořádku —
# a kdo by je „opravil" vrácením textu, vrátil by i duplikaci.
# Naměřeno před rozdělením: z 15 požadovaných textů jich 13 bydlelo v sekcích,
# které se přesouvají (Prostředí, Jak ověřovat, Jak dokumentovat, Kdy práce…).
print("=== DSH_HOME: AGENTS.md (OBECNÁ PRAVIDLA – platí v každé session) ===")
zkontroluj(OBECNA, [
    # Čím se liší od stavu projektu.
    "trvalá pravidla",
    # Prostředí.
    "Select-String",
    "PYTHONIOENCODING",
    # Nástroje zapisují do tempu a NEMUSÍ to být vidět.
    "Zapisuj do workspace",
    # Pasti, které vypadají jako chyba logiky.
    "dsh-prostredi",
    # Ověřování: měření, ne dojem.
    "známém správném",
    "proběhla?",
    # 1. 10. 2026: „není to vada" je taky výsledek, ale musí být doložený.
    "Není to vada",
    # Nasazení: HTTP 200 není důkaz.
    "HTTP 200",
    "last-modified",
    # Handoff: přepis nesmí ztratit otevřené body.
    "nic nesmí zmizet",
    # Kdy práce patří do nové session.
    "nezávislosti pohledu",
    # Co nikdy.
    "Nepushovat bez vyžádání",
], "AGENTS.md obecná (DSH_HOME)")

print("=== workspace: AGENTS.md (PRAVIDLA PROJEKTU) ===")
zkontroluj(WS / "AGENTS.md", [
    # Musí být jasné, čím se liší od HANDOFF.md.
    "trvalá pravidla",
    "HANDOFF.md",
    # Pasti prostředí jsou sice obecné, ale projekt na ně musí odkázat —
    # jinak agent v projektu o skillu `dsh-prostredi` neví.
    "dsh-prostredi",
    # forge-quest je ŽIVÁ hra, ne mrtvá minulost.
    "forge-quest",
], "AGENTS.md projekt")

print("=== dsh-prostredi: zapis do tempu bez chyby ===")
zkontroluj(SKILLS / "dsh-prostredi" / "SKILL.md", [
    # 1. 10. 2026: Godot --write-movie zapsal „někam" a nic neřekl.
    # Pozor na zalamování – hledaný text musí být na jednom řádku.
    "NIC NEŘEKNE",
    "že soubor existuje",
], "dsh-prostredi temp")

print("=== orchestra: jak ověřit nasazení na Pages ===")
zkontroluj(SKILLS / "orchestra" / "SKILL.md", [
    "HTTP 200 není důkaz",
    "last-modified",
    "z HTML se verze nepozná",
], "orchestra nasazení")

print("=== orchestra: brána, která přestala měřit ===")
zkontroluj(SKILLS / "orchestra" / "SKILL.md", [
    "TIŠE PŘESTALA MĚŘIT",
    "test-check-schema.py",
    "commitnout do hry",
], "orchestra nález brány")

print("=== workspace: README + FORGE-ORCHESTRA-MOZNOSTI ===")
zkontroluj(WS / "README.md", [
    "AGENTS.md",
    # forge-quest je ŽIVÁ hra, ne mrtvá minulost.
    "jsou ŽIVÉ",
    "odvozuje z názvu repa",
    "zjisti-pages.mjs",
], "workspace README")
zkontroluj(WS / "FORGE-ORCHESTRA-MOZNOSTI.md", [
    # Nález 11: brána po migraci tiše přestala měřit.
    "TIŠE PŘESTALA MĚŘIT",
    "prázdným seznamem",
    "test-check-schema.py",
    "AGENTS.md",
    # Dřív tu stálo „zatím nezapojené", což po zapojení do ci.yml lhalo.
    "zapojené",
], "FORGE-ORCHESTRA-MOZNOSTI nález 11")

print("=== PLAN-VISION-ORCHESTRA: past 4 + počty testů ===")
zkontroluj(WS / "PLAN-VISION-ORCHESTRA.md", [
    "Čtyři pasti, které se při migraci našly",
    "TIŠE PŘESTALA MĚŘIT",
    "test-check-schema.py",
    # Počty musí sedět s realitou (měří se jinde, tady se hlídá, že tu jsou).
    "**34 testů**",
    "**36 testů**",
], "PLAN-VISION past 4")

print("=== SKILLY-AKTUALIZACE: pátá vlna ===")
zkontroluj(WS / "SKILLY-AKTUALIZACE.md", [
    "pátá vlna",
    "dsh-prostredi",
    # Čtyři chyby v regexu, které odhalily až testy.
    "IGNORECASE",
    "shodný hash",
], "SKILLY-AKTUALIZACE vlna 5")

print()
print(f"Kontrol: {kontrol}, chyb: {chyb}")
print("VŠE OK" if chyb == 0 else "NALEZENY CHYBY")
sys.exit(0 if chyb == 0 else 1)
