from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class DocumentStructure(BaseModel):
    sections: List[Dict[str, Any]]
    html_preview: str

class RewriteRequest(BaseModel):
    section_ids: List[str]
    document_id: str
    knowledge_base_ids: List[str] = []
    custom_instructions: Optional[str] = None

class RewriteResponse(BaseModel):
    rewrites: Dict[str, str]
