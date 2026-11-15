import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from app.models.schemas import ApprovalDecisionRequest
from app.db.mongo import MongoDBManager, to_object_id, serialize_doc
from app.routers.chat_router import get_current_user_context
from app.agents.action_agent import ActionAgent
from app.models.state import AgentState

router = APIRouter(prefix="/approvals", tags=["Human-in-the-Loop (HITL) Approvals"])

@router.get("")
def list_pending_approvals(user_ctx: Dict[str, Any] = Depends(get_current_user_context)):
    org_oid = to_object_id(user_ctx["organization_id"])
    query = {"organizationId": org_oid}

    # If regular employee, only show their own requests
    if user_ctx["user_role"] == "EMPLOYEE":
        query["requestedBy"] = to_object_id(user_ctx["user_id"])

    approvals = list(MongoDBManager.approval_requests().find(query).sort("createdAt", -1))
    return [serialize_doc(a) for a in approvals]

@router.post("/{approval_id}/decision")
def submit_approval_decision(
    approval_id: str,
    req: ApprovalDecisionRequest,
    user_ctx: Dict[str, Any] = Depends(get_current_user_context)
):
    if user_ctx["user_role"] not in ["MANAGER", "ORG_ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(
            status_code=403,
            detail="Action approval or rejection requires Manager or Administrator privileges"
        )

    appr_oid = to_object_id(approval_id)
    approval_doc = MongoDBManager.approval_requests().find_one({"_id": appr_oid})
    if not approval_doc:
        raise HTTPException(status_code=404, detail="Approval Request not found")

    if approval_doc["status"] != "PENDING":
        raise HTTPException(status_code=400, detail=f"Request is already resolved as '{approval_doc['status']}'")

    now = datetime.datetime.utcnow()

    # Update approval request status in MongoDB
    MongoDBManager.approval_requests().update_one(
        {"_id": appr_oid},
        {
            "$set": {
                "status": req.decision,
                "reviewedBy": to_object_id(user_ctx["user_id"]),
                "reviewedByName": user_ctx["user_name"],
                "reviewNotes": req.review_notes or f"Marked as {req.decision} by {user_ctx['user_name']}",
                "reviewedAt": now
            }
        }
    )

    execution_result = None

    if req.decision == "APPROVED":
        # Resume the Action Agent execution
        resume_state: AgentState = {
            "conversation_id": str(approval_doc.get("conversationId", "")),
            "user_id": str(approval_doc["requestedBy"]),
            "user_name": approval_doc.get("requestedByName", "Employee"),
            "user_email": "caller@acme.com",
            "user_role": user_ctx["user_role"],
            "organization_id": str(approval_doc["organizationId"]),
            "department_id": None,
            "query": f"Approved {approval_doc['actionType']}",
            "intent": "action_execution",
            "execution_plan": ["action_agent"],
            "current_step": 1,
            "selected_agent": "action_agent",
            "agent_traces": [],
            "rag_citations": [],
            "rag_context_text": "",
            "intermediate_results": {},
            "approval_required": False,
            "approval_id": approval_id,
            "approval_status": "APPROVED",
            "action_type": approval_doc["actionType"],
            "action_payload": approval_doc["actionPayload"],
            "final_response": "",
            "tokens_used": 0,
            "duration_ms": 0,
            "error": None
        }

        executed_state = ActionAgent.execute(resume_state)
        execution_result = executed_state["intermediate_results"].get("action_agent")

    return {
        "approval_id": approval_id,
        "decision": req.decision,
        "reviewed_by": user_ctx["user_name"],
        "reviewed_at": now.isoformat(),
        "execution_result": execution_result
    }
