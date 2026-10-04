#!/usr/bin/env node
// Stažení FREE assetu z evidovaného zdroje + zápis provenance (P1).
//
// PROČ TO EXISTUJE:
// Assety se dosud do her dostávaly ručně (Blender, SDXL, Gemini) a nikde nebylo
// zapsané, ODKUD jsou a pod jakou licencí. Zdrojů s CC0 je přitom dost a část
// z nich má i API (Poly Haven dává k souboru rovnou md5), takže stahování může
// být deterministické – a co je deterministické, nemá co dělat v LLM.
//
// KLÍČOVÉ ROZHODNUTÍ: tenhle nástroj NEVOLÁ ŽÁDNÝ MODEL. Fetch assetu je
// stahování a počítání hashe, ne rozhodování. Model dostane až hotový soubor
// a jeho cestu (granule typu `code`, která asset zapojí). Důvod je naměřený:
// free modely padají na formátu („SEARCH blok bez <<<<<<<"), ne na tom, že by
// nezvládly přečíst URL.
//
// CO ZAPISUJE:
//   <projekt>/assets/asset-lock.json   – co hra použila (soubor, zdroj, hash)
//   <projekt>/assets/CREDITS.md        – GENEROVANÝ z locku (kvůli CC-BY)
// Lock i CREDITS jsou deterministické (žádné datum) – jinak by brána
// „soubor neodpovídá tomu, co by se vygenerovalo" hlásila falešný poplach.
// Datum je jen v registru (kdy byla položka ověřena), ne v locku.
//
// POZOR NA LIMIT AUTO-MERGE: brána pouští změny do 60 řádků a počítá je
// z `gh pr view --json files`. Binárky (png/ogg/wav) hlásí GitHub jako 0/0,
// takže limit nespotřebují – ale asset-lock.json je text a počítá se CELÝ.
// Proto je formát locku kompaktní a proto se nestahují celé balíky.
//
// Použití:
//   node orchestra/tools/asset-fetch.mjs --seznam [--zdroj polyhaven] [--hledat kamen]
//   node orchestra/tools/asset-fetch.mjs --pak polyhaven/coast_sand_rocks_02 --projekt <cesta ke hře>
//   node orchestra/tools/asset-fetch.mjs --pak kenney/interface-sounds --extract "Audio/click1.ogg" --projekt <cesta>
//   node orchestra/tools/asset-fetch.mjs --overit            # přepočítá hashe v locku
//   node orchestra/tools/asset-fetch.mjs --registruj --nazev "..." --url https://... --licence cc0 --autor X --overeno
//
// Návratový kód: 0 = OK, 1 = chyba (nesouhlasí hash, nepovolená licence, chybí soubor).

import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, writeFileSync, statSync, readdirSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { inflateRawSync } from 'node:zlib';

const TADY = dirname(fileURLToPath(import.meta.url));
// P8l (presun na E:, 4. 10. 2026): `TADY` je <repo>/tools, takze koren
// repa je o jednu uroven vys a sourozenec (koren her) jeste o jednu.
const KOREN_ORCHESTRY = resolve(TADY, '..');      // root repa orchestra
const KOREN_HER = resolve(TADY, '..', '..');      // E:\\Workspaces
const _HRA_JMENO = process.env.FORGE_HRA || 'uo-shadows';
const _HRA = join(KOREN_HER, _HRA_JMENO);
const REGISTR = join(KOREN_ORCHESTRY, 'assets', 'asset-registry.json');

const args = process.argv.slice(2);
const hodnota = (n, vychozi = '') => {
  const i = args.indexOf(n);
  return i >= 0 && args[i + 1] ? args[i + 1] : vychozi;
};
const prepinac = (n) => args.includes(n);

const licencniAllowlist = () => {
  const r = nactiRegistr();
  return new Set((r.povolene_licence || []).map((l) => String(l).toLowerCase()));
};

// --------------------------------------------------------------- pomocné ----
function chyba(zprava) {
  console.error(`CHYBA: ${zprava}`);
  process.exit(1);
}

function nactiRegistr() {
  if (!existsSync(REGISTR)) chyba(`registr není: ${REGISTR}`);
  let data;
  try {
    data = JSON.parse(readFileSync(REGISTR, 'utf8'));
  } catch (e) {
    chyba(`registr nejde přečíst: ${String(e).slice(0, 200)}`);
  }
  if (!Array.isArray(data.assety)) chyba('registr nemá pole "assety"');
  return data;
}

function ulozRegistr(data) {
  writeFileSync(REGISTR, JSON.stringify(data, null, 2) + '\n', 'utf8');
}

/**
 * Povolí jen http/https. Bez téhle kontroly by šlo do registru (a tím do běhu
 * agenta) vložit file:// nebo jiné schéma a stáhnout cokoli z disku runneru.
 */
function overUrl(url) {
  let u;
  try {
    u = new URL(url);
  } catch {
    chyba(`není platná URL: ${url}`);
  }
  if (u.protocol !== 'https:' && u.protocol !== 'http:') {
    chyba(`povolené je jen http/https, ne ${u.protocol}`);
  }
  return u;
}

const hashSouboru = (cesta, algoritmus) =>
  createHash(algoritmus).update(readFileSync(cesta)).digest('hex');

const lidsky = (b) => (b > 1024 * 1024 ? `${(b / 1024 / 1024).toFixed(1)} MB` : `${Math.round(b / 1024)} kB`);

async function stahni(url) {
  overUrl(url);
  const res = await fetch(url, { redirect: 'follow', headers: { 'user-agent': 'forge-orchestra/1.0' } });
  if (!res.ok) chyba(`HTTP ${res.status} u ${url}`);
  return Buffer.from(await res.arrayBuffer());
}

// ---------------------------------------------------------------- lock ----
const cestaLocku = (projekt) => join(projekt, 'assets', 'asset-lock.json');

/**
 * Která hra? `--projekt` je nejjistější, ale ruční vypisování cesty je otrava
 * a snadno se splete (pak nástroj píše lock do orchestra místo do hry).
 * Proto se hledá klon hry pod `games/` – a když je jich víc, řekne to rovnou,
 * místo aby tiše sáhl po špatné.
 */
function najdiProjekt() {
  const zadany = hodnota('--projekt');
  if (zadany) return resolve(zadany);
  const koren = KOREN_HER;
  if (!existsSync(koren)) chyba('chybí --projekt a není tu ani složka games/');
  const hry = readdirSync(koren, { withFileTypes: true })
    .filter((d) => d.isDirectory() && existsSync(join(koren, d.name, '.forge', 'roadmap.json')))
    .map((d) => join(koren, d.name));
  if (hry.length === 1) return hry[0];
  if (!hry.length) chyba(`v ${koren} není žádný klon hry (poznám ji podle .forge/roadmap.json) – použij --projekt`);
  chyba(`v ${koren} je víc her (${hry.map((h) => h.split(/[\\/]/).pop()).join(', ')}) – použij --projekt`);
}

function nactiLock(projekt) {
  const cesta = cestaLocku(projekt);
  if (!existsSync(cesta)) {
    return {
      _generated: 'tools/asset-fetch.mjs – needituj ručně, přepíše se',
      verze: 1,
      povolene_licence: nactiRegistr().povolene_licence,
      soubory: [],
    };
  }
  try {
    const l = JSON.parse(readFileSync(cesta, 'utf8'));
    if (!Array.isArray(l.soubory)) l.soubory = [];
    return l;
  } catch (e) {
    chyba(`asset-lock.json nejde přečíst: ${String(e).slice(0, 200)}`);
  }
}

/** Zápis souboru do projektu – cesta se NESMÍ vymknout z projektu (žádné ../). */
function zapsatDoSouboru(projekt, relativniCesta, data) {
  if (relativniCesta.includes('..') || relativniCesta.startsWith('/') || /^[a-z]:/i.test(relativniCesta)) {
    chyba(`cesta se vymyká projektu: ${relativniCesta}`);
  }
  const cil = join(projekt, relativniCesta);
  mkdirSync(dirname(cil), { recursive: true });
  writeFileSync(cil, data);
  return cil;
}

/**
 * CREDITS.md se GENERUJE z locku. Důvod: kdyby byl ruční, rozešel by se
 * s lockem a u CC-BY by hra měla špatnou atribuci – a to je právní vada, ne
 * kosmetická. Díky generování stačí bráně porovnat soubor s očekávaným textem.
 */
function creditsText(lock) {
  const podleZdroje = new Map();
  for (const s of lock.soubory || []) {
    const klic = `${s.zdroj}|${s.licence}|${s.autor || 'neuveden'}`;
    if (!podleZdroje.has(klic)) podleZdroje.set(klic, []);
    podleZdroje.get(klic).push(s);
  }
  const radky = [
    '<!-- GENEROVÁNO: orchestra/tools/asset-fetch.mjs – needituj ručně -->',
    '# Poděkování a licence assetů',
    '',
    'Assety třetích stran použité v tomto projektu. U licencí CC-BY je uvedení',
    'autora PODMÍNKOU použití, proto tenhle soubor není dobrovolný.',
    '',
  ];
  for (const [klic, soubory] of [...podleZdroje.entries()].sort()) {
    const [zdroj, licence, autor] = klic.split('|');
    radky.push(`## ${zdroj} — ${licence.toUpperCase()}`);
    radky.push('');
    radky.push(`- Autor: ${autor}`);
    if (soubory[0].url) radky.push(`- Zdroj: ${soubory[0].url}`);
    if (soubory[0].web) radky.push(`- Web: ${soubory[0].web}`);
    radky.push(`- Soubory (${soubory.length}):`);
    for (const s of soubory.map((x) => x.soubor).sort()) radky.push(`  - \`${s}\``);
    radky.push('');
  }
  radky.push('## Vlastní a vygenerované assety');
  radky.push('');
  radky.push('Assety vzniklé v projektu (Blender, SDXL/ComfyUI, Gemini) jsou uvedené');
  radky.push('v `asset-lock.json` se zdrojem `vlastni` a licencí projektu.');
  radky.push('');
  return radky.join('\n');
}

function ulozLockACredits(projekt, lock) {
  lock.soubory.sort((a, b) => a.soubor.localeCompare(b.soubor));
  const lockCesta = cestaLocku(projekt);
  mkdirSync(dirname(lockCesta), { recursive: true });
  writeFileSync(lockCesta, JSON.stringify(lock, null, 2) + '\n', 'utf8');
  const creditsCesta = join(projekt, 'assets', 'CREDITS.md');
  writeFileSync(creditsCesta, creditsText(lock), 'utf8');
  console.log(`zapsáno: ${relative(projekt, lockCesta)} (${lock.soubory.length} souborů)`);
  console.log(`zapsáno: ${relative(projekt, creditsCesta)}`);
}

/** Záznam do locku – s kontrolou licence a s tím, že nepřepíše cizí záznam. */
function pridejZaznam(lock, zaznam) {
  if (!licencniAllowlist().has(String(zaznam.licence).toLowerCase())) {
    chyba(`licence "${zaznam.licence}" není v povoleném seznamu (${[...licencniAllowlist()].join(', ')})`);
  }
  const i = lock.soubory.findIndex((s) => s.soubor === zaznam.soubor);
  if (i >= 0) {
    if (lock.soubory[i].hash !== zaznam.hash) {
      console.log(`  přepis: ${zaznam.soubor} byl v locku s jiným hashem (${lock.soubory[i].hash.slice(0, 8)} → ${zaznam.hash.slice(0, 8)})`);
    }
    lock.soubory[i] = zaznam;
  } else {
    lock.soubory.push(zaznam);
  }
}

// ------------------------------------------------------------- polyhaven ----
/**
 * Poly Haven: hash i velikost bereme Z API, ne z hlavičky odpovědi.
 * Tím se ověřuje i to, že obsah na CDN odpovídá tomu, co API tvrdí – kdyby
 * Poly Haven něco přegeneroval, poznáme to hned a ne až ve hře.
 */
async function vyberPolyHaven(asset, esc) {
  const apiUrl = `https://api.polyhaven.com/files/${encodeURIComponent(asset)}`;
  const res = await fetch(apiUrl, { headers: { 'user-agent': 'forge-orchestra/1.0' } });
  if (!res.ok) chyba(`Poly Haven API ${res.status} pro ${asset}`);
  const data = await res.json();
  const mapa = data[esc.map];
  if (!mapa) chyba(`mapa "${esc.map}" u ${asset} není (jsou: ${Object.keys(data).join(', ')})`);
  const uroven = mapa[esc.rozliseni];
  if (!uroven) chyba(`rozlišení "${esc.rozliseni}" u ${asset}/${esc.map} není (jsou: ${Object.keys(mapa).join(', ')})`);
  const soubor = uroven[esc.format];
  if (!soubor || !soubor.url) {
    chyba(`formát "${esc.format}" u ${asset}/${esc.map}/${esc.rozliseni} není (jsou: ${Object.keys(uroven).join(', ')})`);
  }
  return { url: soubor.url, md5: soubor.md5 || '', velikost: soubor.size || 0, apiUrl, include: soubor.include || null };
}

// ------------------------------------------------------------------ kenney ----
/**
 * Minimální čtení ZIPu (jen centrální adresář + stored/deflate záznamy).
 * PROČ NE NĚJAKÁ KNIHOVNA: orchestra nemá závislosti a přidávat ZIP knihovnu
 * kvůli jednomu balíčku by znamenalo další místo, které zestárne. Potřebujeme
 * jen vypsat obsah a vybalit vybrané soubory.
 */
function ctiZip(buffer) {
  // Najdi End of Central Directory (podpis 0x06054b50) od konce.
  let eocd = -1;
  for (let i = buffer.length - 22; i >= Math.max(0, buffer.length - 66000); i--) {
    if (buffer.readUInt32LE(i) === 0x06054b50) { eocd = i; break; }
  }
  if (eocd < 0) chyba('ZIP: nenašel jsem konec centrálního adresáře');
  const pocet = buffer.readUInt16LE(eocd + 10);
  let offset = buffer.readUInt32LE(eocd + 16);
  const soubory = [];
  for (let i = 0; i < pocet; i++) {
    if (buffer.readUInt32LE(offset) !== 0x02014b50) chyba('ZIP: poškozený centrální adresář');
    const metoda = buffer.readUInt16LE(offset + 10);
    const komprimovano = buffer.readUInt32LE(offset + 20);
    const rozmbaleno = buffer.readUInt32LE(offset + 24);
    const delkaJmena = buffer.readUInt16LE(offset + 28);
    const delkaExtra = buffer.readUInt16LE(offset + 30);
    const delkaKomentare = buffer.readUInt16LE(offset + 32);
    const lokalniOffset = buffer.readUInt32LE(offset + 42);
    const jmeno = buffer.toString('utf8', offset + 46, offset + 46 + delkaJmena);
    soubory.push({ jmeno, metoda, komprimovano, rozmbaleno, lokalniOffset });
    offset += 46 + delkaJmena + delkaExtra + delkaKomentare;
  }
  return soubory;
}

function vybalZeZipu(buffer, zaznam) {
  const o = zaznam.lokalniOffset;
  if (buffer.readUInt32LE(o) !== 0x04034b50) chyba(`ZIP: špatná lokální hlavička u ${zaznam.jmeno}`);
  const delkaJmena = buffer.readUInt16LE(o + 26);
  const delkaExtra = buffer.readUInt16LE(o + 28);
  const start = o + 30 + delkaJmena + delkaExtra;
  const data = buffer.subarray(start, start + zaznam.komprimovano);
  let vystup;
  if (zaznam.metoda === 0) {
    vystup = Buffer.from(data);
  } else if (zaznam.metoda === 8) {
    // Metoda 8 = deflate BEZ zlib hlavičky → inflateRawSync (ne inflateSync).
    vystup = inflateRawSync(data);
  } else {
    chyba(`ZIP: nepodporovaná komprese ${zaznam.metoda} u ${zaznam.jmeno}`);
  }
  // Kontrola velikosti z centrálního adresáře: kdyby se dekomprese utrhla,
  // poznali bychom to tady a ne až ve hře (rozbitý .ogg se pozná špatně).
  if (zaznam.rozmbaleno && vystup.length !== zaznam.rozmbaleno) {
    chyba(`ZIP: ${zaznam.jmeno} má po rozbalení ${vystup.length} B, adresář tvrdí ${zaznam.rozmbaleno} B`);
  }
  return vystup;
}

/** Hvězdičkový filtr na cestu v ZIPu ("Audio/*.ogg"). */
function filtr(path, vzor) {
  if (!vzor) return false;
  const re = new RegExp('^' + vzor.split('*').map((c) => c.replace(/[.+?^${}()|[\]\\]/g, '\\$&')).join('.*') + '$', 'i');
  return re.test(path);
}

// ------------------------------------------------------------- režimy ----
function tiskSeznamu() {
  const r = nactiRegistr();
  const zdroj = hodnota('--zdroj');
  const hledat = hodnota('--hledat').toLowerCase();
  const assety = r.assety.filter((a) => (!zdroj || a.zdroj === zdroj)
    && (!hledat || `${a.id} ${a.nazev} ${a.typ}`.toLowerCase().includes(hledat)));
  console.log(`registr: ${REGISTR}`);
  console.log(`zdrojů: ${r.zdroje.length}, assetů: ${r.assety.length}, vybráno: ${assety.length}\n`);
  for (const a of assety) {
    const stav = a.overeno ? 'OVĚŘENO' : 'neověřeno';
    console.log(`  ${a.id}`);
    console.log(`    ${a.nazev} — ${a.typ}, ${a.licence}, ${stav}${a.velikost ? `, ${lidsky(a.velikost)}` : ''}`);
    if (a.poznamka) console.log(`    ${a.poznamka}`);
  }
  console.log('\nzdroje:');
  for (const z of r.zdroje) {
    console.log(`  ${z.id.padEnd(14)} ${z.licence.padEnd(14)} strojově: ${z.strojove ? 'ano' : 'NE'}  ${z.web || ''}`);
  }
}

/** Ověří hash v locku proti souborům na disku. Nic nestahuje. */
function overLock(projekt) {
  const lock = nactiLock(projekt);
  if (!lock.soubory.length) {
    console.log(`lock je prázdný (${relative(projekt, cestaLocku(projekt))})`);
    return 0;
  }
  let chyb = 0;
  for (const s of lock.soubory) {
    const cil = join(projekt, s.soubor);
    if (!existsSync(cil)) {
      console.log(`  CHYBÍ   ${s.soubor}`);
      chyb++;
      continue;
    }
    const skutecny = hashSouboru(cil, s.algoritmus || 'sha256');
    if (skutecny !== s.hash) {
      console.log(`  ZMĚNĚNO ${s.soubor}`);
      console.log(`          v locku:   ${s.hash}`);
      console.log(`          na disku:  ${skutecny}`);
      chyb++;
    } else {
      console.log(`  OK      ${s.soubor} (${s.algoritmus})`);
    }
  }
  console.log(chyb ? `\n${chyb} soubor(ů) nesouhlasí` : '\nvše souhlasí');
  return chyb ? 1 : 0;
}

/** Zaeviduje už stažený soubor (ruční zdroje: OpenGameArt, Freesound, Mixamo). */
function registruj(projekt) {
  const relativni = hodnota('--soubor') || chyba('chybí --soubor (cesta v projektu, např. assets/audio/coin.wav)');
  const cil = join(projekt, relativni);
  if (!existsSync(cil)) chyba(`soubor v projektu není: ${cil}`);
  const licence = hodnota('--licence') || chyba('chybí --licence (cc0 | cc-by | ofl | mit | public-domain)');
  const zdroj = hodnota('--zdroj') || 'rucni';
  const lock = nactiLock(projekt);
  pridejZaznam(lock, {
    soubor: relativni.replace(/\\/g, '/'),
    zdroj,
    licence: licence.toLowerCase(),
    autor: hodnota('--autor', 'neuveden'),
    url: hodnota('--url', ''),
    web: hodnota('--web', ''),
    algoritmus: 'sha256',
    hash: hashSouboru(cil, 'sha256'),
    velikost: statSync(cil).size,
    overeno: true,
  });
  ulozLockACredits(projekt, lock);
  console.log('záznam přidán ručnímu zdroji – licence i autor se berou z toho, co jsi zadal.');
  return 0;
}

// -------------------------------------------------------------- stahování ----
async function stahniPak(projekt) {
  const id = hodnota('--pak') || chyba('chybí --pak <id assetu z registru>');
  const registr = nactiRegistr();
  const asset = registr.assety.find((a) => a.id === id);
  if (!asset) chyba(`asset "${id}" v registru není (viz --seznam)`);
  if (!licencniAllowlist().has(String(asset.licence).toLowerCase())) {
    chyba(`licence "${asset.licence}" není povolená`);
  }
  const lock = nactiLock(projekt);
  console.log(`asset: ${asset.id} (${asset.nazev}) — ${asset.licence}, ${asset.zdroj}`);

  if (asset.zdroj === 'polyhaven') {
    const esc = asset.esc || {};
    const vyber = await vyberPolyHaven(id.split('/')[1], esc);
    console.log(`  API: ${vyber.apiUrl}`);
    console.log(`  soubor: ${vyber.url}`);
    console.log(`  očekáváno: ${lidsky(vyber.velikost)}, md5 ${vyber.md5}`);
    const data = await stahni(vyber.url);
    const md5 = createHash('md5').update(data).digest('hex');
    if (vyber.md5 && md5 !== vyber.md5) {
      chyba(`md5 NESOUHLASÍ – obsah na CDN se změnil.\n  API:     ${vyber.md5}\n  staženo: ${md5}`);
    }
    if (vyber.velikost && data.length !== vyber.velikost) {
      chyba(`velikost NESOUHLASÍ: API ${vyber.velikost} vs staženo ${data.length}`);
    }
    const nazevSouboru = vyber.url.split('/').pop();
    const kam = (asset.kam || 'assets/').replace(/\/?$/, '/');
    const relativni = `${kam}${nazevSouboru}`;
    zapsatDoSouboru(projekt, relativni, data);
    console.log(`  staženo a ověřeno (${lidsky(data.length)}) → ${relativni}`);
    pridejZaznam(lock, {
      soubor: relativni,
      zdroj: 'polyhaven',
      licence: asset.licence,
      autor: asset.autor || 'Poly Haven',
      web: registr.zdroje.find((z) => z.id === 'polyhaven')?.web || '',
      url: vyber.url,
      algoritmus: 'md5',
      hash: md5,
      velikost: data.length,
      overeno: true,
    });
    // Modely mají textury v "include" – bez nich je .gltf/.fbx neúplný.
    if (vyber.include && !prepinac('--bez-textur')) {
      for (const [rel, info] of Object.entries(vyber.include)) {
        const jmeno = rel.split('/').pop();
        const cilRel = `${kam}${nazevSouboru.replace(/\.[a-z0-9]+$/i, '')}_${jmeno}`;
        const t = await stahni(info.url);
        const tmd5 = createHash('md5').update(t).digest('hex');
        if (info.md5 && tmd5 !== info.md5) chyba(`md5 textury ${jmeno} nesouhlasí`);
        zapsatDoSouboru(projekt, cilRel, t);
        console.log(`  + textura ${cilRel} (${lidsky(t.length)})`);
        pridejZaznam(lock, {
          soubor: cilRel, zdroj: 'polyhaven', licence: asset.licence,
          autor: asset.autor || 'Poly Haven', url: info.url,
          algoritmus: 'md5', hash: tmd5, velikost: t.length, overeno: true,
        });
      }
    }
    ulozLockACredits(projekt, lock);
    return 0;
  }

  if (asset.zdroj === 'kenney') {
    const data = await stahni(asset.url);
    const sha = createHash('sha256').update(data).digest('hex');
    if (asset.sha256 && asset.sha256 !== 'SEM_DOPLNI_SHA256' && sha !== asset.sha256) {
      chyba(`sha256 balíčku NESOUHLASÍ – Kenney balíček přegeneroval.\n  registr: ${asset.sha256}\n  staženo: ${sha}\n  → ověř, že jde opravdu o stejný balíček, a teprve pak hash v registru přepiš.`);
    }
    console.log(`  balíček ověřen: ${lidsky(data.length)}, sha256 ${sha.slice(0, 16)}…`);
    const obsah = ctiZip(data).filter((z) => !z.jmeno.endsWith('/'));
    console.log(`  v balíčku ${obsah.length} souborů`);
    const vzory = [];
    const zCli = hodnota('--extract');
    if (zCli) vzory.push(zCli);
    for (const v of asset.extract || []) vzory.push(v);
    if (!vzory.length) {
      console.log('  (nic se nevybaluje – přidej --extract "Audio/*.ogg")');
      for (const z of obsah.slice(0, 40)) console.log(`    ${z.jmeno}`);
      if (obsah.length > 40) console.log(`    … a dalších ${obsah.length - 40}`);
      return 0;
    }
    const vybrane = obsah.filter((z) => vzory.some((v) => filtr(z.jmeno, v)));
    if (!vybrane.length) chyba(`filtr nic nevybral (${vzory.join(', ')}) – podívej se na obsah balíčku bez --extract`);
    const kam = (asset.kam || 'assets/').replace(/\/?$/, '/');
    for (const z of vybrane) {
      const jmeno = z.jmeno.split('/').pop();
      const relativni = `${kam}${jmeno}`;
      const bajty = vybalZeZipu(data, z);
      zapsatDoSouboru(projekt, relativni, bajty);
      console.log(`  vybaleno ${z.jmeno} → ${relativni} (${lidsky(bajty.length)})`);
      pridejZaznam(lock, {
        soubor: relativni,
        zdroj: 'kenney',
        licence: asset.licence,
        autor: asset.autor || 'Kenney',
        web: registr.zdroje.find((z2) => z2.id === 'kenney')?.web || '',
        url: asset.url,
        balicek: asset.id,
        algoritmus: 'sha256',
        hash: createHash('sha256').update(bajty).digest('hex'),
        velikost: bajty.length,
        overeno: true,
      });
    }
    ulozLockACredits(projekt, lock);
    return 0;
  }

  if (asset.zdroj === 'google-fonts') {
    const data = await stahni(asset.url);
    const sha = createHash('sha256').update(data).digest('hex');
    const kam = (asset.kam || 'assets/fonts/').replace(/\/?$/, '/');
    const relativni = `${kam}${asset.url.split('/').pop()}`;
    zapsatDoSouboru(projekt, relativni, data);
    console.log(`  staženo ${lidsky(data.length)} → ${relativni}`);
    pridejZaznam(lock, {
      soubor: relativni, zdroj: 'google-fonts', licence: asset.licence,
      autor: asset.autor || 'viz OFL', web: asset.web || 'https://fonts.google.com',
      url: asset.url, algoritmus: 'sha256', hash: sha, velikost: data.length, overeno: true,
    });
    ulozLockACredits(projekt, lock);
    return 0;
  }

  chyba(`zdroj "${asset.zdroj}" tenhle nástroj neumí stáhnout (ruční zdroje se evidují přes --registruj)`);
}

// ------------------------------------------------------------------ main ----
async function main() {
  // Projekt se hledá, JEN když ho režim potřebuje – jinak by `--seznam`
  // spadl na „není tu žádná hra", což s výpisem registru nemá co dělat.
  if (prepinac('--seznam') || args.length === 0) {
    tiskSeznamu();
    return 0;
  }
  if (prepinac('--registruj')) return registruj(najdiProjekt());
  if (prepinac('--overit')) return overLock(najdiProjekt());
  if (hodnota('--pak')) {
    const projekt = najdiProjekt();
    if (!existsSync(join(projekt, 'assets'))) {
      chyba(`projekt nemá složku assets/: ${projekt}`);
    }
    return await stahniPak(projekt);
  }
  console.error('nevím, co dělat. Viz --seznam nebo hlavička souboru.');
  return 1;
}

main()
  .then((kod) => process.exit(kod || 0))
  .catch((e) => {
    // Síťové chyby musí být vidět celé – tady se ladí, ne produkuje.
    console.error(`CHYBA: ${e && e.stack ? e.stack : String(e)}`);
    process.exit(1);
  });
