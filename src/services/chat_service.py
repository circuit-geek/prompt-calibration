import json
from pathlib import Path
from typing import List

import ollama

from src.constants.properties import GPT_MODEL
from src.entities.db_model import Session, Chat
from src.entities.schema import (
    UserChatRequest, ChatFeedback, FeedbackAction,
    NewChatSession, LLMFeedbackInput,
    LLMFeedbackOutput, ChatHistoryItem, SessionInfo
)
from src.utils.llm_utils import client


async def create_new_session(new_chat: NewChatSession) -> Session:
    session = Session.create(user_id=new_chat.user_id, session_name=new_chat.chat_name)
    return session

async def validate_session(session_id: str) -> Session:
    session = Session.get_or_none(Session.id == session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")
    return session

async def generate_response(request: UserChatRequest) -> str:
    installed_models = ollama.list().models
    installed_model_names = [m.model for m in installed_models]

    if request.model not in installed_model_names:
        print(f"Model {request.model} not found.")
        ollama.pull(request.model)
    else:
        print(f"Model {request.model} is already installed.")

    response = ollama.chat(
        model=request.model,
        messages=[
            {"role": "system", "content": request.base_system_prompt},
            {"role": "user", "content": request.user_prompt}
        ],
        stream=False
    )
    return response.message.content


async def create_chat_with_response(session_id: str, user_message: str, assistant_message: str,
                                    model_used: str, prompt_version_id: str = None) -> Chat:

    await validate_session(session_id)

    chat = Chat.create(
        session_id=str(session_id),
        user_message=user_message,
        assistant_message=assistant_message,
        model_used=model_used,
        prompt_version_id=prompt_version_id,
        rating=None,
        feedback=None,
        action=None
    )
    return chat


async def get_session_history(user_id: str) -> List[SessionInfo]:

    query = Session.select().where(Session.user_id == user_id)

    sessions = []
    for session in query:
        sessions.append(SessionInfo(
            id=str(session.id),
            user_id=str(session.user_id),
            session_name=session.session_name
        ))

    return sessions


async def get_chat_history_in_session(session_id: str) -> List[ChatHistoryItem]:

    await validate_session(session_id)
    query = Chat.select().where(Chat.session_id == str(session_id))

    history = []
    for chat in query:
        history.append(ChatHistoryItem(
            id=str(chat.id),
            user_message=chat.user_message,
            assistant_message=chat.assistant_message,
            model_used=chat.model_used,
            rating=chat.rating,
            feedback=chat.feedback,
        ))

    return history

async def update_chat_feedback(chat_id: str, feedback: ChatFeedback,
                               action: FeedbackAction = None) -> dict:

    chat = Chat.get_or_none(Chat.id == chat_id)
    if not chat:
        raise ValueError(f"Chat not found: {chat_id}")

    chat.rating = feedback.rating
    chat.feedback = feedback.feedback
    if action:
        chat.action = action.value

    chat.save()

    return {
        "chat_id": str(chat.id),
        "rating": chat.rating,
        "feedback": chat.feedback,
        "action": chat.action
    }


async def act_on_feedback(request: LLMFeedbackInput) -> LLMFeedbackOutput:

    system_prompt = Path("src/prompts/calibrator_system_prompt.jinja").read_text()
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt + str(request.rating) +
                           request.feedback + request.base_system_prompt
            }
        ]
    )
    response = json.loads(response.choices[0].message.content)
    prompt = response["calibrated_system_prompt"]
    
    return LLMFeedbackOutput(
        calibrated_system_prompt=prompt
    )