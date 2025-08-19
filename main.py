import os

from agent.models import ComplianceCheckAgentState
from agent.workflow import agent
from schema import Part


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
