"""Демо-адаптер (заглушка): генерирует тестовые данные, чтобы всё
работало без реальных ключей API.

В demo-режиме используется для всех сайтов (в том числе кастомных).
Просмотры растут каждый сбор, с шансом появляются новые отклики — так
легко увидеть оповещения и звук в действии.
"""
import random
from datetime import datetime, timezone

from config.settings import settings
from adapters.base import (
    SiteAdapter,
    VacancyData,
    Stats,
    ResponseData,
    ResumeData,
)

CANDIDATES = [
    ("Иван Петров", "Python backend, FastAPI, 2 года опыта"),
    ("Анна Смирнова", "React, TypeScript, frontend, UI/UX"),
    ("Пётр Иванов", "Data analyst, SQL, Pandas, визуализация"),
    ("Мария Кузнецова", "Продажи B2B, CRM, SaaS, переговоры"),
    ("Дмитрий Соколов", "Python/Django, асинхронный код, SQL"),
    ("Елена Волкова", "Frontend Vue/React, дизайн интерфейсов"),
    ("Сергей Морозов", "DevOps, Docker, Linux, CI/CD"),
    ("Ольга Новикова", "Менеджер проектов, Agile, командная работа"),
]


class MockAdapter(SiteAdapter):
    """Заглушка реального API: данные генерируются случайно."""

    def __init__(self, site_key: str, site_name: str, url: str = ""):
        self.site_key = site_key
        self.site_name = site_name
        self.url = url.rstrip("/") if url else ""
        self.auth_type = "none"

    # ---------- вакансии ----------
    async def fetch_vacancies(self) -> list[VacancyData]:
        # В демо вакансии живут в БД (seed), здесь возвращаем пусто.
        return []

    # ---------- статистика ----------
    async def fetch_stats(self, external_id: str) -> Stats:
        # Приращение просмотров за один сбор + шанс нового отклика.
        views_step = random.randint(1, settings.DEMO_VIEWS_STEP)
        new_responses = 1 if random.random() < settings.DEMO_NEW_RESPONSE_CHANCE else 0
        return Stats(views_count=views_step, responses_count=new_responses)

    # ---------- отклики ----------
    async def fetch_responses(self, external_id: str) -> list[ResponseData]:
        # С шансом вернуть «нового» кандидата. Детектор сам решит,
        # был ли отклик действительно новым (сравнивая с именами в БД).
        if random.random() >= settings.DEMO_NEW_RESPONSE_CHANCE:
            return []
        name, message = random.choice(CANDIDATES)
        return [
            ResponseData(
                candidate_name=f"{name} #{random.randint(100, 999)}",
                resume_url=f"https://example.com/resume/{random.randint(1000, 9999)}",
                responded_at=datetime.now(timezone.utc),
                message=message,
            )
        ]

    # ---------- поиск резюме ----------
    def supports_resume_search(self) -> bool:
        return True

    async def search_resumes(self, query: dict) -> list[ResumeData]:
        """Генерирует тестовые резюме под фильтры вакансии."""
        title = query.get("title", "разработчик")
        city = query.get("city", "")
        pool = random.sample(CANDIDATES, k=min(4, len(CANDIDATES)))
        results = []
        for i, (name, about) in enumerate(pool):
            score = max(40, 100 - i * 12 - random.randint(0, 10))
            results.append(
                ResumeData(
                    resume_url=f"https://example.com/resume/{1000 + i}",
                    candidate_name=name,
                    title=f"{title} — {city or 'удалённо'}".strip(),
                    match_score=score,
                    extra={"about": about},
                )
            )
        results.sort(key=lambda r: r.match_score, reverse=True)
        return results

