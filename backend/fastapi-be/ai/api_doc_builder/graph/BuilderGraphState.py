from typing import List, Dict, Optional,TypedDict

class BuilderGraphState(TypedDict):
    endpoints: Dict[str, List[Dict]]
    batched_endpoints: List[Dict[str, List[Dict]]] = []
    doc_snippets: List[Dict] = []
    final_document: Optional[Dict] = None
    metrics: Dict = {
        "total_endpoints": 0,
        "total_snippets": 0,
        "execution_time": 0.0
    }