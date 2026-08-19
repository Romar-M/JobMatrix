"""Реестр адаптеров сайтов.

Сайты двух видов:
- статичные (hh_ru, superjob, ...) — встроенные адаптеры;
- кастомные (custom_1, ...) — добавлены через UI «+ Сайт», хранятся в БД
  (таблица sites) и обслуживаются GenericAdapter.

В demo-режиме все сайты заменяются заглушкой MockAdapter (тестовые данные).
"""
from sqlalchemy.orm import Session

from config.settings import settings
from adapters.base import SiteAdapter
from adapters.mock import MockAdapter
from adapters.generic import GenericAdapter
from adapters.hh_ru import HhRuAdapter
from adapters.superjob import SuperJobAdapter
from adapters.avito import AvitoAdapter
from adapters.rabota_ru import RabotaRuAdapter
from adapters.zarplata_ru import ZarplataRuAdapter

REAL_ADAPTERS: dict[str, type[SiteAdapter]] = {
    "hh_ru": HhRuAdapter,
    "superjob": SuperJobAdapter,
    "avito": AvitoAdapter,
    "rabota_ru": RabotaRuAdapter,
    "zarplata_ru": ZarplataRuAdapter,
}

SITE_NAMES = {
    "hh_ru": "hh.ru",
    "superjob": "SuperJob",
    "avito": "Авито",
    "rabota_ru": "Rabota.ru",
    "zarplata_ru": "Zarplata.ru",
}

# Базовые URL статичных сайтов (для ссылок в шапке матрицы)
SITE_URLS = {
    "hh_ru": "https://hh.ru",
    "superjob": "https://superjob.ru",
    "avito": "https://www.avito.ru",
    "rabota_ru": "https://rabota.ru",
    "zarplata_ru": "https://zarplata.ru",
}


def static_sites() -> list[dict]:
    """Встроенные сайты (всегда доступны)."""
    result = []
    for key in settings.ENABLED_SITES:
        result.append(
            {
                "key": key,
                "name": SITE_NAMES.get(key, key),
                "url": SITE_URLS.get(key, ""),
                "auth_type": "api_key",
                "is_custom": False,
                "has_api_key": bool(getattr(settings, _token_attr(key), "")),
                "enabled": True,
            }
        )
    return result


def _token_attr(site_key: str) -> str:
    """Имя атрибута настроек с ключом API для статичного сайта."""
    mapping = {
        "hh_ru": "HH_API_TOKEN",
        "superjob": "SUPERJOB_API_KEY",
        "avito": "AVITO_API_TOKEN",
        "rabota_ru": "RABOTA_RU_API_KEY",
        "zarplata_ru": "ZARPLATA_RU_API_KEY",
    }
    return mapping.get(site_key, "")


def custom_sites(db: Session) -> list[dict]:
    """Сайты, добавленные пользователем через UI (таблица sites)."""
    from storage.models import Site

    rows = db.query(Site).order_by(Site.name).all()
    return [
        {
            "key": s.key,
            "name": s.name,
            "url": s.url,
            "auth_type": s.auth_type,
            "api_key": s.api_key,
            "is_custom": True,
            "has_api_key": bool(s.api_key),
            "enabled": s.enabled,
        }
        for s in rows
    ]


def all_sites(db: Session) -> list[dict]:
    """Полный список сайтов для матрицы: статичные + кастомные."""
    return static_sites() + custom_sites(db)


def get_adapter(site_key: str, db: Session | None = None) -> SiteAdapter:
    """Вернуть адаптер для сайта.

    В demo-режиме всегда заглушка MockAdapter (для кастомных — с именем
    и url из БД). В боевом — реальный адаптер для статичных сайтов и
    GenericAdapter для кастомных.
    """
    name = SITE_NAMES.get(site_key, site_key)
    url = SITE_URLS.get(site_key, "")
    auth_type = "api_key"
    api_key = ""

    if db is not None and site_key not in SITE_NAMES:
        # Кастомный сайт: берём данные из БД
        from storage.models import Site

        site = db.query(Site).filter(Site.key == site_key).first()
        if site:
            name, url, auth_type, api_key = (
                site.name,
                site.url,
                site.auth_type,
                site.api_key,
            )

    if settings.DEMO_MODE:
        return MockAdapter(site_key, name, url=url)

    cls = REAL_ADAPTERS.get(site_key)
    if cls is not None:
        return cls()
    return GenericAdapter(site_key, name, url=url, api_key=api_key, auth_type=auth_type)


def enabled_sites() -> list[str]:
    """Ключи статичных сайтов (совместимость со старым кодом)."""
    return settings.ENABLED_SITES

