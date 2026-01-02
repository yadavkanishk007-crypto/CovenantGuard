import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

# App-specific imports
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
    "period": ["period", "reporting", "quarter", "year", "date"],
    "revenue": ["revenue", "sales", "total revenue"],
    "ebitda": ["ebitda", "operating profit"],
    "debt": ["debt", "total debt", "liabilities"],
    "interest_expense": ["interest", "interest expense", "finance costs"]
}


# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def _get_column_name(df: pd.DataFrame, aliases: List[str]) -> str:
    """
    Finds the actual column header in the dataframe that matches
    one of the provided aliases. Returns None if no match found.
    """
    for col in df.columns:
        # cleanup column name for comparison
        col_clean = str(col).strip().lower()
        for alias in aliases:
            if alias in col_clean:
                return col
    return None


# -------------------------------------------------
# MAIN ENTRY: INTAKE
# -------------------------------------------------

def intake_spreadsheet(file_path: str) -> Dict[str, Any]:
    """
    Batch processes a spreadsheet of companies.
    """

    # 1. Validate file
    if not file_path.lower().endswith(SUPPORTED_FILE_TYPES):
        raise ValueError("Unsupported file type")

    # 2. Load spreadsheet
    df = (
        pd.read_csv(file_path)
        if file_path.lower().endswith(".csv")
        else pd.read_excel(file_path)
    )

    # 3. Map Columns
    # We identify which column corresponds to which field ONCE.
    col_map = {}
    missing_cols = []

    for field, aliases in FIELD_ALIASES.items():
        found_col = _get_column_name(df, aliases)
        if found_col:
            col_map[field] = found_col
        else:
            # We enforce strict requirements for financial columns
            missing_cols.append(field)

    if missing_cols:
        raise ValueError(f"Could not find columns for: {', '.join(missing_cols)}")

    # 4. Process Rows
    processed_count = 0
    errors = []
    success_ids = []

    # Convert to list of dicts for easier iteration
    records = df.to_dict(orient="records")

    for index, row in enumerate(records):
        row_num = index + 2  # identifying Excel row number (header is 1)

        # Create a new DB session per row to isolate transactions
        db: Session = SessionLocal()

        try:
            # --- Extract Data using the map ---
            raw_company = row.get(col_map["company"])
            raw_period = row.get(col_map["period"])
            raw_rev = row.get(col_map["revenue"])
            raw_ebitda = row.get(col_map["ebitda"])
            raw_debt = row.get(col_map["debt"])
            raw_interest = row.get(col_map["interest_expense"])

            # --- Basic Validation ---
            if pd.isna(raw_rev) or pd.isna(raw_ebitda) or pd.isna(raw_debt) or pd.isna(raw_interest):
                raise ValueError("Missing financial data")

            # --- Normalize Identifiers ---
            entity = str(raw_company if not pd.isna(raw_company) else f"Unknown_Row_{row_num}").strip()
            period = str(raw_period if not pd.isna(raw_period) else datetime.utcnow().year).strip()

            # Create a unique reporting ID
            reporting_id = f"{entity}-{period}"

            financials = {
                "period": reporting_id,
                "revenue": float(raw_rev),
                "ebitda": float(raw_ebitda),
                "debt": float(raw_debt),
                "interest_expense": float(raw_interest)
            }

            # --- Auto Covenants ---
            # Prevent division by zero
            debt_to_ebitda = financials["debt"] / financials["ebitda"] if financials["ebitda"] != 0 else 0.0
            interest_coverage = financials["ebitda"] / financials["interest_expense"] if financials["interest_expense"] != 0 else 0.0

            covenants = [
                {
                    "covenant_name": "Leverage",
                    "metric": "leverage",
                    "threshold": 3.0,
                    "actual": debt_to_ebitda,
                    "frequency": "Quarterly"
                },
                {
                    "covenant_name": "Interest Coverage",
                    "metric": "interest_coverage",
                    "threshold": 1.5,
                    "actual": interest_coverage,
                    "frequency": "Quarterly"
                }
            ]

            # --- Run Engine ---
            results = []
            statuses = []
            for covenant in covenants:
                r = evaluate_covenant(covenant, financials)
                results.append(r)
                statuses.append(r.status)

            overall_risk = aggregate_risk(statuses)

            # --- Persist Safely ---
            evaluation = Evaluation(
                period=financials["period"],
                overall_risk=overall_risk
            )
            db.add(evaluation)
            db.commit()
            db.refresh(evaluation)

            for r in results:
                db.add(
                    CovenantResult(
                        evaluation_id=evaluation.id,
                        covenant_name=r.covenant_name,
                        metric=r.metric,
                        value=r.value,
                        status=r.status
                    )
                )
            db.commit()

            # Track success
            success_ids.append(evaluation.id)
            processed_count += 1

        except Exception as e:
            db.rollback()
            errors.append(f"Row {row_num} ({str(row.get(col_map.get('company'), 'Unknown'))}): {str(e)}")

        finally:
            db.close()

    # 5. Final Response
    return {
        "status": "COMPLETED",
        "total_processed": processed_count,
        "total_errors": len(errors),
        "evaluation_ids": success_ids,
        "error_log": errors
    }


# -------------------------------------------------
# REPORT GENERATOR
# -------------------------------------------------

def generate_batch_report(evaluation_ids: List[int], output_filename="Master_Covenant_Report.xlsx") -> str:
    """
    Generates a single Excel file summarizing all processed companies.
    """
    db = SessionLocal()
    master_data = []

    try:
        # 1. Fetch all evaluations in one go
        evaluations = db.query(Evaluation).filter(Evaluation.id.in_(evaluation_ids)).all()

        for ev in evaluations:
            # 2. Extract base record
            row = {
                "Evaluation ID": ev.id,
                "Entity-Period": ev.period,
                "Overall Risk": ev.overall_risk,
            }

            # 3. Flatten Covenant Results into columns
            results = db.query(CovenantResult).filter(CovenantResult.evaluation_id == ev.id).all()

            for res in results:
                row[f"{res.covenant_name} (Actual)"] = res.value
                row[f"{res.covenant_name} (Status)"] = res.status

            master_data.append(row)

    finally:
        db.close()

    # 4. Create DataFrame and export
    if not master_data:
        return None

    df = pd.DataFrame(master_data)

    # Optional: Reorder columns to put Entity and Risk first
    cols = ["Entity-Period", "Overall Risk"] + [c for c in df.columns if c not in ["Entity-Period", "Overall Risk", "Evaluation ID"]]
    df = df[cols]

    output_path = f"reports/{output_filename}"
    df.to_excel(output_path, index=False)

    return output_path
