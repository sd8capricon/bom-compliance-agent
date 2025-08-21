from operator import gt, lt
from typing import Tuple

from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

from agent.models import Jurisdictions, SubstanceMapping, SubstanceMappings
from agent.utils.unit_converter import UnitConverter
from prompts import (
    JURISDICTION_PART_SUBSTANCE_MAPPING,
    JURISDICTION_SUBSTANCE_EXTRACTION,
)
from schema import (
    CompliantSubstance,
    Jurisdiction,
    JurisdictionPartComplianceResult,
    Part,
    Substance,
    Tolerance,
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
    parser = PydanticOutputParser(pydantic_object=Jurisdictions)
    template = PromptTemplate.from_template(JURISDICTION_SUBSTANCE_EXTRACTION)
    chain = template | llm | parser

    result: Jurisdictions = chain.invoke(
        {"text": text, "format_instructions": parser.get_format_instructions()}
    )

    if not result.jurisdictions:
        return []

    return [juridiction for juridiction in result.jurisdictions]


def get_substance_mappings(
    part: Part, jurisidiction: Jurisdiction
) -> list[SubstanceMapping]:
    """
    Map the part substances to the substances in the jurisdiction

    Args:
        part (Part): Substances belonging to Part
        jurisidiction (Jurisdiction): Susbtance Tolerances of the Jurisdiction

    Returns:
        SubstanceMappings: Mapping between part susbtances and jurisdiction
    """

    parser = PydanticOutputParser(pydantic_object=SubstanceMappings)
    template = PromptTemplate.from_template(JURISDICTION_PART_SUBSTANCE_MAPPING)
    chain = template | llm | parser

    result: SubstanceMappings = chain.invoke(
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

    violations: list[Violation] = []
    compliant_substances: list[CompliantSubstance] = []

    for mapping in mappings:

        part_substance = mapping.part_substance
        jurisidiction_substance = mapping.jurisidiction_substance

        if jurisidiction_substance is None:
            compliant_substances.append(
                CompliantSubstance(
                    substance_name=part_substance.name,
                    substance_standard_name=part_substance.standardized_name,
                    substance_concentration=Tolerance(
                        value=part_substance.value,
                        unit=part_substance.unit,
                        tolerance_condition=None,
                    ),
                    jurisdiction_tolerance=Tolerance(
                        value=None, unit=None, tolerance_condition=None
                    ),
                    is_ambiguous=True,
                    note=f"No regulation for {part_substance.name} was not found in the given jurisdiction",
                )
            )
            continue

        # Check Validity of the substances
        if part_substance.value is None:
            raise ValueError(f"{part_substance.name} part substance value is not known")
        if part_substance.unit is None:
            raise ValueError(f"{part_substance.unit} part substance unit is not known")
        if jurisidiction_substance.value is None:
            raise ValueError(
                f"{jurisidiction_substance.name} jurisdiction substance value is not known"
            )
        if jurisidiction_substance.unit is None:
            raise ValueError(
                f"{jurisidiction_substance.name} jurisdiction substance value is not known"
            )

        # Convert part substance value and unit to match the units of the jursidiciont substance
        part_substance.value = UnitConverter.convert(
            part_substance.value,
            part_substance.unit,
            jurisidiction_substance.unit,
        )
        part_substance.unit = jurisidiction_substance.unit

        tolerance_condition = jurisidiction_substance.tolerance_condition
        check = ops.get(tolerance_condition) if tolerance_condition else None

        if check is None:  # Unknown Tolerance condition
            # Ambigious Compliance
            compliant_substances.append(
                CompliantSubstance(
                    substance_name=part_substance.name,
                    substance_standard_name=part_substance.standardized_name,
                    substance_concentration=Tolerance(
                        value=part_substance.value,
                        unit=part_substance.unit,
                        tolerance_condition=None,
                    ),
                    jurisdiction_tolerance=Tolerance(
                        value=jurisidiction_substance.value,
                        unit=jurisidiction_substance.unit,
                        tolerance_condition=None,
                    ),
                    is_ambiguous=True,
                    note=f"{jurisidiction_substance.name} does not have any specified tolerance in the given jurisdiction",
                )
            )
        elif check(part_substance.value, jurisidiction_substance.value):
            # Violation
            if tolerance_condition == "gte":
                violation_reason = f"Substance {part_substance.name} does not meet minimum requirements of the jurisdiction"
            else:
                violation_reason = f"Substance {part_substance.name} exceeds permisible limits of the jurisdiction"

            violations.append(
                Violation(
                    substance_name=part_substance.name,
                    substance_standard_name=part_substance.standardized_name,
                    substance_concentration=Tolerance(
                        value=part_substance.value,
                        unit=part_substance.unit,
                        tolerance_condition=None,
                    ),
                    jurisdiction_tolerance=Tolerance(
                        value=jurisidiction_substance.value,
                        unit=jurisidiction_substance.unit,
                        tolerance_condition=None,
                    ),
                    violation_reason=violation_reason,
                )
            )
        else:
            # Compliant
            compliant_substances.append(
                CompliantSubstance(
                    substance_name=part_substance.name,
                    substance_standard_name=part_substance.standardized_name,
                    substance_concentration=Tolerance(
                        value=part_substance.value,
                        unit=part_substance.unit,
                        tolerance_condition=None,
                    ),
                    jurisdiction_tolerance=Tolerance(
                        value=jurisidiction_substance.value,
                        unit=jurisidiction_substance.unit,
                        tolerance_condition=None,
                    ),
                    is_ambiguous=True,
                    note=f"Substance {jurisidiction_substance.name} passes the requirementes of the given jurisdiction.",
                )
            )

    return violations, compliant_substances


def dfs_part_traversal(
    part: Part, jurisdiction: Jurisdiction
) -> JurisdictionPartComplianceResult:
    """
    DFS traversal that builds a PartComplianceResult tree.
    Compliance is determined by check_jurisdiction_part_compliance and propagated upward.
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
        comliant_substances=compliant_substances,
        bom_results=bom_results,
    )
