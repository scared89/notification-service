# Сервис уведомлений 

Сервис для отправки уведомлений с поддержкой fallback (email → sms → telegram) и очередей на Celery.

## Стэк
- **Django 4.2** + **Django REST Framework**
- **PostgreSQL**
- **Redis**
- **Celery**
- **Docker Compose**
---

### 1. Клонирование репозитория

```bash
git clone https://github.com/scared89/notification-service.git
cd notification-service
```

### 2. Настройка переменных окружения

Копируйте шаблон:
```bash
cp .env.example .env
```

### 3. Запуск через Docker Compose

```bash
docker compose up --build
```

Поднимаем контейнеры:
- db — PostgreSQL
- redis — Redis
- backend — Django-приложение
- celery-worker — Celery-воркер
___

### 4. Применение миграций

#### Mac/Linux
```bash
docker compose exec backend python manage.py migrate
```

#### Windows
```bash
winpty docker compose exec backend python manage.py migrate
```

### 5. Тесты

Проект использует pytest + pytest-django + pytest-celery.
Запуск тестов

#### Mac/Linux
```bash
docker compose exec backend pytest -v
```

#### Windows 
```bash
winpty docker compose exec backend pytest -v
```
