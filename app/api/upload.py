import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.auth import get_current_user
from app.db.session import SessionLocal
from app.models.uploaded_file import UploadedFile
from app.schemas.upload import UploadedFileOut
from app.services.file_processor import process_file


router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_EXTENSIONS = {".pdf", ".txt"}
STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=UploadedFileOut)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Upload a PDF or TXT file.
    - Saves to local storage/ directory with a UUID prefix
    - Creates a DB record with status=PENDING
    - Kicks off background processing (embedding + ChromaDB indexing)
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Save file to storage/
    stored_name = f"{uuid.uuid4()}{ext}"
    file_path = STORAGE_DIR / stored_name

    contents = await file.read()
    file_path.write_bytes(contents)

    # Create DB record
    record = UploadedFile(
        filename=stored_name,
        original_name=file.filename,
        file_path=str(file_path.resolve()),
        status="PENDING",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Enqueue background processing
    background_tasks.add_task(process_file, record.id)

    return record


@router.get("", response_model=List[UploadedFileOut])
def list_uploads(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Return all uploaded files, newest first."""
    return (
        db.query(UploadedFile)
        .order_by(UploadedFile.created_at.desc())
        .all()
    )
