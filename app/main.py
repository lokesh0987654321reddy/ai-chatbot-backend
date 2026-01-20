
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.api import model as models

from app.db.session import engine
from app.db.base import Base

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


@app.get("/")
async def root():
    return {"message": "AI Chatbot Backend is running"}

app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(models.router)

