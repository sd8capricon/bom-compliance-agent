from __future__ import annotations

from pydantic import BaseModel, Field


class Substance(BaseModel):
    """
    Represents a chemical substance with its measured value and unit.
    """

    name: str = Field(..., description="The name of the substance (e.g., 'Lead').")
    value: float = Field(
        ..., description="The concentration or amount of the substance."
    )
    unit: str = Field(
        ..., description="The unit of measurement (e.g., 'mg/kg', 'ppm')."
    )


class Tolerance(BaseModel):
    """
    Represents a tolerance limit for a substance in a specific unit.
    """

    value: float = Field(
        ..., description="The maximum allowed value for the substance."
    )
    unit: str = Field(..., description="The unit of measurement for the tolerance.")


class Part(BaseModel):
    """
    Represents a single part in a Bill of Materials (BOM).
    """

    id: str = Field(..., description="A unique identifier for the part.")
    name: str = Field(..., description="The name of the part.")
    bom: list[Part] | None = Field(
        None, description="A list of sub-parts, if this is an assembly."
    )
    substances: list[Substance] | None = Field(
        None, description="A list of substances found in the part."
    )


class Jurisdiction(BaseModel):
    """
    Represents a regulatory jurisdiction with its substance tolerance limits.
    """

    name: str = Field(
        ..., description="The name of the jurisdiction (e.g., 'RoHS', 'REACH')."
    )
    substance_tolerances: list[Substance] | None = Field(
        None,
        description="A list of substances and their tolerances applicable to this jurisdiction.",
    )


class Violation(BaseModel):
    """
    Details of a specific compliance violation.
    """

    substance_name: str = Field(
        ..., description="The name of the substance that is in violation."
    )
    substance_concentration: Tolerance = Field(
        ..., description="The measured concentration of the substance."
    )
    jurisdiction_tolerance: Tolerance = Field(
        ...,
        description="The allowed tolerance limit for the substance in the jurisdiction.",
    )
    violation_reason: str = Field(
        ..., description="A description of why the violation occurred."
    )


class PartComplianceResult(BaseModel):
    """
    The compliance check result for a single part within a specific jurisdiction.
    """

    part_id: str
    part_name: str = Field(..., description="The name of the part being checked.")
    jurisdiction_name: str = Field(
        ...,
        description="The name of the jurisdiction against which compliance was checked.",
    )
    is_compliant: bool | None = Field(
        ..., description="True if the part is compliant, False otherwise."
    )
    violations: list[Violation] | None = Field(
        None, description="A list of all compliance violations found."
    )
    bom_results: list[PartComplianceResult] | None = Field(
        None, description="The compliance results for the sub-parts in the BOM."
    )


class ComplianceReport(BaseModel):
    """
    A comprehensive report detailing the compliance check across multiple jurisdictions.
    """

    name: str = Field(
        ..., description="The name of the report or the main part being analyzed."
    )
    jurisdictions: list[Jurisdiction] = Field(
        ..., description="A list of all jurisdictions checked in the report."
    )
    top_level_part_result: PartComplianceResult = Field(
        ...,
        description="The compliance result for the main part being analyzed, including all nested results.",
    )
