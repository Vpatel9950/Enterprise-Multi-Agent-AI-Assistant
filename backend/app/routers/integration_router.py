from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Integration, User
from app.schemas import IntegrationCreate, IntegrationResponse
from app.auth import get_current_user, require_admin
from app.services.integration_service import IntegrationService

router = APIRouter(prefix="/integrations", tags=["External Enterprise Integrations"])

@router.get("", response_model=List[IntegrationResponse])
def list_integrations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Integration).all()

@router.post("", response_model=IntegrationResponse)
def create_integration(int_in: IntegrationCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    integration = Integration(
        name=int_in.name,
        service_type=int_in.service_type,
        webhook_url=int_in.webhook_url,
        config_json=int_in.config_json or "{}",
        status="connected"
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration

@router.post("/{integration_id}/test")
def test_integration(integration_id: int, payload: Dict[str, Any] = {}, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    result = IntegrationService.trigger_integration(
        db,
        service_type=integration.service_type,
        action="manual_test",
        payload=payload or {"test": True, "sender": current_user.email}
    )
    return result
