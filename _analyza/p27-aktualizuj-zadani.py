# -*- coding: utf-8 -*-
r"""P27 (dodatek) — AKTUALIZACE ZADÁNÍ pro P28: rozhodnutí, nasazení stropu, stav.

Použití: python _analyza/p27-aktualizuj-zadani.py <sha_hry>
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
Z = WS / "NEXT-SESSION-INSTRUKCE.md"
HRA = sys.argv[1] if len(sys.argv) > 1 else "bc51e46"
HEAD_ORCH = sys.argv[2] if len(sys.argv) > 2 else "b668910"

kontrol = 0
chyb = []


def k(ok, popis):
    global kontrol
    kontrol += 1
    print("  %s  %s" % ("OK  " if ok else "CHYBA", popis))
    if not ok:
        chyb.append(popis)


def vymen(dvojice, popis):
    t = Z.read_text(encoding="utf-8")
    for stary, novy in dvojice:
        n = t.count(stary)
        if n != 1:
            k(False, "%s: kotva %d× (musí 1×): %r" % (popis, n, stary[:70]))
            continue
        t = t.replace(stary, novy, 1)
        print("      OK %r" % stary[:60])
    Z.write_bytes(t.encode("utf-8"))
    k(True, "%s: zapsáno" % popis)


vymen([
    # ── hlavička: živý stav ────────────────────────────────────────────────
    ("`uo-shadows` = **`af6abd8`**", "`uo-shadows` = **`%s`**" % HRA),
    ("`forge-orchestra` = `38ff4ad` · `uo-shadows` = `af6abd8`",
     "`forge-orchestra` = `%s` · `uo-shadows` = `%s`" % (HEAD_ORCH, HRA)),
    ("Práce P27 je **COMMITNUTÁ** (`1bdc982`, `649ca9b`, `77ade9f`) a **NEPUSHNUTÁ**;",
     "Práce P27 je **COMMITNUTÁ I PUSHNUTÁ** (`1bdc982`, `649ca9b`, `77ade9f`, `38ff4ad`,\n"
     "`8f80b0d`, `a8ff943`, `07169c7`, `b668910`);"),
    # ── §2.2: co je hotové a co zbývá ──────────────────────────────────────
    ("| **B4** | **Zapnout strop na granuli** (`GRAIN_MAX_RUNS = \"5\"`) | `HANDOFF.md` §46 | Až bude vidět, že watchdog stačí. ⚠ Změna chování živé služby = nasazení |",
     "| ~~**B4**~~ | **✅ HOTOVO 8. 10. 2026:** strop granulí **ZAPNUT na 8** a **NASAZEN** (`07169c7` → `deploy.yml` #34 `success`) | `HANDOFF.md` §58, `PLAN…` §6 (B3) | **Proč 8:** víc než `MAX_ATTEMPTS` (5), `ESCALATE_AFTER` (3) pod ním. **Mez acceptance:** zastavení se projeví až u granule s ≥ 8 běhy (dnes 0 blokovaných) |"),
    ("| **O1** | **Rozhodnout `O3`, `O10`, `O5–O8`** | `PLAN-ROZVOJ-ORCHESTRA.md` §6 | Jsou to **rozhodnutí**, ne kód.",
     "| ~~**O1**~~ | **✅ ROZHODNUTO 8. 10. 2026 (uživatel):** `O5`, `O6`, `O10` = souhlas · `O8` = celek, ale postupně · `O9` hotovo a ověřeno · `O3` zodpovězeno · `O7` **odloženo** (žádná druhá hra neexistuje) | `PLAN-ROZVOJ-ORCHESTRA.md` §6 + **§6.1** | Zapsáno i s důvody; nic k rozhodování nezbývá |"),
    # ── §5: měřená východiska ──────────────────────────────────────────────
    ("git -C E:\\Workspaces\\uo-shadows      rev-parse --short HEAD            -> af6abd8",
     "git -C E:\\Workspaces\\uo-shadows      rev-parse --short HEAD            -> %s" % HRA),
    ("node tools\\test-tick-offline.mjs            -> 205/0\npython _analyza\\tick-mutace.py              -> 20 vrat, 41/0",
     "node tools\\test-tick-offline.mjs            -> 205/0\npython _analyza\\tick-mutace.py              -> 20 vrat, 41/0\npython tools\\test-grain-cap.py              -> 22/0 (INFO: strop ZAPNUTY na 8)\nnode _analyza\\p27-over-nasazeni.mjs         -> deploy.yml #34 success na 07169c7"),
], "ZADÁNÍ: rozhodnutí a měření")

# ── stavový řádek (přepis celého odstavce) ─────────────────────────────────
t = Z.read_text(encoding="utf-8")
i = t.find("**STAVOVÝ ŘÁDEK")
if i < 0:
    k(False, "stavový řádek nenalezen")
else:
    novy = (
        f"**STAVOVÝ ŘÁDEK (8. 10. 2026, ~15:4x +02:00):** orchestra **`{HEAD_ORCH}`**\n"
        f"= `origin/main` (**PUSHNUTO**, 0 nepushnutých) · hra **`{HRA}`** (cizí session,\n"
        "píše průběžně; P27 do ní nezapsala) · živá služba `/health` →\n"
        "`ok=true ready=1 running=0 games=1`, **strop granulí ZAPNUTÝ na 8**\n"
        "(`deploy.yml` #34 `success`) · brány: `g3` **49 bran / 1 nedeklarovaný exit =\n"
        "CIZÍ skill `dialog-s-uzivatelem` (neplatný YAML, mimo repo)**,\n"
        "`validate-all` → **VŠE V POŘÁDKU** (nad čerstvým inventářem),\n"
        "`test-tick-offline` **205/0**, `p27-a --plne` **133/0**, `p27-b` **27/0**,\n"
        "`over-skilly` **0 mrtvých cest** (3 cesty jiného projektu = poznámka) ·\n"
        "inventář **čerstvý** (přegenerován jako poslední krok) · **rozhodnutí uživatele**\n"
        "zapsána v `PLAN-ROZVOJ-ORCHESTRA.md` §6 (+ §6.1 = rozsah brány `over-skilly`).\n"
    )
    Z.write_bytes((t[:i] + novy).encode("utf-8"))
    k(True, "stavový řádek přepsán")

t2 = Z.read_text(encoding="utf-8")
k("%s" % HEAD_ORCH in t2 and "%s" % HRA in t2, "zadání tvrdí oba živé HEADy")
k("ZAPNUT na 8" in t2 or "ZAPNUTÝ na 8" in t2, "zadání nese strop 8")
k("PUSHNUTO" in t2, "zadání nese, že je pushnuto")
k("ROZHODNUTO 8. 10. 2026" in t2, "zadání nese rozhodnutí")
b = Z.read_bytes()
k(b.count(b"\r\n") == 0 and not b.startswith(b"\xef\xbb\xbf"), "zadání: LF a bez BOM")

print()
print("=" * 78)
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
for c in chyb:
    print("  CHYBA: %s" % c)
sys.exit(1 if chyb else 0)
