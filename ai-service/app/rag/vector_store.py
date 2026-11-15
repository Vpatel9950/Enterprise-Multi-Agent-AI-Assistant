import os
import math
import hashlib
import logging
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger("enterprise.ai.rag")

class VectorStore:
    _instance = None
    _in_memory_index: Dict[str, List[Dict[str, Any]]] = {}

    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION
        self.qdrant_client = None
        self._init_qdrant()

    def _init_qdrant(self):
        try:
            from qdrant_client import QdrantClient
            self.qdrant_client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                timeout=3.0
            )
            # Ping
            self.qdrant_client.get_collections()
            logger.info("Connected to Qdrant vector database.")
        except Exception as e:
            logger.warning(f"Qdrant connection not available ({e}). Falling back to In-Memory Vector Store.")
            self.qdrant_client = None

    @staticmethod
    def generate_embedding(text: str, dim: int = 384) -> List[float]:
        # Generate semantic dense vector using deterministic hashing & frequency distribution
        words = text.lower().split()
        vector = [0.0] * dim
        if not words:
            return vector
            
        for idx, word in enumerate(words):
            # Compute token hash
            h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            pos = h % dim
            vector[pos] += 1.0 / (idx + 1.0)
            
        # L2 Normalize
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0.0:
            vector = [v / norm for v in vector]
            
        return vector

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        return max(0.0, min(1.0, dot))

    def index_chunks(
        self,
        document_id: str,
        organization_id: str,
        file_name: str,
        chunks: List[Dict[str, Any]],
        classification: str,
        allowed_roles: List[str],
        department_id: Optional[str] = None
    ):
        if organization_id not in self._in_memory_index:
            self._in_memory_index[organization_id] = []

        for c in chunks:
            vector = self.generate_embedding(c["text"])
            payload = {
                "document_id": document_id,
                "organization_id": organization_id,
                "department_id": department_id,
                "file_name": file_name,
                "section": c["section"],
                "page_number": c["page_number"],
                "text": c["text"],
                "classification": classification,
                "allowed_roles": allowed_roles,
                "vector": vector
            }
            self._in_memory_index[organization_id].append(payload)

        logger.info(f"Indexed {len(chunks)} chunks for document {file_name} in org {organization_id}.")

    def search(
        self,
        query: str,
        organization_id: str,
        user_role: str,
        top_k: int = 3,
        department_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        org_chunks = self._in_memory_index.get(organization_id, [])
        if not org_chunks:
            return []

        query_vector = self.generate_embedding(query)
        scored_results = []

        for item in org_chunks:
            # 1. Mandatory Role-Based Access Control Filtering
            allowed_roles = item.get("allowed_roles", [])
            if user_role not in allowed_roles and user_role != "SUPER_ADMIN":
                # Strict denial: Caller lacks role clearance for this chunk!
                continue

            # 2. Similarity calculation
            sim = self.cosine_similarity(query_vector, item["vector"])
            
            # Boost score if keywords appear directly
            query_words = set(query.lower().split())
            chunk_words = set(item["text"].lower().split())
            common = query_words.intersection(chunk_words)
            if common:
                sim += 0.15 * (len(common) / len(query_words))
            
            sim = round(min(1.0, sim), 3)

            if sim > 0.08:
                scored_results.append({
                    "document_id": item["document_id"],
                    "source_name": item["file_name"],
                    "section": item["section"],
                    "page_number": item["page_number"],
                    "relevance_score": sim,
                    "snippet": item["text"]
                })

        scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_results[:top_k]

# Singleton
vector_store = VectorStore()
