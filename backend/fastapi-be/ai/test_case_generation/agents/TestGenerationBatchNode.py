from typing import List, Dict
from ai.utils.parse_json_response import parse_json_response
from ai.utils.get_llm_response import get_llm_response
from ai.test_case_generation.graph.TestGraphState import TestGraphState
from ai.test_case_generation.prompts.get_test_generation_prompt import get_test_generation_prompt
from configs.logger import get_custom_logger

logger = get_custom_logger(__name__)

def TestGenerationNode(state: TestGraphState) -> TestGraphState:
    """
    Generates test cases for API endpoints from batched collections, passing entire batch to prompt.
    """
    batches = state.get("batched_endpoints", [])
    if not batches:
        logger.warning("No endpoint batches found in the state.")
        return {"test_cases": []}

    logger.info(f"Starting Test Generation from {len(batches)} batches...")

    all_endpoints = []

    for i, batch in enumerate(batches):
        logger.info(f"Processing test batch {i+1}/{len(batches)}...")

        # Assign unique IDs to endpoints across all collections in the batch
        endpoint_count = 0
        for collection_name, endpoints in batch.items():
            logger.info(f"Assigning IDs for collection {collection_name} with {len(endpoints)} endpoints...")
            for ep in endpoints:
                ep["id"] = str((i * 1000) + endpoint_count + 1)  # Ensure unique IDs across batches
                ep["collection"] = collection_name
                endpoint_count += 1
            all_endpoints.extend(endpoints)

        # Generate prompt for the entire batch
        prompt = get_test_generation_prompt([batch])  # Pass the entire batch as a single dictionary

        try:
            system_prompt = "You are an expert at generating test cases for API endpoints"
            response = get_llm_response(prompt, system_prompt)
            if response:
                test_cases = parse_json_response(response)
                logger.info(f"Generated test cases for batch {i+1} with {len(test_cases)} entries.")
                # Assign test cases to endpoints based on ID
                for ep in all_endpoints:
                    _id = ep["id"]
                    ep["test_cases"] = test_cases.get(_id, {
                        "success": [{"payload": {}, "expected_response": {}, "response_code": 0}],
                        "failure": [{"payload": {}, "expected_response": {}, "response_code": 0}]
                    })
            else:
                logger.warning(f"Empty response from LLM for batch {i+1}.")
        except Exception as e:
            logger.error(f"Error processing batch {i+1}: {e}")

    # Group endpoints by collection
    collection_map = {}
    for ep in all_endpoints:
        collection = ep.get("collection", "Unknown")
        collection_map.setdefault(collection, []).append(ep)

    grouped_output = [{k: v} for k, v in collection_map.items()]
    logger.info(f"Finished generating test cases for {len(all_endpoints)} endpoints.")
    return {**state, "test_cases": grouped_output}