from pydantic import BaseModel
from enum import Enum
from typing import Optional

class UserModel(BaseModel):
    user_id: str
    name: str
    email: str

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserRegisterSuccess(BaseModel):
    user_id: str
    name: str
    email_id: str

class UserLogin(BaseModel):
    email_id: str
    password: str

class UserChatRequest(BaseModel):
    base_system_prompt: Optional[str]
    user_prompt: str
    model: Optional[str]

class ChatResponse(BaseModel):
    message: str

class ChatFeedback(BaseModel):
    rating: int
    feedback: str

class NewChatSession(BaseModel):
    user_id: str
    chat_name: str

class FeedbackAction(str, Enum):
    CALIBRATE_PROMPT = "calibrate_prompt"
    NO_ACTION_NEEDED = "no_action_needed"

class ChatObject(BaseModel):
    session_id: str
    message: str
    model_used: Optional[str] = None
    prompt_version_id: Optional[str] = None
    rating: Optional[int] = None
    feedback: Optional[str] = None
    action: Optional[str] = None

class LLMFeedbackInput(BaseModel):
    rating: int
    feedback: str
    base_system_prompt: str

class LLMFeedbackOutput(BaseModel):
    calibrated_system_prompt: str


