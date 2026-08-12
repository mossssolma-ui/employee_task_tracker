FROM python:3.13-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apk add --no-cache postgresql-libs

RUN pip install --no-cache-dir poetry==2.4.1

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-interaction

COPY . .

EXPOSE 8000