# JobMatrix — Архитектура

_Архитектура JobMatrix: плагинные адаптеры сайтов, WebSocket-оповещения с звуком, модель данных, режимы local/server, деплой._

# JobMatrix — Архитектура

_Панель работодателя: матрица «вакансия × сайт», отклики с оповещениями, поиск резюме. Плагинные адаптеры на ~6 сайтов, работа локально и на сервере._

## 1. Общая схема

```
        ┌────────────────────────────────────────────────────┐
        │               WEB-ИНТЕРФЕЙС (браузер)              │
        │  Матрица: строки = вакансии, столбцы = сайты       │
        │  + кнопка «Найти человека»                         │
        │  + всплывающие оповещения и звук при отклике 🔔    │
        └───────┬───────────────────────────┬────────────────┘
                │ REST API (JSON)           │ WebSocket /ws/events
        ┌───────▼───────────────────────────▼────────────────┐
        │               BACKEND (FastAPI)                    │
        │  /api/vacancies  /api/resumes  /api/notifications  │
        │  + WebSocket-хаб оповещений (notifications/hub.py) │
        └───────┬───────────────────────────┬────────────────┘
                │                           │
   ┌────────────▼───────────┐   ┌───────────▼──────────────────┐
   │   ADAPTERS (плагины)   │   │  NOTIFICATIONS              │
   │   ~6 сайтов, единый    │   │  detector: diff откликов →  │
   │   интерфейс SiteAdapter│   │  событие → WebSocket → UI   │
   └────────┬───────────────┘   └───────────┬──────────────────┘
            │                              │
   ┌────────▼──────────────────────────────▼─────────────────┐
   │              САЙТЫ РАЗМЕЩЕНИЯ                           │
   │   hh.ru · SuperJob · Авито · Rabota.ru · Zarplata.ru    │
   │   (API / парсинг / вебхуки, где есть)                   │
   └─────────────────────────────────────────────────────────┘
            │
   ┌────────▼──────────────────────────────┐
   │              БАЗА ДАННЫХ              │
   │  SQLite (локально) / PostgreSQL (серв.)│
   └────────────────────────────────────────┘
            ▲
   ┌────────┴──────────────┐
   │   SCHEDULER           │
   │  периодический сбор:  │
   │  вакансии, просмотры, │
   │  отклики → события    │
   └───────────────────────┘
```

## 2. Ключевые понятия

- **Работодатель** — владелец вакансий. Все вакансии в JobMatrix принадлежат ему.
- **Вакансия** — сущность компании (одна строка в матрице).
- **Размещение (Listing)** — факт публикации вакансии на конкретном сайте.
- **Отклик (Response)** — кандидат откликнулся на вакансию на сайте.
- **Событие (Event)** — новое оповещение: «новый отклик на hh.ru по вакансии X».

## 3. Плагинные адаптеры сайтов (`adapters/`)

### Идея

Каждый сайт — отдельный класс-адаптер с **единым интерфейсом**. Система не знает деталей сайта — только `SiteAdapter`. Добавление нового сайта = один класс + регистрация в реестре. Каркас рассчитан на **~6 сайтов**.

### Интерфейс

```python
# adapters/base.py
class SiteAdapter(ABC):
    site_key: str          # "hh_ru"
    site_name: str         # "hh.ru"
    auth_type: str         # "api_key" | "oauth" | "none"

    @abstractmethod
    async def fetch_vacancies(self) -> list[VacancyData]:
        """Все размещённые вакансии компании на сайте."""

    @abstractmethod
    async def fetch_stats(self, listing) -> Stats:
        """Просмотры и отклики по конкретному размещению."""

    @abstractmethod
    async def fetch_responses(self, listing) -> list[ResponseData]:
        """Свежие отклики кандидатов."""

    # Опционально:
    def supports_resume_search(self) -> bool: return False
    async def search_resumes(self, query) -> list[ResumeData]: ...

    # Опционально (где сайт даёт вебхуки):
    def supports_webhooks(self) -> bool: return False
    async def handle_webhook(self, payload) -> Event: ...
```

### Реестр (`adapters/registry.py`)

```python
ADAPTERS = {
    "hh_ru":      HhRuAdapter,
    "superjob":   SuperJobAdapter,
    "avito":      AvitoAdapter,
    "rabota_ru":  RabotaRuAdapter,
    "zarplata_ru": ZarplataRuAdapter,
    # + 1 резервный слот под будущий сайт
}
```

Включение/выключение — через `.env`:

```ini
ENABLED_SITES=hh_ru,superjob,avito
```

### Заводская нормализация

Все адаптеры возвращают **единые модели данных**, поэтому в БД и UI сайты неразличимы:

```
VacancyData: external_id, site, title, city, salary_from, salary_to,
             currency, url, description, published_at
Stats:       views_count, responses_count
ResponseData: candidate_name, resume_url, responded_at, message
ResumeData:   resume_url, candidate_name, match_score
```

## 4. Оповещения о новых откликах 🔔

### Поток

```
scheduler/detector (каждые N минут)
   │
   ├─▶ adapter.fetch_stats() / fetch_responses()
   │
   ├─▶ сравнение с сохранёнными счётчиками (responses_count)
   │     если откликов стало больше → создаём Response + Event
   │
   └─▶ notifications/hub.py → рассылка по WebSocket
         │
         ▼
   браузер: Notification API (всплывающее окно)
            + Web Audio API (звуковой сигнал)
```

### WebSocket-хаб (`notifications/hub.py`)

- Эндпоинт `WS /ws/events` — браузер держит соединение.
- При новом `Event` хаб рассылает JSON всем подключённым клиентам:

```json
{
  "type": "new_response",
  "vacancy_title": "Python-разработчик",
  "site": "hh_ru",
  "candidate_name": "Иван П.",
  "resume_url": "https://...",
  "ts": "2025-01-01T12:00:00Z"
}
```

- Если WebSocket недоступен — fallback на **SSE** или **long-polling** (`/api/notifications/poll`).

### Браузер (`api/static/`)

- `Notification.requestPermission()` — при первом открытии.
- Получение события → показ уведомления (Popup) + проигрывание звука через `AudioContext` (короткий «бип»).
- Настройки: звук вкл/выкл, показывать только важные события, период «не беспокоить».

### Обнаружение новых откликов (`notifications/detector.py`)

- Сравнивает `responses_count` текущего сбора с сохранённым в БД.
- Где сайт даёт список откликов — детектор извлекает новых кандидатов по дате.
- Где сайт даёт вебхуки (hh.ru в будущем) — событие приходит мгновенно, без опроса.

## 5. Backend API

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/api/vacancies` | Матрица «вакансия × сайт» |
| GET | `/api/vacancies/{id}` | Карточка вакансии |
| POST | `/api/vacancies` | Добавить вакансию в пул |
| PUT/DELETE | `/api/vacancies/{id}` | Обновить/удалить |
| POST | `/api/collect/run` | Принудительный сбор сейчас |
| GET | `/api/sites` | Список сайтов и их статус |
| GET | `/api/responses` | Все отклики (фильтр по вакансии/сайту) |
| GET | `/api/notifications` | Последние события |
| POST | `/api/notifications/ack` | Отметить события прочитанными |
| WS | `/ws/events` | Реальное время: новые отклики |
| POST | `/api/vacancies/{id}/find-person` | Поиск резюме по вакансии |
| GET | `/api/vacancies/{id}/resumes` | Результаты поиска резюме |

## 6. Модель данных (`storage/models.py`)

```
Company            # работодатель (одна компания на инстанс)
  id, name, site_id_on_hh, site_id_on_superjob ...

Vacancy            # вакансия компании (строка матрицы)
  id, title, company_id, city, salary_from, salary_to,
  currency, description, created_at, active

VacancyListing     # размещение на сайте (ячейка матрицы)
  id, vacancy_id FK, site, external_id, url,
  published_at, views_count, responses_count,
  last_checked_at
  UNIQUE(vacancy_id, site)

Response           # отклик кандидата
  id, listing_id FK, candidate_name, resume_url,
  responded_at, message, is_new (флаг для оповещений)

Event              # событие оповещения
  id, type ("new_response"), listing_id FK,
  payload (JSON), created_at, read_at

ResumeMatch        # найденное резюме под вакансию
  id, vacancy_id FK, site, resume_url,
  candidate_name, match_score, searched_at

CollectLog         # журнал сборов
  id, site, started_at, finished_at, status, errors
```

Ключевая идея матрицы: **вакансия одна** → много `VacancyListing` (по сайту) → одна строка, по ячейке на сайт.

## 7. Режимы работы

### 7.1. Локально

- БД: **SQLite** (`data/jobmatrix.db`).
- Сервер + планировщик + хаб — один процесс (фоновый лаунчер).
- Адрес: `http://localhost:8000`.
- Оповещения работают внутри браузера на этой машине.

### 7.2. Удалённый сервер

- БД: **PostgreSQL** (контейнер).
- `docker-compose`: `db` + `app`.
- Адрес: `http://<сервер>:8000` из любого браузера.
- Оповещения работают у каждого, кто открыл интерфейс в браузере (WebSocket тянет до сервера).

Переключение — только конфигом:

```ini
# config/.env
APP_MODE=local|server
DATABASE_URL=sqlite:///data/jobmatrix.db
# или postgresql://user:pass@db:5432/jobmatrix
COLLECT_INTERVAL_MINUTES=30
ENABLED_SITES=hh_ru,superjob
PORT=8000
SOUND_ENABLED=true
```

## 8. Кроссплатформенный фоновый запуск одной кнопкой

```
двойной клик по start.bat (Windows) / ./start.sh (Linux/macOS)
        │
        ▼
launcher/run.py (pythonw / nohup — фон, без окна терминала)
        │
        ├── поднять FastAPI (uvicorn)
        ├── запустить APScheduler
        ├── открыть http://localhost:8000 в браузере
        └── работать в фоне до остановки
```

- `start.bat` — `pythonw launcher/run.py` (Windows, без консоли).
- `start.sh` — `nohup python3 launcher/run.py &` (Linux/macOS).
- `tray.py` — опциональная иконка в трее: «Открыть», «Остановить», «Статус».

## 9. Деплой на сервер (Docker)

```bash
docker compose up -d
```

Поднимает `db` (PostgreSQL) и `app` (JobMatrix). Доступ — `http://<адрес>:8000`. Для серверного режима — простой токен авторизации `X-Auth-Token`.

## 10. Безопасность и секреты

- API-ключи сайтов — только в `.env` (пример `config/.env.example`), **не в коде**.
- `.gitignore` исключает `.env` и `data/`.
- Токен авторизации для серверного режима.
- Для hh.ru — OAuth-токен работодателя (права на вакансии и отклики компании).

## 11. Ограничения и риски

- **Парсинг** (Авито, rabota.ru): блокировки → задержки, ротация User-Agent, приоритет официальных API.
- **hh.ru**: для чтения вакансий компании токен не нужен, для откликов — нужен OAuth работодателя.
- **SuperJob**: открытое API с ключом.
- **Rate limits**: уважать лимиты сайтов, настройки задержек в `.env`.
- **Отклики без API**: если сайт не отдаёт счётчик откликов — только ручной ввод или вебхук (где есть).

