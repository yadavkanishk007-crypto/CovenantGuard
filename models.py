from pydantic import BaseModel
from typing import Literal 


class Covenant(BaseModel):
    covenant_name: str
    metric: Literal["leverage", "interest_coverage"]
    threshold: float

class Financials(BaseModel):
    period: str
    revenue: float
    ebitda: float
    debt: float
    interest_expense: float


class EvaluationResult(BaseModel):
    covenant_name: str
    metric: str
    value: float
    status: str

class EvaluationRequest(BaseModel):
    covenants: list[Covenant]
    financials: Financials

