
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
| **71** | **„S prázdným `CONVENTIONS.md` by se vešlo 12 z 21 granulí"** — skript to vypsal, ačkoli o řádek výš tvrdil, že se nevejde ani jedna (a sám jsem to uživateli tak řekl) | **Nebylo to 12.** Počítal jsem `zbytek - t_conv`, ale **`zbytek` UŽ `CONVENTIONS.md` obsahuje`** → „vlastní část" mi vyšla **4 175 t.** místo skutečných **335 t.** (rozdíl **12×**). A v hlavičce skriptu zůstala **stará proměnná** se stejným jménem, takže psala totéž špatné číslo | **Číslo si odporovalo s jiným řádkem téhož výstupu** — a to je vždy vada měření, ne „zajímavý výsledek". Odhalil to **`p19i-sonda2.py`** (nezávislý přepis téhož vzorce), ne moje pozornost. **Poučení: jedno jméno nesmí znamenat dvě veličiny** (`nejmensi_t` = s pevnou částí / bez ní) |
