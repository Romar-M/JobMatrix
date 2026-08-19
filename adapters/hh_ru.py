"""Адаптер hh.ru — официальное API работодателя.

В боевом режиме (DEMO_MODE=false + HH_API_TOKEN) здесь будут
реальные запросы к api.hh.ru: вакансии компании, статистика,
отклики, поиск резюме.
"""
from config.settings import settings
from adapters.base import (
    SiteAdapter,
    VacancyData,
    Stats,
    ResponseData,
    ResumeData,
)


class HhRuAdapter(SiteAdapter):
    site_key = "hh_ru"
    site_name = "hh.ru"
    auth_type = "oauth"

    BASE_URL = "https://api.hh.ru"

    def _headers(self) -> dict:
        headers = {"User-Agent": "JobMatrix/0.1 (local demo)"}
        if settings.HH_API_TOKEN:
            headers["Authorization"] = f"Bearer {settings.HH_API_TOKEN}"
        return headers

    async def fetch_vacancies(self) -> list[VacancyData]:
        # TODO(production): GET /vacancies?employer_id=...&page=...
        # Без токена вернём пусто — не блокируем работу в демо.
        return []

    async def fetch_stats(self, external_id: str) -> Stats:
        # TODO(production): статистика по вакансии (просмотры/отклики)
        return Stats()

    async def fetch_responses(self, external_id: str) -> list[ResponseData]:
        # TODO(production): GET /negotiations — отклики по вакансии
        return []

    def supports_resume_search(self) -> bool:
        return True

    async def search_resumes(self, query: dict) -> list[ResumeData]:
        # TODO(production): GET /resumes?text=...&area=... (работодатель)
        return []

