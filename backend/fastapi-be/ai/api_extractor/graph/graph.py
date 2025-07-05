from langgraph.graph import StateGraph,END

from ai.api_extractor.graph.GraphState import GraphState

from ai.api_extractor.nodes.LoadbackendFiles import LoadBackendFilesNode
from ai.api_extractor.nodes.FilesChunker import FilesChunkerNode
from ai.api_extractor.nodes.Merger import MergeEndpointsNode

from ai.api_extractor.agents.ExtractOpenAPIPythonNode import ExctractOpenAPIPythonNode
from ai.api_extractor.agents.ExtractOpenAPIJSNode import ExtractOpenAPIJSNode

def create_graph() -> StateGraph:
    """Create the graph for loading and chunking backend files."""
    workflow = StateGraph(GraphState)
    # Define the graph structure
    workflow.add_node("load_files",LoadBackendFilesNode)
    workflow.add_node("chunk_files",FilesChunkerNode)
    workflow.add_node("extract_python_endpoints", ExctractOpenAPIPythonNode)  # Placeholder for future nodes
    workflow.add_node("extract_js_endpoints", ExtractOpenAPIJSNode)
    workflow.add_node("merger", MergeEndpointsNode)  # Placeholder for the end of the workflow
        
    workflow.set_entry_point("load_files")
    workflow.add_edge("load_files", "chunk_files")
    workflow.add_edge("chunk_files", "extract_python_endpoints")
    workflow.add_edge("chunk_files", "extract_js_endpoints")  # Assuming both Python and JS endpoints are extracted from the same chunked files
    workflow.add_edge("extract_python_endpoints","merger")  # End of the workflow
    workflow.add_edge("extract_js_endpoints","merger")  # End of the workflow
    workflow.add_edge("merger", END)  # Final end node
    
    graph = workflow.compile()
    return graph