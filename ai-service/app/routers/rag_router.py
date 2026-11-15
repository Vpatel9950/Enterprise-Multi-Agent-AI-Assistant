from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.models.schemas import DocumentIndexRequest, RAGQueryRequest
from app.db.mongo import MongoDBManager, to_object_id, serialize_doc
from app.rag.service import RAGService
from app.routers.chat_router import get_current_user_context

router = APIRouter(prefix="/rag", tags=["Knowledge Base & RAG Engine"])

@router.get("/documents")
def list_documents(user_ctx: Dict[str, Any] = Depends(get_current_user_context)):
    org_oid = to_object_id(user_ctx["organization_id"])
    docs = list(MongoDBManager.uploaded_documents().find(
        {"organizationId": org_oid},
        {"fullContent": 0}  # exclude fullContent from list (too large)
    ).sort("createdAt", -1))
    return [serialize_doc(d) for d in docs]

@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    user_ctx: Dict[str, Any] = Depends(get_current_user_context)
):
    if user_ctx["user_role"] not in ["ORG_ADMIN", "SUPER_ADMIN", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Delete requires Manager or Admin clearance")
    org_oid = to_object_id(user_ctx["organization_id"])
    doc_oid = to_object_id(document_id)
    result = MongoDBManager.uploaded_documents().delete_one({"_id": doc_oid, "organizationId": org_oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "document_id": document_id}

@router.post("/index")
def index_document(
    req: DocumentIndexRequest,
    user_ctx: Dict[str, Any] = Depends(get_current_user_context)
):
    if user_ctx["user_role"] not in ["ORG_ADMIN", "SUPER_ADMIN", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Document indexing requires Manager or Admin clearance")

    res = RAGService.process_and_index_document(
        organization_id=user_ctx["organization_id"],
        file_name=req.file_name,
        content=req.content,
        file_type=req.file_type,
        classification=req.classification,
        allowed_roles=req.allowed_roles,
        department_id=req.department_id,
        uploaded_by=user_ctx["user_id"],
        uploaded_by_name=user_ctx["user_name"]
    )
    return res

@router.post("/upload")
async def upload_document_file(
    file: UploadFile = File(...),
    classification: str = Form("INTERNAL"),
    allowed_roles: str = Form("EMPLOYEE,MANAGER,ORG_ADMIN,SUPER_ADMIN"),
    user_ctx: Dict[str, Any] = Depends(get_current_user_context)
):
    if user_ctx["user_role"] not in ["ORG_ADMIN", "SUPER_ADMIN", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Upload requires Manager or Admin clearance")

    content_bytes = await file.read()
    try:
        text_content = content_bytes.decode("utf-8")
    except Exception:
        text_content = str(content_bytes)

    roles_list = [r.strip() for r in allowed_roles.split(",") if r.strip()]
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "txt"

    res = RAGService.process_and_index_document(
        organization_id=user_ctx["organization_id"],
        file_name=file.filename,
        content=text_content,
        file_type=file_ext,
        classification=classification,
        allowed_roles=roles_list,
        uploaded_by=user_ctx["user_id"],
        uploaded_by_name=user_ctx["user_name"]
    )
    return res

@router.post("/query")
def test_rag_query(
    req: RAGQueryRequest,
    user_ctx: Dict[str, Any] = Depends(get_current_user_context)
):
    results = RAGService.query(
        query=req.query,
        organization_id=user_ctx["organization_id"],
        user_role=user_ctx["user_role"],
        top_k=req.top_k,
        department_id=req.department_id
    )
    return {
        "query": req.query,
        "caller_role": user_ctx["user_role"],
        "matches_count": len(results),
        "results": results
    }
