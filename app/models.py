from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # <-- id tanımlı mı? ✅
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
