"""Адаптер Zarplata.ru — API/парсинг.

В демо-режиме сюда не обращаются (используется MockAdapter).
"""
from adapters.base import SiteAdapter, VacancyData, Stats, ResponseData, ResumeData


class ZarplataRuAdapter(SiteAdapter):
    site_key = "zarplata_ru"
    site_name = "Zarplata.ru"
    auth_type = "api_key"

    async def fetch_vacancies(self) -> list[VacancyData]:
        # TODO(production): API Zarplata.ru
        return []

    async def fetch_stats(self, external_id: str) -> Stats:
        return Stats()

    async def fetch_responses(self, external_id: str) -> list[ResponseData]:
        return []

    def supports_resume_search(self) -> bool:
        return True

    async def search_resumes(self, query: dict) -> list[ResumeData]:
        return []

