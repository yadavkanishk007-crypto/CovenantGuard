def aggregate_risk(results: list[str]) -> str:
    """
    Normalize covenant statuses into overall risk.
    Engine uses: GREEN / RED
    System stores: LOW / HIGH
    """

    if "RED" in results:
        return "HIGH"

    return "LOW"
