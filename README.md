![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![Pydantic](https://img.shields.io/badge/Pydantic-2.13-orange)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-supported-blue)
![Pytest](https://img.shields.io/badge/Pytest-9.0-yellow)
![Coverage](https://img.shields.io/badge/Coverage-83%25-brightgreen)

# Wallet Service API

REST API для управления балансом кошельков. Реализован на FastAPI с асинхронной архитектурой, конкурентной обработкой запросов через row-level locking и полным покрытием тестами.

## Содержание
- [Технологии](#технологии)
- [Функциональность API](#функциональность-api)
- [Конкурентность](#конкурентность)
- [Начало работы](#начало-работы)
- [API Документация](#api-документация)
- [Тестирование](#тестирование)


## Технологии
- [FastAPI](https://fastapi.tiangolo.com/) - современный веб-фреймворк
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/) - асинхронный ORM
- [PostgreSQL](https://www.postgresql.org/) - реляционная база данных
- [Pydantic](https://docs.pydantic.dev/) - валидация данных
- [Alembic](https://alembic.sqlalchemy.org/) - миграции БД
- [Pytest](https://docs.pytest.org/) - фреймворк для тестирования
- [Docker](https://www.docker.com/) - контейнеризация

## Функциональность API

### Кошельки
- **Получение баланса** — `GET /api/v1/wallets/{wallet_uuid}` — возвращает текущий баланс кошелька
- **Пополнение (DEPOSIT)** — `POST /api/v1/wallets/{wallet_uuid}/operation` — зачисление средств
- **Снятие (WITHDRAW)** — `POST /api/v1/wallets/{wallet_uuid}/operation` — списание средств с проверкой достаточности

### Валидация
- UUID кошелька — строгая валидация формата UUID v4
- Сумма операции — положительное Decimal с двумя знаками после запятой
- Тип операции — только DEPOSIT или WITHDRAW

### Обработка ошибок
- **400** — недостаточно средств, невалидный тип операции
- **404** — кошелёк не найден
- **409** — конфликт целостности данных (сработал constraint БД)
- **422** — ошибка валидации входных данных
- **500** — внутренняя ошибка сервера или БД

## Конкурентность

Параллельные запросы к одному кошельку обрабатываются корректно благодаря:
- `SELECT ... FOR UPDATE` — блокировка строки на время транзакции
- `CHECK (balance >= 0)` на уровне БД — дополнительная защита от гонки данных
- Атомарные операции — каждый запрос видит актуальный баланс

При высоких нагрузках рекомендуется добавить `nowait=True` и реализовать retry-логику с exponential backoff на стороне клиента.
## Начало работы

### Требования
- Docker
- Docker Compose

### Установка и запуск

1. **Клонируйте репозиторий**
```bash 
git clone <https://github.com/Kongemal357/itk_academy_test_task.git>
```

2. **Скопируйте и настройте файл переменных окружения**
```bash
cp .env.example .env
```

3. **Запустите приложение**
```bash
docker-compose up -d
```
Приложение будет доступно по адресу: http://localhost:8000

## API Документация
После запуска доступны интерактивные документации:

- Swagger UI - http://localhost:8000/docs

- ReDoc - http://localhost:8000/redoc

## Тестирование

Проект покрыт интеграционными тестами. Для запуска:
```bash
# Запуск всех тестов
docker compose run --rm tests pytest -v

# Только юнит-тесты
docker compose run --rm tests pytest tests/test_unit/ -v

# Только интеграционные тесты
docker compose run --rm tests pytest tests/test_integration/ -v

```