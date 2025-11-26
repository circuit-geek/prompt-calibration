from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.entities.db_model import db_init
from src.apis.user_routes import users_router
from src.apis.chat_routes import chat_router

async def lifespan(app: FastAPI):
    db_init()
    yield

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # Allow cookies and authorization headers
    allow_methods=["*"],     # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],     # Allow all headers
)

app.include_router(users_router)
app.include_router(chat_router)


