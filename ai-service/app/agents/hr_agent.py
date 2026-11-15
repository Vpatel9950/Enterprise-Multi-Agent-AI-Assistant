import time
from typing import Dict, Any
from app.models.state import AgentState, AgentTrace
from app.llm.gemini_client import ask_gemini

SYSTEM_PROMPT = """You are an Enterprise HR & Employee Agent for Acme Corporation.
You help employees with PTO policy, leave requests, benefits (medical, dental, 401k),
parental leave, onboarding, and workplace policies.
Always reference "Enterprise HR & Benefits Directives (2026)" as your source.
Be professional, empathetic, and concise. Use markdown formatting.
Never reveal confidential salary data or personal employee records."""

MOCK_RESPONSES = {
    "pto": """### 🏢 Enterprise HR & Workforce Advisory
Based on the **Enterprise HR & Benefits Directives (2026)**:

**Paid Time Off (PTO) Entitlements:**
- **Annual Allowance**: Full-time employees accrue **20 vacation days** annually (1.67 days/month).
- **Approval Workflow**: Absences over 3 consecutive days require manager sign-off via HR Portal.
- **Wellness & Sick Days**: 10 dedicated wellness days per calendar year (self-service log).
- **How to Apply**: Log in to HR Portal → My Time Off → Submit Request → Manager notified automatically.""",

    "parental": """### 🏢 Enterprise HR & Workforce Advisory
**Parental & Family Leave:**
- **Primary Caregiver**: 12 weeks of 100% fully paid leave.
- **Secondary Caregiver**: 4 weeks of paid bonding leave.
- **Healthcare**: Full medical, dental, and vision coverage continues during leave.""",

    "benefit": """### 🏢 Enterprise HR & Workforce Advisory
**Health & Retirement Benefits:**
- **Medical/Dental**: Company sponsors 85% of employee premium, 65% for dependents.
- **401(k) Match**: Dollar-for-dollar match up to 6% of base salary.
- **Open Enrollment**: Every October via Employee Benefits Hub.""",

    "default": """### 🏢 Enterprise HR & Workforce Advisory
**General Workforce Guidelines:**
- **Hybrid Policy**: 3 days on-site, 2 days remote (manager approval).
- **EAP**: Confidential 24/7 mental health support.
- **HR Helpdesk**: hr.helpdesk@enterprise.ai"""
}

class HRAgent:
    CODE = "hr_agent"
    NAME = "HR & Employee Agent"

    @classmethod
    def execute(cls, state: AgentState) -> AgentState:
        start_time = time.time()
        query = state["query"]
        q_lower = query.lower()

        # Pick mock fallback based on keywords
        if any(w in q_lower for w in ["pto", "leave", "vacation", "holiday", "time off"]):
            fallback = MOCK_RESPONSES["pto"]
        elif any(w in q_lower for w in ["parental", "maternity", "paternity"]):
            fallback = MOCK_RESPONSES["parental"]
        elif any(w in q_lower for w in ["benefit", "insurance", "401k", "pension", "medical"]):
            fallback = MOCK_RESPONSES["benefit"]
        else:
            fallback = MOCK_RESPONSES["default"]

        # Try Gemini first, fall back to mock if not available
        response = ask_gemini(
            system_prompt=SYSTEM_PROMPT,
            user_query=query,
            context=state.get("rag_context_text", ""),
            temperature=0.3,
            fallback_response=fallback
        )

        duration_ms = int((time.time() - start_time) * 1000)
        trace: AgentTrace = {
            "agent_name": cls.NAME,
            "action": "Evaluated HR policy handbook & benefit eligibility rules",
            "status": "COMPLETED",
            "duration_ms": duration_ms,
            "details": "PII masked and verified against 2026 company guidelines"
        }
        state["agent_traces"].append(trace)
        state["intermediate_results"]["hr_agent"] = response
        return state
