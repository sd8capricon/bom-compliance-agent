"""
agent/models.py

This module defines models specific to compliance check agent
"""

from typing import TypedDict

from langchain_core.documents import Document
from pydantic import BaseModel, Field

from schema import Jurisdiction, Part


class ComplianceCheckAgentState(BaseModel):
    file_path: str
    pages: list[Document] = []
    jurisdictions: list[Jurisdiction] = []
    part: Part


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

    part_substance_standardized_name: str | None = Field(
        None,
        description="The standardized IUPAC name or elemental symbol of the substance "
        "as identified in the part's composition. This is mapped to the "
        "equivalent substance defined by the jurisdiction.",
    )
    jurisidiction_substance_standardized_name: str | None = Field(
        None,
        description="The standardized IUPAC name or elemental symbol of the substance "
        "as specified by the jurisdiction's regulatory requirements. "
        "This is the target reference to which the part's substance is matched.",
    )


class SubstanceMappings(BaseModel):
    mappings: list[SubstanceMapping] = Field(
        [], description="List of mappings between jurisdiction and part substances"
    )
