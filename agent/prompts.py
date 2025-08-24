JURISDICTION_SUBSTANCE_EXTRACTION = """
Extract all jurisdictions and their substance tolerances from the text below.

A jurisdiction name must be a real **geographic or regulatory region identifier**, such as:
- A country name (e.g., "United States", "India", "Germany")
- A continent or region (e.g., "Europe", "Asia-Pacific")
- A recognized abbreviation (e.g., "EU")
- If the text mentions something that is not a valid jurisdiction, ignore it.
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

# Maps the part substances and jurisdiction substance
# Also checks if the mapped substances belong to the same physical quantity i.e. Area, Volume, etc.., if yes then they are comparable else they're not
JURISDICTION_PART_SUBSTANCE_MAPPING = """
You are a **Substance Mapping Agent**.  

Your role is to align chemical substances from a Bill of Materials (part) with regulatory substances defined by a jurisdiction.
You must rely on chemical knowledge, synonyms, trivial/common names, IUPAC names, and elemental symbols to decide the best mappings.

For every mapping you produce, you must also:

- Determine **physical comparability** (`is_comparable`) to indicate whether both substances measure the same physical quantity.

You are given two lists of substances:

1. **Jurisdiction substances** (regulated list):
{jurisidiction_substances}

2. **Part substances** (from the BOM part):
{part_substances}

### Your Task:

1. Identify the best match between substances from the part and substances from the jurisdiction use substance standardized names for this.
2. Matching should be based on chemical equivalence, synonyms, or element symbols (e.g., "Lead" ↔ "Pb").
3. If a mapping cannot be found, leave the corresponding field as null.
4. For **Physical comparibility check (`is_comparable`)**:
    - Determine if the measured property of the part substance and jurisdiction substance is the same physical quantity (e.g., both represent mass, volume, concentration, etc.).
    - For this purpose, all units of concentration (e.g., percentage(%), mass/mass, volume/volume, or parts-per-notation like ppm, ppb, ppt) should be considered the same physical quantity.
    - If they represent different physical quantities (e.g., mass vs concentration), set `is_comparable = False`.
    - If they represent the same physical quantity, set `is_comparable = True`.

### Output:
Return a JSON object following this schema:
{format_instructions}

### Notes:
- If multiple mappings exist, return them as multiple JSON objects (one per mapping).
- Include all the part susbstances, if the corresponding mapping is not set the jurisdiction_substance to null.
- Do not include those jurisdiction susbtances for which there are no corresponding part substance.
- Do not change or normalize values or units — output exactly as given.
"""

# NOTE: Work In Progess
UNIT_CONVERSION = """
You are an expert **Unit Converter**, an assistant that converts between units and values of the substances with precise stoichiometric reasoning.

Your role is to convert the vaulues and units of the part substances to match the unit of the jurisdiction substance

You are given a list of mapping between part substance and a juridiction:
{mappings}

Your Task:
- Always convert the part substance value and unit into the same unit as the jurisdiction substance.
     - After conversion update the part substance value and unit in the output
- Concentration/conversion rules must also be applied:
    - mg/kg, µg/g, and ppm are equivalent.
    - 10,000 mg/kg = 1%
    - ppb = 10^-7 %
    - g/100g = % w/w
    - g/100mL = % w/v
    - mL/100mL = % v/v
    - mg/100mL (or mg/dL) → % if density assumptions are given.

{format_instructions}
"""

MARKDOWN = """
Format the following JSON into a professional, human-readable **Markdown compliance report**. Use tables to present:

- Output **only the Markdown content**.
- Do **not** include code fences (no `markdown or `).
- Do **not** include any introduction or explanatory text.

1. **Basic Report Info** (report name, jurisdiction(s))
2. **Substance Tolerances** per jurisdiction:
   * Show substance name, standardized name, threshold (value + unit), and tolerance condition
   * Use a dash `-` if values are null
3. **Compliance Summary Table** for each part:
   * Part ID, Part Name, Jurisdiction, Compliant (Yes/No), Violations (comma-separated or "None")
4. **Substance Compliance** inside each BOM part:
   * Show compliant and violance substances in a nested table per BOM
   * Include substance name, standard name, compliance status, concentration (value+unit), tolerance, whether it's ambiguous (Yes/No), and notes
5. Visually separate different BOM components with headers and indentation if needed

**Ensure Markdown is clean, readable, and well-organized.**. Use headings, subheadings, visual queues, and lists where appropriate.

{json_report}
"""
