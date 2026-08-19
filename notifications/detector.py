"""Детектор новых откликов: находит кандидатов, которых ещё нет в БД,
создаёт Response и событие new_response."""
import json
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from adapters.base import SiteAdapter
from storage.models import VacancyListing, Response, Event

logger = logging.getLogger(__name__)


async def detect_new_responses(
    db: Session,
    adapter: SiteAdapter,
    listing: VacancyListing,
) -> list[Event]:
    """Проверить размещение на новые отклики.

    Возвращает список созданных событий (их потом рассылаем по WebSocket).
    """
    try:
        fetched = await adapter.fetch_responses(listing.external_id)
    except Exception as exc:  # noqa: BLE001
        logger.warning("fetch_responses %s/%s: %s", adapter.site_key, listing.external_id, exc)
        return []

    if not fetched:
        return []

    known = {
        r.candidate_name
        for r in db.query(Response).filter(Response.listing_id == listing.id).all()
    }

    events: list[Event] = []
    for rd in fetched:
        if rd.candidate_name in known:
            continue
        response = Response(
            listing_id=listing.id,
            candidate_name=rd.candidate_name,
            resume_url=rd.resume_url,
            message=rd.message,
            responded_at=rd.responded_at or datetime.now(timezone.utc),
            is_new=True,
        )
        db.add(response)
        known.add(rd.candidate_name)

        event = Event(
            type="new_response",
            listing_id=listing.id,
            vacancy_title=listing.vacancy.title if listing.vacancy else "",
            site=listing.site,
            payload=json.dumps(
                {
                    "candidate_name": rd.candidate_name,
                    "resume_url": rd.resume_url,
                    "message": rd.message,
                },
                ensure_ascii=False,
            ),
        )
        db.add(event)
        events.append(event)

    if events:
        db.commit()
    return events

