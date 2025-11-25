from fastapi import FastAPI
from src.entities.db_model import db_init
from src.apis.user_routes import users_router
from src.apis.chat_routes import chat_router

async def lifespan(app: FastAPI):
    db_init()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(users_router)
app.include_router(chat_router)


