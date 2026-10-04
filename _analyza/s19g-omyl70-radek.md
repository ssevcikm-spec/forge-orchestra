
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
| **70** | **„`deploy B1` je červená, takže se deploy nepovedl"** — brána vypsala dvě `CHYBA` | **Obě byly falešné poplachy.** Měřidlo porovnalo zadaný commit s **HEADem `main`** a hledalo deploy na **HEADu** — ale `deploy.yml` má filtr **`paths: conductor/**`**, takže commit `1e3925e` (mění jen `tools/`) **deploy správně nemá**. Nasazený kód conductora je **`7c11b2d`** (deploy **#32 success**) a **je nasazený dál** | **Tatáž vada jako H8** (`validate-all.mjs --jen hra`): **měřidlo se ptalo na jinou věc, než která rozhoduje.** Opraveno podle vzoru, který v projektu **už byl** — `a3-kontrola.mjs:43–52` se ptá na **poslední změnu `conductor/**`**. Ověřeno **oběma směry**: `7c11b2d` → `✓ VŠE V POŘÁDKU`; `1e3925e` → správně „žádný deploy na tom commitu". **Kdo by té bráně věřil, šel by opravovat funkční deploy** |
