from typing import TypedDict,Optional, List,Dict

class TestGraphState(TypedDict):
    endpoints: Dict[str,List[Dict]]
    batched_endpoints: Optional[List[Dict[str,List[Dict]]]]
    test_cases: Optional[list]