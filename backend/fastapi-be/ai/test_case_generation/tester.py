from ai.test_case_generation.graph.test_graph import create_test_graph
from ai.test_case_generation.graph.TestGraphState import TestGraphState
import traceback
from configs.logger import get_custom_logger

logger = get_custom_logger(__name__)

test_graph = create_test_graph()

async def invoke_graph(state: TestGraphState) -> TestGraphState:
    """
    Invoke the graph to process backend files and extract OpenAPI endpoints.
    """

    logger.info("Starting graph invocation...")
    try:
        updated_state =await test_graph.ainvoke(state)
        logger.info("Graph invocation completed successfully.")
    except Exception as e:
        logger.error(f"Graph invocation failed: {e}")
        return state
    
    endpoints = updated_state.get("batched_endpoints", [])
    if not endpoints:
        logger.warning("No endpoints available in the state.")

    return updated_state
