from operator import gt, lt
from typing import Tuple

from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

from agent.models import Jurisdictions, SubstanceMapping, SubstanceMappingList
from agent.prompts import (
    JURISDICTION_PART_SUBSTANCE_MAPPING,
    JURISDICTION_SUBSTANCE_EXTRACTION,
)
from agent.utils.compliance_utils import make_compliant, make_violation
from agent.utils.unit_converter import UnitConverter
from schema import (
    CompliantSubstance,
    Jurisdiction,
    JurisdictionPartComplianceResult,
    Part,
    Violation,
)

load_dotenv()

MODEL = "gemma-3-4b-it"
llm = ChatGoogleGenerativeAI(model=MODEL, temperature=0.25)

ops = {
    "gte": lt,  # violation if part < jurisdiction
    "lte": gt,  # violation if part > jurisdiction
    "eq": lambda a, b: a != b,  # violation if unequal
}


def extract_jurisdiction(text: str) -> list[Jurisdiction]:
    """
    Extract jurisdictional substance regulations from raw text.

    This function uses a language model with a structured output parser to identify
    jurisdictions and their associated substance tolerances from unstructured text.
    The extracted information is returned as a list of `Jurisdiction` objects.

    Args:
        text (str):
            The input text containing information about jurisdictions and
            their regulated substances.

    Returns:
        List[Jurisdiction]:
            A list of jurisdiction objects, each containing the jurisdiction name
            and its associated substance tolerances.
            Returns an empty list if no jurisdictions are found.
    """

    # Initialize a parser that enforces output in the form of Jurisdictions
    parser = PydanticOutputParser(pydantic_object=Jurisdictions)
    # Load the extraction prompt template
    template = PromptTemplate.from_template(JURISDICTION_SUBSTANCE_EXTRACTION)
    # Chain: prompt -> LLM -> structured parser
    chain = template | llm | parser
    # Invoke the chain with the input text and parser formatting instructions
    result: Jurisdictions = chain.invoke(
        {"text": text, "format_instructions": parser.get_format_instructions()}
    )

    # Return empty list if no jurisdiction were detected
    if not result.jurisdictions:
        return []

    print(result.jurisdictions)

    return [juridiction for juridiction in result.jurisdictions]


def get_substance_mappings(
    part: Part, jurisidiction: Jurisdiction
) -> list[SubstanceMapping]:
    """
    Generate mappings between a part's substances and a jurisdiction's regulated substances.

    Args:
        part (Part): The part containing a list of substances to be evaluated.
        jurisidiction (Jurisdiction): The jurisdiction specifying regulated substances
            and their tolerances.

    Returns:
        list[SubstanceMapping]: A list of mappings connecting each part substance
        to the appropriate jurisdiction substance, including tolerance details.
    """

    # Parser to enforce structured output in the form of SubstanceMappings
    parser = PydanticOutputParser(pydantic_object=SubstanceMappingList)
    # Prepare the prompt template for jurisdiction-part substance mapping
    template = PromptTemplate.from_template(JURISDICTION_PART_SUBSTANCE_MAPPING)
    # Chain: prompt -> LLM -> structured parser
    chain = template | llm | parser

    # Invoke the chain with part and jurisdiction substances
    result: SubstanceMappingList = chain.invoke(
        {
            "jurisidiction_substances": jurisidiction.substance_tolerances,
            "part_substances": part.substances,
            "format_instructions": parser.get_format_instructions(),
        }
    )

    return result.mappings


def check_compliance(
    mappings: list[SubstanceMapping],
) -> Tuple[list[Violation], list[CompliantSubstance]]:
    """
    Evaluate compliance of part substances against jurisdictional tolerances.

    This function takes a list of `SubstanceMapping` objects (linking part substances
    to jurisdiction substances) and checks whether each part substance complies
    with the jurisdiction's defined tolerance limits. It categorizes results into:

    - **Violations**: Substances that exceed or fail to meet the jurisdiction's tolerance.
    - **CompliantSubstance**: Substances that comply, are ambiguous (due to missing
      regulation or undefined tolerance condition), or have no jurisdiction match.

    Args:
        mappings (List[SubstanceMapping]):
            A list of mappings between part substances and their corresponding
            jurisdiction substances.

    Raises:
        ValueError: If a required value (concentration) for part or jurisdiction
            substance is missing.
        ValueError: If a required unit for part or jurisdiction substance is missing.
        ValueError: If the jurisdiction substance value is undefined.
        ValueError: If the jurisdiction substance unit is undefined.

    Returns:
        Tuple[List[Violation], List[CompliantSubstance]]:
            - A list of violations explaining why each substance failed compliance.
            - A list of compliant or ambiguous substances, including notes where relevant.
    """

    violations: list[Violation] = []
    compliant_substances: list[CompliantSubstance] = []

    for mapping in mappings:

        print(mapping)

        part_substance = mapping.part_substance
        jurisidiction_substance = mapping.jurisidiction_substance

        # Case 1: No jurisdiction regulation for the given substance
        if jurisidiction_substance is None:
            compliant_substances.append(
                make_compliant(
                    part_substance,
                    None,
                    True,
                    note=f"No regulation for {part_substance.name} was found in the given jurisdiction",
                )
            )
            continue

        # Case 2: Part and Jurisdiction susbtances are not comparable
        if not mapping.is_comparable:
            compliant_substances.append(
                make_compliant(
                    part_substance,
                    jurisidiction_substance,
                    True,
                    note=f"The part substance ({part_substance.name}, {part_substance.value}{part_substance.unit}) and the jurisdiction substance ({jurisidiction_substance.name}, {jurisidiction_substance.value}{jurisidiction_substance.unit}) are not directly comparable. They differ in substance identity, measurement basis, or units of measure.",
                )
            )
            continue

        # Case 3: Validate that both part and jurisdiction substances have values/units
        if part_substance.value is None:
            raise ValueError(f"{part_substance.name} part substance value is not known")
        if part_substance.unit is None:
            raise ValueError(f"{part_substance.unit} part substance unit is not known")
        # Validate that jurisidiction substance have values/unit

        # If value is zero and condition is lte
        # Then that substance is not allowed
        if (
            jurisidiction_substance.value == 0.0
            and jurisidiction_substance.unit is None
        ):
            violations.append(
                make_violation(
                    part_substance,
                    jurisidiction_substance,
                    reason=f"The {part_substance.name} substance is not permitted in the given jurisdiction",
                )
            )
            continue

        if jurisidiction_substance.value is None:
            raise ValueError(
                f"{jurisidiction_substance.name} jurisdiction substance value is not known"
            )
        if jurisidiction_substance.unit is None:
            raise ValueError(
                f"{jurisidiction_substance.name} jurisdiction substance unit is not known"
            )

        # Case 4: Normalize units by converting part substance units to match jurisdiction units
        part_substance.value = UnitConverter.convert(
            part_substance.value,
            part_substance.unit,
            jurisidiction_substance.unit,
        )
        part_substance.unit = jurisidiction_substance.unit

        # Case 5: Retrieve tolerance condition operator (e.g., <=, >=, <, >)
        tolerance_condition = jurisidiction_substance.tolerance_condition
        check = ops.get(tolerance_condition) if tolerance_condition else None

        if check is None:
            # No defined tolerance -> ambiguous compliance
            compliant_substances.append(
                make_compliant(
                    part_substance,
                    jurisidiction_substance,
                    ambiguous=True,
                    note=f"{jurisidiction_substance.name} does not have any specified tolerance in the given jurisdiction",
                )
            )
        elif check(part_substance.value, jurisidiction_substance.value):
            # Substance violates the jurisdiction tolerance
            if tolerance_condition == "gte":
                violation_reason = f"Substance {part_substance.name} does not meet minimum requirements of the jurisdiction"
            else:
                violation_reason = f"Substance {part_substance.name} exceeds permisible limits of the jurisdiction"

            violations.append(
                make_violation(
                    part_substance, jurisidiction_substance, violation_reason
                )
            )
        else:
            # Substance complies with jurisdiction tolerance
            compliant_substances.append(
                make_compliant(
                    part_substance,
                    jurisidiction_substance,
                    ambiguous=False,
                    note=f"Substance {part_substance.name} passes the requirements of the given jurisdiction.",
                )
            )

    return violations, compliant_substances


def dfs_part_traversal(
    part: Part, jurisdiction: Jurisdiction
) -> JurisdictionPartComplianceResult:
    """
    Performs a depth-first traversal of a part and its bill of materials (BOM)
    to evaluate compliance with a given jurisdiction's substance regulations.

    The function checks whether the part contains regulated substances,
    determines compliance status, and propagates compliance/violation
    results upward from its children in the BOM.

    Args:
        part (Part):
            The part to evaluate, including its substances and any child parts
            defined in its BOM.
        jurisdiction (Jurisdiction):
            The regulatory jurisdiction whose compliance rules should be
            applied when evaluating the part and its children.

    Returns:
        JurisdictionPartComplianceResult:
            An object containing:
            - `part_id` and `part_name` of the evaluated part
            - `jurisdiction_name` used for compliance evaluation
            - `is_compliant`: overall compliance status of this part and its BOM
            - `violations`: list of violations found in this part
            - `compliant_substances`: substances explicitly verified as compliant
            - `bom_results`: compliance results for each child part in the BOM
    """

    if part.substances:
        # Get Part Substance and Jurisdiction Substance Mappings
        mappings: list[SubstanceMapping] = get_substance_mappings(part, jurisdiction)

        # Check Part Compliance
        violations, compliant_substances = check_compliance(mappings)
        is_compliant = True if not violations else False
    else:
        is_compliant = True
        violations: list[Violation] = []
        compliant_substances: list[CompliantSubstance] = []

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
        compliant_substances=compliant_substances,
        bom_results=bom_results,
    )
