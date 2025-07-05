from typing import Dict, List, Optional
from ai.api_extractor.graph.GraphState import GraphState
from configs.logger import get_custom_logger

logger = get_custom_logger(__name__)

import os

def group_endpoints_by_file(endpoints):
    grouped = {}

    for ep in endpoints:
        file_path = ep.get("file")
        if file_path is not None:
            normalized = os.path.normpath(file_path)
            filename = os.path.splitext(os.path.basename(normalized))[0]
            group_name = filename[0].upper() + filename[1:]

            if group_name not in grouped:
                grouped[group_name] = []
            grouped[group_name].append(ep)
    
    return grouped

def MergeEndpointsNode(state:GraphState) -> GraphState:
    """
    Merges endpoints from different languages into a single list.
    """
    python_endpoints = state.get("python_endpoints", [])
    js_endpoints = state.get("js_endpoints", [])
    
    merged_endpoints = python_endpoints + js_endpoints
    
    if not merged_endpoints:
        logger.warning("No endpoints found to merge.")
        return state
    
    logger.info(f"Merged {len(merged_endpoints)} endpoints from Python, JavaScript, and TypeScript.")
    
    # Optionally, group endpoints by file if needed
    grouped_endpoints = group_endpoints_by_file(merged_endpoints)
    
    return {"endpoints": grouped_endpoints}