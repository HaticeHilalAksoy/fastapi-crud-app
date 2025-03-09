"""
Görev yönetimi için API uç noktalarını içeren modül.
"""

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_redis
from app.models import Task

router = APIRouter()


class TaskCreate(BaseModel):
    """Yeni görev oluşturma modelini tanımlayan sınıf."""

    title: str
    description: str


class TaskUpdate(BaseModel):
    """Mevcut görevi güncelleme modelini tanımlayan sınıf."""

    title: str
    description: str
    completed: bool


def get_db():
    """
    Veritabanı bağlantısını yöneten bağımlılık fonksiyonu.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/tasks/")
async def get_tasks(db: Session = Depends(get_db)):
    """
    Tüm görevleri getir (Redis Cache Kullanımı).
    """
    redis = await anext(get_redis())
    cache_key = "tasks_list"
    cached_tasks = await redis.get(cache_key)

    if cached_tasks:
        try:
            tasks = json.loads(cached_tasks)
        except json.JSONDecodeError:
            tasks = None

        if not tasks:
            await redis.delete(cache_key)
            cached_tasks = None

    if cached_tasks:
        return {"cached": True, "tasks": json.loads(cached_tasks)}

    tasks = db.query(Task).all()
    tasks_data = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
        }
        for task in tasks
    ]

    await redis.setex(cache_key, 60, json.dumps(tasks_data if tasks_data else []))

    return {"cached": False, "tasks": tasks_data}


@router.post("/tasks/")
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Yeni görev oluştur (Redis Cache Güncellemesi Dahil).
    """
    redis = await anext(get_redis())
    new_task = Task(
        title=task.title,
        description=task.description,
        completed=False,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    cache_key = "tasks_list"
    cached_tasks = await redis.get(cache_key)
    tasks_data = json.loads(cached_tasks) if cached_tasks else []

    tasks_data.append(
        {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "completed": new_task.completed,
        }
    )

    await redis.setex(cache_key, 60, json.dumps(tasks_data))

    return new_task


@router.put("/tasks/{task_id}")
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
):
    """
    Görevi güncelle (Redis Cache Güncellemesi Dahil).
    """
    redis = await anext(get_redis())
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Görev bulunamadı")

    task.title = task_update.title
    task.description = task_update.description
    task.completed = task_update.completed

    db.commit()
    db.refresh(task)

    cache_key = "tasks_list"
    cached_tasks = await redis.get(cache_key)

    if cached_tasks:
        tasks_data = json.loads(cached_tasks)
        for t in tasks_data:
            if t["id"] == task_id:
                t["title"] = task_update.title
                t["description"] = task_update.description
                t["completed"] = task_update.completed
                break
        await redis.setex(cache_key, 60, json.dumps(tasks_data))

    return task


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Görevi sil (Redis Cache Güncellemesi Dahil).
    """
    redis = await anext(get_redis())
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Görev bulunamadı")

    db.delete(task)
    db.commit()

    cache_key = "tasks_list"
    cached_tasks = await redis.get(cache_key)

    if cached_tasks:
        tasks_data = json.loads(cached_tasks)
        tasks_data = [t for t in tasks_data if t["id"] != task_id]
        await redis.setex(cache_key, 60, json.dumps(tasks_data))

    return {"message": "Görev başarıyla silindi"}
