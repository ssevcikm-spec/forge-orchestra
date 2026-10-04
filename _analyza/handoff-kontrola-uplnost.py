# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
"""Ověří, že přepisem HANDOFF.md NIC NEZMIZELO.

AGENTS.md: „Přepisuješ-li HANDOFF.md, nic nesmí zmizet. Handoff je jediné místo,
kde žijí otevřené body — jejich ztráta je nejdražší chyba předání. Po přepisu
vypiš, které body zůstaly, a ověř je (hledáním klíčových slov), ne pamětí."

Seznam níž je opsaný z PŮVODNÍHO handoffu (přečteného před přepisem) —
jsou to všechny identifikátory otevřených bodů a klíčové termíny.

Použití:  python _analyza\\handoff-kontrola-uplnost.py [cesta/k/HANDOFF.md]
          (cesta navíc je pro MUTAČNÍ TEST — ten potřebuje fixturu, ne živý
          dokument; bez argumentu se čte živý `HANDOFF.md`)
"""

import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ⚠ CESTA JE VOLITELNÁ — doplněno 2. 10. 2026 pro Úkol 4 zadání
# `ZADANI-OPRAVA-MERIDEL.md` („handoff úplnost: smaž z HANDOFF.md jednu kotvu").
# Bez toho by mutační test musel sáhnout na ŽIVÝ `HANDOFF.md` — a v témže
# workspace pracuje souběžná session (naměřeno). Fixtura je bezpečnější
# a měří TOTÉŽ: seznam klíčů je pevný, mění se jen dokument.
H = (pathlib.Path(sys.argv[1]) if len(sys.argv) > 1
     else pathlib.Path(_STANICE / 'HANDOFF.md'))
if not H.is_file():
    print("CHYBA: %s neexistuje — není co kontrolovat" % H)
    sys.exit(2)
text = H.read_text(encoding="utf-8")

# (kategorie, klíčový výraz, co to je)
KLICE = [
    # ── čeká na rozhodnutí uživatele ─────────────────────────────────────────
    ("rozhodnutí", "O3", "opravit vady conductoru (fáze B)"),
    ("rozhodnutí", "O10", "ST9 součástí fáze B"),
    ("rozhodnutí", "O5", "cesty v konfiguraci"),
    ("rozhodnutí", "O6", "vlastnictví souborů"),
    ("rozhodnutí", "O7", "druhá hra"),
    ("rozhodnutí", "O8", "způsob schvalování fází"),
    ("rozhodnutí", "O9", "NAZEV-REPA (vyřešeno)"),

    # ── otevřené technické body ──────────────────────────────────────────────
    ("technické", "N0.2", "brána na závislosti bran"),
    ("technické", "N0.3", "stav CI cílové hry v /health"),
    ("technické", "N12", "tři různé vision.test.mjs"),
    ("technické", "vision.test.mjs", "tři různé kopie"),
    ("technické", "Z8", "nehotové Z8/Z9"),
    ("technické", "Z9", "nehotové Z8/Z9"),
    ("technické", "migrace-schema.py", "citovaný neexistující soubor"),
    ("technické", "ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md", "27 untracked"),
    ("technické", "PLAN-SEPARACE-WORKSPACE.md", "plán k revizi"),
    ("technické", "N10", "tajemství nemají izolované ACL"),
    ("technické", "MAX_ATTEMPTS", "mrtvý kód (B5)"),
    ("technické", "B5", "komentáře :31, :233"),
    ("technické", "PLAN-ORCHESTRA-AI-AGENTI.md", "plán k revizi (N0–N5, R1–R15)"),
    ("technické", "CONVENTIONS.md", "pravidlo jazyka v šabloně (nehotovo)"),

    # ── fáze B/C/D ──────────────────────────────────────────────────────────
    ("fáze", "B1", "naposledy_selhalo místo updated_at"),
    ("fáze", "B2", "/report zapíše roadmapu"),
    ("fáze", "B3", "strop a watchdog na i_id"),
    ("fáze", "B4", "listGames fallback"),
    ("fáze", "C2", "test-eskalace.py opsaný watchdog"),
    ("fáze", "C3", "test agent.yml"),
    ("fáze", "C4", "spec.json chráněný"),
    ("fáze", "C5", "offline testy tří bran"),
    ("fáze", "D2", "drift z git ls-files"),
    ("fáze", "D3", "onboarding jako test"),
    ("fáze", "D4", "game_id a absolutní cesty"),
    ("fáze", "D5", "prepisy.json + forge.config.json"),
    ("fáze", "F0 hotová", "stav fází"),

    # ── nálezy z předchozích session, POŘÁD otevřené ────────────────────────
    ("nálezy", "N11", "tři mrtvé brány"),
    ("nálezy", "LGTM", "272 položek, agent-init"),
    ("nálezy", "agent-init", "razítka v jedné minutě"),
    ("nálezy", "worker", "role worker/judge, kterou kód nečte"),
    ("nálezy", "acceptance", "nečte žádný kód"),
    ("nálezy", "provides", "nečte žádný kód"),
    ("nálezy", "73,4", "orchestra je největší nájemník"),
    ("nálezy", "60,4", "podíl souborů"),
    ("nálezy", "80 v 59", "grep tool 0 vs Python walk 80"),
    ("nálezy", "verify-setup.py", "9 sourozeneckých složek"),
    ("nálezy", "6× CHYBI", "co by hlásil po separaci"),

    # ── deferred ────────────────────────────────────────────────────────────
    ("deferred", "Bootstrap objektů", "kdo vytváří objekty ve hře"),
    ("deferred", "main.json", "4 markery"),
    ("deferred", "sprites.json", "zastaralý template"),
    ("deferred", "green slime", "16 barev"),
    ("deferred", "480x270", "zavádějící resolution"),
    ("deferred", "blender", "krok v worker.mjs"),
    ("deferred", "FORGE_CMD", "mrtvý default"),
    ("deferred", "pc-domaci", "čeká na rozhodnutí o uzlu"),
    ("deferred", "kontaktní arch", "ruční fitness funkce"),
    ("deferred", "read_image", "ruční fitness funkce"),

    # ── tři visící PR ───────────────────────────────────────────────────────
    ("PR", "#28", "save.gd"),
    ("PR", "#29", "hud.gd"),
    ("PR", "#30", "mining.gd"),
    ("PR", "size_lines", "chybí u 13 z 18"),
    ("PR", "engine.shell", "čeká na ně"),

    # ── running state ───────────────────────────────────────────────────────
    ("stav", "3a2e691", "HEAD orchestra"),
    ("stav", "d0bf4f9", "HEAD hry"),
    ("stav", "oracle-frankfurt", "domácí uzel žije"),
    ("stav", "57,6", "pc-domaci offline hodin"),
    ("stav", "#141", "failed úloha entity.enemy"),

    # ── jak dovolat session ─────────────────────────────────────────────────
    ("session", "dsh-session-prehled.mjs", "rozlišení session"),
    ("session", "send_message", "umí jen podagenty"),
    ("session", "app.asar", "shim míří do neexistujícího bin.js"),
    ("session", "hl2-rozbal-session2.mjs", "multi-frame zstd"),
    ("session", "997", "rámců v session logu"),

    # ── omyly ───────────────────────────────────────────────────────────────
    ("omyly", "sim.crafting", "omyl 1 — size_lines patří jiné granuli"),
    ("omyly", "em-dash", "omyl 3 — mutace se tiše neprovedla"),
    ("omyly", "7cd67c66", "session analýzy"),
    ("omyly", "7db45275", "session jazyka"),
    ("omyly", "eb127abd", "session provedení"),

    # ── jazyk (bývalá §10) ──────────────────────────────────────────────────
    ("jazyk", "2 002", "nálezů v inventáři"),
    ("jazyk", "161", "souborů"),
    ("jazyk", "IMPLEMENTACE-HRANICE-JAZYKA.md", "plán Z1–Z8 (proveden)"),
    ("jazyk", "hl-neanglicky-v-kodu.py", "skener"),
    ("jazyk", "spec.json", "záměrně se nepřejmenovává"),

    # ── co už otevřené není ─────────────────────────────────────────────────
    ("uzavřené", "6d2a856", "zámek owns"),
    ("uzavřené", "3a2e691", "fáze A + D1"),
    ("uzavřené", "merged_by", "PR nesloučil robot"),
]

chybi = [(kat, k, co) for kat, k, co in KLICE if k not in text]
najdene = len(KLICE) - len(chybi)

print("=" * 78)
print("KONTROLA ÚPLNOSTI HANDOFFu — nic nesmí zmizet")
print("=" * 78)
print(f"  kontrolovaných klíčů: {len(KLICE)}")
print(f"  nalezených:           {najdene}")
print(f"  CHYBÍ:                {len(chybi)}")
print()

if chybi:
    for kat, k, co in chybi:
        print(f"  ✗ [{kat}] {k!r} — {co}")
    print()
    print("POZOR: chybějící bod = ztracený otevřený bod. Doplnit do HANDOFF.md!")
    sys.exit(1)

print("  VŠE OK — všech", len(KLICE), "bodů je v novém handoffu.")
sys.exit(0)
