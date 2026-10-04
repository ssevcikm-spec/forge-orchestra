
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
| **L13** | **Vkládáš-li text, který sám sebe zmiňuje, nesmí být kotva hledaná v TOMTÉMŽ textu** — jinak se vloží dvakrát | naměřeno 2. 10. 2026 (omyl **68**): skript vkládal §18.16 „před nadpis `## 18.`", ale ta kotva je i **uvnitř nově vloženého textu** (odkaz „§18.15") → po prvním vložení se posunula a druhá náhrada přidala oddíl **znovu**; `HANDOFF.md` měl `## 18.` **3×** a `### 8g.` **2×**. Předtím **dvojitý append** nafoukl soubor z 202 443 B na 234 375 B. **Řešení:** hledej kotvu **v původním souboru** a skládej **spojením řetězců**, ne dalším hledáním po zápisu; a měj **zálohu kopií** (`overovani` §2.1) | `HANDOFF.md` §18.16, `_analyza\s18d-sestav-handoff.py` |
