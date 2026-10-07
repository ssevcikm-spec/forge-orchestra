# -*- coding: utf-8 -*-
r"""N0.3 + fáze B — řádek session 38 do kroniky §1 (6.–7. 10. 2026).

PROČ SKRIPTEM: řádky tabulky §1 mají **přes 2000 znaků**, takže kotva z načteného
řádku by ho NAHRADILA zkráceným textem (omyl **194**, **206**). Bere se proto
z disku a vkládá ZA poslední řádek (37).

⚠ Počet omylů v řádku je **`—`**: uživatel 6. 10. 2026 rozhodl **„omyly nepiš“**
(viz řádek 37). Není to nula — je to **vědomě nevedený sloupec**, a proto se
**nepřičítá** do souhrnu §3.

Idempotentní, zapisuje bajty (LF).
"""
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
K = WS / "KRONIKA-PROJEKTU.md"

RADEK_38 = (
    "| **38** | **6.–7. 10. 2026** (21:1x UTC – 06:2x UTC) | "
    "**akční (conductor: N0.3 + fáze B)** | **Převzetí práce podle "
    "`PREDANI-ORCHESTRA-SESSION.md` a vady conductoru.** Uživatel zadal: ověř, "
    "proč selhává fronta úkolů → naměřeno ŽIVĚ: `/health` hlásilo `ok: true` přes "
    "22 h, ve kterých **selhalo 9 běhů v řadě**; ve frontě **49 osiřelých úloh** na "
    "jednu granuli; `entity.npc` spálil **8 běhů**, `entity.enemy` **5**; watchdog "
    "se **nikdy nemohl spustit** (prah 8 > strop 5 a počítal běhy jednoho úkolu). "
    "Provedeno: **N0.3** (`/health` hlásí stav CÍLE), **B2, B3a, B3b, B4, B5**, "
    "**první test rozhodovací logiky conductora** (skutečný `/tick` i `/report`), "
    "oprava čítače brány `C2: mutace N1` a dokumentace, která popírala nástroje | "
    "**Brány:** `g3` **49 bran / 0 bez čítače** · nové brány s mutačními důkazy: "
    "`test-health-cile` 21/0 + 11/0, `test-watchdog-granule` 17/0 + 11/0, "
    "`test-report-cooldown` 8/0 + 9/0, `test-listgames` 10/0 + 9/0, "
    "`test-grain-cap` 22/0 + 11/0, `test-tick-offline` **40 kontrol** + 8 vrat 17/0 · "
    "`validate-all` po pushi **1 → 0** problémů (`E. lokální kód = repo`) · "
    "commit **`598e207`** (25 souborů, +3714/−109) · deploy **#33 success** · "
    "**živě ověřeno:** `/health` → `targets[0]`: `main_ci: success (ci.yml #117)`, "
    "`forge.ok: false`, `selhani_v_rade: 20`; `/tick` → "
    "`watchdog: 2 ohlášeno (prah 3)`, `spusteno: 1 úloh` | **—** | "
    "**Nálezy a poučení:** (1) **brána, která nemá jak selhat, není brána** — "
    "watchdog měl prah NAD stropem a počítal špatnou entitu, takže se nikdy "
    "nespustil; pozná se to jen měřením („v `payload` není `eskalovano`“). "
    "(2) **`over-skilly.py` celou dobu hlásil „0 mrtvých cest“**, a přitom skill "
    "měl **24 odkazů na neexistující layout** (`orchestra/tools/`) — brána měřila "
    "jiný tvar cest, než jaký v dokumentu byl. (3) **VLASTNÍ PAST: málem jsem "
    "commitoval MUTANTA** — ve stageované verzi `index.ts` zůstalo `if (false) {` "
    "z mutačního testu (`_mutace.mutuj` ji měl vrátit; disk byl správně, index ne). "
    "Zachránila to kontrola **stageovaného blobu** na známé značky mutantů "
    "(`git show :soubor`), ne `git diff`. **Poučení: u repa, kde běží mutační testy, "
    "se před commitem kontroluje INDEX, ne pracovní strom.** "
    "(4) **Počet v názvu brány zestaral dvakrát** (3 → 6 → 8 vrat) — jméno, které "
    "tvrdí počet, je další místo, kde vzniká nepravda; název je proto bez počtu. "
    "**Co zůstává:** `/poll`, `/claim`, `/heartbeat`, `/tasks/cleanup` "
    "a `/roadmap/reset` handlerem netestuje žádný test; slepé místo `over-skilly`; "
    "fáze C a D |"
)

kontrol = 0
chyb = []


def k(ok: bool, popis: str) -> None:
    global kontrol
    kontrol += 1
    print(f"  {'OK  ' if ok else 'CHYBA'}  {popis}")
    if not ok:
        chyb.append(popis)


print("=" * 78)
print("Kronika §1 — řádek session 38 (N0.3 + fáze B conductoru)")
print("=" * 78)

puvodni = K.read_bytes()
text = puvodni.decode("utf-8")
radky = text.splitlines(keepends=True)
k("\r" not in text, "kronika má LF (zapisuje se bajty)")

if any(r.startswith("| **38** |") for r in radky):
    print("  OK    řádek 38 už v kronice je — nevkládám")
    kontrol += 1
else:
    i37 = next((n for n, r in enumerate(radky) if r.startswith("| **37** |")), None)
    k(i37 is not None, "kotva: řádek session 37")
    if i37 is not None:
        konec = "\n" if radky[i37].endswith("\n") else ""
        radky.insert(i37 + 1, RADEK_38 + konec)
        k(any(r.startswith("| **38** |") for r in radky), "řádek 38 vložen ZA řádek 37")

nove = "".join(radky).encode("utf-8")
if nove != puvodni:
    K.write_bytes(nove)
    print(f"  ZAPSÁNO: KRONIKA-PROJEKTU.md ({len(puvodni)} → {len(nove)} B)")
else:
    print("  beze změny")

zpet = K.read_bytes()
k(zpet == nove, "soubor na disku odpovídá zapsanému")
k(not zpet.startswith(b"\xef\xbb\xbf"), "kronika nemá BOM")
k(zpet.count(b"\r\n") == 0, "v kronize nejsou CRLF")
t2 = zpet.decode("utf-8")
k("| **38** |" in t2, "dokument obsahuje řádek 38")
k("watchdog: 2 ohlášeno (prah 3)" in t2, "řádek nese ŽIVÉ ověření watchdogu")
k("selhani_v_rade: 20" in t2, "řádek nese živé ověření /health")
k("598e207" in t2, "řádek jmenuje commit")
k("MUTANTA" in t2, "řádek vede vlastní past (mutant ve stagei)")

# Souhrn §3 se NEPŘEPOČÍTÁVÁ: řádek 38 omyly nevede (uživatel je nechce vést).
k("| **celkem** | **27 bloků, 35 sessions** | **208** | **181 = 87 %** | **54** |" in t2,
  "souhrn §3 zůstal (27 bloků / 35 sessions / 208) — řádek 38 omyly nevede")

print()
print("=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {len(chyb)} chyb")
print("=" * 78)
for c in chyb:
    print(f"  CHYBA: {c}")

sys.exit(1 if chyb else 0)
