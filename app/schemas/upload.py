from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UploadedFileOut(BaseModel):
    id: int
    filename: str
    original_name: str
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
