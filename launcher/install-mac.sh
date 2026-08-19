#!/bin/bash
# Установка JobMatrix для macOS: права на .app, опционально копирование в /Applications

set -e
cd "$(dirname "$0")"

echo "== JobMatrix: установка приложений macOS =="

chmod +x "JobMatrix.command" "stop.command" "start.sh" 2>/dev/null || true
chmod +x "JobMatrix.app/Contents/MacOS/JobMatrix" \
        "JobMatrixStop.app/Contents/MacOS/JobMatrixStop" \
        "install-mac.sh"

echo "OK: исполняемые права установлены."

read -r -p "Скопировать приложения в /Applications? [y/N] " ans
if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then
  cp -R "JobMatrix.app" "JobMatrixStop.app" /Applications/
  echo "OK: скопировано в /Applications."
  echo "Примечание: приложения из /Applications ищут проект в ~/JobMatrix,"
  echo "~/Documents/JobMatrix или ~/Documents/Obsidian Vault/Programs/JobMatrix."
fi

echo
echo "Готово. Запуск — двойной клик по JobMatrix.app, остановка — JobMatrixStop.app."

