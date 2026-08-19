import json
import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Conversation, Message, Agent, User
from app.schemas import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse
from app.auth import get_current_user
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["Chat & Multi-Agent Conversations"])

@router.get("/conversations", response_model=List[ConversationResponse])
def get_user_conversations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    return conversations

@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(conv_in: ConversationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conversation = Conversation(
        title=conv_in.title or "New Conversation",
        user_id=current_user.id,
        assigned_agent_id=conv_in.agent_id
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    # Insert welcome system message
    assigned = db.query(Agent).filter(Agent.id == conv_in.agent_id).first() if conv_in.agent_id else None
    agent_name = assigned.name if assigned else "Enterprise Multi-Agent Orchestrator"
    
    welcome_msg = Message(
        conversation_id=conversation.id,
        sender_type="system",
        sender_name="System",
        agent_id=conv_in.agent_id,
        content=f"Conversation initialized with **{agent_name}**. Ask any query to receive multi-agent enterprise assistance."
    )
    db.add(welcome_msg)
    db.commit()
    db.refresh(conversation)
    return conversation

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.delete(conversation)
    db.commit()
    return {"status": "success", "message": "Conversation deleted"}

@router.post("/send", response_model=List[MessageResponse])
def send_message(msg_in: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Fetch or create conversation
    if msg_in.conversation_id:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == msg_in.conversation_id, Conversation.user_id == current_user.id)
            .first()
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(
            title=msg_in.content[:30] + "..." if len(msg_in.content) > 30 else msg_in.content,
            user_id=current_user.id,
            assigned_agent_id=msg_in.agent_id
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 2. Record User Message
    user_msg = Message(
        conversation_id=conversation.id,
        sender_type="user",
        sender_name=current_user.full_name,
        agent_id=msg_in.agent_id,
        content=msg_in.content
    )
    db.add(user_msg)
    db.commit()

    # 3. Determine Agent (Manual target or Auto-routed by supervisor)
    active_agents = db.query(Agent).filter(Agent.is_active == True).all()
    if msg_in.agent_id:
        target_agent = db.query(Agent).filter(Agent.id == msg_in.agent_id).first()
    else:
        target_agent = LLMService.route_intent(msg_in.content, active_agents)

    if not target_agent and active_agents:
        target_agent = active_agents[0]

    # Update conversation title if default
    if conversation.title == "New Conversation":
        conversation.title = msg_in.content[:35]
    conversation.assigned_agent_id = target_agent.id
    conversation.updated_at = datetime.datetime.utcnow()
    db.commit()

    # 4. RAG Knowledge Search
    rag_results = RAGService.query_knowledge_base(db, msg_in.content, top_k=3)

    # 5. LLM Response Generation
    llm_output = LLMService.generate_agent_response(
        db=db,
        query=msg_in.content,
        agent=target_agent,
        rag_snippets=rag_results
    )

    metadata = {
        "duration_ms": llm_output["duration_ms"],
        "citations": llm_output.get("citations", []),
        "subagent_traces": llm_output.get("subagent_traces", [])
    }

    # 6. Record Agent Message
    agent_msg = Message(
        conversation_id=conversation.id,
        sender_type="agent",
        sender_name=target_agent.name,
        agent_id=target_agent.id,
        content=llm_output["content"],
        metadata_json=json.dumps(metadata)
    )
    db.add(agent_msg)
    db.commit()

    db.refresh(user_msg)
    db.refresh(agent_msg)

    return [user_msg, agent_msg]
