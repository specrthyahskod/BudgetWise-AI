from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class FinancialReportPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.total_budget = 2000.00
        self.transactions = []
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        top_bar = QHBoxLayout()

        self.back_btn = QPushButton("← Back to Dashboard")
        self.back_btn.setFixedHeight(36)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 0 15px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)

        title = QLabel("📊 Comprehensive Financial Report")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #111827;")

        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.back_btn)

        self.report_card = QFrame()
        self.report_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }
        """)

        self.card_layout = QVBoxLayout(self.report_card)
        self.card_layout.setContentsMargins(25, 25, 25, 25)
        self.card_layout.setSpacing(15)

        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.report_card, 1)

        self.setLayout(main_layout)

    def update_report(self, total_budget, transactions):
        self.total_budget = total_budget
        self.transactions = transactions

        for i in reversed(range(self.card_layout.count())):
            widget = self.card_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        total_income = 0.0
        total_expenses = 0.0
        for t in self.transactions:
            if t[2] == "Income":
                total_income = total_income + t[4]
            else:
                total_expenses = total_expenses + t[4]

        net_savings = (self.total_budget + total_income) - total_expenses

        categories = {}
        for t in self.transactions:
            if t[2] != "Income":
                cat = t[2]
                if cat in categories:
                    categories[cat] = categories[cat] + t[4]
                else:
                    categories[cat] = t[4]

        lbl_base = QLabel(f"• Base Monthly Allowance: ${self.total_budget:,.2f}")
        lbl_base.setFont(QFont("Arial", 12))

        lbl_inc = QLabel(f"• Total Income Earned: +${total_income:,.2f}")
        lbl_inc.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_inc.setStyleSheet("color: #16A34A;")

        lbl_exp = QLabel(f"• Total Money Spent: -${total_expenses:,.2f}")
        lbl_exp.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_exp.setStyleSheet("color: #DC2626;")

        lbl_sav = QLabel(f"• Net Remaining Balance: ${net_savings:,.2f}")
        lbl_sav.setFont(QFont("Arial", 14, QFont.Bold))
        lbl_sav.setStyleSheet("color: #111827;")

        lbl_breakdown = QLabel("Category-wise Spending Breakdown:")
        lbl_breakdown.setFont(QFont("Arial", 13, QFont.Bold))
        lbl_breakdown.setStyleSheet("color: #374151; margin-top: 15px;")

        self.card_layout.addWidget(lbl_base)
        self.card_layout.addWidget(lbl_inc)
        self.card_layout.addWidget(lbl_exp)
        self.card_layout.addWidget(lbl_sav)
        self.card_layout.addWidget(lbl_breakdown)

        if len(categories) > 0:
            for cat in categories:
                amt = categories[cat]
                lbl_cat = QLabel(f"  - {cat}: ${amt:,.2f}")
                lbl_cat.setFont(QFont("Arial", 11))
                self.card_layout.addWidget(lbl_cat)
        else:
            lbl_none = QLabel("  - No expense transactions recorded yet.")
            lbl_none.setFont(QFont("Arial", 11))
            lbl_none.setStyleSheet("color: #6B7280;")
            self.card_layout.addWidget(lbl_none)

        self.card_layout.addStretch()