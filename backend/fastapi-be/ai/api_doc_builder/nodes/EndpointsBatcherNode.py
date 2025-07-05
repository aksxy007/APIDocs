from typing import Dict, List
from ai.api_doc_builder.graph.BuilderGraphState import BuilderGraphState
from ai.api_doc_builder.utils.batch_endpoints_per_collection import batch_endpoints
from configs.logger import get_custom_logger

logger = get_custom_logger(__name__)

def EndpointBatcherNode(state: BuilderGraphState) -> BuilderGraphState:
    """
    Batches endpoints by collection, ensuring each batch stays under MAX_TOKENS_PER_DOC_BATCH.
    Returns a plain dict merged with batched_endpoints.
    """
    try:
        logger.info("Batching endpoints by collection...")
        batched_endpoints = batch_endpoints(state["endpoints"])
        logger.info(f"Created {len(batched_endpoints)} batches from {len(state['endpoints'])} collections.")
        return {**state, "batched_endpoints": batched_endpoints}
    except Exception as e:
        logger.error(f"Error during batching endpoints: {e}")
        return state
