# -*- coding: utf-8 -*-
r"""P30 — MUTAČNÍ DŮKAZ, ŽE MĚŘIDLO `p30-a-overeni.py` MĚŘÍ.

CO DOKAZUJE (a proč to nestačí tvrdit):
  Měření, které nikdy nespadne, není měření. Tenhle test vrací vady do TOHO,
  CO MĚŘIDLO HLÍDÁ, a ověřuje, že se **verdikt změní**:

  * **M1 — dokument:** číslo tvrzení v `HANDOFF.md` §60 se změní (`215/0` →
    `216/0`). Kdyby měřidlo číslo NEPŘEČETLO z dokumentu (mělo ho napsané
    v sobě), mutace by neprošla — to je přesně nález **N9**.
  * **M2 — zdroj brány:** `tools/over-skilly.py` začne hlásit o jednu zmínku
    víc. Kdyby měřidlo čítač jen neopisovalo z dokumentu, ale také ho neměřilo,
    mutace by neprošla.

KAŽDÁ MUTACE MÁ TŘI NOHY (aby se „spadlo" nedalo splést s něčím jiným):
  1. **zdravý stav** → měřidlo `exit 0`
  2. **mutant** → měřidlo `exit 1` a spadlá kontrola JMENUJE mutovanou věc
  3. **mutant + oslabené měřidlo** (kopie bez porovnání) → `exit 0`
     ⇒ červená pocházela z TOHO porovnání, ne odjinud

Soubor se vrací **bajt na bajt** — hlídá to `_analyza/_mutace.py`.

Použití: python _analyza\p30-mutace.py
"""

import os
import pathlib
import re
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _mutace import mutuj  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
HANDOFF = WS / "HANDOFF.md"
BRANA = WS / "tools" / "over-skilly.py"
MERIDLO = WS / "_analyza" / "p30-a-overeni.py"
SCRATCH = WS / "_analyza" / "tick-scratch"
OSLABENE = SCRATCH / "p30-oslabene.py"
DOKLAD = WS / "_analyza" / "p30-mutace-vystup.txt"

# ⚠ Kotvy jsou Z MĚŘENÉHO ODDÍLU (§60) a MUSÍ být v souboru právě 1×.
#    215/0 se v HANDOFF.md vyskytuje 4× — proto je kotva delší.
# ⚠ P32 (H145): ANI „delší" kotva nestačila. P31 do svého záznamu **§62 CITOVALA**
#    přesně `test-tick-offline → 215/0` — takže kotva byla v dokumentu **2×**
#    a `mutuj` spadl na `ValueError: kotva je v souboru 2×`. Tím měřidlo přišlo
#    o CELÝ diferenciál (exit 1, žádný čítač) — a to je TÁŽ past jako **H131**,
#    jen na kotvě DOKUMENTU místo kotvy v kódu: **záznam, který tvrzení cituje,
#    rozbije měřidlo vázané na jediný výskyt v CELÉM dokumentu.**
#    Kotva proto nese i okolní text z §60 (nikdo ho needituje — §60 je záznam)
#    a P0 navíc ověřuje, že leží uvnitř MĚŘENÉHO oddílu.
KOTVA_DOK = "test-tick-offline → 215/0 (bylo 205/0) · tick-mutace → 20 vrat, 41/0"
KOTVA_DOK_NOVA = KOTVA_DOK.replace("215/0", "216/0")
KOTVA_BRANY = "{vsech_cest} zmínek, {mrtvych} mrtvých"
# ⚠ Sabotuje se KONTRAKT („0 mrtvých cest“), ne počet zmínek: ten je STAV
# (mění ho každá editace skillu) a měřidlo ho hlásí jako ROZDÍL, ne CHYBU.
KOTVA_BRANY_NOVA = "{vsech_cest} zmínek, {mrtvych + 1} mrtvých"
RADEK_ROZCHOD = 'm.ok_(False, f"A3 {jmeno}: ROZCHOD — dokument {cit} vs naměřeno {hodnoty}")'
# ⚠ Kopie leží v `tick-scratch/` (o úroveň hloub), takže `parents[1]` by ukazovalo
#    na `_analyza/` a měřidlo by spadlo na „HANDOFF.md NENÍ“ — tedy na JINÉM
#    místě, než se měří. WS se proto v kopii nahrazuje absolutní cestou.
RADEK_WS = "WS = pathlib.Path(__file__).resolve().parents[1]"

_vystup = []
ok = 0
chyby = []


def p(radek=""):
    print(radek)
    _vystup.append(radek)


def kontrola(podminka, text):
    global ok
    p(f"  {'OK  ' if podminka else 'CHYBA'} {text}")
    if podminka:
        ok += 1
    else:
        chyby.append(text)


def sekce(cislo, text):
    """Tělo oddílu `## <cislo>.` — kotva se bere z MĚŘENÉHO oddílu (vzor P28/B, H131)."""
    m = re.search(r"^## %s\." % re.escape(str(cislo)), text, re.M)
    if not m:
        return ""
    m2 = re.search(r"^## ", text[m.end():], re.M)
    return text[m.start(): m.end() + m2.start()] if m2 else text[m.start():]


def spust_meridlo(cesta, vystup):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([sys.executable, str(cesta), "--jen", "A3", "--vystup", vystup],
                       cwd=str(WS), capture_output=True, env=env, timeout=1800)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace")


def leg(popis, cesta_meridla, vystup, cekany_exit, cekany_text=None):
    kod, out = spust_meridlo(cesta_meridla, vystup)
    kontrola(kod == cekany_exit, f"{popis}: exit={kod} (čekán {cekany_exit})")
    if cekany_text:
        kontrola(cekany_text in out, f"{popis}: výstup obsahuje {cekany_text!r}")
        for l in out.splitlines():
            if cekany_text in l:
                p(f"         {l.strip()[:160]}")
    return kod, out


def main():
    p(f"# P30 — MUTAČNÍ DŮKAZ MĚŘIDLA · {time.strftime('%Y-%m-%d %H:%M:%S')}")
    p("")

    # ── pojistky proti tichému omylu ────────────────────────────────────────
    p("── P0: POJISTKY (kotvy a oslabená kopie) ──")
    text_dok = HANDOFF.read_text(encoding="utf-8")
    # ⚠ P32 (H145): kotva musí být v dokumentu 1× **A ZÁROVEŇ ležet v MĚŘENÉM
    #    oddílu (§60)** — jinak by se mutovalo místo, které měřidlo nečte.
    #    Obě podmínky jsou v JEDNÉ kontrole SCHVÁLNĚ: přidání další kontroly by
    #    posunulo čítač (16 → 17) a tím i baseline tvrzení v §61 — přesně to je
    #    churn, který projekt už jednou platil (H135).
    _s60 = sekce("60", text_dok)
    kontrola(text_dok.count(KOTVA_DOK) == 1 and _s60.count(KOTVA_DOK) == 1,
             f"kotva v dokumentu 1× ({text_dok.count(KOTVA_DOK)}×) "
             f"A v MĚŘENÉM oddílu §60 1× ({_s60.count(KOTVA_DOK)}×): {KOTVA_DOK!r}")
    text_brany = BRANA.read_text(encoding="utf-8")
    kontrola(text_brany.count(KOTVA_BRANY) == 1,
             f"kotva v bráně je 1× ({text_brany.count(KOTVA_BRANY)}×): {KOTVA_BRANY!r}")

    SCRATCH.mkdir(parents=True, exist_ok=True)
    text_mer = MERIDLO.read_text(encoding="utf-8")
    kontrola(text_mer.count(RADEK_ROZCHOD) == 1,
             f"oslabovaný řádek je v měřidle 1× ({text_mer.count(RADEK_ROZCHOD)}×)")
    kontrola(text_mer.count(RADEK_WS) == 1,
             f"řádek s `WS` je v měřidle 1× ({text_mer.count(RADEK_WS)}×)")
    oslabeny = text_mer.replace(RADEK_ROZCHOD, 'm.ok_(True, "OSLABENO (test mutace)")')
    oslabeny = oslabeny.replace(RADEK_WS, f'WS = pathlib.Path(r"{WS}")')
    kontrola("OSLABENO (test mutace)" in oslabeny and f'WS = pathlib.Path(r"{WS}")' in oslabeny,
             "oslabená kopie má VYPNUTÉ porovnání i SPRÁVNÝ workspace")
    OSLABENE.write_bytes(oslabeny.encode("utf-8"))
    p(f"         oslabená kopie: {OSLABENE.relative_to(WS)}")

    # ⚠ POJISTKA: zdravá oslabená kopie musí projít — kdyby spadla, každá
    #    „třetí noha“ by byla červená z jiného důvodu a diferenciál by lhal.
    kod0, out0 = spust_meridlo(OSLABENE, "_analyza/p30-mutace-oslabene-zdrava-vystup.txt")
    kontrola(kod0 == 0, f"oslabená kopie ve ZDRAVÉM stavu projde (exit={kod0})")
    if kod0 != 0:
        for l in out0.splitlines():
            if l.startswith("  CHYBA"):
                p(f"         {l.strip()[:160]}")

    # ── 1. ZDRAVÝ STAV (základna pro diferenciál) ───────────────────────────
    p("")
    p("── 1: ZDRAVÝ STAV (měřidlo musí projít) ──")
    leg("zdravý", MERIDLO, "_analyza/p30-mutace-zdravy-vystup.txt", 0)

    # ── 2. M1: MUTACE ČÍSLA V DOKUMENTU ────────────────────────────────────
    p("")
    p("── M1: DOKUMENT TVRDÍ JINÉ ČÍSLO (měřidlo ho musí PŘEČÍST) ──")
    # ⚠ P32 (H145): dvojznačná kotva NESMÍ SHODIT CELÝ TEST. Naměřeno 9. 10. 2026:
    #    `mutuj` vyhodil `ValueError` a měřidlo skončilo **exit 1 bez čítače** —
    #    „brána, která na nález spadne, hlásí míň než brána, která ho vypíše“.
    #    Dnes se to hlásí jako POJMENOVANÁ chyba a zbytek testu (M2) doběhne.
    try:
        with mutuj(HANDOFF, KOTVA_DOK, KOTVA_DOK_NOVA) as m1:
            p(f"         kotva nalezena {m1.pocet_vyskytu}× · {m1.hash_pred[:12]} → {m1.hash_po_mutaci[:12]}")
            leg("M1 mutant", MERIDLO, "_analyza/p30-mutace-m1-mutant-vystup.txt", 1, "ROZCHOD")
            leg("M1 mutant + oslabené měřidlo", OSLABENE, "_analyza/p30-mutace-m1-oslabene-vystup.txt", 0)
        kontrola(m1.hash_po_navratu == m1.hash_pred, "M1: HANDOFF.md vrácen bajt na bajt")
    except ValueError as e:
        kontrola(False, f"M1 NELZE PROVÉST (dvojznačná kotva v dokumentu): {str(e)[:130]}")
        p("         → diferenciál M1 je NEZMĚŘENÝ; příčina je kotva, ne měřená věc")

    # ── 3. M2: MUTACE ZDROJE BRÁNY ─────────────────────────────────────────
    p("")
    p("── M2: BRÁNA HLÁSÍ JINÝ ČÍTAČ (měřidlo ho musí ZMĚŘIT) ──")
    with mutuj(BRANA, KOTVA_BRANY, KOTVA_BRANY_NOVA) as m2:
        p(f"         kotva nalezena {m2.pocet_vyskytu}× · {m2.hash_pred[:12]} → {m2.hash_po_mutaci[:12]}")
        leg("M2 mutant", MERIDLO, "_analyza/p30-mutace-m2-mutant-vystup.txt", 1, "ROZCHOD")
        leg("M2 mutant + oslabené měřidlo", OSLABENE, "_analyza/p30-mutace-m2-oslabene-vystup.txt", 0)
    kontrola(m2.hash_po_navratu == m2.hash_pred, "M2: tools/over-skilly.py vrácen bajt na bajt")

    # ── 4. KONTROLA, ŽE OSLABENÍ NEBYLO TICHE ──────────────────────────────
    p("")
    p("── 4: KONTROLA SABOTÁŽE (oslabená kopie nesmí být slepá na VŠE) ──")
    kod, out = spust_meridlo(OSLABENE, "_analyza/p30-mutace-oslabene-kontrola-vystup.txt")
    kontrola("OSLABENO" not in out or kod == 0,
             "oslabená kopie projde i ve zdravém stavu (oslabení je cílené, ne globální)")

    p("")
    p(f"── VÝSLEDEK: {ok} kontrol, {len(chyby)} chyb ──")
    for c in chyby:
        p(f"  CHYBA: {c}")
    if not chyby:
        p("  (každá mutace ZMĚNILA verdikt; soubory vráceny bajt na bajt)")
    DOKLAD.write_bytes(("\n".join(_vystup) + "\n").encode("utf-8"))
    print(f"\n[doklad] {DOKLAD.relative_to(WS)} ({DOKLAD.stat().st_size} B, UTF-8)")
    return 1 if chyby else 0


if __name__ == "__main__":
    sys.exit(main())
