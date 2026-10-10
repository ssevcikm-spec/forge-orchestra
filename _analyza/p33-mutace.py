# -*- coding: utf-8 -*-
r"""P33 — MUTAČNÍ DŮKAZ: umí měřidlo P33 SPADNOUT?

PROČ TENHLE TEST EXISTUJE: `AGENTS.md` — „Napsal jsi test? Vrať do kódu vadu
a podívej se, že spadne." Bez toho je i 60/0 jen ticho. Test proto vrací vady
do **KOPIÍ** (živý `HANDOFF.md` se NESMÍ změnit) a měří DVĚ věci:

  * **M1 — čtení tvrzení:** zmutuje se TVRZENÍ v §63 (`over-skilly` 92/0 → 93/0)
    v KOPII dokumentu (seam `P33_HANDOFF`) → měřidlo MUSÍ spadnout na té kontrole
    a živý dokument zůstat bajt na bajt. Tím je dokázáno, že se tvrzení opravdu
    **ČTE Z DOKUMENTU** a nebere z hlavy.
  * **M2 — brána cronu umí spadnout:** měřidlu se podstrčí **POST-nasazovací**
    stav jako „stav před nasazením“ (seam `P33_HEALTH`) → kontrola C8-5 („nad
    před-nasazovacím stavem musí predikát SPADNOUT“) MUSÍ selhat. Tím je
    dokázáno, že ta kontrola není prázdná.
  * **M3 — návrat:** živé soubory jsou po testu bajt na bajt původní a v `_analyza/`
    nezůstal žádný scratch.

Použití: python _analyza/p33-mutace.py
"""

import hashlib
import importlib.util
import os
import pathlib
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
P33A = ANALYZA / "p33-a-overeni.py"
LIVE_HANDOFF = WS / "HANDOFF.md"
HEALTH_PO = ANALYZA / "p33-health-po-vystup.txt"
SCRATCH = ANALYZA / "p33-mutace-scratch"

# ── kotvy mutací (MUSÍ se shodovat se zdrojem; ověřuje se PŘED během) ─────────
TVRZENI_STARE = "`over-skilly` **92/0**"
TVRZENI_NOVE = "`over-skilly` **93/0**"

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
    vse = []
    for m in __import__("re").finditer(r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb", t):
        vse.append((m.group(1), m.group(2)))
    return vse[-1] if vse else None


def nacti_p33():
    spec = importlib.util.spec_from_file_location("p33_modul", str(P33A))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


print("=" * 78)
print("P33 — MUTAČNÍ DŮKAZ měřidla (umí spadnout?)")
print("=" * 78)
SCRATCH.mkdir(parents=True, exist_ok=True)
sha_live_pred = sha(LIVE_HANDOFF)
sha_p33a_pred = sha(P33A)

# ── 0) pojistky ─────────────────────────────────────────────────────────────
print("\n0) POJISTKY (co test předpokládá)")
zk(P33A.is_file(), "měřidlo `p33-a-overeni.py` existuje")
mod = nacti_p33()
text63, l0, l1 = mod.oddil(r"^##\s+63\.", LIVE_HANDOFF)
zk(text63.count(TVRZENI_STARE) == 1,
   "kotva tvrzení je v §63 PRÁVĚ 1× (jinak by mutace trefila jiné místo)",
   "počet=%d (řádky §63: %d–%d)" % (text63.count(TVRZENI_STARE), l0, l1))
zk(HEALTH_PO.is_file(), "doklad ŽIVÉHO `/health` existuje (%s)" % HEALTH_PO.name)

# ── 1) M1: zmutované TVRZENÍ v KOPII dokumentu ─────────────────────────────
print("\n1) M1 — měřidlo musí spadnout na ZMUTOVANÉM TVRZENÍ v §63")
kod0, v0 = spust([sys.executable, "-B", str(P33A), "--jen", "C3",
                  "--vystup", str(SCRATCH / "m1-zdravy.txt")])
c0 = citac(v0)
zk(kod0 == 0, "zdravý běh `--jen C3` → exit 0 (naměřeno %s)" % (kod0,))
zk(c0 is not None and c0[1] == "0", "a 0 chyb (naměřeno %s)" % (c0,))

kopie = SCRATCH / "handoff-m1.md"
txt = LIVE_HANDOFF.read_text(encoding="utf-8")
# ⚠ MUTUJE SE V TOM OKNĚ, KTERÉ MĚŘIDLO MĚŘÍ (§63). Kdyby se nahradil „první
# výskyt v CELÉM dokumentu“, trefil by se jiný oddíl (tatáž kotva je v dokumentu
# víc než 1×) a mutace by měřidlo vůbec nezasáhla — přesně past H131/H145.
i63 = txt.find(text63)
t63_new = text63.replace(TVRZENI_STARE, TVRZENI_NOVE, 1)
zk(i63 >= 0 and t63_new != text63, "mutace míří DO §63 (okno měření), ne jinam")
zmut = txt[:i63] + t63_new + txt[i63 + len(text63):]
kopie.write_bytes(zmut.encode("utf-8"))
# ověření NA ZÁPISU (ne na vstupu): v KOPII se §63 musí číst s novým tvrzením
t63_kopie, _, _ = mod.oddil(r"^##\s+63\.", kopie)
zk(zmut != txt, "kopie dokumentu se od živého LIŠÍ (mutace se provedla)")
zk(t63_kopie.count(TVRZENI_NOVE) == 1 and t63_kopie.count(TVRZENI_STARE) == 0,
   "a v §63 KOPIE je 93/0 a 92/0 tam NENÍ",
   "v CELÉM živém dokumentu je kotva %d× (proto se mutuje v okně §63)"
   % txt.count(TVRZENI_STARE))
kod1, v1 = spust([sys.executable, "-B", str(P33A), "--jen", "C3",
                  "--vystup", str(SCRATCH / "m1-zmutovany.txt")],
                 env={"P33_HANDOFF": str(kopie)})
c1 = citac(v1)
zk(kod1 != 0, "měřidlo nad ZMUTOVANÝM dokumentem SPADNE (exit=%d)" % kod1)
zk(c1 is not None and c1[1] != "0", "a čítač to ukáže (naměřeno %s)" % (c1,))
zk("C3 over-skilly" in v1 and "NAMĚŘENO" in v1,
   "a spadne PRÁVĚ na tom tvrzení (výpis kontroly):",
   [l.strip() for l in v1.splitlines() if "C3 over-skilly" in l][:1])
zk(sha(LIVE_HANDOFF) == sha_live_pred,
   "živý `HANDOFF.md` se přitom NEZMĚNIL (bajt na bajt)")

# ── 2) M2: podstrčený POST-nasazovací stav místo před-nasazovacího ─────────
print("\n2) M2 — kontrola C8-5 musí selhat, když „stav před nasazením“ tep MÁ")
kod2, v2 = spust([sys.executable, "-B", str(P33A), "--jen", "C8",
                  "--vystup", str(SCRATCH / "m2-zdravy.txt")])
c2 = citac(v2)
zk(kod2 == 0, "zdravý běh `--jen C8` → exit 0 (naměřeno %s, %s)" % (kod2, c2))
kod3, v3 = spust([sys.executable, "-B", str(P33A), "--jen", "C8",
                  "--vystup", str(SCRATCH / "m2-podstrceny.txt")],
                 env={"P33_HEALTH": str(HEALTH_PO)})
zk(kod3 != 0, "s PODSTRČENÝM post-nasazovacím stavem měřidlo SPADNE (exit=%d)" % kod3)
zk("C8-5" in v3, "a spadne PRÁVĚ na kontrole C8-5 („nad tím stavem musí brána spadnout“)",
   [l.strip() for l in v3.splitlines() if "C8-5" in l][:2])

# ── 3) M3: návrat a úklid ──────────────────────────────────────────────────
print("\n3) M3 — návrat a úklid")
zk(sha(LIVE_HANDOFF) == sha_live_pred, "živý `HANDOFF.md` je po celém testu bajt na bajt původní")
zk(sha(P33A) == sha_p33a_pred, "měřidlo `p33-a-overeni.py` je bajt na bajt původní")
shutil.rmtree(SCRATCH, ignore_errors=True)
zk(not SCRATCH.exists(), "scratch `p33-mutace-scratch/` je uklizený")
zbyle = sorted(x.name for x in ANALYZA.glob("p33-mutace-scratch"))
zk(not zbyle, "a v `_analyza/` po něm nic nezůstalo (%s)" % (zbyle or "nic"))

print("\n" + "=" * 78)
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
for c in chyb:
    print("   CHYBA %s" % c)
print("=" * 78)
sys.exit(1 if chyb else 0)
