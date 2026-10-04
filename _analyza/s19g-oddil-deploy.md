
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
### 19.2 Vada měřidla nalezená AŽ TÍM, že push prošel — `f3-over-deploy.mjs`

**Co se stalo:** po pushi obou repů spadla brána `deploy B1` v `g3-brany.py`
a vypsala **dvě `CHYBA`**:

```
  GitHub main = 1e3925e2c  (kontrola diakritiky: doplnit dalsich 14 souboru …)
  CHYBA GitHub main = očekávaný commit  — 1e3925e2c vs 7c11b2d
  CHYBA deploy běžel na tomto commitu  — na 1e3925e2c žádný deploy — push nezměnil conductor/**?
```

**Obě hlášky byly falešné poplachy na SPRÁVNÉM stavu** — a je to **tatáž vada,
kterou tahle session už jednou našla** (nález **H8** u brány `check-schema`):
**měřidlo se ptalo na jinou věc, než která rozhoduje.**

| Co měřidlo dělalo | Co dělat MÁ |
|---|---|
| porovnalo `cekany` (= commit, na kterém má běžet deploy) s **HEADem `main`** | ptát se na **poslední změnu `conductor/**`** — protože `deploy.yml` má filtr **`paths: conductor/**`** |
| hledalo deploy na **HEADu `main`** | hledat deploy na **poslední změně `conductor/**`** |

**Proč to je vada a ne kosmetika:** commit `1e3925e` mění **jen
`tools/kontrola-diakritiky.py`** → deploy **správně neběžel**. Nasazený kód
conductora je **`7c11b2d`** (deploy **#32**, `success`) a **je pořád pravda, že
je nasazený**. Měřidlo to hlásilo jako dvě chyby — a **kdo by mu věřil, šel by
„opravovat" deploy, který je v pořádku.**

**Jak se to opravilo:** podle vzoru, který v projektu **už existuje** —
`a3-kontrola.mjs:43–52` se ptá přesně takhle:

```js
const zmenaConductoru = await gh(`/repos/${REPO}/commits?path=conductor/src/index.ts&per_page=1`);
const shaConductoru = zmenaConductoru[0]?.sha;
const naCommitu = nas.find((r) => r.head_sha === shaConductoru);
```

a **navíc** se ověří původní smysl parametru: *„běžel deploy na TOM commitu,
který jsem zadal?"*

**Ověřeno po opravě (oba směry — jinak by to bylo jen tvrzení):**

| Volání | Výsledek |
|---|---|
| `f3-over-deploy.mjs 7c11b2d` (poslední změna `conductor/**`) | **`✓ VŠE V POŘÁDKU`**, `exit 0` — „deploy běžel na zadaném commitu 7c11b2d — #32 success" |
| `f3-over-deploy.mjs 1e3925e` (HEAD, mění jen `tools/`) | `kód conductora z main JE nasazený` ✅, ale **`CHYBA deploy běžel na zadaném commitu 1e3925e — žádný deploy na tom commitu`** — a **to je správně**: na tom commitu deploy neběžel a běžet neměl |

> **⚠ Poučení (a je to po druhé v téhle session):** brána, která se ptá na
> **HEAD** místo na **to, co rozhoduje**, vyrobí **falešný nález o správném
> systému**. U `check-schema` to bylo `--jen` (neexistující přepínač), tady
> `paths: conductor/**`. **Společný podpis: měřidlo porovnává dvě věci, které
> spolu nesouvisí, a obě vypadají jako měření.** Oprava není „vypnout bránu",
> ale **ptát se na správnou veličinu.**
