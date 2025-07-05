from pydantic import BaseModel
from typing import Optional, List, Dict

class Endpoint(BaseModel):
    """
    Represents an API endpoint with its details.
    """
    user_id: Optional[str] = None
    repo_url = str = None
    branch: Optional[str] = None
    endpoints: List[Dict] = []
    metadata: Optional[Dict] = None