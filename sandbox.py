import os

from agent.models import SubstanceMapping, SubstanceMappingList
from agent.operations import check_compliance, dfs_part_traversal
from schema import Jurisdiction, Part, Substance

jurisdictions = [
    Jurisdiction(
        name="European Union",
        substance_tolerances=[
            Substance(
                name="Lead",
                standardized_name="Pb",
                value=0.1,
                unit="%",
                tolerance_condition="lte",
            ),
            Substance(
                name="Mercury",
                standardized_name="Hg",
                value=0.1,
                unit="%",
                tolerance_condition="lte",
            ),
            Substance(
                name="Cadmium",
                standardized_name="Cd",
                value=0.01,
                unit="%",
                tolerance_condition="lte",
            ),
            Substance(
                name="Hexabromocyclododecane",
                standardized_name="HBCDD",
                value=None,
                unit=None,
                tolerance_condition=None,
            ),
            Substance(
                name="Bis(2-ethylhexyl) phthalate",
                standardized_name="DEHP",
                value=0.1,
                unit="%",
                tolerance_condition="lte",
            ),
            Substance(
                name="Butyl benzyl phthalate",
                standardized_name="BBP",
                value=0.1,
                unit="%",
                tolerance_condition="lte",
            ),
            Substance(
                name="Dibutyl phthalate",
                standardized_name="DBP",
                value=0.1,
                unit="%",
                tolerance_condition="lte",
            ),
            Substance(
                name="DEHP",
                standardized_name="di(2-ethylhexyl) phthalate",
                value=None,
                unit=None,
                tolerance_condition="lte",
            ),
            Substance(
                name="DBP",
                standardized_name="dibutyl phthalate",
                value=None,
                unit=None,
                tolerance_condition="lte",
            ),
            Substance(
                name="DIBP",
                standardized_name="diisobutyl phthalate",
                value=None,
                unit=None,
                tolerance_condition="lte",
            ),
            Substance(
                name="Regulation (EC) No 1907/2006",
                standardized_name="1907/2006",
                value=None,
                unit=None,
                tolerance_condition=None,
            ),
            Substance(
                name="Hexavalent chromium",
                standardized_name="Cr(VI)",
                value=0.1,
                unit="%",
                tolerance_condition="lte",
            ),
            Substance(
                name="Polybrominated biphenyls",
                standardized_name="PBB",
                value=0.1,
                unit="%",
                tolerance_condition="lte",
            ),
            Substance(
                name="Polybrominated diphenyl ethers",
                standardized_name="PBDE",
                value=0.1,
                unit="%",
                tolerance_condition="lte",
            ),
            Substance(
                name="Diisobutyl phthalate",
                standardized_name="DIBP",
                value=0.1,
                unit="%",
                tolerance_condition="lte",
            ),
        ],
    )
]

pcb_assy_001_mapping = SubstanceMappingList(
    mappings=[
        SubstanceMapping(
            part_substance=Substance(
                name="Lead",
                standardized_name="Pb",
                value=0.009,
                unit="mg/kg",
                tolerance_condition=None,
            ),
            jurisidiction_substance=Substance(
                name="Lead",
                standardized_name="Pb",
                value=0.1,
                unit="%",
                tolerance_condition="lte",
            ),
            is_comparable=True,
        ),
        SubstanceMapping(
            part_substance=Substance(
                name="Tin",
                standardized_name="Sn",
                value=99.9,
                unit="%",
                tolerance_condition=None,
            ),
            jurisidiction_substance=None,
            is_comparable=False,
        ),
    ]
)
casting_001_mapping = SubstanceMappingList(
    mappings=[
        SubstanceMapping(
            part_substance=Substance(
                name="Brominated Flame Retardants",
                standardized_name="polybrominated diphenyl ethers",
                value=0.005,
                unit="mg/kg",
                tolerance_condition=None,
            ),
            jurisidiction_substance=Substance(
                name="Polybrominated diphenyl ethers",
                standardized_name="PBDE",
                value=0.1,
                unit="%",
                tolerance_condition="lte",
            ),
            is_comparable=True,
        )
    ]
)

# part_path = os.path.join("data", "parts", "remote_controller.json")
# with open(part_path, "r", encoding="utf-8") as file:
#     part = Part.model_validate_json(file.read())

# report = dfs_part_traversal(part, jurisdictions[0])

res = check_compliance(pcb_assy_001_mapping.mappings)
print(res)
res = check_compliance(casting_001_mapping.mappings)
print(res)
