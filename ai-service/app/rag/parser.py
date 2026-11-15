import re
from typing import List, Dict, Any, Optional

class DocumentParser:
    @staticmethod
    def clean_text(text: str) -> str:
        # Normalize whitespace and strip control characters
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\t', ' ', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()

    @classmethod
    def parse_text(cls, content: str, file_type: str = "txt") -> List[Dict[str, Any]]:
        cleaned = cls.clean_text(content)
        lines = cleaned.split('\n')
        
        sections = []
        current_section = "General"
        current_buffer = []
        
        for line in lines:
            trimmed = line.strip()
            # Detect markdown or text headers
            if trimmed.startswith(("#", "SECTION", "CHAPTER", "ARTICLE")) or (len(trimmed) < 40 and trimmed.isupper() and len(trimmed) > 3):
                if current_buffer:
                    sections.append({
                        "section": current_section,
                        "text": "\n".join(current_buffer).strip()
                    })
                    current_buffer = []
                current_section = trimmed.lstrip("#").strip()
            else:
                if trimmed:
                    current_buffer.append(trimmed)
                    
        if current_buffer:
            sections.append({
                "section": current_section,
                "text": "\n".join(current_buffer).strip()
            })
            
        return sections if sections else [{"section": "Full Document", "text": cleaned}]
