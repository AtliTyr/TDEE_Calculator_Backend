#!/bin/bash
# Ждём пока DATABASE_URL станет доступен
echo "Running migrations..."
alembic upgrade head

echo "Starting server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000