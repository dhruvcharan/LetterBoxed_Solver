#STAGE 1: Builder image
FROM python:3.11-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     python3-dev \
#     && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

# Install dependencies
RUN pip install --upgrade pip && \
    pip install uv && \
    uv pip install --system .

# STAGE 2: Runtime image
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --chown=appuser:appgroup . .

RUN mkdir -p /app/logs && \
    chown -R appuser:appgroup /app

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

USER appuser

EXPOSE ${PORT}

CMD gunicorn --bind 0.0.0.0:${PORT} \
    --workers=4 \
    --threads=2 \
    --timeout=120 \
    --log-level=info \
    --log-file=/app/logs/gunicorn.log \
    --access-logfile=/app/logs/access.log \
    --error-logfile=/app/logs/error.log \
    --capture-output \
    wsgi:app