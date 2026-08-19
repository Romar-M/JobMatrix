"""Планировщик: периодический сбор данных с сайтов.

Цикл сбора:
1. Для каждого размещения: fetch_stats -> обновить счётчики.
2. Детектор новых откликов -> создаёт события.
3. События рассылаются по WebSocket всем браузерам.

Обрабатываются и встроенные сайты, и кастомные (добавленные через UI).
Приостановленные (paused) и снятые (archived) размещения пропускаются —
счётчики по ним не собираются.
"""
import json
import logging
from datetime import datetime, timezone

from config.settings import settings
from adapters.registry import all_sites, get_adapter
from notifications.detector import detect_new_responses
from notifications.hub import hub
from storage.db import SessionLocal
from storage.models import VacancyListing, CollectLog

logger = logging.getLogger(__name__)


async def collect_once() -> dict:
    """Один проход сбора по всем сайтам (встроенные + кастомные)."""
    summary = {"checked": 0, "events": 0, "errors": []}
    db = SessionLocal()
    try:
        for site in all_sites(db):
            key = site["key"]
            log = CollectLog(site=key, status="running")
            db.add(log)
            db.flush()
            try:
                adapter = get_adapter(key, db)
                listings = (
                    db.query(VacancyListing)
                    .filter(
                        VacancyListing.site == key,
                        VacancyListing.status == "published",
                    )
                    .all()
                )
                for listing in listings:
                    stats = await adapter.fetch_stats(listing.external_id)
                    if settings.DEMO_MODE:
                        # В демо адаптер возвращает приращения
                        listing.views_count += stats.views_count
                        listing.responses_count += stats.responses_count
                    else:
                        # В боевом режиме сайт возвращает абсолютные значения
                        listing.views_count = stats.views_count
                        listing.responses_count = stats.responses_count

                    events = await detect_new_responses(db, adapter, listing)
                    listing.last_checked_at = datetime.now(timezone.utc)
                    summary["checked"] += 1

                    for event in events:
                        summary["events"] += 1
                        try:
                            payload = json.loads(event.payload or "{}")
                        except Exception:  # noqa: BLE001
                            payload = {}
                        await hub.broadcast(
                            {
                                "type": event.type,
                                "event_id": event.id,
                                "vacancy_title": event.vacancy_title,
                                "site": event.site,
                                "candidate_name": payload.get("candidate_name", ""),
                                "ts": event.created_at.isoformat() if event.created_at else None,
                            }
                        )

                log.status = "ok"
                log.message = f"checked={summary['checked']}"
            except Exception as exc:  # noqa: BLE001
                logger.exception("Ошибка сбора на сайте %s", key)
                log.status = "error"
                log.message = str(exc)
                summary["errors"].append(f"{key}: {exc}")
            finally:
                log.finished_at = datetime.now(timezone.utc)
                db.commit()
        return summary
    finally:
        db.close()

