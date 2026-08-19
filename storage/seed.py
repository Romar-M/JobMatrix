"""Начальные демо-данные: компания, вакансии, размещения по сайтам.

Вызывается при первом запуске (БД пустая), чтобы интерфейс сразу
показывал наполненную матрицу.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from storage.db import SessionLocal
from storage.models import Company, Vacancy, VacancyListing

SITES = [
    ("hh_ru", "https://hh.ru/vacancy/100001"),
    ("superjob", "https://superjob.ru/vacancy/200001"),
    ("avito", "https://www.avito.ru/vacancy/300001"),
    ("rabota_ru", "https://rabota.ru/vacancy/400001"),
    ("zarplata_ru", "https://zarplata.ru/vacancy/500001"),
]

DEMO_VACANCIES = [
    {
        "title": "Python-разработчик (backend)",
        "city": "Москва",
        "salary_from": 180000,
        "salary_to": 250000,
        "experience": "1-3 года",
        "description": "Разработка веб-сервисов на Python/FastAPI, работа с БД.",
        "skills": "Python, FastAPI, SQL, Docker, PostgreSQL",
        "published": [
            ("hh_ru", 120, 5),
            ("superjob", 45, 2),
            ("avito", 30, 0),
        ],
    },
    {
        "title": "Frontend-разработчик (React)",
        "city": "Санкт-Петербург",
        "salary_from": 160000,
        "salary_to": 220000,
        "experience": "1-3 года",
        "description": "Разработка интерфейсов на React, TypeScript.",
        "skills": "React, TypeScript, HTML, CSS, Redux",
        "published": [
            ("hh_ru", 90, 3),
            ("superjob", 60, 1),
            ("rabota_ru", 25, 0),
        ],
    },
    {
        "title": "Data-аналитик",
        "city": "Удалённо",
        "salary_from": 150000,
        "salary_to": 200000,
        "experience": "3-6 лет",
        "description": "Анализ данных, построение отчётов, работа с SQL.",
        "skills": "Python, SQL, Pandas, Excel, BI",
        "published": [
            ("hh_ru", 200, 8),
            ("superjob", 100, 4),
        ],
    },
    {
        "title": "Менеджер по продажам (B2B)",
        "city": "Москва",
        "salary_from": 90000,
        "salary_to": 150000,
        "experience": "1-3 года",
        "description": "Продажи SaaS-продуктов, работа в CRM.",
        "skills": "Продажи, CRM, переговоры, Excel",
        "published": [
            ("avito", 55, 6),
            ("zarplata_ru", 40, 2),
            ("rabota_ru", 35, 1),
        ],
    },
]


def seed_if_empty(db: Session | None = None) -> None:
    """Создать демо-данные, если в БД ещё нет ни одной вакансии."""
    own_session = db is None
    session = db or SessionLocal()
    try:
        if session.query(Vacancy).count() > 0:
            return

        company = Company(name="Рома-Софт (демо)")
        session.add(company)
        session.flush()

        now = datetime.now(timezone.utc)
        for idx, v in enumerate(DEMO_VACANCIES):
            vacancy = Vacancy(
                company_id=company.id,
                title=v["title"],
                city=v["city"],
                salary_from=v["salary_from"],
                salary_to=v["salary_to"],
                experience=v["experience"],
                description=v["description"],
                skills=v["skills"],
            )
            session.add(vacancy)
            session.flush()

            for site_key, url_tpl in SITES:
                published = [p for p in v["published"] if p[0] == site_key]
                if not published:
                    continue
                _, views, responses = published[0]
                listing = VacancyListing(
                    vacancy_id=vacancy.id,
                    site=site_key,
                    external_id=f"{idx + 1}-{site_key}",
                    url=f"{url_tpl}?v={idx + 1}",
                    status="published",
                    published_at=now - timedelta(days=10 - idx),
                    views_count=views,
                    responses_count=responses,
                    last_checked_at=now,
                )
                session.add(listing)

        session.commit()
    finally:
        if own_session:
            session.close()

