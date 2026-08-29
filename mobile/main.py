import flet as ft
import requests

RENDER_API_BASE = "https://budgetwise-ai.onrender.com"

def main(page: ft.Page):
    page.title = "BudgetWise Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    wage_input = ft.TextField(
        label="Hourly Wage ($)",
        value="26.44",
        keyboard_type=ft.KeyboardType.NUMBER
    )
    hours_input = ft.TextField(
        label="Fortnight Hours Worked",
        value="40",
        keyboard_type=ft.KeyboardType.NUMBER
    )
    country_dropdown = ft.Dropdown(
        label="Jurisdiction",
        value="Australia",
        options=[
            ft.dropdown.Option("Australia"),
            ft.dropdown.Option("United States"),
            ft.dropdown.Option("United Kingdom"),
        ]
    )

    result_text = ft.Text(size=14, weight=ft.FontWeight.W_500)

    def calculate_tax(e):
        try:
            wage = float(wage_input.value)
            hrs = float(hours_input.value)
            country = country_dropdown.value
            
            payload = {
                "hourly_wage": wage,
                "hours_worked": hrs,
                "country_name": country,
                "claim_allowance": True
            }
            
            res = requests.post(
                f"{RENDER_API_BASE}/api/tax/calculate",
                json=payload,
                timeout=10
            )
            if res.status_code == 200:
                data = res.json()
                status_icon = "Compliant ✅" if data.get("is_visa_compliant", True) else "Breached ⚠️"
                result_text.value = (
                    f"Gross Pay: ${data['gross_fortnight']:.2f}\n"
                    f"Tax Withheld: -${data['tax_withheld']:.2f}\n"
                    f"Net Take-Home: ${data['net_takehome']:.2f}\n"
                    f"Pension/Super: +${data['statutory_pension']:.2f}\n"
                    f"Visa Status: {status_icon}"
                )
            else:
                gross = wage * hrs
                result_text.value = (
                    f"Offline Estimate:\n"
                    f"Gross: ${gross:.2f}\n"
                    f"Estimated Net: ${gross * 0.85:.2f}"
                )
            page.update()
        except Exception as err:
            result_text.value = f"Calculation error: {str(err)}"
            page.update()

    calc_btn = ft.ElevatedButton(
        "Run Compliance & Net Pay",
        on_click=calculate_tax,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE
    )

    page.add(
        ft.Text("BudgetWise AI Mobile", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
        ft.Text("Personalized student statutory tax & work limits", size=12, color=ft.Colors.GREY_400),
        country_dropdown,
        wage_input,
        hours_input,
        calc_btn,
        ft.Divider(),
        result_text
    )

if __name__ == "__main__":
    ft.app(target=main)