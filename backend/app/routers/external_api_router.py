from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Agent, Workflow
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/v1/external", tags=["External Developer REST APIs"])

@router.get("/agents")
def get_external_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).filter(Agent.is_active == True).all()
    return [{"id": a.id, "name": a.name, "code": a.code, "role": a.role_description} for a in agents]

@router.post("/chat")
def external_chat_invoke(
    payload: Dict[str, Any], 
    db: Session = Depends(get_db), 
    x_api_key: Optional[str] = Header(None)
):
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query field is required")

    agent_code = payload.get("agent_code")
    active_agents = db.query(Agent).filter(Agent.is_active == True).all()

    if agent_code:
        target_agent = db.query(Agent).filter(Agent.code == agent_code, Agent.is_active == True).first()
    else:
        target_agent = LLMService.route_intent(query, active_agents)

    if not target_agent and active_agents:
        target_agent = active_agents[0]

    rag_snippets = RAGService.query_knowledge_base(db, query, top_k=2)
    response_data = LLMService.generate_agent_response(db, query, target_agent, rag_snippets=rag_snippets)

    return {
        "status": "success",
        "query": query,
        "assigned_agent": target_agent.name if target_agent else "System",
        "agent_code": target_agent.code if target_agent else "system",
        "response": response_data["content"],
        "citations": response_data.get("citations", []),
        "duration_ms": response_data["duration_ms"]
    }

@router.post("/workflows/trigger")
def external_workflow_trigger(
    payload: Dict[str, Any], 
    db: Session = Depends(get_db),
    x_api_key: Optional[str] = Header(None)
):
    workflow_id = payload.get("workflow_id")
    if not workflow_id:
        raise HTTPException(status_code=400, detail="workflow_id field is required")

    try:
        run = WorkflowService.execute_workflow(db, workflow_id, payload.get("input", {}))
        return {
            "status": "success",
            "run_id": run.id,
            "workflow_id": run.workflow_id,
            "execution_status": run.status,
            "duration_ms": run.duration_ms,
            "output_log": run.output_log
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
