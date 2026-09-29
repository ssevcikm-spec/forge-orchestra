@echo off
rem Obal nad wrangler (Cloudflare CLI), ktery drzi vsechna data ve workspace.
rem Duvod: sandbox nepovoluje zapis do ~/.wrangler ani do systemove npm cache.
rem
rem Pouziti:
rem   gameforge\orchestra\wrangler.cmd login
rem   gameforge\orchestra\wrangler.cmd d1 create forge-conductor
rem   gameforge\orchestra\wrangler.cmd deploy
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
