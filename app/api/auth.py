from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# User Registration
# -----------------------------
@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return JWT token immediately after registration
    access_token = create_access_token({"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# -----------------------------
# User Login
# -----------------------------
@router.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": db_user.email})
      # 🔐 Set HttpOnly cookie
    response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    secure=False,        # True only in HTTPS
    samesite="lax",
    max_age=60 * 60,
    path="/",            # 🔥 IMPORTANT
    )  
    return {"message": "Login successful"}


@router.get("/me")
def get_current_user_info(current_user: str = Depends(get_current_user)):
    return {"email": current_user}
