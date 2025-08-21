from langgraph.graph import END, START, StateGraph

from agent.models import ComplianceCheckAgentState
from agent.steps import (
    build_report,
    check_part_compliance,
    get_jurisdictions,
    parse_pdf,
)

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
workflow.add_node("check_part_compliance", check_part_compliance)
workflow.add_node("build_report", build_report)
# Graph Edges
workflow.add_edge(START, "parse_pdf")
workflow.add_edge("parse_pdf", "get_jurisdictions")
workflow.add_edge("get_jurisdictions", "check_part_compliance")
workflow.add_edge("check_part_compliance", "build_report")
workflow.add_edge("build_report", END)

agent = workflow.compile()

if __name__ == "__main__":
    png_bytes = agent.get_graph().draw_mermaid_png()
    with open("compliance_workflow.png", "wb") as f:
        f.write(png_bytes)
    print("Graph saved as compliance_workflow.png")
