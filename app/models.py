"""
Bu dosya SQLAlchemy modellerini içerir.
"""

from sqlalchemy import Boolean, Column, Integer, String

from app.database import Base


class Task(Base):
    """
    Task modeli, görev bilgilerini tutan SQLAlchemy modelidir.
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    completed = Column(Boolean, default=False)
