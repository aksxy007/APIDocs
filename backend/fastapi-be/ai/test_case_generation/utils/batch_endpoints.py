from typing import Dict, List
import tiktoken
from dotenv import load_dotenv
import os

load_dotenv()

MAX_TOKENS_PER_TEST_BATCH = int(os.getenv("MAX_TOKENS_PER_TEST_BATCH"))
# Initialize tokenizer for your LLM model (update model name if needed)
encoding = tiktoken.get_encoding("cl100k_base")  # or "gpt-3.5-turbo", etc.

def estimate_tokens(text: str) -> int:
    """Accurately estimate token count using tiktoken."""
    return len(encoding.encode(text))

def batch_endpoints_by_collection(
    collection_to_endpoints: Dict[str, List[Dict]],
    max_tokens_per_batch:int= MAX_TOKENS_PER_TEST_BATCH
) -> List[Dict[str, List[Dict]]]:
    """
    Batches API endpoints grouped by collection into multiple batches
    without exceeding a max token limit per batch.
    """
    batches = []
    current_batch = {}
    current_tokens = 0

    for collection, endpoints in collection_to_endpoints.items():
        total_collection_tokens = sum(estimate_tokens(str(ep)) for ep in endpoints)

        if current_tokens + total_collection_tokens > max_tokens_per_batch:
            if current_batch:
                batches.append(current_batch)
            current_batch = {}
            current_tokens = 0

        current_batch[collection] = endpoints
        current_tokens += total_collection_tokens

    if current_batch:
        batches.append(current_batch)

    return batches
