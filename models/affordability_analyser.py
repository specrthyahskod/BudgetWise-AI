import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any

class AffordabilityAnalytics:
    """Evaluates purchase safety against current income, and past expenditure history"""

    def __init__(self, current_balance: float, hourly_net_wage: float = 23.50):
        self.current_balance = float(current_balance)
        self.hourly_net_wage = max(1.0, float(hourly_net_wage))

    def evaluate(self, item_name: str, cost: float, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        cost = float(cost)
        now = datetime.now()

        work_hours_needed = cost / self.hourly_net_wage #net_wage
        is_capital_purchase = (cost >= 2000.0)

        if not is_capital_purchase:
            # Short span [Current week] expenditure curve analysis (< $2,000 AUD) ===
            start_of_week = now - timedelta(days=now.weekday())
            week_df = transactions_df[transactions_df["date"] >= start_of_week] if not transactions_df.empty else pd.DataFrame()
            
            weekly_spent = week_df["amount"].sum() if not week_df.empty else 0.0
            days_left_in_week = max(1, 7 - now.weekday())
            
            remaining_liquidity = self.current_balance - cost
            daily_safespend_after = max(0.0, remaining_liquidity / days_left_in_week)

            if remaining_liquidity < 150.0:
                verdict = "HIGH RISK ⛔"
                explanation = (
                    f"Buying '{item_name}' (${cost:,.2f}) will deplete your reserves to ${remaining_liquidity:,.2f}. "
                    f"This leaves only ${daily_safespend_after:,.2f}/day for the rest of this week."
                )
            elif remaining_liquidity < 400.0:
                verdict = "CAUTION ⚠️"
                explanation = (
                    f"'{item_name}' is technically affordable, but compresses this week's daily allowance "
                    f"to ${daily_safespend_after:,.2f}/day. You have spent ${weekly_spent:,.2f} so far this week."
                )
            else:
                verdict = "AFFORDABLE ✅"
                explanation = (
                    f"Safe to purchase. You maintain a solid buffer of ${remaining_liquidity:,.2f} "
                    f"with a SafeSpend limit of ${daily_safespend_after:,.2f}/day remaining this week."
                )

            return {
                "horizon": "Current Week Micro-Curve",
                "verdict": verdict,
                "cost": cost,
                "work_hours": work_hours_needed,
                "explanation": explanation,
                "projected_balance": remaining_liquidity,
                "detail_metric": f"Daily SafeSpend Remaining: ${daily_safespend_after:,.2f}/day"
            }

        else:
            # Past 3 weeks expenditure curve analysis (>2000$)       
            three_weeks_ago = now - timedelta(days=21)
            past_3w_df = transactions_df[transactions_df["date"] >= three_weeks_ago] if not transactions_df.empty else pd.DataFrame()

            # Weekly expenditure aggregation
            if not past_3w_df.empty:
                weekly_totals = past_3w_df.groupby(past_3w_df["date"].dt.isocalendar().week)["amount"].sum().tolist()
            else:
                weekly_totals = [350.0, 420.0, 390.0]  # Fallback typical student expenditure

            mean_weekly_burn = float(np.mean(weekly_totals))
            burn_std = float(np.std(weekly_totals)) if len(weekly_totals) > 1 else 50.0
            
            # Capital buffer calculation (4 weeks trailing emergency burn + item cost)
            mandatory_reserve = mean_weekly_burn * 3.0
            surplus_after_purchase = self.current_balance - (cost + mandatory_reserve)

            if self.current_balance < cost:
                verdict = "INSUFFICIENT FUNDS ⛔"
                explanation = (
                    f"Cannot afford '{item_name}' (${cost:,.2f}). Total available balance is ${self.current_balance:,.2f}. "
                    f"Shortfall: ${abs(self.current_balance - cost):,.2f}."
                )
            elif surplus_after_purchase < 0:
                verdict = "STRUCTURAL DEFICIT ⚠️"
                explanation = (
                    f"Purchasing '{item_name}' consumes ${cost:,.2f} AUD and breaches your 3-week trailing living reserve "
                    f"(${mandatory_reserve:,.2f} based on ~${mean_weekly_burn:,.2f}/week average spend). "
                    f"You risk cash-flow exhaustion within 2 weeks."
                )
            else:
                verdict = "CAPITAL APPROVED ✅"
                explanation = (
                    f"Approved. After allocating ${cost:,.2f} AUD, you preserve your 3-week trailing baseline "
                    f"reserve (${mandatory_reserve:,.2f}) with an uncommitted buffer of ${surplus_after_purchase:,.2f}."
                )

            return {
                "horizon": "3-Week Macro Velocity",
                "verdict": verdict,
                "cost": cost,
                "work_hours": work_hours_needed,
                "explanation": explanation,
                "projected_balance": self.current_balance - cost,
                "detail_metric": f"3-Wk Average Burn: ${mean_weekly_burn:,.2f}/week (±${burn_std:,.2f})"
            }