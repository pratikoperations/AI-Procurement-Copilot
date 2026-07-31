"""Category and commodity metadata for procurement intelligence."""

COMMODITIES = {
    "Packaging Procurement": {
        "Corrugated Board": {
            "family": "Paper Packaging",
            "unit": "piece",
            "primary_cost_drivers": ["kraft paper", "conversion", "printing", "freight"],
            "risk_signals": ["paper index volatility", "moisture", "compression strength", "MOQ"],
        },
        "Flexible Laminates": {
            "family": "Flexible Packaging",
            "unit": "kg",
            "structures": ["PET / PE", "PET / MetPET / PE", "BOPP / CPP"],
            "print_profiles": ["Unprinted", "Up to 4 colours", "5–8 colours"],
            "print_processes": ["Rotogravure", "Flexographic"],
            "adhesive_types": ["Solvent-based", "Solvent-free"],
            "primary_cost_drivers": ["substrates", "ink", "adhesive", "printing", "lamination", "process loss", "tooling", "freight"],
            "risk_signals": ["substrate availability", "print capability", "lamination capability", "tooling dependency", "process loss"],
            "assumption_profile_version": "C2.0",
            "source_label": "Synthetic controlled demonstration assumptions",
        },
        "PET Bottles": {
            "family": "Rigid Packaging",
            "unit": "piece",
            "primary_cost_drivers": ["PET resin", "preform", "blowing", "freight"],
            "risk_signals": ["resin volatility", "mould dependency", "transport cube", "food compliance"],
        },
        "Labels": {
            "family": "Printed Packaging",
            "unit": "piece",
            "primary_cost_drivers": ["facestock", "adhesive", "liner", "printing", "finishing"],
            "risk_signals": ["artwork control", "adhesive performance", "colour variation", "MOQ"],
        },
    },
    "Raw Material Procurement": {
        "PET Resin": {
            "family": "Polymers",
            "unit": "kg",
            "primary_cost_drivers": ["commodity index", "conversion premium", "freight", "duty", "FX"],
            "risk_signals": ["oil linkage", "import dependency", "FX exposure", "single-source concentration"],
        },
        "Polyethylene": {
            "family": "Polymers",
            "unit": "kg",
            "primary_cost_drivers": ["ethylene index", "producer premium", "freight", "duty"],
            "risk_signals": ["feedstock volatility", "plant outage", "grade substitution", "allocation risk"],
        },
        "Polypropylene": {
            "family": "Polymers",
            "unit": "kg",
            "primary_cost_drivers": ["propylene index", "producer premium", "freight", "duty"],
            "risk_signals": ["feedstock volatility", "capacity outage", "grade qualification", "import exposure"],
        },
        "Aluminium Foil": {
            "family": "Metals",
            "unit": "kg",
            "primary_cost_drivers": ["LME aluminium", "conversion premium", "energy", "freight", "FX"],
            "risk_signals": ["LME volatility", "energy cost", "gauge availability", "trade restrictions"],
        },
        "Steel": {
            "family": "Metals — Steel Sheets and Coils",
            "unit": "kg",
            "reporting_unit": "metric tonnes",
            "calculation_currency": "USD",
            "comparison_unit": "USD/kg",
            "display_modes": ["USD", "INR", "Both"],
            "accepted_quote_currencies": ["USD", "INR"],
            "fx_source_label": "User-controlled demonstration assumption; not live market data",
            "profiles": {
                "CR_COIL_COMMERCIAL": {
                    "display_name": "Cold-Rolled Steel Coil",
                    "grade_family": "Controlled CR commercial-quality demonstration family",
                    "thickness_mm": 0.80,
                    "width_min_mm": 1000,
                    "width_max_mm": 1250,
                    "zinc_coating_gsm": 0,
                    "topcoat_micron": 0,
                    "backcoat_micron": 0,
                    "surface_requirement": "Controlled commercial finish",
                    "coil_weight_band_mt": [5, 15],
                },
                "GI_COIL_Z120": {
                    "display_name": "Galvanized Steel Coil",
                    "grade_family": "Controlled GI substrate demonstration family",
                    "thickness_mm": 0.60,
                    "width_min_mm": 1000,
                    "width_max_mm": 1250,
                    "zinc_coating_gsm": 120,
                    "topcoat_micron": 0,
                    "backcoat_micron": 0,
                    "surface_requirement": "Controlled galvanized finish",
                    "coil_weight_band_mt": [5, 15],
                },
                "PPGI_COIL_Z120": {
                    "display_name": "Pre-Painted Galvanized Steel Coil",
                    "grade_family": "Controlled PPGI substrate demonstration family",
                    "thickness_mm": 0.50,
                    "width_min_mm": 1000,
                    "width_max_mm": 1250,
                    "zinc_coating_gsm": 120,
                    "topcoat_micron": 20,
                    "backcoat_micron": 5,
                    "surface_requirement": "Controlled pre-painted finish",
                    "coil_weight_band_mt": [4, 12],
                },
            },
            "primary_cost_drivers": [
                "base steel", "grade premium", "rolling and conversion", "zinc coating",
                "paint treatment", "energy", "yield loss", "slitting", "packing",
                "freight", "duty", "supplier margin",
            ],
            "risk_signals": [
                "steel index volatility", "mill allocation", "grade substitution",
                "energy exposure", "coating-line dependency", "import dependency",
                "FX exposure", "duty changes", "capacity utilisation", "quality continuity",
            ],
            "assumption_profile_version": "C3.1-STEEL-v1",
            "source_label": "Synthetic controlled demonstration assumptions; not metallurgical certification or engineering approval",
        },
        "Copper": {
            "family": "Metals",
            "unit": "kg",
            "primary_cost_drivers": ["LME copper", "fabrication premium", "freight", "FX"],
            "risk_signals": ["mine disruption", "LME volatility", "regional premium", "substitute availability"],
        },
        "Kraft Paper": {
            "family": "Paper and Fibre",
            "unit": "kg",
            "variants": ["Recycled Kraft", "Virgin Kraft"],
            "gsm_profiles": [120, 150, 180],
            "strength_profiles": ["18 BF", "22 BF", "28 BF"],
            "primary_cost_drivers": ["paper index", "mill premium", "freight", "grade premium", "supplier margin"],
            "risk_signals": ["mill allocation", "moisture variation", "recycled fibre availability", "quality continuity"],
            "downstream_link": "Corrugated Board",
            "assumption_profile_version": "C1.0",
            "source_label": "Synthetic controlled demonstration assumptions",
        },
    },
}


def get_categories():
    """Return supported procurement categories."""
    return list(COMMODITIES.keys())


def get_commodities(category):
    """Return commodities available for a category."""
    return list(COMMODITIES.get(category, {}).keys())


def get_commodity_profile(category, commodity):
    """Return metadata for a category and commodity combination."""
    return COMMODITIES.get(category, {}).get(commodity, {})
