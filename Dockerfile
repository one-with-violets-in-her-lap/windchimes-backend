FROM python:3.10.14-slim

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /windchimes-graphql-api

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

COPY windchimes_backend ./windchimes_backend

ENTRYPOINT ["poetry", "run", "python", "-m", "windchimes_backend.graphql_api.main"]
