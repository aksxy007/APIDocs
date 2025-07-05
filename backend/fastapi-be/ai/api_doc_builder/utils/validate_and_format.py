from typing import Dict, List
from configs.logger import get_custom_logger

logger = get_custom_logger(__name__)

def validate_and_format_doc(snippets: List[Dict]) -> Dict[str, Dict]:
    """
    Formats LLM-generated OpenAPI snippets into a collection-wise grouped structure.
    Each endpoint method includes OpenAPI data and code snippets.
    """

    if not snippets:
        logger.warning("No documentation snippets to process.")
        return {}

    collections: Dict[str, Dict[str, Dict[str, Dict]]] = {}

    for snippet in snippets:
        for path, data in snippet.items():
            collection_name = data.get("collection_name", "Unknown")
            openapi_snippet = data.get("openapi_snippet", {})
            path_snippets = data.get("code_snippets", {})

            if collection_name not in collections:
                collections[collection_name] = {}

            if path not in collections[collection_name]:
                collections[collection_name][path] = {}

            for method, method_data in openapi_snippet.items():
                # Embed code snippets directly into method
                method_data["code_snippets"] = path_snippets
                collections[collection_name][path][method] = method_data

    return collections
