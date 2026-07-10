"""Supplier allocation module placeholder for Build 0.2."""


def placeholder_allocation(primary_supplier, backup_supplier=None):
    """Return a simple starter allocation split."""
    if backup_supplier:
        return [
            {"Supplier": primary_supplier, "Allocation %": 75, "Role": "Primary"},
            {"Supplier": backup_supplier, "Allocation %": 25, "Role": "Backup"},
        ]
    return [{"Supplier": primary_supplier, "Allocation %": 100, "Role": "Primary"}]
