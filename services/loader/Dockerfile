FROM python:3.11-slim AS builder

ENV POETRY_VERSION=2.1.3 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# non-root user
RUN groupadd -r appuser --gid=999 && \
    useradd -r -g appuser --uid=999 --home-dir=/app --shell=/bin/bash appuser

RUN bash -o pipefail -c 'curl -sSL https://install.python-poetry.org | POETRY_VERSION=${POETRY_VERSION} POETRY_HOME=${POETRY_HOME} python3 -'
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app
RUN chown appuser:appuser /app

COPY --chown=appuser:appuser pyproject.toml poetry.lock README.md ./
RUN poetry install --only=main --no-root && poetry cache clear . --all --no-interaction

# source code
COPY --chown=appuser:appuser src ./src


# runtime
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/src /app/src

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
USER appuser

ENTRYPOINT ["python", "src/loader/loader.py"]
