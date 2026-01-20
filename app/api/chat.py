from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.services.chatbot import stream_bot_response,stream_openrouter_response, get_model_config, get_chat_history, build_ollama_messages
from app.core.auth import get_current_user  # JWT dependency
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.chat import ChatSession, ChatRequest
from app.models.message import ChatMessage


router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/chat/stream")
async def chat_stream(message: str, chatId: int, db: Session = Depends(get_db)):
    history = get_chat_history(chatId, db)
    ollama_messages = build_ollama_messages(history, message, personality="comedy")
    def event_generator():
        for token in stream_openrouter_response(ollama_messages):
            yield f"data: {token}\n\n"

        # ✅ IMPORTANT: signal stream completion
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

@router.get("/chat/stream/openrouter")
async def chat_stream(message: str, chatId: int, model: str, db: Session = Depends(get_db)):
    history = get_chat_history(chatId, db)
    messages = build_ollama_messages(history, message, personality="comedy")

    model_config = get_model_config(model)


    def event_generator():
        for token in stream_openrouter_response(messages, model_config=model_config):
            if token.startswith("[ERROR]"):
                yield f"data: {token}\n\n"
                break
            yield f"data: {token}\n\n"
        
        # ✅ IMPORTANT: signal stream completion
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.post("/chat/new")
def create_chat(db: Session = Depends(get_db), user=Depends(get_current_user)):
    chat = ChatSession(user_id=user.id)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

@router.get("/chat/history")
def get_history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(ChatSession)\
        .filter(ChatSession.user_id == user.id)\
        .order_by(ChatSession.created_at.desc())\
        .all()


@router.get("/chat/{chat_id}/messages")
def get_messages(chat_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(ChatMessage)\
        .filter(ChatMessage.chat_id == chat_id)\
        .order_by(ChatMessage.created_at)\
        .all()


@router.post("/chat/{chat_id}/save")
def save_chat_messages(
    chat_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    user_text = payload.get("user")
    bot_text = payload.get("bot")

    if not user_text or not bot_text:
        raise HTTPException(status_code=400, detail="Invalid payload")

    # Save user message
    db.add(ChatMessage(
        chat_id=chat_id,
        sender="user",
        content=user_text
    ))

    # Save bot message
    db.add(ChatMessage(
        chat_id=chat_id,
        sender="bot",
        content=bot_text
    ))

    db.commit()

    return {"status": "saved"}

@router.put("/chats/{chat_id}/title")
def update_chat_title(chat_id: int, title: str, db: Session = Depends(get_db)):
    chat = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    chat.title = title
    db.commit()
    return {"title": title}

