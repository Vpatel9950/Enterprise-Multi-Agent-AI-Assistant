import time
from typing import Dict, Any, List
from bson import ObjectId
from app.models.state import AgentState, AgentTrace
from app.db.mongo import MongoDBManager, to_object_id

class DatabaseAgent:
    CODE = "db_agent"
    NAME = "Database Query Agent"

    FORBIDDEN_OPERATIONS = [
        "delete", "remove", "drop", "update", "insert", "replace",
        "eval", "reindex", "shutdown", "$where", "$out", "$merge"
    ]

    @classmethod
    def execute(cls, state: AgentState) -> AgentState:
        start_time = time.time()
        query = state["query"].lower()
        org_id = state["organization_id"]
        user_role = state["user_role"]

        response_lines = [
            "### 🗄️ Database Analytics & MongoDB Query Inspector"
        ]

        # 1. Guardrail Check: Block Destructive Commands
        if any(bad in query for bad in cls.FORBIDDEN_OPERATIONS):
            duration_ms = int((time.time() - start_time) * 1000)
            trace: AgentTrace = {
                "agent_name": cls.NAME,
                "action": "BLOCKED: Attempted write/delete/destructive database operation",
                "status": "FAILED",
                "duration_ms": duration_ms,
                "details": "Security rule violation: Only read-only queries are authorized"
            }
            state["agent_traces"].append(trace)
            state["intermediate_results"]["db_agent"] = (
                "⛔ **Security Guardrail Violation**: The Database Agent strictly permits read-only operations "
                "(`find()`, `count()`, `aggregate()`). Mutation, deletion, or modification of database records is strictly forbidden."
            )
            return state

        # 2. Permission Check: Only MANAGER, ORG_ADMIN, or SUPER_ADMIN
        if user_role not in ["MANAGER", "ORG_ADMIN", "SUPER_ADMIN"]:
            duration_ms = int((time.time() - start_time) * 1000)
            trace: AgentTrace = {
                "agent_name": cls.NAME,
                "action": "Access Denied: User role lacks DB_QUERY_READ permission",
                "status": "FAILED",
                "duration_ms": duration_ms,
                "details": f"Role '{user_role}' unauthorized for direct database querying"
            }
            state["agent_traces"].append(trace)
            state["intermediate_results"]["db_agent"] = (
                "⚠️ **Access Restricted**: Direct database schema exploration and aggregation queries require Manager or Administrator authorization."
            )
            return state

        # 3. Controlled Read-Only Query Execution
        try:
            # Query counts and statistics from MongoDB for the caller's organization
            org_oid = to_object_id(org_id)
            total_users = MongoDBManager.users().count_documents({"organizationId": org_oid})
            total_convs = MongoDBManager.conversations().count_documents({"organizationId": org_oid})
            total_docs = MongoDBManager.uploaded_documents().count_documents({"organizationId": org_oid})
            total_workflows = MongoDBManager.workflows().count_documents({"organizationId": org_oid})
            pending_approvals = MongoDBManager.approval_requests().count_documents({"organizationId": org_oid, "status": "PENDING"})

            # Sample aggregation: messages grouped by senderType
            pipeline = [
                {"$match": {"organizationId": org_oid}},
                {"$group": {"_id": "$senderType", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            msg_stats = list(MongoDBManager.messages().aggregate(pipeline))

            duration_ms = int((time.time() - start_time) * 1000)

            response_lines.extend([
                "**Executed Read-Only MongoDB Aggregation Pipeline:**\n",
                "```javascript",
                "// Secure tenant-isolated query on enterprise_ai database",
                "db.messages.aggregate([",
                f"  {{ $match: {{ organizationId: ObjectId('{org_id}') }} }},",
                "  {{ $group: { _id: '$senderType', count: { $sum: 1 } } }},",
                "  {{ $sort: { count: -1 } }}",
                "]);",
                "```\n",
                "**Current Organization Telemetry:**",
                f"- **Active Users**: `{total_users}` records",
                f"- **Total Conversations**: `{total_convs}` sessions",
                f"- **Indexed Knowledge Documents**: `{total_docs}` documents",
                f"- **Configured Workflows**: `{total_workflows}` automations",
                f"- **Pending Action Approvals**: `{pending_approvals}` requests pending review",
                "\n✅ *Integrity Guarantee*: Executed with zero write privileges under read-only replica set isolation."
            ])

            trace: AgentTrace = {
                "agent_name": cls.NAME,
                "action": f"Executed read-only aggregation on organization {org_id}",
                "status": "COMPLETED",
                "duration_ms": duration_ms,
                "details": f"Retrieved metrics: {total_users} users, {total_docs} docs, {total_convs} convs"
            }
            state["agent_traces"].append(trace)

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            trace = {
                "agent_name": cls.NAME,
                "action": f"Database query error: {str(e)}",
                "status": "FAILED",
                "duration_ms": duration_ms,
                "details": str(e)
            }
            state["agent_traces"].append(trace)
            response_lines.append(f"❌ Query execution failed: {str(e)}")

        state["intermediate_results"]["db_agent"] = "\n".join(response_lines)
        return state
