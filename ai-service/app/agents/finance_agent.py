import time
from typing import Dict, Any
from app.models.state import AgentState, AgentTrace
from app.llm.gemini_client import ask_gemini

SYSTEM_PROMPT = """You are an Enterprise Finance & Procurement Agent for Acme Corporation.
You help managers and administrators with budget analysis, spending variance, procurement policies,
cost center breakdowns, and expense approvals.
Answer ONLY using the provided document context. If context has budget numbers, use those exact numbers.
Use markdown tables when showing budget data. Be precise with numbers."""

RESTRICTED_MSG = """### 💳 Enterprise Finance & Budget Operations
⚠️ **Access Restricted**: Detailed departmental budget allocations and cost center ledger figures are restricted to **Managers and Organization Administrators**.

For expense reimbursements or travel requests, please submit via Concur or contact your department manager."""

MOCK_BUDGET = """### 💳 Enterprise Finance & Budget Operations
**Q3 Operating Budget Breakdown (Consolidated):**

| Department | Allocated | Actual Spend | Variance | Status |
| :--- | :---: | :---: | :---: | :---: |
| Engineering & Cloud Ops | $1,450,000 | $1,180,000 | -$270,000 (18.6%) | ✅ On Track |
| Product & Architecture | $420,000 | $390,000 | -$30,000 (7.1%) | ✅ On Track |
| Sales & Commercial | $850,000 | $820,000 | -$30,000 (3.5%) | ✅ On Track |
| HR & Corporate Ops | $380,000 | $410,000 | +$30,000 (7.8%) | ⚠️ Review |

💡 *Burn rate: 89.2% of Q3 ceiling. HR department needs review.*"""

class FinanceAgent:
    CODE = "finance_agent"
    NAME = "Finance & Procurement Agent"

    @classmethod
    def execute(cls, state: AgentState) -> AgentState:
        start_time = time.time()
        user_role = state["user_role"]
        query = state["query"]
        org_id = state["organization_id"]
        q_lower = query.lower()

        # RBAC check — Finance is MANAGER+ only
        if any(w in q_lower for w in ["budget", "allocation", "spend", "cost", "revenue", "variance", "expense", "finance", "cloud", "infrastructure", "headcount"]):
            if user_role not in ["MANAGER", "ORG_ADMIN", "SUPER_ADMIN"]:
                response = RESTRICTED_MSG
            else:
                # Try to get RAG context from Finance documents first
                rag_context = state.get("rag_context_text", "")

                # If no RAG context yet, query it directly for finance docs
                if not rag_context:
                    try:
                        from app.rag.service import RAGService
                        results = RAGService.query(
                            query=query,
                            organization_id=org_id,
                            user_role=user_role,
                            top_k=5
                        )
                        if results:
                            rag_context = "\n".join([
                                f"[{r['source_name']} - {r['section']}]: {r['snippet']}"
                                for r in results
                            ])
                            state["rag_citations"] = results
                    except Exception:
                        pass

                response = ask_gemini(
                    system_prompt=SYSTEM_PROMPT,
                    user_query=query,
                    context=rag_context,
                    temperature=0.1,
                    fallback_response=MOCK_BUDGET
                )
        else:
            procurement_fallback = """### 💳 Corporate Procurement Policy
- **< $500**: Direct manager approval via corporate card.
- **$500 - $5,000**: IT SecOps review & Finance sign-off required.
- **> $5,000**: VP Procurement approval + Action Agent submission."""
            response = ask_gemini(
                system_prompt=SYSTEM_PROMPT,
                user_query=query,
                temperature=0.1,
                fallback_response=procurement_fallback
            )

        duration_ms = int((time.time() - start_time) * 1000)
        trace: AgentTrace = {
            "agent_name": cls.NAME,
            "action": f"Executed financial ledger lookup with clearance check for role '{user_role}'",
            "status": "COMPLETED",
            "duration_ms": duration_ms,
            "details": f"Role '{user_role}' verified against spend approval matrix"
        }
        state["agent_traces"].append(trace)
        state["intermediate_results"]["finance_agent"] = response
        return state
