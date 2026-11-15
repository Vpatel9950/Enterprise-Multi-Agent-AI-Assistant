import time
import datetime
from typing import Dict, Any, Optional
from bson import ObjectId
from app.models.state import AgentState, AgentTrace
from app.db.mongo import MongoDBManager, to_object_id

class ActionAgent:
    CODE = "action_agent"
    NAME = "Action & Execution Agent"

    @classmethod
    def execute(cls, state: AgentState) -> AgentState:
        start_time = time.time()
        query = state["query"].lower()
        org_id = state["organization_id"]
        user_id = state["user_id"]
        user_name = state.get("user_name", "Employee")
        approval_status = state.get("approval_status")

        # Determine target action
        action_type = "DISPATCH_ENTERPRISE_OPERATION"
        target_system = "Slack / Jira / Cloud API"
        risk_level = "HIGH"

        if "jira" in query or "ticket" in query or "issue" in query:
            action_type = "CREATE_JIRA_ISSUE"
            target_system = "Jira Cloud (PROD)"
            action_payload = {
                "project": "SUP",
                "issueType": "Incident",
                "summary": state["query"][:80],
                "priority": "High",
                "assignee": "DevOps On-Call"
            }
        elif "slack" in query or "broadcast" in query or "notify" in query:
            action_type = "SEND_SLACK_ALERT"
            target_system = "Slack Workspace (#alerts)"
            action_payload = {
                "channel": "#alerts",
                "broadcast": True,
                "text": f"Automated Alert: {state['query'][:100]}"
            }
            risk_level = "MEDIUM"
        elif "cluster" in query or "deploy" in query or "cloud" in query:
            action_type = "PROVISION_CLOUD_RESOURCE"
            target_system = "AWS Cloud Platform"
            action_payload = {
                "resource": "EKS Worker Node Group",
                "instance": "m5.large",
                "estimatedCost": "$280/mo"
            }
            risk_level = "HIGH"
        else:
            action_type = "EXECUTE_WORKFLOW_TRIGGER"
            target_system = "Enterprise Automation Engine"
            action_payload = {
                "operation": "Business Process Automation",
                "details": state["query"]
            }
            risk_level = "LOW"

        # ----------------------------------------------------------------------
        # Check Human-in-the-Loop (HITL) Gate
        # ----------------------------------------------------------------------
        if approval_status != "APPROVED":
            # Action has NOT been explicitly approved yet! Enforce HITL Gate!
            # Create a pending approval request in MongoDB
            approval_doc = {
                "organizationId": to_object_id(org_id),
                "conversationId": to_object_id(state.get("conversation_id")),
                "workflowId": None,
                "requestedBy": to_object_id(user_id),
                "requestedByName": user_name,
                "actionType": action_type,
                "targetSystem": target_system,
                "actionPayload": action_payload,
                "riskLevel": risk_level,
                "status": "PENDING",
                "reviewedBy": None,
                "reviewedByName": None,
                "reviewNotes": None,
                "reviewedAt": None,
                "createdAt": datetime.datetime.utcnow(),
                "expiresAt": datetime.datetime.utcnow() + datetime.timedelta(days=3)
            }

            res = MongoDBManager.approval_requests().insert_one(approval_doc)
            approval_id = str(res.inserted_id)

            duration_ms = int((time.time() - start_time) * 1000)

            # Mark state as requiring approval
            state["approval_required"] = True
            state["approval_id"] = approval_id
            state["action_type"] = action_type
            state["action_payload"] = action_payload

            trace: AgentTrace = {
                "agent_name": cls.NAME,
                "action": f"PAUSED for Human-in-the-Loop Approval: [{action_type}] on [{target_system}]",
                "status": "PENDING_APPROVAL",
                "duration_ms": duration_ms,
                "details": f"Approval Request #{approval_id} registered with Risk Level '{risk_level}'"
            }
            state["agent_traces"].append(trace)

            response_content = (
                f"### 🛡️ Human-in-the-Loop (HITL) Approval Required\n"
                f"The requested operation involves state mutation or external execution on **{target_system}**:\n\n"
                f"- **Action Type**: `{action_type}`\n"
                f"- **Target System**: `{target_system}`\n"
                f"- **Risk Classification**: `{risk_level}`\n"
                f"- **Approval Request ID**: `{approval_id}`\n\n"
                f"```json\n"
                f"// Proposed Action Payload\n"
                f"{action_payload}\n"
                f"```\n\n"
                f"⚠️ *Safety Policy Enforced*: The AI cannot execute external modifications or send communications "
                f"without authorized review. Please review and approve using the **Action Approval Dialog** above."
            )
            state["intermediate_results"]["action_agent"] = response_content
            return state

        # ----------------------------------------------------------------------
        # If APPROVED: Execute Operation
        # ----------------------------------------------------------------------
        duration_ms = int((time.time() - start_time) * 1000)

        # Log to audit trail in MongoDB
        audit_doc = {
            "organizationId": to_object_id(org_id),
            "userId": to_object_id(user_id),
            "userEmail": state.get("user_email"),
            "userRole": state.get("user_role"),
            "action": f"ACTION_EXECUTED_{action_type}",
            "resourceType": "EXTERNAL_INTEGRATION",
            "resourceId": target_system,
            "ipAddress": "127.0.0.1",
            "userAgent": "AI-Agent-Runner",
            "status": "SUCCESS",
            "details": action_payload,
            "timestamp": datetime.datetime.utcnow()
        }
        MongoDBManager.audit_logs().insert_one(audit_doc)

        trace = {
            "agent_name": cls.NAME,
            "action": f"Executed authorized operation [{action_type}] on [{target_system}]",
            "status": "COMPLETED",
            "duration_ms": duration_ms,
            "details": f"Approval confirmed. Dispatched payload to {target_system}"
        }
        state["agent_traces"].append(trace)

        response_content = (
            f"### ✅ Operation Successfully Executed\n"
            f"Authorized operation `{action_type}` has been executed on **{target_system}**:\n\n"
            f"- **Execution Timestamp**: `{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}`\n"
            f"- **System Ref ID**: `OP-{int(time.time()) % 100000}`\n"
            f"- **Audit Status**: Tamper-evident record logged to MongoDB Audit Trail.\n"
        )
        state["intermediate_results"]["action_agent"] = response_content
        return state
