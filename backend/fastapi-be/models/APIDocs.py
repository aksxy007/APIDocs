from pydantic import BaseModel
from typing import Optional, List, Dict

class APIDocs(BaseModel):
    user_id:Optional[str]
    repo_url:str
    branch: Optional[str]
    count: int
    group_count: Dict[str, int] = {}
    api_docs:Dict[str,List[Dict]]