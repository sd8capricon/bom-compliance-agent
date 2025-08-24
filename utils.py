import os

import streamlit as st
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.messages import AIMessage
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

from agent.models import ComplianceCheckAgentState
from agent.prompts import MARKDOWN
from agent.workflow import agent
from schema import ComplianceReport, Part

load_dotenv()


def run_agent(part_file, pdf_file):
    # Parse Part JSON
    part = Part.model_validate_json(part_file.read().decode("utf-8"))

    # Save uploaded PDF temporarily
    pdf_path = os.path.join("temp", "temp_regulation.pdf")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    with open(pdf_path, "wb") as f:
        f.write(pdf_file.read())

    # Create agent state
    agent_state = ComplianceCheckAgentState(
        file_path=pdf_path,
        part=part,
        report_name=f"Compliance Report for {getattr(part, 'name', 'Unknown Part')}",
    )

    # Run agent
    agent_state = ComplianceCheckAgentState.model_validate(agent.invoke(agent_state))

    # Cleanup temp file
    cleanup_temp_file(pdf_path)

    return agent_state


def cleanup_temp_file(path: str):
    """Safely remove temporary file if it exists."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception as e:
        st.warning(f"⚠️ Could not delete temp file: {e}")


def generate_markdown_result(compliance_report: ComplianceReport) -> str:
    MODEL = "gemini-2.5-flash"
    llm = ChatGoogleGenerativeAI(model=MODEL, temperature=0.5)
    template = PromptTemplate.from_template(MARKDOWN)
    print("▶️ Starting: generate_markdown_report")
    chain = template | llm
    result: AIMessage = chain.invoke(
        {"json_report": compliance_report.jurisdiction_compliance_results}
    )
    print("✅ Completed: generate_markdown_report")
    return result.content
