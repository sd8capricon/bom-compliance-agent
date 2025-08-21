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

    agent_state = ComplianceCheckAgentState(
        file_path=file_path,
        part=part,
        report_name="RoHs Compliance Report for Remote Controller",
    )
    agent_state = ComplianceCheckAgentState.model_validate(agent.invoke(agent_state))

    # Save final state as JSON
    output_path = os.path.join("data", "results", "agent_state.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(agent_state.model_dump_json(indent=2))

    print(f"✅ Agent state saved to {output_path}")


if __name__ == "__main__":
    main()
