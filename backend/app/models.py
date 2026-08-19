import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="user") # "admin" or "user"
    department = Column(String, default="General")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user")
    workflows = relationship("Workflow", back_populates="creator")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False) # e.g., 'customer_support', 'hr_agent'
    role_description = Column(String, nullable=False)
    system_prompt = Column(Text, nullable=False)
    model_name = Column(String, default="gpt-4o-mini")
    temperature = Column(Float, default=0.7)
    tools_enabled = Column(Text, default="[]") # JSON string array of enabled tools
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    conversations = relationship("Conversation", back_populates="assigned_agent")
    messages = relationship("Message", back_populates="agent")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, default="New Conversation")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    status = Column(String, default="active") # "active", "archived"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    assigned_agent = relationship("Agent", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(String, nullable=False) # "user", "agent", "system", "delegated_agent"
    sender_name = Column(String, nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, default="{}") # JSON string containing RAG sources, sub-agent traces, latency
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
    agent = relationship("Agent", back_populates="messages")

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    uploaded_by = Column(String, default="System Admin")
    category = Column(String, default="General Policy")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    trigger_type = Column(String, nullable=False) # e.g., 'on_ticket_created', 'on_lead_received', 'scheduled_daily'
    target_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    config_json = Column(Text, default="{}") # Trigger parameters and action configurations
    status = Column(String, default="active") # "active", "paused"
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    run_count = Column(Integer, default=0)
    last_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    creator = relationship("User", back_populates="workflows")
    target_agent = relationship("Agent")
    runs = relationship("WorkflowRun", back_populates="workflow", cascade="all, delete-orphan")

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    status = Column(String, nullable=False) # "success", "failed", "running"
    input_payload = Column(Text, default="{}")
    output_log = Column(Text, default="")
    executed_at = Column(DateTime, default=datetime.datetime.utcnow)
    duration_ms = Column(Integer, default=0)

    workflow = relationship("Workflow", back_populates="runs")

class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    service_type = Column(String, nullable=False) # "slack", "crm", "erp", "email", "jira"
    status = Column(String, default="connected") # "connected", "disconnected"
    api_key_masked = Column(String, default="••••••••••••")
    webhook_url = Column(String, nullable=True)
    config_json = Column(Text, default="{}")
    last_sync_at = Column(DateTime, default=datetime.datetime.utcnow)

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    agent_id = Column(Integer, nullable=True)
    action_type = Column(String, nullable=False) # "chat_query", "workflow_trigger", "rag_search", "agent_delegation"
    response_time_ms = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    satisfaction_score = Column(Float, nullable=True) # 1-5 rating
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
