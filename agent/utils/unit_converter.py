class UnitConverter:
    # Base units for categories
    BASES = {
        "weight": "kg",
        "distance": "m",
        "area": "m²",
        "volume": "m³",
        "concentration": "%",  # concentration conversions are special
    }

    # Conversion factors to base units (category, factor)
    FACTORS = {
        # Weight (base = kg)
        "mg": ("weight", 1e-6),
        "g": ("weight", 1e-3),
        "kg": ("weight", 1),
        "tonne": ("weight", 1000),
        "lb": ("weight", 0.45359237),
        "oz": ("weight", 0.0283495),
        # Distance (base = m)
        "mm": ("distance", 0.001),
        "cm": ("distance", 0.01),
        "m": ("distance", 1),
        "km": ("distance", 1000),
        "in": ("distance", 0.0254),
        "ft": ("distance", 0.3048),
        "yd": ("distance", 0.9144),
        "mi": ("distance", 1609.344),
        # Area (base = m²)
        "mm²": ("area", 1e-6),
        "cm²": ("area", 1e-4),
        "m²": ("area", 1),
        "km²": ("area", 1e6),
        "in²": ("area", 0.00064516),
        "ft²": ("area", 0.092903),
        "yd²": ("area", 0.836127),
        "acre": ("area", 4046.86),
        # Volume (base = m³)
        "m³": ("volume", 1),
        "cm³": ("volume", 1e-6),
        "mm³": ("volume", 1e-9),
        "L": ("volume", 0.001),
        "mL": ("volume", 1e-6),
        "in³": ("volume", 1.6387e-5),
        "ft³": ("volume", 0.0283168),
        "gallon": ("volume", 0.00378541),
        "pint": ("volume", 0.000473176),
        "cup": ("volume", 0.000236588),
        # Concentration (special: % ↔ ppm)
        "%": ("concentration", None),
        "mg/kg": ("concentration", None),
        "ppm": ("concentration", None),
    }

    @classmethod
    def convert(cls, value: float, from_unit: str, to_unit: str) -> float:
        from_unit = from_unit.strip()
        to_unit = to_unit.strip()

        if from_unit == to_unit:
            return value

        # Handle concentration separately
        if (
            cls.FACTORS[from_unit][0] == "concentration"
            or cls.FACTORS[to_unit][0] == "concentration"
        ):
            return cls._convert_concentration(value, from_unit, to_unit)

        cat_from, factor_from = cls.FACTORS[from_unit]
        cat_to, factor_to = cls.FACTORS[to_unit]

        if cat_from != cat_to:
            raise ValueError(f"Incompatible units: {from_unit} vs {to_unit}")

        # convert to base, then to target
        base_value = value * factor_from
        return base_value / factor_to

    @staticmethod
    def _convert_concentration(value: float, from_unit: str, to_unit: str) -> float:
        # Normalize synonyms
        aliases = {"percent": "%", "ppm": "mg/kg"}
        from_unit = aliases.get(from_unit, from_unit)
        to_unit = aliases.get(to_unit, to_unit)

        # 1% = 10000 mg/kg
        if from_unit == "%" and to_unit in ("mg/kg", "ppm"):
            return value * 10000
        if from_unit in ("mg/kg", "ppm") and to_unit == "%":
            return value / 10000
        if from_unit in ("mg/kg", "ppm") and to_unit in ("mg/kg", "ppm"):
            return value
        if from_unit == "%" and to_unit == "%":
            return value

        raise ValueError(
            f"Unsupported concentration conversion: {from_unit} -> {to_unit}"
        )
