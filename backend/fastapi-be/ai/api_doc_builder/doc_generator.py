from ai.api_doc_builder.graph.doc_builder_graph import create_doc_builder_graph
from ai.api_doc_builder.graph.BuilderGraphState import BuilderGraphState
from configs.logger import get_custom_logger

logger = get_custom_logger(__name__)

graph = create_doc_builder_graph()

async def invoke_doc_graph(state: BuilderGraphState) -> BuilderGraphState:
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
    
    final_documents = updated_state.get("doc_snippets", [])
    if not final_documents:
        logger.warning("No API Docs available in the state.")

    return updated_state
