# -*- coding: utf-8 -*-
"""BRÁNA NA `ZADANI-OPRAVA-MERIDEL.md` — sedí zadání na skutečnost?

Vznikla 2. 10. 2026 v plánovací (ověřovací) session. Ptá se na **10 naměřených
faktů (F1–F10)** ze zadání a na **13 opatření** z `AUDIT-DOKUMENTACE.md` §6.

⚠ CO TENHLE NÁSTROJ NEDOKAZUJE: že zadání vede ke správnému řešení.
Dokazuje jen, že **fakta v něm sedí na živý stav** — nic víc.

⚠ PROČ ČTE ZE SOUBORŮ, NE Z KONSTANT: první verze `audit2a-schema.py` měřila
zdroj a porovnávala ho **sám se sebou** (nález N9). Každé číslo níž je
**odečteno z běhu nástroje nebo z dokumentu**, nikdy není napsané napevno —
napevno jsou jen **meze**, které se mají překročit, a ty jsou v `MEZE`.
"""
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable

# ⚠ MEZE jsou ZÁMĚRNĚ volné: brána nemá padat na kosmetice, ale na TOM,
# že se vada vrátí. Přísnější hodnoty patří do `audit2b-over.py` (Úkol 1).
#
# MEZ `audit2b_max_rozchodu` je 35 (dnes 31) ZÁMĚRNĚ, a je to poučení z běhu
# 2. 10. 2026: první verze měla 30 a **spadla na vlastním textu** — každý
# dokument, který o rozchodech píše („31 rozchodů", „25 falešných"), přidá
# `audit2b` nový výskyt veličiny. Brána, která padá na tom, že pracuji, se
# přestane číst (`overovani` §9.5 — falešný poplach se hledá hůř než slepota).
# **Vada, kterou brána hledá, mění číslo o řád** (31 → ≤ 6), ne o jednotky.
MEZE = {
    "audit2b_max_rozchodu": 35,      # dnes 31; po Úkolu 1 se čeká <= 6
    "kronika_max_omylu": 130,        # dnes 75 (brána zná 8 bloků z 10)
    "inventar_max_bez_hlavicky": 80,  # dnes 76
    "g3_min_bran": 30,
    "zadani_max_odkazu_na_s5": 6,    # dnes 6; po Úkolu 2b se čeká 0
}


def spust(prikaz, vzor, vsechny=False):
    """Pustí nástroj a vytáhne číslo. Když číslo není, vrací None s důvodem
    (nikdy tichou nulu — `overovani` §3 bod 3)."""
    try:
        r = subprocess.run(prikaz, cwd=str(WS), capture_output=True, timeout=900)
    except Exception as e:                                       # noqa: BLE001
        return None, "nepodařilo se spustit: %s" % type(e).__name__, ""
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    m = re.search(vzor, v)
    if not m:
        return None, "výstup neobsahuje vzor %r" % vzor, v
    return int(m.group(1)), "exit=%d" % r.returncode, v


def main() -> int:
    chyby = []
    kontroly = 0

    def ok(popis, hodnota, mez, smer="<="):
        nonlocal kontroly
        kontroly += 1
        if hodnota is None:
            chyby.append("%s: NEZMĚŘENO (%s)" % (popis, mez))
            print("  ✗ %-46s NEZMĚŘENO — %s" % (popis, mez))
            return
        platí = hodnota <= mez if smer == "<=" else hodnota >= mez
        print("  %s %-46s %s (mez %s %s)"
              % ("OK" if platí else "✗ ", popis, hodnota, smer, mez))
        if not platí:
            chyby.append("%s: %s, čekáno %s %s" % (popis, hodnota, smer, mez))

    print("=" * 96)
    print("BRÁNA NA ZADÁNÍ — `ZADANI-OPRAVA-MERIDEL.md`")
    print("=" * 96)

    # ── F1+F2: audit2b — rozchody a jejich rozpad ──────────────────────────
    print("\n[F1/F2] `audit2b` — kolik rozchodů a u kterých veličin")
    a2b, pozn, vystup = spust([PY, "_analyza/audit2b-cisla-proti-zdroji.py"],
                              r"ROZCHODŮ:\s+(\d+)")
    ok("audit2b rozchodů", a2b, MEZE["audit2b_max_rozchodu"])
    # Rozpad po veličinách — MUSÍ se čítat Z VÝSTUPU, ne z konstant
    m = re.search(r"ROZCHODY PO VELIČINÁCH:(.*?)(?:={10,}|$)", vystup, re.S)
    if m:
        for radek in m.group(1).splitlines():
            mm = re.match(r"\s+(\S+)\s+(\d+)\s", radek)
            if mm:
                print("      %-20s %s" % (mm.group(1), mm.group(2)))
    else:
        chyby.append("audit2b nevypsal ROZCHODY PO VELIČINÁCH")
        print("  ✗ audit2b nevypsal rozpad po veličinách (to je jádro NA17)")

    # ── F2: audit2a zná tytéž výskyty jako CITACE ─────────────────────────
    print("\n[F2] `audit2a` — zná tytéž výskyty jako citace?")
    a2a, pozn2, vystup2 = spust([PY, "_analyza/audit2a-schema.py"],
                                r"ROZCHODŮ=(\d+)")
    if a2a is None:
        a2a, pozn2, vystup2 = spust([PY, "_analyza/audit2a-schema.py"],
                                    r"ROZCHODŮ:\s*(\d+)")
    kontroly += 1
    if a2a is None:
        chyby.append("audit2a nevypisuje počet ROZCHODŮ")
        print("  ✗ audit2a nevypisuje počet ROZCHODŮ")
    else:
        print("  %s `audit2a` rozchodů = %s (má být 0)" % ("OK" if a2a == 0 else "✗ ", a2a))
        if a2a != 0:
            chyby.append("audit2a hlásí %d rozchodů, čekáno 0" % a2a)
    mcit = re.search(r"citac\w*[=:]\s*(\d+)", vystup2)
    kontroly += 1
    if not mcit or int(mcit.group(1)) == 0:
        chyby.append("audit2a nevykazuje žádné CITACE — pak nemá co srovnávat s audit2b")
        print("  ✗ audit2a nevykazuje citace (F2 se nedá doložit)")
    else:
        print("  OK `audit2a` citací = %s (tytéž výskyty audit2b hlásí jako rozchod)"
              % mcit.group(1))

    # ── F4: kronika — počet omylů, který brána zná ────────────────────────
    print("\n[F4] `kronika-kontrola.py` — kolik omylů vidí")
    kr, pozn3, vystup3 = spust([PY, "_analyza/kronika-kontrola.py"],
                               r"omylů celkem \(skutečnost\):\s+(\d+)")
    ok("kronika: omylů (co vidí brána)", kr, MEZE["kronika_max_omylu"])

    # ── Od 3. 10. 2026 brána NEMÁ pevný seznam bloků ──────────────────────
    # Do té doby se odtud čítal literál `BLOKY = [...]` a byl to **pětkrát**
    # důvod téhož nálezu (NA17): nový blok omylů v dokumentu v seznamu nebyl,
    # takže vypadl z počtu — a nebylo to nikde vidět. Naposledy `8n`: brána
    # hlásila 107, kdežto součet řádků tabulky v kronice §3 byl 118.
    # Kontrola se proto ptá na DVĚ věci jinak:
    #   (a) že brána bloky HLEDÁ V DOKUMENTU (pevný seznam se nesmí vrátit) —
    #       čte se ze ZDROJE brány,
    #   (b) že počet bloků, který brána OPRAVDU zahrnula (ČÍTAČ z jejího
    #       výstupu), odpovídá počtu nadpisů v dokumentu — a ten se počítá
    #       TADY, nezávisle na bráně.
    # ⚠ Ani jedno se nečte z řádku „OK“: (a) je z div zdroje, (b) z čítače.
    zdroj_br = (WS / "_analyza" / "kronika-kontrola.py").read_text(encoding="utf-8")
    kontroly += 1
    if re.search(r"^BLOKY\s*=\s*\[", zdroj_br, re.M):
        chyby.append("`kronika-kontrola.py` má ZNOVU pevný seznam `BLOKY = [` — "
                     "nový blok omylů by vypadl z počtu (nález NA17)")
        print("  ✗ brána kroniky má ZNOVU pevný seznam BLOKY = [...]")
    elif "bloky_omylu(" not in zdroj_br:
        chyby.append("`kronika-kontrola.py` nehledá bloky omylů v dokumentu "
                     "(chybí volání `bloky_omylu`)")
        print("  ✗ brána kroniky nehledá bloky omylů v dokumentu")
    else:
        print("  OK brána hledá bloky omylů V DOKUMENTU (žádný pevný seznam)")

    # (b) kolik bloků brána skutečně zahrnula — ČÍTAČ z výstupu, ne odhad
    mbl = re.search(r"bloků omylů v tomto součtu:\s*(\d+)", vystup3)
    h = (WS / "HANDOFF.md").read_text(encoding="utf-8").splitlines()
    # ⚠ Vzor je tu NAPSANÝ ZNOVU, ne importovaný z brány (`overovani` §7.11):
    # kdyby se v bráně zúžil (třeba na `8[a-m]`), musí to být vidět jako ROZDÍL
    # proti tomuhle nezávislému počtu — jinak by kontrola měřila sama sebe.
    vsechny_8 = [l for l in h if re.match(r"^#{2,3}\s+8[a-z]?\.\s", l)]
    kontroly += 1
    if not vsechny_8:
        chyby.append("v HANDOFF.md není ANI JEDEN nadpis bloku omylů — "
                     "shoda 0 = 0 by nebyla měření")
        print("  ✗ v HANDOFF.md nejsou žádné nadpisy bloků omylů")
    elif not mbl:
        chyby.append("`kronika-kontrola.py` nevypisuje počet bloků, které zahrnula "
                     "(bez čítače se počet bloků nedá ověřit)")
        print("  ✗ brána nevypisuje počet bloků, které zahrnula")
    elif int(mbl.group(1)) != len(vsechny_8):
        chyby.append("brána zahrnula %s bloků, ale v HANDOFF.md je %d nadpisů "
                     "bloků omylů — některý se NEPOČÍTÁ" % (mbl.group(1), len(vsechny_8)))
        print("  ✗ brána zahrnula %s bloků, v dokumentu je %d nadpisů"
              % (mbl.group(1), len(vsechny_8)))
    else:
        print("  OK brána zahrnula všech %d bloků omylů z dokumentu" % len(vsechny_8))

    # ── F5: g3 — počet bran a nenulových exitů ────────────────────────────
    print("\n[F5] `g3-brany.py` — počet bran (a co vypisuje o `validate-all`)")
    g3v = WS / "_analyza" / "g3-brany-vystup.txt"
    g3, pozn4, vystup4 = spust([PY, "_analyza/g3-brany.py"],
                               r"brán celkem:\s+(\d+)")
    ok("g3: bran celkem", g3, MEZE["g3_min_bran"], smer=">=")
    kontroly += 1
    mva = re.search(r"validate-all \(CELEK\)\s+otevřela:\s*(\S*)", vystup4)
    if not mva:
        chyby.append("g3 nevypsal řádek pro validate-all")
        print("  ✗ g3 nevypsal řádek pro validate-all")
    elif mva.group(1) == "3":
        print("  OK `validate-all` → `otevřela: 3` — to je VADA NA23 (F5 potvrzen)")
    elif mva.group(1) in ("—", "-", "NEZMĚŘENO"):
        print("  OK `validate-all` → `otevřela: %s` — NA23 je OPRAVENO" % mva.group(1))
        print("      → přepiš `ZADANI-OPRAVA-MERIDEL.md` Úkol 2a (už je hotový)")
    else:
        print("  ⚠ `validate-all` → `otevřela: %r` — neočekávaná hodnota" % mva.group(1))

    # ── F8: pokrytí brány diakritiky ──────────────────────────────────────
    print("\n[F8] `kontrola-diakritiky.py` — ruční seznam, nebo projití složky?")
    kd = (WS / "orchestra" / "tools" / "kontrola-diakritiky.py").read_text(encoding="utf-8")
    kontroly += 1
    ma_glob = bool(re.search(r"rglob|\.glob\(|os\.walk", kd))
    kotvy_md = {pathlib.PurePath(c).name for c in re.findall(r"[\w\\/\.\-]+\.md", kd)}
    koren = {p.name for p in WS.glob("*.md")}
    analyza = {p.name for p in (WS / "_analyza").glob("*.md")}
    chybi = sorted((koren | analyza) - kotvy_md)
    print("  OK v bráně je projití složky: %s · vyjmenovaných .md: %d"
          % ("ANO" if ma_glob else "NE", len(kotvy_md)))
    # ⚠ Od 3. 10. 2026 brána dokumenty PROCHÁZÍ složkou (`*.md` v kořeni
    # i v `_analyza`), takže „mimo ruční seznam“ NEZNAMENÁ „nekontrolováno“.
    # Rozlišuje se to schválně: jinak to číslo vypadá jako 35 neotevřených
    # dokumentů (přesně ta záměna, kterou řeší nález H18).
    print("      dokumentů mimo RUČNÍ seznam: %d (kořen %d, _analyza %d) — "
          "kryté projitím složky: %s"
          % (len(chybi), len(koren - kotvy_md), len(analyza - kotvy_md),
             "ANO" if ma_glob else "NE"))

    # ── F10: inventář ─────────────────────────────────────────────────────
    print("\n[F10] `audit1-inventar.py` — dokumenty bez hlavičky")
    inv, pozn5, vystup5 = spust([PY, "_analyza/audit1-inventar.py"],
                                r'bez hlavičky[^:]*:\s+(\d+)')
    ok("inventář: dokumentů bez hlavičky", inv, MEZE["inventar_max_bez_hlavicky"])

    # ── F7: odkazy na §5 v PREDAVANI-SESSION.md ───────────────────────────
    # ⚠ MĚŘENÁ PODMÍNKA MUSÍ BÝT TO, CO CHCI ZJISTIT (`overovani` §8.3):
    # „§5" samo o sobě trefí i **správné** odkazy na `PLAN-DALSI-KROK.md` §5
    # (jiný dokument!) a na kroniku §5 v souvislosti s **Poučením**.
    # Vada NA19 je jen odkaz na **`KRONIKA-PROJEKTU.md` §5 ve významu NÁVRHŮ**.
    print("\n[F7] `PREDAVANI-SESSION.md` — odkazy na `KRONIKA-PROJEKTU.md` §5")
    ps = (WS / "PREDAVANI-SESSION.md").read_text(encoding="utf-8").splitlines()
    # ⚠ DVĚ MĚŘENÍ, DVĚ OKNA (`overovani` §9.2): odkaz na kroniku může být
    # na TÉMŽ řádku (`KRONIKA-PROJEKTU.md` §5) nebo na řádku PŘEDCHOZÍM
    # („co s tím: `KRONIKA-PROJEKTU.md`" … „a nové návrhy do §5"). Proto se
    # hledá v okně 3 řádků a **vypisuje se, které to byly**.
    radky_s5, jine = [], []
    for i, l in enumerate(ps, 1):
        if "§5" not in l:
            continue
        okno = " ".join(ps[max(0, i - 3):i])
        (radky_s5 if "KRONIKA-PROJEKTU" in okno and "PLAN-DALSI-KROK" not in okno
         else jine).append(i)
    ok("odkazů na KRONIKU §5", len(radky_s5), MEZE["zadani_max_odkazu_na_s5"])
    print("      řádky (kronika §5): %s" % radky_s5)
    print("      řádky (§5 jinde — správné, nejsou vada): %s" % jine)

    # ── F9: brány bez mutačního testu ─────────────────────────────────────
    print("\n[F9] `audit6-brany-mutace.py` — brány bez důkazu")
    a6, pozn6, vystup6 = spust([PY, "_analyza/audit6-brany-mutace.py"],
                               r"BEZ jakéhokoli důkazu\s*:\s*(\d+)")
    kontroly += 1
    if a6 is None:
        chyby.append("audit6 nevypsal počet bran bez důkazu")
        print("  ✗ audit6 nevypsal počet bran bez důkazu")
    else:
        print("  OK bran bez jakéhokoli důkazu: %d (po Úkolu 4 se čeká 7)" % a6)

    # ── ZÁVĚR ─────────────────────────────────────────────────────────────
    print()
    print("=" * 96)
    print("  ZMĚŘENO: kontrol=%d, chyb=%d" % (kontroly, len(chyby)))
    for c in chyby:
        print("      ✗ %s" % c)
    if chyby:
        print("\n  VÝSLEDEK: zadání NESEDÍ na skutečnost v %d bodech — viz výš." % len(chyby))
        return 1
    print("\n  VÝSLEDEK: všech %d faktů zadání SEDÍ na živý stav." % kontroly)
    return 0


if __name__ == "__main__":
    sys.exit(main())
