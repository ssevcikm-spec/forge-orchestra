# -*- coding: utf-8 -*-
"""TEST brány N32 — umí vůbec spadnout? (mutační důkaz)

PROČ: `AGENTS.md` — „Napsal jsi test? Vrať do kódu vadu a podívej se, že spadne."
Brána, která nemá jak selhat, není brána. Tenhle test proto:

  1) ověří KONTROLNÍ stav: nad zdravým stromem brána skončí `exit 0`,
  2) vloží do JEDNOHO živého `.py` `from __future__ import annotations`
     ZA první příkaz (což je přesně vada H85) a ověří, že `compile()` na to
     skutečně zareaguje (kdyby ne, mutace se tiše neprovedla — a to tvrdí totéž
     co mutace, která projde),
  3) spustí bránu a vyžádá `exit 1` + nález pojmenovaný RELATIVNÍ CESTOU oběti,
  4) vrátí soubor BAJT NA BAJT a ověří SHA-256 i to, že brána je zase zelená.

Soubor se vrací ve `finally` — i kdyby test spadl uprostřed.
Použití: python _analyza/test-n32-mutace.py
"""

import hashlib
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
BRANA = WS / "_analyza" / "n32-kompilovatelnost.py"
FUTURE = "from __future__ import annotations"

kontroly = []


def zk(ok: bool, popis: str, detail: str = "") -> None:
    kontroly.append((ok, popis, detail))
    print(f"  {'OK  ' if ok else 'CHYBA'} {popis}{f'  [{detail}]' if detail else ''}")


def spust_branu():
    r = subprocess.run([sys.executable, str(BRANA)], capture_output=True,
                       cwd=str(WS), timeout=300)
    return r.returncode, (r.stdout + r.stderr).decode("utf-8", "replace")


print("=" * 78)
print("TEST N32 — umí brána kompilovatelnosti spadnout?")
print("=" * 78)

# ── 1) KONTROLNÍ stav ────────────────────────────────────────────────────
print("\n--- 1) kontrolní stav (zdravý strom) --------------------------------")
kod0, v0 = spust_branu()
zk(kod0 == 0, "zdravý strom → exit 0", f"exit={kod0}")
zk("0 nekompilovatelných" in v0, "čítač hlásí 0 nekompilovatelných")

# ── 2) vyber oběť a zmutuj ji ────────────────────────────────────────────
print("\n--- 2) mutace jednoho živého souboru --------------------------------")
kandidati = [p for p in sorted((WS / "_analyza").glob("*.py"))
             if "_archiv" not in p.parts
             and p.name not in ("n32-kompilovatelnost.py", "test-n32-mutace.py")]
obet = None
nove_radky = None
puvodni = None
for k in kandidati:
    b = k.read_bytes()
    t = b.decode("utf-8")
    radky = t.splitlines(keepends=True)
    i = next((j for j, l in enumerate(radky)
              if l.strip() and not l.lstrip().startswith(("#", '"""', "'''",
                                                          'r"""', "r'''"))), None)
    if i is None:
        continue
    kandidat = radky[:i + 1] + [FUTURE + "\n"] + radky[i + 1:]
    try:
        compile("".join(kandidat), str(k), "exec")
        continue                       # mutace tenhle soubor nepolapí → jiný
    except SyntaxError:
        obet, nove_radky, puvodni = k, kandidat, b
        break

zk(obet is not None, "našel se soubor, na kterém mutace vyrobí SyntaxError",
   obet.name if obet else "—")

if obet is None:
    print("\nVÝSLEDEK: 0 kontrol, 1 chyb — test nemohl pokračovat")
    sys.exit(1)

sha_pred = hashlib.sha256(puvodni).hexdigest()
print(f"      oběť: {obet.relative_to(WS)}  (SHA-256 {sha_pred[:16]}…)")

try:
    obet.write_bytes("".join(nove_radky).encode("utf-8"))
    # mutace se musí SKUTEČNĚ projevit — jinak test tvrdí totéž co slepý test
    try:
        compile(obet.read_text(encoding="utf-8"), str(obet), "exec")
        zk(False, "mutace se projevila (compile hlásí SyntaxError)")
    except SyntaxError as e:
        zk("__future__" in str(e.msg), "mutace se projevila (compile hlásí __future__)",
           e.msg)

    # ── 3) brána musí spadnout ───────────────────────────────────────────
    print("\n--- 3) brána nad zmutovaným stromem --------------------------------")
    kod1, v1 = spust_branu()
    zk(kod1 == 1, "zmutovaný strom → exit 1", f"exit={kod1}")
    rel = str(obet.relative_to(WS))
    zk(rel in v1, "brána nález POJMENOVALA (relativní cestou)", rel)
    zk("1 nekompilovatelných" in v1, "čítač hlásí 1 nekompilovatelný")
finally:
    # ── 4) vrácení BAJT NA BAJT ──────────────────────────────────────────
    print("\n--- 4) vrácení souboru bajt na bajt --------------------------------")
    obet.write_bytes(puvodni)
    sha_po = hashlib.sha256(obet.read_bytes()).hexdigest()
    zk(sha_po == sha_pred, "SHA-256 po vrácení je shodný", sha_po[:16] + "…")
    kod2, v2 = spust_branu()
    zk(kod2 == 0, "po vrácení je brána zase zelená", f"exit={kod2}")

chyb = sum(1 for ok, _, _ in kontroly if not ok)
print("\n" + "=" * 78)
print(f"VÝSLEDEK: {len(kontroly)} kontrol, {chyb} chyb")
for ok, popis, d in kontroly:
    if not ok:
        print(f"   CHYBA {popis}  [{d}]")
print("=" * 78)
sys.exit(1 if chyb else 0)
