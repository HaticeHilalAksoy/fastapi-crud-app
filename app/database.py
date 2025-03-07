import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import redis.asyncio as redis

# .env dosyası yükleme
load_dotenv()

# Ortam değişkenlerinden veritabanı ayarlarını al
DB_HOST = os.getenv("DB_HOST", "db")  # Docker içindeki PostgreSQL'in adı "db"
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mysecretpassword")
DB_NAME = os.getenv("DB_NAME", "fastapi_crud")
DB_PORT = os.getenv("DB_PORT", "5432")

# SQLAlchemy bağlantı URL'si oluştur
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Engine ve Session oluşturma
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model
Base = declarative_base()

# Redis bağlantısı
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

async def get_redis():
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )
    try:
        yield redis_client
    finally:
        await redis_client.close()