#!/bin/bash
set -e  # остановить скрипт при любой ошибке

echo "Waiting for database connection..."
sleep 5

# Опционально: добавить проверку подключения к БД перед миграциями
# while ! pg_isready -h $(echo $DATABASE_URL | sed -E 's/.*@([^:]+):.*/\1/') -p $(echo $DATABASE_URL | sed -E 's/.*:([0-9]+)\/.*/\1/') >/dev/null 2>&1; do
#   echo "Database not ready yet, waiting..."
#   echo $DATABASE_URL
#   sleep 2
# done

echo "Database is ready. Running migrations..."
alembic upgrade head

echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000