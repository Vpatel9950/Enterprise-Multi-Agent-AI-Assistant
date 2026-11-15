from typing import TypedDict, List, Dict, Any, Optional

class AgentTrace(TypedDict):
    agent_name: str
    action: str
    status: str             # "STARTED", "COMPLETED", "FAILED", "PENDING_APPROVAL"
    duration_ms: int
    details: Optional[str]

class Citation(TypedDict):
    document_id: str
    source_name: str
    page_number: Optional[int]
    section: Optional[str]
    relevance_score: float
    snippet: str

class AgentState(TypedDict):
    # Context & User Identity
    conversation_id: str
    user_id: str
    user_name: str
    user_email: str
    user_role: str          # "SUPER_ADMIN", "ORG_ADMIN", "MANAGER", "EMPLOYEE"
    organization_id: str
    department_id: Optional[str]

    # Query & Execution
    query: str
    intent: str
    execution_plan: List[str]
    current_step: int
    selected_agent: str

    # Agent Collaboration Traces & Citations
    agent_traces: List[AgentTrace]
    rag_citations: List[Citation]
    rag_context_text: str

    # Sub-task Results & Intermediate Payloads
    intermediate_results: Dict[str, Any]

    # Human-in-the-Loop (HITL) Gate
    approval_required: bool
    approval_id: Optional[str]
    approval_status: Optional[str]      # "PENDING", "APPROVED", "REJECTED"
    action_type: Optional[str]
    action_payload: Optional[Dict[str, Any]]

    # Output
    final_response: str
    tokens_used: int
    duration_ms: int
    error: Optional[str]
