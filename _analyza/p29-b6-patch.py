# -*- coding: utf-8 -*-
r"""P29/B6 — NASADÍ DVĚ OPRAVY DO `conductor/src/index.ts`.

CO OPRAVUJE (obojí naměřeno 9. 10. 2026, ne odhadnuto):

1) **OSIŘELÉ ŘÁDKY CACHE SE UKLÍZEJÍ SAMY.** `roadmap` je jen cache toho, co
   conductor vydal. `roadmapTick` uměl řádky jen PŘIDÁVAT (`INSERT … ON CONFLICT
   DO UPDATE`) — žádný `DELETE` v něm nebyl. Když architekt přepíše roadmapu,
   staré řádky zůstanou a jejich úlohy vypadají jako legitimní práce.
   Měřeno živě (`POST /tasks/cleanup?dry_run`): **21 granulí v souborech,
   25 řádků v cache, 5 osiřelých** — z toho `entity.enemy` s úlohou **#239
   `ready`**. Ruční úklid existoval, ale **nikdo ho nevolal**.

2) **TIK ŘEKNЕ, PROČ NIC NESPUSTIL.** Ruční tik vrátil „spusteno: 0 úloh“
   a přitom bylo **5 úloh `ready`** — a z odpovědi se nedalo zjistit, která
   a proč se přeskočila: `find()` je zahazoval tiše (`grainCapped`, zámek)
   a cooldown vyfiltruje SQL ještě před ním.

⚠ POJISTKY, KTERÉ SE NESMÍ ZTRATIT:
  * maže se JEN pro hru, jejíž roadmapa se PŘEČETLA a je NEPRÁZDNÁ (za
    `if (!items.length) continue;`) — nenačtená roadmapa nesmí mazat nic;
  * maže se JEN `item_id` začínající `{game_id}/` — cizí hry se nedotýká;
  * úloha osiřelého řádku se NEBLOKUJE tady: udělá to invariant „úkol bez řádku
    v roadmapě“ níž v témže tiku (jedno místo, ne dvě);
  * stávající SQL cooldownu se NEMĚNÍ — čte ho brána `f2-over-cooldown.py`
    a `test-cooldown.py` (vytahují ho ze zdrojáku), takže nová diagnostika je
    dotaz NAVÍC, ne náhrada.

Použití: python _analyza\p29-b6-patch.py [--dry-run]
"""

import argparse
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
SRC = WS / "conductor" / "src" / "index.ts"

ZAMENY = [
    # ── 1) čítač uklizených osiřelých řádků ────────────────────────────────
    ("vloz", "  let created = 0;\n  const createdKeys: string[] = [];",
     "  let created = 0;\n  const createdKeys: string[] = [];\n"
     "  // P29/B6: kolik osiřelých řádků se uklidilo (viz blok níž) — tik to hlásí.\n"
     "  let smazanoOsirelych = 0;"),

    # ── 2) vlastní uklizení osiřelých řádků ────────────────────────────────
    ("vloz", "    if (!items.length) continue;\n",
     """    if (!items.length) continue;

    // ── P29/B6: OSIŘELÉ ŘÁDKY CACHE SE UKLÍZEJÍ SAMY ──────────────────────
    // `roadmap` je jen CACHE toho, co conductor vydal. Když soubor granulí
    // změní (architekt přepíše roadmapu), staré řádky v cache zůstanou — a jejich
    // úlohy pak vypadají jako legitimní práce, i když je granule v souboru dávno
    // není. Naměřeno 9. 10. 2026 (`POST /tasks/cleanup?dry_run`): 21 granulí
    // v souborech, 25 řádků v cache, **5 osiřelých** — z toho `entity.enemy`
    // s úlohou **#239 `ready`**. Ruční úklid (`/tasks/cleanup`) to uměl, ale
    // NIKDO HO NEVOLAL, takže se stav jen ručně opravoval a vracel.
    // Tady se uklidí sám — v tiku, který roadmapu stejně čte.
    // ⚠ Úloha se tady NEBLOKUJE: udělá to invariant „úkol bez řádku v roadmapě“
    // níž v témže tiku. Jedno místo, ne dvě.
    const platneKlice = new Set(items.map((i) => `${g.game_id}/${i.id}`));
    const osireleRadky = (rows.results || []).filter(
      (r) => r.item_id.startsWith(`${g.game_id}/`) && !platneKlice.has(r.item_id));
    for (const r of osireleRadky) {
      const del = await env.DB.prepare("DELETE FROM roadmap WHERE item_id = ?")
        .bind(r.item_id).run().catch(() => undefined);
      smazanoOsirelych += del?.meta?.changes ?? 0;
    }
"""),

    # ── 3) hlášení uklizení v návratové zprávě roadmapTick ─────────────────
    ('  if (!created) return "roadmapa je hotová (nebo čeká na závislosti / cooldown)";',
     '  if (smazanoOsirelych) {\n'
     '    await notify(env, "Forge: osiřelé granule uklizeny",\n'
     '      `${smazanoOsirelych} řádků cache bylo mimo aktuální roadmapu — jejich úlohy\\n`\n'
     '      + `zablokuje invariant „úkol bez řádku v roadmapě“ v témže tiku.`,\n'
     '      "warning").catch(() => undefined);\n'
     '  }\n'
     '  const osirMsg = smazanoOsirelych ? `; osiřelých řádků uklizeno: ${smazanoOsirelych}` : "";\n'
     '  if (!created) return "roadmapa je hotová (nebo čeká na závislosti / cooldown)" + osirMsg;'),

    ('  return `z roadmapy založeno ${created} granulí`;',
     '  return `z roadmapy založeno ${created} granulí` + osirMsg;'),

    # ── 4) dispatch: vidět, PROČ se úloha přeskočila ───────────────────────
    ("  const started: number[] = [];\n  while (true) {",
     "  const started: number[] = [];\n"
     "  // P29/B6: „spusteno: 0“ musí být VYSVĚTLENÉ. Naměřeno 9. 10. 2026: ruční\n"
     "  // tik vrátil „spusteno: 0 úloh“ a přitom bylo 5 úloh `ready` — a z odpovědi\n"
     "  // se NEDALO zjistit, která a proč se přeskočila (`find()` je zahazoval tiše).\n"
     "  // „Nula a nezměřeno nejsou úspěch.“\n"
     "  const preskoceno: string[] = [];\n"
     "  while (true) {"),

    ("""    const task = (readyAll.results || []).find((t) => {
      // B3b: zastavenou granuli nevydávej — i kdyby jí v D1 zůstal úkol 'ready'
      // (cooldown i strop se musí ptát na TÝŽ klíč: `grainKeyOf` × `GRAIN_KEY_SQL`).
      if (grainCapped(grainRunsMap?.get(grainKeyOf(t.payload) || ""), cap)) return false;
      return !lockKeys(t.payload, env).some((k) => locked.has(k));
    });""",
     """    const task = (readyAll.results || []).find((t) => {
      // B3b: zastavenou granuli nevydávej — i kdyby jí v D1 zůstal úkol 'ready'
      // (cooldown i strop se musí ptát na TÝŽ klíč: `grainKeyOf` × `GRAIN_KEY_SQL`).
      // P29/B6: každé `return false` se POJMENUJE — viz `preskoceno` níž.
      const klic = grainKeyOf(t.payload) || "";
      const runs = grainRunsMap?.get(klic);
      if (grainCapped(runs, cap)) {
        preskoceno.push(`#${t.id} STROP GRANULE ${runs}/${cap} (${klic})`);
        return false;
      }
      const kolize = lockKeys(t.payload, env).filter((k) => locked.has(k));
      if (kolize.length) {
        preskoceno.push(`#${t.id} ZÁMEK ${kolize.join(", ")}`);
        return false;
      }
      return true;
    });"""),

    # ── 5) cooldown jmenovitě (SQL ho vyfiltruje dřív, než ho `find()` vidí) ─
    ("""  return `spusteno: ${started.length} úloh; polling: ${polled}; ${roadmapMsg}${zombieMsg}${eskalMsg}`
    + (aktivniHry.length ? "" : " | POZOR: žádná AKTIVNÍ hra → nedispatchuji (B4)");""",
     """  const preskocenoMsg = preskoceno.length
    ? ` | přeskočeno: ${[...new Set(preskoceno)].slice(0, 6).join("; ")}` : "";
  // Cooldown vyfiltruje SQL JEŠTĚ PŘED `find()`, takže ho `preskoceno` nevidí.
  // Když se nic nespustilo, musí být vidět i on — jinak zůstane „0 úloh“ tiché.
  let cooldownMsg = "";
  if (!started.length) {
    const cd = await env.DB.prepare(
      `SELECT t.id FROM tasks t JOIN roadmap rm ON rm.task_id = t.id
        WHERE t.status='ready' AND t.target='cloud'
          AND rm.naposledy_selhalo > datetime('now', ?) ORDER BY t.id LIMIT 10`,
    ).bind(`-${retryH} hours`).all<{ id: number }>().catch(() => null);
    const ids = (cd?.results || []).map((r) => `#${r.id}`);
    if (ids.length) cooldownMsg = ` | v cooldownu ${ids.length} úloh: ${ids.join(", ")}`;
  }
  return `spusteno: ${started.length} úloh; polling: ${polled}; ${roadmapMsg}${zombieMsg}${eskalMsg}${cooldownMsg}${preskocenoMsg}`
    + (aktivniHry.length ? "" : " | POZOR: žádná AKTIVNÍ hra → nedispatchuji (B4)");"""),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    text = SRC.read_text(encoding="utf-8")
    chyb = 0
    for i, polozka in enumerate(ZAMENY, 1):
        druh, stary, novy = (polozka if len(polozka) == 3
                             else ("zamena", polozka[0], polozka[1]))
        n = text.count(stary)
        if n != 1:
            print("CHYBA záměna %d: kotva je v souboru %d× (musí být 1×)" % (i, n))
            chyb += 1
            continue
        # ⚠ DVA DRUHY ZÁMĚNY (a každý má jinou kontrolu):
        #  * `zamena` — starý text se NAHRAZUJE; nový ho NESMÍ obsahovat, jinak
        #    by kontrola hledala totéž (omyl #18/#106 téhle rodiny).
        #  * `vloz`   — kotva ZŮSTÁVÁ a přidává se za ni; tady je naopak důkazem
        #    správnosti to, že nový text začíná starým a je DELŠÍ.
        if druh == "zamena" and stary in novy:
            print("CHYBA záměna %d: nový text OBSAHUJE starý (kontrola by hledala totéž)" % i)
            chyb += 1
            continue
        if druh == "vloz" and not (novy.startswith(stary) and len(novy) > len(stary)):
            print("CHYBA záměna %d: `vloz` musí začínat kotvou a být delší" % i)
            chyb += 1
            continue
        text = text.replace(stary, novy, 1)
        print("OK    %s %d: %d znaků → %d znaků" % (druh, i, len(stary), len(novy)))
    if chyb:
        print("NIC SE NEZAPSALO (%d chybných záměn)" % chyb)
        return 1
    if args.dry_run:
        print("DRY RUN — soubor se nezměnil")
        return 0
    SRC.write_bytes(text.encode("utf-8"))
    print("zapsáno: %s (%d B)" % (SRC.relative_to(WS), len(text.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
