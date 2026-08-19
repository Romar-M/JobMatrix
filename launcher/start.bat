@echo off
rem ============================================
rem  JobMatrix — запуск одной кнопкой (Windows)
rem  Сервер стартует в фоне, браузер открывается сам.
rem  Окно закрывается автоматически.
rem  Хотите совсем без окна? Используйте start.vbs
rem ============================================
title JobMatrix
cd /d "%~dp0.."

rem --- запуск в фоне (pythonw предпочтительно) ---
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw launcher\run.py
) else (
    where pyw >nul 2>nul
    if %errorlevel%==0 (
        start "" pyw launcher\run.py
    ) else (
        start "" /min python launcher\run.py
    )
)

rem --- ждём подъёма сервера (до 20 сек) ---
set "URL=http://127.0.0.1:8000"
set /a TRY=0
:wait
set /a TRY+=1
if %TRY% gtr 20 (
    echo [JobMatrix] Сервер не поднялся за 20 сек. Смотрите data\logs\app.log
    timeout /t 5 >nul
    exit /b 1
)
>nul 2>nul curl -s -o nul "%URL%"
if %errorlevel%==0 goto open
>nul 2>nul powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri '%URL%' -UseBasicParsing -TimeoutSec 1) | Out-Null; exit 0 } catch { exit 1 }"
if %errorlevel%==0 goto open
timeout /t 1 /nobreak >nul
goto wait

:open
start "" "%URL%"
exit /b 0

