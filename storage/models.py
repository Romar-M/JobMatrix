"""Модели данных JobMatrix.

Компания -> Вакансии -> Размещения (сайт) -> Отклики / События / Резюме.
Сайты: статичные (hh_ru, superjob, ...) + кастомные, добавленные через UI.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from storage.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Site(Base):
    """Пользовательский сайт размещения, добавленный через интерфейс («+ Сайт»).

    В demo-режиме работает как заглушка (MockAdapter), в боевом — как
    GenericAdapter, который шлёт HTTP-запросы на указанный URL.
    """

    __tablename__ = "sites"

    id = Column(Integer, primary_key=True)
    key = Column(String(50), unique=True, nullable=False)  # например: custom_1
    name = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    auth_type = Column(String(20), default="api_key")  # api_key | oauth | none
    api_key = Column(String(500), default="")
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, default="Моя компания")
    created_at = Column(DateTime, default=utcnow)

    vacancies = relationship("Vacancy", back_populates="company")


class Vacancy(Base):
    """Вакансия компании — строка матрицы."""

    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String(200), nullable=False)
    city = Column(String(120), default="")
    salary_from = Column(Integer, nullable=True)
    salary_to = Column(Integer, nullable=True)
    currency = Column(String(10), default="RUB")
    experience = Column(String(50), default="1-3 года")
    description = Column(Text, default="")
    skills = Column(Text, default="")  # через запятую — для поиска резюме
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

    company = relationship("Company", back_populates="vacancies")
    listings = relationship(
        "VacancyListing", back_populates="vacancy", cascade="all, delete-orphan"
    )
    resume_matches = relationship("ResumeMatch", back_populates="vacancy")


class VacancyListing(Base):
    """Размещение вакансии на конкретном сайте (ячейка матрицы)."""

    __tablename__ = "vacancy_listings"
    __table_args__ = (UniqueConstraint("vacancy_id", "site", name="uq_listing_site"),)

    id = Column(Integer, primary_key=True)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    site = Column(String(50), nullable=False)  # ключ адаптера: hh_ru, custom_1 ...
    external_id = Column(String(100), default="")
    url = Column(String(500), default="")
    status = Column(String(20), default="published")  # published | draft | archived
    published_at = Column(DateTime, nullable=True)

    views_count = Column(Integer, default=0)
    responses_count = Column(Integer, default=0)
    last_checked_at = Column(DateTime, nullable=True)

    vacancy = relationship("Vacancy", back_populates="listings")
    responses = relationship("Response", back_populates="listing", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="listing", cascade="all, delete-orphan")


class Response(Base):
    """Отклик кандидата на размещение."""

    __tablename__ = "responses"

    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey("vacancy_listings.id"), nullable=False)
    candidate_name = Column(String(200), default="")
    resume_url = Column(String(500), default="")
    message = Column(Text, default="")
    responded_at = Column(DateTime, default=utcnow)
    is_new = Column(Boolean, default=True)  # флаг для оповещений

    listing = relationship("VacancyListing", back_populates="responses")


class Event(Base):
    """Событие оповещения (например, «новый отклик»)."""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    type = Column(String(50), default="new_response")  # new_response | system
    listing_id = Column(Integer, ForeignKey("vacancy_listings.id"), nullable=True)
    vacancy_title = Column(String(200), default="")
    site = Column(String(50), default="")
    payload = Column(Text, default="{}")  # JSON
    created_at = Column(DateTime, default=utcnow)
    read_at = Column(DateTime, nullable=True)

    listing = relationship("VacancyListing", back_populates="events")


class ResumeMatch(Base):
    """Найденное резюме под вакансию («Найти человека»)."""

    __tablename__ = "resume_matches"

    id = Column(Integer, primary_key=True)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    site = Column(String(50), nullable=False)
    resume_url = Column(String(500), default="")
    candidate_name = Column(String(200), default="")
    title = Column(String(200), default="")
    match_score = Column(Integer, default=0)  # 0-100
    searched_at = Column(DateTime, default=utcnow)

    vacancy = relationship("Vacancy", back_populates="resume_matches")


class CollectLog(Base):
    """Журнал сборов данных с сайтов."""

    __tablename__ = "collect_logs"

    id = Column(Integer, primary_key=True)
    site = Column(String(50), default="")
    started_at = Column(DateTime, default=utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="running")  # running | ok | error
    message = Column(Text, default="")

