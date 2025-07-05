from pydantic import BaseModel
from typing import Optional

class EndpointRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = None

    