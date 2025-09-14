# ---- Builder -----------------------------------------------------------------
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=">=2.0.0,<3.0.0" \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for building wheels (add more if your deps need them)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry 2.x
RUN python -m pip install --upgrade pip && \
    pip install "poetry${POETRY_VERSION}"

# Use layer caching: lock files first, then install deps (without your source)
COPY pyproject.toml poetry.lock* ./
# In Poetry 2: --only=main keeps just default deps; --no-root skips installing your package yet
RUN poetry install --no-interaction --no-ansi --no-root --only=main

# Now copy the project and build a wheel
COPY . .
RUN poetry build -f wheel

# ---- Runtime -----------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Non-root user
RUN adduser --disabled-password --gecos "" --uid 10001 app
WORKDIR /app

# Install only your wheel and runtime deps
COPY --from=builder /app/dist/*.whl /tmp/dist/
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir /tmp/dist/*.whl && \
    rm -r /tmp/dist/

# Copy alembic files
COPY --chown=app:app expanses_tracker/persistence/migrations /app/expanses_tracker/persistence/migrations
COPY --chown=app:app alembic.ini /app/alembic.ini
COPY --chown=app:app entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

USER app

CMD ["/app/entrypoint.sh"]
