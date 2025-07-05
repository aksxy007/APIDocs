from typing import Dict, Any
from configs.logger import get_custom_logger
from ai.api_doc_builder.graph.BuilderGraphState import BuilderGraphState
from ai.api_doc_builder.utils.validate_and_format import validate_and_format_doc

logger = get_custom_logger(__name__)

def ValidateAndFormatDocNode(state: BuilderGraphState) -> Dict[str, Any]:
    """
    A LangGraph node that validates and formats OpenAPI documentation.
    It uses the output from the LLM (stored in `doc_snippets`) and returns the final OpenAPI doc and code snippets.
    """
    
    try:
        logger.info("Starting OpenAPI validation and formatting...")
        doc_snippets = state.get("doc_snippets", [])
        if not doc_snippets:    
            logger.warning("No documentation snippets found in the state.")
            return state
        
        openapi_docs = validate_and_format_doc(doc_snippets)
        final_document = openapi_docs
         
        if not final_document:
            logger.warning("OpenAPI document generation failed or returned empty.")

        return {
            **state,
            "final_document": final_document,
        }

    except Exception as e:
        logger.error(f"Error in ValidateAndFormatDocNode: {e}")
        return state
