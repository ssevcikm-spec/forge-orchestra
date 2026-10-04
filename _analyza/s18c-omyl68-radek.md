
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
| **68** | **„Skript na vložení §18 je hotový"** — spustil jsem ho **dvakrát** a `HANDOFF.md` vyskočil z **202 443 B na 234 375 B**; oddíly `8g` i `18` byly v souboru **DVAKRÁT** | Musel jsem **vrátit soubor ze zálohy** (`_analyza\handoff-pred-s18.md`, 174 971 B) a vložit ho **jednou**. Skript byl **append bez kontroly, co v souboru už je** | Napsal jsem „vkládací" skript a **netestoval jsem ho podruhé** — přitom `overovani` §7.3 říká přesně tohle („nástroj, který jen přidá řádky, umí rozvrátit soubor"). Zachránila to **záloha kopií**, ne kontrola. **Opraveno:** skript teď před zápisem **odmítne běh, když kotva v souboru už je** (`exit 2`) |
