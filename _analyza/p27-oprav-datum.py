# -*- coding: utf-8 -*-
r"""P27 — OPRAVA DATA ve vlastních záznamech: dnes je **8. 10. 2026**, ne 7. 10.

PROČ: zadání P27 vzniklo 7. 10. 2026 večer, ale session P27 **měřila 8. 10.
2026** (živý čas: 2026-10-08 10:2x +02:00). Zapsal jsem do vlastních záznamů
datum **7. 10.** — tedy **nepravdivé datum měření**. Vlastní záznam z téže
session se opravuje (není to historie; je to vada zápisu).

⚠ MĚNÍ SE JEN MŮJ VÝŘEZ:
  * `HANDOFF.md` — jen oddíl **§57** (poslední oddíl, celý je můj),
  * `KRONIKA-PROJEKTU.md` — jen **řádek 42** a **§2.20**,
  * `_analyza/p27-*.py` — celé soubory (všechny jsou moje).
  * `p20-d-doklady.py` — jen blok „PŘESKOČENO 7. 10. 2026 (P27)"; zmínka
    „# ⚠ P24 (7. 10. 2026) — NEMAŽ" je CIZÍ TEXT a **zůstává**.
  * `tools/test-tick-offline.mjs` — moje hlavička P27 datum neuvádí, takže
    se v něm **nic nemění** (jeho „7. 10." patří P24/P25).

Použití: python _analyza/p27-oprav-datum.py
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
H = WS / "HANDOFF.md"
K = WS / "KRONIKA-PROJEKTU.md"
P20D = WS / "_analyza" / "p20-d-doklady.py"

STARY = "7. 10. 2026"
NOVY = "8. 10. 2026"

# (soubor, jak vymezit MŮJ výřez, co v něm nahradit)
kontrol = 0
chyb = []


def k(ok, popis):
    global kontrol
    kontrol += 1
    print("  %s  %s" % ("OK  " if ok else "CHYBA", popis))
    if not ok:
        chyb.append(popis)


def vymen_ve_vyrezu(cesta, oteviraci, uzaviraci, dvojice, popis):
    """Nahradí dvojice POUZE ve výřezu <otevírací>…<uzavírací> (jinak nic)."""
    text = cesta.read_text(encoding="utf-8")
    i = text.find(oteviraci)
    if i < 0:
        k(False, "%s: výřez %r nenalezen" % (popis, oteviraci))
        return
    j = text.find(uzaviraci, i) if uzaviraci else -1
    if uzaviraci and j < 0:
        k(False, "%s: konec výřezu %r nenalezen" % (popis, uzaviraci))
        return
    if j < 0:
        j = len(text)
    usek = text[i:j]
    novy_usek = usek
    for a, b in dvojice:
        n = novy_usek.count(a)
        if n == 0:
            k(False, "%s: kotva %r ve výřezu není" % (popis, a[:60]))
            continue
        novy_usek = novy_usek.replace(a, b)
        print("      %s: %d× %r → %r" % (popis, n, a[:50], b[:50]))
    if novy_usek == usek:
        k(False, "%s: výřez se NEZMĚNIL" % popis)
        return
    cesta.write_bytes((text[:i] + novy_usek + text[j:]).encode("utf-8"))
    k(True, "%s: zapsáno" % popis)


print("=" * 78)
print("P27 — oprava data ve vlastních záznamech (7. 10. → 8. 10. 2026)")
print("=" * 78)

# ── HANDOFF §57 ─────────────────────────────────────────────────────────────
vymen_ve_vyrezu(H, "## 57. P27", None, [
    (STARY, NOVY),
    ("HEAD 1bdc982 + záznamy", "HEAD 649ca9b"),
    ("nepushnutých 5 (P25, 3× P26, P27)", "nepushnutých 6 (P25, 3× P26, 2× P27)"),
    ("`origin/main..HEAD`\n  bude **5** (P25, tři commity P26, P27)",
     "`origin/main..HEAD`\n  bude **6** (P25, tři commity P26, dva commity P27)"),
], "HANDOFF §57")

# ── KRONIKA: řádek 42 ───────────────────────────────────────────────────────
text = K.read_text(encoding="utf-8")
m = re.search(r"^\| \*\*42\*\* \|.*$", text, re.M)
k(m is not None, "kronika: řádek 42 nalezen")
if m:
    radek = m.group(0)
    novy = radek.replace(STARY, NOVY)
    k(novy != radek, "kronika: řádek 42 obsahoval %r" % STARY)
    K.write_bytes((text[:m.start()] + novy + text[m.end():]).encode("utf-8"))
    print("      řádek 42: datum opraveno")

# ── KRONIKA: §2.20 ─────────────────────────────────────────────────────────
vymen_ve_vyrezu(K, "### 2.20 Nálezy z P27", "\n## 3. ", [(STARY, NOVY)],
                "KRONIKA §2.20")

# ── moje nástroje ───────────────────────────────────────────────────────────
for jmeno in ("p27-a-overeni.py", "p27-b-mutace.py", "p27-radek-kroniky.py",
              "p27-sonda-endpointy.py", "p27-sonda-inventar.py"):
    p = WS / "_analyza" / jmeno
    t = p.read_text(encoding="utf-8")
    if STARY not in t:
        print("  OK    %s: žádné %r" % (jmeno, STARY))
        kontrol += 1
        continue
    p.write_bytes(t.replace(STARY, NOVY).encode("utf-8"))
    k(True, "%s: %d× %r → %r" % (jmeno, t.count(STARY), STARY, NOVY))

# ── p20-d: JEN můj blok ─────────────────────────────────────────────────────
t = P20D.read_text(encoding="utf-8")
stare_jmeno = "PŘESKOČENO 7. 10. 2026 (P27)"
k(stare_jmeno in t, "p20-d: můj blok P27 nalezen")
t2 = t.replace(stare_jmeno, "PŘESKOČENO 8. 10. 2026 (P27)")
P20D.write_bytes(t2.encode("utf-8"))
k("PŘESKOČENO 8. 10. 2026 (P27)" in t2, "p20-d: blok P27 má správné datum")
k("# ⚠ P24 (7. 10. 2026) — NEMAŽ" in t2, "p20-d: CIZÍ text P24 zůstal nedotčen")

# ── kontroly po zápisu ─────────────────────────────────────────────────────
print()
for p, popis in ((H, "HANDOFF"), (K, "KRONIKA")):
    b = p.read_bytes()
    k(b.count(b"\r\n") == 0, "%s: LF (žádné CRLF)" % popis)
    k(not b.startswith(b"\xef\xbb\xbf"), "%s: bez BOM" % popis)
t_h = H.read_text(encoding="utf-8")
i57 = t_h.find("## 57. P27")
k(STARY not in t_h[i57:], "HANDOFF §57 už neuvádí 7. 10. 2026")
t_k = K.read_text(encoding="utf-8")
m42 = re.search(r"^\| \*\*42\*\* \|.*$", t_k, re.M)
k(m42 is not None and STARY not in m42.group(0), "řádek 42 už neuvádí 7. 10. 2026")
i220 = t_k.find("### 2.20 Nálezy z P27")
j220 = t_k.find("\n## 3. ", i220)
k(STARY not in t_k[i220:j220], "§2.20 už neuvádí 7. 10. 2026")
# cizí záznamy se NESMÍ změnit
for kotva, popis in (("| **41** |", "řádek 41"), ("| **40** |", "řádek 40"),
                     ("### 2.19 Nálezy z P26", "§2.19"),
                     ("## 56. P26 —", "HANDOFF §56")):
    k(kotva in (t_h if "HANDOFF" in popis else t_k), "%s zůstal" % popis)

print()
print("=" * 78)
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
for c in chyb:
    print("  CHYBA: %s" % c)
sys.exit(1 if chyb else 0)
