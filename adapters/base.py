"""Базовый интерфейс адаптеров сайтов и нормализованные модели данных."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class VacancyData:
    external_id: str
    title: str
    url: str
    city: str = ""
    salary_from: int | None = None
    salary_to: int | None = None
    currency: str = "RUB"
    description: str = ""
    published_at: datetime | None = None


@dataclass
class Stats:
    views_count: int = 0
    responses_count: int = 0


@dataclass
class ResponseData:
    candidate_name: str
    resume_url: str = ""
    responded_at: datetime | None = None
    message: str = ""


@dataclass
class ResumeData:
    resume_url: str
    candidate_name: str = ""
    title: str = ""
    match_score: int = 0
    extra: dict = field(default_factory=dict)


class SiteAdapter(ABC):
    """Единый интерфейс для всех сайтов размещения (~6 штук)."""

    site_key: str = ""
    site_name: str = ""
    auth_type: str = "none"  # none | api_key | oauth

    @abstractmethod
    async def fetch_vacancies(self) -> list[VacancyData]:
        """Все размещённые вакансии компании на сайте."""

    @abstractmethod
    async def fetch_stats(self, external_id: str) -> Stats:
        """Просмотры и отклики по конкретному размещению."""

    @abstractmethod
    async def fetch_responses(self, external_id: str) -> list[ResponseData]:
        """Свежие отклики кандидатов по размещению."""

    # ---- Опционально ----
    def supports_resume_search(self) -> bool:
        return False

    async def search_resumes(self, query: dict) -> list[ResumeData]:
        raise NotImplementedError

    def supports_webhooks(self) -> bool:
        return False

