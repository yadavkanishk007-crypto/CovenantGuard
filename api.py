import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Internal modules
from app.models import Covenant, Financials, EvaluationRequest
from app.engine import evaluate_covenant
from app.scoring import aggregate_risk
from app.db_utils import get_db
from app.db_models import Evaluation, CovenantResult, User
from app.reports import generate_pdf, generate_excel
from app.logger import logger
from app.auth_models import UserCreate, UserLogin
from app.security import hash_password, verify_password
from app.token import create_access_token
from app.auth_dependency import get_current_user
from app.intake import intake_spreadsheet  # Consolidated import

router = APIRouter()

# Request Model for Excel Intake
class ExcelIntakeRequest(BaseModel):
    file_path: str

# =========================================================
# AUTH ROUTES (PUBLIC)
# =========================================================

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=user.username,
        hashed_password=hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()

    logger.info(f"New user registered: {user.username} ({user.role})")

    return {"message": "User created successfully"}


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": user.username,
        "role": user.role
    })

    logger.info(f"User logged in: {user.username}")

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role
    }

# =========================================================
# CORE BUSINESS ROUTES (PROTECTED)
# =========================================================

@router.post("/evaluate")
def evaluate(
    payload: EvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "operator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    try:
        results = []
        statuses = []

        # ✅ FIX: extract from payload
        covenants = payload.covenants
        financials = payload.financials

        for covenant in covenants:
            r = evaluate_covenant(covenant, financials)
            results.append(r)
            statuses.append(r.status)

        overall = aggregate_risk(statuses)

        evaluation = Evaluation(
            period=financials.period,
            overall_risk=overall
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)

        for r in results:
            db.add(CovenantResult(
                evaluation_id=evaluation.id,
                covenant_name=r.covenant_name,
                metric=r.metric,
                value=r.value,
                status=r.status
            ))

        db.commit()

        return {
            "evaluation_id": evaluation.id,
            "overall_risk": overall,
            "results": [r.dict() for r in results]
        }

    except Exception as e:
        db.rollback()
        logger.exception("Evaluation failed")
        raise HTTPException(status_code=400, detail=f"Evaluation failed: {str(e)}")

# =========================================================
# DATA INTAKE (PROTECTED)
# =========================================================

@router.post("/intake/excel")
def excel_intake(
    req: ExcelIntakeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Parses an Excel file via the 'intake' module and returns the extracted data
    structure so the frontend can review it before submitting an evaluation.
    """
    # Optional: Add role check here if needed
    try:
        return intake_spreadsheet(req.file_path)
    except Exception as e:
        logger.error(f"Excel intake failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# =========================================================
# HISTORY & AUDIT (PROTECTED)
# =========================================================

@router.get("/evaluations")
def list_evaluations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    evaluations = db.query(Evaluation).all()

    return [
        {
            "id": e.id,
            "period": e.period,
            "overall_risk": e.overall_risk,
            "created_at": e.created_at
        }
        for e in evaluations
    ]


@router.get("/evaluations/{evaluation_id}")
def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()

    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    return {
        "id": evaluation.id,
        "period": evaluation.period,
        "overall_risk": evaluation.overall_risk,
        "created_at": evaluation.created_at,
        "results": [
            {
                "covenant_name": r.covenant_name,
                "metric": r.metric,
                "value": r.value,
                "status": r.status
            }
            for r in evaluation.results
        ]
    }

# =========================================================
# REPORTS (PROTECTED, FILE STREAMING)
# =========================================================

@router.get("/evaluations/{evaluation_id}/report/pdf")
def pdf_report(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()

    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    results = [
        {
            "covenant_name": r.covenant_name,
            "metric": r.metric,
            "value": r.value,
            "status": r.status
        }
        for r in evaluation.results
    ]

    file_path = generate_pdf(
        evaluation.id,
        evaluation.period,
        evaluation.overall_risk,
        results
    )

    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Report generation failed")

    logger.info(
        f"PDF report generated for evaluation {evaluation.id} by {current_user.username}"
    )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_path
    )

@router.get("/evaluations/{evaluation_id}/report/excel")
def excel_report(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    evaluation = db.query(Evaluation).filter(
        Evaluation.id == evaluation_id
    ).first()

    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    results = [
        {
            "covenant_name": r.covenant_name,
            "metric": r.metric,
            "value": r.value,
            "status": r.status
        }
        for r in evaluation.results
    ]

    file_path = generate_excel(
        evaluation.id,
        evaluation.period,
        evaluation.overall_risk,
        results
    )

    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"Covenant_Report_{evaluation.id}.xlsx"
    )
