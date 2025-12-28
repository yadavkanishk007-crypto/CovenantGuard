# app/engine.py
from app.models import Covenant, Financials, EvaluationResult


def evaluate_covenant(covenant: Covenant, data: Financials) -> EvaluationResult:
    """
    Production-grade covenant evaluation engine.
    Explicit, auditable, and schema-safe.
    """

    # Compute metric explicitly (NO getattr, NO magic)
    if covenant.metric == "leverage":
        value = data.debt / data.ebitda
        compliant = value <= covenant.threshold

    elif covenant.metric == "interest_coverage":
        value = data.ebitda / data.interest_expense
        compliant = value >= covenant.threshold

    else:
        raise ValueError(f"Unsupported covenant metric: {covenant.metric}")

    status = "GREEN" if compliant else "RED"

    return EvaluationResult(
        covenant_name=covenant.covenant_name,
        metric=covenant.metric,
        value=round(value, 2),
        status=status
    )
