# -*- coding: utf-8 -*-
r"""P21 — zápis řádku session, nálezů H104–H106 a souhrnu do `KRONIKA-PROJEKTU.md`.

PROČ SKRIPTEM (a ne `edit` toolem): řádek session P20 v kronice je DELŠÍ než
okno, ve kterém se čte. „Vložení" kotvou z načteného (zkráceného) řádku by celý
řádek NAHRADILO zkráceným textem — to je omyl **206** z P20 a stálo by to
záznam session. Skript proto bere řádek **z disku** a vkládá ZA něj.

IDEMPOTENTNÍ: když už řádek i sekce v dokumentu jsou, jen to ověří a nic
nemění — proto ho může pouštět i `_analyza/p20-d-doklady.py` v dávce.

⚠ Konce řádků se NEMĚNÍ: soubor se čte po bajtech, řádky se dělí
`splitlines(keepends=True)` a zapisuje se zpět `write_bytes`. Pythoní
`write_text()` by `\n` přeložil na `\r\n` a vyrobil dvojité `\r`
(viz skill `dsh-prostredi` §3).

Použití: python _analyza/p21-zapis-kroniky.py
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
KRONIKA = WS / "KRONIKA-PROJEKTU.md"

RADEK_35 = (
    "| **35** | **6. 10. 2026** (12:0x–12:4x UTC = 14:0x–14:4x +02:00) | "
    "**akční (dokončení P20)** | **DOKONČENÍ P20: ověření bran, commit a push** — "
    "než se cokoli udělalo, změřil se ŽIVÝ stav, a ten byl jiný, než tvrdilo zadání: "
    "P20 **NEBYLA commitnutá** (H104) — `HEAD` = `origin/main` = `b781c84` a **23 souborů** "
    "leželo v pracovním stromě. Pak **šest bran po sobě**, **commit** a **push** "
    "(vyžádal uživatel) | "
    "**Brány PŘED commitem: `g3` 37 bran / 0 nenulových / `exit 0` · `validate-all` "
    "`✓ VŠE V POŘÁDKU` · `kronika SEDÍ` (205/103/33) · `handoff` 83/83 · `NEOVĚŘENO` 0 · "
    "doklady 21 (jediný červený = H103, doložený falešný poplach). Inventář přegenerován "
    "(**6 809 nálezů**) a brány po něm znovu zelené. **Commit `b2fd758`** (23 souborů, "
    "+2327/−296) a **push `b781c84..b2fd758`**; `ls-remote` → **`b2fd758`**, "
    "`origin/main..HEAD` = **0** | **—** | "
    "**Nálezy H104–H106:** zadání P20 **tvrdilo commit, který neexistoval** "
    "(reflog `HEAD@{0}` = P19) · nabídka **H1 stojí na neplatném předpokladu** — "
    "`save.gd` se ve hře **nikdy nevolá** (jediný volající je test), takže "
    "„spawn přepíše pozici“ **nenastává** · hlavička zadání udávala čas "
    "**„13:2x UTC“, ale mtime souboru je 13:30 +02:00 = 11:30 UTC** "
    "(lokální čas zapsaný jako UTC) |"
)

SEKCE_215 = """### 2.15 Nálezy H104–H107 (z P21, 6. 10. 2026 — PROVÁDĚCÍ session: ověření bran, commit a push P20)

**Vznikly z téhož kroku: NEJDŘÍV se měřil živý stav, teprve pak se něco dělalo.**
Neobviňují cizí kód — **H104** je nález o **dokumentu** (tvrdil stav, který
nenastal), **H105** o **nepoužívaném kódu** (vada je jinde, než zadání tvrdilo),
**H106** o **časovém údaji** (lokální čas vydávaný za UTC) a **H107** o **dokladu,
který byl zelený z nesprávného důvodu** (měřil rovnost, jež po commitu platit
nemůže). Záznam: `HANDOFF.md` **§39**.

| # | Nález | Doklad (měřením) | Stav |
|---|---|---|---|
| **H104** | **Zadání P20 tvrdilo, že P20 je COMMITNUTÁ** („`HEAD` orchestry je `b781c84` + **1 commit P20** … **NEPUSHNUTÝ**“); **nebyla commitnutá vůbec.** Všech **23 souborů** P20 leželo **necommitnutých** v pracovním stromě a `HEAD` = `origin/main` = **`b781c84`**; reflog commit P20 **neměl**. Kdo by zadání věřil, **pushoval by něco, co neexistuje** — a `zadání kontrola` by čítala jiný počet commitů, než zadání tvrdilo | `git status --porcelain` (**23 položek**: 14× `M`, 9× `??`), `git reflog -10` (`HEAD@{0}` = commit **P19**), `git rev-parse HEAD` == `git rev-parse origin/main` == `b781c84`, `git rev-list --count origin/main..HEAD` = **0** | **VYŘEŠENO** — P20 **commitnuta** (`b2fd758`) a **pushnuta**; tvrzení zůstává v zadání jako **historické** (nepřepisuje se) |
| **H105** | **Nabídka H1 stojí na NEPLATNÉM předpokladu.** Zadání tvrdilo: *„`save()` uloží pozici, ale **spawn ji přepíše**“*. Naměřeno: **`save.gd` se ve hře NIKDY nevolá** — `main.tscn` má **jediný uzel** (`game.gd`), ten `save.gd` nezná a jeho **vlastní** `_save_state()`/`_load_state()` (přes `user://sandbox.cfg`) **taky nikdo nevolá**. Hra tedy **neukládá nic**, takže spawn nemá co přepsat — „opravit spawn“ by opravovalo kód, který se nespouští | **statická analýza** (NEspuštěno): `main.tscn` (6 řádků, jen `game.gd`), `grep` přes **celý** rep hry (`*.gd` i `*.tscn`) → jediný volající `save.gd` je **`tests/run_tests.gd:849`**; `_save_state`/`_load_state`/`sandbox.cfg` se vyskytují **jen ve svých definicích** (`game.gd:355–377`) | **OTEVŘENO** — mění obsah nabídky H1: správná práce je **zapojit persist do hry** (nebo rozhodnout, že hra ukládat nemá). Hra je ale **záměrně pozastavená** (rozhodnutí uživatele: chystá přepis architektury zadání hry) |
| **H106** | **Hlavička zadání P20 udávala čas jako UTC, ale byl to čas LOKÁLNÍ.** Stojí tam *„6. 10. 2026, 13:2x UTC“*; `mtime` téhož souboru je **13:30 +02:00 = 11:30 UTC**. Rozdíl je přesně offset pásma, takže se **nezapsal špatný okamžik, ale špatné pásmo** — a kdo porovná `mtime` souboru s hlavičkou, dostane **dvouhodinový rozpor** a bude hledat změnu, která se nestala | `(Get-Date).ToUniversalTime()` vs. `(Get-Date)` v témž okamžiku (**12:10 UTC = 14:10 +02:00**), `mtime` souboru `NEXT-SESSION-INSTRUKCE.md`, a **vlastní řádek kroniky P20**, který pásma uvádí správně („10:2x–13:2x UTC = 12:2x–15:2x +02:00“) | **ZAPSÁNO** — pravidlo pro příští session: **čas vždy s pásmem** (nebo označit, že jde o lokální). Historický údaj se **nepřepisuje** |
| **H107** | **Doklad P20 `p20-a-kody-bran.py` měřil ROVNOST kotvy zadání s živým `HEAD` — a zelený byl JEN PROTO, že práce P20 nebyla commitnutá.** Zadání se ale píše **PŘED commitem**, takže po každém commitu se rovnost **nutně** rozbije, ačkoli je zadání v pořádku (kotva pořád ukazuje na commit, na kterém se měřilo). Doklad tedy netvrdil „zadání je v pořádku“, ale „nikdo od měření necommitnul“ — **a to je jiná věta**. Odhalil to `p20-d-doklady.py`, který ho pouští v dávce — ne nový test | `p20-a-kody-bran.py` **po** commitu P20 (`b2fd758`): **`exit 1`** se dvěma `CHYBA` („v ŽIVÉM zadání se našla kotva orchestry“, „kotva zadání = živý HEAD“); **před** commitem týž doklad **8/0** | **OPRAVENO (P21)** — kontrola se ptá, co má: **„je kotva skutečný commit v repu a není novější než `HEAD`?“** (`cat-file -t` + `merge-base --is-ancestor`; obojí **bez `^`** — `shell=True` by ho zahodil, past §5c). Fixtury na `zadani-kontrola.py` (kotva = živý `HEAD` → `exit 0`; kotva = nedostupný commit → `exit 1`) zůstávají **beze změny** |
"""

STARY_CELKEM = "| **celkem** | **26 bloků, 33 sessions** |"
NOVY_CELKEM = "| **celkem** | **26 bloků, 34 sessions** |"

kontrol = 0
chyb = []


def k(ok: bool, popis: str) -> None:
    global kontrol
    kontrol += 1
    print(f"  {'OK  ' if ok else 'CHYBA'}  {popis}")
    if not ok:
        chyb.append(popis)


print("=" * 78)
print("P21 — zápis do KRONIKA-PROJEKTU.md (idempotentní)")
print("=" * 78)

k(KRONIKA.is_file(), f"kronika existuje: {KRONIKA}")

puvodni = KRONIKA.read_bytes()
text = puvodni.decode("utf-8")
radky = text.splitlines(keepends=True)

k("\r" not in text, "soubor má konce řádků bez CR (LF) — zapisuje se zpět bajty")

# --- 1) řádek session 35 do §1 ---------------------------------------------
idx34 = next((i for i, r in enumerate(radky) if r.startswith("| **34** |")), None)
k(idx34 is not None, "řádek session 34 (P20) v §1 nalezen")

uz35 = any(r.startswith("| **35** |") for r in radky)
if uz35:
    print("  OK    řádek 35 už v kronice je — nevkládám")
    kontrol += 1
    # ⚠ OPRAVA TYPU: první verze vložila typ „prováděcí (dokončení P20)“, který
    # brána `kronika-kontrola.py` NEZNÁ (uznává akční/plánovací/ověřovací/
    # analýza/rozhodovací) → hlásila „1 řádků session nemá uvedený typ“.
    # Našla to BRÁNA, ne já — proto se typ opravuje tady, a ne ručně.
    i35 = next(i for i, r in enumerate(radky) if r.startswith("| **35** |"))
    if "**prováděcí" in radky[i35]:
        radky[i35] = radky[i35].replace("**prováděcí (dokončení P20)**",
                                        "**akční (dokončení P20)**")
        k("**akční (dokončení P20)**" in radky[i35], "typ řádku 35 opraven na `akční`")
    else:
        print("  OK    typ řádku 35 je uznávaný — neměním")
        kontrol += 1
else:
    k(idx34 is not None, "je kam vložit (kotva 34)")
    if idx34 is not None:
        konec = "\n" if radky[idx34].endswith("\n") else ""
        radky.insert(idx34 + 1, RADEK_35 + konec)
        k(any(r.startswith("| **35** |") for r in radky), "řádek 35 vložen ZA řádek 34")

# --- 2) sekce 2.15 s nálezy H104–H106 --------------------------------------
uz215 = any(r.startswith("### 2.15 ") for r in radky)
if uz215:
    print("  OK    sekce 2.15 už v kronice je — nevkládám")
    kontrol += 1
else:
    idx3 = next((i for i, r in enumerate(radky) if r.startswith("## 3. Počty omylů")), None)
    k(idx3 is not None, "kotva `## 3. Počty omylů` nalezena")
    if idx3 is not None:
        radky.insert(idx3, SEKCE_215 + "\n")
        k(any(r.startswith("### 2.15 ") for r in radky), "sekce 2.15 vložena před §3")

# --- 3) souhrnný řádek `celkem` v §3 ---------------------------------------
i_cel = next((i for i, r in enumerate(radky) if r.startswith("| **celkem** |")), None)
k(i_cel is not None, "souhrnný řádek `celkem` v §3 nalezen")
if i_cel is not None:
    radek = radky[i_cel]
    if NOVY_CELKEM in radek:
        print("  OK    souhrn už je přepočítaný (34 sessions) — neměním")
        kontrol += 1
    else:
        k(STARY_CELKEM in radek, "souhrn má očekávaný tvar (33 sessions)")
        radky[i_cel] = radek.replace(STARY_CELKEM, NOVY_CELKEM)
        k(NOVY_CELKEM in radky[i_cel], "souhrn přepsán na 34 sessions")

# --- 4) zápis a kontrola ----------------------------------------------------
novy = "".join(radky).encode("utf-8")
if novy != puvodni:
    KRONIKA.write_bytes(novy)
    print(f"  ZAPSÁNO: {KRONIKA.name} ({len(puvodni)} → {len(novy)} B)")
else:
    print("  beze změny (vše už bylo zapsané)")

zpet = KRONIKA.read_bytes()
k(zpet == novy, "soubor na disku odpovídá zapsanému")
k(not zpet.startswith(b"\xef\xbb\xbf"), "kronika nemá BOM")
k(zpet.count(b"\r\n") == 0, "v souboru nejsou CRLF (zůstalo LF)")

# --- 5) nezávislé ověření toho, co má být v dokumentu ----------------------
t2 = zpet.decode("utf-8")
k("| **35** |" in t2, "dokument obsahuje řádek session 35")
k("### 2.15 Nálezy H104–H107" in t2, "dokument obsahuje sekci s H104–H107")
for h in ("**H104**", "**H105**", "**H106**", "**H107**"):
    k(h in t2, f"dokument obsahuje {h}")
k("**26 bloků, 34 sessions**" in t2, "souhrn §3 uvádí 34 sessions")

# počet řádků tabulky §1 — TÝMŽ vzorem jako brána `kronika-kontrola.py` (r. 355),
# NE vlastním. První verze měla vzor vlastní a dala **33 místo 34** (řádek, který
# nezačíná `| **`, jí unikl) — a vytiskla to jako číslo. Je to táž past jako
# „statická metrika, která nic nespustí“: měřidlo se musí ptát AUTORITY.
import re as _re
_i1 = t2.find("## 1. Přehledová tabulka")
_i2 = t2.find("## 2.", _i1) if _i1 >= 0 else -1
v1 = t2[_i1:_i2] if _i1 >= 0 and _i2 > _i1 else ""
pocet_sessions = sum(1 for r in v1.splitlines()
                     if _re.match(r"^\|\s*\*\*\d+\*\*\s*\|", r))
print(f"\n  (řádků sessions v §1, vzorem brány: {pocet_sessions})")
k(pocet_sessions == 34, f"§1 má 34 řádků sessions (naměřeno {pocet_sessions})")

print("\n" + "=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {len(chyb)} chyb")
print("=" * 78)
for c in chyb:
    print(f"  CHYBA: {c}")

sys.exit(1 if chyb else 0)
