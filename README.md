# Сервис микроблогов (Аналог Twitter для корпоративной сети)

## Описание
Бэкенд для корпоративного сервиса микроблогов, реализованное на **FastAPI** с использованием **PostgreSQL, 
SQLAlchemy (async)** и **Alembic** для миграций. Функционал включает:
- Создание/удаление твитов (с опциональными медиафайлами).
- Лайки/анлайки твитов.
- Фолловинг/анфолловинг пользователей.
- Получение ленты твитов (сортировка по популярности: убывание по количеству лайков).
- Просмотр профилей пользователей (с followers/following).

Данные хранятся в PostgreSQL. Аутентификация по api-key в HTTP-header. Медиафайлы сохраняются в /media и подаются 
как статические файлы.
В ответах GET /api/tweets attachments возвращаются как relative paths (например, "/media/uuid_file.jpg"), которые 
можно использовать напрямую в UI (монтируется на /media).

Документация API доступна по /docs (Swagger) после запуска.

## Требования
- Docker и Docker Compose
- Python 3.13+

## Установка и запуск
### Через Docker Compose (рекомендуется)
1. Склонируйте репозиторий: `git clone <название_репозитория>`.
2. Создайте `.env` в корне, например:
postgres_user=postgres
postgres_password=postgres
postgres_host=db
postgres_port=5432
postgres_db=postgres_db
3. Запустите: `docker-compose up -d --build`.
4. Приложение доступно на http://localhost:8000. Swagger: http://localhost:8000/docs.
5. Для инициализации тестовых данных, в Docker добавлены файлы из `init_data.py`.
6. Media файлы сохраняются в /media (доступны на http://localhost:8000/media/<uuid_file.jpg>).

### Локально (без Docker)
1. Установите зависимости: `pip install -r requirements.txt`.
2. Настройте PostgreSQL и `.env`.
3. Примените миграции: `alembic upgrade head`.
4. Запустите: `uvicorn app.main:app --reload`.
5. Инициализируйте данные: `python init_data.py`.

## Зависимости

- **requirements.txt** — зависимости для продакшена (Docker)
- **requirements-dev.txt** — зависимости для разработки, тестов и CI

## Тестирование
- Интеграционные и unit-тесты: `pytest` (покрытие ~90%).
- Линтеры: `flake8 .` 
- Форматирование: `black .` + `isort .`
- Mypy: `mypy .` (статическая типизация, ошибок нет после исправлений).

## CI/CD
CI на GitHub Actions (.github/workflows/ci.yml): lint, mypy, тесты.

## Тестовые пользователи
| **Имя**      | **API-ключ** |
|--------------|--------------|
| Test User 1  | test         |
| Test User 2  | test2        |
| Test User 3  | test3        |

## Структура проекта
- `app/`: Основной код (routes, crud, models и т.д.)
- `migrations/`: Alembic миграции
- `tests/`: Unit + integration тесты
- `media/`: Загруженные медиафайлы (gitignore для содержимого)
- `static/`: Фронтенд
- `.github/workflows/`: CI
