from app.db.chroma import client, resume_collection
from app.services.embedding import get_embedding
from app.utils.chunker import chunk_text
import uuid
from pathlib import Path

RESUME_PATH = Path("data/resumes/resume.txt")

def load_resume_text():
    return RESUME_PATH.read_text(encoding="utf-8")

def index_resume(resume_text: str):
    chunks = chunk_text(resume_text)

    for chunk in chunks:
        print(f"Indexing chunk: {chunk[:60]}...")
        print("resume_collection:", resume_collection)
        embedding = get_embedding(chunk)
        resume_collection.add(
            ids=[str(uuid.uuid4())],
            documents=[chunk],
            embeddings=[embedding]
        )
        print("Number of documents:", resume_collection.count())
