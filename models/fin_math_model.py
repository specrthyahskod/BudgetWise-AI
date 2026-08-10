import numpy as np

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

    def evaluate_use_case(self, case_id: int, payload: dict):
        match case_id:
            case 1:
                accrued_budget = payload.get("accrued_budget", 1440.00)
                current_expenses = payload.get("current_expenses", 158.49)
                proposed_amount = payload.get("proposed_amount", 18.00)
                current_day = payload.get("current_day", 7)
                daily_expenses_dict = payload.get("daily_expenses", {})

                forecast = self.forecast_end_of_fortnight(
                    current_day=current_day,
                    current_expenses=current_expenses + proposed_amount,
                    accrued_budget=accrued_budget,
                    daily_expenses_dict=daily_expenses_dict
                )

                return {
                    "use_case": "Case 1: Solvent / Disciplined Flow",
                    "status": "APPROVED",
                    "should_warn": False,
                    "forecast": forecast,
                    "message": f"✅ Transaction Approved! Safe Daily Limit: ${forecast['safe_daily_limit']:.2f}/day"
                }

            case 2:
                accrued_budget = payload.get("accrued_budget", 951.84)
                current_expenses = payload.get("current_expenses", 919.50)
                proposed_amount = payload.get("proposed_amount", 55.00)
                current_day = payload.get("current_day", 7)
                daily_expenses_dict = payload.get("daily_expenses", {})

                forecast = self.forecast_end_of_fortnight(
                    current_day=current_day,
                    current_expenses=current_expenses + proposed_amount,
                    accrued_budget=accrued_budget,
                    daily_expenses_dict=daily_expenses_dict
                )

                warning_msg = (
                    f"⚠️ FINANCIAL MODEL WARNING (Use Case 2 Triggered):\n"
                    f"Current Daily Burn Rate: ${forecast['burn_rate_per_day']:.2f}/day\n"
                    f"Projected Fortnight Spend: ${forecast['projected_total_expense']:.2f}\n"
                    f"Projected Deficit: ${forecast['projected_deficit']:.2f}\n"
                    f"Recommended Safe Limit: ${forecast['safe_daily_limit']:.2f}/day"
                )

                return {
                    "use_case": "Case 2: Insolvent / High Burn Rate Trigger",
                    "status": "WARNING",
                    "should_warn": not forecast["is_solvent"],
                    "forecast": forecast,
                    "message": warning_msg
                }

            case _:
                return {
                    "use_case": "Default Case: Unhandled ID",
                    "status": "UNKNOWN",
                    "should_warn": False,
                    "forecast": None,
                    "message": "Dynamic Evaluation"
                }

finance_calc = FinancialMathModel
if __name__ == "__main__":
    model = FinancialMathModel(total_fortnight_days=14)

    case_1_payload = {
        "accrued_budget": 1440.00,
        "current_expenses": 158.49,
        "proposed_amount": 18.00,
        "current_day": 7,
        "daily_expenses": {1: 62.00, 2: 20.00, 4: 5.50, 5: 18.00, 6: 45.00, 7: 13.99}
    }
    res_1 = model.evaluate_use_case(case_id=1, payload=case_1_payload)

    print("=" * 60)
    print(f"📌 {res_1['use_case']}")
    print("=" * 60)
    print(f"Status:      {res_1['status']}")
    print(f"Should Warn: {res_1['should_warn']}")
    print(f"Message:     {res_1['message']}")
    print("Forecast Details:", res_1['forecast'])
    print("\n")

    case_2_payload = {
        "accrued_budget": 951.84,
        "current_expenses": 919.50,
        "proposed_amount": 55.00,
        "current_day": 7,
        "daily_expenses": {1: 570.00, 2: 85.50, 3: 30.00, 4: 24.50, 5: 110.00, 6: 65.00, 7: 34.50}
    }
    res_2 = model.evaluate_use_case(case_id=2, payload=case_2_payload)

    print("=" * 60)
    print(f"📌 {res_2['use_case']}")
    print("=" * 60)
    print(f"Status:      {res_2['status']}")
    print(f"Should Warn: {res_2['should_warn']}")
    print(f"Message:\n{res_2['message']}")
    print("\nForecast Details:", res_2['forecast'])
    print("=" * 60)