# Druhé kolo — sběr git faktů do JSON pro Node skript.
# Důvod: sandbox `workspace-write` blokuje podprocesy s piped stdio v Node
# (EPERM), takže git se pouští odsud a výsledek se předá souborem.
# Spuštění: pwsh -File _analyza\hl2-git.ps1
$ErrorActionPreference = 'Stop'
$WS  = 'C:\Users\Ssevc\Local-Deepseek'
$GIT = Join-Path $WS 'orchestra\tools\git.cmd'
$hra = 'games\uo-shadows'

function Git([string[]]$a) { (& $GIT @a) -join "`n" }

$out = [ordered]@{
  mereno            = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
  localHead         = Git @('-C', $hra, 'rev-parse', 'HEAD')
  originMain        = Git @('-C', $hra, 'rev-parse', 'origin/main')
  aheadBehind       = Git @('-C', $hra, 'rev-list', '--left-right', '--count', 'origin/main...HEAD')
  localHeadScripts  = @(Git @('-C', $hra, 'ls-tree', '-r', '--name-only', 'HEAD', '--', 'scripts/') -split "`n" | Where-Object { $_ -and $_ -notlike '*.uid' })
  originMainScripts = @(Git @('-C', $hra, 'ls-tree', '-r', '--name-only', 'origin/main', '--', 'scripts/') -split "`n" | Where-Object { $_ -and $_ -notlike '*.uid' })
  roadmapSoubor     = (Get-Content (Join-Path $WS "$hra\.forge\roadmap.json") -Raw)
  roadmapVOrigin    = (Git @('-C', $hra, 'show', 'origin/main:.forge/roadmap.json'))
  vsichniSoubory    = @(Git @('-C', $hra, 'ls-tree', '-r', '--name-only', 'origin/main') -split "`n" | Where-Object { $_ })
}

# Které granule jsou HOTOVÉ podle souboru a přitom jejich soubory v origin/main nejsou
$soubor = $out.roadmapSoubor | ConvertFrom-Json
$out.hotoveGranule = @($soubor.grains | Where-Object { $_.done -eq $true } | ForEach-Object { $_.id })
$out.vsechnyGranule = @($soubor.grains | ForEach-Object { $_.id })
$out.ownsMap = @{}
foreach ($g in $soubor.grains) { $out.ownsMap[$g.id] = @($g.owns) }

$json = $out | ConvertTo-Json -Depth 12
[System.IO.File]::WriteAllText((Join-Path $WS '_analyza\hl2-git.json'), $json, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "zapsano _analyza\hl2-git.json"
Write-Host "localHead  = $($out.localHead)"
Write-Host "originMain = $($out.originMain)"
Write-Host "scripts: local=$($out.localHeadScripts.Count) origin/main=$($out.originMainScripts.Count)"
