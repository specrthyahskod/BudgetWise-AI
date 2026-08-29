from PyQt5.QtWidgets import (
    QDialog, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QDoubleSpinBox,
    QSpinBox, QProgressBar, QFrame, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from utils.currency_service import WORLD_COUNTRIES

COUNTRY_METRIC_PRESETS = {
    "Australia 🇦🇺": {"wage": 24.10, "shift_hrs": 6.0, "visa_limit": 48, "currency": "AUD ($)", "rent_bench": 350.0},
    "USA 🇺🇸": {"wage": 15.00, "shift_hrs": 4.0, "visa_limit": 40, "currency": "USD ($)", "rent_bench": 450.0},
    "UK 🇬🇧": {"wage": 11.44, "shift_hrs": 4.0, "visa_limit": 40, "currency": "GBP (£)", "rent_bench": 300.0},
    "Canada 🇨🇦": {"wage": 17.30, "shift_hrs": 5.0, "visa_limit": 48, "currency": "CAD ($)", "rent_bench": 380.0},
    "New Zealand 🇳🇿": {"wage": 23.15, "shift_hrs": 5.0, "visa_limit": 40, "currency": "NZD ($)", "rent_bench": 280.0},
    "Germany 🇩🇪": {"wage": 12.82, "shift_hrs": 4.0, "visa_limit": 40, "currency": "EUR (€)", "rent_bench": 320.0},
    "Ireland 🇮🇪": {"wage": 12.70, "shift_hrs": 4.0, "visa_limit": 40, "currency": "EUR (€)", "rent_bench": 340.0}
}

class StudentOnboardingWizard(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(620, 520)

        self.user_answers = {
            "origin_country": "India 🇮🇳",
            "study_destination": "Australia 🇦🇺",
            "study_level": "Undergraduate",
            "living_arrangement": "Shared Apartment",
            "weekly_rent": 300.0,
            "employment_type": "Casual / Part-Time",
            "hourly_wage": 24.10,
            "shift_hours": 6.0,
            "visa_fortnight_limit": 48,
            "transport_mode": "Public Transport",
            "grocery_diet": "Standard Cook-at-Home",
            "emergency_target": 500.0,
            "initial_vault": 250.0,
            "budget_alert_threshold": 80,
            "ai_safespend_strictness": "Standard (EWMA Balanced)",
            "primary_financial_goal": "Cover Tuition & Living"
        }

        self.init_ui()

    def init_ui(self):
        container = QFrame(self)
        container.setGeometry(0, 0, 620, 520)
        container.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border: 2px solid #3B82F6;
                border-radius: 16px;
            }
            QLabel { color: #F8FAFC; border: none; }
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QRadioButton { color: #CBD5E1; font-size: 13px; spacing: 8px; }
            QRadioButton::indicator { width: 16px; height: 16px; }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Header Bar
        top_bar = QHBoxLayout()
        self.lbl_step_counter = QLabel("Step 1 of 16")
        self.lbl_step_counter.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_step_counter.setStyleSheet("color: #60A5FA;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(1, 16)
        self.progress_bar.setValue(1)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background-color: #1E293B; border-radius: 4px; border: none; }
            QProgressBar::chunk { background-color: #3B82F6; border-radius: 4px; }
        """)

        top_bar.addWidget(self.lbl_step_counter)
        top_bar.addSpacing(10)
        top_bar.addWidget(self.progress_bar, 1)
        layout.addLayout(top_bar)

        self.steps_stack = QStackedWidget()
        self.create_all_16_steps()
        layout.addWidget(self.steps_stack, 1)

        nav_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Back")
        self.btn_back.setFixedHeight(38)
        self.btn_back.setStyleSheet("background-color: #1E293B; color: #94A3B8; font-weight: bold; border-radius: 8px; border: 1px solid #334155;")
        self.btn_back.clicked.connect(self.prev_step)
        self.btn_back.setEnabled(False)

        self.btn_next = QPushButton("Next →")
        self.btn_next.setFixedHeight(38)
        self.btn_next.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border-radius: 8px; border: none;")
        self.btn_next.clicked.connect(self.next_step)

        nav_layout.addWidget(self.btn_back)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_next)
        layout.addLayout(nav_layout)

    def create_page(self, title_text, desc_text):
        page = QWidget()
        lyt = QVBoxLayout(page)
        lyt.setContentsMargins(10, 10, 10, 10)
        lyt.setSpacing(12)

        t_lbl = QLabel(title_text)
        t_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        t_lbl.setStyleSheet("color: #F8FAFC;")

        d_lbl = QLabel(desc_text)
        d_lbl.setFont(QFont("Segoe UI", 10))
        d_lbl.setStyleSheet("color: #94A3B8;")
        d_lbl.setWordWrap(True)

        lyt.addWidget(t_lbl)
        lyt.addWidget(d_lbl)
        lyt.addSpacing(5)
        return page, lyt

    def create_all_16_steps(self):
        # Step 1: Study Destination 
        p1, l1 = self.create_page("🌍 Where are you studying?", "Select your target country to fetch student minimum wages, visa caps, and living indexes.")
        self.combo_dest = QComboBox()
        self.combo_dest.addItems(list(COUNTRY_METRIC_PRESETS.keys()) + ["Other International Destination 🌐"])
        self.combo_dest.currentTextChanged.connect(self.on_destination_selected)
        l1.addWidget(self.combo_dest)
        l1.addStretch()
        self.steps_stack.addWidget(p1)

        # Step 2: Origin Country 
        p2, l2 = self.create_page("🛫 Home / Origin Country", "Select your origin for customized real-time currency conversions.")
        self.combo_origin = QComboBox()
        country_keys = [f"{c} {f}" for c, (f, _, _, _) in WORLD_COUNTRIES.items()]
        self.combo_origin.addItems(country_keys)
        self.combo_origin.setCurrentText("India 🇮🇳")
        l2.addWidget(self.combo_origin)
        l2.addStretch()
        self.steps_stack.addWidget(p2)

        # Step 3: Academic Degree Level
        p3, l3 = self.create_page("🎓 Current Degree Level", "Your study profile helps calibrate expense patterns.")
        self.combo_degree = QComboBox()
        self.combo_degree.addItems(["Undergraduate / Bachelor's", "Postgraduate / Master's", "Doctorate / PhD", "Vocational / TAFE / Diploma", "High School / Foundation"])
        l3.addWidget(self.combo_degree)
        l3.addStretch()
        self.steps_stack.addWidget(p3)

        # Step 4: Hourly Wage Configuration (Auto-set by destination)
        p4, l4 = self.create_page("💵 Base Hourly Wage", "Auto-calculated based on destination national minimum student wage standards.")
        self.spin_wage = QDoubleSpinBox()
        self.spin_wage.setRange(5.0, 150.0)
        self.spin_wage.setValue(24.10)
        self.spin_wage.setPrefix("$ ")
        self.spin_wage.setSuffix(" / hr")
        l4.addWidget(self.spin_wage)
        l4.addStretch()
        self.steps_stack.addWidget(p4)

        # Step 5: Average Shift Hours
        p5, l5 = self.create_page("⏱️ Shift Duration", "Standard duration of one worked shift on your job.")
        self.spin_shift = QDoubleSpinBox()
        self.spin_shift.setRange(1.0, 12.0)
        self.spin_shift.setValue(6.0)
        self.spin_shift.setSuffix(" hours / shift")
        l5.addWidget(self.spin_shift)
        l5.addStretch()
        self.steps_stack.addWidget(p5)

        # Step 6: Visa Fortnight Work Limits
        p6, l6 = self.create_page("📜 Visa Work Limitation Cap", "Maximum allowed work hours per fortnight during study terms.")
        self.spin_visa = QSpinBox()
        self.spin_visa.setRange(0, 80)
        self.spin_visa.setValue(48)
        self.spin_visa.setSuffix(" hours / fortnight")
        l6.addWidget(self.spin_visa)
        l6.addStretch()
        self.steps_stack.addWidget(p6)

        # Step 7: Accommodation Style
        p7, l7 = self.create_page("🏠 Accommodation Type", "Where are you currently residing?")
        self.combo_living = QComboBox()
        self.combo_living.addItems(["Shared Student Apartment", "Private Studio / Flat", "On-Campus Dormitory", "Homestay / Family", "Sublet / Temporary"])
        l7.addWidget(self.combo_living)
        l7.addStretch()
        self.steps_stack.addWidget(p7)

        # Step 8: Weekly Rent / Housing Cost
        p8, l8 = self.create_page("💳 Weekly Rent & Utilities", "Estimated housing allocation per week.")
        self.spin_rent = QDoubleSpinBox()
        self.spin_rent.setRange(0.0, 2000.0)
        self.spin_rent.setValue(300.0)
        self.spin_rent.setPrefix("$ ")
        self.spin_rent.setSuffix(" / wk")
        l8.addWidget(self.spin_rent)
        l8.addStretch()
        self.steps_stack.addWidget(p8)

        # Step 9: Daily Commute / Transit Method
        p9, l9 = self.create_page("🚆 Commute & Transit", "Primary method of travel to university and workplace.")
        self.combo_transit = QComboBox()
        self.combo_transit.addItems(["Public Transit (Concession Bus/Train)", "Walking / Cycling", "Personal Car / Motorbike", "Rideshare / Uber"])
        l9.addWidget(self.combo_transit)
        l9.addStretch()
        self.steps_stack.addWidget(p9)

        # Step 10: Grocery & Meal Budgeting Style
        p10, l10 = self.create_page("🛒 Meal & Grocery Habits", "How do you plan your food expenses?")
        self.combo_meals = QComboBox()
        self.combo_meals.addItems(["Budget Home-Cooking (Aldi / Coles specials)", "Balanced Cooking & Weekly Dining Out", "Frequent Takeout / Campus Cafes", "Meal Plan Provided"])
        l10.addWidget(self.combo_meals)
        l10.addStretch()
        self.steps_stack.addWidget(p10)

        # Step 11: Emergency Vault Starting Capital
        p11, l11 = self.create_page("🛡️ Starting Emergency Vault", "Initial reserve funds to isolate in your emergency vault.")
        self.spin_vault_init = QDoubleSpinBox()
        self.spin_vault_init.setRange(0.0, 10000.0)
        self.spin_vault_init.setValue(300.0)
        self.spin_vault_init.setPrefix("$ ")
        l11.addWidget(self.spin_vault_init)
        l11.addStretch()
        self.steps_stack.addWidget(p11)

        # Step 12: Emergency Vault Target Goal
        p12, l12 = self.create_page("🎯 Emergency Target Reserve", "Minimum target balance before unrestricted non-emergency withdrawals unlock.")
        self.spin_vault_target = QDoubleSpinBox()
        self.spin_vault_target.setRange(100.0, 20000.0)
        self.spin_vault_target.setValue(500.0)
        self.spin_vault_target.setPrefix("$ ")
        l12.addWidget(self.spin_vault_target)
        l12.addStretch()
        self.steps_stack.addWidget(p12)

        # Step 13: AI SafeSpend Sensitivity Linker
        p13, l13 = self.create_page("🤖 AI SafeSpend Sensitivity", "Tune the EWMA pace monitor for predictive expense warnings.")
        self.combo_ai_strict = QComboBox()
        self.combo_ai_strict.addItems(["Strict (EWMA Alpha 0.50 - High Vigilance)", "Standard (EWMA Alpha 0.35 - Balanced)", "Relaxed (EWMA Alpha 0.20 - Flexible)"])
        self.combo_ai_strict.setCurrentIndex(1)
        l13.addWidget(self.combo_ai_strict)
        l13.addStretch()
        self.steps_stack.addWidget(p13)

        # Step 14: Fortnight Budget Burn Alert Trigger
        p14, l14 = self.create_page("⚠️ Budget Alert Threshold", "Trigger UI warnings when spending exceeds this percentage of total fortnight budget.")
        self.spin_burn_alert = QSpinBox()
        self.spin_burn_alert.setRange(50, 95)
        self.spin_burn_alert.setValue(80)
        self.spin_burn_alert.setSuffix("% of Total Budget")
        l14.addWidget(self.spin_burn_alert)
        l14.addStretch()
        self.steps_stack.addWidget(p14)

        # Step 15: Primary Financial Objective
        p15, l15 = self.create_page("🎯 Primary Financial Goal", "What is your main financial priority this semester?")
        self.combo_goal = QComboBox()
        self.combo_goal.addItems(["Build Emergency Savings Buffer", "Pay Upcoming Semester Tuition", "Cover Living Expenses Independently", "Travel & Holiday Fund"])
        l15.addWidget(self.combo_goal)
        l15.addStretch()
        self.steps_stack.addWidget(p15)

        # Step 16: Automated App Setup Confirmation
        p16, l16 = self.create_page("🚀 Ready to Launch BudgetWise AI!", "Click Finish to apply these parameters, initialize your emergency vault, and customize your workspace.")
        self.lbl_summary = QLabel()
        self.lbl_summary.setStyleSheet("color: #4ADE80; font-size: 13px; font-weight: bold;")
        l16.addWidget(self.lbl_summary)
        l16.addStretch()
        self.steps_stack.addWidget(p16)

    def on_destination_selected(self, dest):
        if dest in COUNTRY_METRIC_PRESETS:
            preset = COUNTRY_METRIC_PRESETS[dest]
            self.spin_wage.setValue(preset["wage"])
            self.spin_shift.setValue(preset["shift_hrs"])
            self.spin_visa.setValue(preset["visa_limit"])
            self.spin_rent.setValue(preset["rent_bench"])

    def next_step(self):
        curr_idx = self.steps_stack.currentIndex()
        if curr_idx < 15:
            if curr_idx == 14:
                self.lbl_summary.setText(
                    f"✓ Studying in: {self.combo_dest.currentText()}\n"
                    f"✓ Base Hourly Wage: ${self.spin_wage.value():.2f}/hr\n"
                    f"✓ Fortnight Visa Cap: {self.spin_visa.value()} Hours\n"
                    f"✓ Emergency Vault Starting Capital: ${self.spin_vault_init.value():.2f}\n"
                    f"✓ Primary Target: {self.combo_goal.currentText()}"
                )
                self.btn_next.setText("Finish & Configure App ✨")
                self.btn_next.setStyleSheet("background-color: #16A34A; color: white; font-weight: bold; border-radius: 8px; border: none;")

            self.steps_stack.setCurrentIndex(curr_idx + 1)
            self.progress_bar.setValue(curr_idx + 2)
            self.lbl_step_counter.setText(f"Step {curr_idx + 2} of 16")
            self.btn_back.setEnabled(True)
        else:
            self.collect_and_save()
            self.accept()

    def prev_step(self):
        curr_idx = self.steps_stack.currentIndex()
        if curr_idx > 0:
            self.steps_stack.setCurrentIndex(curr_idx - 1)
            self.progress_bar.setValue(curr_idx)
            self.lbl_step_counter.setText(f"Step {curr_idx} of 16")
            self.btn_next.setText("Next →")
            self.btn_next.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border-radius: 8px; border: none;")
            if curr_idx - 1 == 0:
                self.btn_back.setEnabled(False)

    def collect_and_save(self):
        self.user_answers = {
            "origin_country": self.combo_origin.currentText(),
            "study_destination": self.combo_dest.currentText(),
            "study_level": self.combo_degree.currentText(),
            "hourly_wage": self.spin_wage.value(),
            "hours_per_shift": self.spin_shift.value(),
            "visa_fortnight_limit": self.spin_visa.value(),
            "living_arrangement": self.combo_living.currentText(),
            "weekly_rent": self.spin_rent.value(),
            "transport_mode": self.combo_transit.currentText(),
            "grocery_diet": self.combo_meals.currentText(),
            "emergency_vault": self.spin_vault_init.value(),
            "emergency_target": self.spin_vault_target.value(),
            "ai_safespend_strictness": self.combo_ai_strict.currentText(),
            "budget_alert_threshold": self.spin_burn_alert.value(),
            "primary_financial_goal": self.combo_goal.currentText(),
            "onboarding_completed": True
        }

    def get_configured_profile(self):
        return self.user_answers