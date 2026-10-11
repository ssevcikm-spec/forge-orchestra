# -*- coding: utf-8 -*-
r"""P35 — MUTAČNÍ DŮKAZ: umí měřidlo `p35-a-overeni.py` SPADNOUT — a umí i PROJÍT?

PROČ TENHLE TEST EXISTUJE (`AGENTS.md`): „Napsal jsi test? Vrať do kódu vadu
a podívej se, že spadne." Bez toho je i „52/0" jen ticho. A druhá polovina
téhož: **kontrola, která spadne VŽDY, není o nic lepší než ta, která projde
vždy** — proto se každá mutace měří i v ZDRAVÉM stavu (musí projít).

CO SE MUTUJE (vždy do KOPIE přes seam — živé soubory se NESMÍ změnit):
  M1  TVRZENÍ v §65 (seam `P35_HANDOFF`): vypuštěný čítač `levně 50/0, plně 96/0`
      → A4 MUSÍ hlásit „§65 NETVRDÍ čítač měřidla P34" a spadnout. Dokazuje,
      že se tvrzení OPRAVDU ČTE Z DOKUMENTU (H155), nebere z hlavy.
  M2  DOKLAD ROZKLADU (seam `P35_ROZKLAD`): malý počet bajtů → B1 musí spadnout
      na tvrzení „tik tahá z GitHubu > 100 kB každou minutu".
  M3  DOKUD ROZKLADU ROADMAPY (seam `P35_ROZKLAD_ROADMAPY`): PROHOZENÉ časy
      (mapFn levný, cyklus drahý) → B1 musí spadnout. Tím je doložené, že oprava
      stojí na MĚŘENÍ, ne na vyprávění.
  M4  ŽIVÝ STAV (seam `P35_HEALTH`): `/health` BEZ `last_cron_pokus` (starší
      deploy) → A2 musí spadnout na „posílá POKUS".
  M5  KÓD CONDUCTORA (seam `P35_CONDUCTOR`): do KOPIE se vrátí drahá varianta
      `Uint8Array.from(atob(…), mapFn)` → B1 musí spadnout na kontrole kódu.
      (Mutuje se KOPIE — `conductor/src/index.ts` je živý soubor; H163.)
  M6  NÁVRAT: živé soubory jsou po testu BAJT NA BAJT původní a v `_analyza/`
      nezůstal žádný scratch.

⚠ Proč se mutuje `replace()` a ne přes `_analyza/_mutace.py`: `_mutace.mutuj`
  hlídá ŽIVÝ soubor (`try/finally` + `sha256`). Tady se NEMUTUJE živý soubor,
  ale KOPIE v `p35-mutace-scratch/` — a knihovna je stavěná na živou cestu.
  Pojistky proti „mutace se tiše neprovedla" (omyl #18/#106) jsou tu proto
  udělané ručně a POVINNĚ: kotva musí být v souboru PRÁVĚ 1×, text se musí
  ZMĚNIT a na konci se hash živých souborů porovnává s hodnotou před testem.

Použití: python _analyza\p35-mutace.py
"""
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
P35A = ANALYZA / "p35-a-overeni.py"
LIVE_HANDOFF = WS / "HANDOFF.md"
LIVE_CONDUCTOR = WS / "conductor" / "src" / "index.ts"
LIVE_TAIL = ANALYZA / "p35-tail-raw-vystup.txt"
LIVE_ROZKLAD = ANALYZA / "p35-rozklad-tiku-vystup.txt"
LIVE_ROZKLAD_RM = ANALYZA / "p35-rozklad-roadmapy-vystup.txt"
SCRATCH = ANALYZA / "p35-mutace-scratch"

ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
kontrol = 0
chyb = []


def zk(ok, popis, detail=""):
    global kontrol
    kontrol += 1
    print("  %s  %s" % ("OK  " if ok else "CHYBA", popis)
          + ("\n      %s" % detail if detail else ""))
    if not ok:
        chyb.append(popis)


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def spust(cmd, env=None, timeout=3600):
    r = subprocess.run([str(a) for a in cmd], cwd=str(WS), env={**ENV, **(env or {})},
                       capture_output=True, timeout=timeout)
    return r.returncode, ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace")


def citac(t):
    vse = list(re.finditer(r"V[ÝY]SLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb", t))
    return (vse[-1].group(1), vse[-1].group(2)) if vse else None


def mutuj_kopii(rel, zdroj, stary, novy, jmeno):
    """Zapíše KOPII `zdroj` do scratch s jednou záměnou; vrátí cestu kopie.

    Pojistky (jinak by „mutace, která se neprovedla" tvrdila totéž co úspěšná):
      * kotva je ve zdroji PRÁVĚ 1×,
      * text se SKUTEČNĚ změnil,
      * nový text NEOBSAHUJE starý jako podřetězec.
    """
    cesta = SCRATCH / jmeno
    cesta.write_bytes(pathlib.Path(zdroj).read_bytes())
    txt = pathlib.Path(zdroj).read_text(encoding="utf-8")
    zk(txt.count(stary) == 1, "%s: kotva je ve zdroji PRÁVĚ 1×" % rel)
    zmeneny = txt.replace(stary, novy, 1)
    zk(zmeneny != txt and stary not in zmeneny,
       "%s: MUTACE SE PROVEDLA (text se změnil a starý v něm není)" % rel)
    cesta.write_text(zmeneny, encoding="utf-8")
    return cesta


def mutuj_kopii_re(rel, zdroj, vzor, nahrada, jmeno):
    """Táž pojistka jako `mutuj_kopii`, ale kotva je REGEX (naměřená čísla se
    mezi běhy mění — natvrdo psaná kotva by po změně měření tiše nenarazila)."""
    cesta = SCRATCH / jmeno
    txt = pathlib.Path(zdroj).read_text(encoding="utf-8")
    nove, n = re.subn(vzor, nahrada, txt, count=1)
    zk(n == 1, "%s: vzor trefil PRÁVĚ 1× (naměřeno %d)" % (rel, n))
    zk(nove != txt, "%s: MUTACE SE PROVEDLA (text se změnil)" % rel)
    cesta.write_text(nove, encoding="utf-8")
    return cesta


print("=" * 84)
print("P35 — MUTAČNÍ DŮKAZ měřidla (umí spadnout? a umí i projít?)")
print("=" * 84)
SCRATCH.mkdir(parents=True, exist_ok=True)
sha_handoff = sha(LIVE_HANDOFF)
sha_cond = sha(LIVE_CONDUCTOR)
sha_mer = sha(P35A)

print("\n0) POJISTKY")
zk(P35A.is_file(), "měřidlo `p35-a-overeni.py` existuje")
for d, popis in [(LIVE_HANDOFF, "živý `HANDOFF.md`"), (LIVE_CONDUCTOR, "živý conductor"),
                 (LIVE_TAIL, "doklad živého tailu"), (LIVE_ROZKLAD, "rozklad GitHub části"),
                 (LIVE_ROZKLAD_RM, "rozklad čtení roadmapy")]:
    zk(d.is_file(), "%s existuje (%s)" % (popis, d.name))

# ── M1: tvrzení v §65 (KOPIE dokumentu) ─────────────────────────────────────
print("\n1) M1 — měřidlo musí spadnout, když v §65 NENÍ tvrzení, které hledá")
TVRZ = "levně 50/0, plně 96/0"
txt = LIVE_HANDOFF.read_text(encoding="utf-8")
zk(txt.count(TVRZ) == 1,
   "kotva tvrzení je v CELÉM dokumentu PRÁVĚ 1× (jinak by mutace trefila jinam)",
   "počet=%d" % txt.count(TVRZ))
kopie_h = mutuj_kopii("HANDOFF", LIVE_HANDOFF, TVRZ, "(údaj vypuštěn mutací)", "handoff-m1.md")
kod, v = spust([sys.executable, "-B", str(P35A), "--jen", "A4", "--levne",
                "--vystup", str(SCRATCH / "m1-zmutovany.txt")],
               env={"P35_HANDOFF": str(kopie_h)}, timeout=1800)
zk(kod != 0, "měřidlo nad ZMUTOVANÝM dokumentem SPADNE (exit=%d)" % kod)
zk("NETVRDÍ čítač" in v, "a spadne PRÁVĚ na chybějícím tvrzení",
   [l.strip() for l in v.splitlines() if "NETVRDÍ" in l][:1])
zk(sha(LIVE_HANDOFF) == sha_handoff, "živý `HANDOFF.md` se přitom NEZMĚNIL (bajt na bajt)")

# ── M2: rozklad GitHub části (seam P35_ROZKLAD) ─────────────────────────────
print("\n2) M2 — malý objem GitHub části → B1 musí spadnout")
kopie_r = mutuj_kopii_re("rozklad", LIVE_ROZKLAD, r"přenesených bajtů na tik:\s*\d+\s*B",
                         "přenesených bajtů na tik: 10 B", "rozklad-m2.txt")
kod, v = spust([sys.executable, "-B", str(P35A), "--jen", "B1",
                "--vystup", str(SCRATCH / "m2.txt")],
               env={"P35_ROZKLAD": str(kopie_r)}, timeout=1800)
zk(kod != 0, "B1 nad podstrčeným malým objemem SPADNE (exit=%d)" % kod)
zk("> 100 kB KAŽDOU MINUTU" in v, "a spadne PRÁVĚ na kontrole objemu GitHub části",
   [l.strip() for l in v.splitlines() if "100 kB" in l][:1])

# ── M3: rozklad čtení roadmapy (seam P35_ROZKLAD_ROADMAPY) ──────────────────
print("\n3) M3 — PROHOZENÉ časy dekodéru → B1 musí spadnout")
kopie_rr = mutuj_kopii_re("rozklad-roadmapy", LIVE_ROZKLAD_RM,
                          r"3\. Uint8Array\.from\(mapFn\) PO ZNACÍCH:\s*[\d.]+\s*ms",
                          "3. Uint8Array.from(mapFn) PO ZNACÍCH:  0.05 ms",
                          "rozklad-rm-m3.txt")
kod, v = spust([sys.executable, "-B", str(P35A), "--jen", "B1",
                "--vystup", str(SCRATCH / "m3.txt")],
               env={"P35_ROZKLAD_ROADMAPY": str(kopie_rr)}, timeout=1800)
zk(kod != 0, "B1 nad prohozenými časy SPADNE (exit=%d) — oprava stojí na MĚŘENÍ" % kod)
zk("dekódování po ZNACÍCH" in v, "a spadne PRÁVĚ na kontrole ceny dekodéru",
   [l.strip() for l in v.splitlines() if "dekódování" in l][:1])

# ── M4: živý stav (seam P35_HEALTH) — OBA směry ─────────────────────────────
print("\n4) M4 — A2 musí PROJÍT na zdravém stavu a SPADNOUT bez `last_cron_pokus`")
# ⚠ ČASY SE BEROU Z HODIN, ne natvrdo: naměřeno při psaní tohohle testu —
# první verze měla `last_cron` psaný napevno, takže byl vůči „teď" o desítky
# minut starý a predikát brány (SPRÁVNĚ) hlásil vadu. Test pak tvrdil, že měřidlo
# „neumí projít", ačkoli chyba byla ve fixtuře (past: vina testu, ne nástroje).
from datetime import datetime, timedelta, timezone  # noqa: E402

def iso(min_zpet):
    return (datetime.now(timezone.utc) - timedelta(minutes=min_zpet)).strftime("%Y-%m-%dT%H:%M:%S.000Z")


zdravy = {"http_status": 200, "ok": True, "time": iso(0),
          "ready": 3, "running": 0,
          "last_cron": iso(0.5), "last_cron_min": 0,
          "last_cron_pokus": iso(0.2), "last_cron_pokus_min": 0,
          "last_tick": iso(0.5), "last_tick_zdroj": "cron"}
f_zdravy = SCRATCH / "health-zdravy.json"
f_zdravy.write_text(json.dumps(zdravy), encoding="utf-8")
kod, v = spust([sys.executable, "-B", str(P35A), "--jen", "A2",
                "--vystup", str(SCRATCH / "m4-zdravy.txt")],
               env={"P35_HEALTH": str(f_zdravy)}, timeout=600)
zk(kod == 0, "ZDRAVÝ stav → A2 PROJDE (exit=%d, čítač %s) — kontrola není vždy červená"
   % (kod, citac(v)))
stary = {k: x for k, x in zdravy.items() if not k.startswith("last_cron_pokus")}
f_stary = SCRATCH / "health-bez-pokusu.json"
f_stary.write_text(json.dumps(stary), encoding="utf-8")
kod, v = spust([sys.executable, "-B", str(P35A), "--jen", "A2",
                "--vystup", str(SCRATCH / "m4-stary.txt")],
               env={"P35_HEALTH": str(f_stary)}, timeout=600)
zk(kod != 0, "STARŠÍ `/health` (bez pokusu) → A2 SPADNE (exit=%d)" % kod)
zk("posílá `last_cron_pokus`" in v, "a spadne PRÁVĚ na kontrole pokusu",
   [l.strip() for l in v.splitlines() if "last_cron_pokus" in l and "CHYBA" in l][:1])

# ── M5: kód conductora (seam P35_CONDUCTOR) ─────────────────────────────────
print("\n5) M5 — vrácená DRAHÁ varianta dekodéru → B1 musí spadnout")
kod_zdroj = LIVE_CONDUCTOR.read_text(encoding="utf-8")
NOVA = ("      const bin = atob(String(data.content || \"\").replace(/\\n/g, \"\"));\n"
        "      const bytes = new Uint8Array(bin.length);\n"
        "      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);")
STARA = ("      const bytes = Uint8Array.from(\n"
         "        atob(String(data.content || \"\").replace(/\\n/g, \"\")),\n"
         "        (c) => c.charCodeAt(0),\n"
         "      );")
zk(kod_zdroj.count(NOVA) == 1, "kotva NOVÉHO kódu je v conductoru PRÁVĚ 1×")
kopie_c = SCRATCH / "conductor-m5.ts"
kopie_c.write_text(kod_zdroj.replace(NOVA, STARA, 1), encoding="utf-8")
zk(sha(kopie_c) != sha_cond, "kopie conductora se od živého LIŠÍ (mutace se provedla)")
kod, v = spust([sys.executable, "-B", str(P35A), "--jen", "B1",
                "--vystup", str(SCRATCH / "m5.txt")],
               env={"P35_CONDUCTOR": str(kopie_c)}, timeout=1800)
zk(kod != 0, "B1 nad kopií s DRAHÝM dekodérem SPADNE (exit=%d)" % kod)
zk("INDEXOVANÝ CYKLUS" in v, "a spadne PRÁVĚ na kontrole kódu opravy",
   [l.strip() for l in v.splitlines() if "INDEXOVANÝ CYKLUS" in l][:1])
zk(sha(LIVE_CONDUCTOR) == sha_cond, "živý conductor se přitom NEZMĚNIL (bajt na bajt)")

# ── M6: návrat a úklid ─────────────────────────────────────────────────────
print("\n6) M6 — návrat a úklid")
zk(sha(LIVE_HANDOFF) == sha_handoff, "živý `HANDOFF.md` je po celém testu bajt na bajt původní")
zk(sha(LIVE_CONDUCTOR) == sha_cond, "živý conductor je po celém testu bajt na bajt původní")
zk(sha(P35A) == sha_mer, "měřidlo `p35-a-overeni.py` je bajt na bajt původní")
shutil.rmtree(SCRATCH, ignore_errors=True)
zk(not SCRATCH.exists(), "scratch `p35-mutace-scratch/` je uklizený")
zbyle = sorted(x.name for x in ANALYZA.glob("p35-mutace-scratch*"))
zk(not zbyle, "a v `_analyza/` po něm nic nezůstalo (%s)" % (zbyle or "nic"))

print("\n" + "=" * 84)
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
for c in chyb:
    print("   CHYBA %s" % c)
print("=" * 84)
sys.exit(1 if chyb else 0)
