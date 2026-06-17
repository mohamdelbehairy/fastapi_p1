from fastapi import FastAPI
from sqlmodel import SQLModel

from app.database import engine
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router


app = FastAPI()

@app.on_event("startup")
async def startup():
    SQLModel.metadata.create_all(engine)

app.router.include_router(auth_router)
app.router.include_router(users_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}