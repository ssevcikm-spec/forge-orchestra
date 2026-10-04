# Dodatečné měření po uzavření fáze A (1. 10. 2026, 14:30–14:45 UTC)

> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Co to je:** druhé kolo měření, které vzniklo z pokynu „nakonec změř".
Není to přepis prvního měření (13:35–14:10 UTC) — je to **jeho pokračování**
a je potřeba číst obojí. První měření je v `HLOUBKOVA-MERENI.md`.

**Proč se měřilo znovu:** mezi prvním a druhým měřením se **změnil kód**
(jiná session dokončila fázi A a D1) i **stav orchestra** — a přesně proto
zadání žádá měřit, ne věřit.

---

## 1. Co se změnilo v kódu (a je hotové)

| Co | Stav před (HEAD `525d45b`) | Stav teď (pracovní strom) |
|---|---|---|
| `validate-all.mjs` návratový kód | `exit 0` **vždy** (i při „✗ NALEZENO 3 PROBLÉMŮ") | `process.exitCode = chyb === 0 ? 0 : 1`; **naměřeno `exit 1`** při 4 nálezech |
| `validate-all.mjs` — kterou bránu volá | `tools/kontrola-schematu.py` (stará slepá kopie) | `repo/.forge/check-schema.py` (správná) |
| `tools/kontrola-schematu.py` | existoval, 305 řádků | **smazán** |
| `test-cooldown.py` | SQL **opsané**, `assert` 0×, `sys.exit` 0× → vždy `exit 0` | SQL **ze zdrojáku**, `assert` i `sys.exit`; **naměřeno `exit 1`** (našel S12) |
| `release.yml` v šabloně | `NAZEV-REPA` **3×** (nefunkční odkaz v každé nové hře) | `${{ github.repository }}` na obou místech, `NAZEV-REPA` **0×** |

**Ověřeno spuštěním** (ne čtením):

```
node orchestra\tools\validate-all.mjs     → „✗ NALEZENO 4 PROBLÉMŮ", exit 1
python orchestra\tools\test-cooldown.py   → „10 kontrol, 1 chyb", exit 1
                                             (ta 1 chyba JE S12 — správně červený test)
```

**A jedna věc, která se opravila v dokumentaci, ne v kódu:** `test-eskalace.py`
**není** vada „lže zelenou" — má `sys.exit(0 if vse_ok else 1)` (`:121`).
Tvrzení se šířilo plánem i handoffem; opraveno.

---

## 2. Co jsem dodělal já (a co to změnilo)

### 2.1 Mrtvé odkazy na smazaný `kontrola-schematu.py` (4 soubory)

```
orchestra/repo/.forge/check-schema.py   :22-23   → python .forge/check-schema.py
games/uo-shadows/.forge/check-schema.py :22-23   → totéž (test hlídá shodný hash!)
games/uo-shadows/scripts/level.gd       :24,107  → odkaz na .forge/check-schema.py
orchestra/tools/validate-all.mjs        :182     → komentář „rozpor je očekávaný stav"
                                                   (už není — schéma je rozhodnuté)
```

**Navíc jsem ze šablony odstranil všechna tvrzení o konkrétní hře** (testovací
otázka z `AGENTS.md`: *„Platí to i pro projekt, který ještě neexistuje?"*):

```
orchestra/repo/.forge/check-schema.py:
   před:  „naměřeno 30. 9. 2026 (hra `uo-shadows`)", „scripts/level.gd", „scripts/world.gd"
   teď:   „naměřeno 30. 9. 2026 na hře", „vstupní bod vykreslování", „druhá logika světa"
          + nový odstavec „KONKRÉTNÍ DŮKAZ PATŘÍ HŘE, NE SEM"
   naměřeno: `uo-shadows` v šabloně 12× → 0×
```

**Kontrola po každé editaci** (protože test hlídá shodný hash obou kopií):

```
sablona sha256 e9d38f0647304ef8  24039 B
hra     sha256 e9d38f0647304ef8  24039 B   → SHODNÉ
python games/uo-shadows/.forge/check-schema.py .   → „Schéma je v souladu", exit 0
```

### 2.2 Past, na kterou jsem u toho narazil (a je poučná)

Editor zapsal **CRLF a zahodil BOM** u souborů, které projekt drží na LF:

```
                        HEAD            disk po editaci      po opravě
level.gd                BOM ANO, LF     BOM ne,  LF   →      BOM ANO, LF
check-schema.py (obě)   BOM ne,  LF     BOM ne,  CRLF →      BOM ne,  LF
validate-all.mjs        BOM ne,  LF     BOM ne,  CRLF →      BOM ne,  LF
```

V `.gitattributes` jsou `*.py`, `*.mjs`, `*.gd` na `text eol=lf` — takže
**pracovní strom měl jinou podobu než zbytek repa**. Opraveno nástrojem
`_analyza/hl-konce-radku.py` (**zapisuje bajty**, ne text) a ověřeno
`_analyza/hl-bom.py`. **A druhá past téhož druhu:** `git show` přes PowerShell
(`> soubor`) zapíše **UTF-16LE** — BOM pak vypadá, že se „nezměnil".
Číst gitu výstup v Pythonu s `shell=True` (git.cmd je batch).

### 2.3 `done` v roadmapě srovnáno se stavem v D1 (8 granul)

**Stav před:** soubor 18 granul, `done: true` u **2**; D1 14 řádků, `done` u **10**.
To je nebezpečné, protože `/roadmap/reset` staví stav **ze souboru** — 8 granul
by se po resetu vydalo znovu (zachránila by je jen křehká cesta „párování PR
podle názvu").

**Stav po** (`_analyza/srovnej-roadmap-done.py --provest`):

```
core.skills      done_note: „PR #24 sloučené 30. 9."
world.map        done_note: „PR #21 sloučené 30. 9."
entity.player    done_note: „PR #25 sloučené 1. 10."
sim.combat       done_note: „PR #26 sloučené 1. 10."
sim.economy      done_note: „PR #22 sloučené 30. 9."
sim.assist       done_note: „PR #27 sloučené 1. 10."
persist.save     done_note: „POZOR: v D1 hotovo (task 139), ale PR NENÍ sloučené…"
ui.hud           done_note: „POZOR: v D1 hotovo (task 140), ale PR NENÍ sloučené…"
```

**Kontrola:** `json.loads` OK, **18 granul, `done: true` 10** (shodné s D1),
`lint-roadmapa.py` → hledané vady 1–4: **žádné**.

**A past, kterou jsem u toho udělal já:** první verze skriptu hledala „konec
objektu granule" jako první řádek `}` — a **rozvrátila soubor** (211 řádků
místo 195, neplatné JSON). Zachránila to záloha
`_analyza/zaloha-roadmap-pred-sync.json` (16270 B, `sha256 7a2628b39bd7`).
Nová verze vkládá **přímo za `depends_on`**, po každé granulaci **znovu
parsuje** a při chybě nezapisuje. **Poučení je v hlavičce skriptu.**

---

## 3. Dvě nové vady — naměřené dnes, ne odvozené

### 3.1 S29 — úkol je „hotový", ale práce není v `main`

```
scripts/save.gd  v main NENÍ      (git ls-files scripts → 18 souborů, ani jeden z nich)
scripts/hud.gd   v main NENÍ
a přesto: task #139 a #140 jsou v D1 'done', roadmap je vede jako 'done'

PR #28 (persist.save)  open, +90/−0,  mergeable_state=clean, NESLOUČENÝ
PR #29 (ui.hud)        open, +76/−0,  mergeable_state=clean, NESLOUČENÝ
   komentář v obou: „🤖 Automatické sloučení neproběhlo (pravidla: 0, CI: )"

PROČ: granule persist.save a ui.hud NEMAJÍ size_lines
      → maxLinesOf() vrátí výchozích 60 (index.ts:149-153)
      → gate správně zamítl: add+del > max_lines (agent.yml:646)
```

**Rozdíl proti S24:** S24 je odvozené z kódu („timeout se jen okomentuje").
**S29 je naměřené**: stav `done` a stav `main` se rozešly a nikdo to nevidí.

### 3.2 S30 — granule, na kterou nikdo nepočká

```
granule bez řádku v D1 a bez done:true v souboru: 4
   core.attributes   ← MÁ sloučené PR #19, ale řádek v D1 někdo smazal
   entity.item       ← MÁ sloučené PR #20, řádek v D1 smazán
   sim.offline       ← nikdy neběžela
   engine.shell      ← nikdy neběžela

zavislosti čekající na tyhle granule: 15
   (entity.player, sim.combat, sim.crafting, sim.economy, entity.npc,
    entity.enemy, sim.assist, persist.save, ui.hud, engine.shell)

zachranná cesta (index.ts:502-503, párování PR podle TITULKU):
   core.attributes → ZACHYTÍ (titulkyZachrana=true)
   entity.item     → ZACHYTÍ
   ALE: funguje jen pro PR v POSLEDNÍCH 100 ZAVŘENÝCH
   dnes: zavřených PR celkem 27, nejstarší #1 → limit je daleko
```

**Tedy:** dnes to funguje, ale **ne díky databázi — díky shodě titulků PR**.
U aktivnější hry (100+ PR) by `core.attributes` a `entity.item` přestaly
existovat a **10 granul by čekalo navěky** — a vypadalo by to jako
„čeká na závislosti", což je legitimní stav.

---

## 4. Stav, ve kterém se práce předává (14:45 UTC)

```
orchestra (git):  M README.md · M repo/.forge/workflows/release.yml · D tools/kontrola-schematu.py
                  M tools/test-cooldown.py · M tools/validate-all.mjs
                  + MOJE: M repo/.forge/check-schema.py · M tools/validate-all.mjs (komentář)
hra (git):        M .forge/check-schema.py · M .forge/roadmap.json · M scripts/level.gd
conductor:        ok: true, ready: 4, running: 0, games: 1
                  4 úlohy ready, všechny v cooldownu (nejbližší dispatch 16:10:54 UTC)
                  /failed prázdné
uzly:             oracle-frankfurt žije (naposledy před 1 min), pc-domaci 42,5 h offline
PR:               29 celkem, 24 sloučených, 2 otevřené (#28, #29), 0 zavřených bez sloučení
CI hry na main:   19 z posledních 20 success
```

**Nic jsem necommitoval ani nepushoval** — v obou repech jsou jen změny
v pracovním stromě a čekají na tvé vyžádání (`AGENTS.md`).
