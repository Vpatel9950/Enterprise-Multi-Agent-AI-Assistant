import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId
from app.db.mongo import MongoDBManager, to_object_id
from app.rag.parser import DocumentParser
from app.rag.chunker import TextChunker
from app.rag.vector_store import vector_store

class RAGService:
    @classmethod
    def process_and_index_document(
        cls,
        organization_id: str,
        file_name: str,
        content: str,
        file_type: str = "txt",
        classification: str = "INTERNAL",
        allowed_roles: List[str] = None,
        department_id: Optional[str] = None,
        uploaded_by: Optional[str] = None,
        uploaded_by_name: Optional[str] = None
    ) -> Dict[str, Any]:
        if allowed_roles is None:
            allowed_roles = ["EMPLOYEE", "MANAGER", "ORG_ADMIN", "SUPER_ADMIN"]

        # Parse & Chunk
        sections = DocumentParser.parse_text(content, file_type=file_type)
        all_chunks = []
        for sec in sections:
            sec_chunks = TextChunker.chunk_section(
                section_name=sec["section"],
                text=sec["text"],
                chunk_size=200,
                overlap=30
            )
            all_chunks.extend(sec_chunks)

        # Store in MongoDB
        doc_record = {
            "organizationId": to_object_id(organization_id),
            "departmentId": to_object_id(department_id),
            "fileName": file_name,
            "fileType": file_type.lower(),
            "fileSize": len(content.encode('utf-8')),
            "storagePath": f"/storage/{organization_id}/{file_name}",
            "contentPreview": content[:500] + "..." if len(content) > 500 else content,
            "fullContent": content,  # Store full text for rich RAG indexing on restart
            "chunkCount": len(all_chunks),
            "vectorCollection": "enterprise_kb_vectors",
            "classification": classification,
            "allowedRoles": allowed_roles,
            "uploadedBy": to_object_id(uploaded_by) if uploaded_by else None,
            "uploadedByName": uploaded_by_name or "System",
            "status": "INDEXED",
            "errorMessage": None,
            "createdAt": datetime.datetime.utcnow(),
            "updatedAt": datetime.datetime.utcnow()
        }

        insert_res = MongoDBManager.uploaded_documents().insert_one(doc_record)
        doc_id = str(insert_res.inserted_id)

        # Index in Vector Store
        vector_store.index_chunks(
            document_id=doc_id,
            organization_id=organization_id,
            file_name=file_name,
            chunks=all_chunks,
            classification=classification,
            allowed_roles=allowed_roles,
            department_id=department_id
        )

        return {
            "document_id": doc_id,
            "file_name": file_name,
            "chunks_indexed": len(all_chunks),
            "status": "INDEXED"
        }

    @classmethod
    def query(
        cls,
        query: str,
        organization_id: str,
        user_role: str,
        top_k: int = 3,
        department_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # Ensure documents from MongoDB are indexed in the vector store
        cls.ensure_synced_from_mongodb(organization_id)
        
        # Execute query with strict permission check
        return vector_store.search(
            query=query,
            organization_id=organization_id,
            user_role=user_role,
            top_k=top_k,
            department_id=department_id
        )

    @classmethod
    def ensure_synced_from_mongodb(cls, organization_id: str):
        # Sync documents from MongoDB if index is empty
        if organization_id not in vector_store._in_memory_index or not vector_store._in_memory_index[organization_id]:
            docs = list(MongoDBManager.uploaded_documents().find({
                "organizationId": to_object_id(organization_id),
                "status": "INDEXED"
            }))
            for d in docs:
                # Prefer fullContent (rich seed data), fall back to contentPreview
                content = d.get("fullContent") or d.get("contentPreview", "")
                if content:
                    sections = DocumentParser.parse_text(content, d.get("fileType", "txt"))
                    chunks = []
                    for s in sections:
                        chunks.extend(TextChunker.chunk_section(s["section"], s["text"]))
                    vector_store.index_chunks(
                        document_id=str(d["_id"]),
                        organization_id=organization_id,
                        file_name=d["fileName"],
                        chunks=chunks,
                        classification=d.get("classification", "INTERNAL"),
                        allowed_roles=d.get("allowedRoles", ["EMPLOYEE", "MANAGER", "ORG_ADMIN", "SUPER_ADMIN"]),
                        department_id=str(d["departmentId"]) if d.get("departmentId") else None
                    )
