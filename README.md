# Django theaters app

## База данных

<img width="655" alt="Снимок экрана 2024-06-17 в 12 49 29" src="https://github.com/agent-yandex/theaters_django/assets/88597840/4fcd5a90-c1d5-40e0-9dc6-dfb7ce3a3f93">

## Установка

1. Развернуть Docker контейнер с PostgreSQL

```bash
docker run -d --name django_theaters -p 58921:5432 -e POSTGRES_USER=nikita -e POSTGRES_PASSWORD=qwerty postgres:15.5
```

2. Установка зависимостей

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Миграции базы данных

```bash
python3 manage.py migrate
```

4. Запуск приложения

```bash
python3 manage.py runserver
```