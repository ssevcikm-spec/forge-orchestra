# -*- coding: utf-8 -*-
r"""P20 — Úkol D (část): SPUSTÍ VŠECHNY DOKLADY `_analyza/` a vypíše, které projdou.

PROČ: doklady jsou důkazy a **nesmí tiše shnít**. Session, která mění brány,
musí vědět, které doklady tím rozbila — jinak zůstanou červené a nikdo nepozná,
jestli je vada v bráně, nebo v dokladu (`overovani` §10.1: `exit 1` ze špatného
důvodu vypadá jako správný nález).

⚠ NENÍ to náhrada `g3`: `g3` pouští jen VYBRANÉ brány. Tohle pouští i DOKLADY,
které v `g3` záměrně nejsou (jsou jednorázové nebo stavové) — proto se výsledek
nevydává za stav bran.

⚠ ROZŠÍŘENO P21 (6. 10. 2026): vzor bere i `p21-*` — session P21 přidala
`_analyza/p21-zapis-kroniky.py`, a **doklad, který není v tomhle seznamu,
shnije** (`HANDOFF.md` §38.8). Skript je **idempotentní**, takže v dávce
jen ověří, že řádek session i nálezy v kronice jsou.

Použití: python _analyza/p20-d-doklady.py
"""

import hashlib
import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
VZOR = re.compile(r"^(ov-|p1[6-9]-|p2[0-9]-|p3[0-9]-)")

# Sonda `p20-sonda-*` a `p20-c-kandidati` jsou JEDNORÁZOVÉ diagnostiky —
# spouštět je znovu nemá smysl (a `p20-c-kandidati` pouští ostatní doklady).
# ⚠ `p20-sonda-klicu.py` si navíc staví VLASTNÍ harness z živého `g3` a sahá
# přitom na `p20-scratch`; pouštět ho v dávce je zbytečné riziko.
PRESKOCIT = {"p20-sonda-jmena.py", "p20-sonda-klicu.py", "p20-c-kandidati.py",
             "p20-d-doklady.py",
             # ⚠ PŘESKOČENO 6. 10. 2026 (při dopisování záznamů P22): tenhle
             # doklad je **DOBOVÝ** — jeho kontroly tvrdí **pevná čísla**
             # („souhrn má očekávaný tvar 33 sessions", „§1 má 34 řádků").
             # Jenže souhrn je dnes **35 sessions / 208 omylů**, protože
             # přibyl řádek 36 a blok `8za` — takže správně hlásí **4 CHYBY**
             # a `exit 1`, ačkoli je kronika v pořádku.
             # Není to vada dokladu (v době vzniku měřil správně) ani kroniky:
             # je to **doklad, který měří STAV, ne smlouvu** — a stav se mění.
             # Kdyby zůstal v dávce, každá příští session uvidí „červený doklad"
             # a bude „opravovat" správná data. **Nemaže se** (je to záznam),
             # jen se **nespouští v dávce**; jeho roli převzal
             # `p22-zapis-zaznamu.py`, který je **idempotentní** a čísla si
             # bere **z brány** (`kronika-kontrola.py`), ne z hlavy.
             "p21-zapis-kroniky.py",
             # ⚠ PŘESKOČENO 7. 10. 2026 (P24): SONDY, které odpovídaly na JEDNU
             # otázku a mají odpovězeno. `p24-sonda-site.py` měřila, jestli jde
             # z Pythonu na síť (jde — a Cloudflare blokuje `Python-urllib`
             # podle User-Agenta, což je její hlavní nález);
             # `p24-sonda-m2.py` hledala, proč mutace M2 neshodí test tiku
             # (falešný svět zacyklil dispatch smyčku → Node `exit 134`).
             # Obě jsou **jednorázové diagnostiky**, ne opakovatelné doklady.
             # ⚠ PŘESKOČENO 7. 10. 2026 (P26): SONDY, které odpovídaly na JEDNU
             # otázku a mají odpovězeno. `p26-sonda-zapis.py` měřila STAV
             # SANDBOXU (zápis podprocesem do podadresářů workspace — v P26 to
             # **ZAMRZLO**, ne `PermissionError`; nález **P26-J**) a
             # `p26-sonda-rozsah.py` naměřila, KDE VŠUDE žijí řádky tabulek Hxx
             # (99 živých v 2 souborech + 139 zmrazených v 7 zálohách) — to je
             # podklad opravy brány `ov-g-neovereno.py` (nález **P25-K**).
             # Obě jsou **jednorázové diagnostiky**, ne opakovatelné doklady.
             "p26-sonda-zapis.py", "p26-sonda-rozsah.py",
             # ⚠ P24 (7. 10. 2026) — NEMAŽ: `p26` výše je PŘIDÁNÍ, ne náhrada.
             # Naměřeno P26: při vkládání sond P26 se tenhle řádek málem přepsal
             # a `p24-sonda-*` z `PRESKOCIT` **vypadly** — chytila to až brána
             # `p25-a-overeni.py` (A6: „sondy nejsou v PRESKOCIT“).
             "p24-sonda-site.py", "p24-sonda-m2.py",
             # ⚠ PŘESKOČENO 8. 10. 2026 (P27): SONDY, které odpovídaly na JEDNU
             # otázku a mají odpovězeno. `p27-sonda-endpointy.py` naměřila, které
             # endpointy volá test tiku (a které ne — na tom stál Úkol B1);
             # `p27-sonda-inventar.py` vypisuje, co je v otisku vstupů inventáře
             # (obě repa, vyloučené artefakty) — podklad měření A7.
             # Obě jsou **jednorázové diagnostiky**, ne opakovatelné doklady.
             "p27-sonda-endpointy.py", "p27-sonda-inventar.py",
             # ⚠ PŘESKOČENO 8. 10. 2026 (P28): SONDA, která odpovídala na JEDNU
             # otázku a má odpovězeno. `p28-sonda-cesty.py` naměřila, které
             # TVARY cest brána `over-skilly.py` neviděla (71 viděla, 90 jich
             # v dokumentech je) — to je podklad opravy B5 (§51.3). Je to
             # **jednorázová diagnostika**, ne opakovatelný doklad.
             "p28-sonda-cesty.py",
             # ⚠ PŘESKOČENO 9. 10. 2026 (P29): `p29-docx-vytah.py` je JEDNORÁZOVÝ
             # převod vstupu (docx od uživatele na ploše → text pro analýzu) a
             # `p29-b6-patch.py` je ZÁPISOVÝ patcher conductora — ten se v dávce
             # spouštět NESMÍ (podruhé by kotvy nenašel a nejde o měření).
             # Ostatní `p29-*` doklady bere `VZOR` sám (ověřeno: `p29-a-overeni.py`
             # i `p29-b6-mutace.py` odpovídají vzoru `p2[0-9]-`).
             "p29-docx-vytah.py", "p29-b6-patch.py",
             # ⚠ PŘESKOČENO 9. 10. 2026 (P30) — a je to VĚDOMÉ OPAK pravidla
             # „VZOR ho bere sám“, proto s důvodem:
             #  * `p30-mutace.py` je MUTAČNÍ TEST, který dočasně mění
             #    `HANDOFF.md` a `tools/over-skilly.py`. Tahle dávka má přitom
             #    POJISTKU PROTI ZÁPISU, která hash `HANDOFF.md` sleduje —
             #    pouštět v dávce skript, který sledovaný dokument mutuje, je
             #    přesně to, před čím ta pojistka je. Patří mimo dávku.
             #  * `p30-a-overeni.py` dávka BERE (vzor `p3[0-9]-` výš) — běží
             #    v LEVNÉM režimu (~1,5 min) a vypisuje čítač pro tuhle dávku.
             #    S `--plne` by pouštěl `g3` (rekurze) a `validate-all`, proto
             #    se v dávce `--plne` NEPOUŽÍVÁ.
             #  * `p30-sonda-stav.mjs`, `p30-sonda-d1.mjs`, `p30-sonda-deploy.mjs`
             #    jsou SONDY (živá služba, D1, GitHub API). Dávka hledá jen
             #    `*.py`, takže se jí netýkají — jsou tady proto, aby bylo
             #    vidět, že je nikdo nemá pouštět „naslepo“ v gatu.
             "p30-mutace.py", "p30-sonda-stav.mjs", "p30-sonda-d1.mjs", "p30-sonda-deploy.mjs",
             # ⚠ PŘESKOČENO 9. 10. 2026 (P30) — NAMĚŘENO, NE ODHADNUTO: tahle dávka
             # **přepsala živé dokumenty**. Pojistka proti zápisu níž ohlásila změnu
             # u **čtyř** sledovaných souborů (HANDOFF, KRONIKA, NEXT-SESSION,
             # `_registr-bran.json`) — a `mtime` ukázal, že HANDOFF, KRONIKA
             # i NEXT-SESSION mají **týž čas 9:41:55**, tedy je zapsal JEDEN skript.
             # Je to `p27-dopln-zaznamy.py`: jeho `vymen()` zapíše soubor
             # **i když kotvy nenašel** (řádek 41 je bez podmínky) a `exit 1` hlásí
             # až potom — „doklad, který spadl“, tedy **přesto zapsal**.
             # Následek: v zadání P30 zmizel STAVOVÝ ŘÁDEK (vrátil se text z P27).
             # `p27-aktualizuj-zadani.py` a `p27-patch-zadani.py` píšou do téhož
             # souboru. **Patcher staré session nepatří do dávky** — jeho práce je
             # hotová (stejný důvod, jako je v PRESKIP `p21-zapis-kroniky.py`).
             "p27-dopln-zaznamy.py", "p27-aktualizuj-zadani.py", "p27-patch-zadani.py",
             # ⚠ PŘESKOČENO 9. 10. 2026 (P31) — dva nové soubory, každý z JINÉHO
             # důvodu (a oba s KÓDEM, ne jen se jménem):
             #  * `p31-mutace.py` je MUTAČNÍ TEST OPRAV C1/C2 — dočasně mění
             #    `p28-b-mutace.py` a `p29-a-overeni.py` v KOPIÍCH a sám pouští
             #    měřidla, která sahají na `HANDOFF.md`. Dávka má POJISTKU PROTI
             #    ZÁPISU, která hash dokumentů sleduje — pouštět v ní test, který
             #    dokumenty čte a kopie mutuje, je přesně to, před čím pojistka je.
             #    (Stejný důvod jako u `p30-mutace.py`.)
             #  * `p31-sonda-g3.py` je JEDNORÁZOVÁ DIAGNOSTIKA (odpověděla na
             #    otázku „proč je `p28-b-mutace.py` 27/2": H131 + H132) a pouští
             #    přitom DVĚ `g3` — v dávce by to bylo 2× 200 s navíc a nic by
             #    neměřila. `p31-a-overeni.py` dávka BERE (vzor `p3[0-9]-`) —
             #    běží v LEVNÉM režimu a vypisuje čítač pro tuhle dávku.
             "p31-mutace.py", "p31-sonda-g3.py",
             # ⚠ PŘESKOČENO 9. 10. 2026 (P31) — NAMĚŘENO, NE ODHADNUTO: tahle dávka
             # **přesto přepsala dokumenty**. Nová pojistka (viz níž) ukázala
             # doklad po dokladu, KDO to byl: **`p27-oprav-datum.py`** zapsal
             # `HANDOFF.md` i `KRONIKA-PROJEKTU.md` (jednorázový patcher data —
             # jeho DRUHÝ běh je vždy nová editace), a **`p30-oprav-datum.py`**
             # ho hned opravil zpět (proto se na konci tvářily jako nezměněné).
             # Je to TÁŽ TŘÍDA jako tři patchery výš — P30 ho do `PRESKIP`
             # nedala, protože viděla jen ČISTÝ VÝSLEDEK (po opravě).
             "p27-oprav-datum.py",
             # ⚠ PŘESKOČENO 9. 10. 2026 (P32) — čtyři nové soubory, každý z JINÉHO
             # důvodu (a každý s KÓDEM, ne jen se jménem):
             #  * `p32-mutace.py` je MUTAČNÍ TEST měřidla P32 a oprav H136/H140 —
             #    vrací vady do KOPIÍ a ověřuje diferenciál; dávka má POJISTKU
             #    PROTI ZÁPISU, která hash dokumentů sleduje, takže mutační test
             #    do ní nepatří (stejný důvod jako `p30-mutace.py`/`p31-mutace.py`).
             #  * `p32-test-zapis-kotvy.py` je TEST PATCHERU (H136): spouští
             #    `p27-dopln-zaznamy.py` na FIXTURÁCH přes `P27_HANDOFF`/
             #    `P27_KRONIKA` — tedy pouští patcher, kterého se dávka záměrně
             #    bojí (`p27-*` je v PRESKIP). Do dávky nepatří.
             #  * `p32-sonda-h139.py` je JEDNORÁZOVÁ DIAGNOSTIKA (odpověděla na
             #    otázku „mění mutace `REPO` verdikt brány?") — naměřila, že
             #    MĚNÍ, a že vadná byla kontrola, ne mutace (H140/H141).
             #  * `p32-a-overeni.py` dávka BERE (vzor `p3[0-9]-`) — běží v LEVNÉM
             #    režimu (~30 s, bez sítě) a vypisuje čítač pro tuhle dávku;
             #    `--plne` (p28-b-mutace, diferenciál úklidu, živé sondy) se
             #    v dávce NEPOUŽÍVÁ (rekurze a čas).
             "p32-mutace.py", "p32-test-zapis-kotvy.py", "p32-sonda-h139.py",
             #  * `p32-zapis-zaznamu.py` je ZÁPISOVÝ patcher (píše `HANDOFF.md`,
             #    `KRONIKU` a `NEXT-SESSION-INSTRUKCE.md`) — stejná třída jako
             #    `p27-*` patchery výš. V dávce se spouštět NESMÍ: dávka má
             #    POJISTKU PROTI ZÁPISU a tenhle skript jediný zapisuje ZÁMĚRNĚ.
             "p32-zapis-zaznamu.py",
             #  * `p32-prepis-zadani.py` je JEDNORÁZOVÝ PŘEPIS
             #    `NEXT-SESSION-INSTRUKCE.md` ze šablony mimo repo (hlavička musí
             #    nést commit, který vznikne až commitem). V dávce se spouštět
             #    NESMÍ: přepsal by ZADÁNÍ — a to je jeden ze čtyř dokumentů,
             #    jejichž hash pojistka dávky hlídá (H130/H138).
             "p32-prepis-zadani.py",
             #  * `p32-sonda-b3.mjs` je SONDA ŽIVÉ SLUŽBY (Úkol B3): mění stav
             #    (`POST /game/active` false/true) a volá `POST /tick`. Dávka
             #    hledá jen `*.py`, takže se jí netýká — je tady proto, aby bylo
             #    VIDĚT, že ji nikdo nemá pouštět „naslepo“ (vzor `p30-sonda-*`).
             "p32-sonda-b3.mjs",
             #  * `p32-sonda-cf-verze.mjs` je SONDA K NASAZENÍ (krok 3 ověření
             #    „server posílá nový artefakt“): stahuje LOG nasazovacího běhu
             #    (`/actions/jobs/<id>/logs`, 302 na blob storage) a vytahuje
             #    z něj `Current Version ID` / `Uploaded`. Pouští se ručně.
             "p32-sonda-cf-verze.mjs"}

# ⚠ POJISTKA PROTI ZÁPISU (P22, 6. 10. 2026) — naměřeno auditem nástrojů:
# tahle dávka spouští i skripty, které ZAPISUJÍ do dokumentů
# (`p20-oprav-kroniku.py` i `p21-zapis-kroniky.py` píšou do `KRONIKA-PROJEKTU.md`;
# `p19-b-kontroly.py` dočasně mutuje živý soubor a vrací ho).
# `validate-all.mjs` na to pojistku MÁ (`zapisuje = /write_text|write_bytes|…/`),
# tenhle skript ji NEMĚL — a běží v dávce, takže ji potřebuje víc.
# Pojistka nedělá nic záludného: (a) vytipuje zápisové skripty PŘED během,
# (b) změří hash sledovaných dokumentů PŘED a PO a rozdíl OHLÁSÍ.
# Když se dokument změní, není to automaticky vada (skripty jsou idempotentní),
# ale musí to být VIDĚT — tichá změna dokumentu dávkou je nejhorší varianta.
ZAPIS = re.compile(r"write_text|write_bytes|writeFileSync|copyfile|copy2")
SLEDOVANE = [WS / "KRONIKA-PROJEKTU.md", WS / "HANDOFF.md",
             WS / "NEXT-SESSION-INSTRUKCE.md",
             # ⚠ REGISTR BRAN (doplněno 6. 10. 2026): naměřeno, že dávka
             # **přepsala živý registr** obsahem z fixtury (`bran_celkem: 1`,
             # brána `A1: zdravá`) — nějaký harness si staví kopii `g3`
             # s vlastním `BRANY`. Běh byl „zelený“ a registr přitom **lhal**;
             # poznalo se to jen měřením obsahu. Proto se hlídá i on — a kdo
             # si staví harness, dá `FORGE_REGISTR=<scratch>` (nebo
             # `FORGE_BEZ_REGISTRU=1`), viz komentář v `g3-brany.py`.
             ANALYZA / "_registr-bran.json"]


def hash_souboru(p):
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        return None


skripty = sorted(p for p in ANALYZA.glob("*.py")
                 if VZOR.match(p.name) and p.name not in PRESKOCIT)

zapisove = sorted(p.name for p in skripty
                  if ZAPIS.search(p.read_text(encoding="utf-8", errors="replace")))
pred = {p.name: hash_souboru(p) for p in SLEDOVANE}

print("=" * 78)
print("P20/D — všechny doklady `_analyza/`: projdou ještě?")
print("=" * 78)
print(f"  skriptů: {len(skripty)}")
print(f"  ⚠ z toho ZAPISUJÍCÍCH do souborů: {len(zapisove)} — {', '.join(zapisove) or '(žádný)'}")
print(f"  hlídám změnu: {', '.join(p.name for p in SLEDOVANE)}\n")

vysledky = []
vinnici = []
po_jednom = dict(pred)
for p in skripty:
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, "-B", str(p)], capture_output=True,
                           text=True, encoding="utf-8", errors="replace",
                           cwd=str(WS), timeout=1800)
        kod = r.returncode
        v = (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        kod, v = "TIMEOUT", ""
    trvani = time.time() - t0
    m = None
    for m in re.finditer(r"VÝSLEDEK[^\n]*?(\d+) kontrol, (\d+) chyb", v):
        pass
    citac = f"{m.group(1)}/{m.group(2)}" if m else "—"
    vysledky.append((p.name, kod, trvani, citac, v))
    stav = "OK   " if kod == 0 else f"exit={kod}"
    print(f"  {stav:8} {p.name:34} {trvani:6.1f}s  kontroly: {citac}")
    # ⚠ H138 (P31): POJISTKA SE PTÁ PO KAŽDÉM DOKLADU ZVLÁŠŤ, ne jen na konci.
    # Naměřeno 9. 10. 2026: na konci se našel JEDEN změněný soubor
    # (`_registr-bran.json`) a **nebylo vidět, který doklad ho zapsal** — muselo
    # se to dohledávat ručně. Kdo ho změnil, se teď VYPÍŠE.
    po_tomto = {q.name: hash_souboru(q) for q in SLEDOVANE}
    zmenil = [n for n in po_jednom if po_jednom[n] != po_tomto[n]]
    if zmenil:
        vinnici.append((p.name, zmenil))
        print(f"           ⚠ ZAPSAL DO DOKUMENTU: {', '.join(zmenil)}")
    po_jednom = po_tomto

selhale = [x for x in vysledky if x[1] != 0]
po = {p.name: hash_souboru(p) for p in SLEDOVANE}
zmenene = [n for n in pred if pred[n] != po[n]]

print("\n" + "=" * 78)
print(f"SOUHRN: {len(vysledky)} dokladů, {len(selhale)} s nenulovým exit")
print("=" * 78)
print("\nZÁPIS DO DOKUMENTŮ (pojistka, P22):")
if vinnici:
    print("  KDO ZAPSAL (po každém dokladu):")
    for jmeno, co in vinnici:
        print(f"    {jmeno:34} → {', '.join(co)}")
if zmenene:
    for n in zmenene:
        print(f"  ⚠ ZMĚNĚN: {n}  ({pred[n][:12] if pred[n] else '—'} → {po[n][:12] if po[n] else '—'})")
    print("  → dávka dokladů zapsala do dokumentu; ověř, že je to zamýšlené (skripty jsou idempotentní)")
else:
    print(f"  žádný z {len(SLEDOVANE)} sledovaných dokumentů se nezměnil")
    print(f"  (zápisové skripty ve dávce: {len(zapisove)} — {', '.join(zapisove) or 'žádný'})")

for jmeno, kod, trvani, citac, v in selhale:
    print(f"\n--- {jmeno}  (exit={kod}) ---")
    chyby = [l.strip() for l in v.splitlines() if "CHYBA" in l]
    for l in chyby[:8]:
        print(f"    {l[:160]}")
    if not chyby:
        for l in [x for x in v.splitlines() if x.strip()][-6:]:
            print(f"    | {l[:160]}")

sys.exit(1 if selhale else 0)
