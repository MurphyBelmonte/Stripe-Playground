# Financial Command Center AI - Application Dockerfile
# Multi-stage build for smaller runtime image

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System dependencies for common crypto/build wheels
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libssl-dev \
        ca-certificates \
        curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt requirements_setup_wizard.txt ./
RUN python -m pip install --upgrade pip \
 && pip install -r requirements.txt \
 && pip install -r requirements_setup_wizard.txt \
 && pip install gunicorn==21.2.0

# Copy application code
COPY . /app

# Create non-root user and prepare directories
RUN useradd -m appuser \
 && mkdir -p /app/data /app/secure_config /app/certs \
 && chown -R appuser:appuser /app

# Copy entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Runtime image
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_HOME=/app \
    PORT=8000

WORKDIR /app

# Minimal system deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
 && rm -rf /var/lib/apt/lists/*

# Copy installed site-packages and binaries from builder
COPY --from=base /usr/local /usr/local

# Copy application code and entrypoint
COPY --from=base /app /app
COPY --from=base /entrypoint.sh /entrypoint.sh

# Ensure runtime directories exist with proper ownership
RUN useradd -m appuser \
 && mkdir -p /app/data /app/secure_config /app/certs \
 && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app_with_setup_wizard:app"]


