FROM node:22-alpine AS web-build
WORKDIR /web
COPY partie-4-frontend/package*.json ./
RUN npm ci
COPY partie-4-frontend/ ./
RUN npm run build
FROM python:3.12-slim
WORKDIR /app
COPY requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt
COPY pyproject.toml ./
COPY commun/packages/ ./commun/packages/
COPY commun/data/seed/ ./commun/data/seed/
COPY partie-1-data-engineering/ ./partie-1-data-engineering/
COPY partie-2-backend/ ./partie-2-backend/
COPY partie-3-nlp/ ./partie-3-nlp/
COPY partie-4-frontend/ ./partie-4-frontend/
COPY partie-5-analytics/ ./partie-5-analytics/
RUN pip install --no-cache-dir --no-deps .
COPY --from=web-build /web/dist /app/partie-4-frontend/dist
ENV PYTHONUNBUFFERED=1 PORT=8000 SAWTNA_PROJECT_ROOT=/app
EXPOSE 8000
CMD ["python", "-m", "sawtna.serve"]
