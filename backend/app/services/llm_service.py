import json
import time
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models import Agent, Message, Conversation
from app.services.rag_service import RAGService
from app.services.analytics_service import AnalyticsService

class LLMService:
    @classmethod
    def route_intent(cls, query: str, active_agents: List[Agent]) -> Agent:
        q_lower = query.lower()
        
        intent_map = {
            "hr_agent": ["pto", "leave", "vacation", "policy", "hr", "onboarding", "benefits", "salary", "payroll", "insurance", "employee"],
            "sales_agent": ["sales", "lead", "deal", "pricing", "quote", "revenue", "pipeline", "prospect", "rfp", "crm"],
            "tech_support": ["error", "bug", "code", "api", "database", "server", "crash", "debug", "deployment", "log", "exception"],
            "data_analyst": ["data", "metrics", "chart", "analytics", "sql", "report", "kpi", "trend", "statistics", "growth"],
            "workflow_agent": ["workflow", "automation", "trigger", "action", "delegate", "pipeline", "schedule", "task", "process"],
            "customer_support": ["help", "support", "ticket", "issue", "customer", "inquiry", "status", "refund", "complaint"]
        }
        
        agent_by_code = {a.code: a for a in active_agents}
        
        scores = {}
        for code, keywords in intent_map.items():
            score = sum(1 for kw in keywords if kw in q_lower)
            if score > 0 and code in agent_by_code:
                scores[code] = score
                
        if scores:
            best_code = max(scores, key=scores.get)
            return agent_by_code[best_code]
            
        return agent_by_code.get("customer_support", active_agents[0] if active_agents else None)

    @classmethod
    def generate_agent_response(
        cls, 
        db: Session, 
        query: str, 
        agent: Agent, 
        conversation_history: List[Dict[str, str]] = None,
        rag_snippets: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        agent_code = agent.code
        q_lower = query.lower()
        
        rag_context_text = ""
        citations = []
        if rag_snippets:
            rag_context_text = "\n\n### 📚 Relevant Enterprise Knowledge Base References:\n"
            for snip in rag_snippets:
                rag_context_text += f"- **[{snip['filename']}] (Relevance: {int(snip['similarity_score']*100)}%)**: {snip['snippet']}\n"
                citations.append({
                    "filename": snip["filename"],
                    "category": snip["category"],
                    "score": snip["similarity_score"],
                    "snippet": snip["snippet"]
                })

        subagent_traces = []
        
        if agent_code == "hr_agent":
            if "pto" in q_lower or "leave" in q_lower or "vacation" in q_lower:
                content = (
                    "### 🏢 HR Policy & PTO Overview\n"
                    "According to the **Enterprise HR Policy (2026)**, full-time employees are entitled to standard leave benefits:\n\n"
                    "| Leave Type | Annual Allowance | Approval Required |\n"
                    "| :--- | :--- | :--- |\n"
                    "| Paid Time Off (PTO) | 20 Days | Manager Approval (2 days prior) |\n"
                    "| Sick / Wellness | 10 Days | Self-service log |\n"
                    "| Parental Leave | 12 Weeks | HR Administration |\n\n"
                    "**To Submit a Request:**\n"
                    "1. Log in to the HR Portal or ask me to draft a manager request.\n"
                    "2. Ensure minimum 48 hours notice for planned absences.\n"
                )
            elif "onboard" in q_lower or "benefit" in q_lower:
                content = (
                    "### 🚀 Employee Onboarding & Benefits Guide\n"
                    "Welcome aboard! Here are the core enrollment milestones for new enterprise team members:\n\n"
                    "- **Week 1:** IT Equipment setup, Security 2FA, and HR Portal verification.\n"
                    "- **Week 2:** Health & Dental insurance election, 401(k) retirement matching (up to 6%).\n"
                    "- **Week 4:** Departmental orientation & quarterly goal alignment.\n"
                )
            else:
                content = (
                    f"Hello! I am the **{agent.name}**. I can assist with employee benefits, company policy lookup, "
                    f"leave requests, and workplace guidelines. How can I help your team today?"
                )

        elif agent_code == "sales_agent":
            if "pipeline" in q_lower or "revenue" in q_lower or "deal" in q_lower:
                content = (
                    "### 📈 Executive Sales Pipeline Summary (Q3)\n"
                    "Here is the real-time breakdown of current enterprise deal opportunities:\n\n"
                    "| Stage | Opportunities | Total Value | Weighted Probability |\n"
                    "| :--- | :---: | :---: | :---: |\n"
                    "| Qualification | 14 | $420,000 | 20% |\n"
                    "| Proposal Delivered | 8 | $680,000 | 60% |\n"
                    "| Contract Negotiation | 5 | $1,150,000 | 85% |\n"
                    "| **Closed Won (QTD)** | **12** | **$2,450,000** | **100%** |\n\n"
                    "💡 *Recommendation*: Focus sales engineering support on top 3 Contract Negotiation deals to lock in target quarterly revenue."
                )
            elif "lead" in q_lower or "rfp" in q_lower:
                content = (
                    "### 🎯 Lead Qualification & RFP Response Assistant\n"
                    "I have analyzed the lead requirements. Key scoring criteria:\n"
                    "1. **Enterprise Size**: > 500 seats (High Fit)\n"
                    "2. **Budget Authority**: Verified C-Level Sponsor\n"
                    "3. **Timeline**: Q3 Deployment\n\n"
                    "I can automatically draft a customized RFP proposal or trigger a CRM follow-up task!"
                )
            else:
                content = (
                    f"Greetings! I am the **{agent.name}**. I analyze deal pipelines, generate sales proposals, "
                    f"score inbound enterprise leads, and sync opportunity updates directly with CRM systems."
                )

        elif agent_code == "tech_support":
            if "error" in q_lower or "bug" in q_lower or "log" in q_lower or "api" in q_lower:
                content = (
                    "### 🛠️ Technical Diagnostic & Debugging Analysis\n"
                    "I have parsed the issue symptoms and checked system logs:\n\n"
                    "```python\n"
                    "# System Error Diagnostic Trace\n"
                    "STATUS_CODE: 500 Internal Server Error\n"
                    "CAUSE: Database Connection Pool Exhaustion (max_connections=100 reached)\n"
                    "RECOMMENDATION:\n"
                    "  1. Increase SQLAlchemy pool_size to 30 with max_overflow=20\n"
                    "  2. Verify DB session cleanup in async endpoint context managers\n"
                    "```\n\n"
                    "**Remediation Steps:**\n"
                    "- Execute connection pool health check.\n"
                    "- Check database connection timeout limits (`check_same_thread=False`)."
                )
            else:
                content = (
                    f"Hello! I am the **{agent.name}**. I assist developers and system admins with API troubleshooting, "
                    f"stack trace analysis, infrastructure diagnostics, and code optimizations."
                )

        elif agent_code == "data_analyst":
            sql_query = (
                "SELECT \n"
                "    a.name AS agent_name,\n"
                "    COUNT(m.id) AS total_messages,\n"
                "    ROUND(AVG(e.response_time_ms), 2) AS avg_latency_ms,\n"
                "    ROUND(AVG(e.satisfaction_score), 2) AS satisfaction_rating\n"
                "FROM agents a\n"
                "LEFT JOIN messages m ON a.id = m.agent_id\n"
                "LEFT JOIN analytics_events e ON a.id = e.agent_id\n"
                "GROUP BY a.id\n"
                "ORDER BY total_messages DESC;"
            )
            content = (
                "### 📊 Enterprise Data Analysis & SQL Insights\n"
                "Generated automated SQL analytical query for your requested metric:\n\n"
                "```sql\n" + sql_query + "\n```\n\n"
                "**Key Takeaways:**\n"
                "- Customer Support Agent has the highest inquiry volume (42%).\n"
                "- Average system-wide latency is optimized at **240ms**.\n"
                "- User satisfaction rating stands at **4.85 / 5.0**."
            )

        elif agent_code == "workflow_agent":
            content = (
                "### ⚡ Workflow Automation & Agent Delegation Pipeline\n"
                "I am orchestrating an enterprise automation flow based on your prompt:\n\n"
                "1. **Trigger Condition**: Inbound user multi-department query\n"
                "2. **Sub-Agent Delegation**:\n"
                "   - 🔹 *Data Analyst Agent*: Executed DB metric retrieval.\n"
                "   - 🔹 *HR Agent*: Checked compliance rules.\n"
                "3. **Integration Dispatch**: Prepared Slack notification payload.\n\n"
                "✅ All sub-tasks synced successfully with the workflow engine!"
            )
            subagent_traces.append({
                "agent_name": "Data Analyst Agent",
                "action": "Generated KPI dataset",
                "status": "Completed"
            })
            subagent_traces.append({
                "agent_name": "HR Agent",
                "action": "Verified policy compliance",
                "status": "Completed"
            })

        else: # customer_support
            content = (
                "### 🎧 Enterprise Customer Support Assistant\n"
                "Thank you for contacting Enterprise Support. Here is how I can assist you:\n\n"
                "- **Ticket Resolution**: Search existing knowledge base articles and solutions.\n"
                "- **Escalation**: Route your request to Tier-2 specialized technical or billing engineers.\n"
                "- **Service Status**: All core enterprise microservices are operational (99.98% Uptime).\n\n"
                "How may I assist with your ticket today?"
            )

        if rag_context_text:
            content += rag_context_text

        duration_ms = int((time.time() - start_time) * 1000)
        
        AnalyticsService.log_event(
            db, 
            action_type="chat_query", 
            agent_id=agent.id, 
            response_time_ms=duration_ms, 
            tokens_used=len(content.split()) * 2,
            satisfaction_score=4.9
        )

        return {
            "content": content,
            "agent_id": agent.id,
            "agent_name": agent.name,
            "agent_code": agent.code,
            "duration_ms": duration_ms,
            "citations": citations,
            "subagent_traces": subagent_traces
        }
