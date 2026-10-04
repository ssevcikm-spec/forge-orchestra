# Ověří, že při přepisu HANDOFF.md nic nezmizelo.
# Kontroluje KLÍČOVÁ SLOVA otevřených bodů ze STARÉHO handoffu proti novému.
# Vzor: AGENTS.md — „Po přepisu vypiš, které body zůstaly, a ověř je hledáním."
import io
import sys

NOVY = 'HANDOFF.md'

# (popis bodu ze starého handoffu, [klíčová slova, z nichž ASPOŇ JEDNO musí být v novém])
BODY = [
    ('N0.2 brána na závislosti bran', ['N0.2']),
    ('N0.3 stav CI v /health', ['N0.3']),
    ('test-cooldown lže zelenou', ['test-cooldown']),
    ('test-eskalace lže zelenou', ['test-eskalace']),
    ('tři verze vision.test.mjs', ['vision.test.mjs']),
    ('root vision.test.mjs kandidát na smazání', ['root']),
    ('3h zpoždění nové granule', ['naposledy_selhalo', '3h', '3 h']),
    ('obcházení cooldownu přes /report', ['/report']),
    ('strop/watchdog na granuli', ['watchdog']),
    ('fallback listGames', ['listGames']),
    ('komentář MAX_ATTEMPTS v index.ts', ['MAX_ATTEMPTS']),
    ('tajemství bez izolovaných ACL', ['ACL']),
    ('tři plány k revizi', ['PLAN-ORCHESTRA-AI-AGENTI', 'PLAN-SEPARACE']),
    ('bootstrap objektů ve hře (deferred)', ['bootstrap', 'spawn']),
    ('sprites.json zastaralý (deferred)', ['sprites.json']),
    ('--resolution 480x270 (deferred)', ['480x270']),
    ('blender: a FORGE_CMD (deferred)', ['FORGE_CMD']),
    ('domácí uzel pc-domaci', ['pc-domaci']),
    ('LGTM / mrtvé brány (N11)', ['LGTM']),
    ('vize: role worker/judge', ['worker']),
    ('acceptance/provides nečte nikdo', ['acceptance']),
    ('grep 80 ku 0 (N6)', ['80']),
    ('orchestra 73,4 % workspace (N5)', ['73,4']),
    ('verify-setup 9 složek (N8)', ['verify-setup']),
    ('Z8/Z9 nehotové dokumenty', ['Z8', 'Z9']),
    ('open: push na GitHub', ['push', 'origin/main']),
    ('baseline LGTM 272', ['272']),
    ('forge-quest je živá hra', ['forge-quest']),
    ('ovládání commitů: nepushovat bez vyžádání', ['bez vyžádání']),
]

with io.open(NOVY, encoding='utf-8') as f:
    text = f.read()
nizky = text.lower()

chybi = []
for popis, klice in BODY:
    nalezeno = [k for k in klice if k.lower() in nizky]
    if not nalezeno:
        chybi.append((popis, klice))
    else:
        print('  OK   %-42s (%s)' % (popis, ', '.join(nalezeno)))

print()
if chybi:
    print('CHYBI %d BODU:' % len(chybi))
    for popis, klice in chybi:
        print('  CHYBI  %-40s hledano: %s' % (popis, klice))
    sys.exit(1)
print('VŠE OK — %d kontrolovaných bodů, 0 chybějících.' % len(BODY))
sys.exit(0)
