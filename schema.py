from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Substance(BaseModel):
    """
    Represents a chemical substance with its measured value and unit.
    """

    name: str = Field(
        ..., description="The common/trivial name of the substance (e.g., 'Lead')."
    )
    standardized_name: str = Field(
        ...,
        description="The standard IUPAC name of the substance/compound (e.g. ethanoic acid for acetic acid) or the standard element symbol as per periodic table (e.g. 'Pb' for Lead)",
    )
    value: float | None = Field(
        ..., description="The concentration or amount of the substance."
    )
    unit: str | None = Field(
        ..., description="The unit of measurement (e.g., 'mg/kg', 'ppm')."
    )
    tolerance_condition: Literal["gte", "lte", "eq"] | None = Field(
        None,
        description="Condition used to compare a value against a tolerance threshold. "
        "'gte' means greater than or equal to, 'lte' means less than or equal to, "
        "and 'eq' means equal to. If None, no condition is applied.",
    )

    @classmethod
    def find_by_standard_name(
        cls, substances: list[Substance], standard_name: str
    ) -> Substance | None:
        """
        Search for a substance in a collection by its standardized_name.
        Returns the first match, or None if not found.
        """
        for sub in substances:
            if sub.standardized_name == standard_name:
                return sub
        return None


class Part(BaseModel):
    """
    Represents a single part in a Bill of Materials (BOM).
    """

    id: str = Field(..., description="A unique identifier for the part.")
    name: str = Field(..., description="The name of the part.")
    bom: list[Part] | None = Field(
        None, description="A list of sub-parts, if this is an assembly."
    )
    substances: list[Substance] = Field(
        [], description="A list of substances found in the part."
    )


class Jurisdiction(BaseModel):
    """
    Represents a regulatory jurisdiction with its substance tolerance limits.
    """

    name: str = Field(
        ...,
        description="The full, official name of the jurisdiction. (e.g. European Union', 'United States of America', or 'Japan'.).",
    )
    abbreviation: str = Field(
        ...,
        description="The common, abbreviated code for the jurisdiction. (e.g. 'EU', 'USA', or 'JP')",
    )
    substance_tolerances: list[Substance] = Field(
        [],
        description="A list of substances and their tolerances applicable to this jurisdiction.",
    )


class Tolerance(BaseModel):
    """
    Represents a tolerance limit for a substance in a specific unit.
    """

    value: float | None = Field(
        ..., description="The maximum allowed value for the substance."
    )
    unit: str | None = Field(
        ..., description="The unit of measurement for the tolerance."
    )
    tolerance_condition: Literal["gte", "lte", "eq"] | None = Field(
        None,
        description="Condition used to compare a value against a tolerance threshold. "
        "'gte' means greater than or equal to, 'lte' means less than or equal to, "
        "and 'eq' means equal to. If None, no condition is applied.",
    )


class Violation(BaseModel):
    """
    Details of a specific compliance violation.
    """

    substance_name: str = Field(
        ...,
        description="The common/trivial name of the substance that is in violation.",
    )
    substance_standard_name: str = Field(
        ...,
        description="The standard IUPAC name of the substance/compound (e.g. ethanoic acid for acetic acid) or the standard element symbol as per periodic table (e.g. 'Pb' for Lead)",
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


class CompliantSubstance(BaseModel):
    """
    Details of a substance that was checked and found compliant (no violation).
    """

    substance_name: str = Field(
        ...,
        description="The common/trivial name of the substance that is in violation.",
    )
    substance_standard_name: str = Field(
        ...,
        description="The standard IUPAC name of the substance/compound (e.g. ethanoic acid for acetic acid) or the standard element symbol as per periodic table (e.g. 'Pb' for Lead)",
    )
    substance_concentration: Tolerance = Field(
        ..., description="The measured concentration of the substance."
    )
    jurisdiction_tolerance: Tolerance = Field(
        ...,
        description="The allowed tolerance limit for the substance in the jurisdiction.",
    )
    is_ambiguous: bool = Field(
        False,
        description="If the substanc's compliance cannot be determined for certain",
    )
    note: str = Field(
        ..., description="Extra commentary on the compliance of the substance"
    )


class JurisdictionPartComplianceResult(BaseModel):
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
    violations: list[Violation] = Field(
        [], description="A list of all compliance violations found."
    )
    compliant_substances: list[CompliantSubstance] = Field(
        [],
        description="A list of substances checked that were within limits (no violations).",
    )
    bom_results: list[JurisdictionPartComplianceResult] = Field(
        [], description="The compliance results for the sub-parts in the BOM."
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
    jurisdiction_compliance_results: list[JurisdictionPartComplianceResult] = Field(
        ...,
        description="Compliance result of the part for each jurisdiction.",
    )
