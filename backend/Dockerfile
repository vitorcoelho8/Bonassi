FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY backend .
COPY frontend /app/frontend

WORKDIR /app/backend

EXPOSE 5001

CMD ["sh", "-c", "flask --app app.main:app db upgrade && flask --app app.main:app init-db && gunicorn --bind 0.0.0.0:5001 app.main:app"]
