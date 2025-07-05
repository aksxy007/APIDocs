from pydantic import BaseModel
from typing import Optional,List, Dict

class APIDocsRequest(BaseModel):
    """
    Represents a request for test generation.
    """
    user_id: Optional[str] = None
    repo_url: str
    branch: Optional[str] = None