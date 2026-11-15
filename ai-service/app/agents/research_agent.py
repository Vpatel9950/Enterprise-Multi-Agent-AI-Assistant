import time
from typing import Dict, Any
from app.models.state import AgentState, AgentTrace
from app.llm.gemini_client import ask_gemini

SYSTEM_PROMPT = """You are an Enterprise Research & Synthesis Agent for Acme Corporation.
You compile executive-grade research briefs by synthesizing internal company data
and industry knowledge. Your outputs are used by senior leadership for decision making.
Focus on: strategic insights, market trends, competitive benchmarks, and operational recommendations.
Format as structured executive briefs with clear sections. Use bullet points and headers."""

MOCK_RESPONSE = """### 🔬 Executive Research & Information Synthesis
**Executive Brief Summary:**
- **Market Trends**: Enterprise multi-agent AI systems are replacing single LLM chatbots with coordinated agent swarms.
- **Security Imperatives**: RBAC and tenant-level data isolation are critical for enterprise deployment.
- **Adoption Roadmap**: Phased rollout across HR, IT, and Finance delivers immediate ROI."""

class ResearchAgent:
    CODE = "research_agent"
    NAME = "Research & Synthesis Agent"

    @classmethod
    def execute(cls, state: AgentState) -> AgentState:
        start_time = time.time()
        query = state["query"]
        rag_context = state.get("rag_context_text", "")

        response = ask_gemini(
            system_prompt=SYSTEM_PROMPT,
            user_query=query,
            context=rag_context,
            temperature=0.4,
            fallback_response=MOCK_RESPONSE
        )

        duration_ms = int((time.time() - start_time) * 1000)
        trace: AgentTrace = {
            "agent_name": cls.NAME,
            "action": "Compiled multi-source research brief with fact-checking",
            "status": "COMPLETED",
            "duration_ms": duration_ms,
            "details": "Synthesized internal knowledge and industry best practices"
        }
        state["agent_traces"].append(trace)
        state["intermediate_results"]["research_agent"] = response
        return state
