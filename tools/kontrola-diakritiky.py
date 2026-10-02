"""Kontrola diakritiky v dokumentech, které tahle session měnila.

PowerShell soubory s diakritikou jednou poškodil (dvojité kódování), takže se
kontrola dělá Pythonem – viz HANDOFF.md, „Pozor při editaci souborů
s diakritikou".
"""

import pathlib
import sys

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
SOUBORY = [
    WS / "AGENTS.md",
    WS / "ARCHITEKTURA-ANALYZA-ZADANI.md",
    WS / "HANDOFF.md",
    WS / "SKILLY-AKTUALIZACE.md",
    WS / "MOZNOSTI-AGENTA.md",
    WS / "FORGE-ORCHESTRA-MOZNOSTI.md",
    WS / "PLAN-VISION-ORCHESTRA.md",
    # 1. 10. 2026: analýza architektury a její podklady. Byly napsané bez
    # kontroly diakritiky — a to je přesně ta vada, kterou tenhle nástroj
    # hledá. Nový dokument se musí přidat SEM, jinak ho kontrola nevidí
    # (stejná past jako u netrackovaného souboru v gitu).
    WS / "ANALYZA-ARCHITEKTURY-ORCHESTRA.md",
    WS / "ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md",
    WS / "PLAN-ROZVOJ-ORCHESTRA.md",
    # 1. 10. 2026 (večer): hloubková analýza a její druhé kolo měření.
    # NAMĚŘENO PŘI PŘIDÁVÁNÍ: tenhle nástroj má PEVNÝ seznam, takže nový
    # dokument projde zeleně, i když ho kontrola nikdy neotevřela. Je to táž
    # vada jako `kontrola-driftu.mjs` s ručním seznamem 12 souborů — a je
    # zapsaná jako S27 v ANALYZA-HLOUBKOVA-ORCHESTRA.md §4.
    WS / "ANALYZA-HLOUBKOVA-ORCHESTRA.md",
    WS / "_analyza" / "HLOUBKOVA-MERENI.md",
    WS / "_analyza" / "HLOUBKOVA-MERENI-2.md",
    WS / "ANALYZA-HLOUBKOVA-2-ZADANI.md",
    # Druhé kolo hloubkové analýzy (2. 10. 2026). Přidáno proto, že tahle
    # brána je SAMA příkladem vady S27: má ruční seznam, takže nový dokument
    # projde „zeleně", aniž ho kdy otevře. Naměřeno 2. 10. 2026: oba soubory
    # níž v seznamu nebyly a brána přesto hlásila „VŠE OK".
    WS / "ANALYZA-HLOUBKOVA-ORCHESTRA-2.md",
    WS / "_analyza" / "HLOUBKOVA-MERENI-3.md",
    WS / "IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md",
    # 2. 10. 2026: jazykový inventář a jeho plán. NAMĚŘENO PŘI PŘIDÁVÁNÍ: tenhle
    # dokument v seznamu NEBYL, ačkoli vznikl ve stejný den jako tři soubory
    # výše — brána tedy hlásila „VŠE OK" nad dokumentem, který nikdy neotevřela.
    # Je to **po páté** táž vada (S27): ruční seznam, který se musí doplňovat
    # ručně, není brána. Náprava (projít složku, ne seznam) je samostatné
    # rozhodnutí — do té doby sem každý nový dokument PATŘÍ.
    WS / "IMPLEMENTACE-HRANICE-JAZYKA.md",
    # 2. 10. 2026 (08:5x): plán úprav z nových nálezů (N1–N6) vzniklý při
    # provádění A1–A4 a Z1–Z8. Přidán ve STEJNÉ session, která ho napsala —
    # protože „přidám ho příště" je přesně ten krok, na kterém se to **po páté**
    # nepovedlo (viz komentář výše). Nový dokument v tomhle workspace patří sem
    # ve chvíli vzniku, ne později.
    WS / "IMPLEMENTACE-NOVE-NALEZY-Z-UKOTVENI.md",
    # 2. 10. 2026 (09:0x): prompt pro novou session (ověření práce předchozí
    # session + pokračování). Vznikl při sjednocení zdrojů po souběhu TŘÍ session.
    WS / "PROMPT-NOVA-SESSION.md",
    # 2. 10. 2026 (06:25): záznam o souběhu DVOU SESSION nad tímhle workspace.
    # NAMĚŘENO PŘI PŘIDÁVÁNÍ: `HANDOFF.md` psaly dvě session současně a jedna
    # z nich si toho nevšimla — zápis jí systém odmítl, což je správně.
    WS / "SOUBEH-SESSION-NALEZY.md",
    # Živý rozcestník nasazení (11 opatření, cíl −79 % nákladů). Do 2. 10. 2026
    # nebyl zmíněný v AGENTS.md, HANDOFF.md ANI OTEVRENA-TEMATA.md.
    WS / "DEPLOY-VYLEPSENI.md",
    WS / "OTEVRENA-TEMATA.md",
    # 2. 10. 2026 (dopoledne): metodický dokument „jak psát design dokumenty
    # a plánovat vývoj" — vznikl na zadání uživatele a je určený k dalšímu
    # budování (podklad pro revizi skillu game-developer a přepis designu hry).
    # Přidán ve STEJNÉ session, která ho napsala — „přidám ho příště" je krok,
    # na kterém to v tomhle workspace padlo už pětkrát (viz komentáře výš).
    WS / "JAK-PSAT-DESIGN-A-PLANOVAT-VYVOJ.md",
    # 2. 10. 2026 (10:4x): zadání pro novou session po ověření — co provést,
    # co zadokumentovat a co připravit pro plánovací session. Vzniklo ve session,
    # která ověřovala práci session `eb127abd` (12/12 bodů §7.2).
    # POZOR: tenhle soubor sám sobě přikazuje, že sem patří — a je to právě ten
    # krok, na kterém to v tomhle workspace padlo ŠESTKRÁT (vada S27: ruční seznam).
    WS / "NEXT-SESSION-INSTRUKCE.md",
    # 2. 10. 2026 (11:3x–12:0x): dokumenty, které vznikly při plnění zadání
    # (push orchestra, granule, N1/N3, rozhodnutí o nástrojích, podklad pro
    # plánovací session). Přidány ve STEJNÉ session, která je napsala — je to
    # **posedmé**, co se tenhle krok dělá ručně, a posedmé to byl krok, na
    # kterém to v tomhle workspace padalo (vada S27: ruční seznam místo projití
    # složky). Důkaz, že to není formalita: kdyby tu nebyly, brána by nad nimi
    # hlásila „VŠE OK", aniž je otevřela.
    WS / "_analyza" / "C-PODKLAD-SMLOUVY.md",
    WS / "_analyza" / "a3-brany-novych-granuli.md",
    # 2. 10. 2026: POSTUP PŘEDÁVÁNÍ mezi sessionami (dva kroky: plánovací
    # a akční) se šablonami promptů. Nahrazuje jednorázový PROMPT-NOVA-SESSION.md.
    # Je to dokument, ze kterého se bude **řídit každé další předání** — kdyby ho
    # brána neviděla, mohla by v něm být rozbitá diakritika a nikdo by si toho
    # nevšiml právě ve chvíli, kdy se podle něj rozhoduje.
    WS / "PREDAVANI-SESSION.md",
    WS / "orchestra" / "repo" / ".forge" / "check-schema.py",
    WS / "orchestra" / "repo" / ".forge" / "vision-profile.json",
    WS / "orchestra" / "repo" / ".forge" / "baseline.py",
    WS / "orchestra" / "tools" / "test-check-schema.py",
    WS / "games" / "uo-shadows" / ".github" / "workflows" / "ci.yml",
    WS / "README.md",
    WS / "orchestra" / "README.md",
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\dsh-prostredi\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\vision\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\game-assets\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\game-developer\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\orchestra\SKILL.md"),
]

# Typické znaky dvojitého kódování UTF-8 přečtené jako Windows-1250
ROZBITE = ["Ã", "Ä", "Å"]

chyb = 0
for f in SOUBORY:
    if not f.exists():
        print(f"  CHYBA {f.name}: neexistuje")
        chyb += 1
        continue
    s = f.read_text(encoding="utf-8")
    nalezene = [z for z in ROZBITE if z in s]
    stav = "OK  " if not nalezene else "CHYBA"
    if nalezene:
        chyb += 1
    # Popisek musí nést i rodiče: jinak se v seznamu tři různé soubory jmenují
    # „SKILL.md" a není poznat, který je který.
    popis = f"{f.parent.name}\\{f.name}"
    print(f"  {stav} {popis:34} {len(s):7} znaků  "
          f"rozbito: {', '.join(nalezene) if nalezene else 'ne'}")

print()
print("VŠE OK" if chyb == 0 else f"NALEZENY CHYBY ({chyb})")
sys.exit(0 if chyb == 0 else 1)
