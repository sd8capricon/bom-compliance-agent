import os

from langchain_community.document_loaders import PyMuPDFLoader
from langgraph.graph import END, START, StateGraph

from agent.models import ComplianceCheckAgentState
from agent.operations import dfs_part_traversal, extract_jurisdiction
from schema import Jurisdiction, Part

# ComplianceCheckAgent
# 1. parse pdf file extract text from each page
# 2. extract jurisdictions from each page, then deduplicate jurisdictions and substances within them
# 3. check compliance of the part for each jurisdiction
#   - DFS approach
#   - Find the 1:1 mapping between jurisdiction and part substances
#   - Halt when non compliant part is reached
#   - Ask user to continue checking or generate report of the seen parts
# 4. generate the compliance report md


def parse_pdf(state: ComplianceCheckAgentState) -> ComplianceCheckAgentState:
    loader = PyMuPDFLoader(state.file_path)
    docs = loader.load()
    state.pages = docs
    return state


def get_jurisdictions(state: ComplianceCheckAgentState) -> ComplianceCheckAgentState:
    jurisdictions_map: dict[str, Jurisdiction] = {}
    page_jurisdictions: list[Jurisdiction] = []
    for page in state.pages:
        page_jurisdictions = extract_jurisdiction(page.page_content)
        for j in page_jurisdictions:
            # Deduplicate substances in this jurisdiction before processing
            if j.substance_tolerances:
                j.substance_tolerances = list(
                    {s.name: s for s in j.substance_tolerances}.values()
                )

            if j.name not in jurisdictions_map:
                jurisdictions_map[j.name] = j
            else:
                existing = jurisdictions_map[j.name]
                if len(existing.substance_tolerances) == 0:
                    existing.substance_tolerances = j.substance_tolerances
                else:
                    # Merge based on name only
                    merged_substances = {
                        s.name: s for s in existing.substance_tolerances
                    }
                    for s in j.substance_tolerances:
                        merged_substances[s.name] = s
                    existing.substance_tolerances = list(merged_substances.values())

    # Final pass: ensure substances in each jurisdiction are deduplicated by name
    for jur in jurisdictions_map.values():
        if jur.substance_tolerances:
            jur.substance_tolerances = list(
                {s.name: s for s in jur.substance_tolerances}.values()
            )

    state.jurisdictions = list(jurisdictions_map.values())

    return state


def check_part_compliance(
    state: ComplianceCheckAgentState,
) -> ComplianceCheckAgentState:
    for jurisdiction in state.jurisdictions:
        jurisdiction_part_compliance_report = dfs_part_traversal(
            state.part, jurisdiction
        )
    return state


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
