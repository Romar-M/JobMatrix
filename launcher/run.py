"""Запуск JobMatrix одной командой: сервер + планировщик + браузер.

Работает в двух режимах:
    python launcher/run.py             # видна консоль (отладка)
    pythonw launcher/run.py            # Windows: полностью в фоне, без окна

Под pythonw у процесса нет консоли: sys.stdout/sys.stderr равны None,
поэтому они перенаправляются в data/logs/app.log — иначе print() падает
с AttributeError и сервер не стартует (именно это ломало старый start.bat).

Также пишется PID-файл (data/jobmatrix.pid) — по нему stop.bat/stop.vbs
останавливают сервер, ведь фоновому процессу некуда жать Ctrl+C.

Флаги:
    --no-browser   не открывать браузер автоматически
"""
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.settings import settings  # noqa: E402

DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
PID_FILE = DATA_DIR / "jobmatrix.pid"
LOG_FILE = LOG_DIR / "app.log"


def _redirect_streams_if_headless() -> None:
    """pythonw не имеет консоли: stdout/stderr = None -> перенаправляем в файл."""
    if sys.stdout is None:
        sys.stdout = open(LOG_FILE, "a", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(LOG_FILE, "a", encoding="utf-8")


def _write_pid() -> None:
    try:
        PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    except OSError:
        pass


def _remove_pid() -> None:
    try:
        if PID_FILE.exists():
            PID_FILE.unlink()
    except OSError:
        pass


def _is_port_busy(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex((host, port)) == 0


def _open_browser_later() -> None:
    """Открыть интерфейс через пару секунд, когда сервер уже поднялся."""
    time.sleep(1.8)
    url = f"http://{settings.HOST}:{settings.PORT}"
    try:
        webbrowser.open(url)
    except Exception:  # noqa: BLE001
        pass


def main() -> None:
    _redirect_streams_if_headless()
    _write_pid()

    no_browser = "--no-browser" in sys.argv
    url = f"http://{settings.HOST}:{settings.PORT}"

    # Сервер уже запущен (например, стартовали повторно) — просто открываем браузер
    if _is_port_busy(settings.HOST, settings.PORT):
        print(f"[JobMatrix] Порт {settings.PORT} уже занят — сервер уже работает.")
        if not no_browser:
            try:
                webbrowser.open(url)
            except Exception:  # noqa: BLE001
                pass
        return

    if not no_browser:
        threading.Thread(target=_open_browser_later, daemon=True).start()

    import uvicorn
    from api.main import app

    print(f"[JobMatrix] Запуск: {url}")
    print(f"[JobMatrix] Демо-режим: {settings.DEMO_MODE} | Сбор каждые {settings.COLLECT_INTERVAL_MINUTES} мин")
    print(f"[JobMatrix] Логи: {LOG_FILE}")
    print("[JobMatrix] Остановка: launcher\\stop.bat (или Ctrl+C, если видна консоль)")

    try:
        uvicorn.run(app, host=settings.HOST, port=settings.PORT, log_level="info")
    finally:
        _remove_pid()


if __name__ == "__main__":
    main()

