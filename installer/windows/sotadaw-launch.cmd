@echo off
rem SOTA DAW Windows launcher (SCAFFOLD — mirrors the proven Linux launchers:
rem per-user workspace bootstrap + Time-Machine git init + engine shim).
set SOTADAW_NO_UPLINK=1
set "WS=%LOCALAPPDATA%\sotadaw"
set "ENGINE=%~dp0"
if not exist "%WS%" (
  echo [sotadaw] first run: creating workspace at %WS%
  xcopy /E /I /Q "%ENGINE%payload" "%WS%" >nul
  set SOTADAW_FIRST_RUN=1
)
where git >nul 2>nul && if not exist "%WS%\.git" (
  git -C "%WS%" init -q
  git -C "%WS%" config user.name "SOTA DAW"
  git -C "%WS%" config user.email "sotadaw@localhost"
  git -C "%WS%" add -A
  git -C "%WS%" commit -qm "workspace born"
)
if not exist "%WS%\app\build\m1_artefacts\Release" mkdir "%WS%\app\build\m1_artefacts\Release"
copy /Y "%ENGINE%bin\m1.exe" "%WS%\app\build\m1_artefacts\Release\m1.exe" >nul
rem m1.exe is COPIED away from bin\ — its DLLs must ride along (faust.dll = live-JIT;
rem Windows resolves DLLs from the exe's OWN dir first). Real-install dialog 2026-07-12:
rem "code execution cannot proceed because faust.dll was not found".
copy /Y "%ENGINE%bin\*.dll" "%WS%\app\build\m1_artefacts\Release\" >nul 2>nul
rem bundled CPython (embeddable): the agent works with zero preinstalled Python
if exist "%ENGINE%python\python.exe" set "PATH=%ENGINE%python;%PATH%"
rem live-JIT: bundled faust stdlib for brand-new .dsp instruments
if exist "%ENGINE%faustlibs\stdfaust.lib" set "SOTADAW_FAUST_LIB_PATH=%ENGINE%faustlibs"
set "SOTADAW_ROOT=%WS%"
rem CI gates the REAL staging headlessly (workspace m1 = the bits the app invokes)
if defined SOTADAW_STAGE_ONLY exit /b 0
start "" "%ENGINE%bin\SOTA DAW.exe" %*
