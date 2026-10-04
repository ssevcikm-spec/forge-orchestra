
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
### 18.16 Vlastní omyl, který vznikl AŽ ZÁPISEM — dvojité vložení oddílů

**Co se stalo:** skript `_analyza\s18-zapis-handoff.py` vkládá oddíly **appendem**.
Spustil jsem ho **dvakrát** (jednou pro §18 + §8g, podruhé pro doplněk) — a
`HANDOFF.md` vyskočil z **202 443 B na 234 375 B**. Oddíly `8g` i `18` byly
v souboru **dvakrát**. Naměřeno: hledání kotvy `## 18. Ov` → **2×**.

**Jak se to spravilo:** vrátil jsem soubor **ze zálohy kopií**
(`_analyza\handoff-pred-s18.md`, 174 971 B — záloha vznikla **před** prvním
zápisem) a vložil oddíly **jednou**. Ověřeno: každá kotva **1×**
(`### 8g. Omyly`, `## 18. Ov`, `### 18.15 Vada`, omyl `67`),
`handoff-kontrola-uplnost.py` → **83/83**, `kronika-kontrola.py` → `exit 0`.

**Jak se to opravilo (aby se to nemohlo stát znovu):** skript má teď
**pojistku PŘED zápisem** — pro každý vkládaný oddíl zkontroluje, jestli jeho
kotva v `HANDOFF.md` **už není**, a když ano, **skončí `exit 2`** s návodem
vrátit soubor ze zálohy.

> **⚠ Proč to sem patří a není to detail:** je to **třetí** případ téhož vzoru
> v jedné session — **nástroj, který mění soubor, musí ověřit VÝSTUP, ne
> návratovou hodnotu** (`overovani` §7.3: „nástroj, který »jen přidá řádky«, umí
> rozvrátit soubor"). A **zachránila to záloha kopií**, ne kontrola — což je
> přesně to, co `overovani` §2.1 předepisuje („zálohuj kopií, ne prevencí
> gitu"). **Bez té zálohy by se dvě kopie oddílů musely pracně odstranit ručně**
> a hrozilo, že se smaže i něco jiného.
