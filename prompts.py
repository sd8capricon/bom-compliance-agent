JURISDICTION_SUBSTANCE_EXTRACTION = """
Extract all jurisdictions and their substance tolerances from the text below.

A jurisdiction name must be a valid **geographic or regulatory region identifier**, such as:
- A country name (e.g., "United States", "India", "Germany")
- A continent or region (e.g., "Europe", "Asia-Pacific")
- A recognized abbreviation (e.g., "EU")
Do NOT use product names, company names, or generic terms as jurisdiction names.

Substances Extraction Rules
- Extract all mentioned chemical substances.
- *For compounds*:
    - Use the IUPAC name.
    - Example: extract ethanoic acid instead of acetic acid, 2-hydroxypropanoic acid instead of lactic acid.
    - If the text provides a trivial/common name, convert it to the correct IUPAC name.
    - standardized_name must always contain the IUPAC name
- *For elements*:
    - Normalize to the IUPAC element symbol (e.g., Pb, Hg, Cd, As).
    - If the text provides the element name (lead, mercury, cadmium), convert it to the symbol (Pb, Hg, Cd).
    - standardized_name must always contain the IUPAC element symbol, not the full name.

Tolerance Extraction Rules
- *tolerance_condition* must always capture the type of threshold comparison used in the text:
    - "gte" → greater than or equal to (≥, at least, not less than, minimum)
    - "lte" → less than or equal to (≤, at most, not more than, maximum)
    - "eq" → equal to (=, exactly, fixed value)
    - If no explicit comparison is provided, leave as null.
- *Special Case* — Not Tolerated / Prohibited Substances:
    - If the text states a substance is not tolerated, prohibited, or must not be present, set:
        - value = 0
        - unit = null
        - tolerance_condition = "lte"
    
Rules:
1. Do NOT repeat jurisdictions — if a jurisdiction appears more than once, merge their substances into one.
2. Do NOT repeat substances within the same jurisdiction — keep only one entry for each substance name.
3. Substance tolerances must include the `value`, `unit` and `tolerance_condition` where available; if missing, leave as null.
4. Only extract jurisdiction name that clearly refer to a country, region, continent, or regulatory body abbreviation.
5. `name` -> Store the common/trivial name exactly as it appears in the text (Pb, Lead, acetic acid).
6. `standardized_name` -> Store the IUPAC name (for compounds) or the IUPAC element symbol (for elements).

Text:
{text}

{format_instructions}
"""
