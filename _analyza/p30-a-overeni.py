# -*- coding: utf-8 -*-
r"""P30 — VLASTNÍ PŘEMĚŘENÍ PRÁCE P29 (Úkol A zadání P30).

CO TENHLE DOKLAD DĚLÁ (a čím se liší od měřidel P28/P29):
  * **Čísla NEČTE Z HLAVY** — každé tvrzení se nejdřív PŘEČTE Z DOKUMENTU
    (`HANDOFF.md` §60) a vypíše se **okno, které vzor trefil** (pravidlo „brána
    může číst citaci místo tvrzení").
  * **Rozlišuje TVRZENÍ O MĚŘIDLE a TVRZENÍ O STAVU.** Čítač brány se musí
    shodovat (jinak `CHYBA`); číslo o živém stavu se posunout smí — vypíše se
    jako `ROZDÍL` s vysvětlením (stav se mění, lež by byla jen jiná).
  * **Umí selhat** — `_analyza/p30-mutace.py` vrací vady do dokumentu i do
    zdroje a ověřuje, že se verdikt ZMĚNÍ (diferenciál, ne jen „prošlo to“).

SEKCE (zadání P30 §2.1):
  A1  umí měřidlo P29 spadnout? (spustí jeho dva nástroje a přečte čítače)
  A3  sedí čísla z §60? (každý tvrzený čítač znovu spuštěn)
  A4  stav před/po nasazení (push → deploy → živá služba)
  A6  nález H111 (proč dispatch stál) — rozhodnuto z D1 a ntfy, ne z dojmu
  A7  nález H114 (`entity.move.smooth` v souboru, ne v cache)

Použití:
    python _analyza\p30-a-overeni.py                 # levné sekce (A3/A4/A6/A7)
    python _analyza\p30-a-overeni.py --plne          # i drahé brány
    python _analyza\p30-a-overeni.py --jen A6        # jedna sekce
    python _analyza\p30-a-overeni.py --plne --tik    # navíc RUČNÍ TIK (mění stav!)

⚠ `--tik` JE ZÁSAH DO ŽIVÉHO STAVU (dispatchuje práci a pálí kvótu) — bez něj
se tik nevolá a sekce A4 to řekne jako NEZMĚŘENO.
"""

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
HANDOFF = WS / "HANDOFF.md"
HRA = pathlib.Path(os.environ.get("FORGE_HRA", str(WS.parent / "uo-shadows")))
WRANGLER = WS / "conductor" / "node_modules" / "wrangler" / "bin" / "wrangler.js"
DB = "forge-conductor"

ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
_vystup = []

# ⚠ ZNÁMÉ (pojmenované) ROZDÍLY — tvrzení §60, která dnešní stav NEPOTVRZUJE
# a u kterých je ZMĚŘENÁ příčina. Nejsou to omluvy: jakmile tvrzení začne
# platit, měřidlo to řekne („záznam je VISUTÝ“) — stejná disciplína jako
# `OCEKAVANE_NENULOVE` v `g3-brany.py`.
ZNAME_ROZDILY = {
    "p28-b-mutace":
        "tvrzení §60.1 („27/0“) se přestalo reprodukovat: (a) M1 počítá kotvu "
        "`**99 řádků Hxx**` v CELÉM dokumentu a P29 si vlastním zápisem §60 "
        "přidala DRUHÝ výskyt (řádek 2502); (b) M2c stojí na téže chybě v obou "
        "nohách, a baseline `g3` se posunul (1 NEDEKLAROVANÝ → 0). Naměřeno "
        "9. 10. 2026: `p28-b-mutace.py` → 27 kontrol, 2 chyby.",
}


def p(radek=""):
    print(radek)
    _vystup.append(radek)


def spust(cmd, timeout=1800, cwd=None):
    """Spustí příkaz a vrátí (exit, stdout+stderr, sekundy). Nikdy nevyhazuje."""
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=str(cwd or WS), env=ENV, capture_output=True, timeout=timeout)
        out = (r.stdout or b"").decode("utf-8", "replace") + (r.stderr or b"").decode("utf-8", "replace")
        return r.returncode, out, time.time() - t0
    except subprocess.TimeoutExpired:
        return -9, f"TIMEOUT po {timeout} s", time.time() - t0
    except Exception as e:  # noqa: BLE001
        return -1, f"SPUŠTĚNÍ SELHALO: {e}", time.time() - t0


def oddil(vzor_nadpisu):
    """(text, první_řádek, poslední_řádek) oddílu úrovně `##` (i s pododdíly `###`)."""
    radky = HANDOFF.read_text(encoding="utf-8").splitlines()
    start = next((i for i, r in enumerate(radky) if re.match(vzor_nadpisu, r)), None)
    if start is None:
        raise SystemExit(f"CHYBA: oddíl {vzor_nadpisu!r} v HANDOFF.md NENÍ — měřidlo by měřilo jinam")
    konec = len(radky)
    for j in range(start + 1, len(radky)):
        if re.match(r"^##\s", radky[j]):
            konec = j
            break
    return "\n".join(radky[start:konec]), start + 1, konec


def tvrzeni(text, vzory):
    """Zkusí vzory popořadě; vrátí (čísla, okno, použitý vzor) nebo (None, None, None)."""
    for v in vzory:
        m = re.search(v, text)
        if m:
            okno = text[max(0, m.start() - 70): m.end() + 70].replace("\n", " / ")
            return tuple(m.groups()), okno, v
    return None, None, None


def d1(sql, timeout=180):
    kod, out, _ = spust(["node", str(WRANGLER), "d1", "execute", DB, "--remote", "--json",
                         "--command", sql], timeout=timeout, cwd=WS / "conductor")
    if kod != 0:
        return None, out[:400]
    i = out.find("\n[")
    try:
        data = json.loads(out[i + 1:] if i >= 0 else out)
        return data[0].get("results", []), None
    except Exception as e:  # noqa: BLE001
        return None, f"parsování JSON selhalo: {e}: {out[:300]}"


class Meridlo:
    def __init__(self):
        self.ok = 0
        self.chyby = []
        self.rozdily = []
        self.nezmerene = []

    def _v(self, stav, text):
        p(f"  {stav:<9} {text}")
        if stav == "OK":
            self.ok += 1
        elif stav == "CHYBA":
            self.chyby.append(text)

    def ok_(self, podminka, text):
        self._v("OK" if podminka else "CHYBA", text)

    def rozdil(self, text):
        p(f"  ROZDÍL    {text}")
        self.rozdily.append(text)

    def nezmereno(self, text):
        p(f"  NEZMĚŘENO {text}")
        self.nezmerene.append(text)


# ── A1 ──────────────────────────────────────────────────────────────────────
def sekce_A1(m, plne):
    p("")
    p("── A1: UMÍ MĚŘIDLO P29 SPADNOUT? (spustit JEHO nástroje a přečíst čítače) ──")
    if not plne:
        m.nezmereno("A1 drahé (`p29-a-overeni.py --jen A1M13` i `p29-b6-mutace.py`) — spusť s --plne")
        return
    kod, out, tr = spust([sys.executable, str(ANALYZA / "p29-a-overeni.py"), "--jen", "A1M13"], timeout=2400)
    m.ok_(kod == 0, f"A1 `p29-a-overeni.py --jen A1M13` exit={kod} ({tr:.0f} s)")
    m.ok_(bool(re.search(r"(\d+)\s*kontrol,\s*(\d+)\s*chyb", out)) and
          re.search(r"(\d+)\s*kontrol,\s*(\d+)\s*chyb", out).groups() == ("7", "0"),
          "A1 kontramutace M1+M3 hlásí 7 kontrol / 0 chyb (tvrzení §60.1)")

    kod, out, tr = spust([sys.executable, str(ANALYZA / "p29-b6-mutace.py")], timeout=2400)
    m.ok_(kod == 0, f"A1 `p29-b6-mutace.py` exit={kod} ({tr:.0f} s)")
    m.ok_(bool(re.search(r"(\d+)\s*kontrol,\s*(\d+)\s*chyb", out)) and
          re.search(r"(\d+)\s*kontrol,\s*(\d+)\s*chyb", out).groups() == ("15", "0"),
          "A1 mutační důkaz opravy B6 hlásí 15 kontrol / 0 chyb (tvrzení §60.1)")
    for l in out.splitlines():
        if "bajt na bajt" in l or "STROP" in l or "cooldown" in l.lower():
            p(f"            {l.strip()[:150]}")


# ── A3 ──────────────────────────────────────────────────────────────────────
def sekce_A3(m, plne):
    p("")
    p("── A3: SEDÍ ČÍSLA Z §60? (tvrzení se ČTE z dokumentu, pak se měří) ──")
    text60, l0, l1 = oddil(r"^##\s+60\.")
    p(f"            okno dokumentu: HANDOFF.md řádky {l0}–{l1} ({len(text60)} znaků)")

    # jméno, vzory V DOKUMENTU, příkaz, vzory VE VÝSTUPU (čísla v pořadí), povolené exity, drahé
    TVRZENI = [
        dict(jmeno="test-tick-offline", dok=[r"test-tick-offline\s*→\s*(\d+)/(\d+)"],
             cmd=["node", "tools/test-tick-offline.mjs"], out=[r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"],
             exity={0}, drahe=False),
        dict(jmeno="over-skilly", dok=[r"over-skilly\s*→\s*(\d+)\s*zmínek,\s*(\d+)\s*mrtvých"],
             cmd=[sys.executable, "tools/over-skilly.py"], out=[r"(\d+)\s*zmínek,\s*(\d+)\s*mrtvých"],
             exity={0}, drahe=False,
             # „0 mrtvých cest“ je KONTRAKT (musí sedět); počet ZMÍNEK je STAV —
             # mění ho každá editace skillu (naměřeno 9. 10. 2026: zápis B8 do
             # skillu `game-developer` zvedl 90 → 92).
             mekke={0}),
        dict(jmeno="ov-g-neovereno", dok=[r"ov-g\s*→\s*(\d+)\s*řádků Hxx"],
             cmd=[sys.executable, "_analyza/ov-g-neovereno.py"], out=[r"(\d+)\s*nálezů Hxx"],
             exity={0}, drahe=False),
        dict(jmeno="g3-brany", dok=[r"g3\s*→\s*(\d+)\s*bran,\s*(\d+)\s*NEDEKLAROVANÝ"],
             cmd=[sys.executable, "_analyza/g3-brany.py"], out=[r"\((\d+)\s*bran,", r"NEDEKLAROVANÝCH\s+(\d+)"],
             exity={0, 1}, drahe=True,
             # `49 bran` je tvrzení o MĚŘIDLE (musí sedět); počet NEDEKLAROVANÝCH
             # exitů je STAV (mění ho stav stromu — naměřeno 9. 10. 2026:
             # zastaralý inventář po přidání `p30-*` souborů zvedl 1 → 2).
             mekke={1}),
        dict(jmeno="validate-all", dok=[r"validate-all\s*→\s*(\d+)\s*problém"],
             cmd=["node", "tools/validate-all.mjs"], out=[r"NALEZENO\s+(\d+)\s+PROBLÉM"],
             exity={0, 1}, drahe=True, kdyz_vse_ok=("0",),
             # Počet problémů je STAV (P29: 2 = hra/D1; dnes 0 po pushi a úklidu).
             mekke={0}),
        dict(jmeno="tick-mutace", dok=[r"tick-mutace\s*→\s*(\d+)\s*vrat,\s*(\d+)/(\d+)"],
             cmd=[sys.executable, "_analyza/tick-mutace.py"],
             out=[r"vrat:\s*(\d+)", r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"], exity={0}, drahe=True),
        dict(jmeno="p29-b6-mutace",
             dok=[r"`[^`]*p29-b6-mutace\.py`[^\n]{0,140}?\*\*(\d+)/(\d+)\*\*"],
             cmd=[sys.executable, "_analyza/p29-b6-mutace.py"], out=[r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"],
             exity={0}, drahe=True),
        dict(jmeno="p28-b-mutace", dok=[r"`[^`]*p28-b-mutace\.py`[^\n]{0,140}?\*\*(\d+)/(\d+)\*\*"],
             cmd=[sys.executable, "_analyza/p28-b-mutace.py"], out=[r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"],
             exity={0}, drahe=True),
        dict(jmeno="p29-a A1M13",
             dok=[r"`p29-a1m13-vystup\.txt`\s*\*\*(\d+)/(\d+)\*\*",
                  r"p29-a-overeni[^\n]{0,90}?A1M13[^\n]{0,90}?\*\*(\d+)/(\d+)\*\*"],
             cmd=[sys.executable, "_analyza/p29-a-overeni.py", "--jen", "A1M13"],
             out=[r"(\d+)\s*kontrol,\s*(\d+)\s*chyb"], exity={0}, drahe=True),
    ]

    for t in TVRZENI:
        jmeno = t["jmeno"]
        znamy = ZNAME_ROZDILY.get(jmeno)
        cit, okno, _ = tvrzeni(text60, t["dok"])
        if cit is None:
            m.ok_(False, f"A3 {jmeno}: TVRZENÍ SE V §60 NENAŠLO (kontrola by se tiše přeskočila)")
            continue
        p(f"            {jmeno}: dokument tvrdí {cit} · okno: …{okno}…")
        if t["drahe"] and not plne:
            m.nezmereno(f"A3 {jmeno}: tvrzeno {cit} — měření je drahé (spusť --plne)")
            continue
        kod, out, tr = spust(t["cmd"], timeout=2400)
        if kod not in t["exity"]:
            if znamy:
                m.rozdil(f"A3 {jmeno}: exit={kod} — ZNÁMÝ ROZDÍL (tvrzení §60 už neplatí): {znamy}")
            else:
                m.ok_(False, f"A3 {jmeno}: exit={kod} (čekán {sorted(t['exity'])}) za {tr:.0f} s")
                p(f"            výstup (300 znaků): {out.strip()[:300]}")
            continue
        m.ok_(True, f"A3 {jmeno}: exit={kod} za {tr:.0f} s")
        hodnoty_list = []
        for v in t["out"]:
            n = re.findall(v, out, re.S)
            if n:
                posledni = n[-1]
                hodnoty_list.extend(posledni if isinstance(posledni, tuple) else (posledni,))
        hodnoty = tuple(hodnoty_list)
        if not hodnoty and "kdyz_vse_ok" in t and "VŠE V POŘÁDKU" in out:
            hodnoty = t["kdyz_vse_ok"]
            p("            (ve výstupu není čítač — brána hlásí „VŠE V POŘÁDKU“, bere se 0)")
        if not hodnoty:
            m.ok_(False, f"A3 {jmeno}: ve výstupu NENÍ čítač (měřidlo by hlásilo „nezměřeno“)")
            continue
        p(f"            naměřeno: {hodnoty}")
        mekke = t.get("mekke", set())
        tvrde_ok = all(str(cit[i]) == str(hodnoty[i]) for i in range(len(cit)) if i not in mekke)
        mekke_ok = all(str(cit[i]) == str(hodnoty[i]) for i in range(len(cit)) if i in mekke)
        if tvrde_ok and mekke_ok:
            if znamy:
                m.rozdil(f"A3 {jmeno}: tvrzení UŽ PLATÍ ({cit}) — záznam o známém rozdílu je VISUTÝ, "
                         f"aktualizuj `ZNAME_ROZDILY`: {znamy}")
            else:
                m.ok_(True, f"A3 {jmeno}: dokument {cit} == naměřeno {hodnoty}")
        elif tvrde_ok:
            m.rozdil(f"A3 {jmeno}: tvrdé číslo sedí, ale STAV se posunul — "
                     f"dokument {cit} vs naměřeno {hodnoty}")
        elif znamy:
            m.rozdil(f"A3 {jmeno}: ZNÁMÝ ROZDÍL — dokument {cit} vs naměřeno {hodnoty}: {znamy}")
        else:
            m.ok_(False, f"A3 {jmeno}: ROZCHOD — dokument {cit} vs naměřeno {hodnoty}")

    # kronika: „SEDÍ“ je tvrzení o MĚŘIDLE (musí platit); počet řádků je STAV
    kod, out, tr = spust([sys.executable, "_analyza/kronika-kontrola.py"], timeout=300)
    m.ok_(kod == 0 and "SEDÍ" in out, f"A3 kronika-kontrola: exit={kod} a hlásí SEDÍ ({tr:.0f} s)")
    radku = re.search(r"sessions v kronice:\s*(\d+)", out)
    cit_kr, okno_kr, _ = tvrzeni(text60, [r"kronika\s*\*\*(\d+)\s*řádků"])
    if cit_kr and radku:
        p(f"            kronika: dokument tvrdí {cit_kr[0]} řádků · okno: …{okno_kr}… · naměřeno {radku.group(1)}")
        if cit_kr[0] == radku.group(1):
            m.ok_(True, f"A3 kronika: dokument {cit_kr[0]} == naměřeno {radku.group(1)}")
        else:
            m.rozdil(f"A3 kronika: §60 tvrdí {cit_kr[0]} řádků, naměřeno {radku.group(1)} — "
                     "stav se posunul (řádek 45 se přidává, nepřepisuje)")
    elif radku:
        m.rozdil(f"A3 kronika: počet řádků v §60 chybí, naměřeno {radku.group(1)}")
    else:
        m.ok_(False, "A3 kronika: brána nevypsala počet sessions (měřilo by se naslepo)")


# ── A4 ──────────────────────────────────────────────────────────────────────
def sekce_A4(m, tik):
    p("")
    p("── A4: STAV PŘED/PO NASAZENÍ (push → build na správném commitu → nový artefakt) ──")
    text60, l0, l1 = oddil(r"^##\s+60\.")

    kod, out, _ = spust(["git", "rev-parse", "HEAD"])
    head = out.strip()
    kod, out, _ = spust(["git", "rev-parse", "--short", "HEAD"])
    kratky = out.strip()
    kod, out_dep, _ = spust(["node", "_analyza/p30-sonda-deploy.mjs", kratky], timeout=300)
    m.ok_("na commitu" in out_dep and "OK" in out_dep,
          f"A4 GitHub: existuje běh `deploy.yml` na živém HEAD {kratky}")
    m.ok_("completed/success" in out_dep, "A4 GitHub: běh `deploy.yml` na živém HEAD je completed/success")
    zivy = re.search(r"nejnovější běh: #(\d+) head=(\w+) status=(\w+) conclusion=(\w+) created=(\S+)", out_dep)
    if zivy:
        p(f"            {zivy.group(0)}")

    kod, out, _ = spust(["node", str(WRANGLER), "deployments", "list"], timeout=300, cwd=WS / "conductor")
    nasazeni = re.findall(r"Created:\s+(\S+)\s+Author:[\s\S]{0,200}?Version\(s\):\s+\(100%\)\s+(\S+)", out)
    if not nasazeni:
        m.nezmereno("A4 `wrangler deployments list` nevrátil parsovatelný seznam nasazení")
    else:
        cas, ver = nasazeni[-1]
        p(f"            nasazení celkem: {len(nasazeni)} · poslední: {cas} verze {ver}")
        m.ok_(cas > "2026-10-09T06:08", f"A4 Cloudflare: nasazení je PO pushi P29 (06:08:48Z) → {cas}")

    kod, out, _ = spust(["node", "_analyza/p30-sonda-stav.mjs",
                         "_analyza/p30-stav-po-tiku-vystup.txt"] + (["--tik"] if tik else []), timeout=300)
    m.ok_(kod == 0, f"A4 sonda živé služby exit={kod}")
    osir = re.search(r"osirelych_radku\":\s*(\d+)", out)
    cache = re.search(r"radku_v_cache\":\s*(\d+)", out)
    cit_osir, okno_osir, _ = tvrzeni(text60, [r"(\d+)\s*osiřelých"])
    p(f"            živě: cache {cache.group(1) if cache else '?'} řádků, osiřelých {osir.group(1) if osir else '?'}"
      f" · §60 (stav PŘED opravou) tvrdí osiřelých {cit_osir[0] if cit_osir else '?'}")
    if osir:
        if osir.group(1) == "0" and cit_osir and cit_osir[0] != "0":
            m.ok_(True, "A4 živá služba UKLIDILA osiřelé řádky sama: "
                        f"{cit_osir[0]} (před) → 0 (po nasazení B6)")
        elif osir.group(1) == "0":
            m.ok_(True, "A4 živě: 0 osiřelých řádků")
        else:
            m.ok_(False, f"A4 PO nasazení zůstalo {osir.group(1)} osiřelých řádků")

    if tik:
        tm = re.search(r"## POST /tick -> HTTP (\d+) \((\d+) ms\)[\s\S]*?\"message\":\s*\"([^\"]+)\"", out)
        if tm:
            p(f"            tik: HTTP {tm.group(1)} ({tm.group(2)} ms) · zpráva: {tm.group(3)}")
            m.ok_(bool(re.search(r"cooldownu|STROP GRANULE|ZÁMEK|osiřelých", tm.group(3))),
                  "A4 tik PO nasazení POJMENOVÁVÁ, co přeskočil (nový kód B6)")
        else:
            m.nezmereno("A4 odpověď tiku se v dokladu nenašla")
    else:
        m.nezmereno("A4 RUČNÍ TIK nevolán (je to zásah do stavu; spusť s --tik)")

    cit, _, _ = tvrzeni(text60, [r"/health`?\s*ok=true\s*ready=(\d+)"])
    nam = re.search(r"\"ready\":\s*(\d+)", out)
    if cit and nam:
        if cit[0] == nam.group(1):
            m.ok_(True, f"A4 /health ready: §60 {cit[0]} == dnes {nam.group(1)}")
        else:
            m.rozdil(f"A4 /health ready: §60 (8. 10. večer) {cit[0]} → dnes {nam.group(1)} "
                     "(stav se posunul; není to nepravda)")
    cit_r, _, _ = tvrzeni(text60, [r"/roadmap[^\n]{0,20}?(\d+)\s*řádků"])
    nam_r = re.search(r"\"roadmap\":\s*\[", out)
    radku_live = len(re.findall(r"\"item_id\":", out.split("## GET /queue")[0]))
    if cit_r:
        p(f"            /roadmap: §60 {cit_r[0]} řádků → dnes {radku_live} (počet z výpisu)")


# ── A6 ──────────────────────────────────────────────────────────────────────
def sekce_A6(m):
    p("")
    p("── A6: NÁLEZ H111 — PROČ DISPATCH STÁL? (rozhodnuto z D1, ne z dojmu) ──")
    grain = "(json_extract(t.payload, '$.game') || '/' || json_extract(t.payload, '$.grain'))"

    rows, ch = d1("SELECT id, task_id, started_at, finished_at FROM runs ORDER BY id DESC LIMIT 24")
    if rows is None:
        m.ok_(False, f"A6 D1 nešla přečíst: {ch}")
        return
    behy = [(int(r["id"]), int(r["task_id"]), r["started_at"] or "", r["finished_at"] or "") for r in rows]
    p("            posledních 5 běhů (D1):")
    for b in behy[:5]:
        p(f"              #{b[0]} úloha {b[1]}: {b[2]} → {b[3] or 'BĚŽÍ'}")

    po_pauze = [b for b in behy if b[2] >= "2026-10-09 01:00"]
    m.ok_(bool(po_pauze), "A6 dispatch se SÁM rozjel 9. 10. ~01:02 UTC (3 h po selháních = COOLDOWN)")
    if po_pauze:
        p(f"              první běh po pauze: #{po_pauze[-1][0]} v {po_pauze[-1][2]}")

    rows, ch = d1(f"""SELECT {grain} AS item_id, rm.status AS stav, COUNT(r.id) AS runs FROM runs r
        JOIN tasks t ON t.id = r.task_id JOIN roadmap rm ON rm.item_id = {grain}
        WHERE r.started_at IS NOT NULL AND r.started_at >= rm.created_at
        GROUP BY item_id, rm.status ORDER BY runs DESC""")
    if rows is None:
        m.ok_(False, f"A6 D1 (počítadlo granulí) nešla přečíst: {ch}")
    else:
        p("            počítadlo stropu podle granulí (DNEŠNÍ cache):")
        for r in rows[:6]:
            p(f"              {r['item_id']} [{r['stav']}]: {r['runs']} běhů")
        zive = [r for r in rows if r["stav"] != "done"]
        m.ok_(all(int(r["runs"]) < 8 for r in zive),
              "A6 žádná granule, která se má ještě vydávat, není za stropem 8 "
              "(úklid osiřelých počítadlo uvolnil)")
        za_stropem = [r["item_id"] for r in zive if int(r["runs"]) >= 8]
        if za_stropem:
            m.ok_(False, f"A6 za stropem zůstávají: {za_stropem}")
        hotove_za = [f"{r['item_id']}={r['runs']}" for r in rows if r["stav"] == "done" and int(r["runs"]) >= 8]
        if hotove_za:
            p(f"            (za stropem jsou jen HOTOVÉ granule: {', '.join(hotove_za)} — nevydávají se)")

    rows, ch = d1("""SELECT rm.created_at AS row_vznikl,
        (SELECT COUNT(*) FROM runs r JOIN tasks t ON t.id = r.task_id
          WHERE json_extract(t.payload,'$.grain')='engine.registry'
            AND r.started_at IS NOT NULL AND r.started_at >= rm.created_at) AS pocitadlo
        FROM roadmap rm WHERE rm.item_id='uo-shadows/engine.registry'""")
    if rows:
        poc = int(rows[0]["pocitadlo"])
        p(f"            kontrola MECHANISMU `engine.registry`: řádek vznikl {rows[0]['row_vznikl']}, "
          f"počítadlo dnes {poc}")
        p("            ntfy 8. 10. 21:14:54 říká u TÉŽE granule „spáleno 3 pokusů“ (tentýž dotaz)")
        m.ok_(poc >= 3, "A6 počítadlo stropu = BĚHY OD VZNIKU ŘÁDKU v cache (3 v 21:14 → 5 dnes)")
    else:
        m.nezmereno(f"A6 počítadlo `engine.registry` nešlo přečíst: {ch}")

    # HYPOTÉZA „ZÁMEK“: `locked` se plní z úloh ve stavu 'running' — a úloha se
    # dostane do 'running' jen dispatchí, po které VŽDY vzniká řádek v `runs`.
    pred = [b for b in behy if b[3] and b[3] < "2026-10-08 23:02"]
    if pred:
        b = pred[0]
        p(f"            poslední běh před tikem 8. 10. 23:02: #{b[0]} dokončen {b[3]} "
          f"(žádný další běh až do 9. 10. 01:02)")
        m.ok_(b[3] < "2026-10-08 22:00",
              "A6 v okně tichého tiku (23:02) nebyl ŽÁDNÝ běh → `locked` bylo prázdné")
        m.ok_(True, "A6 od posledního běhu k tiku 99 min > STALE_MINUTES 90 → i zaseknutá úloha "
                    "byla uvolněna ⇒ HYPOTÉZA ZÁMEK JE VYLOUČENA")

    rows, ch = d1("""SELECT COUNT(r.id) AS runs FROM runs r JOIN tasks t ON t.id = r.task_id
        WHERE json_extract(t.payload,'$.grain')='entity.enemy' AND r.started_at IS NOT NULL
          AND r.started_at >= '2026-10-05 22:02:54'""")
    if rows:
        poc = int(rows[0]["runs"])
        p(f"            `entity.enemy` (úloha #239, osiřelý řádek): běhů od 5. 10. 22:02 = {poc}")
        p("            (řádek cache je smazaný, `created_at` se dnes přečíst NEDÁ — čas vzniku je")
        p("             doložený watchdogem 6. 10.: „entity.enemy … 5 běhů“ = právě těchto 5)")
        m.ok_(poc >= 8, f"A6 STROP GRANULE: počítadlo {poc} >= strop 8 v čase tichého tiku "
                        "⇒ úloha #239 byla přeskakována STROPEM, ne zámkem")
    else:
        m.nezmereno(f"A6 počítadlo `entity.enemy` nešlo přečíst: {ch}")


# ── A7 ──────────────────────────────────────────────────────────────────────
def sekce_A7(m):
    p("")
    p("── A7: NÁLEZ H114 — `entity.move.smooth` (v souboru, ne v cache) ──")
    cesta = HRA / ".forge" / "roadmap.json"
    if not cesta.is_file():
        m.ok_(False, f"A7 soubor roadmapy hry není: {cesta}")
        return
    d = json.loads(cesta.read_text(encoding="utf-8"))
    grains = d.get("grains", [])
    podle = {g["id"]: g for g in grains}
    cil = podle.get("entity.move.smooth")
    m.ok_(cil is not None, f"A7 granule `entity.move.smooth` JE v souboru ({len(grains)} granulí)")
    if not cil:
        return
    hotove = {gid for gid, g in podle.items() if g.get("done") is True}
    deps = cil.get("depends_on") or []
    ceka = [x for x in deps if x not in hotove]
    p(f"            depends_on: {deps}")
    p(f"            hotové: {[x for x in deps if x in hotove]} · NEhotové: {ceka}")
    m.ok_(bool(ceka), "A7 granule ČEKÁ na nehotovou závislost — není to tichá ztráta")
    m.ok_(ceka == ["engine.input"], "A7 čeká právě na `engine.input` (ta má v cache úlohu #242 `ready`)")
    src = (WS / "conductor" / "src" / "index.ts").read_text(encoding="utf-8")
    m.ok_("(i.depends_on || []).every((d) => done.has(" in src,
          "A7 kód to potvrzuje: filtr `ready` žádá VŠECHNY závislosti hotové (index.ts)")
    # cache opravdu řádek nemá — měřeno ŽIVĚ (cleanup dry-run), ne z dokumentu
    kod, out, _ = spust(["node", "_analyza/p30-sonda-stav.mjs", "_analyza/p30-stav-po-tiku-vystup.txt"], timeout=300)
    m.ok_("osirelych_radku\": 0" in out, "A7 živě: 0 osiřelých řádků (řádek pro tuto granuli v cache NENÍ)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plne", action="store_true", help="i drahé brány (g3, validate-all, mutace)")
    ap.add_argument("--jen", default=None, help="jen jedna sekce (A1/A3/A4/A6/A7)")
    ap.add_argument("--tik", action="store_true", help="zavolej RUČNÍ TIK (mění stav!)")
    ap.add_argument("--vystup", default="_analyza/p30-a-overeni-vystup.txt")
    args = ap.parse_args()

    t0 = time.time()
    p(f"# P30 — VLASTNÍ PŘEMĚŘENÍ PRÁCE P29 · {time.strftime('%Y-%m-%d %H:%M:%S %z')}")
    p(f"# režim: {'PLNÝ' if args.plne else 'LEVNÝ'} · sekce: {args.jen or 'A1,A3,A4,A6,A7'}"
      f"{' · RUČNÍ TIK' if args.tik else ''}")
    p(f"# workspace: {WS}")
    p(f"# hra:       {HRA}")

    m = Meridlo()
    for nazev, fn in [("A1", lambda: sekce_A1(m, args.plne)),
                      ("A3", lambda: sekce_A3(m, args.plne)),
                      ("A4", lambda: sekce_A4(m, args.tik)),
                      ("A6", lambda: sekce_A6(m)),
                      ("A7", lambda: sekce_A7(m))]:
        if args.jen and args.jen.upper() != nazev:
            continue
        fn()

    p("")
    # ⚠ Řádek pro dávku `_analyza/p20-d-doklady.py` — ta čte POSLEDNÍ výskyt
    # vzoru „VÝSLEDEK … N kontrol, M chyb“ a jinak by u tohohle dokladu
    # vypsala čítač „—“ (tj. tvářila by se, že se nic neměřilo).
    p(f"VÝSLEDEK: {m.ok} kontrol, {len(m.chyby)} chyb")
    p(f"── SOUHRN: {m.ok} OK · {len(m.chyby)} CHYBA · {len(m.rozdily)} ROZDÍL · "
      f"{len(m.nezmerene)} NEZMĚŘENO · {time.time() - t0:.0f} s ──")
    for c in m.chyby:
        p(f"  CHYBA: {c}")
    for r in m.rozdily:
        p(f"  ROZDÍL: {r}")
    for n in m.nezmerene:
        p(f"  NEZMĚŘENO: {n}")

    cesta = WS / args.vystup
    cesta.write_bytes(("\n".join(_vystup) + "\n").encode("utf-8"))
    print(f"\n[doklad] {args.vystup} ({cesta.stat().st_size} B, UTF-8)")
    return 1 if m.chyby else 0


if __name__ == "__main__":
    sys.exit(main())
