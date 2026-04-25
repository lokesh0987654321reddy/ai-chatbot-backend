from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.services.chatbot import stream_bot_response, stream_openrouter_response, get_model_config, get_chat_history
from app.core.auth import get_current_user
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.chat import ChatSession
from app.models.message import ChatMessage
from app.services.retriever import retrieve_context
from app.services.prompt_builder import build_rag_prompt, build_messages

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _prep_rag_messages(message: str, history: list, useRag: bool):
    """Internal helper to build messages based on RAG status."""
    if useRag:
        # Search the user-uploaded 'documents' collection
        context = retrieve_context(message, collection_type="documents")
        return build_rag_prompt(context, history, message, personality="default")
    else:
        return build_messages(history, message, personality="default")

@router.get("/chat/stream")
async def chat_stream(
    message: str, 
    chatId: int, 
    useRag: bool = False, 
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    history = get_chat_history(chatId, db)
    messages = _prep_rag_messages(message, history, useRag)
    
    def event_generator():
        for token in stream_bot_response(messages):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Credentials": "true",
        },
    )

@router.get("/chat/stream/openrouter")
async def chat_stream_openrouter(
    message: str, 
    chatId: int, 
    model: str, 
    useRag: bool = False, 
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    history = get_chat_history(chatId, db)  
    model_config = get_model_config(model)
    messages = _prep_rag_messages(message, history, useRag)

    def event_generator():
        for token in stream_openrouter_response(messages, model_config=model_config):
            if token.startswith("[ERROR]"):
                yield f"data: {token}\n\n"
                break
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Credentials": "true",
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
        return {"error": "Invalid payload"}, 400

    db.add(ChatMessage(chat_id=chat_id, sender="user", content=user_text))
    db.add(ChatMessage(chat_id=chat_id, sender="bot", content=bot_text))
    db.commit()
    return {"status": "saved"}

@router.put("/chats/{chat_id}/title")
def update_chat_title(chat_id: int, title: str, db: Session = Depends(get_db)):
    chat = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    if chat:
        chat.title = title
        db.commit()
    return {"title": title}
