# -*- coding: utf-8 -*-
r"""MUTAČNÍ TEST: měří novou část `tools\over-skilly.py` (cesty v DELEGOVANÝCH
dokumentech, přidáno 7. 10. 2026 při optimalizaci KB) **a nový TVAR cest
(P28/B5, 8. 10. 2026)** a **ZÁZNAM MINULÉHO STAVU (H217, K10, 16. 10. 2026)**.

PROČ TENHLE TEST EXISTUJE: skilly `orchestra` a `game-developer` přesunuly část
znalosti do projektových dokumentů (`PROVOZ-ORCHESTRA.md`, `BRANY-HRY.md`).
Kontrola cest k nástrojům se rozšířila i na ně — ale **nová kontrola je stejně
bezcenná jako každá jiná, dokud se neprokáže, že UMÍ SPADNOUT**. Naměřeno
7. 10. 2026: první pokus o tuhle mutaci se **tiše neprovedl** (PowerShell
spolkl backticky v here-stringu), takže test „prošel" a netvrdil nic.

⚠ TEST NESAHÁ NA ŽIVÉ DOKUMENTY. Používá přepis `FORGE_NAVAZANE` a fixtury
v `_analyza\_scratch-over-skilly\` (uklízí je v `finally`). Důvod je naměřený
(P24): přerušený mutační běh nad živým souborem nechal v kódu čtyři mutanty
a `git status` přitom byl čistý.

Použití: python _analyza\test-over-skilly-delegovane.py
"""

import os
import pathlib
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
SCRATCH = WS / "_analyza" / "_scratch-over-skilly"
BRANA = WS / "tools" / "over-skilly.py"
sys.path.insert(0, str(WS / "_analyza"))
from _mutace import mutuj  # noqa: E402

kontrol = 0
chyb = 0


def test(popis, ok, detail=""):
    global kontrol, chyb
    kontrol += 1
    if ok:
        print(f"  OK   {popis}")
    else:
        chyb += 1
        print(f"  CHYBA {popis}{(' — ' + detail) if detail else ''}")


def spust_nad(fixtury, skills=None):
    """Spustí bránu s DELEGOVANÝMI dokumenty = fixturami. Vrací (exit, výstup).

    ⚠ `FORGE_SKILLS` míří na PRÁZDNÝ adresář: tenhle test měří část o
    delegovaných dokumentech, ne stav cizích skillů. Naměřeno 8. 10. 2026 (P27):
    nový skill `dialog-s-uzivatelem` (cizí session) měl neplatný YAML a test
    kvůli němu hlásil „zdravá fixtura → exit 1" — tedy vadu, která s jeho věcí
    nesouvisela. Falešný poplach se hledá hůř než slepé místo.
    ⚠ P28/B5: `skills` umí PŘEPIS (fixtury skillů pro měření deklarovaných výjimek).
    """
    env = dict(os.environ)
    env["FORGE_NAVAZANE"] = ";".join(str(p) for p in fixtury)
    env["FORGE_SKILLS"] = str(skills or (SCRATCH / "prazdne-skilly"))
    (SCRATCH / "prazdne-skilly").mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, str(BRANA)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(WS), env=env, timeout=300)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


try:
    SCRATCH.mkdir(parents=True, exist_ok=True)

    # ── Fixtura 1: cesta, která EXISTUJE (`tools\status.mjs`) ────────────────
    f_ok = SCRATCH / "fixtura-ok.md"
    f_ok.write_text("Odkaz na `tools\\status.mjs` a `_analyza\\g3-brany.py`.\n",
                    encoding="utf-8", newline="\n")

    # ── Fixtura 2: cesta, která NEEXISTUJE ───────────────────────────────────
    # ⚠ Řádek NESMÍ obsahovat slovo „neexistuje" ani „~~" — brána je bere jako
    # přiznanou historickou zmínku a správně by takovou cestu přeskočila.
    f_spatna = SCRATCH / "fixtura-mrtva-cesta.md"
    f_spatna.write_text("Odkaz na `tools\\mrtvy-nastroj-abc.py`.\n",
                        encoding="utf-8", newline="\n")

    # ── Fixtura 3: přiznaná historická zmínka (NESMÍ spadnout) ───────────────
    f_hist = SCRATCH / "fixtura-historie.md"
    f_hist.write_text(
        "Nástroj `tools\\stary-nastroj-abc.py` už není (smazán 1. 10. 2026).\n",
        encoding="utf-8", newline="\n")

    print("=" * 78)
    print("TEST: cesty v delegovaných dokumentech (over-skilly.py)")
    print("=" * 78)

    # 1) zdravý stav → zelená
    kod, out = spust_nad([f_ok])
    test("zdravá fixtura → exit 0", kod == 0, f"exit={kod}")
    test("zdravá fixtura → počítadlo cest roste (a 0 mrtvých)",
         "zmínek" in out and "0 mrtvých" in out)

    # 2) mrtvá cesta → ČERVENÁ (tohle je jádro testu)
    kod, out = spust_nad([f_spatna])
    test("mrtvá cesta ve fixtuře → exit 1", kod == 1, f"exit={kod}")
    test("mrtvá cesta je POJMENOVANÁ (ne jen nenulový exit)",
         "mrtvy-nastroj-abc.py" in out, out[-200:])

    # 3) přiznaná historická zmínka → zelená (brána nesmí hlásit falešný poplach)
    kod, out = spust_nad([f_hist])
    test("historická zmínka („už není, smazán“) → exit 0", kod == 0, f"exit={kod}")

    # 4) delegovaný dokument, který NEEXISTUJE → ČERVENÁ
    #    (skill by posílal agenta nikam a dosud si toho nikdo nevšiml)
    kod, out = spust_nad([SCRATCH / "dokument-ktery-neni.md"])
    test("neexistující delegovaný dokument → exit 1", kod == 1, f"exit={kod}")

    # 5) REGRESNÍ POJISTKA: s přepisem se ŽIVÉ dokumenty neskenují.
    #    Kdyby se skenovaly, test by mohl mutovat živý text — což je přesně
    #    past, kterou popisuje P24.
    zivy = WS / "PROVOZ-ORCHESTRA.md"
    pred = zivy.read_bytes() if zivy.exists() else b""
    spust_nad([f_ok])
    po = zivy.read_bytes() if zivy.exists() else b""
    test("živý PROVOZ-ORCHESTRA.md test nemění (bajt na bajt)", pred == po)

    # 6) Sabotáž SAMOTNÉHO PŘEPISU: bez `FORGE_NAVAZANE` se musí skenovat živé
    #    dokumenty — kdyby override „prosakoval" i bez proměnné, kontrola by
    #    mlčela o skutečných dokumentech.
    env = dict(os.environ)
    env.pop("FORGE_NAVAZANE", None)
    r = subprocess.run([sys.executable, str(BRANA)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(WS), env=env, timeout=300)
    vystup = (r.stdout or "") + (r.stderr or "")
    test("bez přepisu se skenují ŽIVÉ dokumenty (PROVOZ i BRANY-HRY)",
         "PROVOZ-ORCHESTRA.md" in vystup and "BRANY-HRY.md" in vystup,
         vystup[-200:])

    # ── 7) P28/B5: TVAR CEST, KTERÝ BRÁNA DO 8. 10. 2026 NEVIDĚLA ───────────
    # Nález §51.3: brána hledala cestu POUZE hned za backtickem — naměřeno
    # sondou `_analyza/p28-sonda-cesty.py`: v dokumentech je 90 zmínek a brána
    # jich viděla 71. „0 mrtvých cest" proto NEBYLO důkaz. Následující fixtury
    # měří, že nový tvar (``` blok, příkaz za `python `) brána SKUTEČNĚ vidí.
    f_blok = SCRATCH / "fixtura-code-blok.md"
    f_blok.write_text("```\npython tools\\mrtvy-nastroj-blok.py\n```\n",
                      encoding="utf-8", newline="\n")
    kod, out = spust_nad([f_blok])
    test("mrtvá cesta v ``` bloku → exit 1 (dřív ji brána NEVIDĚLA)",
         kod == 1, f"exit={kod}")
    test("a je POJMENOVANÁ (ne jen nenulový exit)",
         "mrtvy-nastroj-blok.py" in out, out[-200:])

    f_prikaz = SCRATCH / "fixtura-prikaz.md"
    f_prikaz.write_text("Spusť `python _analyza\\mrtvy-nastroj-prikaz.py`.\n",
                        encoding="utf-8", newline="\n")
    kod, out = spust_nad([f_prikaz])
    test("mrtvá cesta za `python ` v backticích → exit 1", kod == 1, f"exit={kod}")
    test("a je pojmenovaná", "mrtvy-nastroj-prikaz.py" in out, out[-200:])

    f_zdrava = SCRATCH / "fixtura-blok-zdrava.md"
    f_zdrava.write_text("```\nnode tools\\validate-all.mjs\n```\n",
                        encoding="utf-8", newline="\n")
    kod, out = spust_nad([f_zdrava])
    test("ZDRAVÁ cesta v ``` bloku → exit 0 (žádný falešný poplach)",
         kod == 0, f"exit={kod}")

    f_vzor = SCRATCH / "fixtura-vzor.md"
    f_vzor.write_text("```\ntools/blender/sprites/body_d0_f*.png\n```\n",
                      encoding="utf-8", newline="\n")
    kod, out = spust_nad([f_vzor])
    test("VZOR se zástupným znakem (`*`) není cesta → exit 0", kod == 0, f"exit={kod}")

    # ── 8) DEKLAROVANÁ VÝJIMKA PLATÍ JEN PRO DEKLAROVANÝ SKILL ──────────────
    # `vision` učí postup pro projekt s vlastním `.python` — jeho cesty na téhle
    # stanici nejsou a být nemusí (je to ŠABLONA). Výjimka je klíčovaná dvojicí
    # (skill, cesta); táž cesta v JINÉM skillu musí bránu shodit (jinak by se
    # z výjimky stalo tiché vypnutí kontroly).
    def fixtura_skillu(koren, jmeno):
        (koren / jmeno).mkdir(parents=True, exist_ok=True)
        (koren / jmeno / "SKILL.md").write_text(
            "---\nname: %s\ndescription: fixtura pro test výjimky\n---\n\n"
            "Postup pro projekt s vlastním pythonem: `tools\\vision.py`.\n" % jmeno,
            encoding="utf-8", newline="\n")
        return koren

    s_vision = fixtura_skillu(SCRATCH / "fixtura-skilly-vision", "vision")
    kod, out = spust_nad([f_ok], skills=s_vision)
    test("deklarovaná výjimka (skill `vision` + `tools\\vision.py`) → exit 0",
         kod == 0, f"exit={kod} — {out[-160:]}")

    s_jiny = fixtura_skillu(SCRATCH / "fixtura-skilly-jiny", "jiny-skill")
    kod, out = spust_nad([f_ok], skills=s_jiny)
    test("TÁŽ cesta v JINÉM skillu → exit 1 (výjimka neprosakuje)",
         kod == 1, f"exit={kod}")
    test("a je pojmenovaná", "vision.py" in out, out[-200:])

    # ── 9) H217 (K10, 16. 10. 2026): ZÁZNAM MINULÉHO STAVU NENÍ ŽIVÝ ODKAZ ───
    # Naměřeno: dokument HRY `docs/BRANY-HRY.md:133` popisuje větou v MINULÉM
    # čase, že „v repu ležela rekurzivní kopie repa (`_analyza/_selftest-copy/`,
    # 11 416 souborů) a brána spadla“. Cesta dnes existovat NEMÁ — a brána ji
    # brala jako živý odkaz (1. NEDEKLAROVANÝ nenulový exit `g3`). Táž třída
    # jako H24: brána měřila ZÁZNAM místo živého tvrzení.
    print()
    print("--- 9) H217: záznam v minulém čase vs ŽIVÝ mrtvý odkaz ---------------")
    # 9a) záznam na JEDNOM řádku (takhle to vyšlo v dokumentu hry)
    f_h217a = SCRATCH / "fixtura-h217-jeden-radek.md"
    f_h217a.write_text(
        "Naměřeno 15. 10. 2026: když v repu ležela rekurzivní kopie repa "
        "(`_analyza/_selftest-copy/`, 11 416 souborů), brána spadla.\n",
        encoding="utf-8", newline="\n")
    kod, out = spust_nad([f_h217a])
    test("9a záznam v minulém čase („ležela“ na témž řádku) → exit 0",
         kod == 0, f"exit={kod} — {out[-160:]}")

    # 9b) ZALÁMANÁ VĚTA: dokumenty jsou zalámané na ~78 znaků, takže slovo
    #     o minulosti běžně zůstane na PŘEDCHOZÍM řádku. Naměřeno vlastní
    #     kalibrací (poprvé to brána shodila) — proto je okno 2 řádky.
    f_h217b = SCRATCH / "fixtura-h217-zalamane.md"
    f_h217b.write_text(
        "**Naměřeno 15. 10. 2026:** když v repu **ležela** rekurzivní kopie repa\n"
        "(`_analyza/_selftest-copy/`, **11 416 souborů / 240 složek**), brána spadla.\n",
        encoding="utf-8", newline="\n")
    kod, out = spust_nad([f_h217b])
    test("9b zalámaná věta (slovo o minulosti na PŘEDCHOZÍM řádku) → exit 0",
         kod == 0, f"exit={kod} — {out[-160:]}")

    # 9c) OHRANIČENOST OKNA: záznam o tři řádky výš už cestu krýt NESMÍ. Jedna
    #     fixtura měří OBĚ strany: řádek 1 je záznam (přeskočí se), řádek 4 je
    #     živý mrtvý odkaz (musí spadnout) — jinak by z pravidla bylo ticho.
    f_h217c = SCRATCH / "fixtura-h217-okno.md"
    f_h217c.write_text(
        "Záznam: v repu ležela kopie (`_analyza/_selftest-copy/`).\n"
        "\n"
        "\n"
        "Živý odkaz na `tools\\mrtvy-nastroj-h217.py`.\n",
        encoding="utf-8", newline="\n")
    kod, out = spust_nad([f_h217c])
    test("9c záznam na ř. 1 NEKRÝVÁ cestu na ř. 4 (okno je OHRANIČENÉ) → exit 1",
         kod == 1, f"exit={kod}")
    test("9c a nález jmenuje ŽIVOU cestu (ne tu z záznamu)",
         "mrtvy-nastroj-h217.py" in out and "_selftest-copy" not in out,
         out[-240:])

    # ── 9b) MUTAČNÍ DŮKAZ: seznam `ZAZNAM_MINULOSTI` je NOSNÝ ──────────────
    # Kdyby seznam „spolkl“ všechno (`.*`), brána by oslepla — mrtvá cesta bez
    # slova o minulosti by prošla jako zelená. Test to musí VIDĚT: pod mutací
    # se verdikt změní z `exit 1` na `exit 0`. (Kdyby se nezměnil, znamenalo by
    # to, že seznam nic neřídí a kalibrace měří jinou věc, než si myslí.)
    print()
    print("--- 9b) sabotáž: seznam záznamu = '.*' musí bránu OSLEPIT ------------")
    kotva = r'|ležel\w*|existoval\w*|býval\w*")'
    try:
        with mutuj(BRANA, kotva, r'|ležel\w*|.*")') as m:
            kod_slep, out_slep = spust_nad([f_spatna])
    except ValueError as e:
        test("mutace seznamu záznamu se PROVEDLA", False, str(e)[:120])
    else:
        test("bez slova o minulosti pod sabotáží brána OSLNE (exit 0)",
             kod_slep == 0, f"exit={kod_slep}")
        test("soubor brány vracen bajt na bajt",
             m.hash_po_navratu == m.hash_pred, f"sha256 {m.hash_po_navratu[:16]}")

    # a po vrácení musí být brána znovu PŘESNÁ (ne „slepá zůstala“)
    kod, out = spust_nad([f_spatna])
    test("po vrácení mutace je brána znovu PŘESNÁ (mrtvá cesta → exit 1)",
         kod == 1, f"exit={kod}")

finally:
    shutil.rmtree(SCRATCH, ignore_errors=True)

print()
print(f"Kontrol: {kontrol}, chyb: {chyb}")
print("VŠE OK" if chyb == 0 else "NALEZENY CHYBY")
sys.exit(0 if chyb == 0 else 1)
