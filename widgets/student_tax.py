from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QCheckBox, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


COUNTRY_TAX_RULES = {
    "Australia": {
        "currency": "AUD ($)",
        "symbol": "$",
        "tax_authority": "ATO (Pay-As-You-Go / PAYG)",
        "pension_name": "Superannuation Guarantee (11.5%)",
        "pension_rate": 0.115,
        "refund_scheme": "DASP Claimable on Departure (Net ~65%)",
        "refund_retention": 0.65,
        "threshold_label": "Claim Tax-Free Threshold ($18,200 annual baseline)",
        "default_threshold": True,
        "calc": "calc_australia"
    },
    "United States": {
        "currency": "USD ($)",
        "symbol": "$",
        "tax_authority": "IRS (Federal Income Tax & F-1 Treaty)",
        "pension_name": "Social Security & Medicare (FICA Exempt for F-1)",
        "pension_rate": 0.0,
        "refund_scheme": "IRS 1040-NR Refund Claim Potential",
        "refund_retention": 1.0,
        "threshold_label": "Apply Student Tax Treaty Benefit ($2,000 baseline)",
        "default_threshold": True,
        "calc": "calc_usa"
    },
    "United Kingdom": {
        "currency": "GBP (£)",
        "symbol": "£",
        "tax_authority": "HMRC (PAYE & National Insurance)",
        "pension_name": "Workplace Auto-Enrolment Pension (5%)",
        "pension_rate": 0.05,
        "refund_scheme": "HMRC P85 Post-Departure Repayment",
        "refund_retention": 0.85,
        "threshold_label": "Claim Personal Allowance (£12,570 annual tax-free)",
        "default_threshold": True,
        "calc": "calc_uk"
    },
    "Canada": {
        "currency": "CAD ($)",
        "symbol": "$",
        "tax_authority": "CRA (T1 Federal & Basic Personal Amount)",
        "pension_name": "Canada Pension Plan / CPP (5.95%)",
        "pension_rate": 0.0595,
        "refund_scheme": "CRA T1 Return Refund Potential",
        "refund_retention": 1.0,
        "threshold_label": "Claim Basic Personal Amount (CAD $15,705)",
        "default_threshold": True,
        "calc": "calc_canada"
    },
    "Germany": {
        "currency": "EUR (€)",
        "symbol": "€",
        "tax_authority": "Finanzamt (Lohnsteuer & Werkstudent Rules)",
        "pension_name": "Rentenversicherung / Pension (9.3%)",
        "pension_rate": 0.093,
        "refund_scheme": "VBL / Pension Refund to Non-EU (after 24 mos)",
        "refund_retention": 1.0,
        "threshold_label": "Werkstudent / Mini-Job Allowance (€12,348 annual)",
        "default_threshold": True,
        "calc": "calc_germany"
    }
}


def normalize_country_key(country_input):
    country_str = str(country_input).lower()
    if "australia" in country_str:
        return "Australia"
    elif "united states" in country_str or "usa" in country_str or "america" in country_str:
        return "United States"
    elif "kingdom" in country_str or "uk" in country_str or "britain" in country_str:
        return "United Kingdom"
    elif "canada" in country_str:
        return "Canada"
    elif "germany" in country_str or "deutschland" in country_str:
        return "Germany"
    return "Australia"


class TaxCalculator(QDialog):
    def __init__(self, hourly_wage, hours_worked_fn, country_name="Australia", parent=None):
        super().__init__(parent)
        self.hourly_wage = float(hourly_wage)
        self.hours_worked_fn = float(hours_worked_fn)
        self.current_country = normalize_country_key(country_name)
        
        self.setWindowTitle("Student Tax Calculator")
        self.setFixedSize(540, 560)
        self.setStyleSheet("background-color: #0F172A; color: #F8FAFC;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        title = QLabel("🏛️ Student Tax Calculator")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subtitle = QLabel("")
        self.subtitle.setFont(QFont("Segoe UI", 9))
        self.subtitle.setStyleSheet("color: #94A3B8;")
        self.subtitle.setWordWrap(True)
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        c_frame = QFrame()
        c_frame.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; border-radius: 8px;")
        c_layout = QHBoxLayout(c_frame)
        c_layout.setContentsMargins(12, 6, 12, 6)

        c_lbl = QLabel("Study Destination:")
        c_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        
        self.combo_country = QComboBox()
        self.combo_country.addItems(list(COUNTRY_TAX_RULES.keys()))
        self.combo_country.setCurrentText(self.current_country)
        self.combo_country.setFixedHeight(30)
        self.combo_country.setStyleSheet("background-color: #0F172A; color: #F8FAFC; border: 1px solid #334155; border-radius: 4px; padding: 2px 8px;")
        self.combo_country.currentTextChanged.connect(self.on_country_switched)

        c_layout.addWidget(c_lbl)
        c_layout.addWidget(self.combo_country, 1)

        inputs_frame = QFrame()
        inputs_frame.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; border-radius: 10px; padding: 10px;")
        in_layout = QVBoxLayout(inputs_frame)
        in_layout.setSpacing(8)

        self.chk_threshold = QCheckBox("")
        self.chk_threshold.setStyleSheet("color: #F8FAFC; font-weight: bold;")
        self.chk_threshold.toggled.connect(self.calculate_all)

        self.lbl_gross_info = QLabel("")
        self.lbl_gross_info.setStyleSheet("color: #60A5FA; font-size: 11px;")

        in_layout.addWidget(self.chk_threshold)
        in_layout.addWidget(self.lbl_gross_info)

        out_frame = QFrame()
        out_frame.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; border-radius: 10px; padding: 12px;")
        out_layout = QVBoxLayout(out_frame)
        out_layout.setSpacing(9)

        self.lbl_gross = self.create_row(out_layout, "Gross Fortnight Pay:", "$0.00", "#F8FAFC")
        self.lbl_tax = self.create_row(out_layout, "Income Tax Withheld:", "-$0.00", "#F87171")
        self.lbl_net = self.create_row(out_layout, "Estimated Net Take-Home Pay:", "$0.00", "#4ADE80", is_bold=True)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #334155;")
        out_layout.addWidget(sep)

        self.lbl_pension = self.create_row(out_layout, "Employer/Employee Contribution:", "+$0.00", "#38BDF8")
        self.lbl_refund = self.create_row(out_layout, "Departure Claim / Refund Potential:", "$0.00", "#FCD34D")

        btn_close = QPushButton("Done")
        btn_close.setFixedHeight(36)
        btn_close.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border-radius: 6px; border: none;")
        btn_close.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(self.subtitle)
        layout.addWidget(c_frame)
        layout.addWidget(inputs_frame)
        layout.addWidget(out_frame)
        layout.addWidget(btn_close)

        self.setLayout(layout)
        self.apply_country_profile()

    def create_row(self, layout, label_text, val_text, color_code, is_bold=False):
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
        val = QLabel(val_text)
        val.setFont(QFont("Segoe UI", 11 if not is_bold else 13, QFont.Bold if is_bold else QFont.Normal))
        val.setStyleSheet(f"color: {color_code};")
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(val)
        layout.addLayout(row)
        return val

    def on_country_switched(self, country_name):
        self.current_country = country_name
        self.apply_country_profile()

    def apply_country_profile(self):
        rules = COUNTRY_TAX_RULES[self.current_country]
        self.subtitle.setText(f"Tax framework made for international students under {rules['tax_authority']} for 2026-27.")
        self.chk_threshold.setText(rules["threshold_label"])
        self.chk_threshold.setChecked(rules["default_threshold"])
        
        sym = rules["symbol"]
        self.lbl_gross_info.setText(
            f"Gross Rate: {sym}{self.hourly_wage:.2f}/hr | Fortnightly Scheduled: {self.hours_worked_fn:.1f} hrs"
        )
        self.calculate_all()

    def calculate_all(self):
        rules = COUNTRY_TAX_RULES[self.current_country]
        calc_func = getattr(self, rules["calc"])
        
        gross_fn = self.hourly_wage * self.hours_worked_fn
        annual_gross = gross_fn * 26.0
        is_threshold = self.chk_threshold.isChecked()
        
        annual_tax, annual_pension = calc_func(annual_gross, is_threshold)
        
        tax_fn = annual_tax / 26.0
        net_takehome = max(gross_fn - tax_fn, 0.0)
        pension_fn = (annual_pension / 26.0) if annual_pension > 0 else (gross_fn * rules["pension_rate"])
        refund_fn = pension_fn * rules["refund_retention"]

        sym = rules["symbol"]
        self.lbl_gross.setText(f"{sym}{gross_fn:,.2f}")
        self.lbl_tax.setText(f"-{sym}{tax_fn:,.2f}")
        self.lbl_net.setText(f"{sym}{net_takehome:,.2f}")
        self.lbl_pension.setText(f"+{sym}{pension_fn:,.2f}")
        self.lbl_refund.setText(f"Est. {sym}{refund_fn:,.2f} / fn")

    def calc_australia(self, annual_gross, threshold_claimed):
        if threshold_claimed:
            if annual_gross <= 18200:
                tax = 0.0
            elif annual_gross <= 45000:
                tax = (annual_gross - 18200) * 0.16
            elif annual_gross <= 135000:
                tax = 4288 + (annual_gross - 45000) * 0.30
            else:
                tax = 31288 + (annual_gross - 135000) * 0.37
        else:
            tax = annual_gross * 0.30
        pension = annual_gross * 0.115
        return tax, pension

    def calc_usa(self, annual_gross, treaty_claimed):
        taxable = max(annual_gross - (2000.0 if treaty_claimed else 0.0), 0.0)
        if taxable <= 11600:
            tax = taxable * 0.10
        elif taxable <= 47150:
            tax = 1160 + (taxable - 11600) * 0.12
        else:
            tax = 5426 + (taxable - 47150) * 0.22
        return tax, 0.0

    def calc_uk(self, annual_gross, allowance_claimed):
        allowance = 12570.0 if allowance_claimed else 0.0
        taxable = max(annual_gross - allowance, 0.0)
        
        if taxable <= 37700:
            it = taxable * 0.20
        else:
            it = 7540 + (taxable - 37700) * 0.40
            
        ni_threshold = 12570.0
        ni = max(annual_gross - ni_threshold, 0.0) * 0.08
        return (it + ni), (annual_gross * 0.05)

    def calc_canada(self, annual_gross, bpa_claimed):
        bpa = 15705.0 if bpa_claimed else 0.0
        taxable = max(annual_gross - bpa, 0.0)
        
        if taxable <= 55867:
            fed_tax = taxable * 0.15
        else:
            fed_tax = 8380 + (taxable - 55867) * 0.205
            
        prov_tax = taxable * 0.05
        return (fed_tax + prov_tax), (annual_gross * 0.0595)

    def calc_germany(self, annual_gross, werkstudent_mode):
        allowance = 12348.0 if werkstudent_mode else 0.0
        taxable = max(annual_gross - allowance, 0.0)
        
        if taxable <= 0:
            tax = 0.0
        elif taxable <= 17005:
            tax = taxable * 0.14
        else:
            tax = 2380 + (taxable - 17005) * 0.24
            
        pension = annual_gross * 0.093
        return tax, pension