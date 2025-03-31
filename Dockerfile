# Use the official Python 3.10.7 slim image
FROM python:3.10.7-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GUNICORN_WORKERS=3

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Use shell form so $GUNICORN_WORKERS is expanded at runtime
CMD gunicorn --bind 0.0.0.0:5000 --workers $GUNICORN_WORKERS --timeout 120 app:app
