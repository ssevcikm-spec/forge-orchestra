# -*- coding: utf-8 -*-
r"""P32 — TEST OPRAVY H136: zapíše `p27-dopln-zaznamy.py` soubor, i když kotvu NENAŠEL?

PROČ TENHLE TEST EXISTUJE: `AGENTS.md` — „Napsal jsi test? Vrať do kódu vadu
a podívej se, že spadne." A druhá polovina téhož: **důkaz je DIFERENCIÁL**, ne
zelená. Test proto měří DVĚ věci:

  * **živý** `p27-dopln-zaznamy.py` nad fixturami s CHYBĚJÍCÍMI kotvami
    **NEZAPÍŠE** (soubor zůstane bajt na bajt, včetně konců řádků), ačkoli
    skončí `exit 1` — to je oprava H136;
  * **oslabená KOPIE** s PŮVODNÍM (nehlídaným) `vymen()` soubor **ZAPÍŠE**
    — tím je dokázáno, že kontrola „nezapsáno" opravdu měří (jinak by test
    procházel i s vrácenou vadou).

⚠ PROČ FIXTURY A NE ŽIVÉ DOKUMENTY: sáhnout testem na živý `HANDOFF.md`
znamená dělat přesně tu vadu, kterou H130/H136 popisují. `p27-dopln-zaznamy.py`
proto od P32 čte cesty z prostředí (`P27_HANDOFF`, `P27_KRONIKA`) a test je
posílá na svoje fixtury.

⚠ JAK SE POZNÁ ZÁPIS: fixtury mají konce řádků **CRLF**, kdežto skript čte
`read_text()` (univerzální newline) a zapisuje `write_bytes(text.encode())`,
tedy s **LF**. Jakýkoli zápis je proto vidět na bajtech — a to i tehdy, když se
obsah „nezmění".

Použití: python _analyza/p32-test-zapis-kotvy.py
"""

import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
P27 = ANALYZA / "p27-dopln-zaznamy.py"
SCRATCH = ANALYZA / "p32-scratch"
KOPIE = ANALYZA / "_p32-mut-p27.py"
sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj  # noqa: E402

# ── kotvy mutace: MUSÍ se shodovat se zdrojem (jinak by se mutace neprovedla) ──
NOVY_VYMEN = '''    chyby = ["%s: kotva %d× (musí 1×): %r" % (popis, text.count(stary), stary[:60])
             for stary, _ in dvojice if text.count(stary) != 1]
    if chyby:
        for c in chyby:
            k(False, c)
        k(False, "%s: NEZAPSÁNO (kotvy nesedí) — soubor zůstal NEDOTČEN" % popis)
        return False
    for stary, novy in dvojice:
        text = text.replace(stary, novy, 1)
    cesta.write_bytes(text.encode("utf-8"))
    k(True, "%s: zapsáno (všech %d kotev 1×)" % (popis, len(dvojice)))
    return True'''
STARY_VYMEN = '''    for stary, novy in dvojice:
        n = text.count(stary)
        if n != 1:
            k(False, "%s: kotva %d× (musí 1×): %r" % (popis, n, stary[:60]))
            continue
        text = text.replace(stary, novy, 1)
    cesta.write_bytes(text.encode("utf-8"))
    k(True, "%s: zapsáno" % popis)'''

# Fixtury: kotvy §57 (ani §57.3) tu NEJSOU; markery bloků naopak ANO, aby
# jediným možným zapisovatelem byl `vymen()`.
FIX_H = ("# FIXTURA HANDOFF (P32) — kotvy §57 tu ZÁMĚRNĚ NEJSOU\r\n"
         "15. **PŘEPSANÝ ŘÁDEK SESSION** je tu proto, aby blok §57 nic nepsal.\r\n")
FIX_K = ("# FIXTURA KRONIKA (P32)\r\n"
         "| **P27-P** | je tu proto, aby blok §2.20 nic nepsal |\r\n")

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


def nasad(pripona):
    h = SCRATCH / ("fixtura-handoff%s.md" % pripona)
    kk = SCRATCH / ("fixtura-kronika%s.md" % pripona)
    h.write_bytes(FIX_H.encode("utf-8"))
    kk.write_bytes(FIX_K.encode("utf-8"))
    return h, kk


def spust(skript, h, kk):
    env = dict(os.environ, PYTHONIOENCODING="utf-8",
               P27_HANDOFF=str(h), P27_KRONIKA=str(kk))
    r = subprocess.run([sys.executable, "-B", str(skript)], capture_output=True,
                       cwd=str(WS), env=env, timeout=300)
    v = (r.stdout or b"").decode("utf-8", "replace") + \
        (r.stderr or b"").decode("utf-8", "replace")
    return r.returncode, v


print("=" * 78)
print("P32 — TEST H136: zapíše patcher soubor, i když kotvu nenašel?")
print("=" * 78)
SCRATCH.mkdir(parents=True, exist_ok=True)

# ── 0) pojistky ─────────────────────────────────────────────────────────────
print("\n0) POJISTKY (co test předpokládá)")
zdroj = P27.read_text(encoding="utf-8")
zk(P27.is_file(), "živý `p27-dopln-zaznamy.py` existuje")
zk(zdroj.count(NOVY_VYMEN) == 1, "kotva OPRAVENÉHO `vymen()` je ve zdroji právě 1×",
   "počet=%d" % zdroj.count(NOVY_VYMEN))
zk(STARY_VYMEN not in zdroj, "PŮVODNÍ (nehlídaný) tvar ve zdroji NENÍ")
zk(NOVY_VYMEN.count(STARY_VYMEN) == 0, "nový tvar NEOBSAHUJE starý jako podřetězec")

# ── 1) ŽIVÝ patcher: se špatnými kotvami NESMÍ zapsat ──────────────────────
print("\n1) ŽIVÝ patcher nad fixturami s CHYBĚJÍCÍMI kotvami")
h1, k1 = nasad("-zivy")
zk(b"\r\n" in h1.read_bytes() and b"\r\n" in k1.read_bytes(),
   "fixtury mají PŘED během konce řádků CRLF (jinak by zápis nebyl vidět)")
sha_h1, sha_k1 = sha(h1), sha(k1)
kod1, v1 = spust(P27, h1, k1)
zk(kod1 != 0, "patcher hlásí chybu (exit=%d)" % kod1)
zk("NEZAPSÁNO" in v1 and "NEDOTČEN" in v1,
   "a v výstupu ŘEKNE, že NEZAPSAL",
   [l.strip() for l in v1.splitlines() if "NEZAPSÁNO" in l][:1])
zk(sha(h1) == sha_h1, "HANDOFF-fixtura je bajt na bajt NEDOTČENÁ (H136 opraven)")
zk(sha(k1) == sha_k1, "KRONIKA-fixtura je bajt na bajt NEDOTČENÁ")

# ── 2) DIFERENCIÁL: oslabená kopie s PŮVODNÍM vymen() ZAPÍŠE ───────────────
print("\n2) DIFERENCIÁL — kopie s PŮVODNÍM `vymen()` (bez hlídání kotvy)")
h2, k2 = nasad("-mutant")
sha_h2, sha_k2 = sha(h2), sha(k2)
shutil.copyfile(P27, KOPIE)
try:
    with mutuj(KOPIE, NOVY_VYMEN, STARY_VYMEN):
        zk(KOPIE.read_text(encoding="utf-8").count(STARY_VYMEN) == 1,
           "v kopii je PŮVODNÍ tvar právě 1× (mutace se PROVEDLA)")
        kod2, v2 = spust(KOPIE, h2, k2)
finally:
    KOPIE.unlink(missing_ok=True)
zk(kod2 != 0, "oslabená kopie také hlásí chybu (exit=%d) — rozdíl NENÍ v exitu" % kod2)
zk(sha(h2) != sha_h2, "ALE HANDOFF-fixturu ZAPSALA (bajty se změnily) → kontrola MĚŘÍ",
   "%s → %s" % (sha_h2[:12], sha(h2)[:12]))
zk(b"\r\n" not in h2.read_bytes(), "a je vidět PROČ: zápis převedl CRLF na LF")
zk(sha(k2) == sha_k2, "KRONIKA-fixtura zůstala nedotčená (blok §2.20 je hlídaný markerem)")
zk(KOPIE.exists() is False, "oslabená kopie patcheru je smazaná")

# ── úklid a souhrn ─────────────────────────────────────────────────────────
shutil.rmtree(SCRATCH, ignore_errors=True)
zk(not SCRATCH.exists(), "scratch je uklizený")

print("\n" + "=" * 78)
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
for c in chyb:
    print("   CHYBA %s" % c)
print("=" * 78)
sys.exit(1 if chyb else 0)
