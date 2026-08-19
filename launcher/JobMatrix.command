# JobMatrix.command

_Запуск JobMatrix одной кнопкой на macOS: сервер в фоне, браузер открывается сам._

#!/usr/bin/env bash
# JobMatrix — запуск одной кнопкой на macOS.
# Двойной клик в Finder → сервер поднимается в фоне (nohup),
# браузер открывается сам, окно терминала закрывается.
set -e
cd "$(dirname "$0")/.."
mkdir -p data

if pgrep -f "launcher/run.py" >/dev/null 2>&1; then
  echo "JobMatrix уже запущен: http://localhost:8000"
  open "http://localhost:8000"
  exit 0
fi

nohup python3 launcher/run.py > data/jobmatrix.log 2>&1 &
sleep 2
open "http://localhost:8000"

echo "JobMatrix запущен в фоне: http://localhost:8000"
echo "Лог: data/jobmatrix.log"
echo "Остановка: двойной клик по launcher/stop.command"
exit 0

