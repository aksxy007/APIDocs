from typing import List, Dict
from ai.utils.parse_json_response import parse_json_response
from ai.utils.get_llm_response import get_llm_response
from ai.test_case_generation.graph.TestGraphState import TestGraphState
from ai.test_case_generation.prompts.get_test_generation_prompt import get_test_generation_prompt
from configs.logger import get_custom_logger
import uuid
import time
import json
import concurrent.futures
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from requests.exceptions import RequestException

logger = get_custom_logger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((RequestException, ValueError)),
    before_sleep=lambda retry_state: logger.info(f"Retrying LLM call (attempt {retry_state.attempt_number})...")
)
def get_llm_response_with_retry(prompt: str, system_prompt: str) -> str:
    """Wrapper for get_llm_response with retry logic."""
    response = get_llm_response(prompt, system_prompt)
    if not response:
        raise ValueError("Empty response from LLM")
    return response

def validate_test_case(case: Dict, operation: str, collection_name: str, endpoint_id: str) -> bool:
    """Validate a single test case for required fields and data consistency."""
    required_fields = ["payload", "expected_response", "response_code"]
    if not all(field in case for field in required_fields):
        logger.warning(f"Missing required fields in test case for {operation} (ID: {endpoint_id}, {collection_name}): {case}")
        return False
    if case["response_code"] == 0:
        logger.warning(f"Invalid response_code in test case for {operation} (ID: {endpoint_id}, {collection_name}): {case}")
        return False
    if operation in ["create", "update", "register", "login_success", "login_failure"]:
        if not isinstance(case["payload"], dict) or not case["payload"]:
            logger.warning(f"Invalid payload in test case for {operation} (ID: {endpoint_id}, {collection_name}): {case}")
            return False
    return True

def TestGenerationNode(state: TestGraphState) -> TestGraphState:
    """
    Generates test cases for API endpoints from batched collections using an LLM.
    Strictly enforces CRUD/auth order and ensures logical consistency.
    """
    batches = state.get("batched_endpoints", [])
    if not batches:
        logger.warning("No endpoint batches found in the state.")
        return {"test_cases": [], "metrics": {"total_endpoints": 0, "total_test_cases": 0}}

    logger.info(f"Starting test case generation for {len(batches)} batches...")
    start_time = time.time()

    all_endpoints = []
    expected_ids = set()
    metrics = {"total_endpoints": 0, "total_test_cases": 0, "success_cases": 0, "failure_cases": 0}

    crud_order = ["create", "read_after_create", "update", "read_after_update", "delete", "read_after_delete", "list", "other"]
    auth_order = ["register", "login_success", "login_failure", "list", "other"]

    def process_batch(batch: Dict, batch_idx: int) -> List[Dict]:
        batch_endpoints = []
        for collection_name, endpoints in batch.items():
            logger.info(f"Processing collection {collection_name} with {len(endpoints)} endpoints in batch {batch_idx+1}...")
            is_auth_collection = collection_name.lower() in ["login", "register", "auth"]
            order = auth_order if is_auth_collection else crud_order

            # Assign unique IDs and validate endpoints
            endpoint_map = {}
            for idx, ep in enumerate(endpoints):
                ep["id"] = str(uuid.uuid4())
                ep["collection"] = collection_name
                expected_ids.add(ep["id"])
                endpoint_map[ep["id"]] = ep
                metrics["total_endpoints"] += 1

            # Generate prompt
            prompt = get_test_generation_prompt([{collection_name: endpoints}])
            system_prompt = (
                "You are an expert at generating test cases for API endpoints. "
                "Generate comprehensive test cases for ALL provided endpoints, using unique endpoint IDs. "
                f"Follow the EXACT order: {order} for {'auth' if is_auth_collection else 'non-auth'} collections. "
                "Ensure logical consistency with the same resource ID or credentials across operations. "
                "Generate at least 3 success and 5 failure cases per endpoint, including edge cases (e.g., max/min values, special characters, empty strings) "
                "and failure cases (e.g., missing fields, invalid data types, rate limits, invalid headers, unauthorized access). "
                "For list endpoints, include pagination tests with varied limit/offset/sort parameters. "
                "Use realistic, domain-specific data (e.g., valid emails, positive prices, unique usernames). "
                "Return test cases in JSON format with unique IDs, operation, payload, expected_response, and response_code."
            )

            try:
                response = get_llm_response_with_retry(prompt, system_prompt)
                test_cases = parse_json_response(response)
                if not test_cases or not isinstance(test_cases, dict):
                    logger.error(f"Invalid JSON response for collection {collection_name} in batch {batch_idx+1}: {response}")
                    for ep in endpoints:
                        logger.error(f"Missing test cases for endpoint ID {ep['id']} ({ep.get('operation', 'unknown')}, {ep.get('path', 'unknown')})")
                        ep["test_cases"] = {"success": [], "failure": []}
                        batch_endpoints.append(ep)
                    continue

                # Ensure all expected operations are present
                present_ops = {tc.get("operation") for tc in test_cases.values()}
                missing_ops = set(order[:-1]) - present_ops  # Exclude 'other'
                if missing_ops:
                    logger.warning(f"Missing operations {missing_ops} for collection {collection_name}. Generating placeholders.")
                    for op in missing_ops:
                        placeholder_id = str(uuid.uuid4())
                        test_cases[placeholder_id] = {
                            "operation": op,
                            "success": [],
                            "failure": [{"payload": {}, "expected_response": {"error": f"Placeholder for missing {op}"}, "response_code": 400}]
                        }

                # Validate and assign test cases
                resource_id = None
                credentials = None
                ordered_test_cases = {}
                for op in order:
                    for _id, tc in test_cases.items():
                        if tc.get("operation") != op:
                            continue
                        ep = endpoint_map.get(_id.split("_")[0], {})
                        if not ep:
                            logger.warning(f"No endpoint found for ID {_id} in collection {collection_name}.")
                            continue

                        # Validate test cases
                        for case_type in ["success", "failure"]:
                            tc[case_type] = [
                                case for case in tc[case_type]
                                if validate_test_case(case, op, collection_name, _id)
                            ]
                            metrics[f"{case_type}_cases"] += len(tc[case_type])

                        # Dependency management
                        if op in ["create", "register"] and tc["success"]:
                            resource_id = tc["success"][0]["expected_response"].get("id") or str(uuid.uuid4())
                            if is_auth_collection:
                                credentials = tc["success"][0]["payload"]
                        elif op in ["read_after_create", "update", "read_after_update", "delete", "read_after_delete"] and tc["success"]:
                            if resource_id:
                                for case in tc["success"]:
                                    case["payload"]["id"] = resource_id
                        elif op == "list" and tc["success"]:
                            if resource_id:
                                for case in tc["success"]:
                                    if "items" in case["expected_response"]:
                                        for item in case["expected_response"]["items"]:
                                            item["id"] = resource_id
                        elif op == "login_success" and tc["success"]:
                            if credentials:
                                for case in tc["success"]:
                                    case["payload"] = credentials
                        elif op == "login_failure" and tc["failure"]:
                            if credentials:
                                for case in tc["failure"]:
                                    if "username" in case["payload"]:
                                        case["payload"]["username"] = credentials.get("username")

                        if tc["success"] or tc["failure"]:
                            ordered_test_cases[_id] = tc
                            ep["test_cases"] = tc
                            batch_endpoints.append(ep)
                            metrics["total_test_cases"] += len(tc["success"]) + len(tc["failure"])

                if not ordered_test_cases:
                    logger.error(f"No valid test cases generated for collection {collection_name}.")
                    for ep in endpoints:
                        ep["test_cases"] = {"success": [], "failure": []}
                        batch_endpoints.append(ep)

                logger.info(f"Generated {len(ordered_test_cases)} valid test cases for collection {collection_name} in batch {batch_idx+1}.")

            except Exception as e:
                logger.error(f"Error processing collection {collection_name} in batch {batch_idx+1}: {e}")
                for ep in endpoints:
                    ep["test_cases"] = {"success": [], "failure": []}
                    batch_endpoints.append(ep)

        return batch_endpoints

    # Parallel processing of batches
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_batch = {executor.submit(process_batch, batch, i): i for i, batch in enumerate(batches)}
        for future in concurrent.futures.as_completed(future_to_batch):
            batch_idx = future_to_batch[future]
            try:
                all_endpoints.extend(future.result())
            except Exception as e:
                logger.error(f"Batch {batch_idx+1} failed: {e}")

    # Group endpoints by collection
    collection_map = {}
    for ep in all_endpoints:
        collection = ep.get("collection", "Unknown")
        collection_map.setdefault(collection, []).append(ep)

    # Ensure output follows the specified order
    grouped_output = []
    for collection_name, endpoints in collection_map.items():
        is_auth_collection = collection_name.lower() in ["login", "register", "auth"]
        order = auth_order if is_auth_collection else crud_order
        ordered_endpoints = sorted(
            endpoints,
            key=lambda ep: order.index(ep["test_cases"].get("operation", "other"))
        )
        grouped_output.append({collection_name: ordered_endpoints})

    metrics["execution_time"] = time.time() - start_time
    logger.info(f"Finished generating {metrics['total_test_cases']} test cases for {metrics['total_endpoints']} endpoints in {metrics['execution_time']:.2f} seconds.")
    logger.info(f"Metrics: {metrics}")
    return {**state, "test_cases": grouped_output, "metrics": metrics}