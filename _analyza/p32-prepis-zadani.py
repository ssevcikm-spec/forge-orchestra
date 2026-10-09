# -*- coding: utf-8 -*-
r"""P32 — JEDNORÁZOVÝ PŘEPIS `NEXT-SESSION-INSTRUKCE.md` pro P33.

PROČ SKRIPTEM: text má 400+ řádků a hlavička musí nést **commit, který vznikl
teprve commitem** (`8bf36ff`) — šablona s placeholdery je proto mimo repo
(`E:\Workspaces\_p33-next-session-draft.md`) a nahradí se tady.

⚠ `NEXT-SESSION-INSTRUKCE.md` se **NECOMMITUJE** (hlavička musí sedět na živý
`HEAD`) — skript ho jen zapíše a ověří, že v něm nezůstal žádný placeholder.

Použití: python _analyza\p32-prepis-zadani.py
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
SABLONA = pathlib.Path(r"E:\Workspaces\_p33-next-session-draft.md")
CIL = WS / "NEXT-SESSION-INSTRUKCE.md"
GIT = WS / "tools" / "git.cmd"


def git(*args):
    r = subprocess.run([str(GIT), "-C", str(WS), *args], capture_output=True)
    return (r.stdout or b"").decode("utf-8", "replace").strip()


# ⚠ HEAD SE ČTE Z GITU, NEZAPEKÁVÁ SE. Naměřeno 9. 10. 2026 (vlastní omyl P32):
# s zapečeným `8bf36ff` skript po druhém commitu spadl na VLASTNÍ kontrole
# („v textu chybí kotva orchestry“) — a zadání by tvrdilo zastaralý commit.
# Kotva zadání se přitom porovnává na ROVNOST s živým `HEAD` (`zadani-kontrola.py`).
HEAD = git("rev-parse", "--short", "HEAD")
STAT = git("diff", "--shortstat", "d3f1a48..HEAD")
_m = re.search(r"(\d+) files? changed, (\d+) insertions?\(\+\), (\d+) deletions?\(-\)", STAT)
COMMIT_INFO = ("`%s` (%s souborů, +%s/−%s)"
               % (HEAD, _m.group(1), _m.group(2), _m.group(3))) if _m else "`%s`" % HEAD

NAHRADY = {
    "__HEAD__": HEAD,
    "__HEAD_SHORT__": HEAD,
    "__HRA__": git("-C", r"E:\Workspaces\uo-shadows", "rev-parse", "--short", "HEAD"),
    "__HRA_STAV__": "naposledy se pohnula **9. 10. 2026 11:56 +02:00** "
                    "a od té doby stojí",
    "__DATUM__": "9. 10. 2026, 20:4x +02:00",
    "__COMMIT_INFO__": COMMIT_INFO,
    "__A4__": "A4 (dávka dokladů `--jen A4`) → **3/0**: „žádný z 4 sledovaných "
              "dokumentů se nezměnil“ a „KDO ZAPSAL“ prázdné (H130/H138 zavřené); "
              "`p32-a-overeni.py` v dávce **39/0** za 33 s",
}

text = SABLONA.read_text(encoding="utf-8")
for klic, hodnota in NAHRADY.items():
    if klic not in text:
        print("CHYBA: placeholder %s v šabloně NENÍ (přepis by tiše vynechal vstup)" % klic)
        sys.exit(1)
    text = text.replace(klic, hodnota)

zbytek = sorted(set(re.findall(r"__[A-Z0-9_]+__", text)))
if zbytek:
    print("CHYBA: v textu zůstaly placeholdery: %s" % zbytek)
    sys.exit(1)

# Pojistky nad obsahem, který se čte měřidlem `zadani-kontrola.py`.
# ⚠ Kotvy se berou Z `NAHRADY` — jinak by kontrola zůstala na starém commitu
# a spadla by na SOBĚ (naměřeno 9. 10. 2026: přesně to se stalo).
for kotva, popis in ((r"`forge-orchestra` = `%s`" % NAHRADY["__HEAD__"], "kotva orchestry"),
                     (r"`uo-shadows` = `%s`" % NAHRADY["__HRA__"], "kotva hry"),
                     ("## 2.1 Úkol A", "oddíl Úkol A"),
                     ("STAVOVÝ ŘÁDEK", "stavový řádek")):
    if not re.search(kotva, text):
        print("CHYBA: v textu chybí %s (%r)" % (popis, kotva))
        sys.exit(1)

CIL.write_bytes(text.encode("utf-8"))
print("  zapsáno: %s (%d B, UTF-8, bez BOM: %s)"
      % (CIL.name, CIL.stat().st_size, CIL.read_bytes()[:3] != b"\xef\xbb\xbf"))
print("VÝSLEDEK: 1 kontrol, 0 chyb")
