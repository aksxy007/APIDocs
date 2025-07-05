from langgraph.graph import StateGraph,END

from ai.api_doc_builder.graph.BuilderGraphState import BuilderGraphState
from ai.api_doc_builder.nodes.EndpointsBatcherNode import EndpointBatcherNode
from ai.api_doc_builder.nodes.ValidateAndFormatNode import ValidateAndFormatDocNode
from ai.api_doc_builder.agents.DocBuilderNode import DocBuilderNode
from ai.api_doc_builder.agents.DocGenNode import DocGeneratorNode

def create_doc_builder_graph() -> StateGraph:
    """Create the graph for loading and chunking backend files."""
    workflow = StateGraph(BuilderGraphState)
    # Define the graph structure
    
    workflow.add_node("batch_endpoints", EndpointBatcherNode)
    # workflow.add_node("generate_snippets", DocBuilderNode)
    workflow.add_node("generate_snippets", DocGeneratorNode)
    # workflow.add_node("validate_and_format", ValidateAndFormatDocNode)
    
    workflow.set_entry_point("batch_endpoints")
    
    workflow.add_edge("batch_endpoints", "generate_snippets")   
    # workflow.add_edge("generate_snippets", "validate_and_format")
    # workflow.add_edge("validate_and_format", END)  # Final end node
    workflow.add_edge("generate_snippets", END)  # Final end node
    
    graph = workflow.compile()
    return graph
    