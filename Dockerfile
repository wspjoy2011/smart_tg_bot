FROM python:3.12.9

# Python configuration
# Don't write .pyc files
# Output logs immediately
# Allow pip to cache packages
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off

# Install Poetry globally
RUN python -m pip install --upgrade pip && \
    pip install poetry

# Copy dependency descriptors
COPY ./poetry.lock /usr/src/poetry/poetry.lock
COPY ./pyproject.toml /usr/src/poetry/pyproject.toml

# Set working directory for dependency install
WORKDIR /usr/src/poetry

# Install only main dependencies (no dev) and skip installing project as a package
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main

# Set working directory for the app itself
WORKDIR /usr/src/bot

# Copy source code into the container
COPY ./src .
