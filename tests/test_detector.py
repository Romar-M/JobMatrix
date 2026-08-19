"""Тест детектора новых откликов (in-memory SQLite + детерминированный адаптер)."""
import asyncio
import os
import tempfile

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DEMO_MODE"] = "true"
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"

import pytest  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from adapters.base import SiteAdapter, ResponseData  # noqa: E402
from notifications.detector import detect_new_responses  # noqa: E402
from storage.db import Base, engine, SessionLocal  # noqa: E402
from storage.models import Company, Vacancy, VacancyListing, Response, Event  # noqa: E402


class OneResponseAdapter(SiteAdapter):
    """Всегда возвращает одного кандидата."""

    site_key = "hh_ru"
    site_name = "hh.ru"

    async def fetch_vacancies(self):
        return []

    async def fetch_stats(self, external_id):
        return None

    async def fetch_responses(self, external_id):
        return [ResponseData(candidate_name="Иван Петров #777", resume_url="https://x/r1")]


class NoResponsesAdapter(SiteAdapter):
    """Никогда не возвращает отклики."""

    site_key = "superjob"
    site_name = "SuperJob"

    async def fetch_vacancies(self):
        return []

    async def fetch_stats(self, external_id):
        return None

    async def fetch_responses(self, external_id):
        return []


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def _listing(db: Session, site: str, title: str = "Python-разработчик"):
    company = Company(name="Test")
    db.add(company)
    db.flush()
    vacancy = Vacancy(company_id=company.id, title=title, city="Москва")
    db.add(vacancy)
    db.flush()
    listing = VacancyListing(vacancy_id=vacancy.id, site=site, external_id="1")
    db.add(listing)
    db.commit()
    return listing


def test_detect_new_response_creates_event(db: Session):
    listing = _listing(db, "hh_ru")

    events = asyncio.run(detect_new_responses(db, OneResponseAdapter(), listing))

    assert len(events) == 1
    assert events[0].type == "new_response"
    assert events[0].vacancy_title == "Python-разработчик"
    assert events[0].site == "hh_ru"

    response = db.query(Response).filter_by(listing_id=listing.id).first()
    assert response is not None
    assert response.candidate_name == "Иван Петров #777"


def test_same_candidate_not_duplicated(db: Session):
    listing = _listing(db, "hh_ru")
    adapter = OneResponseAdapter()

    first = asyncio.run(detect_new_responses(db, adapter, listing))
    second = asyncio.run(detect_new_responses(db, adapter, listing))

    assert len(first) == 1
    assert second == []
    assert db.query(Response).count() == 1


def test_no_responses_no_events(db: Session):
    listing = _listing(db, "superjob")

    events = asyncio.run(detect_new_responses(db, NoResponsesAdapter(), listing))

    assert events == []
    assert db.query(Event).count() == 0

