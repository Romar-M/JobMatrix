#!/usr/bin/env bash
# JobMatrix — запуск одной кнопкой (Linux/macOS)
# Запускает сервер в фоне (nohup) и открывает браузер
set -e
cd "$(dirname "$0")/.."
mkdir -p data

nohup python3 launcher/run.py > data/jobmatrix.log 2>&1 &
echo "JobMatrix запущен в фоне: http://localhost:8000"
echo "Лог: data/jobmatrix.log"
echo "Остановить: pkill -f 'launcher/run.py'"

