import pandas as pd
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.db_models import Evaluation, CovenantResult
from app.engine import evaluate_covenant, aggregate_risk
from app.reports import generate_excel


# -------------------------------------------------
# CONFIG
# -------------------------------------------------

SUPPORTED_FILE_TYPES = (".xlsx", ".xls", ".csv")

FIELD_ALIASES = {
    "company": ["company", "borrower", "entity", "name"],
    "period": ["period", "reporting", "quarter", "year"],
    "revenue": ["revenue"],
    "ebitda": ["ebitda"],
    "debt": ["debt", "total debt"],
    "interest_expense": ["interest", "interest expense"]
}


# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def _extract_value(df: pd.DataFrame, aliases):
    """
    Extracts the first non-null value whose column name
    loosely matches any alias.
    """
    for col in df.columns:
        for alias in aliases:
            if alias in col.lower():
                series = df[col].dropna()
                if not series.empty:
                    return series.iloc[0]
    return None


# -------------------------------------------------
# MAIN ENTRY
# -------------------------------------------------

def intake_spreadsheet(file_path: str) -> Dict[str, Any]:
    """
    Fully automated Excel/CSV intake pipeline.
    """

    # -------------------------
    # 1. Validate file
    # -------------------------
    if not file_path.lower().endswith(SUPPORTED_FILE_TYPES):
        raise ValueError("Unsupported file type")

    # -------------------------
    # 2. Load spreadsheet
    # -------------------------
    df = (
        pd.read_csv(file_path)
        if file_path.lower().endswith(".csv")
        else pd.read_excel(file_path)
    )

    df.columns = [str(c).strip().lower() for c in df.columns]

    # -------------------------
    # 3. Extract fields
    # -------------------------
    company = _extract_value(df, FIELD_ALIASES["company"])
    period = _extract_value(df, FIELD_ALIASES["period"])

    revenue = _extract_value(df, FIELD_ALIASES["revenue"])
    ebitda = _extract_value(df, FIELD_ALIASES["ebitda"])
    debt = _extract_value(df, FIELD_ALIASES["debt"])
    interest = _extract_value(df, FIELD_ALIASES["interest_expense"])

    # -------------------------
    # 4. Validate financials
    # -------------------------
    missing = []
    if revenue is None: missing.append("Revenue")
    if ebitda is None: missing.append("EBITDA")
    if debt is None: missing.append("Debt")
    if interest is None: missing.append("Interest Expense")

    if missing:
        raise ValueError(f"Missing required financial fields: {missing}")

    # -------------------------
    # 5. Normalize identifiers
    # -------------------------
    entity = str(company or "Entity").strip()
    period = str(period or datetime.utcnow().year).strip()
    reporting_id = f"{entity}-{period}"

    financials = {
        "period": reporting_id,
        "revenue": float(revenue),
        "ebitda": float(ebitda),
        "debt": float(debt),
        "interest_expense": float(interest)
    }

    # -------------------------
    # 6. Auto covenants
    # -------------------------
    covenants = [
        {
            "covenant_name": "Leverage",
            "metric": "leverage",
            "threshold": 3.0,
            "actual": financials["debt"] / financials["ebitda"],
            "frequency": "Quarterly"
        },
        {
            "covenant_name": "Interest Coverage",
            "metric": "interest_coverage",
            "threshold": 1.5,
            "actual": financials["ebitda"] / financials["interest_expense"],
            "frequency": "Quarterly"
        }
    ]

    # -------------------------
    # 7. Run engine
    # -------------------------
    results = []
    statuses = []

    for covenant in covenants:
        r = evaluate_covenant(covenant, financials)
        results.append(r)
        statuses.append(r.status)

    overall_risk = aggregate_risk(statuses)

    # -------------------------
    # 8. Persist safely
    # -------------------------
    db: Session = SessionLocal()

    try:
        evaluation = Evaluation(
            period=financials["period"],
            overall_risk=overall_risk
        )
        db.add(evaluation)
        db.commit()

        # 🔐 Ensure ID is loaded before session close
        db.refresh(evaluation)
        evaluation_id = evaluation.id

        for r in results:
            db.add(
                CovenantResult(
                    evaluation_id=evaluation_id,
                    covenant_name=r.covenant_name,
                    metric=r.metric,
                    value=r.value,
                    status=r.status
                )
            )

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    # -------------------------
    # 9. Generate Excel report
    # -------------------------
    report_path = generate_excel(
        evaluation_id,
        financials["period"],
        overall_risk,
        [r.dict() for r in results]
    )

    # -------------------------
    # 10. Response
    # -------------------------
    return {
        "status": "SUCCESS",
        "evaluation_id": evaluation_id,
        "period": financials["period"],
        "overall_risk": overall_risk,
        "report": report_path
    }
