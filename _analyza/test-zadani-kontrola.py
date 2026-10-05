#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""MUTAČNÍ TEST brány `_analyza/zadani-kontrola.py` (nález H53).

PROČ TO EXISTUJE
----------------
`zadani-kontrola.py` po přesunu na `E:` **srovnával orchestra pod klíčem
`orchestra`**, ale zadání ji (podle NÁZVU REPA) jmenuje `forge-orchestra`.
`tvrzene_head.get("orchestra")` proto vrátil `None`, skript vypsal
„? orchestra: zadání netvrdí žádný commit" a **orchestra se vůbec neporovnala**.

Důsledek, který se nesmí splést: skript skončil `exit 1` a jeho verdikt
(„zadání je zastaralé") byl **náhodou správný** — ale **ne z toho důvodu,
kvůli kterému existuje**. Kdyby zadání tvrdilo správný commit, spadl by stejně
(`overovani` §10.1: `exit 1` ze špatného důvodu).

CO TEST MĚŘÍ (dva případy, opačné výsledky)
-------------------------------------------
  1. ZDRAVÝ  — hlavička tvrdí ŽIVÝ HEAD obou repů  → `exit 0`
  2. VRÁCENÁ VADA — hlavička tvrdí STARÝ commit     → `exit 1`
     a ve výstupu je VIDĚT, že se orchestra porovnala (ne „netvrdí žádný commit")

⚠ CO TEST NESMÍ UDĚLAT: přepsat `NEXT-SESSION-INSTRUKCE.md` a nechat ho
změněný. Každý zápis je v `try/finally` a na konci se **ověří bajtová shoda**
(`overovani` §10.6).

Použití: python _analyza\test-zadani-kontrola.py
Návrat:  0 = brána měří správně | 1 = nález | 2 = test sám selhal
"""

import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
BRANA = WS / "_analyza" / "zadani-kontrola.py"
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
GIT = WS / "tools" / "git.cmd"
HRA = WS.parent / "uo-shadows"

kontrol = 0
chyb = 0


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if ok:
        print(f"  OK    {popis}")
    else:
        chyb += 1
        print(f"  CHYBA {popis}")
        if detail:
            for radek in detail.splitlines():
                print(f"        {radek}")


def git(repo: pathlib.Path, *args: str) -> str:
    r = subprocess.run([str(GIT), "-C", str(repo), *args], capture_output=True, shell=True)
    return (r.stdout or b"").decode("utf-8", "replace").strip()


def spust_branu() -> tuple:
    r = subprocess.run([sys.executable, str(BRANA)], capture_output=True,
                       cwd=str(WS), timeout=300)
    v = (r.stdout or b"").decode("utf-8", "replace") + (r.stderr or b"").decode("utf-8", "replace")
    return r.returncode, v


def radek_stavu(text: str) -> str:
    for l in text.splitlines()[:30]:
        if "Stav obou repů při psaní:" in l or "Stav obou repu pri psani:" in l:
            return l
    raise SystemExit("CHYBA: v zadání není řádek „Stav obou repů při psaní“ — test nemá co mutovat")


def nahrad_radek_stavu(text: str, novy: str) -> str:
    stary = radek_stavu(text)
    return text.replace(stary, novy, 1)


def main() -> int:
    if not ZADANI.is_file():
        print(f"CHYBA: {ZADANI} neexistuje")
        return 2

    puvodni = ZADANI.read_bytes()
    text = puvodni.decode("utf-8")
    head_orch = git(WS, "rev-parse", "--short", "HEAD")
    head_hra = git(HRA, "rev-parse", "--short", "HEAD")
    pocet = git(WS, "rev-list", "--count", "origin/main..HEAD")
    print("=" * 74)
    print("MUTAČNÍ TEST: zadani-kontrola.py (nález H53)")
    print("=" * 74)
    print(f"  živý HEAD: forge-orchestra={head_orch}  uo-shadows={head_hra}"
          f"  (nepushnuto: {pocet})")
    print()

    try:
        # ── 1) ZDRAVÝ STAV: hlavička tvrdí ŽIVÝ HEAD ─────────────────────────
        print("--- 1) hlavička tvrdí ŽIVÝ HEAD → očekávám exit 0 ---")
        dobry = nahrad_radek_stavu(
            text,
            f"**Stav obou repů při psaní:** `forge-orchestra` = `{head_orch}` "
            f"(strom čistý) · `uo-shadows` = `{head_hra}` (strom čistý)")
        assert dobry != text, "MUTACE SE NEPROVEDLA (řádek se nezměnil)"
        ZADANI.write_bytes(dobry.encode("utf-8"))
        kod, v = spust_branu()
        radek_orch = [l.strip() for l in v.splitlines() if "forge-orchestra:" in l]
        zkontroluj("zdravá hlavička → exit 0", kod == 0, f"exit={kod}\n" + "\n".join(radek_orch))
        zkontroluj("orchestra SE POROVNALA (ne „netvrdí žádný commit“)",
                   not any("netvrdí žádný commit" in l for l in v.splitlines()),
                   "\n".join(l for l in v.splitlines() if "netvrdí" in l))
        zkontroluj("výstup hlásí shodu s živým HEAD",
                   any(f"OK   forge-orchestra: tvrzený {head_orch}" in l for l in v.splitlines()),
                   "\n".join(radek_orch))

        # ── 2) VRÁCENÁ VADA: hlavička tvrdí STARÝ commit ─────────────────────
        print()
        print("--- 2) hlavička tvrdí STARÝ commit → očekávám exit 1 ---")
        # ⚠ PAST, která mě tady chytila: první verze vzala `HEAD~1` — jenže
        # zdravý stav vkládá do hlavičky `head_orch`, který je NĚKDY sám
        # `HEAD~1` (proto se mutace ticho neprovedla a assert to pojmenoval).
        # Proto se bere **starší commit a přepíše se na zjevně neplatný tvar**:
        # `stary + "0"` nemůže být skutečný HEAD ani náhodou.
        stary = (git(WS, "rev-parse", "--short", "HEAD~1") or "000000") + "0"
        assert not head_orch.startswith(stary[:7]), "zmutovaný sha je náhodou živý HEAD"
        vadny = nahrad_radek_stavu(
            text,
            f"**Stav obou repů při psaní:** `forge-orchestra` = `{stary}` "
            f"(strom čistý) · `uo-shadows` = `{head_hra}` (strom čistý)")
        assert vadny != text and f"`{stary}`" in vadny, "MUTACE SE NEPROVEDLA"
        ZADANI.write_bytes(vadny.encode("utf-8"))
        kod2, v2 = spust_branu()
        zkontroluj("vrácená vada (starý commit) → exit 1", kod2 == 1, f"exit={kod2}")
        zkontroluj("vada je pojmenovaná (rozchod orchestra, ne „netvrdí commit“)",
                   "forge-orchestra: zadání tvrdí" in v2,
                   "\n".join(l.strip() for l in v2.splitlines() if "forge-orchestra" in l))
    finally:
        # ── NÁVRAT: bajt na bajt, i když test spadne uprostřed ───────────────
        ZADANI.write_bytes(puvodni)
        assert ZADANI.read_bytes() == puvodni, "ZADÁNÍ NEVRÁCENO BAJT NA BAJT!"

    print()
    print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb   (zadání vráceno bajt na bajt)")
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())
