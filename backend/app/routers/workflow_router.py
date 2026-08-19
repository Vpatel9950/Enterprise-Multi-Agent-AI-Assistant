import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Workflow, WorkflowRun, User
from app.schemas import WorkflowCreate, WorkflowResponse, WorkflowRunResponse
from app.auth import get_current_user, require_admin
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["Workflow Automations"])

@router.get("", response_model=List[WorkflowResponse])
def list_workflows(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Workflow).order_by(Workflow.created_at.desc()).all()

@router.post("", response_model=WorkflowResponse)
def create_workflow(wf_in: WorkflowCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    wf = Workflow(
        name=wf_in.name,
        description=wf_in.description,
        trigger_type=wf_in.trigger_type,
        target_agent_id=wf_in.target_agent_id,
        config_json=wf_in.config_json or "{}",
        created_by_id=current_user.id,
        status="active"
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return wf

@router.post("/{workflow_id}/trigger", response_model=WorkflowRunResponse)
def trigger_workflow_manual(
    workflow_id: int, 
    payload: Dict[str, Any] = {}, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        run = WorkflowService.execute_workflow(db, workflow_id, payload or {"triggered_by": current_user.email})
        return run
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{workflow_id}/runs", response_model=List[WorkflowRunResponse])
def get_workflow_runs(workflow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    runs = db.query(WorkflowRun).filter(WorkflowRun.workflow_id == workflow_id).order_by(WorkflowRun.executed_at.desc()).all()
    return runs
