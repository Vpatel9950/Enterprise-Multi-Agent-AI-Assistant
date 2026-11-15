from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.db.mongo import MongoDBManager, serialize_doc, to_object_id
from app.routers.chat_router import get_current_user_context

router = APIRouter(prefix="/agents", tags=["AI Agents Management"])

class AgentUpdateDto(BaseModel):
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    is_active: Optional[bool] = None

@router.get("")
def list_agents(user_ctx: Dict[str, Any] = Depends(get_current_user_context)):
    agents = list(MongoDBManager.ai_agents().find({}).sort("createdAt", 1))
    return [serialize_doc(a) for a in agents]

@router.put("/{agent_code}")
def update_agent(
    agent_code: str,
    dto: AgentUpdateDto,
    user_ctx: Dict[str, Any] = Depends(get_current_user_context)
):
    if user_ctx["user_role"] not in ["ORG_ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Modifying AI Agent configurations requires Administrator privileges")

    update_fields = {}
    if dto.system_prompt is not None:
        update_fields["systemPrompt"] = dto.system_prompt
    if dto.temperature is not None:
        update_fields["temperature"] = float(dto.temperature)
    if dto.is_active is not None:
        update_fields["isActive"] = dto.is_active

    if not update_fields:
        return {"status": "no change"}

    res = MongoDBManager.ai_agents().update_one(
        {"code": agent_code},
        {"$set": update_fields}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_code}' not found")

    updated = MongoDBManager.ai_agents().find_one({"code": agent_code})
    return serialize_doc(updated)

@router.get("/logs")
def list_execution_logs(
    limit: int = 20,
    user_ctx: Dict[str, Any] = Depends(get_current_user_context)
):
    org_oid = to_object_id(user_ctx["organization_id"])
    logs = list(MongoDBManager.agent_execution_logs().find(
        {"organizationId": org_oid}
    ).sort("createdAt", -1).limit(limit))
    return [serialize_doc(l) for l in logs]
