from typing import Dict, Any
import traceback
from ai.test_case_generation.utils.batch_endpoints import batch_endpoints_by_collection
from ai.test_case_generation.graph.TestGraphState import TestGraphState
def EndpointBatcherNode(state:TestGraphState) -> TestGraphState:
    """
    LangGraph node function to batch extracted API endpoints by language and file,
    respecting token limits.
    """
    endpoints = state.get("endpoints", [])
    if not endpoints:
        print("No endpoints found in state for batching.")
        return state

    try:
        batches = batch_endpoints_by_collection(endpoints)
        print(f"Batched endpoints into {len(batches)} batches.")
        return {**state, "batched_endpoints":batches}
    except Exception as e:
        print(f"Error batching endpoints: {e}")
        print(traceback.format_exc())
        return state
