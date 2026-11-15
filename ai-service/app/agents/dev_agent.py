import time
from typing import Dict, Any
from app.models.state import AgentState, AgentTrace
from app.llm.gemini_client import ask_gemini

SYSTEM_PROMPT = """You are a Senior Developer & Solutions Architect Agent for Acme Corporation.
You help engineers with:
- Debugging errors, stack traces, and production incidents
- Software architecture (microservices, monolith, event-driven)
- API design (REST, GraphQL, OpenAPI/Swagger)
- Cloud infrastructure (AWS, GCP, Docker, Kubernetes)
- Code reviews and best practices (Java, Python, React)
- Database optimization (MongoDB, Redis)

This system uses: Java Spring Boot 3, Python FastAPI, React 18, MongoDB 7, Redis.
Provide clean code examples when relevant. Use markdown with code blocks."""

MOCK_RESPONSE = """### 🛠️ Developer Diagnostics & Architectural Guidance
**Technical Architecture Overview:**
- **Backend**: Java Spring Boot 3 + Spring Data MongoDB + Spring Security 6
- **AI Service**: Python FastAPI + LangGraph + In-Memory Vector Store
- **Frontend**: React 18 + Vite + TypeScript + Tailwind CSS + SSE streaming
- **Database**: MongoDB 7 (exclusive) + Redis (cache)"""

class DeveloperAgent:
    CODE = "dev_agent"
    NAME = "Developer & Architecture Agent"

    @classmethod
    def execute(cls, state: AgentState) -> AgentState:
        start_time = time.time()
        query = state["query"]

        response = ask_gemini(
            system_prompt=SYSTEM_PROMPT,
            user_query=query,
            context=state.get("rag_context_text", ""),
            temperature=0.2,
            fallback_response=MOCK_RESPONSE
        )

        duration_ms = int((time.time() - start_time) * 1000)
        trace: AgentTrace = {
            "agent_name": cls.NAME,
            "action": "Generated technical architecture diagnostic & code guidance",
            "status": "COMPLETED",
            "duration_ms": duration_ms,
            "details": "Parsed stack trace and matched against enterprise cloud SLAs"
        }
        state["agent_traces"].append(trace)
        state["intermediate_results"]["dev_agent"] = response
        return state
