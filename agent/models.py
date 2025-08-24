"""
agent/models.py

This module defines models specific to compliance check agent
"""

from typing import TypedDict

from langchain_core.documents import Document
from pydantic import BaseModel, Field

from schema import (
    ComplianceReport,
    Jurisdiction,
    JurisdictionPartComplianceResult,
    Part,
    Substance,
)


class ComplianceCheckAgentState(BaseModel):
    report_name: str
    part: Part
    file_path: str
    pages: list[Document] = []
    jurisdictions: list[Jurisdiction] = []
    jurisdiction_compliance_results: list[JurisdictionPartComplianceResult] = []
    compliance_report: ComplianceReport | None = None


class Jurisdictions(BaseModel):
    jurisdictions: list[Jurisdiction] = Field(
        [],
        description="A list of unique jurisdictions, each containing its name and the list "
        "of substance tolerances that apply within that jurisdiction. "
        "Each jurisdiction should appear only once, with all relevant "
        "substances merged, and without duplicate substances.",
    )


class SubstanceNamePair(TypedDict):
    """
    Represents a substance by its common/trivial name and its standardized IUPAC name or element symbol.
    Used for lightweight lookups and mappings without requiring the full Substance model.
    """

    name: str
    standardized_name: str


class SubstanceMapping(BaseModel):
    """
    Defines the correspondence between a substance found in a part
    and a substance defined in a jurisdiction's regulatory list.
    """

    part_substance: Substance = Field(
        ...,
        description="Substance found in the part. This is mapped to the standardized IUPAC name or elemental symbol equivalent substance defined by the jurisdiction.",
    )
    jurisidiction_substance: Substance | None = Field(
        None,
        description="Susbtance found in the jurisdiction's. This is the target reference to which the part's substance IUPAC name or elemental symbol is matched.",
    )
    is_comparable: bool = Field(
        False,
        description="Indicates whether part_substance and jurisdiction_substance can be meaningfully compared after converting part_substance values and units to the jurisdiction's standard. In other words, this is True if both represent the same physical quantity (e.g., mass, concentration).",
    )


class SubstanceMappingList(BaseModel):
    mappings: list[SubstanceMapping] = Field(
        [],
        description="List of mappings (list[SubstanceMapping]) between jurisdiction and part substances",
    )
