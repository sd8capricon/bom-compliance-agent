from langchain_community.document_loaders import PyMuPDFLoader

from agent.models import ComplianceCheckAgentState
from agent.operations import dfs_part_traversal, extract_jurisdiction
from schema import Jurisdiction


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
