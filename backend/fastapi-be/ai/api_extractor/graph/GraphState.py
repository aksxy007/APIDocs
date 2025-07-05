from typing import List, Dict, Optional,TypedDict

class GraphState(TypedDict):
    repo_url:str
    branch: Optional[str] = None
    repo_path: Optional[str] = None
    backend_files: Optional[List[Dict]] = None
    chunks: Optional[List[Dict]] = None
    chunk_batches:Optional[Dict[str, List[Dict]]] = None
    python_endpoints: Optional[List[Dict]] = None
    js_endpoints: Optional[List[Dict]] = None  
    endpoints: Optional[List[Dict]] = None 