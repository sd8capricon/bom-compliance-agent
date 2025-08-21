from typing import Literal
from schema import Tolerance, CompliantSubstance, Violation, Substance


def make_tolerance(
    sub: Substance, condition: Literal["gte", "lte", "eq"] | None = None
) -> Tolerance:
    """Create Tolerance from a substance."""
    return Tolerance(
        value=sub.value,
        unit=sub.unit,
        tolerance_condition=condition,
    )


def make_compliant(
    part_sub: Substance,
    juris_sub: Substance | None,
    ambiguous: bool,
    note: str,
) -> CompliantSubstance:
    """Create CompliantSubstance record."""
    return CompliantSubstance(
        substance_name=part_sub.name,
        substance_standard_name=part_sub.standardized_name,
        substance_concentration=make_tolerance(part_sub),
        jurisdiction_tolerance=(
            make_tolerance(juris_sub)
            if juris_sub
            else Tolerance(value=None, unit=None, tolerance_condition=None)
        ),
        is_ambiguous=ambiguous,
        note=note,
    )


def make_violation(part_sub: Substance, juris_sub: Substance, reason: str) -> Violation:
    """Create Violation record."""
    return Violation(
        substance_name=part_sub.name,
        substance_standard_name=part_sub.standardized_name,
        substance_concentration=make_tolerance(part_sub),
        jurisdiction_tolerance=make_tolerance(juris_sub),
        violation_reason=reason,
    )


def validate_substance(sub: Substance, context: str) -> None:
    """Ensure a substance has both value and unit."""
    if sub.value is None:
        raise ValueError(f"{sub.name} {context} substance value is not known")
    if sub.unit is None:
        raise ValueError(f"{sub.name} {context} substance unit is not known")
