from fastapi import APIRouter, Depends
from src.utils.auth_utils import get_current_user
from src.entities.schema import (
    NewChatSession, UserChatRequest,
    ChatObject, ChatFeedback,
    LLMFeedbackInput
)
from src.services.chat_service import (
    create_new_session, generate_response,
    add_chat_to_session, get_session_history,
    give_response_feedback
)

chat_router = APIRouter(prefix="/chat", tags=["Chat"])

@chat_router.post("/session/create")
async def create_session_route(new_chat: NewChatSession, user=Depends(get_current_user)):
    session = await create_new_session(new_chat)
    return {"session_id": str(session.id), "session_name": session.session_name}


@chat_router.get("/session/{session_id}/history")
async def get_history_route(session_id: str, user=Depends(get_current_user)):
    history = await get_session_history(session_id)
    return {"session_id": session_id, "history": [h.message for h in history]}


@chat_router.post("/session/{session_id}/send")
async def send_message_route(session_id: str,
                             request: UserChatRequest, user=Depends(get_current_user)):
    user_chat = ChatObject(
        session_id=session_id,
        message=request.user_prompt,
        model_used=request.model,
        rating=None,
        feedback=None,
        action=None,
    )
    await add_chat_to_session(user_chat)
    llm_response = await generate_response(request)
    assistant_chat = ChatObject(
        session_id=session_id,
        message=llm_response.message,
        model_used=request.model,
        rating=None,
        feedback=None,
        action=None,
    )
    saved_chat = await add_chat_to_session(assistant_chat)

    return {
        "response": llm_response,
        "assistant_chat_id": str(saved_chat.id)
    }



@chat_router.post("/{chat_id}/feedback")
async def feedback_route(chat_id: str, feedback: ChatFeedback,
                         request: LLMFeedbackInput, user=Depends(get_current_user)):

    result = await give_response_feedback(
        chat_id=chat_id,
        feedback=feedback,
        action=feedback.action,
        request=request,
    )
    return result


