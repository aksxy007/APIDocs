from ai.api_extractor.graph.GraphState import GraphState
from ai.api_extractor.prompts.get_js_extraction_prompt import get_js_extraction_prompt
from ai.utils.get_llm_response import get_llm_response
from ai.utils.parse_json_response import parse_json_response
from configs.logger import get_custom_logger

logger = get_custom_logger(__name__)

def ExtractOpenAPIJSNode(state: GraphState) -> GraphState:
    """
    Extracts OpenAPI definitions from JavaScript/TypeScript files in the repo,
    specifically Express.js or similar APIs.
    """

    batches = state.get("chunk_batches", {})
    if not batches:
        logger.warning("No chunk batches found in the state.")
        return {"js_endpoints": []}

    js_batches = batches.get("javascript", []) + batches.get("typescript", [])
    if not js_batches:
        logger.warning("No JavaScript or TypeScript batches found.")
        return {"js_endpoints": []}

    logger.info(f"Starting JS/TS OpenAPI extraction from {len(js_batches)} batches...")

    all_endpoints = []

    for i, batch in enumerate(js_batches):
        logger.info(f"Processing JS/TS batch {i+1}/{len(js_batches)} with {len(batch)} chunks...")

        prompt = get_js_extraction_prompt(batch)

        try:
            system_prompt = "You are an expert in reading backend code and extracting API endpoints."
            response = get_llm_response(prompt,system_prompt)
            # if i==0:
            #     print("LLM response", response)
            if response:
                endpoints = parse_json_response(response)
                logger.info(f"Extracted {len(endpoints)} endpoints from batch {i+1}.")
                all_endpoints.extend(endpoints)
            else:
                logger.warning(f"Empty response from LLM for batch {i+1}.")

        except Exception as e:
            logger.error(f"Error processing batch {i+1}: {e}")

    logger.info(f"Finished extracting JS endpoints. Total found: {len(all_endpoints)}")
    return {"js_endpoints": all_endpoints}
