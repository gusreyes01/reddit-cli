FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --requirement requirements.txt \
    && useradd --create-home --uid 10001 appuser
COPY --chown=appuser:appuser src/ ./src/
USER appuser
WORKDIR /data

ENTRYPOINT ["python", "/app/src/cli.py"]
CMD ["--help"]
