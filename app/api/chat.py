from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services.chatbot import get_bot_response

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    bot_response = get_bot_response(request.message)
    return ChatResponse(response=bot_response)
