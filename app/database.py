"""Veritabanı bağlantısı ve Redis yapılandırmalarını içeren modül."""

import os

import redis.asyncio as redis
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# PostgreSQL Bağlantı Bilgileri
DB_HOST = os.getenv("DB_HOST", "postgres_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mysecretpassword")
DB_NAME = os.getenv("POSTGRES_DB", "fastapi_crud")
DB_PORT = os.getenv("DB_PORT", "5432")

# Uzun satırı birkaç satıra bölerek düzeltme
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy Bağlantısı
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Redis Bağlantı Bilgileri
REDIS_HOST = os.getenv("REDIS_HOST", "redis_cache")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")


async def get_redis():
    """
    Redis bağlantısını yöneten asenkron fonksiyon.
    """
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=int(REDIS_PORT),
        decode_responses=True,
    )
    try:
        yield redis_client
    finally:
        # `aclose()` ile daha temiz kapatma
        await redis_client.aclose()
