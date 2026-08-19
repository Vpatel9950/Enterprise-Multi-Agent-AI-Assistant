import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Agent, User
from app.schemas import AgentCreate, AgentUpdate, AgentResponse
from app.auth import get_current_user, require_admin

router = APIRouter(prefix="/agents", tags=["AI Agents"])

@router.get("", response_model=List[AgentResponse])
def list_agents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agents = db.query(Agent).all()
    for a in agents:
        if isinstance(a.tools_enabled, str):
            try:
                a.tools_enabled = json.loads(a.tools_enabled)
            except Exception:
                a.tools_enabled = []
    return agents

@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if isinstance(agent.tools_enabled, str):
        try:
            agent.tools_enabled = json.loads(agent.tools_enabled)
        except Exception:
            agent.tools_enabled = []
    return agent

@router.post("", response_model=AgentResponse)
def create_agent(agent_in: AgentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    existing = db.query(Agent).filter(Agent.code == agent_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Agent code already exists")

    tools_json = json.dumps(agent_in.tools_enabled) if agent_in.tools_enabled else "[]"
    agent = Agent(
        name=agent_in.name,
        code=agent_in.code,
        role_description=agent_in.role_description,
        system_prompt=agent_in.system_prompt,
        model_name=agent_in.model_name or "gpt-4o-mini",
        temperature=agent_in.temperature or 0.7,
        tools_enabled=tools_json,
        is_active=agent_in.is_active if agent_in.is_active is not None else True
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    if isinstance(agent.tools_enabled, str):
        agent.tools_enabled = json.loads(agent.tools_enabled)
    return agent

@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: int, agent_in: AgentUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if agent_in.name is not None:
        agent.name = agent_in.name
    if agent_in.role_description is not None:
        agent.role_description = agent_in.role_description
    if agent_in.system_prompt is not None:
        agent.system_prompt = agent_in.system_prompt
    if agent_in.model_name is not None:
        agent.model_name = agent_in.model_name
    if agent_in.temperature is not None:
        agent.temperature = agent_in.temperature
    if agent_in.tools_enabled is not None:
        agent.tools_enabled = json.dumps(agent_in.tools_enabled)
    if agent_in.is_active is not None:
        agent.is_active = agent_in.is_active

    db.commit()
    db.refresh(agent)
    if isinstance(agent.tools_enabled, str):
        agent.tools_enabled = json.loads(agent.tools_enabled)
    return agent
