
import pandas as pd
from datetime import datetime
from typing import Dict, Any
from .engine import evaluate_covenant
from .reports import generate_excel


# =========================
# CONFIGURATION CONTRACT
# =========================

SUPPORTED_FILE_TYPES = (".xlsx", ".xls", ".csv")

COLUMN_MAP = {
    # Loan / Facility
    "Loan ID": "loan_id",
    "Facility ID": "facility_id",
    "Borrower Name": "borrower",

    # Financials
    "DSCR": "dscr",
    "Leverage": "leverage",
    "Interest Coverage": "interest_coverage",

    # Covenant
    "Covenant Name": "name",
    "Covenant Type": "type",
    "Threshold": "threshold",
    "Actual Value": "actual",
    "Frequency": "frequency",
    "Observation Date": "observation_date",

    # Optional
    "Comments": "comments"
}

REQUIRED_COLUMNS = [
    "Loan ID",
    "Covenant Name",
    "Threshold",
    "Actual Value"
]


# =========================
# CORE INTAKE FUNCTION
# =========================

def intake_spreadsheet(file_path: str) -> Dict[str, Any]:
    """
    Primary entrypoint for desktop application.
    Pass a local file path. Returns scored & simulated output.
    """

    # -------------------------
    # 1. FILE VALIDATION
    # -------------------------
    if not file_path.lower().endswith(SUPPORTED_FILE_TYPES):
        raise ValueError("Unsupported file type. Use Excel or CSV.")

    # -------------------------
    # 2. LOAD SPREADSHEET
    # -------------------------
    df = (
        pd.read_csv(file_path)
        if file_path.lower().endswith(".csv")
        else pd.read_excel(file_path)
    )

    # -------------------------
    # 3. COLUMN VALIDATION
    # -------------------------
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # -------------------------
    # 4. NORMALIZE COLUMNS
    # -------------------------
    df = df.rename(columns=COLUMN_MAP)
    df = df.fillna("")

    # -------------------------
    # 5. BASIC DATA VALIDATION
    # -------------------------
    validation_errors = []
    for idx, row in df.iterrows():
        if float(row["threshold"]) < 0:
            validation_errors.append((idx, "Threshold cannot be negative"))
        if float(row["actual"]) < 0:
            validation_errors.append((idx, "Actual value cannot be negative"))

    if validation_errors:
        return {
            "status": "FAILED",
            "errors": validation_errors
        }

    # -------------------------
    # 6. BUILD ENGINE PAYLOAD
    # -------------------------
    payload = {
        "meta": {
            "source": "excel_intake",
            "file": file_path,
            "ingested_at": datetime.utcnow().isoformat()
        },
        "loan": {
            "loan_id": df["loan_id"].iloc[0],
            "facility_id": df.get("facility_id", [""])[0],
            "borrower": df.get("borrower", [""])[0]
        },
        "financials": {
            "dscr": _safe_float(df.get("dscr")),
            "leverage": _safe_float(df.get("leverage")),
            "interest_coverage": _safe_float(df.get("interest_coverage"))
        },
        "covenants": df[
            ["name", "type", "threshold", "actual", "frequency", "observation_date", "comments"]
        ].to_dict(orient="records")
    }

    # -------------------------
    # 7. RUN ENGINE
    # -------------------------
    engine_result = run_engine(payload)

    # -------------------------
    # 8. GENERATE REPORT
    # -------------------------
    report_path = generate_report(engine_result)

    # -------------------------
    # 9. RETURN FINAL OUTPUT
    # -------------------------
    return {
        "status": "SUCCESS",
        "loan_id": payload["loan"]["loan_id"],
        "risk_score": engine_result.get("risk_score"),
        "breaches": engine_result.get("breaches"),
        "report": report_path
    }


# =========================
# INTERNAL UTIL
# =========================

def _safe_float(series):
    try:
        return float(series.iloc[0]) if series is not None else None
    except Exception:
        return None
