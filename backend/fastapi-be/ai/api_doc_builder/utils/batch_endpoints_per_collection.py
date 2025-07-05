from typing import List, Dict
import json
import tiktoken
from dotenv import load_dotenv
import os

load_dotenv()
MAX_TOKENS_PER_DOC_BATCH = int(os.getenv("MAX_TOKENS_PER_DOC_BATCH", 1000))

def estimate_tokens(endpoints: List[Dict], encoding_name: str = "cl100k_base") -> int:
    """
    Estimates the token count for a list of endpoints using tiktoken.
    """
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        endpoints_str = json.dumps(endpoints)
        return len(encoding.encode(endpoints_str))
    except Exception:
        return len(json.dumps(endpoints)) // 4  # Fallback: 1 token ≈ 4 characters

def batch_endpoints(endpoints: Dict[str, List[Dict]], max_token_per_doc_batch: int = MAX_TOKENS_PER_DOC_BATCH) -> List[Dict[str, List[Dict]]]:
    """
    Batches endpoints by collection, ensuring each batch stays under max_token_per_doc_batch.
    """
    result = []
    current_batch = {}
    current_token_count = 0

    for collection_name, collection_endpoints in endpoints.items():
        token_count = estimate_tokens(collection_endpoints)
        if current_token_count + token_count <= max_token_per_doc_batch:
            current_batch[collection_name] = collection_endpoints
            current_token_count += token_count
        else:
            if current_batch:
                result.append(current_batch)
            current_batch = {collection_name: collection_endpoints}
            current_token_count = token_count
    if current_batch:
        result.append(current_batch)

    return result