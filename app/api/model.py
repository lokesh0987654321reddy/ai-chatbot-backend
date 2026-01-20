from fastapi import APIRouter
from app.core.models_registry import MODELS

router = APIRouter(prefix="/models", tags=["Models"])


@router.get("")
def get_models():
    return MODELS
