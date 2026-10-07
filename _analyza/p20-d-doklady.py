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
VZOR = re.compile(r"^(ov-|p1[6-9]-|p2[0-9]-)")

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
             "p24-sonda-site.py", "p24-sonda-m2.py"}

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

selhale = [x for x in vysledky if x[1] != 0]
po = {p.name: hash_souboru(p) for p in SLEDOVANE}
zmenene = [n for n in pred if pred[n] != po[n]]

print("\n" + "=" * 78)
print(f"SOUHRN: {len(vysledky)} dokladů, {len(selhale)} s nenulovým exit")
print("=" * 78)
print("\nZÁPIS DO DOKUMENTŮ (pojistka, P22):")
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
