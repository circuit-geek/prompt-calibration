from fastapi import APIRouter, Depends

from src.entities.schema import (
    NewChatSession, UserChatRequest,
    ChatResponse, ChatFeedback,
    FeedbackAction, LLMFeedbackInput
)
from src.services.chat_service import (
    create_new_session, generate_response,
    get_session_history, create_chat_with_response,
    update_chat_feedback, act_on_feedback, get_chat_history_in_session
)
from src.utils.auth_utils import get_current_user

chat_router = APIRouter(prefix="/chat", tags=["Chat"])

@chat_router.post("/session/create")
async def create_session_route(new_chat: NewChatSession, user=Depends(get_current_user)):
    new_chat.user_id = user.id
    session = await create_new_session(new_chat)
    return {"session_id": str(session.id), "session_name": session.session_name}

@chat_router.post("/session/{session_id}/send")
async def send_message_route(session_id: str,
                             request: UserChatRequest, user=Depends(get_current_user)):

    assistant_message = await generate_response(request)
    saved_chat = await create_chat_with_response(
        session_id=session_id,
        user_message=request.user_prompt,
        assistant_message=assistant_message,
        model_used=request.model
    )

    return ChatResponse(
        message=assistant_message,
        chat_id=str(saved_chat.id)
    )


@chat_router.post("/{chat_id}/feedback")
async def submit_feedback_route(chat_id: str, feedback: ChatFeedback,
                                user=Depends(get_current_user)):

    result = await update_chat_feedback(chat_id, feedback, feedback.action)
    if feedback.action == FeedbackAction.CALIBRATE_PROMPT:
        feedback_input = LLMFeedbackInput(
            rating=feedback.rating,
            feedback=feedback.feedback,
            base_system_prompt=feedback.base_system_prompt
        )

        calibrated = await act_on_feedback(feedback_input)
        result["calibrated_prompt"] = calibrated.calibrated_system_prompt
    return result

@chat_router.get("/session/history")
async def get_history_route(user=Depends(get_current_user)):
    history = await get_session_history(user_id=user.id)
    return {"history": history}

@chat_router.get("/session/{session_id}/chat-history")
async def get_history_route(session_id: str, user=Depends(get_current_user)):
    history = await get_chat_history_in_session(session_id=session_id)
    return {"history": history}

