import uuid
import time
from typing import Dict, List
from ai.utils.get_llm_response import get_llm_response
from ai.utils.parse_json_response import parse_json_response
from ai.api_doc_builder.prompts.get_code_generation_prompt import get_code_snippets_prompt
from ai.api_doc_builder.graph.BuilderGraphState import BuilderGraphState
from configs.logger import get_custom_logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from requests.exceptions import RequestException

logger = get_custom_logger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((RequestException, ValueError)),
    before_sleep=lambda retry_state: logger.info(f"Retrying LLM call (attempt {retry_state.attempt_number})...")
)
def generate_snippet_with_llm(batch: Dict[str, List[Dict]]) -> Dict[str, Dict]:
    prompt = get_code_snippets_prompt(batch)
    system_prompt = (
        "You are a precise API documentation generator. "
        "Only generate code_snippets (curl, python, js, ts, php) for the given endpoints. "
        "Preserve their IDs, do not modify the structure."
    )

    try:
        response = get_llm_response(prompt, system_prompt)
        parsed = parse_json_response(response)
        return parsed if isinstance(parsed, dict) else {}
    except Exception as e:
        logger.error(f"Failed to generate snippets: {e}")
        return {}

def DocGeneratorNode(state: BuilderGraphState) -> BuilderGraphState:
    batches = state.get("batched_endpoints", [])
    if not batches:
        logger.warning("No batches to process.")
        return state

    logger.info(f"Starting DocGeneratorNode with {len(batches)} batches...")

    state["metrics"] = {
        "total_endpoints": 0,
        "total_snippets": 0,
        "execution_time": 0.0
    }

    doc_snippets: Dict[str, List[Dict]] = {}
    start = time.time()

    for i, batch in enumerate(batches):
        logger.info(f"Processing batch {i + 1}/{len(batches)}...")
        enriched_batch = {}

        for collection_name, endpoints in batch.items():
            enriched_endpoints = []
            for ep in endpoints:
                ep_id = str(uuid.uuid4())
                ep["id"] = ep_id
                ep["collection"] = collection_name
                enriched_endpoints.append(ep)
                state["metrics"]["total_endpoints"] += 1
            enriched_batch[collection_name] = enriched_endpoints

        snippet_response = generate_snippet_with_llm(enriched_batch)

        if not snippet_response:
            logger.warning(f"No snippets generated for batch {i + 1}.")
            continue

        for collection_name, endpoints in enriched_batch.items():
            if collection_name not in doc_snippets:
                doc_snippets[collection_name] = []

            for ep in endpoints:
                ep_id = ep["id"]
                if ep_id not in snippet_response:
                    logger.warning(f"No snippets found for endpoint ID {ep_id} in collection {collection_name}.")
                    continue
                
                code_snips = snippet_response.get(ep_id, {})

                # Attach as: { "path": ..., "code_snippets": {...} }
                doc_snippets[collection_name].append({
                    **ep,
                    "code_snippets": {
                        "Bash": code_snips.get("bash", ""),
                        "Python": code_snips.get("python", ""),
                        "Javascript": code_snips.get("javascript", ""),
                        "Typescript": code_snips.get("typescript", ""),
                        "PHP": code_snips.get("php", "")
                    }
                })

                state["metrics"]["total_snippets"] += 1

    state["metrics"]["execution_time"] = time.time() - start
    state["doc_snippets"] = doc_snippets

    logger.info(
        f"Finished generating {state['metrics']['total_snippets']} snippets "
        f"for {state['metrics']['total_endpoints']} endpoints in {state['metrics']['execution_time']:.2f}s."
    )

    return state
