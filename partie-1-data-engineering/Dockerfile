FROM python:3.12-slim
WORKDIR /app
COPY requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt
COPY pyproject.toml ./
COPY commun/packages/ ./commun/packages/
COPY partie-1-data-engineering/ ./partie-1-data-engineering/
COPY partie-2-backend/ ./partie-2-backend/
COPY partie-3-nlp/ ./partie-3-nlp/
COPY partie-4-frontend/ ./partie-4-frontend/
COPY partie-5-analytics/ ./partie-5-analytics/
COPY commun/scripts/download_ocr.py ./commun/scripts/download_ocr.py
RUN pip install --no-cache-dir ".[ocr]"
ENV SAWTNA_PROJECT_ROOT=/app PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-m", "sawtna.data_engineering"]
CMD ["collect"]
