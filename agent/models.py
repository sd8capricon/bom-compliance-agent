"""
agent/models.py

This module defines models specific to compliance check agent
"""

from typing import TypedDict

from pydantic import BaseModel, Field


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

    part_substance_iupac: str | None = Field(
        None,
        description="The standardized IUPAC name or elemental symbol of the substance "
        "as identified in the part's composition. This is mapped to the "
        "equivalent substance defined by the jurisdiction.",
    )
    jurisidiction_substance_iupac: str | None = Field(
        None,
        description="The standardized IUPAC name or elemental symbol of the substance "
        "as specified by the jurisdiction's regulatory requirements. "
        "This is the target reference to which the part's substance is matched.",
    )


class SubstanceMappings(BaseModel):
    mappings: list[SubstanceMapping] = Field(
        [], description="List of mappings between jurisdiction and part substances"
    )
