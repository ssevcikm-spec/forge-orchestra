import { readFileSync } from 'node:fs';
const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'h17' };
const jobs = await (await fetch(`https://api.github.com/repos/${REPO}/actions/runs/36999780638/jobs`, { headers: H })).json();
const job = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
const txt = await lg.text();
const lines = txt.split('\n').map((l) => l.replace(/^\S*Z\s?/, '').replace(/\x1b\[[0-9;]*m/g, ''));
const i = lines.findIndex((l) => /Kontroluji parsování/.test(l));
const j = lines.findIndex((l, k) => k > i && /Import assetů|##\[error\]/.test(l));
console.log('=== beh #145: krok Kontrola parsování ===');
for (const l of lines.slice(Math.max(0, i - 5), j < 0 ? i + 60 : j + 5)) {
  if (l.trim()) console.log('  ' + l.trim().slice(0, 160));
}
