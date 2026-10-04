"""Kontrola diakritiky v dokumentech, které tahle session měnila.

PowerShell soubory s diakritikou jednou poškodil (dvojité kódování), takže se
kontrola dělá Pythonem – viz HANDOFF.md, „Pozor při editaci souborů
s diakritikou".
"""

import pathlib
import sys

# P8 (presun na E:, 4. 10. 2026): BYLY TU JEDEN ROOT, JSOU POTREBA DVA.
#   REPO     = root tohoto repa (E:\Workspaces\forge-orchestra) — dokumenty
#              projektu se presunuly s repem, takze `REPO / "HANDOFF.md"` je dnes
#              `REPO / "HANDOFF.md"`. Odvozuje se z umisteni skriptu, aby
#              nastroj fungoval z jakehokoliv umisteni.
#   STANICE  = koren stanice (C:\Users\Ssevc\Local-Deepseek) — dokumenty, ktere
#              se NEpresouvaly (D6). Ty zustaly na C: a musi se na ne sahat
#              absolutni cestou.
# `REPO` se zamerne prejmenovalo na `REPO`: jmeno `REPO` tady znamenalo "koren
# workspace" a po presunu uz zadny workspace s tema dokumenty neexistuje —
# nechat jmeno by znamenalo, ze budouci ctenar hleda root, ktery neni.
REPO = pathlib.Path(__file__).resolve().parents[1]
STANICE = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
OBECNA = pathlib.Path(r"C:\Users\Ssevc\.dsh\AGENTS.md")
SOUBORY = [
    OBECNA,
    REPO / "AGENTS.md",
    REPO / "ARCHITEKTURA-ANALYZA-ZADANI.md",
    REPO / "HANDOFF.md",
    REPO / "SKILLY-AKTUALIZACE.md",
    STANICE / "MOZNOSTI-AGENTA.md",   # D6: zustal stanici
    REPO / "FORGE-ORCHESTRA-MOZNOSTI.md",
    REPO / "PLAN-VISION-ORCHESTRA.md",
    # 1. 10. 2026: analýza architektury a její podklady. Byly napsané bez
    # kontroly diakritiky — a to je přesně ta vada, kterou tenhle nástroj
    # hledá. Nový dokument se musí přidat SEM, jinak ho kontrola nevidí
    # (stejná past jako u netrackovaného souboru v gitu).
    REPO / "ANALYZA-ARCHITEKTURY-ORCHESTRA.md",
    REPO / "ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md",
    REPO / "PLAN-ROZVOJ-ORCHESTRA.md",
    # 1. 10. 2026 (večer): hloubková analýza a její druhé kolo měření.
    # NAMĚŘENO PŘI PŘIDÁVÁNÍ: tenhle nástroj má PEVNÝ seznam, takže nový
    # dokument projde zeleně, i když ho kontrola nikdy neotevřela. Je to táž
    # vada jako `kontrola-driftu.mjs` s ručním seznamem 12 souborů — a je
    # zapsaná jako S27 v ANALYZA-HLOUBKOVA-ORCHESTRA.md §4.
    REPO / "ANALYZA-HLOUBKOVA-ORCHESTRA.md",
    REPO / "_analyza" / "HLOUBKOVA-MERENI.md",
    REPO / "_analyza" / "HLOUBKOVA-MERENI-2.md",
    REPO / "ANALYZA-HLOUBKOVA-2-ZADANI.md",
    # Druhé kolo hloubkové analýzy (2. 10. 2026). Přidáno proto, že tahle
    # brána je SAMA příkladem vady S27: má ruční seznam, takže nový dokument
    # projde „zeleně", aniž ho kdy otevře. Naměřeno 2. 10. 2026: oba soubory
    # níž v seznamu nebyly a brána přesto hlásila „VŠE OK".
    REPO / "ANALYZA-HLOUBKOVA-ORCHESTRA-2.md",
    REPO / "_analyza" / "HLOUBKOVA-MERENI-3.md",
    REPO / "IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md",
    # 2. 10. 2026: jazykový inventář a jeho plán. NAMĚŘENO PŘI PŘIDÁVÁNÍ: tenhle
    # dokument v seznamu NEBYL, ačkoli vznikl ve stejný den jako tři soubory
    # výše — brána tedy hlásila „VŠE OK" nad dokumentem, který nikdy neotevřela.
    # Je to **po páté** táž vada (S27): ruční seznam, který se musí doplňovat
    # ručně, není brána. Náprava (projít složku, ne seznam) je samostatné
    # rozhodnutí — do té doby sem každý nový dokument PATŘÍ.
    REPO / "IMPLEMENTACE-HRANICE-JAZYKA.md",
    # 2. 10. 2026 (08:5x): plán úprav z nových nálezů (N1–N6) vzniklý při
    # provádění A1–A4 a Z1–Z8. Přidán ve STEJNÉ session, která ho napsala —
    # protože „přidám ho příště" je přesně ten krok, na kterém se to **po páté**
    # nepovedlo (viz komentář výše). Nový dokument v tomhle workspace patří sem
    # ve chvíli vzniku, ne později.
    REPO / "IMPLEMENTACE-NOVE-NALEZY-Z-UKOTVENI.md",
    # 2. 10. 2026 (09:0x): prompt pro novou session (ověření práce předchozí
    # session + pokračování). Vznikl při sjednocení zdrojů po souběhu TŘÍ session.
    REPO / "PROMPT-NOVA-SESSION.md",
    # 2. 10. 2026 (06:25): záznam o souběhu DVOU SESSION nad tímhle workspace.
    # NAMĚŘENO PŘI PŘIDÁVÁNÍ: `HANDOFF.md` psaly dvě session současně a jedna
    # z nich si toho nevšimla — zápis jí systém odmítl, což je správně.
    REPO / "SOUBEH-SESSION-NALEZY.md",
    # Živý rozcestník nasazení (11 opatření, cíl −79 % nákladů). Do 2. 10. 2026
    # nebyl zmíněný v AGENTS.md, HANDOFF.md ANI OTEVRENA-TEMATA.md.
    STANICE / "DEPLOY-VYLEPSENI.md",   # D6: zustal stanici
    STANICE / "OTEVRENA-TEMATA.md",   # D6: zustal stanici
    # 2. 10. 2026 (dopoledne): metodický dokument „jak psát design dokumenty
    # a plánovat vývoj" — vznikl na zadání uživatele a je určený k dalšímu
    # budování (podklad pro revizi skillu game-developer a přepis designu hry).
    # Přidán ve STEJNÉ session, která ho napsala — „přidám ho příště" je krok,
    # na kterém to v tomhle workspace padlo už pětkrát (viz komentáře výš).
    REPO / "JAK-PSAT-DESIGN-A-PLANOVAT-VYVOJ.md",
    # 2. 10. 2026 (10:4x): zadání pro novou session po ověření — co provést,
    # co zadokumentovat a co připravit pro plánovací session. Vzniklo ve session,
    # která ověřovala práci session `eb127abd` (12/12 bodů §7.2).
    # POZOR: tenhle soubor sám sobě přikazuje, že sem patří — a je to právě ten
    # krok, na kterém to v tomhle workspace padlo ŠESTKRÁT (vada S27: ruční seznam).
    REPO / "NEXT-SESSION-INSTRUKCE.md",
    # 4. 10. 2026: plán separace workspace — v něm přibyl §9 (záznam o přesunu
    # obecných pravidel do DSH_HOME) a §10 (plán přesunu na E:, k validaci).
    # Přidán ve STEJNÉ session, která ho psala. Bez toho by brána nad ním
    # hlásila „VŠE OK", aniž ho otevřela — a to je **osmé** opakování téhož
    # kroku (vada S27: ruční seznam místo projití složky). Naměřeno 4. 10. 2026:
    # soubor v seznamu NEBYL, přestože do něj tahle session psala.
    REPO / "PLAN-SEPARACE-WORKSPACE.md",
    # 2. 10. 2026 (11:3x–12:0x): dokumenty, které vznikly při plnění zadání
    # (push orchestra, granule, N1/N3, rozhodnutí o nástrojích, podklad pro
    # plánovací session). Přidány ve STEJNÉ session, která je napsala — je to
    # **posedmé**, co se tenhle krok dělá ručně, a posedmé to byl krok, na
    # kterém to v tomhle workspace padalo (vada S27: ruční seznam místo projití
    # složky). Důkaz, že to není formalita: kdyby tu nebyly, brána by nad nimi
    # hlásila „VŠE OK", aniž je otevřela.
    REPO / "_analyza" / "C-PODKLAD-SMLOUVY.md",
    REPO / "_analyza" / "a3-brany-novych-granuli.md",
    # 2. 10. 2026 (11:0x–12:0x): PLÁN dalších kroků. NAMĚŘENO PŘI PŘIDÁVÁNÍ:
    # tenhle dokument v seznamu **NEBYL**, ačkoli ho plánovací session sama
    # napsala a sám uživatel na to upozornil („PLAN-DALSI-KROK.md tam ještě
    # není"). Je to **po osmé** táž vada (S27: ruční seznam místo projití
    # složky) — a je to zároveň důkaz, že ani upozornění v zadání ten krok
    # neudělá samo. Ručně ověřeno týmž vzorem: 17 960 znaků, rozbito: ne.
    REPO / "PLAN-DALSI-KROK.md",
    REPO / "_analyza" / "A-UKOL-ZAZNAM.md",
    # 2. 10. 2026: POSTUP PŘEDÁVÁNÍ mezi sessionami (dva kroky: plánovací
    # a akční) se šablonami promptů. Nahrazuje jednorázový PROMPT-NOVA-SESSION.md.
    # Je to dokument, ze kterého se bude **řídit každé další předání** — kdyby ho
    # brána neviděla, mohla by v něm být rozbitá diakritika a nikdo by si toho
    # nevšiml právě ve chvíli, kdy se podle něj rozhoduje.
    STANICE / "PREDAVANI-SESSION.md",   # D6: zustal stanici
    REPO / "repo" / ".forge" / "check-schema.py",
    REPO / "repo" / ".forge" / "vision-profile.json",
    REPO / "repo" / ".forge" / "baseline.py",
    REPO / "tools" / "test-check-schema.py",
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
    REPO / "tools" / "kontrola-diakritiky.py",
    # 2. 10. 2026 (plánovací session, 11:4x–12:3x UTC): ověření práce akční
    # session (Úkoly A–D a B1). Doplněny ve STEJNÉ session, která je napsala —
    # a NAMĚŘENO PŘI PŘIDÁVÁNÍ: `HANDOFF.md` v seznamu **už byl** (přidán dřív),
    # ale `_analyza/c2-sonda-uvozovky.py` v něm **nebyl**, ačkoli na něj
    # odkazovaly DVA dokumenty (`HANDOFF.md` §16.11 a `g1-diakritika-novych.py`)
    # — přitom soubor na disku vůbec neexistoval. Byl to **doklad, který se
    # ztratil**; obnoven a přidán sem. Je to **po desáté** táž vada (S27).
    REPO / "_analyza" / "c2-sonda-uvozovky.py",
    # 2. 10. 2026 (11:4x–12:4x): oddíly, kterými se `HANDOFF.md` rozšířil
    # (§17 výsledky ověření, §8f vlastní omyly). Drží se jako samostatné
    # soubory, protože se zapisovaly skriptem (`s17-zapis-handoff.py`,
    # `s8f-zapis-handoff.py`) — a skript, který text vkládá, se musí dát ověřit.
    REPO / "_analyza" / "s17-novy-oddil.md",
    REPO / "_analyza" / "s8f-novy-oddil.md",
    # 2. 10. 2026 (12:2x): §17.11 — doplnění na konci session (finální souhrn
    # bran, přegenerovaný inventář, doplnění všech 12 skillů do brány).
    REPO / "_analyza" / "s17b-doplneni.md",
    # 2. 10. 2026 (12:3x): KRONIKA PROJEKTU — nový TRVALÝ dokument, který
    # přežívá předávání (na rozdíl od `HANDOFF.md`, který se přepisuje).
    # Drží celý příběh: sessions, nálezy, omyly, poučení, návrhy.
    # Patří sem proto, že je to **autorita o průběhu projektu** — kdyby v ní
    # byla rozbitá diakritika, nikdo by si toho nevšiml právě ve chvíli,
    # kdy se podle ní dělá analýza postupu a návrhy na zlepšení.
    REPO / "KRONIKA-PROJEKTU.md",
    # 2. 10. 2026 (12:5x–13:3x UTC, PLÁNOVACÍ session — ověření práce akční
    # session o krok dřív): nástroje, kterými se to ověřovalo. Jsou tady proto,
    # že vznikly ve STEJNÉ session, která je psala — a to je krok, na kterém to
    # v tomhle workspace padlo **dvanáctkrát** (S27: ruční seznam místo
    # projití složky). NAMĚŘENO PŘI PŘIDÁVÁNÍ: `p18-sonda-tpm.py` je toho
    # dokladem — jeho první verze stahovala log `urllib`em a padala na
    # `HTTP 401` po přesměrování (TLS v Pythonu), což vypadalo jako vadný
    # přístup na GitHub, a byl to přitom jen špatný nástroj na tuhle práci.
    REPO / "_analyza" / "p18-sonda-tpm.py",
    REPO / "_analyza" / "p18-stahni-log.mjs",
    REPO / "_analyza" / "p18-prompt-tokeny.py",
    REPO / "_analyza" / "p18-pr-a-behy.mjs",
    REPO / "_analyza" / "p18b-jmena-behu.mjs",
    REPO / "_analyza" / "p18c-stav-uloh.mjs",
    REPO / "_analyza" / "s18-zapis-handoff.py",
    REPO / "_analyza" / "s18-prepocitej-omyly.py",
    REPO / "_analyza" / "s18-novy-oddil.md",
    REPO / "_analyza" / "s8g-novy-oddil.md",
    REPO / "_analyza" / "s18b-doplneni.md",
    REPO / "_analyza" / "s18c-omyl68-radek.md",
    REPO / "_analyza" / "s18c-doplneni.md",
    REPO / "_analyza" / "s18c-dopln-omyl68.py",
    REPO / "_analyza" / "s18c-sonda-kotvy.py",
    REPO / "_analyza" / "s18d-sestav-handoff.py",
    REPO / "_analyza" / "s18e-l13-radek.md",
    REPO / "_analyza" / "s18e-dopln-l13.py",
    REPO / "_analyza" / "s18f-oprav-hlavicku.py",
    REPO / "_analyza" / "p18d-kontrola-utf8.py",
    REPO / "_analyza" / "p19-sonda-groq.py",
    REPO / "_analyza" / "p19-push.py",
    REPO / "_analyza" / "p19b-cekej-pages.mjs",
    REPO / "_analyza" / "s19-oddil-groq.md",
    REPO / "_analyza" / "s19-dopln-odpoved-groq.py",
    REPO / "_analyza" / "s19-push-oddil.md",
    REPO / "_analyza" / "s19-omyl69-radek.md",
    REPO / "_analyza" / "s19-zapis-handoff.py",
    REPO / "_analyza" / "s19b-dopln-souhrn.py",
    REPO / "_analyza" / "s19c-radek16.md",
    REPO / "_analyza" / "s19c-h13.md",
    REPO / "_analyza" / "s19c-l14.md",
    REPO / "_analyza" / "s19c-dopln-kroniku.py",
    REPO / "_analyza" / "s19d-dopln-h13.py",
    REPO / "_analyza" / "s19e-oprav-hlavicku.py",
    REPO / "_analyza" / "s19f-oprav-deploy.py",
    REPO / "_analyza" / "s19g-oddil-deploy.md",
    REPO / "_analyza" / "s19g-omyl70-radek.md",
    REPO / "_analyza" / "s19g-zapis.py",
    REPO / "_analyza" / "s19h-souhrn-8g.py",
    REPO / "_analyza" / "s19i-souhrn-oprava.py",
    REPO / "_analyza" / "p19f-over-main.mjs",
    REPO / "_analyza" / "p19g-granule-vs-groq.py",
    REPO / "_analyza" / "p19h-groq-presne.py",
    REPO / "_analyza" / "p19i-co-zmensit.py",
    REPO / "_analyza" / "p19i-sonda.py",
    REPO / "_analyza" / "p19i-sonda2.py",
    REPO / "_analyza" / "s19k-oddil-granule.md",
    REPO / "_analyza" / "s19k-omyl71-radek.md",
    REPO / "_analyza" / "s19k-zapis.py",
    REPO / "_analyza" / "s19l-souhrn-8g.py",
    REPO / "_analyza" / "s19j-hlavicka-ziva.py",
    REPO / "_analyza" / "s19m-dopln-commity.py",
    REPO / "_analyza" / "s20-odloz-groq.py",
    REPO / "_analyza" / "s20-plan-31.md",
    REPO / "_analyza" / "s20b-plan-poradi.py",
    REPO / "_analyza" / "s20-oddil-odlozeno.md",
    REPO / "_analyza" / "s20-na16-radek.md",
    REPO / "_analyza" / "s20c-zapis-rozhodnuti.py",
    REPO / "_analyza" / "s20d-zadani.py",
    REPO / "_analyza" / "s20d-sonda.py",
    REPO / "_analyza" / "s20e-zadani-doplnky.py",
    REPO.parent / "uo-shadows" / ".github" / "workflows" / "ci.yml",
    REPO / "README.md",
    REPO / "README.md",
    # 2. 10. 2026 (18:0x–19:0x, AKČNÍ session — dokončení auditu dokumentace):
    # zadání, podle kterého se pracovalo. Přidáno **ve stejné session, která
    # vzniklo** — a je to **po třinácté** táž vada (S27: ruční seznam místo
    # projití složky): tenhle soubor vznikl v 18:09:30, tedy AŽ PO auditu,
    # a do seznamu se musel doplnit ručně.
    # ⚠ NAMĚŘENO PŘI PŘIDÁVÁNÍ a zapsáno jako nález: v tomhle seznamu **NENÍ**
    # ani `_analyza/AUDIT-DOKUMENTACE.md` ani žádný z nástrojů, kterými audit
    # měřil (`audit1-*` … `audit6-*`) — jinými slovy **audit dokumentace sám
    # skončil jako dokument, který brána nikdy neotevře.** Pokrývá je jen
    # `g1-diakritika-novych.py` (prochází složku). Náprava je opatření **6**
    # (projití složky místo seznamu) a patří do session B — sem se nedoplňuje,
    # aby se ruční seznam nerozrůstal na stovky cest (audit: 105 cest,
    # 96 řádků komentářů).
    REPO / "ZADANI-DOKONCENI-AUDITU.md",
    # 2. 10. 2026 (18:4x): zadání pro PLÁNOVACÍ session, která ověří dokončení
    # auditu. Vzniklo **mimo** `NEXT-SESSION-INSTRUKCE.md`, protože ten patří
    # souběžné session (nález **H28**, `HANDOFF.md` §23.7).
    # Je to **po čtrnácté** táž vada (S27: ruční seznam místo projití složky) —
    # a proto je u toho číslo: **dokud se seznam nenahradí projitím složky
    # (opatření 6), poroste to s každým novým dokumentem.** Tenhle komentář
    # sám je toho dokladem: za jednu session se sem doplňovalo **dvakrát**.
    REPO / "ZADANI-PO-AUDITU.md",
    # 2. 10. 2026 (19:0x, PLÁNOVACÍ session): oprava měřidel. Vzniklo **mimo**
    # `NEXT-SESSION-INSTRUKCE.md`, protože ten patří souběžné session
    # (nález **H28**, `HANDOFF.md` §23.7 a §24.9).
    REPO / "ZADANI-OPRAVA-MERIDEL.md",
    # 2. 10. 2026 (21:2x, AKČNÍ session — oprava měřidel): zadání pro DALŠÍ
    # session. Vzniklo **mimo** `NEXT-SESSION-INSTRUKCE.md` ze stejného důvodu
    # jako předchozí (ten patří souběžné session, nález **H28**).
    REPO / "ZADANI-DODELAT-MERIDLA.md",
]

# ── PROJITÍ SLOŽKY (2. 10. 2026, 19:0x) — KONEC RUČNÍHO SEZNAMU ──────────────
# **To je opatření 6 z auditu dokumentace** (`AUDIT-DOKUMENTACE.md` §6) a je to
# **patnáctý** výskyt vady S27 (ruční seznam místo projití složky) v projektu.
#
# ⚠ CO SE TÍM MĚŘILO PŘEDTÍM (naměřeno, ne odhad): seznam výš obsahoval
# **57 dokumentů**, ale v kořeni workspace jich bylo **39** a v `_analyza`
# **45** — dohromady **84**. Brána tedy byla zelená nad **28 dokumenty, které
# nikdy neotevřela**; mezi nimi `_analyza\AUDIT-DOKUMENTACE.md` — tedy sám
# audit, podle kterého se opravovalo. Klasický „zelená nad neotevřeným
# souborem" (`overovani` §7.10).
#
# ⚠ A DRUHÁ PAST, KTERÁ SE TÍM ZAVÍRÁ: ruční seznam se musel doplňovat při
# **každém** novém dokumentu — jen 2. 10. 2026 se sem doplňovalo **třikrát**
# (dva dokumenty doplnila předchozí session, třetí tahle). Kdo na to zapomene,
# dostane zelenou od brány, která soubor nevidí, a **nikdo to nepozná**.
#
# PROJITÍM SE ROZSAH ROZŠIŘUJE, NIC SE NEZTRÁCÍ: seznam výš zůstává
# (jsou v něm i soubory mimo tyhle dvě složky) a projdou se k němu navíc
# VŠECHNY `.md` a `.py` v kořeni workspace a v `_analyza\`. Deduplikuje se
# podle `resolve()`, aby se soubor nepočítal dvakrát.
#
# ⚠ CO SE ZÁMĚRNĚ VYLUČUJE (a je to VIDĚT ve výpisu, ne tiché):
#   · `snapshot-*` — zmrazené kopie dokumentace (nález **H27**: kopie nemají
#     vstupovat do měřidel; `audit1-inventar.py` je ze stejného důvodu vylučuje)
#   · `_zaloha*`, `zaloha*`, `*-pred-*`, `*-zaloha*` — **zálohy a pracovní
#     kopie**. Mají právo být rozbité (jsou to kopie stavu před opravou),
#     takže jejich kontrola by vyráběla **falešné poplachy** (`overovani` §9.5).
#     ⚠ **To je přiznaná mez:** co je záloha, pozná brána podle JMÉNA, ne podle
#     obsahu — a to je ruční seznam o vrstvu níž. Zapsáno jako nález **H31**.
VYLOUCENE_PREDPONY = ("snapshot-", "_zaloha", "zaloha", "handoff-pred", "kronika-pred")
VYLOUCENE_OBSAHUJE = ("-pred-", "-zaloha")


def _je_zaloha(p: pathlib.Path) -> bool:
    jmeno = p.name.lower()
    if jmeno.startswith(VYLOUCENE_PREDPONY):
        return True
    return any(cast in jmeno for cast in VYLOUCENE_OBSAHUJE)


_uz = {p.resolve() for p in SOUBORY}
_projdene, _preskocene = 0, []
for _slozka in (REPO, REPO / "_analyza"):
    if not _slozka.is_dir():
        continue
    for _vzor in ("*.md", "*.py"):
        for _p in sorted(_slozka.glob(_vzor)):
            if _je_zaloha(_p) or _p.resolve() in _uz:
                if _je_zaloha(_p):
                    _preskocene.append(_p.name)
                continue
            SOUBORY.append(_p)
            _uz.add(_p.resolve())
            _projdene += 1
print(f"  PROJITÍ SLOŽKY: přidáno {_projdene} souborů (kořen + _analyza), "
      f"celkem ke kontrole {len(SOUBORY)}")
print(f"  VYLOUČENO jako záloha/snapshot: {len(_preskocene)} "
      f"({', '.join(sorted(set(_preskocene))[:6])}{' …' if len(set(_preskocene)) > 6 else ''})")

# ── SKILLY: PROJITÍM SLOŽKY, NE SEZNAMEM ────────────────────────────────────
# Do 2. 10. 2026 tu bylo **12 ručně psaných cest** a byl to dvanáctý výskyt
# vady S27 (ruční seznam místo projití složky) — naposledy se přišlo na to,
# že v seznamu bylo **5 z 12 skillů**, takže brána hlásila „VŠE OK" nad sedmi
# soubory, které nikdy neotevřela. Naměřený důkaz, že to není formalita:
# `overovani` — skill, do kterého táž session psala — v seznamu NEBYL.
#
# Teď se složka PROJDE. Nový skill je vidět ve chvíli vzniku; když některý
# zmizí, brána to ohlásí jako `CHYBA ... neexistuje` (a to je správně —
# chybějící skill je nález, ne ticho).
SKILLS_DIR = pathlib.Path(r"C:\Users\Ssevc\.dsh\skills")
_skilly = sorted(SKILLS_DIR.glob("*/SKILL.md")) if SKILLS_DIR.is_dir() else []
if not _skilly:
    print(f"  CHYBA {SKILLS_DIR}: žádné skilly k projití (složka chybí nebo je prázdná)")
SOUBORY += _skilly

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
VLASTNI = REPO / "tools" / "kontrola-diakritiky.py"
VLASTNI_TEXTY = ["diakritiky", "kódování", "souborů", "příliš", "žluťoučký"]
NAHRADNI = "\ufffd"

chyb = 0
archivovanych = []      # soubory v seznamu, které se ARCHIVOVALY (D5)
for f in SOUBORY:
    if not f.exists():
        # ⚠ P8b (přesun na E:, 4. 10. 2026): archivace (rozhodnutí D5) přesunula
        # ~99 jednorázových nástrojů do `_analyza/_archiv/`. Tenhle seznam je
        # RUČNÍ a nástroje z 2. 10. pořád jmenuje — dřív by každý z nich hlásil
        # `neexistuje` (naměřeno 44 chyb u souborů, které jsou v pořádku, jen
        # archivované).
        # Pravidlo: archivovaný soubor NENÍ chyba, ale musí být VIDĚT — kdyby se
        # přeskočil tiše, brána by nad ním vypadala zeleně, aniž ho otevřela
        # (přesně vada S27, kterou tenhle soubor sám popisuje).
        if (REPO / "_analyza" / "_archiv" / f.name).exists():
            archivovanych.append(f.name)
            continue
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
if archivovanych:
    # Viditelný výčet, ne ticho: brána se má přiznat, co NEotevřela.
    print(f"ARCHIVOVÁNO (D5) — neotevřeno, není to chyba: {len(archivovanych)} "
          f"souborů v `_analyza/_archiv/`")
    for j in sorted(archivovanych)[:6]:
        print(f"    {j}")
    if len(archivovanych) > 6:
        print(f"    … +{len(archivovanych) - 6}")
    print()
print(f"ZMĚŘENO: otevřeno {len(SOUBORY) - len(archivovanych)} z "
      f"{len(SOUBORY)} souborů v seznamu "
      f"(archivováno {len(archivovanych)}, chyb {chyb})")
print("VŠE OK" if chyb == 0 else f"NALEZENY CHYBY ({chyb})")
sys.exit(0 if chyb == 0 else 1)
