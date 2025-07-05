from langgraph.graph import StateGraph,END

from ai.test_case_generation.nodes.EndpointBatcherNode import EndpointBatcherNode
from ai.test_case_generation.agents.TestGenerationNode import TestGenerationNode
from ai.test_case_generation.graph.TestGraphState import TestGraphState


def create_test_graph():
    workflow = StateGraph(TestGraphState)
    
    workflow.add_node("batcher",EndpointBatcherNode)
    workflow.add_node("test_case_generator",TestGenerationNode)
    
    workflow.set_entry_point("batcher")
    workflow.add_edge("batcher","test_case_generator")
    workflow.add_edge("test_case_generator",END)    
    # workflow.add_edge("batcher",END)
    
    test_graph = workflow.compile()
    
    return test_graph