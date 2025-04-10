# ---------- Stage 1: Builder ----------
FROM python:3.12.9-slim AS builder

# Python configuration
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off

# Install Poetry globally
RUN python -m pip install --upgrade pip && \
    pip install poetry

# Create working directory for poetry and copy dependency files
WORKDIR /usr/src/poetry
COPY ./pyproject.toml ./poetry.lock ./

# Disable virtualenv creation and install only main dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main


# ---------- Stage 2: Final Image ----------
FROM python:3.12 AS final

# Copy installed packages from builder image
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy project source code
WORKDIR /usr/src/bot
COPY ./src .
