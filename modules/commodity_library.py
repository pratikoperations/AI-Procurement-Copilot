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
            "primary_cost_drivers": ["film", "foil", "ink", "adhesive", "conversion"],
            "risk_signals": ["migration compliance", "barrier performance", "cylinder cost", "resin volatility"],
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
            "family": "Metals",
            "unit": "kg",
            "primary_cost_drivers": ["ore", "scrap", "energy", "conversion", "freight"],
            "risk_signals": ["cycle volatility", "mill allocation", "grade substitution", "duty changes"],
        },
        "Copper": {
            "family": "Metals",
            "unit": "kg",
            "primary_cost_drivers": ["LME copper", "fabrication premium", "freight", "FX"],
            "risk_signals": ["mine disruption", "LME volatility", "regional premium", "substitute availability"],
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
