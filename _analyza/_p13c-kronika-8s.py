# -*- coding: utf-8 -*-
r"""P13c: doplní do KRONIKA-PROJEKTU.md řádek bloku `8s` (omylů 5) do tabulky §3.

PROČ: brána `kronika-kontrola.py` má **obousměrnou** kontrolu — ptá se i naopak
(„je každý blok omylů v `HANDOFF.md` i v tabulce kroniky?"). Nový blok `8s`
tam chyběl, a brána to **správně** ohlásila:

    CHYBA blok 8s je v HANDOFF.md (5 omylů), ale v tabulce kroniky §3 řádek NEMÁ

Skript vkládá **jen jeden řádek** za `8r` a nic jiného nemění (`overovani` §9.8).
"""

import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = pathlib.Path(r"E:\Workspaces\forge-orchestra\KRONIKA-PROJEKTU.md")
t = P.read_text(encoding="utf-8")

KOTVA = ("| **8r** | plánovací (ověřovací) **4. 10.** 22:5x–23:5x "
         "(**OVĚŘENÍ PŘESUNU NA `E:`**) | **6** | **6** | **3** |")
assert t.count(KOTVA) == 1, f"kotva 8r nalezena {t.count(KOTVA)}x"

NOVY = KOTVA + "\n" + (
    "| **8s** | akční (opravná) **5. 10.** 00:0x–01:1x "
    "(**P13c: OPRAVA PĚTI MĚŘIDEL PO PŘESUNU**) | **5** | **3** | **3** |"
)

t = t.replace(KOTVA, NOVY, 1)
P.write_text(t, encoding="utf-8", newline="")
zpet = P.read_text(encoding="utf-8")
assert zpet.count("| **8s** |") == 1, "řádek 8s se nevložil právě jednou"
assert zpet.count("| **8r** |") == 1, "řádek 8r zmizel!"
print("řádek 8s vložen;", len(zpet.splitlines()), "řádků")
