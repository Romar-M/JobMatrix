# stop.command

_Остановка фонового сервера JobMatrix на macOS одной кнопкой._

#!/usr/bin/env bash
# JobMatrix — остановка фонового сервера на macOS.
cd "$(dirname "$0")/.."
PID_FILE="data/jobmatrix.pid"

if [ -f "$PID_FILE" ]; then
  kill "$(cat "$PID_FILE")" 2>/dev/null && rm -f "$PID_FILE"
  echo "JobMatrix остановлен (по PID-файлу)."
  exit 0
fi

if pkill -f "launcher/run.py" 2>/dev/null; then
  echo "JobMatrix остановлен (pkill)."
else
  echo "JobMatrix не запущен."
fi
exit 0

