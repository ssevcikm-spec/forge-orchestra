#!/usr/bin/env node
// Které soubory má agent EDITOVAT (ne jen číst)?
//
// PROČ TO EXISTUJE (root cause 0% úspěšnosti, naměřeno 30. 9. 2026):
//
// Workflow pouštěl aider jen s `--read CONVENTIONS.md`. Tím se soubory dostaly
// do repo-mapy (READ-ONLY), ale NE do chatu jako editovatelné. Aider má ve
// svém promptu pravidlo „Only create SEARCH/REPLACE blocks for files that the
// user has added to the chat!" – takže model správně odmítl editovat a napsal
// „Please add the file's content to the chat". Přesně to udělaly VŠECHNY
// modely (mistral 17–36 tokenů, cerebras 179–204 tokenů).
//
// Vysvětluje to i vzorec úspěch/neúspěch: granule, které soubor jen VYTVÁŘELY
// (attributes.gd, item.gd), prošly – na nový soubor žádný SEARCH blok není
// potřeba. Granule, které existující soubor UPRAVOVALY (skills.gd, world.gd,
// economy.gd), selhaly VŽDY, bez ohledu na model.
//
// Výstup: seznam cest (jedna na řádek) pro `aider --file <cesta>`.
//
// Použití:
//   node .forge/files-to-edit.mjs --grain core.skills
//   node .forge/files-to-edit.mjs --prompt "V scripts/skills.gd vytvoř …"

import { readFileSync, existsSync } from 'node:fs';

const args = process.argv.slice(2);
const hodnota = (n) => {
  const i = args.indexOf(n);
  return i >= 0 ? args[i + 1] : '';
};
const grain = hodnota('--grain');
const prompt = hodnota('--prompt');
const roadmapCesta = hodnota('--roadmap') || '.forge/roadmap.json';

const vydat = (seznam, odkud) => {
  const ciste = [...new Set(seznam)]
    .map((f) => String(f).trim())
    .filter((f) => f && !f.includes('..') && !f.startsWith('/'))
    // Do chatu patří jen soubory, které smí agent měnit.
    .filter((f) => /\.(gd|json|md|cfg|tscn|tres|godot)$/.test(f));
  if (ciste.length) {
    console.error(`[files-to-edit] ${ciste.length} soubor(ů) z ${odkud}`);
    console.log(ciste.join('\n'));
  } else {
    console.error(`[files-to-edit] žádný soubor nenalezen (${odkud})`);
  }
  process.exit(0);
};

// 1) Nejpřesnější: `owns` granule z roadmapy (conductor podle něj zamyká souběh,
//    takže je to i deklarace „tenhle soubor granule vlastní").
if (grain && existsSync(roadmapCesta)) {
  try {
    const data = JSON.parse(readFileSync(roadmapCesta, 'utf8'));
    const vsechny = data.grains || data.tasks || [];
    const g = vsechny.find((x) => x.id === grain);
    if (g && Array.isArray(g.owns) && g.owns.length) {
      vydat(g.owns, `owns granule ${grain} v ${roadmapCesta}`);
    }
  } catch (e) {
    console.error(`[files-to-edit] roadmapu nejde přečíst: ${String(e).slice(0, 120)}`);
  }
}

// 2) Záloha: cesty zmíněné v zadání. Modely i roadmapa je píšou jako
//    `scripts/neco.gd`, takže se hledá tenhle tvar.
if (prompt) {
  const najdene = prompt.match(/\b(?:scripts|assets|tests|tools)\/[\w./-]+\.\w+/g) || [];
  if (najdene.length) vydat(najdene, 'zadání (prompt)');
}

console.error('[files-to-edit] nic k editaci – agent dostane jen zadání');
process.exit(0);
