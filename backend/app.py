import os
import json
import base64
import urllib.request
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import numpy as np

try:
    from models.ai_engine import StudentAIEngine
except ImportError:
    try:
        from models.ai_engine import StudentAIEngine
    except ImportError:
        StudentAIEngine = None

app = FastAPI(
    title="BudgetWise-AI Cloud Engine",
    version="2.0.0",
    description="Custom Machine Learning, Ordinary Least Squares Velocity, and Statutory Compliance"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Custom NLP Classifier & Risk Heuristic
nlp_engine = StudentAIEngine() if StudentAIEngine else None

# 2. Custom Ordinary Least Squares (OLS) Math Engine
class FinancialMathModel:
    def __init__(self, total_fortnight_days=14):
        self.total_days = total_fortnight_days

    def calculate_spend_velocity(self, daily_expenses_dict, current_day):
        if not daily_expenses_dict or current_day <= 1:
            return 0.0, 0.0

        days = np.array(list(daily_expenses_dict.keys()), dtype=float)
        expenses = np.array(list(daily_expenses_dict.values()), dtype=float)
        cumulative_expenses = np.cumsum(expenses)

        N = len(days)
        X = np.vstack([days, np.ones(N)]).T

        try:
            m, c = np.linalg.lstsq(X, cumulative_expenses, rcond=None)[0]
            return float(m), float(c)
        except np.linalg.LinAlgError:
            return 0.0, 0.0

    def forecast_end_of_fortnight(self, current_day, current_expenses, accrued_budget, daily_expenses_dict):
        days_remaining = max(self.total_days - current_day, 1)
        burn_rate, _ = self.calculate_spend_velocity(daily_expenses_dict, current_day)

        if burn_rate <= 0:
            burn_rate = current_expenses / max(current_day, 1)

        projected_total_expense = current_expenses + (burn_rate * days_remaining)
        projected_deficit = projected_total_expense - accrued_budget
        remaining_balance = accrued_budget - current_expenses
        safe_daily_limit = max(remaining_balance / days_remaining, 0.0)

        return {
            "burn_rate_per_day": round(burn_rate, 2),
            "projected_total_expense": round(projected_total_expense, 2),
            "projected_deficit": round(max(projected_deficit, 0.0), 2),
            "safe_daily_limit": round(safe_daily_limit, 2),
            "is_solvent": projected_total_expense <= accrued_budget
        }

ols_math_engine = FinancialMathModel(total_fortnight_days=14)

class CategorizationRequest(BaseModel):
    description: str

class RiskCheckRequest(BaseModel):
    proposed_amount: float
    total_budget: float
    current_expenses: float
    days_remaining: int

class OLSVelocityRequest(BaseModel):
    daily_expenses: Dict[int, float]
    current_day: int
    current_expenses: float
    accrued_budget: float
    proposed_amount: float = 0.0

class TaxRequest(BaseModel):
    hourly_wage: float
    hours_worked: float
    country_name: str
    claim_allowance: bool = True

# ----------------- API ENDPOINTS -----------------
@app.get("/health")
def health_check():
    return {
        "status": "operational",
        "models_loaded": {
            "nlp_classifier": nlp_engine is not None,
            "least_squares_velocity": True,
            "statutory_tax_engine": True
        }
    }

@app.post("/api/model/classify")
def classify_transaction(payload: CategorizationRequest):
    if not nlp_engine:
        raise HTTPException(status_code=503, detail="StudentAIEngine model not loaded.")
    category = nlp_engine.predict_category(payload.description)
    return {
        "description": payload.description,
        "predicted_category": category,
        "model": "TF-IDF + Multinomial Naive Bayes"
    }

@app.post("/api/model/spending-risk")
def evaluate_spending_risk(payload: RiskCheckRequest):
    if not nlp_engine:
        raise HTTPException(status_code=503, detail="StudentAIEngine model not loaded.")
    risk_score, message = nlp_engine.predict_spending_risk(
        proposed_amount=payload.proposed_amount,
        total_budget=payload.total_budget,
        current_expenses=payload.current_expenses,
        days_remaining=payload.days_remaining
    )
    return {
        "risk_score": risk_score,
        "assessment": message,
        "is_acceptable": risk_score <= 40.0
    }

@app.post("/api/model/ols-velocity")
def evaluate_ols_velocity(payload: OLSVelocityRequest):
    forecast = ols_math_engine.forecast_end_of_fortnight(
        current_day=payload.current_day,
        current_expenses=payload.current_expenses + payload.proposed_amount,
        accrued_budget=payload.accrued_budget,
        daily_expenses_dict=payload.daily_expenses
    )
    return {
        "mathematical_model": "Ordinary Least Squares (OLS) Linear Regression",
        "forecast": forecast,
        "status": "SOLVENT" if forecast["is_solvent"] else "DEFICIT_WARNING"
    }

@app.post("/api/tax/calculate")
def compute_tax(payload: TaxRequest):
    gross_fn = payload.hourly_wage * payload.hours_worked
    annual_gross = gross_fn * 26.0
    c_name = payload.country_name.lower()

    if "australia" in c_name:
        if payload.claim_allowance:
            tax = 0.0 if annual_gross <= 18200 else (annual_gross - 18200) * 0.16 if annual_gross <= 45000 else 4288 + (annual_gross - 45000) * 0.30
        else:
            tax = annual_gross * 0.30
        pension = annual_gross * 0.115
        retention = 0.65
        visa_cap = 48.0
    elif "united states" in c_name or "usa" in c_name:
        taxable = max(annual_gross - (2000.0 if payload.claim_allowance else 0.0), 0.0)
        tax = taxable * 0.10 if taxable <= 11600 else (1160 + (taxable - 11600) * 0.12)
        pension = 0.0
        retention = 1.0
        visa_cap = 40.0
    else:
        tax = annual_gross * 0.15
        pension = annual_gross * 0.05
        retention = 0.85
        visa_cap = 40.0

    tax_fn = tax / 26.0
    pension_fn = pension / 26.0

    return {
        "jurisdiction": payload.country_name,
        "gross_fortnight": round(gross_fn, 2),
        "tax_withheld": round(tax_fn, 2),
        "net_takehome": round(max(gross_fn - tax_fn, 0.0), 2),
        "statutory_pension": round(pension_fn, 2),
        "departure_refund_claimable": round(pension_fn * retention, 2),
        "visa_work_cap_hours": visa_cap,
        "is_visa_compliant": payload.hours_worked <= visa_cap
    }

# ----------------- INTERACTIVE WEB UI -----------------
@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BudgetWise-AI Model Hub</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-6 font-sans">
        <div class="max-w-5xl mx-auto space-y-6">
            <header class="border-b border-slate-800 pb-4 text-center">
                <h1 class="text-3xl font-extrabold text-blue-500">🧠 BudgetWise-AI Algorithmic Engine</h1>
                <p class="text-slate-400 text-sm mt-1">Live Deployment of Scratch ML Classifier, OLS Velocity & Statutory Math</p>
                <div class="mt-3 flex justify-center gap-3">
                    <span class="px-3 py-1 bg-emerald-950 border border-emerald-600 text-emerald-400 text-xs font-semibold rounded-full">Scikit-Learn Naive Bayes: Active</span>
                    <span class="px-3 py-1 bg-sky-950 border border-sky-600 text-sky-400 text-xs font-semibold rounded-full">NumPy OLS Engine: Active</span>
                    <a href="/docs" target="_blank" class="px-3 py-1 bg-blue-900 border border-blue-600 text-blue-300 text-xs font-semibold rounded-full hover:bg-blue-800">Open API Docs</a>
                </div>
            </header>

            <div class="grid md:grid-cols-2 gap-6">
                <!-- NLP Classifier Card -->
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
                    <h2 class="text-lg font-bold text-sky-400">🏷️ Scratch TF-IDF Classifier</h2>
                    <p class="text-xs text-slate-400">Classifies unstructured bank strings via Multinomial Naive Bayes pipeline.</p>
                    <div>
                        <label class="text-xs text-slate-300">Transaction String</label>
                        <input id="nlp_desc" class="w-full bg-slate-950 border border-slate-700 rounded p-2 text-sm" value="Coles Supermarket Sydney">
                    </div>
                    <button onclick="runClassifier()" class="w-full bg-blue-600 hover:bg-blue-500 py-2 rounded text-sm font-semibold">Predict Category</button>
                    <pre id="nlp_res" class="bg-slate-950 p-3 rounded text-xs text-emerald-400 border border-slate-800">Awaiting input...</pre>
                </div>

                <!-- Spending Risk Card -->
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
                    <h2 class="text-lg font-bold text-sky-400">⚠️ Dynamic Purchase Impact Model</h2>
                    <p class="text-xs text-slate-400">Calculates solvency impact ratio and returns a categorized risk percentage.</p>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="text-xs text-slate-300">Proposed Spend ($)</label>
                            <input id="risk_amount" class="w-full bg-slate-950 border border-slate-700 rounded p-2 text-sm" value="85.00">
                        </div>
                        <div>
                            <label class="text-xs text-slate-300">Accrued Budget ($)</label>
                            <input id="risk_budget" class="w-full bg-slate-950 border border-slate-700 rounded p-2 text-sm" value="1000.00">
                        </div>
                        <div>
                            <label class="text-xs text-slate-300">Current Spend ($)</label>
                            <input id="risk_spent" class="w-full bg-slate-950 border border-slate-700 rounded p-2 text-sm" value="820.00">
                        </div>
                        <div>
                            <label class="text-xs text-slate-300">Days Left</label>
                            <input id="risk_days" class="w-full bg-slate-950 border border-slate-700 rounded p-2 text-sm" value="6">
                        </div>
                    </div>
                    <button onclick="runRiskCheck()" class="w-full bg-indigo-600 hover:bg-indigo-500 py-2 rounded text-sm font-semibold">Evaluate Purchase Risk</button>
                    <pre id="risk_res" class="bg-slate-950 p-3 rounded text-xs text-emerald-400 border border-slate-800">Awaiting input...</pre>
                </div>

                <!-- OLS Velocity Card -->
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4 md:col-span-2">
                    <h2 class="text-lg font-bold text-sky-400">📐 Ordinary Least Squares (OLS) Linear Burn Rate Model</h2>
                    <p class="text-xs text-slate-400">Executes <code>np.linalg.lstsq</code> on cumulative spending vectors to detect slope changes.</p>
                    <div class="grid md:grid-cols-3 gap-2">
                        <div>
                            <label class="text-xs text-slate-300">Current Day</label>
                            <input id="ols_day" class="w-full bg-slate-950 border border-slate-700 rounded p-2 text-sm" value="7">
                        </div>
                        <div>
                            <label class="text-xs text-slate-300">Current Spend ($)</label>
                            <input id="ols_spent" class="w-full bg-slate-950 border border-slate-700 rounded p-2 text-sm" value="450.00">
                        </div>
                        <div>
                            <label class="text-xs text-slate-300">Fortnight Budget ($)</label>
                            <input id="ols_budget" class="w-full bg-slate-950 border border-slate-700 rounded p-2 text-sm" value="950.00">
                        </div>
                    </div>
                    <button onclick="runOLS()" class="w-full bg-emerald-600 hover:bg-emerald-500 py-2 rounded text-sm font-semibold">Run Linear Least Squares Forecast</button>
                    <pre id="ols_res" class="bg-slate-950 p-3 rounded text-xs text-emerald-400 border border-slate-800 overflow-x-auto">Awaiting input...</pre>
                </div>
            </div>
        </div>

        <script>
            async function runClassifier() {
                const desc = document.getElementById('nlp_desc').value;
                const res = await fetch('/api/model/classify', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ description: desc })
                });
                const data = await res.json();
                document.getElementById('nlp_res').innerText = JSON.stringify(data, null, 2);
            }

            async function runRiskCheck() {
                const res = await fetch('/api/model/spending-risk', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        proposed_amount: Number(document.getElementById('risk_amount').value),
                        total_budget: Number(document.getElementById('risk_budget').value),
                        current_expenses: Number(document.getElementById('risk_spent').value),
                        days_remaining: Number(document.getElementById('risk_days').value)
                    })
                });
                const data = await res.json();
                document.getElementById('risk_res').innerText = JSON.stringify(data, null, 2);
            }

            async function runOLS() {
                const res = await fetch('/api/model/ols-velocity', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        current_day: Number(document.getElementById('ols_day').value),
                        current_expenses: Number(document.getElementById('ols_spent').value),
                        accrued_budget: Number(document.getElementById('ols_budget').value),
                        proposed_amount: 0.0,
                        daily_expenses: {1: 50.0, 2: 70.0, 3: 45.0, 4: 80.0, 5: 60.0, 6: 90.0, 7: 55.0}
                    })
                });
                const data = await res.json();
                document.getElementById('ols_res').innerText = JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """