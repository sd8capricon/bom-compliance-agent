import os

from langgraph.graph import END, START, StateGraph

from agent.models import ComplianceCheckAgentState
from agent.steps import get_jurisdictions, parse_pdf
from schema import Part

# ComplianceCheckAgent
# 1. parse pdf file extract text from each page
# 2. extract jurisdictions from each page, then deduplicate jurisdictions and substances within them
# 3. check compliance of the part for each jurisdiction
#   - DFS approach
#   - Find the 1:1 mapping between jurisdiction and part substances
#   - Halt when non compliant part is reached
#   - Ask user to continue checking or generate report of the seen parts
# 4. generate the compliance report md

graph_builder = StateGraph(ComplianceCheckAgentState)
# Graph Nodes
graph_builder.add_node("parse_pdf", parse_pdf)
graph_builder.add_node("get_jurisdictions", get_jurisdictions)
graph_builder.add_edge(START, "parse_pdf")
# Graph Edges
graph_builder.add_edge("parse_pdf", "get_jurisdictions")
graph_builder.add_edge("get_jurisdictions", END)
agent = graph_builder.compile()


def main():
    # Open and load the JSON file
    part_path = os.path.join("data", "parts", "remote_controller.json")
    with open(part_path, "r", encoding="utf-8") as file:
        part = Part.model_validate_json(file.read())
    # Path to compliance document
    file_path = "./data/documents/RoHS.pdf"

    agent_state = ComplianceCheckAgentState(file_path=file_path, part=part)
    res = ComplianceCheckAgentState.model_validate(agent.invoke(agent_state))
    print(res.jurisdictions)


if __name__ == "__main__":
    main()
