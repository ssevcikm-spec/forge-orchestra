"""Doplní do conductora eskalaci: po N neúspěších POŠLI NOTIFIKACI (nic nevypínej).

Zadání uživatele: „přepni to jen na notifikaci na telegram" — tedy žádné
pozastavování granule, jen upozornění, aby se na to člověk mohl podívat.

PROČ TO EXISTUJE (audit 30. 9. 2026): `MAX_ATTEMPTS=5` je v provozu mrtvý kód.
Rozhoduje `pollRuns`, který strop nezná – pošle úkol na `ready`, dokud roadmapa
nevyprší cooldown (RETRY_HOURS=3). Úkol tedy může pokračovat donedkonečna:
5 pokusů / 3 h ≈ 40 pokusů za den na jednu granuli a nikdo se to nedozví.
Naměřeno: task #128 i #131 měly 5 pokusů za 16 minut, celkem 121 spálených
pokusů v historii fronty.

Řešení: watchdog v tiku. Když má úkol aspoň `ESCALATE_AFTER` neúspěšných runů
a ještě jsme to nehlásili, pošle se notifikace a úkol se označí
(`payload.eskalovano = true`), aby se to neopakovalo při každém dalším tiku.

Proč počítat RUNY a ne `attempts`: runy jsou skutečně spálené pokusy (každý
dispatch = jeden run), kdežto `tasks.attempts` se chová jinak na cestě
`/report` a jinak na cestě `pollRuns`. Runy jsou společná pravda pro obojí.
"""

import pathlib
import sys

CONDUCTOR = pathlib.Path(
    r"C:\Users\Ssevc\Local-Deepseek\orchestra\conductor\src\index.ts")
WRANGLER = pathlib.Path(
    r"C:\Users\Ssevc\Local-Deepseek\orchestra\conductor\wrangler.toml")

# Kotva, za kterou se funkce vloží (za notify, aby byla po ruce).
KOTVA = """// ------------------------------------------------------- polling běhů ----"""

FUNKCE = '''/**
 * Upozorní, když granule spálila příliš mnoho pokusů.
 *
 * PROČ: `MAX_ATTEMPTS` je v provozu mrtvý kód (rozhoduje `pollRuns`, který
 * strop nezná), takže úkol může pokračovat donekonečna – 5 pokusů / 3h
 * cooldown ≈ 40 pokusů za den na jednu granuli a nikdo se to nedozví.
 * Naměřeno 30. 9. 2026: #128 i #131 měly 5 pokusů za 16 minut, v historii
 * fronty 121 spálených pokusů.
 *
 * ZÁMĚRNĚ SE NIC NEVYPÍNÁ: granule se nechává dál zkoušet (může jít o přechodný
 * výpadek poskytovatele) a posílá se jen notifikace, ať se na to člověk podívá.
 * Aby se neopakovala při každém tiku, označí se úkol `payload.eskalovano`.
 *
 * @returns počet nově ohlášených granulí
 */
async function escalateStuckTasks(env: Env): Promise<number> {
  const prah = Number(env.ESCALATE_AFTER || "8");
  let ohlášeno = 0;
  try {
    const rows = await env.DB.prepare(
      `SELECT t.id, t.title, t.payload,
              (SELECT COUNT(*) FROM runs r WHERE r.task_id = t.id) AS pokusu
         FROM tasks t
        WHERE t.status IN ('ready','failed')
        ORDER BY t.id DESC LIMIT 50`,
    ).all<{ id: number; title: string; payload: string | null; pokusu: number }>();

    for (const t of rows.results || []) {
      if ((t.pokusu ?? 0) < prah) continue;
      let p: Record<string, unknown> = {};
      try { p = JSON.parse(t.payload || "{}"); } catch { /* */ }
      if (p.eskalovano === true) continue; // už jsme hlásili

      const granule = typeof p.grain === "string" ? p.grain : "?";
      const soubory = Array.isArray(p.owns) ? (p.owns as string[]).join(", ") : "?";
      await notify(
        env,
        "Forge: granule se nedari",
        `#${t.id} ${granule}\\n${t.title}\\n`
        + `spáleno ${t.pokusu} pokusů (prah ${prah})\\n`
        + `soubory: ${soubory}\\n`
        + `běh pokračuje dál – nic se nevypíná, jen na vědomí`,
        "warning",
      );
      p.eskalovano = true;
      p.eskalovano_pokusu = t.pokusu;
      await env.DB.prepare("UPDATE tasks SET payload=? WHERE id=?")
        .bind(JSON.stringify(p), t.id).run().catch(() => undefined);
      ohlášeno++;
    }
  } catch (e) {
    console.log("eskalace selhala:", String(e).slice(0, 160));
  }
  return ohlášeno;
}

'''

# Volání v tiku – hned po pollRuns, ať se pracuje s aktuálními daty.
STARE_VOLANI = """  // 0) nejdřív si vyzvedni výsledky běžících cloudových úloh z GitHubu
  const polled = await pollRuns(env).catch((e) => `polling selhal: ${String(e)}`);"""

NOVE_VOLANI = """  // 0) nejdřív si vyzvedni výsledky běžících cloudových úloh z GitHubu
  const polled = await pollRuns(env).catch((e) => `polling selhal: ${String(e)}`);

  // 0b) watchdog: granule, která spálila příliš mnoho pokusů, se OHLÁSÍ.
  //     Nic se nevypíná – jen notifikace, ať se na to dá podívat.
  const eskalovano = await escalateStuckTasks(env);"""


def main() -> int:
    if not CONDUCTOR.exists():
        print(f"CHYBA: {CONDUCTOR} nenalezen")
        return 1
    text = CONDUCTOR.read_text(encoding="utf-8")
    zmeny = []

    if "async function escalateStuckTasks" not in text:
        if KOTVA not in text:
            print("CHYBA: kotva pro vložení funkce nenalezena.")
            return 1
        text = text.replace(KOTVA, FUNKCE + KOTVA, 1)
        zmeny.append("funkce escalateStuckTasks")
    else:
        print("funkce escalateStuckTasks: už tam je")

    if "await escalateStuckTasks(env)" not in text:
        if STARE_VOLANI not in text:
            print("CHYBA: místo pro volání v tiku nenalezeno.")
            return 1
        text = text.replace(STARE_VOLANI, NOVE_VOLANI, 1)
        zmeny.append("volání v tiku")
    else:
        print("volání v tiku: už tam je")

    if zmeny:
        CONDUCTOR.write_text(text, encoding="utf-8")

    # ESCALATE_AFTER do wrangler.toml (vedle ostatních stropů).
    wt = WRANGLER.read_text(encoding="utf-8")
    if "ESCALATE_AFTER" not in wt:
        if 'MAX_ATTEMPTS = "5"' in wt:
            wt = wt.replace(
                'MAX_ATTEMPTS = "5"',
                'MAX_ATTEMPTS = "5"\n'
                '# Po kolika spálených pokusech se granule OHLÁSÍ (Telegram).\n'
                '# Nic se nevypíná – jen notifikace. Watchdog v tiku.\n'
                'ESCALATE_AFTER = "8"',
                1,
            )
            WRANGLER.write_text(wt, encoding="utf-8")
            zmeny.append("ESCALATE_AFTER do wrangler.toml")
        else:
            print("VAROVÁNÍ: MAX_ATTEMPTS ve wrangler.toml nenalezen – ESCALATE_AFTER nedoplněn")
    else:
        print("ESCALATE_AFTER: už tam je")

    print("\nZměny:", ", ".join(zmeny) if zmeny else "(žádné)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
