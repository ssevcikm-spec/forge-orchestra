# -*- coding: utf-8 -*-
r"""P13c: sjednotí řádek 27 v KRONIKA-PROJEKTU.md s KONEČNÝMI čísly P13c-b.

CO SE STALO: jeden pokus o tenhle zápis skončil `AssertionError` (podezření na
neviditelný znak v kotvě) — a protože skript zapisoval **až na konci**, řádek 27
zůstal s čísly z PRVNÍ vlny (`28 bran`, `274 souborů`, `1009`). To je dnes
**nepravda** a v kronice by to číslo žilo dál.

Skript proto nahrazuje **konkrétní čísla**, ověřuje, že náhrada proběhla, a nic
jiného nemění.
"""

import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = pathlib.Path(r"E:\Workspaces\forge-orchestra\KRONIKA-PROJEKTU.md")
t = P.read_text(encoding="utf-8")

NAHRADY = [
    # (starý text, nový text) — mění se JEN v řádku 27 (kontroluje se níž).
    ("`g3`: **28 bran, 0 nedosazených záznamníků, 0 bran, které vůbec nezačaly** (před: **15**)",
     "`g3`: **30 bran, 0 nedosazených záznamníků, 0 bran, které vůbec nezačaly, "
     "0 nenulových exitů** (před: **15 neběželo, 22 nenulových**)"),
    ("`verify-setup` **ZMĚŘENO: 84 kontrol, 0 chyb** (před 6× CHYBI)",
     "`verify-setup` **ZMĚŘENO: 49 kontrol, 0 chyb** (před 6× CHYBI)"),
    ("skener **274 souborů** (z toho **14 netrackovaných**), **NEPOKRYTO 0** (před **69**)",
     "skener **268 souborů** (z toho **23 netrackovaných**), **NEPOKRYTO 0** (před **69**)"),
    ("inventář **1009 souborů**",
     "inventář **1003 souborů**"),
    ("`node tools/validate-all.mjs` → VŠE V POŘÁDKU**",
     "`node tools/validate-all.mjs` → VŠE V POŘÁDKU**; `chybějící importy (statická)` "
     "**67 souborů** a `CI workflow (šablona + hra)` **36 testů**"),
]

# Kotva: řádek 27 musí existovat právě jednou.
radky = t.splitlines(keepends=True)
indexy = [i for i, l in enumerate(radky) if l.startswith("| **27** |")]
assert len(indexy) == 1, f"řádek 27 nalezen {len(indexy)}x"
i = indexy[0]

for stary, novy in NAHRADY:
    pocet = radky[i].count(stary)
    assert pocet == 1, f"v řádku 27 je {pocet}x: {stary[:70]!r}"
    radky[i] = radky[i].replace(stary, novy, 1)

t2 = "".join(radky)
P.write_text(t2, encoding="utf-8", newline="")

zpet = P.read_text(encoding="utf-8")
radek = next(l for l in zpet.splitlines() if l.startswith("| **27** |"))
for stary, _ in NAHRADY:
    assert stary not in radek, f"starý text v řádku 27 ZŮSTAL: {stary[:60]!r}"
for kotva in ("**30 bran**", "**49 kontrol**", "**268 souborů**", "**144–148**",
              "| **8s** |", "| **H69** |"):
    assert kotva in zpet, f"chybí: {kotva}"
print("řádek 27 sjednocen s P13c-b;", len(zpet.splitlines()), "řádků")
