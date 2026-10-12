// p40-probe — DOČASNÝ měřicí Worker (viz wrangler.toml).
//
// CO MĚŘÍ (a co z toho plyne pro conductora):
//   1. `?d1=N`   — N sekvenčních `SELECT 1` na TÉŽE D1. Z živého tailu se pak
//                  odečte `cpuTime` invokace → režie NA JEDEN ROUND-TRIP.
//                  Tik jich dělá 21–23, takže tohle číslo je ta chybějící
//                  polovina rozkladu (offline model ji změřit NEDOKÁŽE).
//   2. `?burn=MS`— přesně zadaný kus CPU v busy-loopu. Podle toho, které
//                  hodnoty ještě doběhnou a které umřou na `exceededCpu`, se
//                  změří EFEKTIVNÍ CPU limit (dokumentace free plánu: 10 ms
//                  s „built-in flexibility“, takže limit NENÍ přesná zeď).
//   3. `?json=KB`— kolik stojí `JSON.parse` velké odpovědi (kontrola, že
//                  offline měření v Node sedí na workerd).
//
// Bez `?token=` (pevný řetězec, není to tajemství služby) vrací 403 — sonda
// nemá být veřejná, i když nic nemění.
//
// Výstup pro člověka je JSON; jména polí jsou ASCII (čte je program).

const TOKEN = "p40-probe";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.searchParams.get("token") !== TOKEN) {
      return new Response(JSON.stringify({ error: "chybi token" }), { status: 403 });
    }
    const d1N = Math.min(200, Number(url.searchParams.get("d1") || "0"));
    // ⚠ `burn` NEPOUŽÍVAT: busy loop s `Date.now()` je ve workerd NEKONEČNÝ —
    // čas se během SYNCHRONNÍHO kódu neposouvá (naměřeno 12. 10. 2026: každé
    // `burn>0` skončilo `exceededCpu` po ~2 s CPU, protože podmínka nikdy
    // neplatila). CPU se proto zadává POČTEM ITERACÍ (`iters`), bez hodin.
    const iters = Math.min(50000000, Number(url.searchParams.get("iters") || "0"));
    const jsonB = Math.min(2000000, Number(url.searchParams.get("jsonb") || "0"));

    const v = { d1_n: d1N, iters, json_b: jsonB };

    // 1) BUSY LOOP — „přesně tolik CPU“ (žádné čtení hodin!)
    if (iters > 0) {
      let x = 0.5;
      for (let i = 0; i < iters; i++) x += Math.sqrt(i + 1) * 1.000001;
      v.iters_x = Math.round(x) % 1000000;
    }

    // 2) D1 — N sekvenčních dotazů; měří se i wall time UVNITŘ workerd
    if (d1N > 0) {
      const casy = [];
      const t0 = Date.now();
      for (let i = 0; i < d1N; i++) {
        const a = Date.now();
        await env.DB.prepare("SELECT 1 AS x").first();
        casy.push(Date.now() - a);
      }
      v.d1_ms_celkem = Date.now() - t0;
      v.d1_ms_prvni = casy[0];
      v.d1_ms_median = casy.sort((a, b) => a - b)[Math.floor(casy.length / 2)];
    }

    // 3) JSON.parse velké odpovědi (jen CPU, bez sítě)
    if (jsonB > 0) {
      const txt = "[\"" + "x".repeat(Math.max(0, jsonB - 4)) + "\"]";
      const p = JSON.parse(txt);
      v.json_bajtu = txt.length;
      v.json_polozek = p.length;
    }

    // 4) `DB.batch()` — TVRZENÍ, NA KTERÉM STOJÍ CELÉ ZLEVNĚNÍ: N příkazů
    //    v JEDNOM round-tripu. Kdyby batch stál jako N samostatných dotazů,
    //    je zlevnění přes batch jen kosmetika.
    const batchN = Math.min(200, Number(url.searchParams.get("batch") || "0"));
    if (batchN > 0) {
      const stmts = Array.from({ length: batchN }, () => env.DB.prepare("SELECT 1 AS x"));
      const vysledky = await env.DB.batch(stmts);
      v.batch_n = batchN;
      v.batch_vysledku = vysledky.length;
    }

    // 5) SKUTEČNÝ payload `/pulls?state=closed&per_page=100` (600 kB) — kolik
    //    stojí `JSON.parse` v workerd (Node měří 2,3 ms, ale Node není workerd).
    const gh = url.searchParams.get("gh") || "";
    if (gh) {
      const rr = await fetch(
        "https://api.github.com/repos/ssevcikm-spec/uo-shadows/pulls?state=closed&per_page=100&sort=updated&direction=desc",
        { headers: { "User-Agent": "forge-probe", Accept: "application/vnd.github+json" } },
      );
      const txt = await rr.text();
      const j = JSON.parse(txt);
      v.gh_status = rr.status;
      v.gh_bajtu = txt.length;
      v.gh_pr = j.length;
    }
    if (gh === "gql") {
      const rr = await fetch("https://api.github.com/graphql", {
        method: "POST",
        headers: { "User-Agent": "forge-probe", "content-type": "application/json" },
        body: JSON.stringify({
          query: "query{repository(owner:\"ssevcikm-spec\",name:\"uo-shadows\"){pullRequests(states:MERGED,last:100,orderBy:{field:UPDATED_AT,direction:DESC}){nodes{title headRefName}}}}",
        }),
      });
      const txt = await rr.text();
      JSON.parse(txt);
      v.gql_status = rr.status;
      v.gql_bajtu = txt.length;
    }

    v.ok = true;
    return new Response(JSON.stringify(v), { headers: { "content-type": "application/json" } });
  },
};
