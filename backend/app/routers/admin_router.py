from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserResponse
from app.auth import require_admin
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/admin", tags=["Admin Portal & Analytics"])

@router.get("/analytics")
def get_analytics_dashboard(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return AnalyticsService.get_overview_metrics(db)

@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()

@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(user_id: int, role: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'admin' or 'user'.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    db.commit()
    db.refresh(user)
    return user

@router.put("/users/{user_id}/status", response_model=UserResponse)
def toggle_user_status(user_id: int, is_active: bool, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user
