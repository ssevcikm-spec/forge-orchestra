<#
.SYNOPSIS
  Lokální test orchestra – ověří celý řetěz bez Cloudflare a bez GitHubu.

.POPIS
  Spustí zkušební conductor (tools/mock-conductor.mjs), založí úkol pro domácí
  uzel, nechá workera úkol vyzvednout a vykonat a vypíše výsledek.

  Ověřuje se tím: heartbeat → claim → vykonání kroků (Godot import + testy)
  → report → stav a statistiky uzlu.

  PROČ TO EXISTUJE: nasazení do cloudu čeká na přihlášení uživatele. Tenhle test
  dokáže, že logika orchestra funguje, ještě než vznikne jediný účet.

.POUŽITÍ
  .\test-local.ps1                      # test s projektem demo1
  .\test-local.ps1 -Project moje-hra
  .\test-local.ps1 -KeepWorkdir         # nechat pracovní složku pro ladění

.POZNÁMKA K SANDBOXU
  Krok `git clone` v tomhle prostředí neprojde: Git pro Windows si volá Cygwin
  `sh`, kterému sandbox nedovolí vytvořit rouru ("couldn't create signal pipe").
  Test proto pracuje s předpřipravenou složkou a krok gitu vynechává. Na telefonu
  (Termux/Linux) git funguje normálně.
#>
param(
    [string]$Project = 'demo1',
    [int]$Port = 8787,
    [string]$Secret = 'test-secret',
    [switch]$KeepWorkdir
)

$ErrorActionPreference = 'Stop'
$tools = $PSScriptRoot                                  # gameforge\orchestra\tools
$orch = Split-Path $tools -Parent                       # gameforge\orchestra
$forge = Split-Path $orch -Parent                       # gameforge
$testDir = Join-Path $orch '.test'
$workDir = Join-Path $testDir 'work'
$projDir = Join-Path $forge "projects\$Project"

if (-not (Test-Path (Join-Path $projDir 'project.godot'))) {
    throw "Projekt '$Project' neexistuje ($projDir). Založ ho: forge.cmd new $Project"
}

Write-Host "=== 1/5 Příprava ===" -ForegroundColor Cyan
if (Test-Path $testDir) { Remove-Item $testDir -Recurse -Force }
New-Item -ItemType Directory -Force -Path $workDir | Out-Null

$env:FORGE_URL = "http://127.0.0.1:$Port"
$env:FORGE_SECRET = $Secret
$env:FORGE_WORKER = 'pc-test'
$env:FORGE_KINDS = 'test,build,assets'
$env:FORGE_WORKDIR = $workDir
$env:FORGE_GODOT = Join-Path $forge 'tools\godot\Godot_v4.7.2-stable_win64_console.exe'
$env:APPDATA = Join-Path $forge 'tools\godot-appdata'
$env:LOCALAPPDATA = Join-Path $forge 'tools\godot-localappdata'
$env:TEMP = Join-Path $forge 'tools\tmp'
$env:TMP = $env:TEMP
$env:PYTHONUTF8 = '1'
# git v tomhle sandboxu potřebuje OpenSSL backend (schannel padá)
$env:GIT_CONFIG_GLOBAL = Join-Path $forge 'tools\gitconfig'

Write-Host "=== 2/5 Spouštím zkušební conductor na portu $Port ===" -ForegroundColor Cyan
$node = (Get-Command node).Source
$mock = Start-Process -FilePath $node `
    -ArgumentList (Join-Path $tools 'mock-conductor.mjs') `
    -PassThru -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $testDir 'mock.log') `
    -RedirectStandardError (Join-Path $testDir 'mock.err')
Start-Sleep -Seconds 2

try {
    Write-Host "=== 3/5 Připravuji pracovní kopii projektu ===" -ForegroundColor Cyan
    # Název pracovní kopie se ODVOZUJE z parametru -Game. Dřív tu bylo natvrdo
    # `forge-quest`, což je JINÉ, živé repo s vlastní hrou i GitHub Pages –
    # test se pak hlásil jménem cizího projektu.
    $dest = Join-Path $workDir $Game
    robocopy $projDir $dest /E /XD .godot build artifacts _raw /NFL /NDL /NJH /NJS /NP | Out-Null
    $files = (Get-ChildItem $dest -Recurse -File | Measure-Object).Count
    Write-Host "  zkopírováno $files souborů do $dest"

    Write-Host "=== 4/5 Zakládám úkol pro domácí uzel ===" -ForegroundColor Cyan
    & node (Join-Path $orch 'bin\task.mjs') add "Godot testy na uzlu" `
        "Import assetů a spuštění testů na domácím uzlu" test `
        --target lan --name $Game --steps "godot-import;godot-test" --artifacts build | Out-Null

    Write-Host "=== 5/5 Worker vyzvedává úkol ===" -ForegroundColor Cyan
    & node (Join-Path $orch 'repo\.forge\node\worker.mjs') --once
    Write-Host "worker exit=$LASTEXITCODE"

    Write-Host "`n=== Výsledek ve conductoru ===" -ForegroundColor Cyan
    & node (Join-Path $orch 'bin\task.mjs') status
    Write-Host "=== Uzly ===" -ForegroundColor Cyan
    & node (Join-Path $orch 'bin\task.mjs') workers

    $log = Get-ChildItem (Join-Path $testDir 'logs') -Filter 'mock-*.log' -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($log) {
        Write-Host "`n=== Konec logu kroků ($($log.Name)) ===" -ForegroundColor Cyan
        Get-Content $log.FullName -Encoding UTF8 | Select-Object -Last 18
    }
}
finally {
    Stop-Process -Id $mock.Id -Force -ErrorAction SilentlyContinue
    if (-not $KeepWorkdir) {
        Start-Sleep -Seconds 1
        Remove-Item $testDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Host "`nZkušební conductor zastaven." -ForegroundColor Green
}
