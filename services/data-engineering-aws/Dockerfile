FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY packages/ ./packages/
COPY services/ ./services/
RUN pip install --no-cache-dir .
ENV SAWTNA_PROJECT_ROOT=/app
ENTRYPOINT ["python", "-m", "sawtna.data_engineering"]
CMD ["collect"]
