from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QDialog, QLineEdit, QComboBox, QDateEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from utils.manager import ThemeManager

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

class EmergencyFundDialog(QDialog):
    def __init__(self, current_fund, remaining_savings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Emergency Vault Control")
        self.setFixedSize(340, 260)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.current_fund = current_fund
        self.remaining_savings = remaining_savings
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("🛡️ Emergency Fund Vault")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.info_label = QLabel(f"Vault Balance: ${self.current_fund:.2f}\nFortnight Savings: ${self.remaining_savings:.2f}")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter Amount ($)")
        self.amount_input.setFixedHeight(34)

        btn_deposit = QPushButton("Deposit to Vault")
        btn_deposit.setFixedHeight(34)
        btn_deposit.setStyleSheet("background-color: #16A34A; color: white; font-weight: bold;")
        btn_deposit.clicked.connect(self.deposit)

        btn_withdraw = QPushButton("Withdraw Emergency Funds")
        btn_withdraw.setFixedHeight(34)
        btn_withdraw.setStyleSheet("background-color: #DC2626; color: white; font-weight: bold;")
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
            self.current_fund = self.current_fund + val
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
            self.current_fund = self.current_fund - val
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
        self.setStyleSheet("background-color: #FFFFFF;")
        self.selected_country = selected_country
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("🔀 AUD Converter")
        title.setFont(QFont("Arial", 12, QFont.Bold))
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
        self.result_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.result_label.setStyleSheet("color: #2563EB;")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        calc_btn = QPushButton("Convert")
        calc_btn.setFixedHeight(36)
        calc_btn.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border-radius: 6px;")
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
    def __init__(self, hourly_wage, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Australia Visa Work Limits")
        self.setFixedSize(340, 290)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.hourly_wage = hourly_wage
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("⏱️ Visa Work Tracker")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.w1_input = QLineEdit()
        self.w1_input.setPlaceholderText("Week 1 Hours Worked")
        self.w1_input.setFixedHeight(34)

        self.w2_input = QLineEdit()
        self.w2_input.setPlaceholderText("Week 2 Hours Worked")
        self.w2_input.setFixedHeight(34)

        self.status_label = QLabel(f"Limit: 48 hrs / fortnight | Pay: ${self.hourly_wage:.2f}/hr")
        self.status_label.setFont(QFont("Arial", 9, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        check_btn = QPushButton("Check Compliance & Earnings")
        check_btn.setFixedHeight(36)
        check_btn.setStyleSheet("background-color: #16A34A; color: white; font-weight: bold; border-radius: 6px;")
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
        
        if w1_text == "":
            w1 = 0.0
        else:
            w1 = float(w1_text)

        if w2_text == "":
            w2 = 0.0
        else:
            w2 = float(w2_text)

        total = w1 + w2
        earnings = total * self.hourly_wage

        if total > 48:
            self.status_label.setText(f"❌ Visa Breach! {total} hrs (>48 hrs)\nEarned: ${earnings:,.2f}")
            self.status_label.setStyleSheet("color: #DC2626; font-weight: bold;")
        else:
            rem = 48 - total
            self.status_label.setText(f"✅ Compliant! Total: {total} hrs ({rem} hrs left)\nEst. Income: ${earnings:,.2f}")
            self.status_label.setStyleSheet("color: #16A34A; font-weight: bold;")


class SetWageDialog(QDialog):
    def __init__(self, current_wage, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Hourly Wage")
        self.setFixedSize(300, 180)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.init_ui(current_wage)

    def init_ui(self, current_wage):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Input Hourly Wage (AUD)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.wage_input = QLineEdit()
        self.wage_input.setText(str(current_wage))
        self.wage_input.setFixedHeight(36)

        save_btn = QPushButton("Save Wage")
        save_btn.setFixedHeight(34)
        save_btn.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border-radius: 6px;")
        save_btn.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(self.wage_input)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def get_wage(self):
        text_val = self.wage_input.text().strip()
        try:
            return float(text_val)
        except:
            return 26.44


class SetBudgetDialog(QDialog):
    def __init__(self, current_budget, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Fortnightly Budget")
        self.setFixedSize(300, 180)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.init_ui(current_budget)

    def init_ui(self, current_budget):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Set Fortnightly Allowance")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.budget_input = QLineEdit()
        self.budget_input.setPlaceholderText("Enter Total Budget ($)")
        self.budget_input.setText(str(current_budget))
        self.budget_input.setFixedHeight(36)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #DC2626; font-size: 11px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(34)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Budget")
        save_btn.setFixedHeight(34)
        save_btn.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border-radius: 6px;")
        save_btn.clicked.connect(self.validate_and_accept)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)

        layout.addWidget(title)
        layout.addWidget(self.budget_input)
        layout.addWidget(self.error_label)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def validate_and_accept(self):
        val_text = self.budget_input.text().strip()
        try:
            val = float(val_text)
            if val < 0:
                self.error_label.setText("Budget cannot be negative.")
                return
            self.accept()
        except:
            self.error_label.setText("Enter a valid number.")

    def get_budget(self):
        return float(self.budget_input.text().strip())


class AddTransactionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log New Transaction")
        self.setFixedSize(320, 380)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Add Transaction")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setFixedHeight(36)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description (e.g. Coles Groceries)")
        self.desc_input.setFixedHeight(36)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["Food", "Education", "Transport", "Shopping", "Entertainment", "Income"])
        self.category_combo.setFixedHeight(36)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount ($)")
        self.amount_input.setFixedHeight(36)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #DC2626; font-size: 11px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(36)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save")
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border-radius: 6px;")
        save_btn.clicked.connect(self.validate_and_accept)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)

        layout.addWidget(title)
        layout.addWidget(QLabel("Date:"))
        layout.addWidget(self.date_input)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.desc_input)
        layout.addWidget(QLabel("Category:"))
        layout.addWidget(self.category_combo)
        layout.addWidget(QLabel("Amount ($):"))
        layout.addWidget(self.amount_input)
        layout.addWidget(self.error_label)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

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
        
        if category == "Income":
            formatted_amount = f"+${val:.2f}"
        else:
            formatted_amount = f"-${val:.2f}"

        return date_str, desc, category, formatted_amount, val


class home(QWidget):
    open_report_signal = pyqtSignal()
    open_calculator_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.username = "Student"
        self.total_budget = 2000.00
        self.hourly_wage = 26.44
        self.emergency_vault = 300.00
        self.selected_country = "India 🇮🇳"
        
        self.fortnight_start_date = QDate.currentDate()
        self.transactions_data = []
        self.history_data = []

        self.init_ui()

    def init_ui(self):
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: none;
            }
            QLabel {
                color: #F8FAFC;
            }
            QPushButton {
                background-color: #334155;
                color: #F8FAFC;
                border: none;
                border-radius: 6px;
                text-align: left;
                padding-left: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(12)

        sb_title = QLabel("⚙️ Settings & Tools")
        sb_title.setFont(QFont("Arial", 12, QFont.Bold))

        btn_reports = QPushButton("📊 Financial Reports")
        btn_reports.setFixedHeight(36)
        btn_reports.clicked.connect(self.open_report_signal.emit)

        btn_calc = QPushButton("🧮 Calculator")
        btn_calc.setFixedHeight(36)
        btn_calc.clicked.connect(self.open_calculator_signal.emit)

        btn_vault = QPushButton("🛡️ Emergency Vault")
        btn_vault.setFixedHeight(36)
        btn_vault.clicked.connect(self.open_emergency_vault_dialog)

        btn_theme = QPushButton("🌓 Toggle Theme")
        btn_theme.setFixedHeight(36)
        btn_theme.clicked.connect(self.toggle_app_theme)

        btn_set_wage = QPushButton("💵 Set Hourly Wage")
        btn_set_wage.setFixedHeight(36)
        btn_set_wage.clicked.connect(self.open_set_wage_dialog)

        btn_reset_fn = QPushButton("🔄 Reset Fortnight")
        btn_reset_fn.setFixedHeight(36)
        btn_reset_fn.clicked.connect(self.trigger_fortnight_reset)

        country_label = QLabel("Origin Country:")
        country_label.setFont(QFont("Arial", 9))

        self.sidebar_country_combo = QComboBox()
        country_keys = list(COUNTRY_DATA.keys())
        self.sidebar_country_combo.addItems(country_keys)
        self.sidebar_country_combo.setFixedHeight(32)
        self.sidebar_country_combo.setStyleSheet("background-color: #334155; color: white; border-radius: 6px; padding: 4px;")
        self.sidebar_country_combo.currentTextChanged.connect(self.on_country_changed)

        sidebar_layout.addWidget(sb_title)
        sidebar_layout.addWidget(btn_reports)
        sidebar_layout.addWidget(btn_calc)
        sidebar_layout.addWidget(btn_vault)
        sidebar_layout.addWidget(btn_theme)
        sidebar_layout.addWidget(btn_set_wage)
        sidebar_layout.addWidget(btn_reset_fn)
        sidebar_layout.addWidget(country_label)
        sidebar_layout.addWidget(self.sidebar_country_combo)
        sidebar_layout.addStretch()

        self.content_widget = QWidget()
        main_layout = QVBoxLayout(self.content_widget)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(12)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        header_bar = QHBoxLayout()
        
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setFixedSize(36, 36)
        self.menu_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                color: #1E293B;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        self.menu_btn.clicked.connect(self.toggle_sidebar)

        welcome_card = QFrame()
        welcome_card.setFixedHeight(75)
        welcome_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(229, 231, 235, 0.8);
                border-radius: 12px;
            }
        """)

        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(15, 10, 15, 10)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.welcome_label = QLabel(f"Welcome back, {self.username}! 👋")
        self.welcome_label.setFont(QFont("Arial", 16, QFont.Bold))

        self.sub_label = QLabel("Fortnightly Cycle Active")
        self.sub_label.setFont(QFont("Arial", 9))

        welcome_layout.addWidget(self.welcome_label)
        welcome_layout.addWidget(self.sub_label)

        header_bar.addWidget(self.menu_btn)
        header_bar.addWidget(welcome_card, 1)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        self.budget_box, self.lbl_budget_val, self.lbl_budget_sub = self.create_metric_card(
            title="Fortnight Budget",
            amount=f"${self.total_budget:.2f}",
            subtitle="Allowance",
            border_color="#2563EB",
            text_color="#1E40AF"
        )

        self.expenses_box, self.lbl_expenses_val, self.lbl_expenses_sub = self.create_metric_card(
            title="Fortnight Expenses",
            amount="$0.00",
            subtitle="0.0% of Budget",
            border_color="#DC2626",
            text_color="#991B1B"
        )

        self.savings_box, self.lbl_savings_val, self.lbl_savings_sub = self.create_metric_card(
            title="Remaining Balance",
            amount=f"${self.total_budget:.2f}",
            subtitle="100.0% Remaining",
            border_color="#16A34A",
            text_color="#166534"
        )

        cards_layout.addWidget(self.budget_box)
        cards_layout.addWidget(self.expenses_box)
        cards_layout.addWidget(self.savings_box)

        tools_frame = QFrame()
        tools_frame.setFixedHeight(50)
        tools_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 10px;
                border: 1px solid #E5E7EB;
            }
            QPushButton {
                background-color: #F1F5F9;
                color: #0F172A;
                font-weight: bold;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
            }
        """)
        tools_layout = QHBoxLayout(tools_frame)
        tools_layout.setContentsMargins(15, 5, 15, 5)

        tools_title = QLabel("🇦🇺 Student Tools:")
        tools_title.setFont(QFont("Arial", 11, QFont.Bold))

        btn_currency = QPushButton(f"🔀 AUD Converter ({self.selected_country})")
        self.btn_currency_ref = btn_currency
        btn_currency.clicked.connect(self.open_currency_converter)

        btn_visa = QPushButton("⏱️ 48-Hr Work Tracker")
        btn_visa.clicked.connect(self.open_visa_tracker)

        tools_layout.addWidget(tools_title)
        tools_layout.addWidget(btn_currency)
        tools_layout.addWidget(btn_visa)

        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                border: 1px solid rgba(229, 231, 235, 0.8);
            }
        """)

        container_layout = QVBoxLayout(table_container)
        container_layout.setContentsMargins(15, 12, 15, 15)
        container_layout.setSpacing(10)

        t_header_layout = QHBoxLayout()
        tbl_title = QLabel("💳 Fortnight Transactions")
        tbl_title.setFont(QFont("Arial", 13, QFont.Bold))

        self.edit_budget_btn = QPushButton("Set Budget")
        self.edit_budget_btn.setFixedHeight(32)
        self.edit_budget_btn.setStyleSheet("""
            QPushButton {
                background-color: #4B5563;
                color: white;
                font-weight: bold;
                font-size: 11px;
                border-radius: 6px;
                padding: 0 10px;
                border: none;
            }
        """)
        self.edit_budget_btn.clicked.connect(self.open_set_budget_dialog)

        self.add_btn = QPushButton("+ Add Transaction")
        self.add_btn.setFixedHeight(32)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                font-weight: bold;
                font-size: 11px;
                border-radius: 6px;
                padding: 0 12px;
                border: none;
            }
        """)
        self.add_btn.clicked.connect(self.open_add_transaction_dialog)

        t_header_layout.addWidget(tbl_title)
        t_header_layout.addStretch()
        t_header_layout.addWidget(self.edit_budget_btn)
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
        self.transactions_table.setSelectionMode(QTableWidget.NoSelection)

        container_layout.addLayout(t_header_layout)
        container_layout.addWidget(self.transactions_table)

        main_layout.addLayout(header_bar)
        main_layout.addLayout(cards_layout)
        main_layout.addWidget(tools_frame)
        main_layout.addWidget(table_container, 1)

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.content_widget, 1)

        self.setLayout(root_layout)
        self.check_auto_fortnight_reset()
        self.recalculate_totals()

    def toggle_app_theme(self):
        ThemeManager.toggle_theme(self)

    def check_auto_fortnight_reset(self):
        today = QDate.currentDate()
        days_passed = self.fortnight_start_date.daysTo(today)

        if days_passed >= 14:
            self.trigger_fortnight_reset()
        else:
            days_left = 14 - days_passed
            self.sub_label.setText(f"Australia Student Companion | Days left in fortnight: {days_left}")

    def trigger_fortnight_reset(self):
        if len(self.transactions_data) > 0:
            for item in self.transactions_data:
                self.history_data.append(item)

        self.transactions_data = []
        self.fortnight_start_date = QDate.currentDate()
        self.populate_table()
        self.recalculate_totals()
        self.sub_label.setText("Fortnight Cycle Reset! Days remaining in fortnight: 14")

    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.setVisible(False)
        else:
            self.sidebar.setVisible(True)

    def on_country_changed(self, text):
        self.selected_country = text
        self.btn_currency_ref.setText(f"🔀 AUD Converter ({self.selected_country})")

    def create_metric_card(self, title, amount, subtitle, border_color, text_color):
        card = QFrame()
        card.setFixedHeight(120)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.95);
                border-top: 5px solid {border_color};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Arial", 11, QFont.Bold))

        lbl_amount = QLabel(amount)
        lbl_amount.setFont(QFont("Arial", 18, QFont.Bold))
        lbl_amount.setStyleSheet(f"color: {text_color};")

        lbl_sub = QLabel(subtitle)
        lbl_sub.setFont(QFont("Arial", 9))

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_amount)
        layout.addWidget(lbl_sub)

        return card, lbl_amount, lbl_sub

    def populate_table(self):
        self.transactions_table.setRowCount(len(self.transactions_data))
        for row_idx, item in enumerate(self.transactions_data):
            date_str = item[0]
            desc = item[1]
            cat = item[2]
            formatted_amount = item[3]

            date_item = QTableWidgetItem(date_str)
            desc_item = QTableWidgetItem(desc)
            cat_item = QTableWidgetItem(cat)
            amount_item = QTableWidgetItem(formatted_amount)

            date_item.setTextAlignment(int(Qt.AlignCenter))
            cat_item.setTextAlignment(int(Qt.AlignCenter))
            amount_item.setTextAlignment(int(Qt.AlignRight | Qt.AlignVCenter))

            if cat == "Income":
                amount_item.setForeground(QColor("#16A34A"))
            else:
                amount_item.setForeground(QColor("#DC2626"))

            self.transactions_table.setItem(row_idx, 0, date_item)
            self.transactions_table.setItem(row_idx, 1, desc_item)
            self.transactions_table.setItem(row_idx, 2, cat_item)
            self.transactions_table.setItem(row_idx, 3, amount_item)

    def recalculate_totals(self):
        total_expenses = 0.0
        total_income = 0.0

        for item in self.transactions_data:
            cat = item[2]
            val = item[4]
            if cat == "Income":
                total_income = total_income + val
            else:
                total_expenses = total_expenses + val

        effective_budget = self.total_budget + total_income
        total_savings = effective_budget - total_expenses

        if effective_budget > 0:
            expense_pct = (total_expenses / effective_budget) * 100
            savings_pct = (total_savings / effective_budget) * 100
        else:
            expense_pct = 0.0
            savings_pct = 0.0

        self.lbl_budget_val.setText(f"${effective_budget:,.2f}")
        self.lbl_expenses_val.setText(f"${total_expenses:,.2f}")
        self.lbl_expenses_sub.setText(f"{expense_pct:.1f}% of Budget")

        self.lbl_savings_val.setText(f"${total_savings:,.2f}")
        self.lbl_savings_sub.setText(f"{savings_pct:.1f}% Remaining")

    def run_ai_safespend_check(self, expense_val):
        total_expenses = 0.0
        for item in self.transactions_data:
            if item[2] != "Income":
                total_expenses = total_expenses + item[4]

        remaining_savings = self.total_budget - total_expenses

        if remaining_savings <= 0:
            return False, "You have exhausted your budget! Logging this expense will put you in debt."

        limit_threshold = remaining_savings * 0.40
        if expense_val > limit_threshold:
            return False, f"⚠️ AI Warning: This spend (${expense_val:.2f}) consumes over 40% of your remaining savings (${remaining_savings:.2f})."

        return True, ""

    def open_emergency_vault_dialog(self):
        total_expenses = sum(item[4] for item in self.transactions_data if item[2] != "Income")
        total_income = sum(item[4] for item in self.transactions_data if item[2] == "Income")
        rem_savings = (self.total_budget + total_income) - total_expenses

        dlg = EmergencyFundDialog(self.emergency_vault, rem_savings, self)
        if dlg.exec_() == QDialog.Accepted:
            self.emergency_vault = dlg.get_fund()

    def open_add_transaction_dialog(self):
        dialog = AddTransactionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_entry = dialog.get_data()
            cat = new_entry[2]
            val = new_entry[4]

            if cat != "Income":
                safe, warning_msg = self.run_ai_safespend_check(val)
                if not safe:
                    box = QMessageBox.warning(
                        self, 
                        "🤖 AI SafeSpend Warning", 
                        f"{warning_msg}\n\nDo you still want to log this expense?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if box == QMessageBox.No:
                        return

            self.transactions_data.insert(0, new_entry)
            self.populate_table()
            self.recalculate_totals()

    def open_set_budget_dialog(self):
        dialog = SetBudgetDialog(self.total_budget, self)
        if dialog.exec_() == QDialog.Accepted:
            self.total_budget = dialog.get_budget()
            self.recalculate_totals()

    def open_set_wage_dialog(self):
        dlg = SetWageDialog(self.hourly_wage, self)
        if dlg.exec_() == QDialog.Accepted:
            self.hourly_wage = dlg.get_wage()

    def open_currency_converter(self):
        dlg = CurrencyConverterDialog(self.selected_country, self)
        dlg.exec_()

    def open_visa_tracker(self):
        dlg = VisaWorkTrackerDialog(self.hourly_wage, self)
        dlg.exec_()

    def get_report_data(self):
        all_transactions = self.history_data + self.transactions_data
        return self.total_budget, all_transactions

    def set_username(self, username):
        self.username = username
        self.welcome_label.setText(f"Welcome back, {self.username}! 👋")