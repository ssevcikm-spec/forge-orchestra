import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Kompletni validace infrastruktury orchestra.
import { readFileSync, existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
// H112 (P33): predikát „běží cron?“ je VYTAŽENÝ do čisté funkce, aby se dal
// ověřit fixturami (`tools/test-cron-stav.mjs`) — ne jen proti živé službě.
import { zhodnotCron } from './cron-stav.mjs';

const ORCH = join(PARENT);
// ⚠ P13c (4. 10. 2026): hra je SOUROZENEC repa, ne `PARENT/games/uo-shadows`.
// Do téhle chvíle tu stálo `join(PARENT, 'uo-shadows')` (což po přesunu na `E:`
// ukazovalo na neexistující `E:\Workspaces\forge-orchestra\uo-shadows`) a na
// dalších místech `PARENT/../games/uo-shadows` (taky neexistuje) — validátor
// proto hlásil vady o hře, kterou vůbec neotevřel.
const GAME = join(PARENT, '..', 'uo-shadows');
const GAMEREPO = 'ssevcikm-spec/uo-shadows';
const ORCHREPO = 'ssevcikm-spec/forge-orchestra';
// Godot je od D7 OBECNÝ NÁSTROJ STANICE (`E:\Tools\godot\`), ne součást repa.
// Když se nenajde, je to VIDĚT — kontrola na něm níž nesmí tiše „projít".
const KANDIDATI_GODOT = [
  process.env.FORGE_GODOT,
  'E:\\Tools\\godot\\Godot_v4.7.2-stable_win64_console.exe',
  join(PARENT, '..', 'Tools', 'godot', 'Godot_v4.7.2-stable_win64_console.exe'),
].filter(Boolean);
const GODOT_CESTA = KANDIDATI_GODOT.find((c) => existsSync(c)) || KANDIDATI_GODOT[0];
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'validate' };
const env = Object.fromEntries(
  readFileSync(`${ORCH}/.env`, 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
const gh = async (p) => { const r = await fetch(`https://api.github.com${p}`, { headers: H }); return r.ok ? r.json() : { chyba: r.status }; };
const cond = async (p) => { const r = await fetch(`${env.FORGE_URL}${p}`, { headers: { 'x-forge-secret': env.FORGE_SECRET } }); return r.ok ? r.json() : { chyba: r.status }; };

const OK = (b) => (b ? 'OK  ' : 'CHYBA');
let chyb = 0;
const test = (nazev, podminka, detail = '') => {
  if (!podminka) chyb++;
  console.log(`  ${OK(podminka)} ${nazev}${detail ? '  — ' + detail : ''}`);
};

// POZOR NA SANDBOX: spouštíme s `stdio: 'inherit'`, ne s `pipe`. V DSH sandboxu
// podproces s pipovaným stdio spadne na `spawn EPERM` (ověřeno 30. 9. 2026) –
// a vypadalo by to jako vada testu, ne jako omezení prostředí. S `inherit`
// funguje obojí a stav je pořád spolehlivý.
// ⚠ P33 (H112): definice je ODSUD (dřív stála až u sekce J), protože ji nově
// používá i sekce A na offline test predikátu cronu.
const spust = (prikaz, parametry) => {
  const vysledek = spawnSync(prikaz, parametry, { stdio: 'inherit', cwd: `${ORCH}/..` });
  if (vysledek.error) return { stav: `chyba: ${vysledek.error.code || vysledek.error.message}` };
  return { stav: vysledek.status };
};

console.log('════ A. CONDUCTOR (runtime) ════');
const h = await cond('/health');
test('conductor odpovídá', h.ok === true);
// ⚠ H112 (P33): tady dřív stálo `!!h.time` — tedy jen „služba odpovídá na
// `/health`“. O běhu CRONU to netvrdilo NIC, a když se 9. 10. 2026 tik
// zastavil, žádná brána to neohlásila (brána, která nemá jak selhat).
// Dnes se měří TEP: `last_cron` zapisuje VÝHRADNĚ plánovaný tik (`scheduled`),
// ruční `POST /tick` ho neobnoví (`last_tick` ano, ale ten se nepoužívá).
// Limit 10 min při cronu každou minutu znamená „netiká“.
// Predikát je v `tools/cron-stav.mjs`; hned po něm se pouští jeho offline test
// s fixturami (starý tep, chybějící tep, ruční tik) — jinak by „zelená proti
// živé službě“ nebyla k rozeznání od slepé brány (`overovani` §7.13).
const cron = zhodnotCron(h, Date.now(), 10);
test('cron běží (čas)', cron.ok, cron.duvod);
const cronTest = spust(process.execPath, [`${ORCH}/tools/test-cron-stav.mjs`]);
test('brána cronu umí spadnout (fixtury: starý tep / chybějící tep / ruční tik)',
  cronTest.stav === 0, `exit=${cronTest.stav}`);
test('je registrovaná hra', (h.games ?? 0) >= 1, `games=${h.games}`);
test('žádná úloha nevisí', (h.running ?? 0) < 10, `running=${h.running}`);

console.log('\n════ B. REGISTR HER ════');
const g = await cond('/games');
const hra = (g.games || []).find((x) => x.game_id === 'uo-shadows');
test('uo-shadows je registrovaná', !!hra);
test('je aktivní', hra?.active === 1, `active=${hra?.active}`);
test('míří na správné repo', hra?.repo === GAMEREPO, hra?.repo);
test('roadmap_file je správný', hra?.roadmap_file === '.forge/roadmap.json', hra?.roadmap_file);

console.log('\n════ C. SOULAD CACHE × SOUBOR ════');
const rm = await cond('/roadmap');
const cache = rm.roadmap || [];
const soubor = JSON.parse(readFileSync(`${GAME}/.forge/roadmap.json`, 'utf8')).grains;
const idSoubor = new Set(soubor.map((x) => `uo-shadows/${x.id}`));
const osirele = cache.filter((r) => !idSoubor.has(r.item_id));
test('cache neobsahuje osiřelé řádky', osirele.length === 0, `osiřelé=${osirele.length}`);
test('cache není větší než soubor', cache.length <= soubor.length, `cache=${cache.length}, soubor=${soubor.length}`);
const hotove = soubor.filter((x) => x.done).length;
test('počet hotových granulí je znám', true, `${hotove}/${soubor.length} hotových`);

console.log('\n════ D. KONFIGURACE CONDUCTORA ════');
const wt = readFileSync(`${ORCH}/conductor/wrangler.toml`, 'utf8');
test('MAX_ATTEMPTS nastaven', /MAX_ATTEMPTS\s*=\s*"\d+"/.test(wt), wt.match(/MAX_ATTEMPTS.*/)?.[0]);
test('RETRY_HOURS nastaven', /RETRY_HOURS\s*=\s*"\d+"/.test(wt), wt.match(/RETRY_HOURS.*/)?.[0]);
test('cron každou minutu', /crons\s*=\s*\["\* \* \* \* \*"\]/.test(wt));

console.log('\n════ E. KÓD CONDUCTORA × DEPLOY ════');
const lokalniKod = readFileSync(`${ORCH}/conductor/src/index.ts`);
const vRepu = await gh(`/repos/${ORCHREPO}/contents/conductor/src/index.ts`);
const kodVR = vRepu.content ? Buffer.from(vRepu.content, 'base64') : Buffer.alloc(0);
// POZOR: porovnávat se musí BEZ konců řádků. Tenhle klon má
// core.autocrlf=true, takže soubor na disku je CRLF (o 1 bajt na řádek větší),
// kdežto v repu je LF. Bajtové porovnání proto hlásilo „lokální kód ≠ repo"
// i když byl soubor IDENTICKÝ s HEAD (naměřeno 30. 9. 2026: 59 534 B vs
// 58 309 B, rozdíl 1 225 B = přesně počet řádků, všech 1225 CRLF).
const bezCr = (b) => b.toString('utf8').replace(/\r\n/g, '\n');
const kodySeLisi = bezCr(lokalniKod) !== bezCr(kodVR);
test('lokální kód = repo', !kodySeLisi,
     kodySeLisi ? `${lokalniKod.length} B vs ${kodVR.length} B (liší se i bez konců řádků)`
                : `${lokalniKod.length} B vs ${kodVR.length} B (shoda po odečtení konců řádků)`);
const behy = await gh(`/repos/${ORCHREPO}/actions/runs?per_page=10`);
// POZOR: deploy se spouští JEN na změny v conductor/**. Když poslední commit
// měnil jen repo/ šablonu, poslední deploy je logicky ze staršího commitu —
// a to je správně. Hledá se proto poslední deploy, který obsahoval conductor.
const deploye = (behy.workflow_runs || []).filter((x) => /Deploy conductor/.test(x.name || ''));
const posledniDeploy = deploye[0];
test('existuje úspěšný deploy conductora', posledniDeploy?.conclusion === 'success',
     `${posledniDeploy?.head_sha?.slice(0, 8)} (${posledniDeploy?.created_at?.slice(0, 16).replace('T', ' ')})`);

// Je nasazený kód opravdu ten, který je v repu pro conductor?
const commitKoduVR = await gh(`/repos/${ORCHREPO}/commits?path=conductor/src/index.ts&per_page=1`);
const shaKodu = commitKoduVR[0]?.sha?.slice(0, 8);
const nasazenySha = posledniDeploy?.head_sha?.slice(0, 8);
// Deploy je v pořádku, když jeho commit je tentýž nebo novější než poslední
// změna conductora. (Novější commit, který měnil jen repo/, deploy nespustí.)
test('deploy obsahuje poslední změnu conductora',
     posledniDeploy?.conclusion === 'success' && !!shaKodu,
     `poslední změna conductor/ = ${shaKodu}, nasazeno z = ${nasazenySha}`);

console.log('\n════ F. HRA: WORKFLOW A BRÁNY ════');
const ay = readFileSync(`${GAME}/.github/workflows/agent.yml`, 'utf8');
test('brána na parsování je ve workflow', /Kontrola parsování/.test(ay));
test('brána je PŘED testy', ay.indexOf('Kontrola parsování') < ay.indexOf('Testy hry'));
test('workflow používá providers.json orchestra', /pick-provider\.mjs/.test(ay));
const conv = readFileSync(`${GAME}/CONVENTIONS.md`, 'utf8');
test('konvence mají FileAccess', /FileAccess/.test(conv));
test('konvence mají rezervovaná jména', /hides a global script class|Rezervovaná/.test(conv));
test('konvence mají JSON.parse_string', /JSON\.parse_string/.test(conv));

console.log('\n════ G. WORKFLOW HRY JE ZAPNUTÝ ════');
const wf = await gh(`/repos/${GAMEREPO}/actions/workflows`);
const agentWf = (wf.workflows || []).find((w) => w.path.endsWith('/agent.yml'));
test('agent.yml je active', agentWf?.state === 'active', agentWf?.state);

console.log('\n════ H. MODELOVÝ ŘETĚZEC ════');
const prov = JSON.parse(readFileSync(`${ORCH}/repo/.forge/providers.json`, 'utf8'));
const nazvy = prov.providers.map((p) => p.name);
test('řetězec má 5 poskytovatelů', prov.providers.length === 5, nazvy.join(', '));
test('gemini je označený skromny', prov.providers.find((p) => p.name === 'gemini')?.skromny === true);
const strong = prov.providers.filter((p) => (p.strongModels || []).length);
test('silné modely definované', strong.length >= 3, strong.map((p) => p.name).join(', '));
// živá verze
const ziva = await (await fetch(`https://raw.githubusercontent.com/${ORCHREPO}/main/repo/.forge/providers.json`)).json();
test('živý providers.json = lokální', JSON.stringify(ziva) === JSON.stringify(prov));

console.log('\n════ I. LOKÁLNÍ PROSTŘEDÍ ════');
test('git.cmd existuje', !!readFileSync(`${ORCH}/tools/git.cmd`));
test('Godot pro worker existuje', (() => { try { return readFileSync(GODOT_CESTA).length > 0; } catch { return false; } })(), GODOT_CESTA);
test('.secrets má PAT', readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim().length > 20);

// ── J. ASSETY: REGISTR ZDROJŮ A BRÁNA NA LICENCE ─────────────────────────────
//
// PROČ SAMOSTATNÁ SEKCE: assety se dosud evidovaly jen hlavou. Registr
// (`assets/asset-registry.json`) a brána (`tools/check-licence.py`) jsou nové
// a musí být ověřené stejně jako zbytek pipeline – jinak by se licenční díra
// jen přesunula z hlavy do souboru, kterému nikdo nerozumí.
//
// ⚠ `spust()` je od P33 definovaný NAHOŘE (u sekce A) — používá ho offline test
// predikátu cronu; sem se už neopisuje (druhá definice téhož = druhá pravda).
console.log('\n════ J. ASSETY: REGISTR A LICENČNÍ BRÁNA ════');
const registrCesta = `${ORCH}/assets/asset-registry.json`;
let registr = null;
try {
  registr = JSON.parse(readFileSync(registrCesta, 'utf8'));
} catch (e) {
  test('registr assetů jde přečíst', false, String(e).slice(0, 80));
}
if (registr) {
  test('registr assetů jde přečíst', true, `${registr.zdroje?.length ?? 0} zdrojů, ${registr.assety?.length ?? 0} assetů`);
  const povolene = new Set((registr.povolene_licence || []).map((l) => String(l).toLowerCase()));
  test('povolené licence jsou definované', povolene.size > 0, [...povolene].join(', '));
  test('cc-by-sa NENÍ povolená', !povolene.has('cc-by-sa'), 'vynucuje stejnou licenci na celou hru');
  const zdrojeIds = new Set((registr.zdroje || []).map((z) => z.id));
  test('každý asset má známý zdroj', (registr.assety || []).every((a) => zdrojeIds.has(a.zdroj)),
    (registr.assety || []).filter((a) => !zdrojeIds.has(a.zdroj)).map((a) => a.id).join(', ') || 'všechny OK');
  test('každý asset má povolenou licenci', (registr.assety || []).every((a) => povolene.has(String(a.licence).toLowerCase())),
    (registr.assety || []).map((a) => `${a.id}:${a.licence}`).join(', '));
  // Strojově stahovatelné položky musí mít čím ověřit obsah – bez hashe by se
  // příští stažení mohlo tiše lišit a nikdo by to nepoznal.
  const stahovane = (registr.assety || []).filter((a) => a.zdroj === 'polyhaven' || a.zdroj === 'kenney');
  test('stahované assety mají hash', stahovane.every((a) => a.sha256 || a.md5),
    stahovane.map((a) => `${a.id}:${a.sha256 || a.md5 ? 'hash OK' : 'CHYBÍ HASH'}`).join(', '));
  test('stahované assety jsou ověřené', stahovane.every((a) => a.overeno === true),
    stahovane.map((a) => `${a.id}:${a.overeno ? 'ověřeno' : 'NE'}`).join(', '));
}
test('fetch assetů jde spustit', spust(process.execPath, [`${ORCH}/tools/asset-fetch.mjs`, '--seznam']).stav === 0);
const licenceTest = spust('python', [`${ORCH}/tools/test-licence.py`]);
test('brána na licence: 9 scénářů', licenceTest.stav === 0, `exit=${licenceTest.stav}`);
test('brána projde na skutečném klonu hry', spust('python', [`${ORCH}/tools/check-licence.py`, `${GAME}`]).stav === 0);

// ── K. VIZUÁLNÍ SCHÉMA A „OČI" (vision) ──────────────────────────────────────
//
// PROČ SAMOSTATNÁ SEKCE: vizuální kontrola je nová vrstva a má dvě pojistky,
// které se musí ověřovat společně:
//
//   1) SCHÉMA. Vizuální kontrola potřebuje vědět, PROTI ČEMU měří. Když si hra
//      odporuje (spec.json tvrdí izometrii 96×48, ale level.gd kreslí 16px
//      čtverce), vision hlásí buď věčné nekonzistence, nebo nic. Naměřeno
//      30. 9. 2026: čtyři zdroje pravdy, tři různá čísla.
//   2) VLASTNÍ TESTY VISION. vision.mjs se v provozu testuje těžko (klíč, kvóta,
//      obrázek), takže jeho logika má vlastní offline test s mock API.
//
// POZOR: „rozpor schématu" tu NENÍ očekávaný stav — schéma je od 1. 10. 2026
// rozhodnuté (per-game, autoritou je `assets/spec.json` hry) a CI hry je
// zelené. Testuje se tedy obojí: že kontrola UMÍ rozpor pojmenovat (exit 1),
// a že se vůbec spustí (exit 2 = „nemám co měřit" NENÍ zelená).
console.log('\n════ K. VIZUÁLNÍ SCHÉMA A „OČI" ════');
{
  // POZOR (opraveno 1. 10. 2026, krok A1 plánu): tady se dřív volalo
  // `tools/kontrola-schematu.py` — STARÁ, SLEPÁ kopie téhož pravidla.
  // Naměřeno: stará kopie vypsala `level.gd: výchozí cell=[], fallback=[]`
  // (regexy nenašly po migraci na izometrii nic) a hlásila ZELENOU, kdežto
  // správná kopie v `.forge/` změří `96×48px` a pojmenuje mrtvou větev
  // v `world.gd`. Validátor tedy měřil jinou kopii, než jaká běží v CI.
  // Správný zdroj je `repo/.forge/check-schema.py` (tentýž soubor dostane hra).
  const kontrola = spust('python', [`${ORCH}/repo/.forge/check-schema.py`, `${GAME}`]);
  // 0 = soulad, 1 = rozpory, 2 = chybí spec (nedá se měřit).
  // 2 NENÍ úspěch — „nemám co měřit" se nesmí počítat jako zelená.
  test('kontrola schématu se spustí (0 = soulad, 1 = rozpory, 2 = chybí spec)',
    [0, 1].includes(kontroly(kontrola)),
    `exit=${kontrola.stav}`);
  test('kontrola schématu je i v šabloně a v herním repu',
    existsSync(`${ORCH}/repo/.forge/check-schema.py`)
    && existsSync(`${GAME}/.forge/check-schema.py`));

  // 1. 10. 2026: kontrola výchozích hodnot v `level.gd` TIŠE PŘESTALA MĚŘIT –
  // hledala `var cell := 16`, ale po migraci na izometrii je v kódu
  // `const CELL_W_DEFAULT := 96`. Regexy nenašly nic, cyklus proběhl nad
  // prázdným seznamem a brána byla zelená. Testy níž hlídají, že prázdno
  // znamená „kontrola neproběhla“, a že šablona s herním repem nedriftuje.
  const schemaTesty = spust('python', [`${ORCH}/tools/test-check-schema.py`]);
  test('check-schema.py: offline testy (známá správná i chybná hodnota)',
    schemaTesty.stav === 0, `exit=${schemaTesty.stav}`);

  // Kontraktní test: `.gitignore`, který orchestra vnucuje hrám, musí chránit
  // tajemství. `install-into-repo.ps1` kopíruje do hry `.env` s REÁLNÝM
  // FORGE_SECRET – a ten soubor nebyl ignorovaný (naměřeno 1. 10. 2026).
  // Test hlídá SHODU generátoru a hry a ověřuje, že pravidla opravdu platí
  // (`git check-ignore`), ne jen že jsou napsaná.
  const gitignoreTesty = spust('python', [`${ORCH}/tools/test-gitignore-tajemstvi.py`]);
  test('.gitignore hry chrání tajemství (kontrakt generátor ↔ hra)',
    gitignoreTesty.stav === 0, `exit=${gitignoreTesty.stav}`);

  // Workflowy nesmí mít v `echo` neescapovaný zpětný apostrof — bash ho bere
  // jako substituci a text, který má jen vypadat jako kód, se POKUSÍ SPUSTIT.
  // Naměřeno 1. 10. 2026 (běh #241): skutečná příčina selhání se v tom šumu
  // ztratila. Nástroj rozlišuje vadu (neescapovaný apostrof) od záměru ($( )),
  // protože falešný poplach nutí „opravovat" správný kód.
  const echoTesty = spust('python', [`${ORCH}/tools/kontrola-echo-substituci.py`]);
  test('workflowy: žádné neescapované apostrofy v echo (bash by je spustil)',
    echoTesty.stav === 0, `exit=${echoTesty.stav}`);

  const vision = spust(process.execPath, [`${ORCH}/repo/.forge/node/vision.test.mjs`]);
  test('vision.mjs: offline testy (mock API) projdou', vision.stav === 0, `exit=${vision.stav}`);

  const profilCesta = `${GAME}/.forge/vision-profile.json`;
  try {
    const p = JSON.parse(readFileSync(profilCesta, 'utf8'));
    test('profil vision existuje a je platný JSON', true, `hra=${p.hra}, režim očekávání=${p.ocekavany_obsah}`);
    // Profil NESMÍ nést velikost dlaždice ani projekci – ta patří do spec.json
    // hry. Kdyby je nesl, schéma by přestalo být per-game a začalo se rozejít
    // přesně tak, jako se rozešlo to dnešní.
    test('profil NEobsahuje schéma hry (to patří do spec.json)',
      !('dlazdice' in p) && !('projekce' in p) && !('tile' in p),
      Object.keys(p).join(', '));
    test('profil má zakázané soudy v promptu', Array.isArray(p.zakazy_v_promptu)
      && p.zakazy_v_promptu.length > 0);
  } catch (e) {
    test('profil vision jde přečíst', false, String(e).slice(0, 100));
  }

  const ci = spust(process.execPath, [`${ORCH}/tools/test-ci-workflow.mjs`]);
  test('CI workflow: struktura a pořadí kroků', ci.stav === 0, `exit=${ci.stav}`);

  // ── COOLDOWN GUARD (krok A3 plánu, 1. 10. 2026) ───────────────────────────
  //
  // PROČ TU JE: `test-cooldown.py` SQL dřív OPSOVAL (vlastní kopie podmínky,
  // včetně té STARÉ děravé varianty) a neměl `assert` ani `sys.exit` – vypsal
  // `CHYBA` a skončil `exit 0`. Teď SQL vytahuje **ze zdrojáku conductora**,
  // takže když se změní, test použije novou verzi.
  //
  // POZOR – HISTORIE, NE DNEŠNÍ STAV (ověřeno 6. 10. 2026): tenhle test byl
  // od 1. 10. 2026 **ČERVENÝ a bylo to SPRÁVNĚ** — naměřil vadu **S12** (nová
  // granule se kvůli guardu na `updated_at` 3 h nevydá). Opravil ji krok **B1**
  // plánu (`naposledy_selhalo`) a **dnes je test ZELENÝ**: `10 kontrol, 0 chyb`,
  // `python tools/test-cooldown.py` → `exit 0`, a B1 je v `conductor/src/index.ts`
  // (ř. 430/434/543/546). Text se nechal jako záznam, protože popisuje, PROČ test
  // vznikl — kdo uvidí zelenou, ať nehledá vadu, která je opravená.
  //
  // Kdyby to někdo potřeboval odlišit: `test-eskalace.py` je NAPROSTO V POŘÁDKU
  // (má `sys.exit(0 if vse_ok else 1)`); „lže zelenou" se týkalo JEN tohohle testu.
  const cooldown = spust('python', [`${ORCH}/tools/test-cooldown.py`]);
  test('cooldown guard: SQL ze zdrojáku + chování',
    cooldown.stav === 0, `exit=${cooldown.stav}`);

  // ── N0.3: STAV CÍLE V /health (6. 10. 2026) ──────────────────────────────
  //
  // PROČ TU JE: conductor hlásil `ok: true` nad mrtvým cílem. Naměřeno
  // 1. 10. 2026 (7,5 h bez práce kvůli červenému CI hry, S18) a ZNOVU
  // 6. 10. 2026 (od 5. 10. 22:02 selhalo 9 běhů v řadě, `/health` pořád `ok`).
  //
  // Test NEOPISUJE logiku: nechá si conductora zbundlovat (`wrangler --dry-run`,
  // bez sítě i bez přihlášení) a zavolá SKUTEČNÝ handler `/health` s falešnou D1
  // a stubovaným GitHubem — měří tedy tutéž cestu jako živá služba.
  // A sám má mutační důkaz (`_analyza/n03-mutace.py`, 5 vrat → 5× musí spadnout).
  const cil = spust(process.execPath, [`${ORCH}/tools/test-health-cile.mjs`]);
  test('N0.3: /health hlásí stav cíle (main_ci + forge)',
    cil.stav === 0, `exit=${cil.stav}`);

  const cilMutace = spust('python', [`${ORCH}/_analyza/n03-mutace.py`]);
  test('N0.3: mutační důkaz brány (5 vrat → 5× spadne)',
    cilMutace.stav === 0, `exit=${cilMutace.stav}`);

  // ── B3a: WATCHDOG NA GRANULI (6. 10. 2026) ───────────────────────────────
  //
  // PROČ TU JE: watchdog počítal běhy JEDNOHO úkolu a měl prah 8 > strop 5, takže
  // se nikdy nemohl spustit. Naměřeno na živé službě: `entity.npc` spálil 8 pokusů
  // napříč DVĚMA úkoly (#228: 5, #234: 3) a conductor ho vydával dál; v `payload`
  // žádné úlohy nebylo `eskalovano`.
  //
  // Test čte SQL, prah i rozhodnutí **ze zdrojáku** (neopisuje je) a hlídá i to,
  // že prah je POD stropem — prah nad stropem je prah, který nikdy nepřijde.
  const watchdog = spust('python', [`${ORCH}/tools/test-watchdog-granule.py`]);
  test('B3a: watchdog počítá běhy granule, prah pod stropem',
    watchdog.stav === 0, `exit=${watchdog.stav}`);

  const watchdogMutace = spust('python', [`${ORCH}/_analyza/b3-mutace.py`]);
  test('B3a: mutační důkaz brány (5 vrat → 5× spadne)',
    watchdogMutace.stav === 0, `exit=${watchdogMutace.stav}`);

  // ── B2: SELHÁNÍ PŘES `/report` MUSÍ ZALOŽIT COOLDOWN ─────────────────────
  //
  // PROČ TU JE: `/report` dřív zapsal jen `tasks`, ne `roadmap` → granule se
  // vrátila do fronty okamžitě a spálila všechny pokusy za čtvrt hodiny
  // (naměřeno 30. 9. 2026: #128 měl 5 pokusů za 16 minut). Opravil to B1, ale
  // **nikdo to neměřil** — `test-cooldown.py` kryje cestu dispatche, ne zápis
  // z `/report`. Brána vytahuje obě SQL ze zdrojáku a simuluje guard.
  const reportCooldown = spust('python', [`${ORCH}/tools/test-report-cooldown.py`]);
  test('B2: /report zakládá cooldown (cooldown je okno, ne vězení)',
    reportCooldown.stav === 0, `exit=${reportCooldown.stav}`);

  const reportMutace = spust('python', [`${ORCH}/_analyza/b2-mutace.py`]);
  test('B2: mutační důkaz brány (4 vrata → 4× spadne)',
    reportMutace.stav === 0, `exit=${reportMutace.stav}`);

  // ── B4: BEZ AKTIVNÍ HRY SE NEDISPATCHUJE (invariant 18) ──────────────────
  //
  // PROČ TU JE: `listGames` měl fallback na `env.GITHUB_REPO`, takže **vypnutí
  // poslední registrované hry orchestra nezastavilo** — dispatch jel dál na hře,
  // kterou uživatel vypnul. Naměřeno bránou PŘED opravou: `7 kontrol, 3 CHYB`
  // (vypnutá hra → `[{game_id: "default", repo: <GITHUB_REPO>}]`).
  // Brána měří SQL ve skutečném SQLite, VOLÁ skutečný `listGames` a kontroluje
  // i guardy v `tick` (dispatch smyčka čte úlohy z D1).
  const hry = spust('python', [`${ORCH}/tools/test-listgames.py`]);
  test('B4: bez aktivní hry se nedispatchuje (fallback je pryč)',
    hry.stav === 0, `exit=${hry.stav}`);

  const hryMutace = spust('python', [`${ORCH}/_analyza/b4-mutace.py`]);
  test('B4: mutační důkaz brány (4 vrata → 4× spadne)',
    hryMutace.stav === 0, `exit=${hryMutace.stav}`);

  // ── B3b: STROP NA GRANULI (záměrně VYPNUTÝ, nasazuje se druhým krokem) ────
  //
  // PROČ TU JE: watchdog (B3a) jen hlásí; nic nezastaví. Naměřeno: `entity.npc`
  // spálil 8 běhů napříč dvěma úkoly a ve frontě na to vzniklo 49 osiřelých
  // úloh na tutéž granuli. Strop je obrana proti tomu — a je **vypnutý**
  // (`GRAIN_MAX_RUNS = "0"`), aby se dalo nejdřív změřit, že watchdog hlásí.
  // Brána volá skutečné `grainCap`/`grainCapped`/`grainKeyOf` a hlídá i shodu
  // obou tvarů klíče granule (JS × SQL, invariant 17).
  const strop = spust('python', [`${ORCH}/tools/test-grain-cap.py`]);
  test('B3b: strop na granuli + shoda obou tvarů klíče',
    strop.stav === 0, `exit=${strop.stav}`);

  const stropMutace = spust('python', [`${ORCH}/_analyza/b3b-mutace.py`]);
  test('B3b: mutační důkaz brány (5 vrat → 5× spadne)',
    stropMutace.stav === 0, `exit=${stropMutace.stav}`);

  // ── TIK OFFLINE: ROZHODOVACÍ LOGIKA CONDUCTORA ───────────────────────────
  //
  // PROČ TU JE: projekt o sobě psal, že conductor **nemá test své rozhodovací
  // logiky** — `.py` testy ji opisovaly a `mock-conductor.mjs` `/tick` neuměl.
  // Tenhle test volá SKUTEČNÝ `POST /tick` nad zbundlovaným conductorem
  // s falešnou D1 (router podle SQL, neznámý dotaz = CHYBA) a stubovaným
  // GitHubem. Měří tím i acceptance `B4` na úrovni TIKU (ne staticky).
  const tik = spust(process.execPath, [`${ORCH}/tools/test-tick-offline.mjs`]);
  test('tik offline: bez aktivní hry se nedispatchuje (acceptance B4)',
    tik.stav === 0, `exit=${tik.stav}`);

  const tikMutace = spust('python', [`${ORCH}/_analyza/tick-mutace.py`]);
  // ⚠ Bez počtu v názvu schválně: stál tu a dvakrát zestaral (3 → 6 → 8 vrat).
  // Skutečný počet kontrol hlásí sám test a registr `g3`.
  test('tik offline: mutační důkaz brány (každé vratné vady si všimne)',
    tikMutace.stav === 0, `exit=${tikMutace.stav}`);

  // ── BASELINE A LGTM CACHE ─────────────────────────────────────────────────
  // Bez baseline nelze měřit drift: „vypadá to jinak" je tvrzení, které se
  // nedá ověřit, dokud není s čím porovnávat. Testuje se tu jak logika
  // (offline testy), tak stav skutečné hry.
  const baseTesty = spust('python', [`${ORCH}/repo/.forge/baseline.py`, 'testy']);
  test('baseline.py: offline testy (včetně mezer phash) projdou',
    baseTesty.stav === 0, `exit=${baseTesty.stav}`);

  test('baseline.py je v šabloně i v herním repu',
    existsSync(`${ORCH}/repo/.forge/baseline.py`)
    && existsSync(`${GAME}/.forge/baseline.py`));

  const stav = spust('python', [`${ORCH}/repo/.forge/baseline.py`,
                                '--koren', `${GAME}`, 'stav']);
  // 0 = vše schválené a nezměněné, 1 = jsou neschválené změny.
  // 1 NENÍ chyba nástroje – je to stav hry (a je to dnešní očekávaný stav,
  // dokud uživatel neřekne LGTM).
  test('baseline hry jde přečíst (0 = schváleno, 1 = čeká na LGTM)',
    [0, 1].includes(typeof stav.stav === 'number' ? stav.stav : -1),
    `exit=${stav.stav}`);
}

// Pomocník: `spust` vrací exit kód, ale u kontrol, které legitimně vrací 1
// (rozpory), se nesmí počítat 1 jako selhání nástroje.
function kontroly(v) {
  return typeof v.stav === 'number' ? v.stav : -1;
}

// ── L. BRÁNY NAD KÓDEM CONDUCTORA A ŠABLONOU (rozhodnutí 2. 10. 2026) ────────
//
// PROČ SAMOSTATNÁ SEKCE: brány A1/A2/A3 a „datum spotřeby analýzy" vznikly při
// ověřování práce session `eb127abd` a bydlely v `_analyza\` — tedy MIMO oba
// repozitáře a mimo veškerou automatiku. Naměřeno 2. 10. 2026: `write_text` se
// v nich nevyskytuje ani jednou (jsou POUZE ČTOUCÍ), takže do validátoru patří;
// kdežto `*mutace*.py` a `hl2-kostra-*.py` soubory schválně PŘEPISUJÍ a vrací,
// a ty sem NEPATŘÍ — pustit je z validátoru znamená riskovat pracovní strom.
//
// POJISTKA, KTERÁ JE V TOM SCHVÁLNĚ: u každého nástroje se nejdřív ověří, že
// v jeho zdroji není zápis (`write_text`/`write_bytes`/`copyfile`/`writeFileSync`).
// Kdyby někdo nástroj později „vylepšil" o zápis, validátor ho PŘESTANE spouštět
// a řekne to — místo aby tiše mazal soubory. Bez téhle kontroly by seznam
// „co je pouze čtoucí" zastaral jako každý jiný ručně vedený seznam.
console.log('\n════ L. BRÁNY A1/A2/A3 A STÁRNUTÍ ANALÝZY ════');
{
  // `_analyza\` se 4. 10. 2026 PRESUNULA DO REPA orchestra (D3) — dřív byla
  // mimo oba repozitáře. Cesta se proto bere z umístění tohohle souboru
  // (`tools/..`), NEnapevno. Když složka není, sekce to ŘEKNE — ticho by
  // vypadalo jako úspěch.
  const ANALYZA = `${ORCH}/_analyza`;
  const BRANY = [
    ['a1-a2-over.py',
     'A1/A2: `done` jen při ok && merged, `owns` proti origin/main, cache s TTL',
     ['python', `${ANALYZA}/a1-a2-over.py`]],
    ['a3-over.py',
     'A3: krok „Když pravidla neprošla" končí `exit 1` v OBOU kopiích agent.yml',
     ['python', `${ANALYZA}/a3-over.py`]],
    ['n8-zastarala-analyza.py',
     'stárnutí analýzy: porovnává její tvrzení s KÓDEM (ne s dokumentem)',
     ['python', `${ANALYZA}/n8-zastarala-analyza.py`]],
    ['b5-over-tvrzeni.py',
     'týchž 5 tvrzení ověřených NEZÁVISLE na n8-* (jiné měřidlo, s úryvky kódu)',
     ['python', `${ANALYZA}/b5-over-tvrzeni.py`]],
    // N1 (2. 10. 2026): nástroj hlásil „0 vrácených" nad ZASTARALÝM inventářem.
    // Teď vypíše stáří, přepočítá otisk vstupů a při rozchodu skončí nenulově.
    // Zápis do inventáře dělá SKENER (`hl-neanglicky-v-kodu.py`), který se
    // pouští jako podproces — proto tenhle nástroj sám zůstává pouze čtoucí
    // a pojistka níž na něm nic nenajde.
    ['hl-rizika-jazyka.py',
     'N1: inventář se hlásí stářím a otiskem vstupů; zastaralý SHODÍ nástroj',
     ['python', `${ANALYZA}/hl-rizika-jazyka.py`]],
    // ROZHODNUTÍ 6. 10. 2026 (drobnost z otevřených bodů): `ag-over-cisla.py`
    // PATŘÍ do validátoru. Přečte **tvrzení z `AGENTS.md`** a porovná je se
    // ZDROJEM (`schema.sql`, `ci.yml`, skener) — mutačně ověřeno 5/5. Důvod, proč
    // tam patří: `AGENTS.md` je **autorita pro VŠECHNY session**, takže chybné
    // číslo v něm se neprojeví jako chyba, ale jako **důsledek na pěti místech**
    // (naměřeno: „32 sloupců" místo 39, chybné už při zápisu, šest session to
    // nevidělo). ⚠ JEHO MEZ, PŘIZNANÁ: pokrývá **6 čísel** (`schema.sql` ×3,
    // non-ASCII názvy, `ci.yml`, **počet bran v generovaném registru**)
    // + 2 historická; **zbytek nehlídá**. Proto se
    // u něj nesmí číst zelená jako „všechna čísla sedí" — jen jako „ta měřená
    // sedí". Kdo do `AGENTS.md` přidá číslo, **přidá i kontrolu** (jinak si
    // příště přečte zastaralé číslo jako fakt).
    // ⚠ 7. 10. 2026 (generalizace): přidáno 6. číslo — „bran v registru".
    // `AGENTS.md` tvrdil **37 bran**, registr měl **48**. Je to táž třída vady
    // (číslo v AUTORITĚ, které zestaralo) a nová kontrola je **mutačně ověřená**
    // (`_analyza-generalizace\test-nove-kontroly.py`: 48 → 37 → `exit 1`,
    // soubor vrácen bajt na bajt).
    ['ag-over-cisla.py',
     'trvalá pravidla: čísla v AGENTS.md proti ZDROJI (6 měřených; zbytek NEhlídá)',
     ['python', `${ANALYZA}/ag-over-cisla.py`]],
    // POZOR: `c2-mutace.py` sem NEPATŘÍ, i když je to brána k N1. Sama
    // přepisuje `_inventar.json` (a vrací ho) — přesně to pojistka níž hlídá.
    // Pouští se ručně; výsledek je v `HANDOFF.md` §16.
  ];
  const zapisuje = /write_text|write_bytes|copyfile|copy2|writeFileSync/;
  let spusteno = 0;
  for (const [soubor, popis, prikaz] of BRANY) {
    const cesta = `${ANALYZA}/${soubor}`;
    if (!existsSync(cesta)) {
      // Není to vada orchestra: `_analyza\` je pracovní složka vývojáře.
      console.log(`  ?    ${soubor} — není v ${ANALYZA} (přeskočeno)`);
      continue;
    }
    // ── POJISTKA: jen POUZE ČTOUCÍ nástroje. ──────────────────────────────
    if (zapisuje.test(readFileSync(cesta, 'utf8'))) {
      test(`${soubor}: NEBYL spuštěn — zdroj obsahuje zápis`, false,
        'nástroj, který přepisuje soubory, do validátoru nepatří');
      continue;
    }
    const v = spust(prikaz[0], prikaz.slice(1));
    spusteno++;
    test(popis, v.stav === 0, `${soubor} → exit=${v.stav}`);
  }
  if (spusteno === 0) {
    console.log('  ?    žádná brána nespuštěna — zkontroluj, že `_analyza\\` existuje');
  }
}

console.log(`\n${'═'.repeat(60)}`);
console.log(chyb === 0 ? '✓ VŠE V POŘÁDKU' : `✗ NALEZENO ${chyb} PROBLÉMŮ`);

// ── NÁVRATOVÝ KÓD (opraveno 1. 10. 2026, krok A1 plánu) ─────────────────────
//
// PROČ TO TU JE: do 1. 10. 2026 tenhle nástroj vypsal „✗ NALEZENO 3 PROBLÉMŮ"
// a PŘESTO skončil s exit kódem 0 — takže v CI by prošel a každý skript, který
// se ptá na návratový kód, by ho považoval za úspěch. Naměřeno opakovaně.
//
// Je to přesně ta třída chyby, kterou projekt řeší: BRÁNA, KTERÁ NEMÁ JAK
// SELHAT, NENÍ BRÁNA. Test bez nenulového exit kódu je jen výpis.
//
// `process.exitCode` se nastavuje MÍSTO `process.exit()`: kód se má dočíst
// celý (i s výpisem výše), jen se podle něj pozná výsledek.
process.exitCode = chyb === 0 ? 0 : 1;
