import re
import math
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import KnowledgeDocument

class RAGService:
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 250, overlap: int = 40) -> List[str]:
        words = text.split()
        chunks = []
        if not words:
            return chunks
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += (chunk_size - overlap)
        return chunks

    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        # Basic token normalization and stop-word filtering
        words = re.findall(r'\w+', text.lower())
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with',
            'by', 'about', 'against', 'between', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'from', 'up', 'down', 'of', 'off', 'over', 'under',
            'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
            'does', 'did', 'can', 'could', 'should', 'would', 'will', 'this', 'that', 'i', 'we'
        }
        return [w for w in words if len(w) > 2 and w not in stopwords]

    @classmethod
    def calculate_similarity(cls, query_words: List[str], chunk_text: str) -> float:
        if not query_words:
            return 0.0
        chunk_words = cls.extract_keywords(chunk_text)
        if not chunk_words:
            return 0.0

        # Term frequency matching with term uniqueness score
        match_count = 0
        for qw in set(query_words):
            if qw in chunk_words:
                match_count += chunk_words.count(qw)

        # Normalized TF-IDF score
        score = match_count / (math.log(len(chunk_words) + 1.0) + 1.0)
        return min(score, 1.0)

    @classmethod
    def query_knowledge_base(cls, db: Session, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        documents = db.query(KnowledgeDocument).all()
        if not documents:
            return []

        query_keywords = cls.extract_keywords(query)
        if not query_keywords:
            return []

        scored_chunks = []
        for doc in documents:
            chunks = cls.chunk_text(doc.content)
            for idx, chunk in enumerate(chunks):
                sim = cls.calculate_similarity(query_keywords, chunk)
                if sim > 0.05:
                    scored_chunks.append({
                        "doc_id": doc.id,
                        "filename": doc.filename,
                        "category": doc.category,
                        "chunk_index": idx,
                        "similarity_score": round(sim, 3),
                        "snippet": chunk
                    })

        scored_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_chunks[:top_k]
