from langgraph.graph import END, START, StateGraph

from agent.models import ComplianceCheckAgentState
from agent.steps import get_jurisdictions, parse_pdf

workflow = StateGraph(ComplianceCheckAgentState)
# Graph Nodes
workflow.add_node("parse_pdf", parse_pdf)
workflow.add_node("get_jurisdictions", get_jurisdictions)
workflow.add_edge(START, "parse_pdf")
# Graph Edges
workflow.add_edge("parse_pdf", "get_jurisdictions")
workflow.add_edge("get_jurisdictions", END)

agent = workflow.compile()
