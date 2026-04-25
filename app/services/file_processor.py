import uuid
import traceback
from pathlib import Path

from app.db.session import SessionLocal
from app.models.uploaded_file import UploadedFile
from app.services.embedding import get_embedding
from app.utils.chunker import chunk_text
from app.db.chroma import client, documents_collection


def _extract_text(file_path: str, original_name: str) -> str:
    """Extract plain text from .txt or .pdf files."""
    ext = Path(original_name).suffix.lower()

    if ext == ".txt":
        return Path(file_path).read_text(encoding="utf-8", errors="ignore")

    elif ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            raise RuntimeError("pypdf is not installed. Run: pip install pypdf")

        reader = PdfReader(file_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    else:
        raise ValueError(f"Unsupported file type: {ext}")


def process_file(file_id: int):
    """
    Background worker called after a file is uploaded.
    Lifecycle: PENDING → PROCESSING → COMPLETED | FAILED
    """
    db = SessionLocal()
    try:
        record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
        if not record:
            return

        # --- Step 1: Mark as PROCESSING ---
        record.status = "PROCESSING"
        db.commit()

        # --- Step 2: Extract text ---
        text = _extract_text(record.file_path, record.original_name)

        if not text.strip():
            raise ValueError("File appears to be empty or has no extractable text.")

        # --- Step 3: Chunk the text ---
        chunks = chunk_text(text)

        # --- Step 4: Embed and store each chunk ---
        for chunk in chunks:
            if not chunk.strip():
                continue
            embedding = get_embedding(chunk)
            documents_collection.add(
                ids=[str(uuid.uuid4())],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{
                    "file_id": str(file_id),
                    "original_name": record.original_name,
                }]
            )

        # --- Step 5: Mark as COMPLETED ---
        record.status = "COMPLETED"
        db.commit()

    except Exception as exc:
        tb = traceback.format_exc()
        print(f"[file_processor] ERROR processing file {file_id}:\n{tb}")
        try:
            record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
            if record:
                record.status = "FAILED"
                record.error_message = str(exc)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
