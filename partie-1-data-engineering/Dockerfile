FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY commun/packages/ ./commun/packages/
COPY partie-1-data-engineering/ ./partie-1-data-engineering/
COPY partie-2-backend/ ./partie-2-backend/
COPY partie-3-nlp/ ./partie-3-nlp/
COPY partie-4-frontend/ ./partie-4-frontend/
COPY partie-5-analytics/ ./partie-5-analytics/
RUN pip install --no-cache-dir .
ENV SAWTNA_PROJECT_ROOT=/app
ENTRYPOINT ["python", "-m", "sawtna.data_engineering"]
CMD ["collect"]
