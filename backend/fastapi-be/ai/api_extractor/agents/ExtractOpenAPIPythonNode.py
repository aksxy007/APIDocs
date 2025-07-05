from ai.utils.get_llm_response import get_llm_response
from ai.api_extractor.graph.GraphState import GraphState
from ai.api_extractor.prompts.get_fastapi_extraction_prompt import get_fastapi_extraction_prompt
from ai.utils.parse_json_response import parse_json_response
from configs.logger import get_custom_logger

logger = get_custom_logger(__name__)

def ExctractOpenAPIPythonNode(state: GraphState):
    """
    Extracts OpenAPI-style FastAPI endpoints from Python backend chunks.
    
    Args:
        state (GraphState): The graph state containing chunk batches.
        
    Returns:
        Dict: A dictionary with the key "python_endpoints" and list of extracted endpoints.
    """
    batches = state.get("chunk_batches", {})
    if not batches:
        logger.warning("No chunk batches found in the state.")
        return {"python_endpoints": []}
    
    python_batches = batches.get("python", [])
    if not python_batches:
        logger.warning("No Python batches found in chunk_batches.")
        return {"python_endpoints": []}

    logger.info(f"Starting OpenAPI extraction for {len(python_batches)} Python batches...")

    all_endpoints = []

    for i, batch in enumerate(python_batches):
        logger.info(f"Processing Python batch {i+1}/{len(python_batches)} with {len(batch)} chunks...")
        
        prompt = get_fastapi_extraction_prompt(batch)
        system_prompt = "You are an expert in reading backend code and extracting API endpoints."

        try:
            response = get_llm_response(prompt,system_prompt)
            # if i==1:
            # print(f"Response from Batch-{i+1}: {response}")

            if response:
                endpoints = parse_json_response(response)
                logger.info(f"Extracted {len(endpoints)} endpoints from batch {i+1}.")
                all_endpoints.extend(endpoints)
            else:
                logger.warning(f"Empty response content from LLM for batch {i+1}.")

        except Exception as e:
            logger.error(f"Error processing batch {i+1}: {e}")

    logger.info(f"Finished extracting. Total endpoints found: {len(all_endpoints)}")
    return {"python_endpoints": all_endpoints}
