import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPixmap


class FinancialReportPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: #0F172A; color: #F8FAFC;")
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # Top Bar
        top_bar = QHBoxLayout()
        
        title_box = QHBoxLayout()
        title_box.setSpacing(10)

        logo_label = QLabel()
        logo_label.setFixedSize(38, 38)
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "BudgetWise_AI_logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(38, 38, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)

        title = QLabel("Comprehensive Financial Report")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #F8FAFC;")

        title_box.addWidget(logo_label)
        title_box.addWidget(title)

        self.back_btn = QPushButton("← Back to Dashboard")
        self.back_btn.setFixedSize(160, 36)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)

        top_bar.addLayout(title_box)
        top_bar.addStretch()
        top_bar.addWidget(self.back_btn)

        # Cards Layout
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        self.card_allowance, self.lbl_allowance_val = self.create_card("Base Allowance", "$0.00", "#60A5FA")
        self.card_income, self.lbl_income_val = self.create_card("Total Income", "+$0.00", "#4ADE80")
        self.card_spent, self.lbl_spent_val = self.create_card("Total Money Spent", "-$0.00", "#F87171")
        self.card_net, self.lbl_net_val = self.create_card("Net Remaining Balance", "$0.00", "#38BDF8")

        cards_layout.addWidget(self.card_allowance)
        cards_layout.addWidget(self.card_income)
        cards_layout.addWidget(self.card_spent)
        cards_layout.addWidget(self.card_net)

        # Breakdown Container
        breakdown_frame = QFrame()
        breakdown_frame.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 12px;
            }
        """)
        breakdown_layout = QVBoxLayout(breakdown_frame)
        breakdown_layout.setContentsMargins(20, 20, 20, 20)
        breakdown_layout.setSpacing(15)

        section_title = QLabel("Category-wise Spending Breakdown")
        section_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        section_title.setStyleSheet("color: #F8FAFC; border: none;")

        self.category_table = QTableWidget()
        self.category_table.setColumnCount(3)
        self.category_table.setHorizontalHeaderLabels(["Category", "Amount Spent ($)", "% of Total Expenses"])
        self.category_table.setStyleSheet("""
            QTableWidget {
                background-color: #0F172A;
                color: #F8FAFC;
                gridline-color: #334155;
                border: 1px solid #334155;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #1E293B;
                color: #94A3B8;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
        """)
        
        header = self.category_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.category_table.verticalHeader().setVisible(False)

        breakdown_layout.addWidget(section_title)
        breakdown_layout.addWidget(self.category_table)

        main_layout.addLayout(top_bar)
        main_layout.addLayout(cards_layout)
        main_layout.addWidget(breakdown_frame, 1)

        self.setLayout(main_layout)

    def create_card(self, title, default_val, text_color):
        card = QFrame()
        card.setFixedHeight(100)
        card.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl_title.setStyleSheet("color: #94A3B8; border: none; background: transparent;")

        lbl_val = QLabel(default_val)
        lbl_val.setFont(QFont("Segoe UI", 18, QFont.Bold))
        lbl_val.setStyleSheet(f"color: {text_color}; border: none; background: transparent;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_val)
        return card, lbl_val

    def update_report(self, base_allowance, transactions):
        total_income = sum(t[4] for t in transactions if len(t) > 4 and t[2] == "Income")
        total_spent = sum(t[4] for t in transactions if len(t) > 4 and t[2] != "Income")
        net_remaining = (base_allowance + total_income) - total_spent

        self.lbl_allowance_val.setText(f"${base_allowance:,.2f}")
        self.lbl_income_val.setText(f"+${total_income:,.2f}")
        self.lbl_spent_val.setText(f"-${total_spent:,.2f}")
        self.lbl_net_val.setText(f"${net_remaining:,.2f}")

        cat_totals = {}
        for t in transactions:
            if len(t) > 4 and t[2] != "Income":
                cat = t[2]
                amount = t[4]
                cat_totals[cat] = cat_totals.get(cat, 0.0) + amount

        self.category_table.setRowCount(len(cat_totals))
        for row_idx, (cat, amt) in enumerate(cat_totals.items()):
            pct = (amt / total_spent * 100) if total_spent > 0 else 0.0
            
            cat_item = QTableWidgetItem(cat)
            amt_item = QTableWidgetItem(f"${amt:,.2f}")
            pct_item = QTableWidgetItem(f"{pct:.1f}%")

            amt_item.setForeground(QColor("#F87171"))
            
            self.category_table.setItem(row_idx, 0, cat_item)
            self.category_table.setItem(row_idx, 1, amt_item)
            self.category_table.setItem(row_idx, 2, pct_item)