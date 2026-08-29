import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="BudgetWise AI Cloud Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EWMARequest(BaseModel):
    samples: List[float]
    alpha: float = 0.35
    total_budget: float
    current_expenses: float
    current_day: int
    target_days: int = 14

class TaxRequest(BaseModel):
    hourly_wage: float
    hours_worked: float
    country_name: str

def calculate_ewma(samples: List[float], alpha: float = 0.35) -> float:
    if not samples:
        return 0.0
    ewma = samples[0]
    for s in samples[1:]:
        ewma = (alpha * s) + ((1 - alpha) * ewma)
    return ewma

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "BudgetWise-AI Engine"}

@app.post("/api/ewma/predict")
def predict_burn_rate(payload: EWMARequest):
    v_ewma = calculate_ewma(payload.samples, payload.alpha)
    days_left = max(payload.target_days - payload.current_day, 1)
    projected_total = payload.current_expenses + (v_ewma * days_left)
    safe_daily_limit = max((payload.total_budget - payload.current_expenses) / days_left, 0.0)
    
    return {
        "daily_burn_velocity": round(v_ewma, 2),
        "projected_fortnight_spend": round(projected_total, 2),
        "deficit": round(max(projected_total - payload.total_budget, 0.0), 2),
        "safe_daily_limit": round(safe_daily_limit, 2),
        "is_breaching": projected_total > payload.total_budget
    }

@app.post("/api/tax/calculate")
def compute_tax(payload: TaxRequest):
    gross_fn = payload.hourly_wage * payload.hours_worked
    annual_gross = gross_fn * 26.0
    
    # Statutory ATO Australia model
    if "australia" in payload.country_name.lower():
        taxable = max(annual_gross - 18200, 0.0)
        annual_tax = taxable * 0.16 if taxable <= 26800 else (4288 + (taxable - 26800) * 0.30)
        pension = annual_gross * 0.115
    else:
        annual_tax = annual_gross * 0.12
        pension = 0.0
        
    tax_fn = annual_tax / 26.0
    return {
        "gross_fortnight": round(gross_fn, 2),
        "tax_withheld": round(tax_fn, 2),
        "net_takehome": round(max(gross_fn - tax_fn, 0.0), 2),
        "pension_contribution": round(pension / 26.0, 2)
    }