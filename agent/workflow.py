from langgraph.graph import END, START, StateGraph

from agent.models import ComplianceCheckAgentState
from agent.steps import get_jurisdictions, parse_pdf

# ComplianceCheckAgent
# 1. parse pdf file extract text from each page
# 2. extract jurisdictions from each page, then deduplicate jurisdictions and substances within them
# 3. check compliance of the part for each jurisdiction
#   - DFS approach
#   - Find the 1:1 mapping between jurisdiction and part substances
#   - Halt when non compliant part is reached
#   - Ask user to continue checking or generate report of the seen parts
# 4. generate the compliance report md

workflow = StateGraph(ComplianceCheckAgentState)
# Graph Nodes
workflow.add_node("parse_pdf", parse_pdf)
workflow.add_node("get_jurisdictions", get_jurisdictions)
workflow.add_edge(START, "parse_pdf")
# Graph Edges
workflow.add_edge("parse_pdf", "get_jurisdictions")
workflow.add_edge("get_jurisdictions", END)

agent = workflow.compile()
