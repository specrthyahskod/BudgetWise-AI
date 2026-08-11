import os
import sys
import webbrowser
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QDialog, QLineEdit, QComboBox, QDateEdit, QMessageBox, QCalendarWidget,
    QMenu, QFileDialog, QInputDialog
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QPixmap, QIcon

from utils.manager import ThemeManager
from utils.user_data_manager import UserDataManager
from models.ai_engine import StudentAIEngine

ai_engine = StudentAIEngine()

COUNTRY_DATA = {
    "India 🇮🇳": {"currency": "INR (₹)", "rate": 55.50},
    "China 🇨🇳": {"currency": "CNY (¥)", "rate": 4.75},
    "USA 🇺🇸": {"currency": "USD ($)", "rate": 0.66},
    "Nepal 🇳🇵": {"currency": "NPR (रू)", "rate": 88.80},
    "Vietnam 🇻🇳": {"currency": "VND (₫)", "rate": 16500.0},
    "UK 🇬🇧": {"currency": "GBP (£)", "rate": 0.52},
    "Philippines 🇵🇭": {"currency": "PHP (₱)", "rate": 38.20},
    "Malaysia 🇲🇾": {"currency": "MYR (RM)", "rate": 3.10}
}

def calculate_ewma(samples, alpha=0.35):
    if not samples:
        return 0.0
    ewma = samples[0]
    for sample in samples[1:]:
        ewma = (alpha * sample) + ((1 - alpha) * ewma)
    return ewma

class WorkCalendarDialog(QDialog):
    def __init__(self, work_days, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Work Shift Calendar")
        self.setFixedSize(420, 500)
        self.setStyleSheet("background-color: #0F172A; color: #F8FAFC;")
        self.work_days = set(work_days)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("📅 Work Shift Tracker")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 10px;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #0F172A;
                border-bottom: 1px solid #334155;
            }
            QCalendarWidget QToolButton {
                color: #F8FAFC;
                background-color: transparent;
                font-weight: bold;
                border-radius: 4px;
            }
            QCalendarWidget QToolButton:hover { background-color: #334155; }
            QCalendarWidget QMenu { background-color: #1E293B; color: #F8FAFC; }
            QCalendarWidget QSpinBox { color: #F8FAFC; background-color: #0F172A; }
            QCalendarWidget QTableView {
                background-color: #1E293B;
                color: #F8FAFC;
                selection-background-color: #2563EB;
                gridline-color: #334155;
            }
            QCalendarWidget QHeaderView::section {
                background-color: #0F172A;
                color: #94A3B8;
                font-weight: bold;
                border: none;
                padding: 4px;
            }
        """)

        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(QColor("#16A34A"))
        self.highlight_format.setForeground(QColor("#FFFFFF"))
        self.normal_format = QTextCharFormat()

        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.status_label.setStyleSheet("color: #60A5FA;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_toggle = QPushButton("Mark / Unmark Date Worked")
        btn_toggle.setFixedHeight(38)
        btn_toggle.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border-radius: 6px; border: none;")
        btn_toggle.clicked.connect(self.toggle_selected_date)

        btn_save = QPushButton("Save & Update Budget")
        btn_save.setFixedHeight(38)
        btn_save.setStyleSheet("background-color: #16A34A; color: white; font-weight: bold; border-radius: 6px; border: none;")
        btn_save.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(self.calendar)
        layout.addWidget(btn_toggle)
        layout.addWidget(self.status_label)
        layout.addWidget(btn_save)

        self.setLayout(layout)
        self.apply_calendar_highlights()

    def apply_calendar_highlights(self):
        for date_str in self.work_days:
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            self.calendar.setDateTextFormat(qdate, self.highlight_format)
        self.status_label.setText(f"Shifts Logged in Fortnight: {len(self.work_days)} Days")

    def toggle_selected_date(self):
        selected_qdate = self.calendar.selectedDate()
        date_str = selected_qdate.toString("yyyy-MM-dd")
        if date_str in self.work_days:
            self.work_days.remove(date_str)
            self.calendar.setDateTextFormat(selected_qdate, self.normal_format)
        else:
            self.work_days.add(date_str)
            self.calendar.setDateTextFormat(selected_qdate, self.highlight_format)
        self.status_label.setText(f"Shifts Logged in Fortnight: {len(self.work_days)} Days")

    def get_work_days(self):
        return list(self.work_days)

class EmergencyFundDialog(QDialog):
    def __init__(self, current_fund, remaining_savings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Emergency Vault Control")
        self.setFixedSize(340, 260)
        self.current_fund = current_fund
        self.remaining_savings = remaining_savings
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("🛡️ Emergency Fund Vault")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.info_label = QLabel(f"Vault Balance: ${self.current_fund:.2f}\nFortnight Savings: ${self.remaining_savings:.2f}")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter Amount ($)")
        self.amount_input.setFixedHeight(34)

        btn_deposit = QPushButton("Deposit to Vault")
        btn_deposit.setFixedHeight(34)
        btn_deposit.setStyleSheet("background-color: #16A34A; color: white; font-weight: bold; border: none;")
        btn_deposit.clicked.connect(self.deposit)

        btn_withdraw = QPushButton("Withdraw Emergency Funds")
        btn_withdraw.setFixedHeight(34)
        btn_withdraw.setStyleSheet("background-color: #DC2626; color: white; font-weight: bold; border: none;")
        btn_withdraw.clicked.connect(self.withdraw)

        layout.addWidget(title)
        layout.addWidget(self.info_label)
        layout.addWidget(self.amount_input)
        layout.addWidget(btn_deposit)
        layout.addWidget(btn_withdraw)

        self.setLayout(layout)

    def deposit(self):
        try:
            val = float(self.amount_input.text().strip())
            if val <= 0:
                return
            self.current_fund += val
            self.accept()
        except:
            pass

    def withdraw(self):
        if self.remaining_savings >= 500.0:
            QMessageBox.warning(
                self, 
                "🔒 Vault Locked!", 
                f"Emergency withdrawal is locked!\n\nYour fortnight savings (${self.remaining_savings:.2f}) is $500 or more. The Emergency Fund can ONLY be touched when savings fall below $500 AUD."
            )
            return

        try:
            val = float(self.amount_input.text().strip())
            if val > self.current_fund:
                QMessageBox.warning(self, "Error", "Cannot withdraw more than current vault balance!")
                return
            self.current_fund -= val
            self.accept()
        except:
            pass

    def get_fund(self):
        return self.current_fund

class CurrencyConverterDialog(QDialog):
    def __init__(self, selected_country, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Personalized AUD Currency Converter")
        self.setFixedSize(320, 260)
        self.selected_country = selected_country
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("🔀 AUD Converter")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.aud_input = QLineEdit()
        self.aud_input.setPlaceholderText("Amount in AUD ($)")
        self.aud_input.setFixedHeight(34)

        self.country_combo = QComboBox()
        country_keys = list(COUNTRY_DATA.keys())
        self.country_combo.addItems(country_keys)
        self.country_combo.setCurrentText(self.selected_country)
        self.country_combo.setFixedHeight(34)

        self.result_label = QLabel("Converted: ---")
        self.result_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.result_label.setStyleSheet("color: #2563EB;")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        calc_btn = QPushButton("Convert")
        calc_btn.setFixedHeight(36)
        calc_btn.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border-radius: 6px; border: none;")
        calc_btn.clicked.connect(self.calculate_conversion)

        layout.addWidget(title)
        layout.addWidget(QLabel("Select Country Currency:"))
        layout.addWidget(self.country_combo)
        layout.addWidget(self.aud_input)
        layout.addWidget(calc_btn)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def calculate_conversion(self):
        aud_text = self.aud_input.text().strip()
        if aud_text == "":
            self.result_label.setText("Enter a valid number!")
            return
        try:
            aud = float(aud_text)
            c_name = self.country_combo.currentText()
            info = COUNTRY_DATA[c_name]
            rate = info["rate"]
            currency_code = info["currency"]
            converted = aud * rate
            symbol = currency_code.split(" ")[1]
            self.result_label.setText(f"Converted: {symbol}{converted:,.2f}")
        except:
            self.result_label.setText("Enter a valid number!")

class VisaWorkTrackerDialog(QDialog):
    def __init__(self, hourly_wage, hours_worked, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Australia Visa Work Limits")
        self.setFixedSize(340, 290)
        self.hourly_wage = hourly_wage
        self.hours_worked = hours_worked
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("⏱️ Visa Work Tracker")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.w1_input = QLineEdit()
        self.w1_input.setPlaceholderText("Week 1 Hours Worked")
        self.w1_input.setText(str(self.hours_worked / 2.0))
        self.w1_input.setFixedHeight(34)

        self.w2_input = QLineEdit()
        self.w2_input.setPlaceholderText("Week 2 Hours Worked")
        self.w2_input.setText(str(self.hours_worked / 2.0))
        self.w2_input.setFixedHeight(34)

        self.status_label = QLabel(f"Limit: 48 hrs / fortnight | Pay: ${self.hourly_wage:.2f}/hr")
        self.status_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        check_btn = QPushButton("Update Work Hours")
        check_btn.setFixedHeight(36)
        check_btn.setStyleSheet("background-color: #16A34A; color: white; font-weight: bold; border-radius: 6px; border: none;")
        check_btn.clicked.connect(self.check_compliance)

        layout.addWidget(title)
        layout.addWidget(self.w1_input)
        layout.addWidget(self.w2_input)
        layout.addWidget(check_btn)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def check_compliance(self):
        w1_text = self.w1_input.text().strip()
        w2_text = self.w2_input.text().strip()
        
        w1 = float(w1_text) if w1_text != "" else 0.0
        w2 = float(w2_text) if w2_text != "" else 0.0

        self.hours_worked = w1 + w2
        earnings = self.hours_worked * self.hourly_wage

        if self.hours_worked > 48:
            self.status_label.setText(f"❌ Visa Breach! {self.hours_worked} hrs (>48 hrs)\nEarned: ${earnings:,.2f}")
            self.status_label.setStyleSheet("color: #DC2626; font-weight: bold;")
        else:
            rem = 48 - self.hours_worked
            self.status_label.setText(f"✅ Compliant! Total: {self.hours_worked} hrs ({rem} hrs left)\nEst. Income: ${earnings:,.2f}")
            self.status_label.setStyleSheet("color: #16A34A; font-weight: bold;")
            self.accept()

    def get_hours(self):
        return self.hours_worked

class SetWageDialog(QDialog):
    def __init__(self, current_wage, current_shift_hours, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Wage & Shift Details")
        self.setFixedSize(300, 220)
        self.init_ui(current_wage, current_shift_hours)

    def init_ui(self, current_wage, current_shift_hours):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("Input Work Details")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(QLabel("Hourly Wage (AUD):"))
        self.wage_input = QLineEdit()
        self.wage_input.setText(str(current_wage))
        self.wage_input.setFixedHeight(34)
        layout.addWidget(self.wage_input)

        layout.addWidget(QLabel("Hours Worked Per Shift:"))
        self.hours_input = QLineEdit()
        self.hours_input.setText(str(current_shift_hours))
        self.hours_input.setFixedHeight(34)
        layout.addWidget(self.hours_input)

        save_btn = QPushButton("Save Details")
        save_btn.setFixedHeight(34)
        save_btn.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border-radius: 6px; border: none;")
        save_btn.clicked.connect(self.accept)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def get_details(self):
        w_text = self.wage_input.text().strip()
        h_text = self.hours_input.text().strip()
        try:
            w = float(w_text)
        except:
            w = 26.44

        try:
            h = float(h_text)
        except:
            h = 6.0

        return w, h

class AddTransactionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI-Assisted Transaction Log")
        self.setFixedSize(340, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Add Transaction")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setFixedHeight(34)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description (e.g. Coles Groceries)")
        self.desc_input.setFixedHeight(34)
        self.desc_input.textChanged.connect(self.auto_predict_category)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["Food", "Education", "Transport", "Shopping", "Entertainment", "Income"])
        self.category_combo.setFixedHeight(34)

        self.ai_badge = QLabel("🤖 AI Category Predictor: Active")
        self.ai_badge.setStyleSheet("color: #2563EB; font-size: 11px; font-weight: bold;")

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount ($)")
        self.amount_input.setFixedHeight(34)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #DC2626; font-size: 11px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Transaction")
        save_btn.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border: none;")
        save_btn.clicked.connect(self.validate_and_accept)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)

        layout.addWidget(title)
        layout.addWidget(QLabel("Date:"))
        layout.addWidget(self.date_input)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.desc_input)
        layout.addWidget(self.ai_badge)
        layout.addWidget(QLabel("Category:"))
        layout.addWidget(self.category_combo)
        layout.addWidget(QLabel("Amount ($):"))
        layout.addWidget(self.amount_input)
        layout.addWidget(self.error_label)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def auto_predict_category(self, text):
        if len(text.strip()) > 2:
            predicted = str(ai_engine.predict_category(text.strip()))
            idx = self.category_combo.findText(predicted)
            if idx != -1:
                self.category_combo.setCurrentIndex(idx)
                self.ai_badge.setText(f"🤖 AI Predicted Category: {predicted}")

    def validate_and_accept(self):
        desc = self.desc_input.text().strip()
        amount_str = self.amount_input.text().strip()

        if desc == "" or amount_str == "":
            self.error_label.setText("Please fill in all fields.")
            return

        try:
            val = float(amount_str)
            if val <= 0:
                self.error_label.setText("Amount must be greater than 0.")
                return
        except:
            self.error_label.setText("Enter a valid numeric amount.")
            return

        self.accept()

    def get_data(self):
        date_str = self.date_input.date().toString("yyyy-MM-dd")
        desc = self.desc_input.text().strip()
        category = self.category_combo.currentText()
        val = float(self.amount_input.text().strip())
        formatted_amount = f"+${val:.2f}" if category == "Income" else f"-${val:.2f}"
        return date_str, desc, category, formatted_amount, val


class home(QWidget):
    open_report_signal = pyqtSignal()
    open_calculator_signal = pyqtSignal()
    logout_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_manager = UserDataManager()
        
        self.username = "Student"
        self.hourly_wage = 26.44
        self.hours_per_shift = 6.0
        self.work_days = []
        self.total_budget = 0.0
        self.emergency_vault = 300.00
        self.selected_country = "India 🇮🇳"
        self.profile_pic_path = ""
        self.password = ""
        self.fortnight_start_date = QDate.currentDate()
        self.transactions_data = []
        self.history_data = []

        self.init_ui()

    def set_username(self, username):
        self.username = username
        all_accounts = self.data_manager.load_data()
        
        if self.username in all_accounts:
            user_info = all_accounts[self.username]
            self.hourly_wage = user_info.get("hourly_wage", 26.44)
            self.hours_per_shift = user_info.get("hours_per_shift", 6.0)
            self.work_days = user_info.get("work_days", [])
            self.emergency_vault = user_info.get("emergency_vault", 300.00)
            self.selected_country = user_info.get("selected_country", "India 🇮🇳")
            self.profile_pic_path = user_info.get("profile_pic", "")
            self.password = user_info.get("password", "")
            self.transactions_data = user_info.get("transactions", [])
            self.history_data = user_info.get("history", [])
        else:
            self.hourly_wage = 26.44
            self.hours_per_shift = 6.0
            self.work_days = []
            self.emergency_vault = 300.00
            self.selected_country = "India 🇮🇳"
            self.profile_pic_path = ""
            self.password = ""
            self.transactions_data = []
            self.history_data = []

        self.welcome_label.setText(f"Welcome back, {self.username}! 👋")
        
        idx = self.sidebar_country_combo.findText(self.selected_country)
        if idx != -1:
            self.sidebar_country_combo.setCurrentIndex(idx)
        self.btn_currency_ref.setText(f"🔀 AUD Converter ({self.selected_country})")

        self.update_avatar_display()
        self.populate_table()
        self.recalculate_totals()

    def save_state(self):
        all_accounts = self.data_manager.load_data()
        all_accounts[self.username] = {
            "username": self.username,
            "password": self.password,
            "hourly_wage": self.hourly_wage,
            "hours_per_shift": self.hours_per_shift,
            "emergency_vault": self.emergency_vault,
            "selected_country": self.selected_country,
            "profile_pic": self.profile_pic_path,
            "work_days": self.work_days,
            "transactions": self.transactions_data,
            "history": self.history_data
        }
        self.data_manager.save_data(all_accounts)

    def init_ui(self):
        self.setObjectName("HomeMainWidget")
        self.setStyleSheet("QWidget#HomeMainWidget { background-color: #0F172A; }")

        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(15, 15, 15, 15)
        root_layout.setSpacing(15)

        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("""
            QFrame { background-color: #1E293B; border-radius: 12px; border: 1px solid #334155; }
            QLabel { color: #F8FAFC; }
            QPushButton {
                background-color: #0F172A;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 6px;
                text-align: left;
                padding-left: 12px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #2563EB; border-color: #2563EB; }
        """)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)

        sb_title = QLabel("⚙️ Settings & Tools")
        sb_title.setFont(QFont("Segoe UI", 12, QFont.Bold))

        btn_reports = QPushButton("📊 Financial Reports")
        btn_reports.setFixedHeight(36)
        btn_reports.clicked.connect(self.open_report_signal.emit)

        btn_calc = QPushButton("🧮 Calculator")
        btn_calc.setFixedHeight(36)
        btn_calc.clicked.connect(self.open_calculator_signal.emit)

        btn_calendar = QPushButton("📅 Work Calendar")
        btn_calendar.setFixedHeight(36)
        btn_calendar.clicked.connect(self.open_work_calendar_dialog)

        btn_vault = QPushButton("🛡️ Emergency Vault")
        btn_vault.setFixedHeight(36)
        btn_vault.clicked.connect(self.open_emergency_vault_dialog)

        btn_set_wage = QPushButton("💵 Set Wage & Shift")
        btn_set_wage.setFixedHeight(36)
        btn_set_wage.clicked.connect(self.open_set_wage_dialog)

        btn_upgrade = QPushButton("⭐ Upgrade")
        btn_upgrade.setFixedHeight(36)
        btn_upgrade.setStyleSheet("""
            QPushButton {
                background-color: #D97706;
                color: white;
                border: 1px solid #F59E0B;
                border-radius: 6px;
                text-align: left;
                padding-left: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B45309;
                border-color: #F59E0B;
            }
        """)
        btn_upgrade.clicked.connect(self.open_upgrade_dialog)

        btn_reset_fn = QPushButton("🔄 Reset Fortnight")
        btn_reset_fn.setFixedHeight(36)
        btn_reset_fn.clicked.connect(self.trigger_fortnight_reset)

        country_label = QLabel("Origin Country:")
        country_label.setFont(QFont("Segoe UI", 9))

        self.sidebar_country_combo = QComboBox()
        country_keys = list(COUNTRY_DATA.keys())
        self.sidebar_country_combo.addItems(country_keys)
        self.sidebar_country_combo.setCurrentText(self.selected_country)
        self.sidebar_country_combo.setFixedHeight(32)
        self.sidebar_country_combo.setStyleSheet("background-color: #0F172A; color: #F8FAFC; border: 1px solid #334155; border-radius: 6px; padding: 4px;")
        self.sidebar_country_combo.currentTextChanged.connect(self.on_country_changed)

        sidebar_layout.addWidget(sb_title)
        sidebar_layout.addWidget(btn_reports)
        sidebar_layout.addWidget(btn_calc)
        sidebar_layout.addWidget(btn_calendar)
        sidebar_layout.addWidget(btn_vault)
        sidebar_layout.addWidget(btn_set_wage)
        sidebar_layout.addWidget(btn_upgrade)
        sidebar_layout.addWidget(btn_reset_fn)
        sidebar_layout.addWidget(country_label)
        sidebar_layout.addWidget(self.sidebar_country_combo)
        sidebar_layout.addStretch()

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #0F172A;")

        main_layout = QVBoxLayout(self.content_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        header_bar = QHBoxLayout()
        welcome_card = QFrame()
        welcome_card.setFixedHeight(75)
        welcome_card.setStyleSheet("background-color: rgba(30, 41, 59, 0.7); border: 1px solid rgba(51, 65, 85, 0.8); border-radius: 12px;")

        welcome_layout = QHBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(15, 8, 15, 8)
        welcome_layout.setSpacing(12)

        self.logo_label = QLabel()
        self.logo_label.setFixedSize(45, 45)
        self.logo_label.setStyleSheet("background: transparent; border: none;")
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "BudgetWise_AI_logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(45, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pix)

        text_container = QVBoxLayout()
        text_container.setSpacing(2)

        self.welcome_label = QLabel(f"Welcome back, {self.username}! 👋")
        self.welcome_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.welcome_label.setStyleSheet("color: #F8FAFC; background: transparent; border: none;")

        self.sub_label = QLabel("Fortnightly Cycle Active")
        self.sub_label.setFont(QFont("Segoe UI", 9))
        self.sub_label.setStyleSheet("color: #94A3B8; background: transparent; border: none;")

        text_container.addWidget(self.welcome_label)
        text_container.addWidget(self.sub_label)

        self.avatar_btn = QPushButton("👤")
        self.avatar_btn.setFixedSize(42, 42)
        self.avatar_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #F8FAFC;
                border: 2px solid #64748B;
                border-radius: 21px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #2563EB;
                border-color: #60A5FA;
            }
        """)
        self.avatar_btn.clicked.connect(self.show_user_menu)

        welcome_layout.addWidget(self.logo_label)
        welcome_layout.addLayout(text_container, 1)
        welcome_layout.addWidget(self.avatar_btn)
        header_bar.addWidget(welcome_card, 1)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        self.budget_box, self.lbl_budget_val, self.lbl_budget_sub = self.create_metric_card(
            "Accrued Budget", f"${self.total_budget:.2f}",
            f"{len(self.work_days)} days worked @ ${self.hourly_wage:.2f}/hr",
            "rgba(59, 130, 246, 0.4)", "#60A5FA"
        )
        self.expenses_box, self.lbl_expenses_val, self.lbl_expenses_sub = self.create_metric_card(
            "Fortnight Expenses", "$0.00", "0.0% of Budget",
            "rgba(239, 68, 68, 0.4)", "#F87171"
        )
        self.savings_box, self.lbl_savings_val, self.lbl_savings_sub = self.create_metric_card(
            "Remaining Balance", f"${self.total_budget:.2f}", "100.0% Remaining",
            "rgba(34, 197, 94, 0.4)", "#4ADE80"
        )

        cards_layout.addWidget(self.budget_box)
        cards_layout.addWidget(self.expenses_box)
        cards_layout.addWidget(self.savings_box)

        tools_frame = QFrame()
        tools_frame.setFixedHeight(50)
        tools_layout = QHBoxLayout(tools_frame)
        tools_layout.setContentsMargins(15, 5, 15, 5)

        tools_title = QLabel("🇦🇺 Student Tools:")
        tools_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        tools_title.setStyleSheet("color: #F8FAFC;")

        btn_currency = QPushButton(f"🔀 AUD Converter ({self.selected_country})")
        self.btn_currency_ref = btn_currency
        btn_currency.setStyleSheet("background-color: #0F172A; color: #F8FAFC; border: 1px solid #334155; border-radius: 6px; padding: 6px 12px; font-weight: 600;")
        btn_currency.clicked.connect(self.open_currency_converter)

        btn_visa = QPushButton("⏱️ 48-Hr Work Tracker")
        btn_visa.setStyleSheet("background-color: #0F172A; color: #F8FAFC; border: 1px solid #334155; border-radius: 6px; padding: 6px 12px; font-weight: 600;")
        btn_visa.clicked.connect(self.open_visa_tracker)

        tools_layout.addWidget(tools_title)
        tools_layout.addWidget(btn_currency)
        tools_layout.addWidget(btn_visa)
        tools_layout.addStretch()

        table_container = QFrame()
        container_layout = QVBoxLayout(table_container)
        container_layout.setContentsMargins(15, 12, 15, 15)

        t_header_layout = QHBoxLayout()
        tbl_title = QLabel("💳 Fortnight Transactions")
        tbl_title.setFont(QFont("Segoe UI", 12, QFont.Bold))

        self.add_btn = QPushButton("+ Add Transaction")
        self.add_btn.setFixedHeight(34)
        self.add_btn.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border-radius: 6px; border: none; padding: 0 14px;")
        self.add_btn.clicked.connect(self.open_add_transaction_dialog)

        t_header_layout.addWidget(tbl_title)
        t_header_layout.addStretch()
        t_header_layout.addWidget(self.add_btn)

        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(4)
        self.transactions_table.setHorizontalHeaderLabels(["Date", "Description", "Category", "Amount"])

        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.transactions_table.verticalHeader().setVisible(False)

        container_layout.addLayout(t_header_layout)
        container_layout.addWidget(self.transactions_table)

        main_layout.addLayout(header_bar)
        main_layout.addLayout(cards_layout)
        main_layout.addWidget(tools_frame)
        main_layout.addWidget(table_container, 1)

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.content_widget, 1)

        self.setLayout(root_layout)
        ThemeManager.apply_dark_theme(self)

    def update_avatar_display(self):
        if self.profile_pic_path and os.path.exists(self.profile_pic_path):
            self.avatar_btn.setText("")
            pixmap = QPixmap(self.profile_pic_path)
            self.avatar_btn.setIcon(QIcon(pixmap))
            self.avatar_btn.setIconSize(QSize(36, 36))
        else:
            self.avatar_btn.setIcon(QIcon())
            self.avatar_btn.setText("👤")

    def show_user_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 600;
            }
            QMenu::item:selected {
                background-color: #2563EB;
                color: white;
            }
        """)

        action_change_pfp = menu.addAction("📷 Change Profile Picture")
        action_change_pass = menu.addAction("🔑 Change Password")
        menu.addSeparator()
        action_logout = menu.addAction("🚪 Logout")

        selected_action = menu.exec_(self.avatar_btn.mapToGlobal(self.avatar_btn.rect().bottomLeft()))

        if selected_action == action_change_pfp:
            self.change_profile_picture()
        elif selected_action == action_change_pass:
            self.change_password()
        elif selected_action == action_logout:
            self.logout()

    def change_profile_picture(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Profile Picture", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.profile_pic_path = file_path
            self.update_avatar_display()
            self.save_state()

    def change_password(self):
        new_pass, ok = QInputDialog.getText(
            self, "Change Password", "Enter your new password:", QLineEdit.Password
        )
        if ok and new_pass.strip():
            self.password = new_pass.strip()
            self.save_state()
            QMessageBox.information(self, "Success", "Password updated successfully!")

    def logout(self):
        box = QMessageBox.question(
            self, "Logout", "Are you sure you want to log out?",
            QMessageBox.Yes | QMessageBox.No
        )
        if box == QMessageBox.Yes:
            self.save_state()
            self.logout_signal.emit()

    def create_metric_card(self, title, amount, subtitle, border_color, text_color):
        card = QFrame()
        card.setFixedHeight(125)
        card.setStyleSheet(f"background-color: rgba(30, 41, 59, 0.7); border: 1px solid {border_color}; border-radius: 12px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_title.setStyleSheet("color: #94A3B8; background: transparent; border: none;")

        lbl_amount = QLabel(amount)
        lbl_amount.setFont(QFont("Segoe UI", 22, QFont.Bold))
        lbl_amount.setStyleSheet(f"color: {text_color}; background: transparent; border: none;")

        lbl_sub = QLabel(subtitle)
        lbl_sub.setFont(QFont("Segoe UI", 8))
        lbl_sub.setStyleSheet("color: #64748B; background: transparent; border: none;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_amount)
        layout.addWidget(lbl_sub)
        return card, lbl_amount, lbl_sub

    def populate_table(self):
        self.transactions_table.setRowCount(len(self.transactions_data))
        for row_idx, item in enumerate(self.transactions_data):
            date_item = QTableWidgetItem(item[0])
            desc_item = QTableWidgetItem(item[1])
            cat_item = QTableWidgetItem(item[2])
            amount_item = QTableWidgetItem(item[3])

            amount_item.setForeground(QColor("#22C55E") if item[2] == "Income" else QColor("#EF4444"))
            self.transactions_table.setItem(row_idx, 0, date_item)
            self.transactions_table.setItem(row_idx, 1, desc_item)
            self.transactions_table.setItem(row_idx, 2, cat_item)
            self.transactions_table.setItem(row_idx, 3, amount_item)

    def recalculate_totals(self):
        total_expenses = sum(item[4] for item in self.transactions_data if item[2] != "Income")
        total_income = sum(item[4] for item in self.transactions_data if item[2] == "Income")

        self.total_budget = len(self.work_days) * self.hours_per_shift * self.hourly_wage
        effective_budget = self.total_budget + total_income
        total_savings = effective_budget - total_expenses

        expense_pct = (total_expenses / effective_budget * 100) if effective_budget > 0 else 0.0
        savings_pct = (total_savings / effective_budget * 100) if effective_budget > 0 else 0.0

        self.lbl_budget_val.setText(f"${effective_budget:,.2f}")
        self.lbl_budget_sub.setText(f"{len(self.work_days)} days worked @ ${self.hourly_wage:.2f}/hr")
        self.lbl_expenses_val.setText(f"${total_expenses:,.2f}")
        self.lbl_expenses_sub.setText(f"{expense_pct:.1f}% of Budget")
        self.lbl_savings_val.setText(f"${total_savings:,.2f}")
        self.lbl_savings_sub.setText(f"{savings_pct:.1f}% Remaining")

    def run_ai_safespend_check(self, proposed_amount):
        today = QDate.currentDate()
        t_current = max(min(self.fortnight_start_date.daysTo(today), 14), 1)
        t_target = 14.0

        daily_expenses_map = {}
        for item in self.transactions_data:
            if item[2] != "Income":
                tx_date = QDate.fromString(item[0], "yyyy-MM-dd")
                day_idx = max(self.fortnight_start_date.daysTo(tx_date), 1)
                daily_expenses_map[day_idx] = daily_expenses_map.get(day_idx, 0.0) + item[4]

        daily_samples = [daily_expenses_map.get(d, 0.0) for d in range(1, t_current + 1)]
        v_ewma = calculate_ewma(daily_samples, alpha=0.35)

        e_current = sum(item[4] for item in self.transactions_data if item[2] != "Income") + proposed_amount
        time_remaining = t_target - t_current
        e_projected = e_current + (v_ewma * time_remaining)

        if e_projected > self.total_budget:
            deficit = e_projected - self.total_budget
            safe_daily_limit = max((self.total_budget - e_current) / max(time_remaining, 1), 0.0)
            
            warning_msg = (
                f"⚠️ Overspending Alert!\n\n"
                f"• Average Daily Pace: ${v_ewma:.2f}/day\n"
                f"• Estimated Total Fortnight Spend: ${e_projected:.2f}\n"
                f"• Projected Shortfall: ${deficit:.2f}\n\n"
                f"Suggested Daily Spend Limit: ${safe_daily_limit:.2f}/day"
            )
            return False, warning_msg

        return True, ""

    def open_add_transaction_dialog(self):
        dialog = AddTransactionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_entry = dialog.get_data()
            if new_entry is None:
                return

            cat = new_entry[2]
            val = new_entry[4]

            if cat != "Income":
                safe, warning_msg = self.run_ai_safespend_check(val)
                if not safe:
                    box = QMessageBox.warning(
                        self, 
                        "Smart Budget Alert", 
                        f"{warning_msg}\n\nDo you still want to log this expense?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if box == QMessageBox.No:
                        return

            self.transactions_data.insert(0, new_entry)
            self.populate_table()
            self.recalculate_totals()
            self.save_state()

    def open_work_calendar_dialog(self):
        dlg = WorkCalendarDialog(self.work_days, self)
        if dlg.exec_() == QDialog.Accepted:
            self.work_days = dlg.get_work_days()
            self.recalculate_totals()
            self.save_state()

    def open_emergency_vault_dialog(self):
        total_expenses = sum(item[4] for item in self.transactions_data if item[2] != "Income")
        total_income = sum(item[4] for item in self.transactions_data if item[2] == "Income")
        rem_savings = (self.total_budget + total_income) - total_expenses

        dlg = EmergencyFundDialog(self.emergency_vault, rem_savings, self)
        if dlg.exec_() == QDialog.Accepted:
            self.emergency_vault = dlg.get_fund()
            self.save_state()

    def open_set_wage_dialog(self):
        dlg = SetWageDialog(self.hourly_wage, self.hours_per_shift, self)
        if dlg.exec_() == QDialog.Accepted:
            self.hourly_wage, self.hours_per_shift = dlg.get_details()
            self.recalculate_totals()
            self.save_state()

    def open_upgrade_dialog(self):
        webbrowser.open("https://budgetwizardai.netlify.app/")

    def open_currency_converter(self):
        dlg = CurrencyConverterDialog(self.selected_country, self)
        dlg.exec_()

    def open_visa_tracker(self):
        dlg = VisaWorkTrackerDialog(self.hourly_wage, len(self.work_days) * self.hours_per_shift, self)
        if dlg.exec_() == QDialog.Accepted:
            self.save_state()

    def on_country_changed(self, text):
        self.selected_country = text
        self.btn_currency_ref.setText(f"🔀 AUD Converter ({self.selected_country})")
        self.save_state()

    def trigger_fortnight_reset(self):
        self.transactions_data = []
        self.work_days = []
        self.fortnight_start_date = QDate.currentDate()
        self.populate_table()
        self.recalculate_totals()
        self.save_state()

    def get_report_data(self):
        all_transactions = self.history_data + self.transactions_data
        return self.total_budget, all_transactions