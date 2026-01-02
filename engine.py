# app/engine.py
from app.models import Covenant, Financials, EvaluationResult


# -----------------------------
# INTERNAL NORMALIZERS
# -----------------------------

def _as_covenant(c):
    """Accept Covenant model or dict."""
    if isinstance(c, Covenant):
        return c
    if isinstance(c, dict):
        return Covenant(**c)
    raise TypeError("Invalid covenant input")


def _as_financials(f):
    """Accept Financials model or dict."""
    if isinstance(f, Financials):
        return f
    if isinstance(f, dict):
        return Financials(**f)
    raise TypeError("Invalid financials input")


# -----------------------------
# CORE ENGINE
# -----------------------------

def evaluate_covenant(covenant, data) -> EvaluationResult:
    """
    Production-grade covenant evaluation engine.
    Accepts dicts or Pydantic models.
    Deterministic, auditable, and safe.
    """

    covenant = _as_covenant(covenant)
    data = _as_financials(data)

    # Defensive numeric guards
    if covenant.metric == "leverage":
        if not data.ebitda or data.ebitda == 0:
            raise ValueError("EBITDA cannot be zero for leverage calculation")

        value = data.debt / data.ebitda
        compliant = value <= covenant.threshold

    elif covenant.metric == "interest_coverage":
        if not data.interest_expense or data.interest_expense == 0:
            raise ValueError("Interest expense cannot be zero")

        value = data.ebitda / data.interest_expense
        compliant = value >= covenant.threshold

    else:
        raise ValueError(f"Unsupported covenant metric: {covenant.metric}")

    status = "PASS" if compliant else "BREACH"

    return EvaluationResult(
        covenant_name=covenant.covenant_name,
        metric=covenant.metric,
        value=round(value, 2),
        status=status
    )


# -----------------------------
# RISK AGGREGATION
# -----------------------------

def aggregate_risk(statuses):
    """
    Aggregates covenant statuses into overall risk.
    Consistent with engine output.
    """

    if not statuses:
        return "UNKNOWN"

    if "BREACH" in statuses:
        return "HIGH"

    return "LOW"
