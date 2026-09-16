# Таблица умножения

Интерактивное веб-приложение для тренировки таблицы умножения для детей 7–11 лет.

## Технологический стек

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy 2.x, SQLite, Alembic
- **Frontend**: Jinja2, Tailwind CSS, Vanilla JavaScript
- **Testing**: pytest, pytest-asyncio, httpx

## Установка и запуск

### Быстрый запуск (Windows)

```cmd
start.bat
```

или в PowerShell:

```powershell
.\start.ps1
```

Скрипт автоматически:
- создаст виртуальное окружение (`venv`)
- установит зависимости из `requirements.txt`
- создаст `.env` из `.env.example`
- запустит сервер на http://localhost:8000

Миграции базы данных применяются автоматически при старте приложения.

### Ручная установка

```powershell
# 1. Создайте и активируйте виртуальное окружение
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows PowerShell
# venv\Scripts\activate.bat        # Windows cmd
# source venv/bin/activate         # Linux / macOS

# 2. Установите зависимости
pip install -r requirements.txt

# 3. Создайте файл .env
copy .env.example .env             # Windows
# cp .env.example .env             # Linux / macOS

# 4. Запустите приложение
python -m app.main
```

Приложение будет доступно по адресу http://localhost:8000

### Docker

```bash
docker-compose up --build
```

Приложение будет доступно по адресу http://localhost:8000

`SECRET_KEY` берётся из `.env` (Compose подставляет его через `${SECRET_KEY}`). На сервере задайте реальный случайный ключ:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

База данных хранится в named volume `app_data` и сохраняется между пересборками контейнера.

## Тестирование

Сначала установите dev-зависимости:

```bash
pip install pytest pytest-asyncio httpx
```

Затем запустите тесты:

```bash
pytest
```

## Полезные команды

```bash
python migrate.py      # применить миграции БД вручную
python reset_db.py     # удалить базу и начать заново (с подтверждением)
```

Если база данных в сломанном состоянии — просто удалите файл `math_project.db` и перезапустите приложение: миграции создадут чистую схему автоматически.

## Структура проекта

```
app/
├── main.py                    # FastAPI приложение
├── api/
│   └── routes/               # API маршруты
├── core/
│   └── config.py             # Конфигурация
├── db/
│   ├── database.py           # Подключение к БД
│   └── migrations/           # Alembic миграции
├── models/                   # SQLAlchemy модели
├── schemas/                  # Pydantic схемы
├── services/                 # Бизнес-логика
├── repositories/             # Работа с БД
├── templates/                # Jinja2 шаблоны
└── static/                   # Статические файлы
tests/                        # Тесты
```

## Функции

- 🎯 **Тренировка**: Выбор таблиц и количества вопросов
- ⏱ **На время**: Решение примеров за ограниченное время
- 🔥 **Мои ошибки**: Повторение сложных примеров
- 🏆 **Испытание**: 20 вопросов за 2 минуты
- 📚 **Таблица**: Изучение таблицы умножения
- 📊 **Прогресс**: Отслеживание результатов
- 🎖 **Достижения**: Система наград
- 🔊 **Звуки**: Аудио обратная связь
- 🗣️ **Озвучивание**: Web Speech API

## Лицензия

MIT
