from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QLineEdit, QPushButton, QLabel, QFrame
)
from PyQt5.QtCore import Qt
import re
import pandas as pd
from datetime import datetime, timedelta

class AffordabilityChatPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(360)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1d24;
                color: #e0e6ed;
                font-family: 'Segoe UI', Arial;
            }
            QTextEdit {
                background-color: #121418;
                border: 1px solid #2e3440;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #121418;
                border: 1px solid #3b4252;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)

        now = datetime.now()
        self.history_df = pd.DataFrame([
            {"date": now - timedelta(days=2), "amount": 42.0},
            {"date": now - timedelta(days=5), "amount": 115.0},
            {"date": now - timedelta(days=10), "amount": 310.0},
            {"date": now - timedelta(days=16), "amount": 280.0}
        ])
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Affordability Assistant")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #60a5fa;")
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setStyleSheet("background-color: transparent; font-size: 14px; color: #94a3b8;")
        self.close_btn.clicked.connect(lambda: self.setVisible(False))

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.close_btn)
        layout.addLayout(header)

        # Chat display transcript
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.append(
            "<span style='color: #94a3b8;'>🤖 <b>BudgetWise AI:</b> Ask me if you can afford an item "
            "(e.g., <i>'Can I buy a Sony headset for $350?'</i> or <i>'MacBook for 2400 AUD'</i>).<br>"
            "Items under $2,000 use your <b>current-week curve</b>; items $2,000+ test against your <b>3-week trailing baseline</b>.</span><br>"
        )
        layout.addWidget(self.chat_history)

        # User input 
        input_bar = QHBoxLayout()
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Enter purchase or amount (AUD)...")
        self.query_input.returnPressed.connect(self.process_query)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.process_query)

        input_bar.addWidget(self.query_input)
        input_bar.addWidget(self.send_btn)
        layout.addLayout(input_bar)

    def process_query(self):
        text = self.query_input.text().strip()
        if not text:
            return

        self.chat_history.append(f"<div align='right'><b>You:</b> {text}</div>")
        self.query_input.clear()

        match = re.search(r"(\$?\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?))", text)
        cost = float(match.group(2).replace(",", "")) if match else None

        if not cost:
            self.chat_history.append(
                "<span style='color: #f87171;'>🤖 Could not parse the price. Please specify a dollar figure (e.g., $450).</span><br>"
            )
            return
        
        item_label = re.sub(r"(\$?\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?))", "", text)
        item_label = item_label.replace("Can I buy", "").replace("Can I afford", "").strip() or "Item"

        # affordability_analyzer model check
        from models.affordability_analyser import AffordabilityAnalytics
        engine = AffordabilityAnalytics(current_balance=2850.00, hourly_net_wage=24.00)
        report = engine.evaluate(item_label, cost, self.history_df)

        # Output metadata struc
        verdict_color = "#4ade80" if "✅" in report["verdict"] else ("#facc15" if "⚠️" in report["verdict"] else "#f87171")
        response_html = f"""
        <div style='background-color: #1e2430; border-left: 3px solid {verdict_color}; padding: 8px; margin-top: 5px;'>
            <b style='color: {verdict_color};'>{report['verdict']}</b> 
            <span style='color: #94a3b8; font-size: 11px;'>[{report['horizon']}]</span><br>
            <p style='margin: 4px 0;'>{report['explanation']}</p>
            <hr style='border: 0; border-top: 1px solid #2e3440;'>
            <small style='color: #cbd5e1;'>
            ⏱ <b>Work Cost:</b> {report['work_hours']:.1f} hours of post-tax labor<br>
            📊 {report['detail_metric']}<br>
            💰 <b>Balance After:</b> ${report['projected_balance']:,.2f} AUD
            </small>
        </div><br>
        """
        self.chat_history.append(response_html)