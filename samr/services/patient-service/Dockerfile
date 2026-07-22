# Stage 1: Builder
FROM python:3.12-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final
FROM python:3.12-slim
RUN groupadd -r samr && useradd -r -g samr samr
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
COPY . .
RUN chown -R samr:samr /app
USER samr
EXPOSE 8002
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3   CMD python manage.py health || exit 1
CMD ["sh", "-c", "until python manage.py migrate --fake-initial --noinput; do sleep 2; done; exec daphne -b 0.0.0.0 -p 8002 config.asgi:application"]
