from fastapi import FastAPI
from app.routes import router
from app.database import engine, Base
app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(router)
@app.get("/")
def read_root():
    return {"message": "FastAPI CRUD App is running!"}
