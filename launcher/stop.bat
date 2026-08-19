@echo off
title JobMatrix — остановка
cd /d "%~dp0.."

echo [JobMatrix] Останавливаю сервер...

if exist data\jobmatrix.pid (
    set /p PID=<data\jobmatrix.pid
    taskkill /F /PID %PID% >nul 2>nul
    if not errorlevel 1 (
        echo [JobMatrix] Остановлен (PID %PID%)
    )
    del data\jobmatrix.pid >nul 2>nul
)

powershell -NoProfile -Command "$p = (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue).OwningProcess; if ($p) { $p | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue } }" >nul 2>nul

echo [JobMatrix] Готово.
timeout /t 2 >nul

