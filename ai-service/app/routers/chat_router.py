import json
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest, ChatResponse, CitationDto, AgentTraceDto
from app.models.state import AgentState
from app.db.mongo import MongoDBManager, to_object_id, serialize_doc
from app.agents.orchestrator import OrchestratorAgent

router = APIRouter(prefix="/chat", tags=["Multi-Agent Chat & Orchestration"])

def get_current_user_context(
    x_user_id: Optional[str] = Header("6732a1000000000000000004"),
    x_user_role: Optional[str] = Header("EMPLOYEE"),
    x_user_name: Optional[str] = Header("Alex Rivera"),
    x_user_email: Optional[str] = Header("alex.rivera@acme.com"),
    x_organization_id: Optional[str] = Header(None)
) -> Dict[str, Any]:
    # Look up user or organization from MongoDB if needed
    if not x_organization_id:
        user_doc = MongoDBManager.users().find_one({"email": x_user_email})
        if user_doc:
            x_organization_id = str(user_doc["organizationId"])
            x_user_id = str(user_doc["_id"])
            x_user_role = user_doc.get("role", "EMPLOYEE")
            x_user_name = user_doc.get("fullName", "User")
        else:
            org_doc = MongoDBManager.organizations().find_one({"code": "acme-corp"})
            x_organization_id = str(org_doc["_id"]) if org_doc else "6732a1000000000000000001"

    return {
        "user_id": x_user_id,
        "user_role": x_user_role,
        "user_name": x_user_name,
        "user_email": x_user_email,
        "organization_id": x_organization_id
    }

@router.post("", response_model=ChatResponse)
def chat_execute(
    req: ChatRequest,
    user_ctx: Dict[str, Any] = Depends(get_current_user_context)
):
    org_id = req.organization_id or user_ctx["organization_id"]

    initial_state: AgentState = {
        "conversation_id": req.conversation_id or "",
        "user_id": user_ctx["user_id"],
        "user_name": user_ctx["user_name"],
        "user_email": user_ctx["user_email"],
        "user_role": user_ctx["user_role"],
        "organization_id": org_id,
        "department_id": None,
        "query": req.query,
        "intent": "",
        "execution_plan": [],
        "current_step": 0,
        "selected_agent": req.preferred_agent_code or "orchestrator",
        "agent_traces": [],
        "rag_citations": [],
        "rag_context_text": "",
        "intermediate_results": {},
        "approval_required": False,
        "approval_id": None,
        "approval_status": None,
        "action_type": None,
        "action_payload": None,
        "final_response": "",
        "tokens_used": 0,
        "duration_ms": 0,
        "error": None
    }

    result_state = OrchestratorAgent.execute_pipeline(initial_state)

    citations_dto = [CitationDto(**c) for c in result_state.get("rag_citations", [])]
    traces_dto = [AgentTraceDto(**t) for t in result_state.get("agent_traces", [])]

    return ChatResponse(
        conversation_id=result_state["conversation_id"],
        assigned_agent="Centralized Orchestrator Agent",
        agent_code=result_state.get("selected_agent", "orchestrator"),
        response=result_state["final_response"],
        citations=citations_dto,
        agent_traces=traces_dto,
        approval_required=result_state.get("approval_required", False),
        approval_id=result_state.get("approval_id"),
        duration_ms=result_state["duration_ms"],
        tokens_used=result_state["tokens_used"]
    )

@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    user_ctx: Dict[str, Any] = Depends(get_current_user_context)
):
    async def event_generator():
        org_id = req.organization_id or user_ctx["organization_id"]

        # Yield event 1: Planning
        step_data = json.dumps({"agent": "Orchestrator Agent", "status": "Analyzing request intent and planning DAG execution..."})
        yield f"event: step\ndata: {step_data}\n\n"
        await asyncio.sleep(0.1)

        # Yield event 2: Execution
        initial_state: AgentState = {
            "conversation_id": req.conversation_id or "",
            "user_id": user_ctx["user_id"],
            "user_name": user_ctx["user_name"],
            "user_email": user_ctx["user_email"],
            "user_role": user_ctx["user_role"],
            "organization_id": org_id,
            "department_id": None,
            "query": req.query,
            "intent": "",
            "execution_plan": [],
            "current_step": 0,
            "selected_agent": req.preferred_agent_code or "orchestrator",
            "agent_traces": [],
            "rag_citations": [],
            "rag_context_text": "",
            "intermediate_results": {},
            "approval_required": False,
            "approval_id": None,
            "approval_status": None,
            "action_type": None,
            "action_payload": None,
            "final_response": "",
            "tokens_used": 0,
            "duration_ms": 0,
            "error": None
        }

        result = OrchestratorAgent.execute_pipeline(initial_state)

        for trace in result["agent_traces"]:
            trace_data = json.dumps(trace)
            yield f"event: agent_trace\ndata: {trace_data}\n\n"
            await asyncio.sleep(0.05)

        # Yield tokens chunk by chunk
        words = result["final_response"].split(" ")
        for i in range(0, len(words), 4):
            chunk = " ".join(words[i:i+4]) + " "
            token_data = json.dumps({"token": chunk})
            yield f"event: token\ndata: {token_data}\n\n"
            await asyncio.sleep(0.02)

        # Yield completion
        complete_data = json.dumps({
            "conversation_id": result["conversation_id"],
            "citations": result.get("rag_citations", []),
            "approval_required": result.get("approval_required", False),
            "approval_id": result.get("approval_id"),
            "duration_ms": result["duration_ms"]
        })
        yield f"event: complete\ndata: {complete_data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/conversations")
def list_conversations(user_ctx: Dict[str, Any] = Depends(get_current_user_context)):
    org_oid = to_object_id(user_ctx["organization_id"])
    user_oid = to_object_id(user_ctx["user_id"])
    convs = list(MongoDBManager.conversations().find(
        {"organizationId": org_oid, "userId": user_oid, "status": "ACTIVE"}
    ).sort("updatedAt", -1))
    return [serialize_doc(c) for c in convs]

@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(conversation_id: str, user_ctx: Dict[str, Any] = Depends(get_current_user_context)):
    conv_oid = to_object_id(conversation_id)
    messages = list(MongoDBManager.messages().find(
        {"conversationId": conv_oid}
    ).sort("createdAt", 1))
    return [serialize_doc(m) for m in messages]
