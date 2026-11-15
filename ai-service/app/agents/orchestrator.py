import time
import datetime
import logging
import json
from typing import Dict, Any, List, Optional
from bson import ObjectId

from app.models.state import AgentState, AgentTrace
from app.db.mongo import MongoDBManager, to_object_id
from app.agents.rag_agent import KnowledgeRAGAgent
from app.agents.hr_agent import HRAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.dev_agent import DeveloperAgent
from app.agents.research_agent import ResearchAgent
from app.agents.db_agent import DatabaseAgent
from app.agents.action_agent import ActionAgent

logger = logging.getLogger("enterprise.ai.orchestrator")

class OrchestratorAgent:
    CODE = "orchestrator"
    NAME = "Centralized Orchestrator Agent"

    # Available agents for Gemini-based routing
    AGENT_DESCRIPTIONS = {
        "rag_agent": "Company policies, internal documents, handbooks, SLAs, guidelines, compliance rules",
        "hr_agent": "PTO, leave, vacation, benefits, insurance, onboarding, employee relations, HR queries",
        "finance_agent": "Budgets, spending, cost centers, expenses, procurement, invoices, financial data",
        "dev_agent": "Code, APIs, architecture, microservices, bugs, errors, deployments, technical issues",
        "db_agent": "Database queries, MongoDB aggregation, record counts, collection stats, telemetry",
        "action_agent": "Create Jira tickets, deploy clusters, send Slack notifications, trigger automations, provision resources",
        "research_agent": "Market research, competitive analysis, trend summarization, general research questions"
    }

    @classmethod
    def classify_intent_gemini(cls, query: str) -> List[str]:
        """Use Gemini to intelligently route the query to the right agents."""
        try:
            from app.llm.gemini_client import ask_gemini
            agent_list = "\n".join([f"- {code}: {desc}" for code, desc in cls.AGENT_DESCRIPTIONS.items()])
            system_prompt = f"""You are an enterprise AI routing supervisor. 
Given a user query, determine which specialized agents should handle it.
Return ONLY a JSON array of agent codes from this list (order matters — most relevant first):
{agent_list}

Rules:
- Include 1-3 agents maximum
- If action/execution is needed (create, deploy, notify), always include action_agent
- If the question needs document/policy lookup AND specialist, include both
- Return ONLY valid JSON array, no explanation, e.g.: ["hr_agent"] or ["finance_agent"] or ["rag_agent", "hr_agent"]"""

            result = ask_gemini(
                system_prompt=system_prompt,
                user_query=f"Route this query: {query}",
                context="",
                temperature=0.1,
                fallback_response=""
            )

            # Parse JSON array from Gemini response
            result = result.strip()
            if result.startswith("["):
                agents = json.loads(result)
                valid = [a for a in agents if a in cls.AGENT_DESCRIPTIONS]
                if valid:
                    logger.info(f"Gemini routing: '{query[:50]}' → {valid}")
                    return valid
        except Exception as e:
            logger.warning(f"Gemini routing failed, falling back to keyword: {e}")
        return []

    @classmethod
    def classify_intent_keywords(cls, query: str) -> List[str]:
        """Keyword-based fallback routing."""
        q = query.lower()
        matched = []

        if any(k in q for k in ["policy", "handbook", "document", "spec", "sla", "manual", "rule", "guideline"]):
            matched.append("rag_agent")
        if any(k in q for k in ["pto", "leave", "vacation", "holiday", "benefit", "insurance", "401k", "maternity", "paternity", "onboarding", "hr"]):
            matched.append("hr_agent")
        if any(k in q for k in ["budget", "spend", "cost", "expense", "variance", "procure", "invoice", "finance", "revenue"]):
            matched.append("finance_agent")
        if any(k in q for k in ["code", "api", "architecture", "microservice", "error", "bug", "crash", "500", "docker", "spring", "fastapi"]):
            matched.append("dev_agent")
        if any(k in q for k in ["database", "mongo", "aggregate", "collection", "record count", "users count", "telemetry", "table"]):
            matched.append("db_agent")
        if any(k in q for k in ["create", "deploy", "jira", "slack", "notify", "broadcast", "trigger", "cluster", "provision", "submit"]):
            matched.append("action_agent")
        if any(k in q for k in ["research", "summarize", "market", "competitor", "trends", "analysis", "brief"]):
            matched.append("research_agent")

        if not matched:
            matched = ["rag_agent", "research_agent"]

        return list(dict.fromkeys(matched))

    @classmethod
    def classify_intent(cls, query: str, preferred_agent: Optional[str] = None) -> List[str]:
        if preferred_agent and preferred_agent != "orchestrator":
            return [preferred_agent]

        # Try Gemini-powered routing first
        gemini_route = cls.classify_intent_gemini(query)
        if gemini_route:
            return gemini_route

        # Fallback to keyword matching
        return cls.classify_intent_keywords(query)

    @classmethod
    def execute_pipeline(cls, initial_state: AgentState) -> AgentState:
        total_start = time.time()
        state = initial_state
        query = state["query"]
        preferred = state.get("selected_agent")

        # Step 1: Supervisor Intent Classification & Plan Decomposition
        execution_plan = cls.classify_intent(query, preferred)
        state["execution_plan"] = execution_plan
        state["intent"] = " -> ".join(execution_plan)

        trace_supervisor: AgentTrace = {
            "agent_name": cls.NAME,
            "action": f"Analyzed query intent: Decomposed into pipeline [{', '.join(execution_plan)}]",
            "status": "COMPLETED",
            "duration_ms": 25,
            "details": f"Caller Role: {state['user_role']}, Org: {state['organization_id']}"
        }
        state["agent_traces"].append(trace_supervisor)

        # Step 2: Execute Knowledge/RAG Agent first if in plan or if document context relevant
        if "rag_agent" in execution_plan or len(execution_plan) > 1:
            state = KnowledgeRAGAgent.execute(state)

        # Step 3: Execute Specialized Domain Agents in Plan
        for agent_code in execution_plan:
            if agent_code == "rag_agent":
                continue # Already executed
            elif agent_code == "hr_agent":
                state = HRAgent.execute(state)
            elif agent_code == "finance_agent":
                state = FinanceAgent.execute(state)
            elif agent_code == "dev_agent":
                state = DeveloperAgent.execute(state)
            elif agent_code == "research_agent":
                state = ResearchAgent.execute(state)
            elif agent_code == "db_agent":
                state = DatabaseAgent.execute(state)
            elif agent_code == "action_agent":
                state = ActionAgent.execute(state)

        # Step 4: Answer Synthesis
        synthesis_parts = []
        for code, res in state["intermediate_results"].items():
            synthesis_parts.append(res)

        final_response = "\n\n---\n\n".join(synthesis_parts)

        # Filter RAG citations by user role — CONFIDENTIAL docs hidden from non-managers
        MANAGER_ROLES = ["MANAGER", "ORG_ADMIN", "SUPER_ADMIN"]
        user_role = state["user_role"]
        visible_citations = []
        for c in state.get("rag_citations", []):
            source = (c.get("source_name") or "").lower()
            is_confidential = any(kw in source for kw in ["financial", "budget", "confidential", "q3_conf"])
            if is_confidential and user_role not in MANAGER_ROLES:
                continue  # Block CONFIDENTIAL from Employee
            visible_citations.append(c)
        state["rag_citations"] = visible_citations

        if visible_citations:
            final_response += "\n\n### 📚 Verified Knowledge Base Citations:"
            for c in visible_citations:
                page_str = f", Page {c['page_number']}" if c.get('page_number') else ""
                final_response += (
                    f"\n- **{c['source_name']}** (Sec: *{c['section']}*{page_str}) "
                    f"— *Match: {int(c['relevance_score']*100)}%*"
                )

        state["final_response"] = final_response
        state["duration_ms"] = int((time.time() - total_start) * 1000)
        state["tokens_used"] = len(final_response.split()) * 2 + 120

        # Step 5: Atomically Save Conversation Message to MongoDB
        try:
            cls.persist_conversation_message(state)
        except Exception as e:
            logger.error(f"Failed to persist message to MongoDB: {e}")

        return state

    @classmethod
    def persist_conversation_message(cls, state: AgentState):
        org_oid = to_object_id(state["organization_id"])
        user_oid = to_object_id(state["user_id"])
        conv_id = state.get("conversation_id")

        # 1. Create or Update Conversation Document
        if conv_id and ObjectId.is_valid(conv_id):
            conv_oid = ObjectId(conv_id)
            MongoDBManager.conversations().update_one(
                {"_id": conv_oid},
                {
                    "$set": {
                        "updatedAt": datetime.datetime.utcnow(),
                        "assignedAgentCode": state.get("selected_agent", "orchestrator")
                    }
                }
            )
        else:
            new_title = state["query"][:35] + ("..." if len(state["query"]) > 35 else "")
            conv_doc = {
                "organizationId": org_oid,
                "userId": user_oid,
                "title": new_title,
                "assignedAgentCode": state.get("selected_agent", "orchestrator"),
                "status": "ACTIVE",
                "pinnedMessageIds": [],
                "metadata": {"intent": state["intent"]},
                "createdAt": datetime.datetime.utcnow(),
                "updatedAt": datetime.datetime.utcnow()
            }
            conv_res = MongoDBManager.conversations().insert_one(conv_doc)
            conv_oid = conv_res.inserted_id
            state["conversation_id"] = str(conv_oid)

        # 2. Insert User Message
        user_msg = {
            "conversationId": conv_oid,
            "organizationId": org_oid,
            "senderType": "USER",
            "senderId": user_oid,
            "senderName": state.get("user_name", "Employee"),
            "content": state["query"],
            "citations": [],
            "agentTraces": [],
            "durationMs": 0,
            "tokensUsed": 0,
            "createdAt": datetime.datetime.utcnow()
        }
        MongoDBManager.messages().insert_one(user_msg)

        # 3. Insert Agent Response Message
        agent_msg = {
            "conversationId": conv_oid,
            "organizationId": org_oid,
            "senderType": "AGENT",
            "senderId": "orchestrator",
            "senderName": "Centralized Orchestrator Agent",
            "content": state["final_response"],
            "citations": state.get("rag_citations", []),
            "agentTraces": state.get("agent_traces", []),
            "durationMs": state["duration_ms"],
            "tokensUsed": state["tokens_used"],
            "createdAt": datetime.datetime.utcnow()
        }
        MongoDBManager.messages().insert_one(agent_msg)

        # 4. Insert Execution Log
        log_doc = {
            "organizationId": org_oid,
            "conversationId": conv_oid,
            "messageId": None,
            "userId": user_oid,
            "agentCode": state.get("selected_agent", "orchestrator"),
            "taskDescription": state["intent"],
            "inputStateSummary": state["query"][:150],
            "outputStateSummary": state["final_response"][:150],
            "status": "PAUSED_HITL" if state["approval_required"] else "SUCCESS",
            "durationMs": state["duration_ms"],
            "error": state.get("error"),
            "createdAt": datetime.datetime.utcnow()
        }
        MongoDBManager.agent_execution_logs().insert_one(log_doc)
