@echo off
rem ============================================================
rem  Вспомогательный запуск JobMatrix (вызывается из start.vbs,
rem  окно скрыто через WScript.Shell Run 0)
rem ============================================================
cd /d "%~dp0.."

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw launcher\run.py
    exit /b 0
)

where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw launcher\run.py
    exit /b 0
)

start "" /min python launcher\run.py
exit /b 0

