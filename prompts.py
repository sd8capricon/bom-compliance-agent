JURISDICTION_EXTRACTION = """
Extract all jurisdictions and their substance tolerances from the text below.

A jurisdiction name must be a valid **geographic or regulatory region identifier**, such as:
- A country name (e.g., "United States", "India", "Germany")
- A continent or region (e.g., "Europe", "Asia-Pacific")
- A recognized abbreviation (e.g., "EU")
Do NOT use product names, company names, or generic terms as jurisdiction names.

Rules:
1. Do NOT repeat jurisdictions — if a jurisdiction appears more than once, merge their substances into one.
2. Do NOT repeat substances within the same jurisdiction — keep only one entry for each substance name.
3. Substance tolerances must include the value and unit where available; if missing, leave as null.
4. Only extract jurisdiction name that clearly refer to a country, region, continent, or regulatory body abbreviation.

Text:
{text}

{format_instructions}
"""
