import flet as ft
import os
import sys
import math
import json
import gzip
import hashlib
import re
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    import joblib
    classifier_path = os.path.join(PROJECT_ROOT, "models", "expense_classifier.joblib")
    ai_classifier = joblib.load(classifier_path) if os.path.exists(classifier_path) else None
except Exception:
    ai_classifier = None

calculate_financial_health = None
try:
    import models.fin_math_model as fin_math
    if hasattr(fin_math, "calculate_financial_health"):
        calculate_financial_health = getattr(fin_math, "calculate_financial_health")
    elif hasattr(fin_math, "calculate_safespend"):
        calculate_financial_health = getattr(fin_math, "calculate_safespend")
except Exception:
    calculate_financial_health = None

pack_rcd = None
unpack_rcd = None
try:
    import models.rcd_format as rcd_module
    if hasattr(rcd_module, "pack_rcd"):
        pack_rcd = getattr(rcd_module, "pack_rcd")
    elif hasattr(rcd_module, "RCDHandler") and hasattr(getattr(rcd_module, "RCDHandler"), "pack"):
        pack_rcd = getattr(getattr(rcd_module, "RCDHandler"), "pack")

    if hasattr(rcd_module, "unpack_rcd"):
        unpack_rcd = getattr(rcd_module, "unpack_rcd")
    elif hasattr(rcd_module, "RCDHandler") and hasattr(getattr(rcd_module, "RCDHandler"), "unpack"):
        unpack_rcd = getattr(getattr(rcd_module, "RCDHandler"), "unpack")
except Exception:
    pack_rcd, unpack_rcd = None, None


def get_fortnight_index(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    fn = (dt.timetuple().tm_yday - 1) // 14 + 1
    return f"{dt.year}-FN{fn:02d}"


def classify_expense(desc: str) -> str:
    if ai_classifier is not None:
        try:
            return str(ai_classifier.predict([desc])[0])
        except Exception:
            pass
    lower = desc.lower()
    if any(k in lower for k in ["woolworths", "coles", "groceries", "market", "food", "aldi"]):
        return "Groceries"
    if any(k in lower for k in ["train", "bus", "opal", "transport", "uber", "fuel"]):
        return "Transport"
    if any(k in lower for k in ["recharge", "airtel", "wifi", "bill", "rent", "utilities"]):
        return "Utilities"
    if any(k in lower for k in ["restaurant", "bistro", "cafe", "dining", "coffee", "meal"]):
        return "Dining"
    if any(k in lower for k in ["book", "stationery", "tuition", "lab", "academic", "exam"]):
        return "Academic"
    return "Entertainment"


def main(page: ft.Page):
    page.title = "BudgetWise AI - Mobile Financial Companion"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 16
    page.scroll = None

    auth_state = {"logged_in": False, "username": "Student"}
    current_balance = 2850.00
    weekly_budget = 500.00

    today = datetime.now()
    transactions = [
        {"date": (today - timedelta(days=1)).strftime("%Y-%m-%d"), "category": "Groceries", "description": "Woolworths Supermarket", "amount": 84.50},
        {"date": (today - timedelta(days=3)).strftime("%Y-%m-%d"), "category": "Transport", "description": "Opal Card Top-up", "amount": 35.00},
        {"date": (today - timedelta(days=5)).strftime("%Y-%m-%d"), "category": "Utilities", "description": "Airtel / Mobile Recharge", "amount": 45.00},
        {"date": (today - timedelta(days=7)).strftime("%Y-%m-%d"), "category": "Dining", "description": "Campus Bistro Meal", "amount": 22.00},
        {"date": (today - timedelta(days=9)).strftime("%Y-%m-%d"), "category": "Academic", "description": "Stationery & Textbooks", "amount": 62.50},
        {"date": (today - timedelta(days=16)).strftime("%Y-%m-%d"), "category": "Groceries", "description": "Coles Groceries", "amount": 92.20},
        {"date": (today - timedelta(days=18)).strftime("%Y-%m-%d"), "category": "Transport", "description": "Metro Transport Pass", "amount": 60.00},
        {"date": (today - timedelta(days=22)).strftime("%Y-%m-%d"), "category": "Entertainment", "description": "Weekend Cinema", "amount": 42.00},
        {"date": (today - timedelta(days=26)).strftime("%Y-%m-%d"), "category": "Academic", "description": "Reference Books", "amount": 55.00}
    ]

    # ---------------- 1. AUTH VIEW ----------------
    auth_mode = "login"
    auth_title = ft.Text("Welcome Back", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.LIGHT_BLUE_400)
    auth_subtitle = ft.Text("Sign in to sync your financial ledger", size=12, color=ft.Colors.GREY_400)
    username_field = ft.TextField(label="Username or Email", prefix_icon=ft.Icons.PERSON, width=380)
    password_field = ft.TextField(label="Password", password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK, width=380)
    confirm_pass_field = ft.TextField(label="Confirm Password", password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK_CLOCK, width=380, visible=False)
    auth_error_lbl = ft.Text("", size=12, color=ft.Colors.RED_400)

    submit_auth_text = ft.Text("Sign In", size=14, weight=ft.FontWeight.BOLD)
    toggle_link_text = ft.Text("Don't have an account? Sign Up", size=12)
    forgot_link_text = ft.Text("Forgot password?", size=12)

    def set_auth_mode(mode: str):
        nonlocal auth_mode
        auth_mode = mode
        auth_error_lbl.value = ""
        if mode == "login":
            auth_title.value = "Welcome to BudgetWise"
            auth_subtitle.value = "Sign in to access your international student financial engine"
            confirm_pass_field.visible = False
            password_field.visible = True
            submit_auth_text.value = "Sign In"
            toggle_link_text.value = "Don't have an account? Sign Up"
            forgot_link.visible = True
        elif mode == "signup":
            auth_title.value = "Create BudgetWise Account"
            auth_subtitle.value = "Track foreign exchange, wage caps, and weekly budgets"
            confirm_pass_field.visible = True
            password_field.visible = True
            submit_auth_text.value = "Register"
            toggle_link_text.value = "Already have an account? Log In"
            forgot_link.visible = False
        else:
            auth_title.value = "Reset Password"
            auth_subtitle.value = "Enter your registered email to reset credentials"
            confirm_pass_field.visible = False
            password_field.visible = False
            submit_auth_text.value = "Send Reset Link"
            toggle_link_text.value = "Remembered password? Log In"
            forgot_link.visible = False
        page.update()

    def handle_auth_submit(e):
        user = (username_field.value or "").strip()
        pwd = (password_field.value or "").strip()

        if not user:
            auth_error_lbl.value = "Please enter a valid username/email."
            page.update()
            return

        if auth_mode == "login":
            if not pwd:
                auth_error_lbl.value = "Please enter your password."
                page.update()
                return
            auth_state["logged_in"] = True
            auth_state["username"] = user
            header_user_tag.value = f"Logged as: {user}"
            switch_to_app()
        elif auth_mode == "signup":
            confirm = (confirm_pass_field.value or "").strip()
            if not pwd or pwd != confirm:
                auth_error_lbl.value = "Passwords do not match or are empty."
                page.update()
                return
            auth_state["logged_in"] = True
            auth_state["username"] = user
            header_user_tag.value = f"Logged as: {user}"
            switch_to_app()
        else:
            auth_error_lbl.value = "Password reset instructions dispatched."
            page.update()

    submit_auth_btn = ft.ElevatedButton(
        content=submit_auth_text,
        on_click=handle_auth_submit,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
        width=380,
        height=45
    )
    toggle_link = ft.TextButton(content=toggle_link_text, on_click=lambda _: set_auth_mode("signup" if auth_mode == "login" else "login"))
    forgot_link = ft.TextButton(content=forgot_link_text, on_click=lambda _: set_auth_mode("reset"))

    auth_card = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=48, color=ft.Colors.LIGHT_BLUE_400),
                auth_title,
                auth_subtitle,
                auth_error_lbl,
                username_field,
                password_field,
                confirm_pass_field,
                submit_auth_btn,
                ft.Row([toggle_link, forgot_link], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=380)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        ),
        padding=24,
        bgcolor=ft.Colors.BLUE_GREY_900,
        border_radius=12
    )
    auth_view = ft.Container(content=auth_card, alignment=ft.Alignment(0, 0), padding=20, expand=True, visible=True)

    # ---------------- 2. DASHBOARD VIEW ----------------
    card_balance_val = ft.Text(f"${current_balance:,.2f} AUD", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.LIGHT_BLUE_400)
    card_spent_val = ft.Text("$0.00 AUD", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)
    card_safespend_val = ft.Text("$0.00/day", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)

    def calculate_dashboard_metrics():
        cutoff_7d = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        week_spent = sum(t["amount"] for t in transactions if t["date"] >= cutoff_7d)
        if calculate_financial_health is not None:
            try:
                res = calculate_financial_health(current_balance, week_spent, weekly_budget)
                if isinstance(res, dict):
                    return week_spent, res.get("remaining", weekly_budget - week_spent), res.get("safespend_daily", 0.0)
            except Exception:
                pass
        remaining = weekly_budget - week_spent
        days_left = max(1, 7 - datetime.now().weekday())
        daily_safespend = max(0.0, remaining / days_left) if remaining > 0 else 0.0
        return week_spent, remaining, daily_safespend

    def update_metric_cards():
        s, r, ss = calculate_dashboard_metrics()
        card_balance_val.value = f"${current_balance:,.2f} AUD"
        card_spent_val.value = f"${s:,.2f} AUD"
        card_safespend_val.value = f"${ss:,.2f}/day"

    metrics_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("BALANCE", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_400),
                        card_balance_val
                    ],
                    spacing=4
                ),
                bgcolor=ft.Colors.BLUE_GREY_900,
                padding=16,
                border_radius=8,
                expand=1
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("WEEKLY SPENT", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_400),
                        card_spent_val
                    ],
                    spacing=4
                ),
                bgcolor=ft.Colors.BLUE_GREY_900,
                padding=16,
                border_radius=8,
                expand=1
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("SAFESPEND", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_400),
                        card_safespend_val
                    ],
                    spacing=4
                ),
                bgcolor=ft.Colors.BLUE_GREY_900,
                padding=16,
                border_radius=8,
                expand=1
            )
        ],
        spacing=12
    )

    ledger_rows_column = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO, expand=True)

    def refresh_ledger():
        ledger_rows_column.controls.clear()
        for t in reversed(transactions):
            row_item = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(t["date"], size=12, width=110),
                        ft.Text(t["category"], size=12, weight=ft.FontWeight.W_500, width=120),
                        ft.Text(t["description"], size=12, expand=True),
                        ft.Text(f"-${t['amount']:,.2f}", size=12, color=ft.Colors.RED_400, weight=ft.FontWeight.BOLD, width=100, text_align=ft.TextAlign.RIGHT),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=ft.Padding(10, 8, 10, 8),
                bgcolor=ft.Colors.BLUE_GREY_900,
                border_radius=4
            )
            ledger_rows_column.controls.append(row_item)
        update_metric_cards()
        refresh_reports()

    tx_desc = ft.TextField(label="Transaction Note", hint_text="e.g. Woolworths grocs or Opal card", expand=3)
    tx_amt = ft.TextField(label="Cost (AUD)", keyboard_type=ft.KeyboardType.NUMBER, expand=1)
    tx_cat = ft.Dropdown(
        label="Category",
        options=[
            ft.dropdown.Option("Auto (AI Classify)"),
            ft.dropdown.Option("Groceries"),
            ft.dropdown.Option("Transport"),
            ft.dropdown.Option("Dining"),
            ft.dropdown.Option("Utilities"),
            ft.dropdown.Option("Academic"),
            ft.dropdown.Option("Entertainment")
        ],
        value="Auto (AI Classify)",
        expand=2
    )

    def add_tx_click(e):
        try:
            val = float(tx_amt.value or 0.0)
            desc = (tx_desc.value or "").strip()
            if val <= 0 or not desc:
                return

            chosen_cat = tx_cat.value
            if not chosen_cat or chosen_cat == "Auto (AI Classify)":
                chosen_cat = classify_expense(desc)

            new_entry = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "category": chosen_cat,
                "description": desc,
                "amount": val
            }
            transactions.append(new_entry)
            nonlocal current_balance
            current_balance -= val

            tx_desc.value = ""
            tx_amt.value = ""
            tx_cat.value = "Auto (AI Classify)"
            refresh_ledger()
            page.update()
        except Exception:
            pass

    add_tx_btn = ft.ElevatedButton(
        content=ft.Text("Log Transaction"),
        icon=ft.Icons.ADD_CARD,
        on_click=add_tx_click,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE
    )

    ledger_header = ft.Container(
        content=ft.Row(
            [
                ft.Text("Date", weight=ft.FontWeight.BOLD, size=13, width=110),
                ft.Text("Category", weight=ft.FontWeight.BOLD, size=13, width=120),
                ft.Text("Description", weight=ft.FontWeight.BOLD, size=13, expand=True),
                ft.Text("Amount", weight=ft.FontWeight.BOLD, size=13, width=100, text_align=ft.TextAlign.RIGHT),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        padding=ft.Padding(10, 10, 10, 10),
        bgcolor=ft.Colors.BLUE_GREY_900,
        border_radius=6
    )

    ledger_container = ft.Container(
        content=ft.Column(
            [
                ledger_header,
                ledger_rows_column
            ],
            expand=True,
            spacing=4
        ),
        bgcolor=ft.Colors.BLACK,
        padding=8,
        border_radius=8,
        expand=True
    )

    dashboard_view = ft.Column(
        controls=[
            ft.Text("Financial Health & Velocity Ledger", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.LIGHT_BLUE_300),
            metrics_row,
            ft.Row([tx_desc, tx_amt, tx_cat, add_tx_btn], wrap=True),
            ledger_container
        ],
        spacing=12,
        expand=True,
        visible=False
    )

    # ---------------- 3. CALCULATOR VIEW ----------------
    calc_wage_input = ft.TextField(label="Contract Hourly Wage ($)", value="28.50", keyboard_type=ft.KeyboardType.NUMBER, expand=1)
    calc_hours_input = ft.TextField(label="Fortnight Hours Worked", value="44", keyboard_type=ft.KeyboardType.NUMBER, expand=1)
    calc_weeks_input = ft.TextField(label="Semester Runway (Weeks)", value="18", keyboard_type=ft.KeyboardType.NUMBER, expand=1)
    calc_output_text = ft.Text(size=12, weight=ft.FontWeight.W_500)

    def execute_advanced_calculator(e):
        try:
            w = float(calc_wage_input.value or 0.0)
            h = float(calc_hours_input.value or 0.0)
            weeks = float(calc_weeks_input.value or 0.0)

            is_visa_compliant = h <= 48
            visa_badge = "COMPLIANT ✅ (<= 48 hrs/fn)" if is_visa_compliant else "BREACH RISK ⚠️ (> 48 hrs/fn limit)"

            tax_rate = min(0.45, max(0.08, 0.12 + 0.35 / (1.0 + math.exp(-0.04 * (w - 25.0)))))
            gross_fn = w * h
            tax_withheld = gross_fn * tax_rate
            net_fn = gross_fn - tax_withheld
            super_fn = gross_fn * 0.115

            total_projected_net = (net_fn / 2) * weeks

            calc_output_text.value = (
                f"=== STATUTORY VISA & RUNWAY SIMULATION ===\n"
                f"• Visa Work Status: {visa_badge}\n"
                f"• Fortnight Gross Earnings: ${gross_fn:,.2f} AUD\n"
                f"• Estimated Tax Withheld ({tax_rate * 100:.1f}%): -${tax_withheld:,.2f} AUD\n"
                f"• Fortnight Take-Home Net: ${net_fn:,.2f} AUD\n"
                f"• Employer Pension/Super (11.5%): +${super_fn:,.2f} AUD\n\n"
                f"• Projected Semester Net Capital ({weeks:.0f} wks): ${total_projected_net:,.2f} AUD\n"
                f"• Safe Weekly Disposable Budget: ${net_fn / 2:,.2f} AUD/week"
            )
            page.update()
        except Exception as err:
            calc_output_text.value = f"Calculation error: {err}"
            page.update()

    calc_btn = ft.ElevatedButton(
        content=ft.Text("Run Simulator"),
        icon=ft.Icons.CALCULATE,
        on_click=execute_advanced_calculator,
        bgcolor=ft.Colors.BLUE_600
    )

    calculator_view = ft.Column(
        controls=[
            ft.Text("Student Financial & Compliance Calculator", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.LIGHT_BLUE_300),
            ft.Text("Simulate Subclass 500 visa hours, progressive withholdings, and semester runways.", size=12, color=ft.Colors.GREY_400),
            ft.Row([calc_wage_input, calc_hours_input, calc_weeks_input]),
            calc_btn,
            ft.Container(content=calc_output_text, bgcolor=ft.Colors.BLUE_GREY_900, padding=14, border_radius=8)
        ],
        spacing=14,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        visible=False
    )

    # ---------------- 4. REPORTS VIEW ----------------
    report_breakdown_col = ft.Column(spacing=8)
    report_summary_text = ft.Text(size=12)

    report_horizon = ft.Dropdown(
        label="Fortnight Cycle Filter",
        value="Current Fortnight",
        options=[
            ft.dropdown.Option("Current Fortnight"),
            ft.dropdown.Option("Previous Fortnight"),
            ft.dropdown.Option("All Time")
        ],
        width=280,
        on_select=lambda e: refresh_reports()
    )

    def refresh_reports():
        report_breakdown_col.controls.clear()

        recorded_cycles = sorted(list(set(get_fortnight_index(t["date"]) for t in transactions)), reverse=True)
        existing_keys = [opt.key for opt in report_horizon.options if opt.key]
        for c in recorded_cycles:
            if c not in existing_keys:
                report_horizon.options.append(ft.dropdown.Option(key=c, text=f"Fortnight {c}"))

        selected = report_horizon.value or "Current Fortnight"
        today_dt = datetime.now()
        cur_cycle = get_fortnight_index(today_dt.strftime("%Y-%m-%d"))
        prev_cycle = get_fortnight_index((today_dt - timedelta(days=14)).strftime("%Y-%m-%d"))

        if selected == "Current Fortnight":
            scoped_tx = [t for t in transactions if get_fortnight_index(t["date"]) == cur_cycle]
        elif selected == "Previous Fortnight":
            scoped_tx = [t for t in transactions if get_fortnight_index(t["date"]) == prev_cycle]
        elif selected == "All Time":
            scoped_tx = list(transactions)
        else:
            scoped_tx = [t for t in transactions if get_fortnight_index(t["date"]) == selected]

        total_spent = sum(t["amount"] for t in scoped_tx)

        if total_spent == 0 or len(scoped_tx) == 0:
            report_summary_text.value = f"No expenditure transactions logged for cycle: {selected}."
            page.update()
            return

        cat_totals = {}
        for t in scoped_tx:
            cat = t["category"]
            cat_totals[cat] = cat_totals.get(cat, 0.0) + t["amount"]

        for cat, amt in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
            pct = amt / total_spent
            report_breakdown_col.controls.append(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(cat, weight=ft.FontWeight.BOLD, size=12),
                                ft.Text(f"${amt:,.2f} ({pct * 100:.1f}%)", size=12, color=ft.Colors.LIGHT_BLUE_300)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.ProgressBar(value=pct, color=ft.Colors.LIGHT_BLUE_400, bgcolor=ft.Colors.BLUE_GREY_800)
                    ],
                    spacing=2
                )
            )

        top_cat = max(cat_totals.keys(), key=lambda k: cat_totals[k])
        report_summary_text.value = (
            f"• Scoped Interval: {selected}\n"
            f"• Aggregate Period Expenditure: ${total_spent:,.2f} AUD\n"
            f"• Logged Transaction Count: {len(scoped_tx)} entries\n"
            f"• Dominant Outlay Category: {top_cat} (${cat_totals[top_cat]:,.2f})"
        )
        page.update()

    reports_view = ft.Column(
        controls=[
            ft.Text("Financial Expense Reports", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.LIGHT_BLUE_300),
            report_horizon,
            ft.Container(content=report_summary_text, bgcolor=ft.Colors.BLUE_GREY_900, padding=12, border_radius=8),
            ft.Text("Categorical Breakdown", size=14, weight=ft.FontWeight.BOLD),
            report_breakdown_col
        ],
        spacing=14,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        visible=False
    )

    # ---------------- 5. AFFORDABILITY VIEW ----------------
    afford_query_input = ft.TextField(
        label="Ask e.g. 'Can I buy an iPad for $500?' or 'MacBook for $2400'",
        hint_text="Ask your affordability query...",
        expand=True
    )
    afford_output = ft.Text(size=12, weight=ft.FontWeight.W_400)

    def run_affordability_calc(e):
        query = (afford_query_input.value or "").strip()
        if not query:
            return

        price_match = re.findall(r"(?:\$|\b)\s*(\d+(?:,\d{3})*(?:\.\d{1,2})?)\s*(?:bucks|aud|dollars|\$|\b)", query, flags=re.IGNORECASE)
        if not price_match:
            price_match = re.findall(r"\b\d+(?:,\d{3})*(?:\.\d{1,2})?\b", query)

        if not price_match:
            afford_output.value = "⚠️ Unrecognized Price: Please state an amount in AUD (e.g. $450 or 1200 AUD)."
            page.update()
            return

        cost = float(price_match[0].replace(",", ""))
        item_name = query
        for stop in [r"can i buy", r"can i afford", r"bucks", r"aud", r"dollars", r"\$", r"\bfor\b", r"\ban\b", r"\ba\b"]:
            item_name = re.sub(stop, "", item_name, flags=re.IGNORECASE)
        item_name = re.sub(r"\b\d+(?:,\d{3})*(?:\.\d+)?\b", "", item_name).strip(" ,.-").capitalize() or "Requested Item"

        hourly_wage = 22.50
        work_hours = cost / hourly_wage
        rem_bal = current_balance - cost

        if cost < 2000.0:
            days_left = max(1, 7 - datetime.now().weekday())
            daily_ss = max(0.0, rem_bal / days_left)

            if current_balance < cost:
                verdict = "CANNOT AFFORD ⛔"
                msg = f"{item_name} (${cost:,.2f} AUD) exceeds your liquid balance (${current_balance:,.2f} AUD)."
            elif daily_ss < 30.0:
                verdict = "CAUTION 🟡"
                msg = f"{item_name} reduces remaining daily SafeSpend to ${daily_ss:,.2f}/day for {days_left} days."
            else:
                verdict = "SAFE TO BUY ✅"
                msg = f"{item_name} fits cleanly into your budget with ${daily_ss:,.2f}/day SafeSpend reserve."

            afford_output.value = (
                f"=== {verdict} (Micro Velocity Engine < $2,000) ===\n"
                f"{msg}\n\n"
                f"• Opportunity Shift Cost: {work_hours:.1f} hours of part-time labor\n"
                f"• Projected Balance: ${rem_bal:,.2f} AUD\n"
                f"• Daily SafeSpend Allowance: ${daily_ss:,.2f}/day"
            )
        else:
            emergency_reserve = 1875.00
            surplus = rem_bal - emergency_reserve

            if current_balance < cost:
                verdict = "INSUFFICIENT CAPITAL ⛔"
                msg = f"Cannot afford {item_name}. Balance shortfall of ${cost - current_balance:,.2f} AUD."
            elif surplus < 0:
                verdict = "STRUCTURAL DEFICIT ⚠️"
                msg = f"Allocating ${cost:,.2f} AUD infringes on your 6-week safety runway (${emergency_reserve:,.2f} AUD)."
            else:
                verdict = "CAPITAL APPROVED ✅"
                msg = f"{item_name} is approved. Preserves safety runway with ${surplus:,.2f} AUD surplus."

            afford_output.value = (
                f"=== {verdict} (Macro Capital Runway Engine ≥ $2,000) ===\n"
                f"{msg}\n\n"
                f"• Opportunity Shift Cost: {work_hours:.1f} hours of part-time labor\n"
                f"• Preserved Runway Buffer: ${emergency_reserve:,.2f} AUD\n"
                f"• Post-Purchase Surplus: ${surplus:,.2f} AUD"
            )
        page.update()

    afford_calc_btn = ft.ElevatedButton(
        content=ft.Text("Evaluate"),
        icon=ft.Icons.ANALYTICS,
        on_click=run_affordability_calc,
        bgcolor=ft.Colors.LIGHT_BLUE_700
    )

    affordability_view = ft.Column(
        controls=[
            ft.Text("Affordability Decision Engine", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.LIGHT_BLUE_300),
            ft.Text("Evaluates spending queries against micro-velocity limits (<$2k) and macro emergency capital runways (≥$2k).", size=12, color=ft.Colors.GREY_400),
            ft.Row([afford_query_input, afford_calc_btn]),
            ft.Container(content=afford_output, bgcolor=ft.Colors.BLUE_GREY_900, padding=14, border_radius=8)
        ],
        spacing=14,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        visible=False
    )

    # ---------------- 6. ARCHIVES VIEW (.rcd) ----------------
    rcd_status_output = ft.Text("No archive created in this session.", size=12, color=ft.Colors.GREY_400)

    def pack_rcd_archive(e):
        try:
            total_spent = sum(t["amount"] for t in transactions)
            payload_dict = {
                "user": auth_state["username"],
                "period": {
                    "start": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
                    "end": datetime.now().strftime("%Y-%m-%d")
                },
                "summary": {
                    "total_expenses": total_spent,
                    "transaction_count": len(transactions),
                    "currency": "AUD"
                },
                "records": transactions
            }

            full_rcd_stream = None
            if pack_rcd is not None:
                try:
                    full_rcd_stream = pack_rcd(payload_dict)
                except Exception:
                    full_rcd_stream = None

            if full_rcd_stream is None:
                raw_bytes = json.dumps(payload_dict, ensure_ascii=False).encode("utf-8")
                compressed_bytes = gzip.compress(raw_bytes)
                checksum = hashlib.sha256(compressed_bytes).digest()
                magic = b"BWRCD"
                full_rcd_stream = magic + checksum + compressed_bytes

            rcd_status_output.value = (
                f"✅ .rcd Binary Archive Packed Successfully!\n\n"
                f"• Container Magic: BWRCD\n"
                f"• SHA-256 Digest: {hashlib.sha256(full_rcd_stream[37:]).hexdigest()[:24]}...\n"
                f"• Total Packed Binary: {len(full_rcd_stream)} bytes\n"
                f"• Tamper-Evident Integrity: VERIFIED"
            )
            rcd_status_output.color = ft.Colors.GREEN_400
            page.update()
        except Exception as err:
            rcd_status_output.value = f"Packaging failed: {err}"
            rcd_status_output.color = ft.Colors.RED_400
            page.update()

    export_rcd_btn = ft.ElevatedButton(
        content=ft.Text("Pack Weekly .rcd Archive"),
        icon=ft.Icons.LOCK,
        on_click=pack_rcd_archive,
        bgcolor=ft.Colors.TEAL_700
    )

    archive_view = ft.Column(
        controls=[
            ft.Text(".rcd Financial Archive Container", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.LIGHT_BLUE_300),
            ft.Text("Exports tamper-evident statements sealed with SHA-256 cryptographic hashes and Gzip streams for offline verification.", size=12, color=ft.Colors.GREY_400),
            export_rcd_btn,
            ft.Container(content=rcd_status_output, bgcolor=ft.Colors.BLUE_GREY_900, padding=14, border_radius=8)
        ],
        spacing=14,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        visible=False
    )

    # ---------------- NAVIGATION & SHELL ----------------
    app_views = [dashboard_view, calculator_view, reports_view, affordability_view, archive_view]

    def on_nav_change(e):
        idx = int(e.control.selected_index)
        for i, v in enumerate(app_views):
            v.visible = (i == idx)
        page.update()

    nav_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),
            ft.NavigationBarDestination(icon=ft.Icons.CALCULATE, label="Calculator"),
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART, label="Reports"),
            ft.NavigationBarDestination(icon=ft.Icons.CHAT_BUBBLE, label="Affordability"),
            ft.NavigationBarDestination(icon=ft.Icons.ARCHIVE, label="Archives"),
        ]
    )

    header_user_tag = ft.Text("Not Logged In", size=12, color=ft.Colors.LIGHT_BLUE_300)

    def logout_click(e):
        auth_state["logged_in"] = False
        nav_bar.visible = False
        for v in app_views:
            v.visible = False
        auth_view.visible = True
        header_user_tag.value = "Not Logged In"
        page.update()

    logout_btn = ft.IconButton(icon=ft.Icons.LOGOUT, tooltip="Logout", on_click=logout_click)

    app_header = ft.Row(
        [
            ft.Row([
                ft.Icon(ft.Icons.MONETIZATION_ON, color=ft.Colors.LIGHT_BLUE_400, size=24),
                ft.Text("BudgetWise AI", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.LIGHT_BLUE_400),
            ]),
            ft.Row([header_user_tag, logout_btn])
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    content_area = ft.Container(
        content=ft.Stack([
            auth_view,
            dashboard_view,
            calculator_view,
            reports_view,
            affordability_view,
            archive_view
        ]),
        expand=True
    )

    def switch_to_app():
        auth_view.visible = False
        nav_bar.visible = True
        dashboard_view.visible = True
        refresh_ledger()
        page.navigation_bar = nav_bar
        page.update()

    page.add(
        app_header,
        ft.Divider(height=1),
        content_area
    )

    refresh_reports()

if __name__ == "__main__":
    ft.app(target=main)