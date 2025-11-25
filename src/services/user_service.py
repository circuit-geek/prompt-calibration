from fastapi.exceptions import HTTPException

from src.entities.db_model import User
from src.entities.schema import UserRegister, UserRegisterSuccess, UserLogin
from src.utils.auth_utils import password_hash, create_access_token


async def user_register(user_data: UserRegister) -> UserRegisterSuccess:
    user_data.password = password_hash.hash(user_data.password)
    user = User.create(**user_data.model_dump())
    return UserRegisterSuccess(
        user_id=str(user.id),
        name=user.name,
        email_id=user.email_id
    )

async def user_login(user_data: UserLogin):
    user = User.get_or_none(User.email_id == user_data.email_id)
    if user:
        password_verify = password_hash.verify(user_data.password, user.password)
        if not password_verify:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(user)
    return {
        "message": "Logged in successfully!",
        "user_id": str(user.id),
        "token": access_token
    }

