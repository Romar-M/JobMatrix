"""Подключение к базе данных (SQLite локально / PostgreSQL на сервере)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config.settings import settings

Base = declarative_base()

_connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    """Создать все таблицы и демо-данные при первом запуске."""
    import storage.models  # noqa: F401 — регистрирует модели в metadata
    Base.metadata.create_all(bind=engine)
    from storage.seed import seed_if_empty
    seed_if_empty()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

