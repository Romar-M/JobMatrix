"""Адаптер SuperJob — официальное API с ключом.

Боевой режим: DEMO_MODE=false + SUPERJOB_API_KEY.
"""
from config.settings import settings
from adapters.base import (
    SiteAdapter,
    VacancyData,
    Stats,
    ResponseData,
    ResumeData,
)


class SuperJobAdapter(SiteAdapter):
    site_key = "superjob"
    site_name = "SuperJob"
    auth_type = "api_key"

    BASE_URL = "https://api.superjob.ru/2.0"

    def _headers(self) -> dict:
        headers = {"X-Api-App-Id": settings.SUPERJOB_API_KEY}
        return headers

    async def fetch_vacancies(self) -> list[VacancyData]:
        # TODO(production): GET /vacancies/?keywords=...&client_id=...
        return []

    async def fetch_stats(self, external_id: str) -> Stats:
        # TODO(production): статистика по вакансии
        return Stats()

    async def fetch_responses(self, external_id: str) -> list[ResponseData]:
        # TODO(production): отклики по вакансии
        return []

    def supports_resume_search(self) -> bool:
        return True

    async def search_resumes(self, query: dict) -> list[ResumeData]:
        # TODO(production): GET /resumes/?keywords=...
        return []

