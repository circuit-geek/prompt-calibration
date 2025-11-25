from pathlib import Path
from typing import List

import ollama

from src.constants.properties import GPT_MODEL
from src.entities.db_model import Session, Chat
from src.entities.schema import (
    UserChatRequest, ChatResponse,
    ChatFeedback, FeedbackAction,
    NewChatSession, ChatObject,
    LLMFeedbackInput, LLMFeedbackOutput
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

async def generate_response(request: UserChatRequest) -> ChatResponse:
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
    return ChatResponse(
        message=response.message.content
    )


async def add_chat_to_session(chat_object: ChatObject) -> Chat:
    await validate_session(chat_object.session_id)
    chat = Chat.create(
        session_id=str(chat_object.session_id),
        message=chat_object.message,
        model_used=chat_object.model_used,
        prompt_version_id=chat_object.prompt_version_id,
        rating=chat_object.rating,
        feedback=chat_object.feedback,
        action=chat_object.action
    )
    return chat


async def get_session_history(session_id: str) -> List[Chat]:
    await validate_session(session_id)
    query = Chat.select().where(Chat.session_id == str(session_id))
    return list(query)

async def give_response_feedback(chat_id: str, feedback: ChatFeedback,
                                 action: FeedbackAction, request: LLMFeedbackInput):

    chat = Chat.get_or_none(Chat.id == chat_id)
    if not chat:
        raise ValueError(f"Chat not found: {chat_id}")

    chat.rating = feedback.rating
    chat.feedback = feedback.feedback

    if action.NO_ACTION_NEEDED.value:
        print("No action needed continuing to next query")
    elif action.CALIBRATE_PROMPT.value:
        await act_on_feedback(request=request)

    return {
        "chat_id": str(chat.id),
        "rating": chat.rating,
        "feedback": chat.feedback,
        "action": chat.action
    }

async def act_on_feedback(request: LLMFeedbackInput) -> LLMFeedbackOutput:
    system_prompt = Path("src/prompts/calibrator_system_prompt.jinja").read_text()
    response = client.chat.completions.create(
        model = GPT_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt + str(request.rating) +
                           request.feedback + request.base_system_prompt
            }
        ]
    )
    return LLMFeedbackOutput(
        calibrated_system_prompt=response.choices[0].message.content
    )