import tiktoken
from typing import List, Dict, Optional
from dotenv import load_dotenv
import os

load_dotenv()

MAX_TOKENS_PER_BATCH = int(os.getenv("MAX_TOKENS_PER_BATCH", 8000))

def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in a given text."""
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def prepare_tokenized_chunks(chunks: List[Dict]) -> List[Dict]:
    """Add token count to each chunk if not already present."""
    for chunk in chunks:
        if "tokens" not in chunk:
            chunk["tokens"] = estimate_tokens(chunk.get("code", ""))
    return chunks

def prepare_batches(chunks: List[Dict], max_tokens: int = MAX_TOKENS_PER_BATCH) -> List[List[Dict]]:
    """Batch chunks such that each batch does not exceed max_tokens."""
    tokenized_chunks = prepare_tokenized_chunks(chunks)
    batches_by_language = {}
    chunks_by_language = {}
    
    for chunk in tokenized_chunks:
        lang = chunk.get("language", "unknown")
        if lang not in chunks_by_language:
            chunks_by_language[lang] = []
        chunks_by_language[lang].append(chunk)

    for lang, lang_chunks in chunks_by_language.items():
        current_batch = []
        batches = []
        current_batch = []
        current_tokens = 0
        
        for chunk in lang_chunks:
            chunk_tokens = chunk.get("tokens")

            if current_tokens + chunk_tokens > max_tokens:
                batches.append(current_batch)
                current_batch = [chunk]
                current_tokens = chunk_tokens
            else:
                current_batch.append(chunk)
                current_tokens += chunk_tokens
        
        if current_batch:
            batches.append(current_batch)
        
        batches_by_language[lang] = batches

    return batches_by_language