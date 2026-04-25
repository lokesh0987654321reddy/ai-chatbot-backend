# app/db/chroma.py
from pathlib import Path
import chromadb

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BASE_DIR / "chroma"
CHROMA_DIR.mkdir(exist_ok=True)

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

resume_collection = client.get_or_create_collection(name="resume")
documents_collection = client.get_or_create_collection(name="documents")
