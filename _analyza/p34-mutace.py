# -*- coding: utf-8 -*-
r"""P34 — MUTAČNÍ DŮKAZ: umí měřidlo `p34-a-overeni.py` SPADNOUT — a umí i PROJÍT?

PROČ TENHLE TEST EXISTUJE (`AGENTS.md`): „Napsal jsi test? Vrať do kódu vadu
a podívej se, že spadne." Bez toho je i „35/0" jen ticho. A druhá polovina
téhož: **kontrola, která spadne VŽDY, není o nic lepší než ta, která projde
vždy** — proto se u A8 měří OBA směry (zdravý stav → ZELENÁ, vadný → ČERVENÁ).

CO SE MUTUJE (vždy do KOPIE, živé soubory se nesmí změnit):
  M1  TVRZENÍ v §64 (seam `P34_HANDOFF`) — vypuštěný odstavec s číslem
      `112/3/2/4` → měřidlo MUSÍ hlásit „TVRZENÍ NENALEZENO“ a spadnout.
      Dokazuje, že se tvrzení OPRAVDU ČTE Z DOKUMENTU (H155), nebere z hlavy.
  M2  ŽIVÝ STAV (seam `P34_HEALTH`): a) ZDRAVÝ tep → A8 musí PROJÍT;
      b) NESOULAD (služba hlásí `last_cron_min` starý, ale `last_cron` čerstvý)
      → A8 musí SPADNOUT na kontrole konzistence predikátu se stavem.
  M3  DOKLAD ANALYTIKY (seam `P34_CF`) bez `exceededResources` → B1 musí spadnout.
  M4  ŽIVÝ TAIL (seam `P34_TAIL`) jen s HTTP eventy (žádný cron) → B1 musí spadnout.
  M5  NÁVRAT: živý `HANDOFF.md` i měřidlo jsou po testu BAJT NA BAJT původní
      a v `_analyza/` nezůstal žádný scratch.

Použití: python _analyza\p34-mutace.py
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
P34A = ANALYZA / "p34-a-overeni.py"
LIVE_HANDOFF = WS / "HANDOFF.md"
LIVE_HEALTH = ANALYZA / "p34-health-vystup.txt"
LIVE_CF = ANALYZA / "p34-cf-analytika-vystup.txt"
LIVE_TAIL = ANALYZA / "p34-tail-cron-plny-vystup.txt"
SCRATCH = ANALYZA / "p34-mutace-scratch"

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
    vse = list(re.finditer(r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb", t))
    return (vse[-1].group(1), vse[-1].group(2)) if vse else None


print("=" * 80)
print("P34 — MUTAČNÍ DŮKAZ měřidla (umí spadnout? a umí i projít?)")
print("=" * 80)
SCRATCH.mkdir(parents=True, exist_ok=True)
sha_handoff_pred = sha(LIVE_HANDOFF)
sha_p34a_pred = sha(P34A)

print("\n0) POJISTKY")
zk(P34A.is_file(), "měřidlo `p34-a-overeni.py` existuje")
zk(LIVE_HANDOFF.is_file(), "živý `HANDOFF.md` existuje")
for d, popis in [(LIVE_HEALTH, "doklad živého /health"), (LIVE_CF, "doklad analytiky"),
                 (LIVE_TAIL, "doklad živého tailu")]:
    zk(d.is_file(), "%s existuje (%s)" % (popis, d.name))

# ── M1: tvrzení v §64 (KOPIE dokumentu) ─────────────────────────────────────
print("\n1) M1 — měřidlo musí spadnout, když v §64 NENÍ tvrzení, které hledá")
kod, v = spust([sys.executable, "-B", str(P34A), "--jen", "A3", "--levne",
                "--vystup", str(SCRATCH / "m1-zdravy.txt")], timeout=3600)
c0 = citac(v)
zk(kod == 0, "zdravý běh `--jen A3 --levne` → exit 0 (naměřeno %d, čítač %s)" % (kod, c0))

txt = LIVE_HANDOFF.read_text(encoding="utf-8")
TVRZ = "Plný běh (C0–C8): 112/3/2/4"
zk(txt.count(TVRZ) == 1,
   "kotva tvrzení je v CELÉM dokumentu PRÁVĚ 1× (jinak by mutace trefila jinam)",
   "počet=%d" % txt.count(TVRZ))
kopie = SCRATCH / "handoff-m1.md"
zmut = txt.replace(TVRZ, "Plný běh (C0–C8): (údaj vypuštěn mutací)", 1)
zk(zmut != txt and TVRZ not in zmut, "MUTACE SE PROVEDLA: číslo z §64 je pryč")
kopie.write_bytes(zmut.encode("utf-8"))
zk(sha(kopie) != sha_handoff_pred, "kopie dokumentu se od živého LIŠÍ")
kod, v = spust([sys.executable, "-B", str(P34A), "--jen", "A3", "--levne",
                "--vystup", str(SCRATCH / "m1-zmutovany.txt")],
               env={"P34_HANDOFF": str(kopie)}, timeout=3600)
zk(kod != 0, "měřidlo nad ZMUTOVANÝM dokumentem SPADNE (exit=%d)" % kod)
zk("TVRZENÍ NENALEZENO" in v, "a spadne PRÁVĚ na chybějícím tvrzení",
   [l.strip() for l in v.splitlines() if "TVRZENÍ NENALEZENO" in l][:1])
zk(sha(LIVE_HANDOFF) == sha_handoff_pred,
   "živý `HANDOFF.md` se přitom NEZMĚNIL (bajt na bajt)")

# ── M2: živý stav (seam P34_HEALTH) — OBA směry ─────────────────────────────
print("\n2) M2 — A8 musí PROJÍT na zdravém stavu a SPADNOUT na nesouladu")
ted = time.time() * 1000
zdravy = {"http_status": 200, "ok": True, "time": "2026-10-11T05:00:00.000Z",
          "ready": 3, "running": 0,
          "last_cron": "2026-10-11T04:59:30.000Z", "last_cron_min": 0,
          "last_cron_pokus": "2026-10-11T04:59:40.000Z", "last_cron_pokus_min": 0,
          "last_tick": "2026-10-11T04:59:30.000Z", "last_tick_zdroj": "cron"}
f_zdravy = SCRATCH / "health-zdravy.json"
f_zdravy.write_text(json.dumps(zdravy), encoding="utf-8")
kod, v = spust([sys.executable, "-B", str(P34A), "--jen", "A8",
                "--vystup", str(SCRATCH / "m2-zdravy.txt")],
               env={"P34_HEALTH": str(f_zdravy)}, timeout=600)
c = citac(v)
zk(kod == 0, "ZDRAVÝ stav → měřidlo PROJDE (exit=%d, čítač %s) — kontrola není vždy červená" % (kod, c))
zk("predikát brány nad tím tepem: OK" in v, "a predikát opravdu tvrdí OK")

nesoulad = dict(zdravy)
nesoulad["last_cron_min"] = 190        # služba tvrdí „starý tep“
f_nes = SCRATCH / "health-nesoulad.json"
f_nes.write_text(json.dumps(nesoulad), encoding="utf-8")
kod, v = spust([sys.executable, "-B", str(P34A), "--jen", "A8",
                "--vystup", str(SCRATCH / "m2-nesoulad.txt")],
               env={"P34_HEALTH": str(f_nes)}, timeout=600)
zk(kod != 0, "NESOULAD (služba: 190 min, predikát: OK) → měřidlo SPADNE (exit=%d)" % kod)
zk("si neodporují" in v, "a spadne PRÁVĚ na kontrole konzistence predikátu se stavem",
   [l.strip() for l in v.splitlines() if "si neodporují" in l][:1])

# ── M3 + M4: doklady příčiny (seam P34_CF / P34_TAIL) ───────────────────────
print("\n3) M3/M4 — doklady příčiny: bez `exceededResources` / bez cron eventu")
try:
    cf = json.loads(LIVE_CF.read_text(encoding="utf-8"))
except Exception as e:  # noqa: BLE001
    cf = None
    zk(False, "doklad analytiky se nedá přečíst: %s" % e)
if cf is not None:
    cf2 = dict(cf)
    cf2["radky"] = [x for x in cf["radky"] if x["dimensions"]["status"] != "exceededResources"]
    f_cf = SCRATCH / "cf-bez-exceeded.json"
    f_cf.write_text(json.dumps(cf2), encoding="utf-8")
    kod, v = spust([sys.executable, "-B", str(P34A), "--jen", "B1",
                    "--vystup", str(SCRATCH / "m3.txt")],
                   env={"P34_CF": str(f_cf)}, timeout=600)
    zk(kod != 0, "M3 analytika bez `exceededResources` → měřidlo SPADNE (exit=%d)" % kod)

tail_lines = [l for l in LIVE_TAIL.read_text(encoding="utf-8", errors="replace").splitlines()
              if l.strip().startswith("{")]
only_http = []
for l in tail_lines:
    try:
        o = json.loads(l)
    except Exception:  # noqa: BLE001
        continue
    if (o.get("event") or {}).get("cron") is None:
        only_http.append(l)
f_tail = SCRATCH / "tail-bez-cronu.txt"
f_tail.write_text("\n".join(only_http) + "\n", encoding="utf-8")
kod, v = spust([sys.executable, "-B", str(P34A), "--jen", "B1",
                "--vystup", str(SCRATCH / "m4.txt")],
               env={"P34_TAIL": str(f_tail)}, timeout=600)
zk(kod != 0, "M4 tail bez cron eventu → měřidlo SPADNE (exit=%d)" % kod)
zk("CRON eventů" in v, "a spadne PRÁVĚ na kontrole „doklad má CRON eventy“",
   [l.strip() for l in v.splitlines() if "CRON eventů" in l][:1])

# ── M5: návrat a úklid ─────────────────────────────────────────────────────
print("\n4) M5 — návrat a úklid")
zk(sha(LIVE_HANDOFF) == sha_handoff_pred, "živý `HANDOFF.md` je po celém testu bajt na bajt původní")
zk(sha(P34A) == sha_p34a_pred, "měřidlo `p34-a-overeni.py` je bajt na bajt původní")
shutil.rmtree(SCRATCH, ignore_errors=True)
zk(not SCRATCH.exists(), "scratch `p34-mutace-scratch/` je uklizený")
zbyle = sorted(x.name for x in ANALYZA.glob("p34-mutace-scratch*"))
zk(not zbyle, "a v `_analyza/` po něm nic nezůstalo (%s)" % (zbyle or "nic"))

print("\n" + "=" * 80)
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
for c in chyb:
    print("   CHYBA %s" % c)
print("=" * 80)
sys.exit(1 if chyb else 0)
