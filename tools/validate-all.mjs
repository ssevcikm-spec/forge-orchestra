// Kompletni validace infrastruktury orchestra.
import { readFileSync, existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const GAME = 'C:/Users/Ssevc/Local-Deepseek/games/uo-shadows';
const GAMEREPO = 'ssevcikm-spec/uo-shadows';
const ORCHREPO = 'ssevcikm-spec/forge-orchestra';
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

console.log('════ A. CONDUCTOR (runtime) ════');
const h = await cond('/health');
test('conductor odpovídá', h.ok === true);
test('cron běží (čas)', !!h.time, h.time);
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
test('Godot pro worker existuje', (() => { try { return readFileSync(`${ORCH}/tools/godot/Godot_v4.7.2-stable_win64_console.exe`).length > 0; } catch { return false; } })());
test('.secrets má PAT', readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim().length > 20);

// ── J. ASSETY: REGISTR ZDROJŮ A BRÁNA NA LICENCE ─────────────────────────────
//
// PROČ SAMOSTATNÁ SEKCE: assety se dosud evidovaly jen hlavou. Registr
// (`assets/asset-registry.json`) a brána (`tools/check-licence.py`) jsou nové
// a musí být ověřené stejně jako zbytek pipeline – jinak by se licenční díra
// jen přesunula z hlavy do souboru, kterému nikdo nerozumí.
//
// POZOR NA SANDBOX: spouštíme s `stdio: 'inherit'`, ne s `pipe`. V DSH sandboxu
// podproces s pipovaným stdio spadne na `spawn EPERM` (ověřeno 30. 9. 2026) –
// a vypadalo by to jako vada testu, ne jako omezení prostředí. S `inherit`
// funguje obojí a stav je pořád spolehlivý.
const spust = (prikaz, parametry) => {
  const vysledek = spawnSync(prikaz, parametry, { stdio: 'inherit', cwd: `${ORCH}/..` });
  if (vysledek.error) return { stav: `chyba: ${vysledek.error.code || vysledek.error.message}` };
  return { stav: vysledek.status };
};

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
test('brána projde na skutečném klonu hry', spust('python', [`${ORCH}/tools/check-licence.py`, `${ORCH}/../games/uo-shadows`]).stav === 0);

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
  const kontrola = spust('python', [`${ORCH}/repo/.forge/check-schema.py`, `${ORCH}/../games/uo-shadows`]);
  // 0 = soulad, 1 = rozpory, 2 = chybí spec (nedá se měřit).
  // 2 NENÍ úspěch — „nemám co měřit" se nesmí počítat jako zelená.
  test('kontrola schématu se spustí (0 = soulad, 1 = rozpory, 2 = chybí spec)',
    [0, 1].includes(kontroly(kontrola)),
    `exit=${kontrola.stav}`);
  test('kontrola schématu je i v šabloně a v herním repu',
    existsSync(`${ORCH}/repo/.forge/check-schema.py`)
    && existsSync(`${ORCH}/../games/uo-shadows/.forge/check-schema.py`));

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

  const profilCesta = `${ORCH}/../games/uo-shadows/.forge/vision-profile.json`;
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
  // POZOR – TENHLE TEST JE DNES ČERVENÝ A JE TO SPRÁVNĚ: naměřil vadu **S12**
  // (nová granule se kvůli guardu na `updated_at` 3 h nevydá). Opravuje ji krok
  // **B1** plánu (`naposledy_selhalo`). Až se B1 udělá, test zčervená v opačném
  // směru a donutí scénář přepsat — takže nezůstane viset na staré pravdě.
  //
  // Kdyby to někdo potřeboval odlišit: `test-eskalace.py` je NAPROSTO V POŘÁDKU
  // (má `sys.exit(0 if vse_ok else 1)`); „lže zelenou" se týkalo JEN tohohle testu.
  const cooldown = spust('python', [`${ORCH}/tools/test-cooldown.py`]);
  test('cooldown guard: SQL ze zdrojáku + chování (dnes nachází vadu S12 → B1)',
    cooldown.stav === 0, `exit=${cooldown.stav}`);

  // ── BASELINE A LGTM CACHE ─────────────────────────────────────────────────
  // Bez baseline nelze měřit drift: „vypadá to jinak" je tvrzení, které se
  // nedá ověřit, dokud není s čím porovnávat. Testuje se tu jak logika
  // (offline testy), tak stav skutečné hry.
  const baseTesty = spust('python', [`${ORCH}/repo/.forge/baseline.py`, 'testy']);
  test('baseline.py: offline testy (včetně mezer phash) projdou',
    baseTesty.stav === 0, `exit=${baseTesty.stav}`);

  test('baseline.py je v šabloně i v herním repu',
    existsSync(`${ORCH}/repo/.forge/baseline.py`)
    && existsSync(`${ORCH}/../games/uo-shadows/.forge/baseline.py`));

  const stav = spust('python', [`${ORCH}/repo/.forge/baseline.py`,
                                '--koren', `${ORCH}/../games/uo-shadows`, 'stav']);
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
