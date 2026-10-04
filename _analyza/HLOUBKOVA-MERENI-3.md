# Třetí kolo měření — „stav, který si systém hlásí sám"

> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Měřeno:** 2. 10. 2026, 05:39–05:45 UTC (07:39–07:45 SELČ).
**Kdo:** session, která orchestra nepsala ani neopravovala (druhé kolo hloubkové analýzy).
**Co to je:** surová naměřená čísla s příkazy. Interpretace je ve
`ANALYZA-HLOUBKOVA-ORCHESTRA-2.md`, tady jsou jen podklady.

**Tři úrovně důkazu** (podle `hlouchkova-analyza` §2): *(1) přečtu* → *(2) spustím
izolovaně* → *(3) spustím v provozu*. U každého čísla je uvedeno, které úrovně
dosahuje. **Nic tady není úroveň 1 vydávaná za úroveň 3.**

---

## 0. Rámec — bod v čase

```
2. 10. 2026  07:39:30 SELČ = 05:39:30 UTC

orchestra        HEAD 3a2e691e8e030391325239539f64e378560cb649
                 ("Oprava slepých bran a odvození odkazu z názvu repa (fáze A + D1)")
                 větev main · pracovní strom ČISTÝ · 1 commit před origin/main

games/uo-shadows HEAD d0bf4f9126b4a9e54d7cb8d534119428240927bf
                 ("Srovnání roadmapy se stavem D1, obecnost brány a mrtvé odkazy")
                 větev main · pracovní strom ČISTÝ · 1 commit před origin/main
                 origin/main = 807803ec5095203b96e592c752764efa4e846aa3
```

**Příkaz:** `orchestra\tools\git.cmd -C <repo> rev-parse HEAD` (git přes
`git.cmd` — schannel v PowerShellu padá).

⚠ **Past, kterou jsem málem zopakoval:** `git status` z kořene workspace vrátí
`fatal: not a git repository` — workspace **není repo**, jsou tu **dva klony**
(`AGENTS.md`, HANDOFF §9.1). Proto se všechny git příkazy volají s `-C`.

**Kód se mezi měřeními nezměnil** — ověřeno `git status --porcelain` → prázdný
v obou repech na začátku i na konci měření.

---

## 1. Živý stav conductora

**Příkaz:** `node _analyza\hl2-live.mjs` (Node `fetch`; TLS z PowerShellu na téhle
stanici nefunguje). Secret se načítá z `orchestra\.env` a **nevypisuje se**.

| Endpoint | Status | Odpověď (05:40:21 UTC) |
|---|---|---|
| `/health` | 200 (veřejný) | `ok:true, ready:2, running:0, games:1` |
| `/games` | 200 | 1 hra: `uo-shadows`, `active:1` |
| `/roadmap` | 200 | **14 řádků**, z toho **11 `done`** |
| `/failed` | 200 | **1 úloha** (task #141) |
| `/queue` | 200 | 51 úloh: `ready:2, done:11, failed:1, blocked:37` |
| `/workers` | 200 | `oracle-frankfurt` (před 1 min), `pc-domaci` (**3457 min = 57,6 h** offline) |

**Uzly:** `oracle-frankfurt` živý, `pc-domaci` **57,6 h offline**.
*(První kolo 1. 10. 14:45 UTC naměřilo 42,5 h — uzel se tedy nevrátil a od té
doby je offline o dalších 15,1 h víc.)*

**Poznámka k číslům:** `/queue` vrací **51** řádků, ale `/roadmap` jen **14** —
jsou to **různé tabulky** (`tasks` vs. `roadmap`) a **různé čítače téhož jména
„úloha"**. Kdo je zamění, dostane rozpor, který neexistuje (past z `AGENTS.md`).

---

## 2. Porovnání roadmap.json × D1 × git

**Příkaz:** `node _analyza\hl2-d1-snapshot.mjs`
(data zamražena do `_analyza\hl2-d1-snapshot.json`)

```
D1 /roadmap:              14 řádků, 11 done
roadmap.json (soubor):    18 granul, 10 done:true
```

### 2.1 Rozchod souboru a D1 — **jeden**

| granule | soubor | D1 | shoda |
|---|---|---|---|
| `sim.mining` | `ne` (chybí `done`) | **`done`** | **<<< ROZCHOD** |
| ostatních 17 | — | — | ok |

`sim.mining` je **nový rozchod**, který první kolo nevidělo: D1 ho vede jako
hotový (task #136), soubor o tom neví.

### 2.2 Granule bez řádku v D1 — **4** (potvrzeno)

`core.attributes`, `entity.item`, `sim.offline`, `engine.shell`

Dvě z nich (`core.attributes`, `entity.item`) **mají sloučené PR #19 a #20**
(měřeno níže) — řádek v D1 jim chybí.

### 2.3 D1 má navíc `core.skills` a `data.content` s `task_id: null`

V `/roadmap` mají `task_id: null` — tedy **řádek vznikl zápisem z `done:true`
v souboru** (`index.ts:601`, INSERT s `task_id = NULL`), ne vydáním úlohy.
To je **doložený otisk** cesty „soubor → D1".

---

## 3. S29 ověřeno znovu — a **je to teď 3 otevřené PR, ne 2**

**Příkaz:** `node _analyza\hl2-s29-s30.mjs` (GitHub API, detail PR)

```
origin/main/scripts:  9 .gd souborů
   assist.gd attributes.gd combat.gd economy.gd game.gd
   item.gd level.gd player.gd skills.gd

PR celkem (/pulls?state=all):  30
   otevřené: 3 | sloučené: 24 | zavřené bez sloučení: 3
```

### 3.1 Tři otevřené PR — všechny „clean", všechny nesloučené

| PR | větev | soubor | ± | `mergeable_state` | `merged_at` |
|---|---|---|---|---|---|
| **#28** | `forge/task-139` | `scripts/save.gd` (+`save.gd.uid`) | +91/−0 | `clean` | **null** |
| **#29** | `forge/task-140` | `scripts/hud.gd` (+`hud.gd.uid`) | +77/−0 | `clean` | **null** |
| **#30** | `forge/task-136` | `scripts/mining.gd` (+`mining.gd.uid`) | +67/−0 | `clean` | **null** |

**`scripts/save.gd`, `scripts/hud.gd` ani `scripts/mining.gd` v `origin/main`
NEJSOU** — měřeno `git ls-tree -r origin/main -- scripts/` → 9 souborů, ani jeden
z nich.

**Co to znamená:** `/roadmap` vede `sim.mining` jako **`done`** (task #136)
a `/queue` vede **#136** jako `done` — a přitom **práce není v `main`** a PR #30
je otevřený. **S29 se rozšířila z 2 granul na 3** mezi 1. 10. 14:45 a 2. 10. 05:44.

### 3.2 `merged_by` — potvrzeno, že slučoval člověk

Posledních 12 sloučených PR, `merged_by` **z detailu** (seznam vrací `null`):

```
#27 2026-10-01T10:09:45Z by=ssevcikm-spec
#26 2026-10-01T10:08:51Z by=ssevcikm-spec
#25 2026-10-01T04:24:41Z by=ssevcikm-spec
#24 2026-09-30T22:41:01Z by=ssevcikm-spec
#22 2026-09-30T16:20:16Z by=ssevcikm-spec
#21 2026-09-30T16:19:32Z by=ssevcikm-spec
#20 2026-09-30T15:51:45Z by=ssevcikm-spec
#19 2026-09-30T15:50:49Z by=ssevcikm-spec
```

**Všech 8 kontrolovaných má `merged_by` = člověk.** Tvrzení „PR se slučují samy"
je **vyvráceno i v druhém kole** — ale pozor, to **neznamená, že auto-merge
nefunguje**; znamená to, že u těchhle osmi **neprošla pravidla** (a tedy je
sloučil člověk ručně).

---

## 4. Řetěz, kterým vzniká „hotovo bez práce" — čten z KÓDU

**Tohle je jádro druhého kola.** Není to odvozené z chování — je to **přečtené
v kódu** a **doložené daty** (tři otevřené PR + tři `done` v D1).

### 4.1 `agent.yml:557-565` — report `success` PŘED rozhodnutím o sloučení

```yaml
557:      - name: Report do conductora
560:        continue-on-error: true
565:        run: node .forge/report.mjs success "PR vytvoren" "${{ steps.pr.outputs.pull-request-url }}"
```

**Krok posílá `success` vždy, když vznikl PR** — bez ohledu na to, jestli se
smí sloučit. Job `auto-merge` začíná až na **ř. 580** a je to **samostatný job**
(`needs: [agent, pull-request]`).

### 4.2 `agent.yml:642-645` — gate jen zapíše `ok=0`, ale **neskončí chybou**

```yaml
642:          if [ $((add + del)) -gt ${{ inputs.max_lines }} ]; then
643:            echo "!! velká změna ($((add + del)) řádků, limit ${{ inputs.max_lines }})"; ok=0
644:          fi
645:          echo "ok=$ok" >> "$GITHUB_OUTPUT"
```

**Následuje `exit 0`** — job `auto-merge` je zelený i když se nesloučilo.

### 4.3 `agent.yml:683-691` — když pravidla neprojdou, **jen komentář**

```yaml
- name: Když pravidla neprošla – nechá se k ruční kontrole
  if: steps.gate.outputs.ok != '1' || steps.ci.outputs.ci != 'ok'
  run: gh pr comment "$PR" --body "🤖 Automatické sloučení neproběhlo …"
```

**Žádný `exit 1`.** Celý workflow tedy skončí **`success`** — a to je vstup do
dalšího kroku.

### 4.4 `index.ts:365-390` — conductor se ptá na `conclusion`, ne na `merged_at`

```ts
365:    const ok = run.conclusion === "success";
...
370:        const prs = await github(env, repo, `/pulls?head=${owner}:forge/task-${row.task_id}&state=all`);
371:        prUrl = prs?.[0]?.html_url ?? null;
372:        // `run.status === completed` znamená, že doběhl CELÝ workflow – tedy
373:        // i krok automatického sloučení. Stav mergnutí je proto v tuhle chvíli
374:        // už konečný a dá se věřit.
375:        merged = Boolean(prs?.[0]?.merged_at);
...
385:    if (ok) {
386:      await env.DB.prepare("UPDATE tasks SET status='done', updated_at=datetime('now') WHERE id=?")
387:        .bind(row.task_id).run();
388:      await env.DB.prepare(
389:        "UPDATE roadmap SET status='done', updated_at=datetime('now') WHERE task_id=?",
390:      ).bind(row.task_id).run().catch(() => undefined);
```

**Tři věci, které jsou tady vidět a které nikdo neporovnává:**

1. **`merged` se načte (ř. 375), ale nikde se nepoužije k rozhodnutí.** Ř. 385
   rozhoduje **jen podle `ok`** — `merged` je mrtvá hodnota. *(Ověřit: `merged`
   se v `index.ts` vyskytuje jen na ř. 367, 375 a v textu notifikace.)*
2. **Komentář na ř. 372–374 je nepravdivý** — tvrdí, že `completed` znamená
   doběhnutí celého workflow **včetně** auto-merge. Ale když gate nastaví `ok=0`,
   **krok sloučení se vůbec nespustí** (`if:` na ř. 677) a job přesto skončí
   `success`. `conclusion === "success"` tedy **není** důkaz o sloučení.
3. **Řádek v `roadmap` se zapíše podle `task_id`** (ř. 389), takže granule
   dostane `done` — a to i když je PR otevřený.

### 4.5 `index.ts:588-608` — soubor je autorita a **přebije realitu**

```ts
588:    for (const i of items) {
590:      if (i.done === true) {
591:        if (!done.has(key)) {
600:          await env.DB.prepare(
601:            `INSERT INTO roadmap (item_id, task_id, status, updated_at)
602:             VALUES (?, NULL, 'done', datetime('now'))
603:             ON CONFLICT(item_id) DO UPDATE SET status='done', updated_at=datetime('now')`,
604:          ).bind(key).run().catch(() => undefined);
605:          done.add(key);
606:        }
607:        continue;                        // ← granule se NIKDY nevydá
608:      }
```

`done: true` v souboru **bezpodmínečně** zapíše `done` do D1 a `continue` —
**nikde se neověřuje, že práce je v `main`.**

### 4.6 Důsledek doložený daty

Tři otevřené PR (#28 `save.gd`, #29 `hud.gd`, #30 `mining.gd`) a **tři `done`
v D1** pro tytéž granule:

| granule | task | PR | `merged_at` | D1 `/roadmap` |
|---|---|---|---|---|
| `persist.save` | #139 | #28 | **null** | **`done`** |
| `ui.hud` | #140 | #29 | **null** | **`done`** |
| `sim.mining` | #136 | #30 | **null** | **`done`** |

**A `roadmap.json` u dvou z nich dokonce varuje** (`:183`, `:194`):

```
"done_note": "POZOR: v D1 hotovo (task 139), ale PR NENÍ sloučené – práce není v main"
"done_note": "POZOR: v D1 hotovo (task 140), ale PR NENÍ sloučené – práce není v main"
```

**Tuhle poznámku nečte žádný kód** (měřeno: 0 čtenářů, zapisovatel je jednorázový
`_analyza\srovnej-roadmap-done.py`).

---

## 5. Vlastní měření — co v předchozích dokumentech NENÍ

### 5.1 `sim.mining` — rozchod, který první kolo nevidělo **(nové)**

```
D1 /roadmap:  uo-shadows/sim.mining  status=done  task_id=136  attempts=5
roadmap.json: sim.mining  done=CHYBÍ (pole `done` není)
/queue:       #136  status=done  attempts=5
PR #30:       forge/task-136, open, merged_at=null, +67/−0, mergeable_state=clean
origin/main:  scripts/mining.gd  NENÍ
```

**Tři místa tvrdí „hotovo", dvě nezávislé skutečnosti říkají „není".**

### 5.2 `size_lines` u všech tří nesloučených granul — hypotéza prvního kola SEDÍ

**Naměřeno (2. 10. 05:45 UTC, `json.load` nad `roadmap.json`):**

| granule | `size_lines` | PR | ± (bez `.uid`) | limit | prošlo? |
|---|---|---|---|---|---|
| `persist.save` | **není** | #28 | +90 (soubor `save.gd`) | 60 (výchozí) | **ne** (90 > 60) |
| `ui.hud` | **není** | #29 | +76 | 60 (výchozí) | **ne** (76 > 60) |
| `sim.mining` | **není** | #30 | +66 | 60 (výchozí) | **ne** (66 > 60) |

⚠ **Tady jsem se spletl já a měním vlastní tvrzení.** V prvním zápisu tohoto
měření jsem tvrdil, že `sim.mining` má `size_lines: "<= 100"` a že příčina
nesloučení u #30 tedy **není** velikost. **To bylo špatně** — spletl jsem si
granuli: `<= 100` mají v souboru **`sim.crafting`, `sim.offline` a `entity.enemy`**,
nikoli `sim.mining`. **Ověřeno znovu** `json.load` nad `games\uo-shadows\.forge\roadmap.json`
a výpisem celého objektu granule `sim.mining`.

**Správný závěr: hypotéza prvního kola (`M2:131-133`, `A:459`) SEDÍ pro všechny
tři granule** — ani jedna nemá `size_lines`, takže `maxLinesOf()` vrátí výchozích
**60** (`index.ts:149-153`) a gate správně zamítne (66/76/90 > 60).

**Co zůstává jako nález:** že **tři** granule nemají `size_lines` a že jde
o **systémovou mezeru**, ne o náhodu — `size_lines` chybí u **13 z 18** granul
(měřeno: má ho jen `entity.player ≤ 120`, `sim.crafting ≤ 100`, `entity.enemy ≤ 90`,
`sim.offline ≤ 100`, `engine.shell ≤ 120`).

### 5.3 Třetí otevřené PR — změna stavu mezi koly **(nové)**

```
1. 10. 2026 14:45 UTC (M2):  2 otevřené PR (#28, #29), 24 sloučených, 29 celkem
2. 10. 2026 05:44 UTC (teď): 3 otevřené PR (#28, #29, #30), 24 sloučených, 30 celkem
```

**Za 15 hodin přibyl 1 PR a 0 sloučení.** S29 se **rozšířila**.

### 5.4 `done_note` je mrtvé pole i v souboru **(nové, ověřeno walkem)**

**Příkaz:** Python walk přes oba repy, komentáře odstraněny.

```
"done_note"  → čtenářů v kódu: 0
             → zapisovatel: _analyza\srovnej-roadmap-done.py (jednorázový)
             → výskyt v index.ts, worker.mjs, agent.yml: 0
```

Pole tedy **existuje jen jako proseba pro člověka**, kterou stroj nevidí.
To je horší varianta S22: nejde o „smlouvu, kterou nikdo nečte", ale o
**varování, které systém sám napsal a sám ignoruje**.

### 5.5 `roadmap.updated_at` — dva zápisy téhož sloupce, dva různé významy **(nové)**

```
schema.sql:62      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
index.ts:464       ALTER TABLE roadmap ADD COLUMN updated_at TEXT   ← bez NOT NULL a defaultu
index.ts:643       INSERT … status='queued'                          ← vznik granule
index.ts:389,404   UPDATE … datetime('now')                          ← změna stavu
index.ts:466       UPDATE updated_at = created_at WHERE updated_at IS NULL
```

Sloupec nese **dva významy zároveň**: „kdy naposledy změněn stav" i „kdy
naposledy selhal" (guard čte `rm.updated_at`). Round 1 to pojmenovalo jako S12;
**nové je, že `schema.sql` a `index.ts` deklarují sloupec jinak** — na živé DB
vznikl `ALTER`em bez defaultu.

### 5.6 Nasazená verze `agent.yml` — ověřena proti GitHubu **(nové)**

**Příkaz:** Node `fetch` na
`https://api.github.com/repos/ssevcikm-spec/uo-shadows/contents/.github/workflows/agent.yml`
s `Accept: application/vnd.github.raw` (PAT ze secrets, nevypisuje se).

```
status 200, 33 425 bajtů (raw z GitHubu)

klíčové řádky nasazené verze:
  340: exit 1
  372: exit 1
  438: exit 1
  454: exit 1
  486: exit 1
  604: id: gate
  652: id: ci
  685: run: gh pr merge "$PR" --squash --delete-branch
  687: - name: Když pravidla neprošla – nechá se k ruční kontrole
  693: gh pr comment "$PR" --body "🤖 **Automatické sloučení neproběhlo** …
```

**Závěr:** `exit 1` je **jen před ř. 604** (tedy v jobu agenta), **žádný není
za krokem 687–693**. → **Auto-merge v NASazené verzi nemá jak selhat** — S32
platí pro produkci, ne jen pro šablonu.

**Poznámka k velikostem:** lokální klon `games\uo-shadows\.github\workflows\agent.yml`
je 34 870 B, raw z GitHubu 33 425 B, šablona `orchestra\repo\...` 34 819 B.
**Tři různé velikosti téhož souboru** — proto se stav ověřoval **raw z GitHubu**,
což je autorita pro to, co se skutečně spouští (drift kontrola hlídá jen 12 cest
a `agent.yml` mezi nimi není).

**Změřeno:** 2. 10. 2026, 05:47 UTC.

---

## 6. Ověření tvrzení prvního kola — co sedí a co ne

| Tvrzení (round 1) | Naměřeno 2. 10. 05:40 UTC | Verdikt |
|---|---|---|
| `scripts/save.gd` a `scripts/hud.gd` v `main` nejsou | `origin/main/scripts` = 9 souborů, ani jeden z nich | **potvrzeno** |
| PR #28, #29 otevřené, `mergeable_state=clean` | #28 `open/clean +91/−0`, #29 `open/clean +77/−0` | **potvrzeno** |
| D1 14 řádků, 10 `done` | 14 řádků, **11 `done`** | **zpřesněno** (přibyl `sim.mining`) |
| soubor 18 granul, 10 `done:true` | 18 granul, 10 `done:true` | **potvrzeno** |
| 4 granule bez řádku v D1 | `core.attributes`, `entity.item`, `sim.offline`, `engine.shell` | **potvrzeno** |
| `core.attributes` a `entity.item` mají sloučené PR #19, #20 | `#19 merged 30. 9. 15:50:49`, `#20 merged 30. 9. 15:51:45` | **potvrzeno** |
| 2 otevřené PR, 24 sloučených, 29 celkem | **3 otevřené, 24 sloučených, 30 celkem** | **VYVRÁCENO** (stav se změnil) |
| „PR se sloučily samy" | `merged_by` = `ssevcikm-spec` u všech 8 kontrolovaných | **vyvráceno i teď** |
| Příčina S29: granule nemají `size_lines` → limit 60 | **všechny tři** (`persist.save`, `ui.hud`, `sim.mining`) `size_lines` nemají; 90/76/66 > 60 | **potvrzeno pro všechny tři** |
| `pc-domaci` 42,5 h offline (1. 10. 14:45) | **3457 min = 57,6 h** (2. 10. 05:40) | **zpřesněno** (roste) |
| orchestra mrtvá 82,7 % času | neměřeno v tomto kole (vyžaduje stažení 247 běhů) | **nepřevzato** |

### 6.1 Oprava mého vlastního omylu (a co z něj plyne)

První kolo tvrdí (`M2:131-133`, `A:459`):

> „granule `persist.save` a `ui.hud` NEMAJÍ `size_lines` → `maxLinesOf()` vrátí
> výchozích 60 → gate správně zamítl (add+del > max_lines)"

**Toto tvrzení je správné a platí i pro třetí granuli `sim.mining`** (66 > 60).
První kolo tedy **nepochybilo** — chyboval jsem **já** v mezikroku, když jsem
`sim.mining` připsal `size_lines: "<= 100"` (patří `sim.crafting`).
**Opraveno v §5.2** a je to zapsané v §10 analýzy jako vlastní omyl.

**Co je na tom poučné:** omyl vznikl **pohledem na špatný řádek tabulky**, kterou
jsem si sám vypsal (`done=... size_lines=...` pro všechny granule) — a **vypadal
jako nález, který vyvrací cizí dokument**. Přesně proto pravidlo z `AGENTS.md`
říká: *„Než označíš cizí číslo za nepravdivé, zkus ho zopakovat týmž postupem,
jakým vzniklo."* Zopakoval jsem ho **jiným** postupem (výpis celého objektu)
a cizí číslo obstálo.

**Skutečný nález místo toho:** `size_lines` chybí u **13 z 18** granul, takže
tři nesloučené PR **nejsou smůla** — je to následek chybějícího pole, které
si nikdo nevynutí.

---

## 7. Nástroje vytvořené tímto kolem

| Skript | Co měří | Poznámka |
|---|---|---|
| `hl2-live.mjs` | živé endpointy conductora | secret z `.env`, nevypisuje se |
| `hl2-d1-snapshot.mjs` | zmrazí D1 do JSON + porovná se souborem | výstup `hl2-d1-snapshot.json` |
| `hl2-s29-s30.mjs` | PR a `main` proti GitHub API | čte `hl2-git.json` |
| `hl2-git.json` | git fakta (protože Node v sandboxu nemůže spustit podproces) | — |
| `hl2-kontrola.py` | **brána**: kontroluje všech 9 bodů „Hotovo znamená" ze zadání | `exit 1` při chybějícím bodu |
| `hl2-mutace-kontrola.py` | **mutační test té brány** | 6 mutací, všechny musí spadnout |

### 7.1 Mutační test brány — bez něj by to byla zelená, ne důkaz

**Naměřeno 2. 10. 2026, 05:52 UTC.** `python _analyza\hl2-mutace-kontrola.py`:

```
vychozi dokument bez mutace:                      exit=0  (spravne)
ponechany jen S31-S34 (4 tridy, pozadovano 5):   exit=1  ← CHYBI 3)
tabulka 'stav -> cim je ukotveno' smazana:       exit=1  ← CHYBI 2)
Varianta B prejmenovana (zbyde 1 varianta):      exit=1  ← CHYBI 7)
podminky selhani smazany:                        exit=1  ← CHYBI 7)
oddil 'Co by tuhle analyzu vyvratilo' smazan:    exit=1  ← CHYBI 1) a 8)
tabulka odpovedi na otazky smazana:              exit=1  ← CHYBI 6)
po vraceni originalu:                            exit=0  (spravne)
```

**6/6 mutací chyceno.** Checkbox „Hotovo znamená" je tedy **změřený**, ne odškrtnutý.

⚠ **A jeden omyl, který to odhalilo:** první verze mého mutačního testu byla
**slepá** — spadla na tom, že jsem v PowerShellu dělal
`$orig -replace '### S36 —[^\n]*', ...` a **em-dash `—` se v konzoli rozbil**,
takže replace **tiše neudělal nic** a test „prošel". Je to přesně past
z `AGENTS.md` („kontrola, která nemá jak selhat"). Opraveno přesunem mutací
do Pythonu, kde se soubor čte i píše s `encoding='utf-8'`.

⚠ **A druhý omyl téhož druhu, naměřený 2. 10. 2026 v 06:15 UTC** (až když jsem
do dokumentu přidal **S37**): mutace „ponech jen S31–S34" odebírala **natvrdo
S35 a S36** — a protože tříd bylo najednou **sedm**, zbylo jich **pět**
a kontrola **správně prošla**. Test tedy **ohlásil slepotu kontroly, která
slepá nebyla**. Opraveno tak, že se počet bere **z dokumentu** a test si na
konci **ověří, že mutace opravdu proběhla** (`assert len(zbyle) == 4`).
**Pravidlo:** mutační test musí mít **assert i na provedení mutace** — jinak
testuje nezměněný soubor.

**Pravidlo k zapamatování:** kdo dělá mutaci **regulárním výrazem nad českým
textem v PowerShellu**, musí počítat s tím, že se diakritika a pomlčky cestou
rozpadnou — a **mutace, která nic nezmění, vypadá jako úspěch**.

---

**Past, která stála čas:** `hl2-s29-s30.mjs` první verze používala
`execFileSync(git.cmd)` → **`EPERM: spawnSync cmd.exe`**. To je **sandbox
`workspace-write`** (podprocesy s piped stdio), **ne vada skriptu**. Řešení:
git z PowerShellu, výsledek souborem. **Zapsáno do skillu `dsh-prostredi` §3c.**

---

## 8. Co v tomto kole NEBYLO měřeno

- **Využití orchestra (82,7 % mrtvá)** — vyžaduje stažení 247 běhů z GitHub API;
  v tomto kole se nepřepočítávalo. **Číslo z 1. 10. platí pro 1. 10.**
- **Proč PR #30 neprošel gate** — nepřečten komentář na PR ani log běhu.
- **Živé schéma D1** — `wrangler d1 execute` padá na `EPERM` v sandboxu;
  všechna tvrzení o schématu jsou z `orchestra\conductor\schema.sql`
  (což je soubor, který se nasazuje — `deploy.yml:36`).
- **Chování `/tick`** — záměrně nevolán: spustil by dispatch a změnil živý stav.
