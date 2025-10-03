# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install uv
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://astral.sh/uv/install.sh | sh
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

ENV DJANGO_SETTINGS_MODULE=config.settings.base

# Collect static just in case (safe if none)
RUN .venv/bin/python -m django --version || true

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

