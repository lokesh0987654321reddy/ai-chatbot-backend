from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chat_sessions.id"))
    sender = Column(String)  # "user" or "bot"
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    chat = relationship("ChatSession", back_populates="messages")
