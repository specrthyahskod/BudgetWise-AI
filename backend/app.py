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

# ----------------- WEB API ENDPOINT DISPLAY -----------------
@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BudgetWise AI — Smart Finance Hub</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; }
            .glow-card {
                background: rgba(15, 23, 42, 0.75);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(51, 65, 85, 0.6);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .glow-card:hover {
                border-color: rgba(59, 130, 246, 0.5);
                box-shadow: 0 12px 30px -10px rgba(37, 99, 235, 0.2);
                transform: translateY(-2px);
            }
            .input-box {
                background: rgba(2, 6, 23, 0.8);
                border: 1px solid rgba(51, 65, 85, 0.8);
                transition: all 0.2s ease;
            }
            .input-box:focus {
                outline: none;
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
            }
            .btn-fx {
                transition: all 0.2s ease;
            }
            .btn-fx:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 20px -4px rgba(59, 130, 246, 0.4);
            }
            .btn-fx:active {
                transform: translateY(1px);
            }
        </style>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-4 sm:p-8 selection:bg-blue-500 selection:text-white">
        
        <!-- Background Ambient Glows -->
        <div class="fixed top-0 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none -z-10"></div>
        <div class="fixed bottom-0 right-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none -z-10"></div>

        <div class="max-w-5xl mx-auto space-y-8">
            
            <!-- Header Section -->
            <header class="text-center space-y-3 pt-2">
                <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                    BudgetWise AI Online Platform
                </div>
                <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                    Smart Financial Control & Forecasting
                </h1>
                <p class="text-slate-400 text-sm max-w-xl mx-auto font-normal">
                    Real-time AI spending classifications, purchase safety checks, and pace prediction designed specifically for students.
                </p>
                <div class="pt-1">
                    <a href="/docs" target="_blank" class="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-blue-400 transition-colors font-medium">
                        Developer Swagger API &rarr;
                    </a>
                </div>
            </header>

            <!-- Cards Grid -->
            <div class="grid md:grid-cols-2 gap-6">

                <!-- 1. Expense Categorizer -->
                <div class="glow-card rounded-2xl p-6 flex flex-col justify-between">
                    <div class="space-y-4">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center gap-2.5">
                                <span class="p-2 rounded-xl bg-blue-500/10 text-blue-400 text-lg">🏷️</span>
                                <div>
                                    <h2 class="text-base font-bold text-white">Smart Expense Categorizer</h2>
                                    <p class="text-xs text-slate-400">Instantly detects spending type from store names</p>
                                </div>
                            </div>
                        </div>

                        <div>
                            <label class="block text-xs font-medium text-slate-300 mb-1.5">Store / Transaction Note</label>
                            <input id="nlp_desc" class="input-box w-full rounded-xl px-3.5 py-2.5 text-sm text-white" value="Zomato">
                        </div>

                        <button onclick="runClassifier()" class="btn-fx w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2.5 rounded-xl text-sm shadow-md">
                            Identify Category
                        </button>
                    </div>

                    <div id="nlp_res_box" class="mt-4 p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 min-h-[58px] flex items-center justify-center text-center">
                        <span class="text-xs text-slate-500 font-medium">Click above to test category matching</span>
                    </div>
                </div>

                <!-- 2. Purchase Safety Check -->
                <div class="glow-card rounded-2xl p-6 flex flex-col justify-between">
                    <div class="space-y-4">
                        <div class="flex items-center gap-2.5">
                            <span class="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 text-lg">🛡️</span>
                            <div>
                                <h2 class="text-base font-bold text-white">Purchase Safety Check</h2>
                                <p class="text-xs text-slate-400">Evaluates if an expense is safe for your remaining balance</p>
                            </div>
                        </div>

                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-medium text-slate-300 mb-1">Item Cost ($)</label>
                                <input id="risk_amount" class="input-box w-full rounded-xl px-3 py-2 text-sm text-white" value="85.00">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-300 mb-1">Fortnight Budget ($)</label>
                                <input id="risk_budget" class="input-box w-full rounded-xl px-3 py-2 text-sm text-white" value="1000.00">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-300 mb-1">Spent So Far ($)</label>
                                <input id="risk_spent" class="input-box w-full rounded-xl px-3 py-2 text-sm text-white" value="820.00">
                            </div>
                            <div>
                                <label class="block text-xs font-medium text-slate-300 mb-1">Days Remaining</label>
                                <input id="risk_days" class="input-box w-full rounded-xl px-3 py-2 text-sm text-white" value="6">
                            </div>
                        </div>

                        <button onclick="runRiskCheck()" class="btn-fx w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2.5 rounded-xl text-sm shadow-md">
                            Check Affordability
                        </button>
                    </div>

                    <div id="risk_res_box" class="mt-4 p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 min-h-[58px] flex items-center justify-center text-center">
                        <span class="text-xs text-slate-500 font-medium">Ready to evaluate your purchase</span>
                    </div>
                </div>

                <!-- 3. Fortnight Budget Forecaster -->
                <div class="glow-card rounded-2xl p-6 md:col-span-2 space-y-5">
                    <div class="flex items-center gap-2.5">
                        <span class="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 text-lg">📈</span>
                        <div>
                            <h2 class="text-base font-bold text-white">14-Day Spending & Budget Forecaster</h2>
                            <p class="text-xs text-slate-400">Projects your end-of-cycle savings based on your daily spending speed</p>
                        </div>
                    </div>

                    <div class="grid sm:grid-cols-3 gap-3">
                        <div>
                            <label class="block text-xs font-medium text-slate-300 mb-1">Current Day in Cycle</label>
                            <input id="ols_day" class="input-box w-full rounded-xl px-3.5 py-2.5 text-sm text-white" value="7">
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-slate-300 mb-1">Current Total Spent ($)</label>
                            <input id="ols_spent" class="input-box w-full rounded-xl px-3.5 py-2.5 text-sm text-white" value="450.00">
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-slate-300 mb-1">Fortnight Budget Target ($)</label>
                            <input id="ols_budget" class="input-box w-full rounded-xl px-3.5 py-2.5 text-sm text-white" value="950.00">
                        </div>
                    </div>

                    <button onclick="runOLS()" class="btn-fx w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2.5 rounded-xl text-sm shadow-md">
                        Calculate Budget Projection
                    </button>

                    <div id="ols_res_box" class="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 min-h-[70px] flex items-center justify-center text-center">
                        <span class="text-xs text-slate-500 font-medium">Click above to generate your fortnight forecast</span>
                    </div>
                </div>

            </div>
            
            <footer class="text-center text-xs text-slate-600 pb-4">
                BudgetWise AI • Engineered for International & Undergraduate Student Mobility
            </footer>
        </div>

        <script>
            async function runClassifier() {
                const desc = document.getElementById('nlp_desc').value;
                const box = document.getElementById('nlp_res_box');
                box.innerHTML = `<span class="text-xs text-blue-400 animate-pulse font-medium">Classifying...</span>`;

                try {
                    const res = await fetch('/api/model/classify', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ description: desc })
                    });
                    const data = await res.json();
                    box.innerHTML = `
                        <div class="flex items-center justify-between w-full px-2">
                            <span class="text-xs text-slate-400">Identified Category:</span>
                            <span class="px-3 py-1 rounded-lg bg-blue-500/20 text-blue-300 border border-blue-500/30 text-xs font-bold">${data.predicted_category}</span>
                        </div>
                    `;
                } catch (e) {
                    box.innerHTML = `<span class="text-xs text-rose-400 font-medium">Connection failed</span>`;
                }
            }

            async function runRiskCheck() {
                const box = document.getElementById('risk_res_box');
                box.innerHTML = `<span class="text-xs text-indigo-400 animate-pulse font-medium">Analyzing...</span>`;

                try {
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
                    const isHigh = data.risk_score > 60;
                    const badgeClass = isHigh ? 'bg-rose-500/20 text-rose-300 border-rose-500/30' : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';

                    box.innerHTML = `
                        <div class="w-full text-left space-y-1.5 px-1">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold ${isHigh ? 'text-rose-400' : 'text-emerald-400'}">${data.assessment}</span>
                                <span class="px-2 py-0.5 rounded text-[11px] font-bold border ${badgeClass}">${Math.round(data.risk_score)}% Risk</span>
                            </div>
                        </div>
                    `;
                } catch (e) {
                    box.innerHTML = `<span class="text-xs text-rose-400 font-medium">Evaluation failed</span>`;
                }
            }

            async function runOLS() {
                const box = document.getElementById('ols_res_box');
                box.innerHTML = `<span class="text-xs text-emerald-400 animate-pulse font-medium">Computing...</span>`;

                try {
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
                    const f = data.forecast;

                    box.innerHTML = `
                        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full text-center">
                            <div class="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                                <span class="block text-[11px] text-slate-400">Daily Pace</span>
                                <span class="text-sm font-bold text-sky-400">$${f.burn_rate_per_day}/day</span>
                            </div>
                            <div class="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                                <span class="block text-[11px] text-slate-400">Projected Total</span>
                                <span class="text-sm font-bold text-white">$${f.projected_total_expense}</span>
                            </div>
                            <div class="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                                <span class="block text-[11px] text-slate-400">Safe Daily Limit</span>
                                <span class="text-sm font-bold text-emerald-400">$${f.safe_daily_limit}/day</span>
                            </div>
                            <div class="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                                <span class="block text-[11px] text-slate-400">Status</span>
                                <span class="text-sm font-bold ${f.is_solvent ? 'text-emerald-400' : 'text-rose-400'}">${f.is_solvent ? 'On Track ✅' : 'Over Budget ⚠️'}</span>
                            </div>
                        </div>
                    `;
                } catch (e) {
                    box.innerHTML = `<span class="text-xs text-rose-400 font-medium">Forecast failed</span>`;
                }
            }
        </script>
    </body>
    </html>
    """