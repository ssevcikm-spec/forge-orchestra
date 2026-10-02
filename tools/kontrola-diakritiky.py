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
    # 2. 10. 2026 (11:0x–12:0x): PLÁN dalších kroků. NAMĚŘENO PŘI PŘIDÁVÁNÍ:
    # tenhle dokument v seznamu **NEBYL**, ačkoli ho plánovací session sama
    # napsala a sám uživatel na to upozornil („PLAN-DALSI-KROK.md tam ještě
    # není"). Je to **po osmé** táž vada (S27: ruční seznam místo projití
    # složky) — a je to zároveň důkaz, že ani upozornění v zadání ten krok
    # neudělá samo. Ručně ověřeno týmž vzorem: 17 960 znaků, rozbito: ne.
    WS / "PLAN-DALSI-KROK.md",
    WS / "_analyza" / "A-UKOL-ZAZNAM.md",
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
    # 2. 10. 2026: BRÁNA SAMA SEBE. Naměřeno při psaní `g1-diakritika-novych.py`
    # (nezávislé ověření všech souborů té session): tenhle soubor **v seznamu
    # nebyl** — tedy kdyby se v NĚM rozbila diakritika, brána by to nikdy
    # neohlásila a sama by přitom hlásila „VŠE OK". Je to **po deváté** táž
    # vada (S27: ruční seznam, který neobsahuje sám sebe).
    # POZOR: soubor obsahuje `ROZBITE` znaky **jako vzorek** — musí je mít, aby
    # je uměl hledat. Kdyby se kontroloval stejně jako ostatní, spadl by sám na
    # sobě (a to je přesně ta past z `AGENTS.md`: „ukázku rozbitého kódování
    # popisuj slovem"). Kontroluje se proto jinak: hledá se jeho typický český
    # text, který by se dvojím kódováním rozbil.
    WS / "orchestra" / "tools" / "kontrola-diakritiky.py",
    # 2. 10. 2026 (plánovací session, 11:4x–12:3x UTC): ověření práce akční
    # session (Úkoly A–D a B1). Doplněny ve STEJNÉ session, která je napsala —
    # a NAMĚŘENO PŘI PŘIDÁVÁNÍ: `HANDOFF.md` v seznamu **už byl** (přidán dřív),
    # ale `_analyza/c2-sonda-uvozovky.py` v něm **nebyl**, ačkoli na něj
    # odkazovaly DVA dokumenty (`HANDOFF.md` §16.11 a `g1-diakritika-novych.py`)
    # — přitom soubor na disku vůbec neexistoval. Byl to **doklad, který se
    # ztratil**; obnoven a přidán sem. Je to **po desáté** táž vada (S27).
    WS / "_analyza" / "c2-sonda-uvozovky.py",
    # 2. 10. 2026 (11:4x–12:4x): oddíly, kterými se `HANDOFF.md` rozšířil
    # (§17 výsledky ověření, §8f vlastní omyly). Drží se jako samostatné
    # soubory, protože se zapisovaly skriptem (`s17-zapis-handoff.py`,
    # `s8f-zapis-handoff.py`) — a skript, který text vkládá, se musí dát ověřit.
    WS / "_analyza" / "s17-novy-oddil.md",
    WS / "_analyza" / "s8f-novy-oddil.md",
    # 2. 10. 2026 (12:2x): §17.11 — doplnění na konci session (finální souhrn
    # bran, přegenerovaný inventář, doplnění všech 12 skillů do brány).
    WS / "_analyza" / "s17b-doplneni.md",
    # 2. 10. 2026 (12:3x): KRONIKA PROJEKTU — nový TRVALÝ dokument, který
    # přežívá předávání (na rozdíl od `HANDOFF.md`, který se přepisuje).
    # Drží celý příběh: sessions, nálezy, omyly, poučení, návrhy.
    # Patří sem proto, že je to **autorita o průběhu projektu** — kdyby v ní
    # byla rozbitá diakritika, nikdo by si toho nevšiml právě ve chvíli,
    # kdy se podle ní dělá analýza postupu a návrhy na zlepšení.
    WS / "KRONIKA-PROJEKTU.md",
    # 2. 10. 2026 (12:5x–13:3x UTC, PLÁNOVACÍ session — ověření práce akční
    # session o krok dřív): nástroje, kterými se to ověřovalo. Jsou tady proto,
    # že vznikly ve STEJNÉ session, která je psala — a to je krok, na kterém to
    # v tomhle workspace padlo **dvanáctkrát** (S27: ruční seznam místo
    # projití složky). NAMĚŘENO PŘI PŘIDÁVÁNÍ: `p18-sonda-tpm.py` je toho
    # dokladem — jeho první verze stahovala log `urllib`em a padala na
    # `HTTP 401` po přesměrování (TLS v Pythonu), což vypadalo jako vadný
    # přístup na GitHub, a byl to přitom jen špatný nástroj na tuhle práci.
    WS / "_analyza" / "p18-sonda-tpm.py",
    WS / "_analyza" / "p18-stahni-log.mjs",
    WS / "_analyza" / "p18-prompt-tokeny.py",
    WS / "_analyza" / "p18-pr-a-behy.mjs",
    WS / "_analyza" / "p18b-jmena-behu.mjs",
    WS / "_analyza" / "p18c-stav-uloh.mjs",
    WS / "_analyza" / "s18-zapis-handoff.py",
    WS / "_analyza" / "s18-prepocitej-omyly.py",
    WS / "_analyza" / "s18-novy-oddil.md",
    WS / "_analyza" / "s8g-novy-oddil.md",
    WS / "_analyza" / "s18b-doplneni.md",
    WS / "_analyza" / "s18c-omyl68-radek.md",
    WS / "_analyza" / "s18c-doplneni.md",
    WS / "_analyza" / "s18c-dopln-omyl68.py",
    WS / "_analyza" / "s18c-sonda-kotvy.py",
    WS / "_analyza" / "s18d-sestav-handoff.py",
    WS / "_analyza" / "s18e-l13-radek.md",
    WS / "_analyza" / "s18e-dopln-l13.py",
    WS / "_analyza" / "s18f-oprav-hlavicku.py",
    WS / "_analyza" / "p18d-kontrola-utf8.py",
    WS / "_analyza" / "p19-sonda-groq.py",
    WS / "_analyza" / "p19-push.py",
    WS / "_analyza" / "p19b-cekej-pages.mjs",
    WS / "_analyza" / "s19-oddil-groq.md",
    WS / "_analyza" / "s19-dopln-odpoved-groq.py",
    WS / "_analyza" / "s19-push-oddil.md",
    WS / "_analyza" / "s19-omyl69-radek.md",
    WS / "_analyza" / "s19-zapis-handoff.py",
    WS / "_analyza" / "s19b-dopln-souhrn.py",
    WS / "_analyza" / "s19c-radek16.md",
    WS / "_analyza" / "s19c-h13.md",
    WS / "_analyza" / "s19c-l14.md",
    WS / "_analyza" / "s19c-dopln-kroniku.py",
    WS / "_analyza" / "s19d-dopln-h13.py",
    WS / "_analyza" / "s19e-oprav-hlavicku.py",
    WS / "_analyza" / "s19f-oprav-deploy.py",
    WS / "_analyza" / "s19g-oddil-deploy.md",
    WS / "_analyza" / "s19g-omyl70-radek.md",
    WS / "_analyza" / "s19g-zapis.py",
    WS / "_analyza" / "s19h-souhrn-8g.py",
    WS / "_analyza" / "s19i-souhrn-oprava.py",
    WS / "_analyza" / "p19f-over-main.mjs",
    WS / "_analyza" / "p19g-granule-vs-groq.py",
    WS / "_analyza" / "p19h-groq-presne.py",
    WS / "_analyza" / "p19i-co-zmensit.py",
    WS / "_analyza" / "p19i-sonda.py",
    WS / "_analyza" / "p19i-sonda2.py",
    WS / "_analyza" / "s19k-oddil-granule.md",
    WS / "_analyza" / "s19k-omyl71-radek.md",
    WS / "_analyza" / "s19k-zapis.py",
    WS / "_analyza" / "s19l-souhrn-8g.py",
    WS / "_analyza" / "s19j-hlavicka-ziva.py",
    WS / "games" / "uo-shadows" / ".github" / "workflows" / "ci.yml",
    WS / "README.md",
    WS / "orchestra" / "README.md",
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\dsh-prostredi\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\vision\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\game-assets\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\game-developer\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\orchestra\SKILL.md"),
    # 2. 10. 2026 (plánovací session): NAMĚŘENO PŘI PŘIDÁVÁNÍ — na disku je
    # **12 skillů**, ale v tomhle seznamu bylo jen **5**. Chybělo i `overovani`,
    # tedy skill, do kterého táž session právě psala (§8.1/§8.2 o tom, že
    # „vydalo se" není „podařilo se") — brána by ho **nikdy neotevřela**
    # a hlásila „VŠE OK". Je to **po jedenácté** táž vada (S27: ruční seznam).
    # Dopsány všechny, které na disku jsou; `kontrola-diakritiky.py` sám se
    # kontroluje zvlášť (má vzorek rozbitých znaků), takže tady není.
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\dsh-usage\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\hlouchkova-analyza\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\imagegen\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\imagegen-local\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\otevrena-temata\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\overovani\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\session-handoff\SKILL.md"),
]

# Typické znaky dvojitého kódování UTF-8 přečtené jako Windows-1250
ROZBITE = ["Ã", "Ä", "Å"]

# ── VÝJIMKA PRO TENHLE SOUBOR ────────────────────────────────────────────────
# Vzor `ROZBITE` výš MUSÍ být v tomhle souboru doslovně — jinak by nehledal nic.
# Kdyby se ale kontroloval stejně jako ostatní, našel by **sám sebe** a brána by
# hlásila vadu na souboru, který je v pořádku (tatáž past, na kterou upozorňuje
# `AGENTS.md`: ukázku rozbitého kódování popisuj slovem, ne znaky).
#
# Kontroluje se proto JINAK — a to DVĚMA pohledy:
#   1. v souboru nesmí být NÁHRADNÍ ZNAK (tím se dvojí kódování projeví:
#      z českého písmene se stane `U+FFFD`), a
#   2. musí v něm být český text (sondou je pět slov).
#
# ⚠ PROČ NESTAČÍ HLEDAT JEN TA SLOVA (naměřeno 2. 10. 2026): seznam
# `VLASTNI_TEXTY` je psaný v TOMTÉŽ souboru, takže když se rozbije text okolo,
# hledané slovo v seznamu zůstane správně — a kontrola projde. Odhalil to až
# mutační test: rozbil jsem VŠECH 7 výskytů jednoho slova a brána stejně
# hlásila „VŠE OK", protože to své (v seznamu) pořád našla. Náhradní znak tuhle
# slepou uličku zavírá — je v souboru vidět, ať je rozbité cokoli.
VLASTNI = WS / "orchestra" / "tools" / "kontrola-diakritiky.py"
VLASTNI_TEXTY = ["diakritiky", "kódování", "souborů", "příliš", "žluťoučký"]
NAHRADNI = "\ufffd"

chyb = 0
for f in SOUBORY:
    if not f.exists():
        print(f"  CHYBA {f.name}: neexistuje")
        chyb += 1
        continue
    s = f.read_text(encoding="utf-8")
    if f.resolve() == VLASTNI.resolve():
        # Sebekontrola: český text musí být CELÝ, a to i kdyby se `ROZBITE`
        # znaky v souboru vyskytovaly (vyskytovat se MUSÍ — je to vzorek).
        chybejici = [t for t in VLASTNI_TEXTY if t not in s]
        nahradnich = s.count(NAHRADNI)
        if chybejici or nahradnich:
            chyb += 1
            duvod = []
            if chybejici:
                duvod.append(f"chybí text {', '.join(chybejici)}")
            if nahradnich:
                duvod.append(f"{nahradnich}× náhradní znak")
            print(f"  CHYBA {f.name:34} {len(s):7} znaků  "
                  f"rozbito: {'; '.join(duvod)}")
        else:
            print(f"  OK   {f.name:34} {len(s):7} znaků  "
                  f"rozbito: ne (sebekontrola: {len(VLASTNI_TEXTY)} českých slov, "
                  f"0 náhradních znaků)")
        continue
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
