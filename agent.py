import os

from agent.models import ComplianceCheckAgentState
from agent.workflow import agent
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
