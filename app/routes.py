from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import SessionLocal, get_redis
from app.models import Task
import json

router = APIRouter()

class TaskCreate(BaseModel):
    title: str
    description: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/tasks/")
async def get_tasks(db: Session = Depends(get_db)):
    redis = await anext(get_redis())  # ✅ Redis bağlantısını async alıyoruz
    cache_key = "tasks_list"
    
    cached_tasks = await redis.get(cache_key)  # ✅ `await` ekledik!

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
    tasks_data = [{"id": task.id, "title": task.title, "description": task.description, "completed": task.completed} for task in tasks]

    await redis.setex(cache_key, 60, json.dumps(tasks_data if tasks_data else []))  # ✅ `await` ekledik!

    return {"cached": False, "tasks": tasks_data}

@router.post("/tasks/")
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    redis = await anext(get_redis())  # ✅ Redis bağlantısını async alıyoruz
    new_task = Task(title=task.title, description=task.description, completed=False)
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    cache_key = "tasks_list"
    cached_tasks = await redis.get(cache_key)  # ✅ `await` ekledik!

    if cached_tasks:
        tasks_data = json.loads(cached_tasks)
    else:
        tasks_data = []

    tasks_data.append({
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "completed": new_task.completed
    })

    await redis.setex(cache_key, 60, json.dumps(tasks_data))  # ✅ `await` ekledik!

    return new_task
