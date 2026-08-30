import flet as ft
import requests
import math

RENDER_API_BASE = "https://budgetwise-ai-mobile.onrender.com"
REST_COUNTRIES_URL = "https://restcountries.com/v3.1/all?fields=name,cca2,currencies,population"
EXCHANGE_RATE_URL = "https://open.er-api.com/v6/latest/USD"

MINIMUM_WAGE_DEFAULTS_USD = {
    "Australia": 16.50, "Luxembourg": 17.10, "New Zealand": 14.20, "Monaco": 14.50,
    "Ireland": 13.80, "Germany": 13.50, "United Kingdom": 14.40, "Belgium": 13.10,
    "France": 12.80, "Netherlands": 14.10, "Canada": 12.50, "United States": 7.25,
    "Japan": 7.10, "South Korea": 7.30, "Spain": 7.80, "Poland": 6.20,
    "Chile": 3.10, "Costa Rica": 3.80, "Turkey": 2.90, "Mexico": 2.10,
    "Brazil": 1.95, "China": 2.20, "South Africa": 1.60, "India": 0.85,
    "Indonesia": 1.10, "Nigeria": 0.45, "Vietnam": 1.25, "Egypt": 0.70
}

REGIONAL_FLOOR_USD = {
    "Western Europe": 12.50, "Northern America": 10.00, "Eastern Europe": 4.50,
    "Latin America": 2.20, "East Asia": 5.00, "South Asia": 0.90,
    "Sub-Saharan Africa": 0.65, "Middle East": 3.50, "Global Default": 1.50
}

def main(page: ft.Page):
    page.title = "BudgetWise Mobile - Global Labor Intelligence"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    country_metadata = {}
    exchange_rates = {"USD": 1.0}

    wage_input = ft.TextField(
        label="Hourly Wage (Local Currency)",
        value="26.44",
        keyboard_type=ft.KeyboardType.NUMBER
    )
    hours_input = ft.TextField(
        label="Fortnight Hours Worked",
        value="40",
        keyboard_type=ft.KeyboardType.NUMBER
    )
    status_bar = ft.Text("Fetching global currency parity and geographic entities...", size=12, color=ft.Colors.AMBER_400)
    result_text = ft.Text(size=13, weight=ft.FontWeight.W_500)

    def calculate_cross_jurisdictional_analytics(wage_local: float, hours: float, country: str):
        meta = country_metadata.get(country, {})
        curr_code = meta.get("currency_code", "USD")
        fx_rate = exchange_rates.get(curr_code, 1.0)

        # Convert baseline minimum wage from USD to local currency: Local Wage = USD Wage * Exchange Rate
        statutory_min_usd = meta.get("min_wage_usd", 1.50)
        statutory_min_local = statutory_min_usd * fx_rate
        # Normalize local user wage to USD: USD Wage = Local Wage / Exchange Rate
        wage_usd = wage_local / fx_rate if fx_rate > 0 else wage_local

        # Formula: Percentage difference between user wage and legal minimum wage: ((User - Min) / Min) * 100
        wage_premium_pct = ((wage_local - statutory_min_local) / statutory_min_local) * 100 if statutory_min_local else 0.0

        # Conditional threshold: 48 hours for AU/CA visa restrictions, 40 hours standard international baseline
        statutory_hour_cap = 48 if country in ["Australia", "Canada"] else 40
        hour_breach = hours > statutory_hour_cap

        # Formula: Logistic sigmoid tax curve modeling progressive tax brackets without rigid tiers:
        # Tax Rate = 0.12 + (0.35 / (1 + e^(-0.04 * (Wage_USD - 25))))
        # Clamped between a minimum tax floor of 8% and a maximum ceiling of 48%
        logistic_tax_rate = min(0.48, max(0.08, 0.12 + 0.35 / (1.0 + math.exp(-0.04 * (wage_usd - 25.0)))))
        
        # Formula: Gross = Wage * Hours; Tax Amount = Gross * Tax Rate; Net = Gross - Tax Amount
        gross_local = wage_local * hours
        tax_withheld_local = gross_local * logistic_tax_rate
        net_local = gross_local - tax_withheld_local
        
        # Formula: Mandatory pension/superannuation estimation at fixed 11.5% statutory rate
        superannuation_local = gross_local * 0.115

        # Formula: Natural log wage disparity metric: ln(User Wage in USD / Legal Minimum Wage in USD)
        parity_differential = math.log(max(0.1, wage_usd) / max(0.1, statutory_min_usd))

        return {
            "currency": curr_code,
            "statutory_min_local": statutory_min_local,
            "wage_premium_pct": wage_premium_pct,
            "statutory_hour_cap": statutory_hour_cap,
            "hour_breach": hour_breach,
            "gross_local": gross_local,
            "tax_withheld_local": tax_withheld_local,
            "net_local": net_local,
            "super_local": superannuation_local,
            "effective_tax_pct": logistic_tax_rate * 100,
            "parity_differential": parity_differential
        }

    def on_country_selected(e):
        selected = country_dropdown.value
        if selected in country_metadata:
            meta = country_metadata[selected]
            curr_code = meta.get("currency_code", "USD")
            fx_rate = exchange_rates.get(curr_code, 1.0)
            local_min = meta.get("min_wage_usd", 1.50) * fx_rate
            wage_input.label = f"Hourly Wage ({curr_code})"
            wage_input.value = f"{local_min:.2f}"
            page.update()

    country_dropdown = ft.Dropdown(
        label="Select Jurisdiction (195+ sovereign entities)",
        hint_text="Loading global registry...",
        disabled=True,
        on_select=on_country_selected
    )

    def process_analytics(e):
        try:
            wage = float(wage_input.value or 0.0)
            hrs = float(hours_input.value or 0.0)
            country = country_dropdown.value or "Australia"

            status_bar.value = "Executing analytics..."
            page.update()

            payload = {
                "hourly_wage": wage,
                "hours_worked": hrs,
                "country_name": country,
                "claim_allowance": True
            }
            try:
                res = requests.post(f"{RENDER_API_BASE}/api/tax/calculate", json=payload, timeout=8)
                if res.status_code == 200:
                    data = res.json()
                    status_icon = "Compliant ✅" if data.get("is_visa_compliant", True) else "Breached ⚠️"
                    result_text.value = (
                        f"=== LIVE BACKEND COMPLIANCE ENGINE ===\n"
                        f"Gross Fortnight: ${data.get('gross_fortnight', 0):.2f}\n"
                        f"Statutory Tax: -${data.get('tax_withheld', 0):.2f}\n"
                        f"Net Take-Home: ${data.get('net_takehome', 0):.2f}\n"
                        f"Pension / Retirement: +${data.get('statutory_pension', 0):.2f}\n"
                        f"Visa Work Threshold: {status_icon}"
                    )
                    status_bar.value = "Calculated via active cloud API."
                    page.update()
                    return
            except Exception:
                pass

            analytics = calculate_cross_jurisdictional_analytics(wage, hrs, country)
            c = analytics["currency"]
            compliance_badge = "BREACH WARNING ⚠️" if analytics["hour_breach"] else "VISA COMPLIANT ✅"

            result_text.value = (
                f"=== ON-DEVICE MULTI-CURRENCY ANALYTIC ENGINE ===\n"
                f"Statutory Baseline Floor: {c} {analytics['statutory_min_local']:.2f}/hr\n"
                f"Wage Premium Spread: {analytics['wage_premium_pct']:+.1f}% vs. statutory minimum\n\n"
                f"Gross Earnings: {c} {analytics['gross_local']:.2f}\n"
                f"Algorithmic Tax (Progressive {analytics['effective_tax_pct']:.1f}%): -{c} {analytics['tax_withheld_local']:.2f}\n"
                f"Net Take-Home: {c} {analytics['net_local']:.2f}\n"
                f"Estimated Retirement/Super (11.5%): +{c} {analytics['super_local']:.2f}\n\n"
                f"Fortnight Limit ({analytics['statutory_hour_cap']} hrs): {compliance_badge}\n"
                f"Wage Differential Log Metric (D): {analytics['parity_differential']:.3f}"
            )
            status_bar.value = "Calculated locally via cross-jurisdictional mathematical engine."
            page.update()

        except Exception as err:
            result_text.value = f"Processing error: {str(err)}"
            page.update()

    def bootstrap_world_data():
        try:
            fx_res = requests.get(EXCHANGE_RATE_URL, timeout=10)
            if fx_res.status_code == 200:
                rates = fx_res.json().get("rates", {})
                exchange_rates.update(rates)

            c_res = requests.get(REST_COUNTRIES_URL, timeout=10)
            if c_res.status_code == 200:
                country_list = c_res.json()
                sorted_names = []

                for item in country_list:
                    common_name = item.get("name", {}).get("common")
                    if not common_name:
                        continue

                    currencies = item.get("currencies", {})
                    first_currency = list(currencies.keys())[0] if currencies else "USD"

                    min_wage = MINIMUM_WAGE_DEFAULTS_USD.get(
                        common_name,
                        REGIONAL_FLOOR_USD.get("Global Default", 1.50)
                    )

                    country_metadata[common_name] = {
                        "currency_code": first_currency,
                        "min_wage_usd": min_wage,
                        "population": item.get("population", 0)
                    }
                    sorted_names.append(common_name)

                sorted_names.sort()
                country_dropdown.options = [ft.dropdown.Option(name) for name in sorted_names]
                country_dropdown.value = "Australia" if "Australia" in country_metadata else sorted_names[0]
                country_dropdown.disabled = False
                country_dropdown.hint_text = "Select country"
                status_bar.value = f"Ready. Indexed {len(sorted_names)} sovereign jurisdictions."
                on_country_selected(None)
                page.update()
        except Exception as err:
            status_bar.value = f"Global entity discovery error: {str(err)}. Running on offline fallbacks."
            country_dropdown.options = [
                ft.dropdown.Option("Australia"),
                ft.dropdown.Option("United States"),
                ft.dropdown.Option("United Kingdom"),
                ft.dropdown.Option("Canada")
            ]
            country_dropdown.disabled = False
            page.update()

    calc_btn = ft.ElevatedButton(
        "Run Compliance & Net Pay",
        on_click=process_analytics,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE
    )

    page.add(
        ft.Text("BudgetWise AI Mobile", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
        ft.Text("Cross-Jurisdictional Statutory Limits & Foreign Exchange Engine", size=12, color=ft.Colors.GREY_400),
        status_bar,
        country_dropdown,
        wage_input,
        hours_input,
        calc_btn,
        ft.Divider(),
        result_text
    )

    bootstrap_world_data()

if __name__ == "__main__":
    ft.app(target=main)