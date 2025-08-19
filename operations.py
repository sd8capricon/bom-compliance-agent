from typing import Tuple

from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

from agent.models import SubstanceMappings, SubstanceNamePair
from prompts import (
    JURISDICTION_PART_SUBSTANCE_MAPPING,
    JURISDICTION_SUBSTANCE_EXTRACTION,
)
from schema import (
    CompliantSubstance,
    Jurisdiction,
    JurisdictionPartComplianceResult,
    Jurisdictions,
    Part,
    Violation,
)

load_dotenv()

MODEL = "gemma-3-4b-it"
llm = ChatGoogleGenerativeAI(model=MODEL, temperature=0.25)


def extract_jurisdiction(text: str) -> list[Jurisdiction]:
    parser = PydanticOutputParser(pydantic_object=Jurisdictions)
    template = PromptTemplate.from_template(JURISDICTION_SUBSTANCE_EXTRACTION)
    chain = template | llm | parser

    result: Jurisdictions = chain.invoke(
        {"text": text, "format_instructions": parser.get_format_instructions()}
    )

    if result.jurisdictions == None:
        return []

    return [juridiction for juridiction in result.jurisdictions]


# Dummy Function to check part compliance in a jurisdiction
def check_jurisdiction_part_compliance(
    part: Part, jurisidiction: Jurisdiction
) -> Tuple[bool, list[Violation], list[CompliantSubstance]]:

    # Check if part has substances
    # Find 1:1 mapping
    # Compare the tolerances
    # Repeat Recusively

    jurisidiction_substance_names: list[SubstanceNamePair] = [
        {"name": substance.name, "standardized_name": substance.standardized_name}
        for substance in jurisidiction.substance_tolerances
    ]
    part_substance_names: list[SubstanceNamePair] = [
        {"name": substance.name, "standardized_name": substance.standardized_name}
        for substance in part.substances
    ]

    parser = PydanticOutputParser(pydantic_object=SubstanceMappings)
    template = PromptTemplate.from_template(JURISDICTION_PART_SUBSTANCE_MAPPING)
    chain = template | llm | parser

    is_compliant = True
    violations: list[Violation] = []
    compliant_substances: list[CompliantSubstance] = []

    if not part_substance_names:
        return is_compliant, violations, compliant_substances

    result: SubstanceMappings = chain.invoke(
        {
            "jurisidiction_substance_names": jurisidiction_substance_names,
            "part_substance_names": part_substance_names,
            "format_instructions": parser.get_format_instructions(),
        }
    )

    print(result)

    return is_compliant, violations, compliant_substances


def dfs_part_traversal(
    part: Part, jurisdiction: Jurisdiction
) -> JurisdictionPartComplianceResult:
    """
    DFS traversal that builds a PartComplianceResult tree.
    Compliance is determined by check_jurisdiction_part_compliance and propagated upward.
    """

    # Check Part Compliance
    is_compliant, violations, compliant_substances = check_jurisdiction_part_compliance(
        part, jurisdiction
    )

    # Traverse Children
    bom_results: list[JurisdictionPartComplianceResult] = []
    if part.bom:
        for child in part.bom:
            child_result = dfs_part_traversal(child, jurisdiction)
            bom_results.append(child_result)
            if child_result.is_compliant is False:
                is_compliant = False  # Propagate failure upward
                # Append a violation with reason stating violation found in child

    return JurisdictionPartComplianceResult(
        part_id=part.id,
        part_name=part.name,
        jurisdiction_name=jurisdiction.name,
        is_compliant=is_compliant,
        violations=violations,
        comliant_substances=compliant_substances,
        bom_results=bom_results,
    )
