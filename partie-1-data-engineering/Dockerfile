FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY commun/packages/ ./commun/packages/
COPY partie-1-data-engineering/ ./partie-1-data-engineering/
RUN pip install --no-cache-dir .
ENV SAWTNA_PROJECT_ROOT=/app
ENTRYPOINT ["python", "-m", "sawtna.data_engineering"]
CMD ["collect"]
