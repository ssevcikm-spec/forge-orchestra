<#
.SYNOPSIS
  Připraví obsah repa hry: zkopíruje orchestraci (.forge, .github) a vygenerovaný
  Godot projekt do cílové složky, kterou pak pushneš na GitHub.

.POUŽITÍ
  # 1) suchý běh – jen vypíše, co by udělal
  .\install-into-repo.ps1 -Target C:\Users\Ssevc\Local-Deepseek\games\uo-shadows -WhatIfOnly

  # 2) ostrý běh
  .\install-into-repo.ps1 -Target C:\Users\Ssevc\Local-Deepseek\games\uo-shadows -Project demo1

  # POZOR: příklady dřív mířily na `…\forge-quest`. To je JINÝ, ŽIVÝ repozitář
  # s vlastní hrou i GitHub Pages – orchestra na něm nic nevyvíjí. Cíl patří
  # do `games\<nazev>` a dnes je to `games\uo-shadows`.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Target,
    [string]$Project = 'demo1',
    [switch]$WhatIfOnly,
    [switch]$Force,
    # -Force povoluje nahrát do NEPRÁZDNÉ složky (běžné re-nahrání).
    # -OverwriteAgentWork navíc povoluje přepsat i práci cloudových agentů –
    # to je záměrně jiný přepínač, aby se to nestalo omylem. Dřív jsem pojistku
    # vázal na -Force, jenže re-nahrání bez -Force nejde vůbec, takže by se
    # nikdy neuplatnila (odhalil to test).
    [switch]$OverwriteAgentWork
)

$ErrorActionPreference = 'Stop'
$Orch = $PSScriptRoot
$Forge = Split-Path $Orch -Parent
$ProjDir = Join-Path (Join-Path $Forge 'projects') $Project

if (-not (Test-Path (Join-Path $ProjDir 'project.godot'))) {
    throw "Projekt '$Project' neexistuje ($ProjDir). Založ ho: forge new $Project"
}

$plan = @(
    @{ From = (Join-Path $Orch 'repo\.forge');            To = (Join-Path $Target '.forge') },
    @{ From = (Join-Path $Orch 'repo\.github');           To = (Join-Path $Target '.github') },
    # Konvence pro agenty: workflow je čte přes `aider --read CONVENTIONS.md`,
    # takže když soubor v repu chybí, agent spadne. Proto se kopíruje taky –
    # dřív se na něj zapomnělo (kopírovaly se jen .forge a .github).
    @{ From = (Join-Path $Orch 'repo\CONVENTIONS.md');    To = (Join-Path $Target 'CONVENTIONS.md') },
    @{ From = $ProjDir;                                   To = $Target }
)

Write-Host "Cíl: $Target" -ForegroundColor Cyan
foreach ($p in $plan) {
    Write-Host ("  {0}  ->  {1}" -f $p.From, $p.To)
}
if ($WhatIfOnly) {
    Write-Host "`n(suchý běh – nic se nekopíruje)" -ForegroundColor Yellow
    return
}

if ((Test-Path $Target) -and -not $Force) {
    $existing = Get-ChildItem $Target -Force -ErrorAction SilentlyContinue
    if ($existing) {
        throw "Cíl $Target už není prázdný. Použij -Force, nebo zvol jinou složku."
    }
}
New-Item -ItemType Directory -Force -Path $Target | Out-Null

# ---------------------------------------------------------------------------
# POJISTKA: nepřepsat práci agentů.
# Hra má dva obrazy – tenhle lokální projekt a repo, kde pracují cloudoví
# agenti. Když se lokální projekt nahraje do repa, jejich změny zmizí. Skript
# si proto pamatuje, jaký commit v repu byl při minulém nahrání; když je teď
# v repu něco novějšího, znamená to práci agenta a nahrání se odmítne.
# (Přenést si ji do projektu umí: forge pull <projekt> --repo "$Target" --fetch)
# ---------------------------------------------------------------------------
$stateFile = Join-Path $Orch '.state\last-stage.json'
$headNow = ''
try { $headNow = (& git -C $Target rev-parse HEAD 2>$null | Select-Object -First 1) } catch { }
if ((Test-Path $stateFile) -and -not $OverwriteAgentWork -and $headNow) {
    $st = (Get-Content $stateFile -Raw) | ConvertFrom-Json
    if ($st.target -eq $Target -and $st.head -and $st.head -ne $headNow) {
        throw @"
V repu $Target jsou NOVĚJŠÍ commity, než jaké tam byly při minulém nahrání.
To je skoro jistě práce agenta – a tohle nahrání by ji přepsalo.

Jak pokračovat:
  1) přenes si ji do projektu:  forge.cmd pull <projekt> --repo "$Target" --fetch
  2) pak teprve nahrávej znovu (s -Force).
Když opravdu chceš práci agenta přepsat, přidej -OverwriteAgentWork.
"@
    }
}

# .forge a .github (adresáře) + CONVENTIONS.md (jednotlivý soubor)
foreach ($p in $plan[0..1]) {
    New-Item -ItemType Directory -Force -Path $p.To | Out-Null
    Copy-Item (Join-Path $p.From '*') $p.To -Recurse -Force
}
$conv = $plan[2]
if (Test-Path $conv.From) {
    Copy-Item $conv.From $conv.To -Force
} else {
    throw "Chybí $($conv.From) – bez něj agent v CI spadne na --read CONVENTIONS.md"
}

# Projekt hry – bez cache a bez mezivýstupů
$skip = @('.godot', 'build', 'artifacts', '_raw', '.git', '.aider.tags.cache.v4', '.aider.chat.history.md', '.aider.input.history')
Get-ChildItem $ProjDir -Force | Where-Object { $skip -notcontains $_.Name -and -not $_.Name.StartsWith('.aider') } | ForEach-Object {
    if ($_.PSIsContainer) {
        Copy-Item $_.FullName $Target -Recurse -Force
    } else {
        Copy-Item $_.FullName $Target -Force
    }
}

# .gitignore – co se do repa neposílá
$gitignore = @'
# Godot
.godot/
*.translation
export_presets.cfg.bak

# Buildy a artefakty (v CI se generují znovu)
build/
artifacts/
assets/_raw/

# Tajemství – NIKDY do gitu.
#
# POZOR, tohle tu DŘÍV NEBYLO a byla to díra (opraveno 1. 10. 2026):
# tenhle skript sám kopíruje `.env` DO HRY (viz `$envSoubor` výš) a ten soubor
# obsahuje REÁLNÝ `FORGE_SECRET` (`repo\.forge\node\.env`). `.gitignore` hry ho
# ale neignoroval – ověřeno `git check-ignore .forge/node/.env` → nic.
# Agent v CI dělá `git add -A`, takže by ho poslal do patche i do PR.
# Že k úniku zatím nedošlo, je jen tím, že ten soubor v herním repu ještě není.
#
# `.env` platí i na `.forge/node/.env` (git vzor bez lomítka matchuje
# v každé úrovni), ale obojí je tu výslovně – ať je záměr vidět.
.env
.forge/node/.env

# Python cache po LOKÁLNÍM spuštění bran (.forge/check-schema.py apod.).
# Kdyby se dostala do repa, `git add -A` by ji poslal do patche a do PR.
__pycache__/
*.pyc

# Lokální nástroje
.forge/provider.json
# Volba poskytovatele pro shell v témže kroku (druhý pokus agenta). Kdyby se
# dostala do repa, `git add -A` by ji poslal do PR a běh bez změny kódu by se
# hlásil jako úspěch.
.forge/provider.env
.forge/*.log
agent.patch
agent.log
# Log z kontrolního spuštění hry (workflow ho píše do RUNNER_TEMP, ale kdyby
# skončil v pracovní složce, `git add -A` by ho poslal do patche a do PR).
smoke.log
.aider*
# Pojistka: cokoli, co vypada jako rozbita cesta k secretu
/C:*Users*
UsersSsevc*
.secrets/
git-credentials
'@
Set-Content -Path (Join-Path $Target '.gitignore') -Value $gitignore -Encoding utf8

# .gitattributes – bez toho by git uložil .sh s CRLF a na Linux runneru by
# install-godot.sh selhal ("$'\r': command not found").
$attr = Join-Path $Orch 'repo\.gitattributes'
if (Test-Path $attr) {
    Copy-Item $attr (Join-Path $Target '.gitattributes') -Force
}

# Zapamatuj si stav repa, ať příští nahrání pozná, že v něm mezitím pracoval agent.
$stateDir = Join-Path $Orch '.state'
New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
$headAfter = ''
try { $headAfter = (& git -C $Target rev-parse HEAD 2>$null | Select-Object -First 1) } catch { }
@{ target = $Target; head = "$headAfter"; staged_at = (Get-Date -Format s) } |
    ConvertTo-Json | Set-Content (Join-Path $stateDir 'last-stage.json') -Encoding utf8

Write-Host "`nHotovo. Obsah:" -ForegroundColor Green
Get-ChildItem $Target -Force | Select-Object Mode, Name | Format-Table -AutoSize

Write-Host @"

Další kroky:
  1) git -C "$Target" init -b main
  2) git -C "$Target" add -A ; git -C "$Target" commit -m "Forge: zaklad hry + orchestr"
  3) git -C "$Target" remote add origin https://github.com/ssevcikm-spec/<repo>.git
  4) git -C "$Target" push -u origin main
     (push z tohoto sandboxu jde přes orchestra\tools\git.cmd)
Nastavení tajemství a conductora: viz README.md a docs v repu orchestra
(ssevcikm-spec/forge-orchestra).
"@
