# TestITK Wallet Service

Сервис управления кошельками: создание кошельков, проведение операций (DEPOSIT/WITHDRAW) и получение баланса через REST
API.

---

## Технологии

* Python 3.13
* FastAPI
* SQLAlchemy (Async)
* Alembic (миграции)
* PostgreSQL 13+
* Docker, Docker Compose
* Pytest, pytest-asyncio, httpx

---

## Структура проекта

```
│   .dockerignore
│   .gitignore
│   alembic.ini
│   compose.yaml                               # поднимает backend + postgres
│   Dockerfile                                 # сборка образа приложения
│   pytest.ini
│   requirements.txt
│
├───alembic                                    # конфигурация и версии миграций
│   │   env.py
│   │   README
│   └───versions
│           53232ba8e566_add_test_data.py
│           73eeaeee457b_init.py
├───backend
│   │   config.py
│   │   db.py                                  # сессия SQLAlchemy
│   │   lock_wallet.py
│   │   __init__.py                            # точка входа FastAPI
│   ├───api                                    # FastAPI-роутеры
│   │       wallet.py
│   │       __init__.py
│   ├───crud                                   # слой работы с БД
│   │       operation.py
│   │       wallet.py
│   │       __init__.py
│   ├───models                                 # ORM-модели
│   │       wallet.py
│   │       __init__.py
│   └───schemas                                # Pydantic-схемы
│           wallet.py
│           __init__.py
└───tests                                      # unit и интеграционные тесты
        conftest.py
        test_crud_wallet.py
        test_endpoints.py
```

---

## Быстрый старт с Docker Compose

1. Клонируйте репозиторий и перейдите в папку проекта:

   ```bash
   git clone https://github.com/IvanOplesnin/TestITK.git
   cd TestITK
   ```
2. Запустите всё одним командой:

   ```bash
   docker compose up -d --build
   ```

3. При первом запуске нужно запустить миграции.

   ```bash
    docker-compose exec backend alembic upgrade head     
    ```
   В консоли должно отобразиться:

![img.png](img.png)
4. Для прогона тестов.

```bash
   docker-compose exec backend  pytest --cov=. --cov-report=term-missing 
```
---

## Как это работает

### Docker Compose

```yaml
services:
  backend:
    image: ivanya0956/testitk
    working_dir: /TestITK
    ports:
      - "8000:8000"
    environment:
      - PG_LINK=postgresql+asyncpg://postgres:password@database:5432/TestITK
      - PG_LINK_ALEMBIC=postgresql+psycopg2://postgres:password@database:5432/TestITK
    depends_on:
      - database

  database:
    image: postgres:13.2-alpine
    working_dir: /database
    ports:
      - "5433:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=TestITK
    volumes:
      - postgres_data:/var/lib/postgresql/data


volumes:
  postgres_data:
```

* **database** слушает порт 5432 внутри контейнера.(запускает на 5433, так как часто по умолчанию запушен локальный postgres)
* **backend** стартует FastAPI-процесс.
* Миграции запускаем после первого запуска контейнеров. В последующих база данных уже будет подниматься с нужными нам данными.

# Образ приложения уже опубликован на Docker Hub. Достаточно положить в проект файл compose.yaml и выполнить:
```bash
docker compose up -d
```

---

## Миграции Alembic
### Созданы две миграции.
- Первая инициализирует таблицы в БД.
- Вторая заполняет ее тестовыми данными.
 Тестовые данные включают в себя пять кошельков(Wallet)

alembic/versions/53232ba8e566_add_test_data.py
```python
def upgrade() -> None:
    """Upgrade schema."""
    wallets = table(
        "wallet",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("uuid", sa.String, nullable=False, unique=True),
        sa.Column("balance", sa.Integer, nullable=False),
    )
    op.bulk_insert(
        wallets,
        [
            {"id": 1, "uuid": "1111111111", "balance": 1500},
            {"id": 2, "uuid": "2222222222", "balance": 1500},
            {"id": 3, "uuid": "3333333333", "balance": 1500},
            {"id": 4, "uuid": "4444444444", "balance": 1500},
            {"id": 5, "uuid": "5555555555", "balance": 1500},
        ]
    )
```
Пять кошельков имеют uuid "1111111111" и т.д с балансами по 1500.

Для возврата к пустой БД нужно ввести команду. 
   ```bash
   docker-compose exec backend alembic downgrade -1
   ```
---

## API Endpoints

### 1. Проведение операции

```
POST /api/v1/wallets/{wallet_uuid}/operation
Content-Type: application/json
```

**Тело запроса**:

| Поле            | Тип     | Описание                          |
|-----------------|---------|-----------------------------------|
| operation\_uuid | string  | UUID операции для идемпотентности |
| operation\_type | string  | "DEPOSIT" или "WITHDRAW"          |
| amount          | integer | Сумма операции (> 0)              |

**Успешный ответ**:

* Код 200 OK
* Тело: `str` — UUID созданной транзакции

**Ошибки**:

* 400 Bad Request при недостатке средств или дублировании `operation_uuid`
* 404 Not Found, если кошелёк не найден

---

### 2. Получение баланса

```
GET /api/v1/wallets/{wallet_uuid}
```

**Успешный ответ**:

* Код 200 OK
* Тело (WalletResponse):

  ```json
  {
    "id": 1,
    "uuid": "1111111111",
    "balance": 1500
  }
  ```
**Ошибки**:
* 404 Not Found, если кошелёк не найден

---

## Тестирование

### Установка dev-зависимостей

```bash
pip install --dev pytest pytest-asyncio httpx sqlalchemy[asyncio] aiosqlite
```

### Настройка pytest (`pytest.ini`)

```ini
[pytest]
python_files = tests/test_*.py
asyncio_mode = auto
pythonpath = .
asyncio_default_fixture_loop_scope = session
```

### Запуск тестов

```bash
docker-compose exec backend  pytest --cov=. --cov-report=term-missing
```

* **Unit-тесты CRUD-слоя** проверяют логику `update_wallet`, `get_wallet_by_uuid` и обработку ошибок.
* **Интеграционные тесты** через `httpx.AsyncClient` (`ASGITransport`) покрывают HTTP-эндпоинты.

---

## Особенности реализации

* **Конкурентность**

    * DB-level lock: `SELECT … FOR UPDATE` в транзакции
    * In-process lock: `asyncio.Lock` для защиты внутри одного процесса
        При высокой нагрузке на один кошелек будет ограничивать кол-во запросов к БД. Даже если у нас запущено несколько экземпляров приложения.

* **Идемпотентность**
  Повторная попытка провести операцию с тем же `operation_uuid` возвращает 400 и не меняет баланс.

* **PEP8 и линтинг**
  Весь код соответствует PEP8.

---
