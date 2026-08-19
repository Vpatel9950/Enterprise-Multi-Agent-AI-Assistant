from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, Token, UserResponse
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_pwd = hash_password(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_pwd,
        full_name=user_in.full_name,
        role=user_in.role or "user",
        department=user_in.department or "General"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return Token(access_token=access_token, token_type="bearer", user=UserResponse.from_orm(user))

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return Token(access_token=access_token, token_type="bearer", user=UserResponse.from_orm(user))

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)
