# newsdigest

Concise setup for local run and Docker.

## Quickstart (local, SQLite)

```bash
cd newsdigest
uv sync
uv run python manage.py migrate --settings=config.settings.local
uv run python manage.py createsuperuser --settings=config.settings.local
uv run python manage.py runserver 0.0.0.0:8000 --settings=config.settings.local
```

- Admin: http://127.0.0.1:8000/admin/
- Fetch feeds manually: `uv run python manage.py fetch_feeds --settings=config.settings.local`

## Quickstart (Docker Compose, Postgres + Redis)

```bash
cd newsdigest
docker compose up --build
```

First-time setup in another shell:

```bash
docker compose exec web python manage.py migrate --settings=config.settings.base
docker compose exec web python manage.py createsuperuser --settings=config.settings.base
```

Services:
- web: Django app on http://127.0.0.1:8000
- worker: Celery worker
- beat: Celery beat (periodic tasks)
- postgres: Postgres database
- redis: Redis broker/result backend

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT
