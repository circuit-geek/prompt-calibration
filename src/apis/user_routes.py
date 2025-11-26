from fastapi import APIRouter, Depends

from src.entities.schema import UserRegister, UserLogin
from src.services.user_service import user_register, user_login
from src.utils.auth_utils import get_current_user

users_router = APIRouter(prefix="/users", tags=["Users"])

@users_router.post("/register")
async def register(user_data: UserRegister):
    response = await user_register(user_data)
    return response

@users_router.post("/login")
async def login(user_data: UserLogin):
    response = await user_login(user_data)
    return response

@users_router.post("/logout")
async def logout(user = Depends(get_current_user)):
    return {"message": "Logged out", "user_id": user.id}