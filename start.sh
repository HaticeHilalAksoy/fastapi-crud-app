#!/bin/sh

echo "⏳ Waiting for PostgreSQL to be ready..."
while ! nc -z postgres_db 5432; do
  sleep 1
done
echo "✅ PostgreSQL is up - starting FastAPI..."

exec uvicorn app.main:app --host 0.0.0.0 --port 8000