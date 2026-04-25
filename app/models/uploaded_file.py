from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)          # UUID-prefixed stored name
    original_name = Column(String, nullable=False)     # Original user filename
    file_path = Column(String, nullable=False)         # Absolute path on disk
    status = Column(String, default="PENDING")         # PENDING | PROCESSING | COMPLETED | FAILED
    error_message = Column(Text, nullable=True)        # Populated on FAILED
    created_at = Column(DateTime, default=datetime.utcnow)
