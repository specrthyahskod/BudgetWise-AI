import flet as ft
import urllib.request
import json

def main(page: ft.Page):
    page.title = "BudgetWise Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    wage_input = ft.TextField(label="Hourly Wage ($)", value="26.44")
    hours_input = ft.TextField(label="Hours Worked (Fortnight)", value="40")
    result_text = ft.Text(size=16, weight=ft.FontWeight.BOLD)

    def calculate_tax(e):
        try:
            wage = float(wage_input.value)
            hrs = float(hours_input.value)
            gross = wage * hrs
            tax = gross * 0.15
            net = gross - tax
            result_text.value = f"Gross: ${gross:.2f}\nTax: -${tax:.2f}\nNet Pay: ${net:.2f}"
            page.update()
        except ValueError:
            result_text.value = "Please enter valid numeric inputs."
            page.update()

    calc_btn = ft.ElevatedButton("Run Compliance & Net Pay", on_click=calculate_tax)

    page.add(
        ft.Text("BudgetWise AI Mobile", size=22, weight=ft.FontWeight.BOLD),
        wage_input,
        hours_input,
        calc_btn,
        result_text
    )

if __name__ == "__main__":
    ft.app(target=main)