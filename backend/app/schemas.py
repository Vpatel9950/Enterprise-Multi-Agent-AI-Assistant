from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any, Dict
from datetime import datetime

# Auth & User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    department: Optional[str] = "General"

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Agent Schemas
class AgentBase(BaseModel):
    name: str
    code: str
    role_description: str
    system_prompt: str
    model_name: Optional[str] = "gpt-4o-mini"
    temperature: Optional[float] = 0.7
    tools_enabled: Optional[List[str]] = []
    is_active: Optional[bool] = True

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    role_description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    tools_enabled: Optional[List[str]] = None
    is_active: Optional[bool] = None

class AgentResponse(AgentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Message & Chat Schemas
class MessageCreate(BaseModel):
    conversation_id: Optional[int] = None
    agent_id: Optional[int] = None # Optional manual override, or auto-route if None
    content: str

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_type: str
    sender_name: str
    agent_id: Optional[int] = None
    content: str
    metadata_json: Optional[str] = "{}"
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    agent_id: Optional[int] = None

class ConversationResponse(BaseModel):
    id: int
    title: str
    user_id: int
    assigned_agent_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageResponse]] = []

    class Config:
        from_attributes = True

# Knowledge Document Schemas
class DocumentCreate(BaseModel):
    filename: str
    category: str = "General Policy"
    content: str

class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    word_count: int
    chunk_count: int
    uploaded_by: str
    category: str
    created_at: datetime

    class Config:
        from_attributes = True

# Workflow Schemas
class WorkflowCreate(BaseModel):
    name: str
    description: str
    trigger_type: str
    target_agent_id: int
    config_json: Optional[str] = "{}"

class WorkflowRunResponse(BaseModel):
    id: int
    workflow_id: int
    status: str
    input_payload: str
    output_log: str
    executed_at: datetime
    duration_ms: int

    class Config:
        from_attributes = True

class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: str
    trigger_type: str
    target_agent_id: int
    config_json: str
    status: str
    run_count: int
    last_run_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Integration Schemas
class IntegrationCreate(BaseModel):
    name: str
    service_type: str
    webhook_url: Optional[str] = None
    config_json: Optional[str] = "{}"

class IntegrationResponse(BaseModel):
    id: int
    name: str
    service_type: str
    status: str
    api_key_masked: str
    webhook_url: Optional[str] = None
    config_json: str
    last_sync_at: datetime

    class Config:
        from_attributes = True

# Analytics Summary
class AnalyticsOverview(BaseModel):
    total_conversations: int
    total_messages: int
    total_workflows: int
    total_documents: int
    active_agents_count: int
    avg_response_time_ms: float
    token_usage_total: int
    avg_satisfaction: float
    top_agents: List[Dict[str, Any]]
    recent_events: List[Dict[str, Any]]
