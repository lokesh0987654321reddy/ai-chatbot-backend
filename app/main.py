
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.api import model as models
from app.api.upload import router as upload_router

# Import models so SQLAlchemy creates their tables on startup
from app.models import uploaded_file  # noqa: F401

from app.db.session import engine
from app.db.base import Base
from app.services.resume_indexer import load_resume_text, index_resume
from app.services.vector_store import collection_has_data

Base.metadata.create_all(bind=engine)



app = FastAPI()

# Allow all origins for development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,   # 🔥 THIS IS CRITICAL
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    if not collection_has_data():
        resume_text = load_resume_text()
        index_resume(resume_text)

    print("✅ Resume indexed successfully")


@app.get("/")
async def root():
    return {"message": "AI Chatbot Backend is running"}

app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(models.router)
app.include_router(upload_router)

