from pydantic import BaseModel
from typing import Optional, List, Dict

class SaveEndpoint(BaseModel):
    user_id: Optional[str] = None
    repo_url: str
    branch: Optional[str] = None
    count: int
    group_count: Dict[str, int] = {}
    endpoints: Dict[str, List[Dict]] = {}
    