from ai.api_extractor.graph.graph import create_graph
from ai.api_extractor.graph.GraphState import GraphState
from configs.logger import get_custom_logger

logger = get_custom_logger(__name__)

graph = create_graph()

async def invoke_graph(state: GraphState) -> GraphState:
    """
    Invoke the graph to process backend files and extract OpenAPI endpoints.
    """

    logger.info("Starting graph invocation...")
    try:
        updated_state =await graph.ainvoke(state)
        print(updated_state.keys())
        logger.info("Graph invocation completed successfully.")
    except Exception as e:
        logger.error(f"Graph invocation failed: {e}")
        return state
    
    endpoints = updated_state.get("endpoints", [])
    if not endpoints:
        logger.warning("No endpoints available in the state.")

    return updated_state
