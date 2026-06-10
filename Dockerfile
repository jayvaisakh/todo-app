# Stage 1: install Python dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: create smaller final image
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY app/ .
COPY tests/ /app/tests/

RUN python -m pip install --no-cache-dir --upgrade pip==26.1.2
RUN useradd --create-home appuser

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
