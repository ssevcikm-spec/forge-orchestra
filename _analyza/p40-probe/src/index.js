// p40-probe v2 — DOČASNÝ měřicí Worker (viz wrangler.toml).
//
// PROČ VZNIKL (P40, druhé kolo): první sonda měřila jen **D1 round-trip**
// (0,42–0,90 ms cpuTime) a podle toho se zlevnil tik z 23 round-tripů na 13 —
// ale živý tik zůstal na **18 ms** (wall time spadl z 3,9 s na 2,1 s!). Rozklad
// tedy nesedí: buď je režie round-tripu v KONDUKTORU jiná než ve smyčce sondy,
// nebo je cena někde jinde. Tahle verze proto měří TŘI věci v JEDNÉ invokaci:
//
//   1. `?f=N`     — N sekvenčních `fetch()` na MALÝ veřejný endpoint
//                   (https://api.github.com/zen, ~15 B). Tik dělá 3 fetche
//                   (GraphQL + otevřené PR + roadmapa) — a kdyby každý stál
//                   ~2–3 ms CPU (režie subrequestu), je to hlavní položka.
//   2. `?d1=N`    — N sekvenčních `SELECT 1` (jako minule; kontrola, že se
//                   číslo opakuje).
//   3. `?batch=N` — N příkazů JEDNÍM `batch()` (kontrola, že batch je 1 round-trip).
//   4. CRON `* * * * *` — handler **NEDĚLÁ NIC** kromě jednoho `console.log`.
//                   Jeho `cpuTime` je BASELINE cron invokace: kdyby byl sám
//                   ~15 ms, pak se tik pod 10 ms nedostane ŽÁDNOU optimalizací
//                   kódu a celý závěr H192 by stál na špatném modelu.
//
// Bez `?token=` vrací 403 (sonda nemá být veřejná, i když nic nemění).

const TOKEN = "p40-probe";

export default {
  async scheduled(_event, _env, ctx) {
    // ZÁMĚRNĚ NIC: jediný console.log, aby se dal event v tailu přiřadit.
    console.log("p40-probe cron: prazdna invokace (baseline)");
    ctx.waitUntil(Promise.resolve());
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.searchParams.get("token") !== TOKEN) {
      return new Response(JSON.stringify({ error: "chybi token" }), { status: 403 });
    }
    const fN = Math.min(50, Number(url.searchParams.get("f") || "0"));
    const d1N = Math.min(200, Number(url.searchParams.get("d1") || "0"));
    const batchN = Math.min(200, Number(url.searchParams.get("batch") || "0"));
    const v = { f_n: fN, d1_n: d1N, batch_n: batchN };

    // 1) FETCHE — malý payload, takže se měří REŽIE SUBREQUESTU, ne parsování
    if (fN > 0) {
      const kody = [];
      for (let i = 0; i < fN; i++) {
        const r = await fetch("https://api.github.com/zen", {
          headers: { "User-Agent": "forge-probe", Accept: "text/plain" },
        });
        kody.push(r.status);
        await r.text();
      }
      v.f_kody = kody.join(",");
    }

    // 2) D1 sekvenčně
    if (d1N > 0) {
      for (let i = 0; i < d1N; i++) {
        await env.DB.prepare("SELECT 1 AS x").first();
      }
    }

    // 3) D1 batch
    if (batchN > 0) {
      const stmts = Array.from({ length: batchN }, () => env.DB.prepare("SELECT 1 AS x"));
      const vys = await env.DB.batch(stmts);
      v.batch_vysledku = vys.length;
    }

    v.ok = true;
    return new Response(JSON.stringify(v), { headers: { "content-type": "application/json" } });
  },
};
