@echo off
rem Obal nad wrangler (Cloudflare CLI), ktery drzi vsechna data ve workspace.
rem Duvod: sandbox nepovoluje zapis do ~/.wrangler ani do systemove npm cache.
rem
rem Pouziti:
rem   orchestra\wrangler.cmd login
rem   orchestra\wrangler.cmd d1 create forge-conductor
rem   orchestra\wrangler.cmd deploy
rem
rem POZOR: ulozene prihlaseni na teto stanici nefunguje (token vyprsela
rem a Cloudflare vraci "Invalid access token"). Deploy conductora resi
rem GitHub Actions v repu orchestra, ktere ma vlastni CLOUDFLARE_API_TOKEN
rem -- tedy cestou push do gitu, ne timhle skriptem.
setlocal
set "ORCH=%~dp0"
set "WRANGLER_HOME=%ORCH%.wrangler"
set "npm_config_cache=%ORCH%.npm-cache"
set "TEMP=%ORCH%.tmp"
set "TMP=%TEMP%"
if not exist "%WRANGLER_HOME%" mkdir "%WRANGLER_HOME%"
if not exist "%npm_config_cache%" mkdir "%npm_config_cache%"
if not exist "%TEMP%" mkdir "%TEMP%"
cd /d "%ORCH%conductor"
call npx.cmd --yes wrangler@latest %*
exit /b %ERRORLEVEL%
