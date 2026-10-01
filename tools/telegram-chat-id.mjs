#!/usr/bin/env node
// Zjistí chat_id pro Telegram bota – bez něj conductor neví, komu psát.
//
// Použití:
//   node tools/telegram-chat-id.mjs                 (token vezme z .secrets/telegram_bot_token.txt)
//   node tools/telegram-chat-id.mjs <token>
//
// DŮLEŽITÉ: nejdřív musíš botovi v Telegramu poslat zprávu (třeba "ahoj").
// Do té doby getUpdates nic nevrátí.
//
// Token se nikam neposílá kromě api.telegram.org a nikdy se nevypisuje.

import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));       // orchestra\tools
const ORCH = join(HERE, '..');                              // orchestra
const TOKEN_FILE = join(ORCH, '.secrets', 'telegram_bot_token.txt');

const token = (process.argv[2] || (existsSync(TOKEN_FILE) ? readFileSync(TOKEN_FILE, 'utf8') : '')).trim();
if (!token) {
  console.error('Chybí token. Ulož ho do .secrets/telegram_bot_token.txt nebo ho předej argumentem.');
  console.error('Token dostaneš od @BotFather v Telegramu (příkaz /newbot).');
  process.exit(2);
}

const res = await fetch(`https://api.telegram.org/bot${token}/getUpdates`);
const data = await res.json().catch(() => ({}));

if (!data.ok) {
  console.error(`Telegram odpověděl chybou: ${data.description || res.status}`);
  console.error('Nejčastější příčina: překlep v tokenu, nebo bot ještě neexistuje.');
  process.exit(1);
}

const chats = new Map();
for (const update of data.result || []) {
  const m = update.message || update.channel_post || update.edited_message;
  const chat = m?.chat;
  if (chat) {
    const name = [chat.first_name, chat.last_name].filter(Boolean).join(' ')
      || chat.title || chat.username || '(bez jména)';
    chats.set(String(chat.id), `${name} (${chat.type})`);
  }
}

if (!chats.size) {
  console.log('Zatím žádné zprávy. Napiš svému botovi v Telegramu cokoli (třeba "ahoj") a spusť to znovu.');
  process.exit(0);
}

console.log('Nalezené chaty:');
for (const [id, name] of chats) console.log(`  ${id}  ${name}`);
console.log('\nNastav chat_id v Cloudflare (jedna z možností):');
console.log('  .\\wrangler.cmd secret put TELEGRAM_CHAT_ID     (vložíš hodnotu z výpisu výše)');
console.log('nebo si o to řekni agentovi a nastaví ho za tebe.');
