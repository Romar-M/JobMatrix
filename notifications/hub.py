"""WebSocket-хаб: рассылка событий всем подключённым браузерам."""
import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Разослать событие всем подключённым клиентам."""
        payload = json.dumps(message, default=str, ensure_ascii=False)
        disconnected = []
        for ws in self.active_connections:
            try:
                await ws.send_text(payload)
            except Exception:  # noqa: BLE001
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)


hub = ConnectionManager()

