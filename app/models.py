"""
This file contains SQLAlchemy models.
"""

from sqlalchemy import Boolean, Column, Integer, String

from app.database import Base


class Task(Base):
    """
    Task model is a SQLAlchemy model that holds task information.
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    completed = Column(Boolean, default=False)
