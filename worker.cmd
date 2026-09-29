@echo off
rem Spust? pull-workera pro tento po??ta? (GPU assety, lok?ln? pl?nov?n?).
rem Souhlas: kroky `shell:` se zeptaj? y/N v konzoli; deterministick? kroky b??? samy.
rem Ctrl+C = konec. Pro jeden cyklus: worker.cmd --once
setlocal
set "ORCH=%~dp0"
node "%ORCH%repo\.forge\node\worker.mjs" %*
exit /b %ERRORLEVEL%
