from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import KnowledgeDocument, User
from app.schemas import DocumentResponse, DocumentCreate
from app.auth import get_current_user, require_admin
from app.services.rag_service import RAGService

router = APIRouter(prefix="/rag", tags=["Knowledge Base & RAG Engine"])

@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    docs = db.query(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).all()
    return docs

@router.post("/documents", response_model=DocumentResponse)
def create_document(doc_in: DocumentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    words = doc_in.content.split()
    chunks = RAGService.chunk_text(doc_in.content)
    
    doc = KnowledgeDocument(
        filename=doc_in.filename,
        file_type="txt",
        content=doc_in.content,
        word_count=len(words),
        chunk_count=len(chunks),
        uploaded_by=current_user.full_name,
        category=doc_in.category or "General Policy"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.post("/upload")
async def upload_document_file(
    file: UploadFile = File(...),
    category: str = Form("General Policy"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    content_bytes = await file.read()
    try:
        text_content = content_bytes.decode("utf-8")
    except Exception:
        text_content = str(content_bytes)

    words = text_content.split()
    chunks = RAGService.chunk_text(text_content)

    doc = KnowledgeDocument(
        filename=file.filename,
        file_type=file.filename.split(".")[-1] if "." in file.filename else "txt",
        content=text_content,
        word_count=len(words),
        chunk_count=len(chunks),
        uploaded_by=current_user.full_name,
        category=category
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return DocumentResponse.from_orm(doc)

@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"status": "success", "message": "Document deleted"}

@router.post("/search")
def search_knowledge_base(query_data: Dict[str, Any], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = query_data.get("query", "")
    results = RAGService.query_knowledge_base(db, query, top_k=5)
    return {"query": query, "matches_found": len(results), "results": results}
