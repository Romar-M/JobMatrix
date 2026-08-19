@echo off
rem ============================================================
rem  Вспомогательная остановка JobMatrix (вызывается из stop.vbs)
rem  Останавливает по PID-файлу, запасной вариант — по порту 8000
rem ============================================================
cd /d "%~dp0.."

rem 1) По PID-файлу
if exist data\jobmatrix.pid (
    set /p PID=<data\jobmatrix.pid
    taskkill /F /PID %PID% >nul 2>nul
    del data\jobmatrix.pid >nul 2>nul
)

rem 2) Запасной вариант: процесс, слушающий порт 8000
powershell -NoProfile -Command "$p = (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue).OwningProcess; if ($p) { $p | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue } }" >nul 2>nul

exit /b 0

