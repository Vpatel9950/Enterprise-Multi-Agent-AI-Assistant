from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    query: str
    preferred_agent_code: Optional[str] = None # Optional override (default: orchestrator auto-route)
    organization_id: Optional[str] = None
    stream: bool = False

class CitationDto(BaseModel):
    document_id: str
    source_name: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    relevance_score: float
    snippet: str

class AgentTraceDto(BaseModel):
    agent_name: str
    action: str
    status: str
    duration_ms: int
    details: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    assigned_agent: str
    agent_code: str
    response: str
    citations: List[CitationDto] = []
    agent_traces: List[AgentTraceDto] = []
    approval_required: bool = False
    approval_id: Optional[str] = None
    duration_ms: int = 0
    tokens_used: int = 0

class DocumentIndexRequest(BaseModel):
    file_name: str
    file_type: str
    content: str
    classification: str = "INTERNAL"
    allowed_roles: List[str] = ["EMPLOYEE", "MANAGER", "ORG_ADMIN", "SUPER_ADMIN"]
    department_id: Optional[str] = None

class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 4
    department_id: Optional[str] = None

class ApprovalDecisionRequest(BaseModel):
    approval_id: str
    decision: str = Field(..., pattern="^(APPROVED|REJECTED)$")
    review_notes: Optional[str] = None
