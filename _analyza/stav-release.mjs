// Ověří, co je SKUTEČNĚ v poznámkách živého release uo-shadows.
// Hypotéza: fix z F0 nahradil natvrdo špatný odkaz za natvrdo placeholdující
// text, který nikdo nenahrazuje → hráč dostane nefunkční URL.
import fs from 'node:fs';

const pat = fs.readFileSync('orchestra/.secrets/github_pat.txt', 'utf8').trim();
const h = { Authorization: 'Bearer ' + pat, 'User-Agent': 'forge-over', Accept: 'application/vnd.github+json' };

for (const repo of ['uo-shadows', 'forge-orchestra']) {
  const r = await fetch(`https://api.github.com/repos/ssevcikm-spec/${repo}/releases`, { headers: h });
  if (!r.ok) {
    console.log(`${repo}: HTTP ${r.status}`);
    continue;
  }
  const j = await r.json();
  console.log(`\n=== ${repo}: ${j.length} release ===`);
  for (const rel of j.slice(0, 2)) {
    console.log(`--- tag=${rel.tag_name} name="${rel.name}" created=${rel.created_at}`);
    const body = rel.body ?? '';
    console.log('    poznámky (prvních 600 znaků):');
    console.log(
      body
        .slice(0, 600)
        .split('\n')
        .map((l) => '      ' + l)
        .join('\n'),
    );
    const maPlaceholder = body.includes('NAZEV-REPA');
    const maSpravny = body.includes(`github.io/${repo}/`);
    console.log(`    >>> obsahuje 'NAZEV-REPA': ${maPlaceholder} | obsahuje správnou URL (github.io/${repo}/): ${maSpravny}`);
  }
}
