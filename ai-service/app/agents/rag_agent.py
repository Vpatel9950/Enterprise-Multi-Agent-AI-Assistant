import time
from typing import Dict, Any, List
from app.models.state import AgentState, AgentTrace, Citation
from app.rag.service import RAGService

class KnowledgeRAGAgent:
    CODE = "rag_agent"
    NAME = "Knowledge & RAG Agent"

    @classmethod
    def execute(cls, state: AgentState) -> AgentState:
        start_time = time.time()
        query = state["query"]
        org_id = state["organization_id"]
        user_role = state["user_role"]
        dept_id = state.get("department_id")

        # 1. Retrieve citations with security ACL filtering
        results = RAGService.query(
            query=query,
            organization_id=org_id,
            user_role=user_role,
            top_k=3,
            department_id=dept_id
        )

        duration_ms = int((time.time() - start_time) * 1000)

        citations: List[Citation] = []
        context_parts = []
        for r in results:
            citations.append({
                "document_id": r["document_id"],
                "source_name": r["source_name"],
                "page_number": r["page_number"],
                "section": r["section"],
                "relevance_score": r["relevance_score"],
                "snippet": r["snippet"]
            })
            context_parts.append(
                f"- **[{r['source_name']}] (Sec: {r['section']}, Page: {r['page_number']}, Score: {int(r['relevance_score']*100)}%)**:\n  \"{r['snippet']}\""
            )

        rag_context = "\n".join(context_parts)
        state["rag_citations"] = citations
        state["rag_context_text"] = rag_context

        # 2. If documents found, use Gemini to synthesize a grounded answer
        if citations:
            fallback_text = f"Retrieved {len(citations)} verified document sources:\n" + rag_context
            try:
                from app.llm.gemini_client import ask_gemini
                system_prompt = """You are a corporate Knowledge Base AI assistant.
Answer employee questions using ONLY the provided document excerpts.
Be concise, accurate, and professional. Format with bullet points where appropriate.
If the excerpts don't fully answer the question, say what IS covered and suggest contacting HR/Finance."""

                gemini_answer = ask_gemini(
                    system_prompt=system_prompt,
                    user_query=query,
                    context=rag_context,
                    temperature=0.3,
                    fallback_response=fallback_text
                )

                if gemini_answer and not gemini_answer.startswith("⚠️ AI response unavailable"):
                    rag_result = f"### 📋 Knowledge Base Advisory\n{gemini_answer}"
                else:
                    rag_result = f"### 📋 Knowledge Base Advisory (Direct Excerpt)\n" + rag_context
            except Exception:
                rag_result = f"### 📋 Knowledge Base Advisory (Direct Excerpt)\n" + rag_context
        else:
            rag_result = "No verified internal company documents matched the query under caller's clearance level."

        # Add agent trace
        trace: AgentTrace = {
            "agent_name": cls.NAME,
            "action": f"Vector search executed across authorized documents for {user_role}. Found {len(citations)} source matches.",
            "status": "COMPLETED",
            "duration_ms": duration_ms,
            "details": f"Searched org {org_id} with clearance role '{user_role}'"
        }
        state["agent_traces"].append(trace)
        state["intermediate_results"]["rag_agent"] = rag_result

        return state
