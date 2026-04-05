FROM python:3.11-slim

WORKDIR /app

RUN useradd --create-home appuser && chown appuser:appuser /app

COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore --upgrade pip && \
    pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

COPY benchmark.py test_benchmark.py ./

USER appuser

CMD ["python", "benchmark.py"]