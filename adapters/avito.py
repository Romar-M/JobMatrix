"""Адаптер Авито Работа — API/парсинг (зависит от доступов).

В демо-режиме сюда не обращаются (используется MockAdapter).
"""
from adapters.base import SiteAdapter, VacancyData, Stats, ResponseData, ResumeData


class AvitoAdapter(SiteAdapter):
    site_key = "avito"
    site_name = "Авито"
    auth_type = "api_key"

    async def fetch_vacancies(self) -> list[VacancyData]:
        # TODO(production): API Авито Работа / парсинг
        return []

    async def fetch_stats(self, external_id: str) -> Stats:
        return Stats()

    async def fetch_responses(self, external_id: str) -> list[ResponseData]:
        return []

    def supports_resume_search(self) -> bool:
        return False

    async def search_resumes(self, query: dict) -> list[ResumeData]:
        return []

