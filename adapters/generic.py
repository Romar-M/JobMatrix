"""GenericAdapter — адаптер для произвольного сайта, добавленного через UI.

В demo-режиме ведёт себя как заглушка (как MockAdapter): генерирует
тестовые данные, чтобы всё работало без реального API.

В боевом режиме должен ходить на url сайта с api_key — здесь оставлены
TODO(production): типовой HTTP-контракт будет зависеть от конкретного
сервиса, поэтому endpoint'ы настраиваются под сайт.
"""
import random
from datetime import datetime, timezone

from config.settings import settings
from adapters.base import SiteAdapter, VacancyData, Stats, ResponseData, ResumeData
from adapters.mock import CANDIDATES, MockAdapter


class GenericAdapter(MockAdapter):
    """Заглушка/универсальный адаптер для пользовательского сайта."""

    def __init__(
        self,
        site_key: str,
        site_name: str,
        url: str = "",
        api_key: str = "",
        auth_type: str = "api_key",
    ):
        super().__init__(site_key, site_name)
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.auth_type = auth_type

    # ---------- демо-режим: тестовые данные (как у MockAdapter) ----------
    # fetch_vacancies / fetch_stats / fetch_responses / search_resumes
    # унаследованы от MockAdapter и работают без сети.

    # ---------- боевой режим: TODO(production) ----------
    async def fetch_vacancies_real(self) -> list[VacancyData]:
        """Здесь будет обращение к API сайта: GET {url}/api/vacancies
        с заголовком Authorization: Bearer {api_key}."""
        raise NotImplementedError(
            "GenericAdapter: настройте реальный контракт для сайта " + self.url
        )

    async def fetch_stats_real(self, external_id: str) -> Stats:
        raise NotImplementedError("GenericAdapter: fetch_stats_real")

    async def fetch_responses_real(self, external_id: str) -> list[ResponseData]:
        raise NotImplementedError("GenericAdapter: fetch_responses_real")

