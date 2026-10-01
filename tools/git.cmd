@echo off
rem Obal nad git, ktery v tomto prostredi prepne TLS backend na OpenSSL.
rem Duvod: schannel v sandboxu selze na SEC_E_NO_CREDENTIALS (viz tools\gitconfig).
rem Pouziti: gameforge\tools\git.cmd status   (vsechny argumenty se predaji dal)
setlocal
set "GIT_CONFIG_GLOBAL=%~dp0gitconfig"
git %*
exit /b %ERRORLEVEL%
