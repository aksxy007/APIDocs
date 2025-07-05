from pydantic import BaseModel
from typing import Optional, List, Dict

class TestCase(BaseModel):
    user_id:Optional[str]
    repo_url:str
    branch: Optional[str]
    count: int
    group_count: Dict[str, int] = {}
    test_cases:List[Dict[str,List[Dict]]]