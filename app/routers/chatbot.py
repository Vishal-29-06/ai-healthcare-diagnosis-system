from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.chatbot import ChatRequest, ChatResponse
from app.core.dependencies import get_current_user
from app.core.chatbot_engine import get_bot_reply

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


@router.post("/ask", response_model=ChatResponse)
def ask_chatbot(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    return get_bot_reply(payload.message)
