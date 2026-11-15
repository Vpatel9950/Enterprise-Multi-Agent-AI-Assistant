from typing import List, Dict, Any

class TextChunker:
    @staticmethod
    def chunk_section(
        section_name: str, 
        text: str, 
        chunk_size: int = 250, 
        overlap: int = 40,
        estimated_page: int = 1
    ) -> List[Dict[str, Any]]:
        words = text.split()
        if not words:
            return []
            
        chunks = []
        i = 0
        chunk_idx = 0
        
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            # Approximate page calculation based on word count (approx 350 words per page)
            page_num = estimated_page + (i // 350)
            
            chunks.append({
                "chunk_index": chunk_idx,
                "section": section_name,
                "page_number": page_num,
                "text": chunk_text,
                "word_count": len(chunk_words)
            })
            
            chunk_idx += 1
            i += (chunk_size - overlap)
            
        return chunks
