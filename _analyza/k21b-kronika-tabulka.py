# -*- coding: utf-8 -*-
r"""Srovná tabulku v `KRONIKA-PROJEKTU.md` §3 do TVARU, KTERÝ ČTE BRÁNA.

PROČ: `kronika-kontrola.py` čte počty omylů **z tabulky kroniky** tímto vzorem:

    ^\| **<blok>** \| <popis> \| **<počet>** \|

Tedy **blok | popis | počet | …**. Moje nová tabulka měla sloupce v jiném pořadí
(`Blok | Session | Počet | …`), takže ji brána nepřečetla — a protože mým
přesunem zároveň zmizela ta stará (kterou číst uměla), brána začala hlásit
„v kronice §3 řádek NEMÁ" u **všech osmi** bloků.

**Bránu jsem neopravoval.** Vzor je správný: kdo tabulku píše, musí ji psát
v tom tvaru, který je **kanonický** (a všechna předchozí vydání ho měla).
Opravuje se tedy **dokument**, ne měřidlo.

Použití:  python _analyza\k21b-kronika-tabulka.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
ZALOHA = WS / "_analyza" / "kronika-pred-k21b.md"
ZAPIS = "--zapis" in sys.argv

text = KRONIKA.read_text(encoding="utf-8")
puvodni = text

STARA = """| Blok | Session | Počet | Z toho vad MĚŘIDLA | Z toho vypadalo jako nález o CIZÍM kódu |
|---|---|---|---|---|
| 1–13 | 30. 9. – 1. 10. | 13 | **9** | — |
| **8b** | ověřovací 1. 10. | **10** | **6** | **5** |
| **8c** | akční 2. 10. 11:3x | **5** | **4** | **2** |
| **8d** | plánovací 2. 10. 10:1x | **6** | **5** | **2** |
| **8e** | akční 2. 10. 11:0x | **11** | **9** | **5** |
| **8f** | plánovací 2. 10. 12:1x | **10** | **9** | **4** |
| **8g** | plánovací 2. 10. 13:0x | **11** | **8** | **3** |
| **8h** | akční 2. 10. 16:1x | **8** | **8** | **4** |
| **celkem** | | **74** | **58 = 78 %** | **31** |"""

NOVA = """| Blok | Session (kdy a jaká) | Počet omylů | Z toho vad MĚŘIDLA | Z toho vypadalo jako nález o CIZÍM kódu |
|---|---|---|---|---|
| **1–13** | 30. 9. – 1. 10. | **13** | **9** | — |
| **8b** | ověřovací 1. 10. | **10** | **6** | **5** |
| **8c** | akční 2. 10. 11:3x | **5** | **4** | **2** |
| **8d** | plánovací 2. 10. 10:1x | **6** | **5** | **2** |
| **8e** | akční 2. 10. 11:0x | **11** | **9** | **5** |
| **8f** | plánovací 2. 10. 12:1x | **10** | **9** | **4** |
| **8g** | plánovací 2. 10. 13:0x | **11** | **8** | **3** |
| **8h** | akční 2. 10. 16:1x | **8** | **8** | **4** |
| **celkem** | **8 bloků, 17 sessions** | **74** | **58 = 78 %** | **31** |

> **⚠ FORMAT TABULKY NENÍ LIBOVOLNÝ — čte ji brána.** `kronika-kontrola.py`
> hledá řádek tvaru `| **<blok>** | <popis> | **<počet>** |`. Když jsem
> v téhle session tabulku přepsal s jiným pořadím sloupců, brána ji
> **nepřečetla** a hlásila „v kronice §3 řádek NEMÁ" u **všech osmi** bloků —
> tedy **falešný poplach na správných datech**. **Opravil se dokument, ne
> měřidlo** (vzor je kanonický a všechna předchozí vydání ho měla)."""

assert text.count(STARA) == 1, "stará tabulka nenalezena (%dx)" % text.count(STARA)
text = text.replace(STARA, NOVA, 1)
assert text != puvodni and NOVA in text, "NÁHRADA NEPROBĚHLA"
print("OK: tabulka §3 srovnána do tvaru, který brána čte")

if ZAPIS:
    ZALOHA.write_bytes(puvodni.encode("utf-8"))
    KRONIKA.write_bytes(text.encode("utf-8"))
    assert KRONIKA.read_text(encoding="utf-8") == text, "zapsaný obsah nesedí"
    print("  záloha: %s; ZAPSÁNO a ověřeno čtením z disku." % ZALOHA.name)
else:
    print("  (dry-run — spusť s --zapis)")
