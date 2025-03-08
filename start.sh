#!/bin/bash
set -e

echo "PostgreSQL bağlantısı bekleniyor..."
/wait-for-it.sh postgres_db:5432 --timeout=60 --strict -- echo "PostgreSQL bağlantısı tamam!"


echo "Redis bağlantısı kuruluyor..."
/wait-for-it.sh redis_cache:6379 -t 30


echo "Uygulama başlatılıyor..."
uvicorn app.main:app --host 0.0.0.0 --port 8000