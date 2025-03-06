import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:mysecretpassword@localhost:5432/fastapi_crud")
REDIS_URL = "redis://redis_cache:6379"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)
