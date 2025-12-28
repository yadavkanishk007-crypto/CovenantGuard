# app/simulator.py
from app.models import Financials


def simulate(financials: Financials, stress: dict) -> Financials:
    stressed = financials.dict()

    for metric, change in stress.items():
        if metric in stressed:
            stressed[metric] = stressed[metric] * (1 + change)

    return Financials(**stressed)
