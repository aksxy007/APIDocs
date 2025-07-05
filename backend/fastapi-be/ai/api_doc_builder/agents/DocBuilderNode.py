from typing import Dict, List
from ai.utils.get_llm_response import get_llm_response
from ai.utils.parse_json_response import parse_json_response
from ai.api_doc_builder.graph.BuilderGraphState import BuilderGraphState
from ai.api_doc_builder.prompts.get_doc_builder_prompt import get_doc_builder_prompt
from configs.logger import get_custom_logger
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from requests.exceptions import RequestException

logger = get_custom_logger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((RequestException, ValueError)),
    before_sleep=lambda retry_state: logger.info(f"Retrying LLM call (attempt {retry_state.attempt_number})...")
)
def generate_snippet_with_llm(batch: Dict[str, List[Dict]]) -> List[Dict]:
    """
    Generates OpenAPI JSON and Markdown snippets for a batch of endpoints using LLM.
    """
    prompt = get_doc_builder_prompt(batch)
    system_prompt = (
        "You are a precise API documentation generator. "
        "Produce valid OpenAPI 3.0 JSON snippets and Markdown code snippets for the provided endpoints. "
        "Ensure logical consistency, unique operationIds across all collections, and domain-specific examples. "
        "Include at least one example per request/response and code snippets in CURL, Python, Node.js, JavaScript, and TypeScript."
    )

    try:
        response = get_llm_response(prompt, system_prompt)
        snippets = parse_json_response(response)
        if not isinstance(snippets, dict):
            raise ValueError(f"Invalid JSON response for batch: {response}")
        # Convert collection-wise snippets to list for compatibility
        snippet_list = []
        for collection_name, paths in snippets.items():
            for path, data in paths.items():
                data["collection_name"] = collection_name  # Add collection metadata
                snippet_list.append({path: data})
        return snippet_list
    except Exception as e:
        logger.error(f"Failed to generate snippets for batch: {e}")
        return []

def DocBuilderNode(state: BuilderGraphState) -> BuilderGraphState:
    """
    Generates OpenAPI and Markdown snippets for each batch of endpoints using LLM.
    """
    batches = state.get("batched_endpoints", [])
    if not batches:
        logger.warning("No endpoint batches found in the state.")
        return {"doc_snippets": [], "metrics": {"total_endpoints": 0, "total_snippets": 0, "execution_time": 0.0}}

    logger.info(f"Starting OpenAPI and Markdown snippet generation for {len(batches)} batches...")

    snippets = []
    state["metrics"] = {
        "total_endpoints": 0,
        "total_snippets": 0,
        "execution_time": 0.0
    }
    start_time = time.time()

    for i, batch in enumerate(batches):
        logger.info(f"Processing batch {i+1}/{len(batches)} with {sum(len(endpoints) for endpoints in batch.values())} endpoints across {len(batch)} collections...")
        try:
            batch_snippets = generate_snippet_with_llm(batch)
            if batch_snippets:
                snippets.extend(batch_snippets)
                state["metrics"]["total_snippets"] += len(batch_snippets)
                state["metrics"]["total_endpoints"] += sum(len(endpoints) for endpoints in batch.values())
                logger.info(f"Generated {len(batch_snippets)} snippets for batch {i+1} across {len(batch)} collections.")
            else:
                logger.warning(f"Empty snippet response for batch {i+1}.")
        except Exception as e:
            logger.error(f"Error processing batch {i+1}: {e}")

    state["metrics"]["execution_time"] = time.time() - start_time
    logger.info(f"Finished generating snippets. Total snippets: {state['metrics']['total_snippets']}, Total endpoints: {state['metrics']['total_endpoints']}")

    return {"doc_snippets": snippets, "metrics": state["metrics"]}