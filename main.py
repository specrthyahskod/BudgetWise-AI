import os
import sys
import re
import numpy as np
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QStackedWidget, QTextEdit, QLineEdit, QPushButton, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QBrush, QPalette, QColor, QIcon

from pages.login import Login
from pages.home import home
from pages.remember_pass import remember_pass
from pages.signup import Signup
from pages.reports import FinancialReportPage
from pages.calculator import CalculatorPage


def get_resource_path(relative_path: str) -> str:
    """Resolves asset paths for local development and PyInstaller onefile bundles."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class AffordabilityChatPanel(QWidget):
    def __init__(self, app_reference):
        super().__init__()
        self.app = app_reference
        self.setFixedWidth(400)
        self.setStyleSheet("""
            QWidget {
                background-color: #0F172A;
                color: #F8FAFC;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QTextEdit#ChatTranscript {
                background-color: #090D16;
                border: 1px solid #1E293B;
                border-radius: 12px;
                padding: 12px;
                font-size: 13px;
                color: #F1F5F9;
            }
            QLineEdit#QueryInput {
                background-color: #1E293B;
                border: 1.5px solid #334155;
                border-radius: 20px;
                padding: 10px 16px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QLineEdit#QueryInput:focus {
                border: 1.5px solid #38BDF8;
                background-color: #162032;
            }
            QPushButton#SendBtn {
                background-color: #0284C7;
                color: #FFFFFF;
                font-weight: 600;
                font-size: 13px;
                border: none;
                border-radius: 18px;
                padding: 8px 18px;
            }
            QPushButton#SendBtn:hover {
                background-color: #0369A1;
            }
            QPushButton#CloseBtn {
                background-color: transparent;
                color: #64748B;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 14px;
            }
            QPushButton#CloseBtn:hover {
                color: #F8FAFC;
                background-color: #1E293B;
            }
            QPushButton#SuggestionChip {
                background-color: #1E293B;
                color: #94A3B8;
                font-size: 11px;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 4px 10px;
            }
            QPushButton#SuggestionChip:hover {
                background-color: #334155;
                color: #38BDF8;
                border-color: #38BDF8;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        header = QHBoxLayout()
        icon_lbl = QLabel("💳")
        icon_lbl.setFont(QFont("Segoe UI", 14))
        
        title_box = QVBoxLayout()
        title = QLabel("Affordability Assistant")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: #F8FAFC; margin: 0;")
        
        subtitle = QLabel("6-Month Trailing Macro Curve Engine")
        subtitle.setFont(QFont("Segoe UI", 8))
        subtitle.setStyleSheet("color: #38BDF8; margin: 0;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.hide)

        header.addWidget(icon_lbl)
        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(close_btn)
        main_layout.addLayout(header)

        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(6)
        chips = [
            ("iPad $500", "Can I buy an iPad for $500?"),
            ("Groceries $120", "Groceries for $120"),
            ("MacBook $2400", "MacBook Pro for $2400 AUD"),
        ]
        for label, text in chips:
            chip_btn = QPushButton(label)
            chip_btn.setObjectName("SuggestionChip")
            chip_btn.clicked.connect(lambda _, q=text: self.submit_quick_query(q))
            chips_layout.addWidget(chip_btn)
        main_layout.addLayout(chips_layout)

        self.chat_history = QTextEdit()
        self.chat_history.setObjectName("ChatTranscript")
        self.chat_history.setReadOnly(True)
        self.display_welcome_banner()
        main_layout.addWidget(self.chat_history, 1)

        input_box = QHBoxLayout()
        input_box.setSpacing(8)
        self.input_field = QLineEdit()
        self.input_field.setObjectName("QueryInput")
        self.input_field.setPlaceholderText("Ask e.g. 'Can I buy shoes for $180?'...")
        self.input_field.returnPressed.connect(self.process_query)

        self.send_btn = QPushButton("Check")
        self.send_btn.setObjectName("SendBtn")
        self.send_btn.clicked.connect(self.process_query)

        input_box.addWidget(self.input_field, 1)
        input_box.addWidget(self.send_btn)
        main_layout.addLayout(input_box)

    def display_welcome_banner(self):
        self.chat_history.setHtml("""
        <div style='background-color: #131B2E; border: 1px solid #1E293B; border-radius: 8px; padding: 12px; margin-bottom: 8px;'>
            <div style='color: #38BDF8; font-weight: bold; font-size: 12px; margin-bottom: 4px;'>🤖 System Ready</div>
            <div style='color: #94A3B8; font-size: 11px; line-height: 1.4;'>
                I verify your transactions across a <b>6-month historical window</b> to evaluate liquidity safety:
                <br>&bull; <b>&lt; $2,000 AUD:</b> Evaluated on current week velocity &amp; daily SafeSpend.
                <br>&bull; <b>&ge; $2,000 AUD:</b> Evaluated against multi-week capital baseline reserves.
            </div>
        </div>
        """)

    def submit_quick_query(self, query: str):
        self.input_field.setText(query)
        self.process_query()

    def process_query(self):
        query = self.input_field.text().strip()
        if not query:
            return

        user_bubble = f"""
        <div style='display: flex; justify-content: flex-end; margin: 8px 0;'>
            <div style='background-color: #0284C7; color: #FFFFFF; padding: 8px 14px; border-radius: 14px 14px 2px 14px; font-size: 12px; max-width: 80%;'>
                <b>You:</b> {query}
            </div>
        </div>
        """
        self.chat_history.append(user_bubble)
        self.input_field.clear()

        price_match = re.findall(r"(?:\$|\b)\s*(\d+(?:,\d{3})*(?:\.\d{1,2})?)\s*(?:bucks|aud|dollars|\$|\b)", query, flags=re.IGNORECASE)
        if not price_match:
            price_match = re.findall(r"\b\d+(?:,\d{3})*(?:\.\d{1,2})?\b", query)

        if not price_match:
            error_bubble = """
            <div style='background-color: #26171E; border-left: 3px solid #EF4444; padding: 8px 10px; border-radius: 4px; margin: 6px 0; font-size: 11px; color: #FCA5A5;'>
                ⚠️ <b>Unrecognized Price:</b> Please include an amount in AUD (e.g., <i>$450</i>, <i>500 bucks</i>, or <i>1200 AUD</i>).
            </div>
            """
            self.chat_history.append(error_bubble)
            return

        cost = float(price_match[0].replace(",", ""))

        item_name = query
        stop_words = [
            r"can i buy", r"can i afford", r"analyse my past", r"analyze my past", 
            r"\d+\s*months?", r"expenditure trend", r"and answer", r"bucks", r"aud", 
            r"dollars", r"\$", r"\bfor\b", r"\ban\b", r"\ba\b", r"\bthe\b"
        ]
        for word in stop_words:
            item_name = re.sub(word, "", item_name, flags=re.IGNORECASE)
        item_name = re.sub(r"\b\d+(?:,\d{3})*(?:\.\d+)?\b", "", item_name).strip() or "Requested Item"
        item_name = item_name.strip(" ,.-").capitalize()

        analysis = self.run_affordability_analysis(item_name, cost)

        ai_card = f"""
        <div style='background-color: #131D31; border: 1px solid #1E293B; border-left: 4px solid {analysis['accent_color']}; border-radius: 8px; padding: 12px; margin: 8px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size: 13px; font-weight: bold; color: {analysis['accent_color']};'>{analysis['verdict']}</span>
                <span style='font-size: 10px; color: #64748B;'>{analysis['horizon']}</span>
            </div>
            <div style='font-size: 12px; color: #E2E8F0; margin: 8px 0; line-height: 1.45;'>{analysis['message']}</div>
            
            <div style='background-color: #0A0F1D; border-radius: 6px; padding: 8px; margin-top: 8px;'>
                <table width='100%' style='font-size: 11px; color: #94A3B8;'>
                    <tr>
                        <td width='50%' style='padding: 2px 0;'>⏱ <b>Labor Cost:</b></td>
                        <td width='50%' style='color: #F8FAFC; text-align: right;'><b>{analysis['work_hours']:.1f} hrs</b> of shifts</td>
                    </tr>
                    <tr>
                        <td style='padding: 2px 0;'>📊 <b>6-Mo Avg Burn:</b></td>
                        <td style='color: #F8FAFC; text-align: right;'>${analysis['monthly_avg_burn']:,.2f}/mo</td>
                    </tr>
                    <tr>
                        <td style='padding: 2px 0;'>🛡 <b>{analysis['buffer_label']}:</b></td>
                        <td style='color: {analysis['buffer_color']}; text-align: right;'><b>{analysis['buffer_value']}</b></td>
                    </tr>
                    <tr>
                        <td style='padding: 2px 0;'>💰 <b>Projected Cash:</b></td>
                        <td style='color: #38BDF8; text-align: right;'><b>${analysis['projected_bal']:,.2f} AUD</b></td>
                    </tr>
                </table>
            </div>
        </div>
        """
        self.chat_history.append(ai_card)

    def run_affordability_analysis(self, item_name: str, cost: float):
        raw_budget = 2500.0
        raw_txs = []
        try:
            raw_budget, raw_txs = self.app.home_page.get_report_data()
        except Exception:
            pass

        now = datetime.now()
        records = []

        if isinstance(raw_txs, (list, tuple)):
            for item in raw_txs:
                if isinstance(item, dict):
                    amt = float(item.get("amount", item.get("price", 0.0)))
                    dt = item.get("date", item.get("timestamp", now))
                    if isinstance(dt, str):
                        try:
                            dt = datetime.fromisoformat(dt)
                        except Exception:
                            try:
                                dt = datetime.strptime(dt[:10], "%Y-%m-%d")
                            except Exception:
                                dt = now
                    elif not isinstance(dt, datetime):
                        dt = now
                    records.append({"amount": amt, "date": dt})
        elif raw_txs is not None and hasattr(raw_txs, "to_dict"):
            try:
                dict_rows = raw_txs.to_dict(orient="records")
                if isinstance(dict_rows, list):
                    for row in dict_rows:
                        amt = float(row.get("amount", row.get("price", 0.0)))
                        dt = row.get("date", row.get("timestamp", now))
                        if isinstance(dt, str):
                            try:
                                dt = datetime.fromisoformat(dt)
                            except Exception:
                                try:
                                    dt = datetime.strptime(dt[:10], "%Y-%m-%d")
                                except Exception:
                                    dt = now
                        elif not isinstance(dt, datetime):
                            dt = now
                        records.append({"amount": amt, "date": dt})
            except Exception:
                pass

        six_months_ago = now - timedelta(days=180)
        trailing_6m_records = [r for r in records if r["date"] >= six_months_ago]
        
        total_6m_spend = sum(r["amount"] for r in trailing_6m_records)
        monthly_avg_burn = total_6m_spend / 6.0 if total_6m_spend > 0 else 1250.0
        weekly_avg_burn = monthly_avg_burn / 4.33

        net_hourly_wage = 22.50
        work_hours = cost / net_hourly_wage

        current_balance = 2850.0
        bal_attr = getattr(self.app.home_page, "balance", None)
        if bal_attr is not None:
            try:
                current_balance = float(bal_attr)
            except Exception:
                pass
        
        remaining_balance = current_balance - cost

        if cost < 2000.0:
            start_of_week = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            week_records = [r for r in records if r["date"] >= start_of_week]
            days_left = max(1, 7 - now.weekday())
            daily_safespend = max(0.0, remaining_balance / days_left)

            if current_balance < cost:
                verdict = "CANNOT AFFORD ⛔"
                color = "#EF4444"
                msg = f"<b>{item_name}</b> (${cost:,.2f} AUD) exceeds your total current balance of ${current_balance:,.2f} AUD by ${cost - current_balance:,.2f} AUD."
            elif remaining_balance < (weekly_avg_burn * 0.5):
                verdict = "HIGH RISK ⚠️"
                color = "#EF4444"
                msg = f"Purchasing <b>{item_name}</b> will deplete your liquidity to ${remaining_balance:,.2f} AUD, falling below your 6-month safety threshold (~${weekly_avg_burn * 0.5:,.2f})."
            elif daily_safespend < 30.0:
                verdict = "CAUTION 🟡"
                color = "#F59E0B"
                msg = f"<b>{item_name}</b> is purchasable, but slashes your remaining daily SafeSpend to <b>${daily_safespend:,.2f}/day</b> for the next {days_left} days."
            else:
                verdict = "SAFE TO BUY ✅"
                color = "#10B981"
                msg = f"<b>{item_name}</b> comfortably fits your spending trends. You maintain an ample SafeSpend reserve of <b>${daily_safespend:,.2f}/day</b> through the end of the week."

            return {
                "verdict": verdict,
                "accent_color": color,
                "horizon": "Current Week Micro Curve (< $2k)",
                "message": msg,
                "work_hours": work_hours,
                "monthly_avg_burn": monthly_avg_burn,
                "buffer_label": "Daily SafeSpend",
                "buffer_value": f"${daily_safespend:,.2f}/day",
                "buffer_color": color,
                "projected_bal": remaining_balance
            }

        else:
            capital_reserve_needed = monthly_avg_burn * 1.5
            surplus = remaining_balance - capital_reserve_needed

            if current_balance < cost:
                verdict = "INSUFFICIENT CAPITAL ⛔"
                color = "#EF4444"
                msg = f"Cannot afford <b>{item_name}</b>. Total available capital is ${current_balance:,.2f} AUD (Shortfall: ${cost - current_balance:,.2f} AUD)."
            elif surplus < 0:
                verdict = "STRUCTURAL DEFICIT ⚠️"
                color = "#F59E0B"
                msg = f"Allocating ${cost:,.2f} AUD for <b>{item_name}</b> cuts into your 6-month baseline emergency runway (${capital_reserve_needed:,.2f} AUD). Projected deficit: ${abs(surplus):,.2f} AUD."
            else:
                verdict = "CAPITAL APPROVED ✅"
                color = "#10B981"
                msg = f"Your 6-month spending trends confirm that <b>{item_name}</b> is safe to purchase. You preserve your emergency buffer (${capital_reserve_needed:,.2f} AUD) with a ${surplus:,.2f} surplus."

            return {
                "verdict": verdict,
                "accent_color": color,
                "horizon": "Macro Capital Curve (≥ $2k)",
                "message": msg,
                "work_hours": work_hours,
                "monthly_avg_burn": monthly_avg_burn,
                "buffer_label": "Capital Runway Surplus",
                "buffer_value": f"${surplus:,.2f} AUD",
                "buffer_color": color,
                "projected_bal": remaining_balance
            }
        
class BudgetWiseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.afford_btn = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("BudgetWise AI")
        self.resize(1100, 750)

        logo_path = get_resource_path(os.path.join("assets", "BudgetWise_AI_logo.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.header_container = QWidget()
        header_layout = QVBoxLayout(self.header_container)
        header_layout.setContentsMargins(15, 10, 15, 5)

        self.title = QLabel("💰 BudgetWise AI")
        self.title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: #F8FAFC; background: transparent;")

        self.subtitle = QLabel("Your AI-powered student finance companion")
        self.subtitle.setFont(QFont("Segoe UI", 11))
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setStyleSheet("color: #94A3B8; background: transparent;")

        header_layout.addWidget(self.title)
        header_layout.addWidget(self.subtitle)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")

        self.login_widget = Login()
        self.home_page = home()
        self.reset_page = remember_pass()
        self.signup_page = Signup()
        self.report_page = FinancialReportPage()
        self.calc_page = CalculatorPage()

        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.reset_page)
        self.stacked_widget.addWidget(self.signup_page)
        self.stacked_widget.addWidget(self.report_page)
        self.stacked_widget.addWidget(self.calc_page)

        self.login_widget.login_successful.connect(self.on_login_success)
        self.login_widget.forgot_password_requested.connect(lambda: self.switch_page(2))
        self.login_widget.signup_requested.connect(lambda: self.switch_page(3))
        self.reset_page.back_to_login_requested.connect(lambda: self.switch_page(0))
        self.signup_page.back_to_login_requested.connect(lambda: self.switch_page(0))
        self.signup_page.signup_successful.connect(self.on_login_success)

        self.home_page.open_report_signal.connect(self.show_report_page)
        self.report_page.back_btn.clicked.connect(lambda: self.switch_page(1))

        self.home_page.open_calculator_signal.connect(lambda: self.switch_page(5))
        self.calc_page.back_btn.clicked.connect(lambda: self.switch_page(1))

        self.home_page.logout_signal.connect(self.handle_logout)

        self.footer_container = QWidget()
        footer_layout = QVBoxLayout(self.footer_container)
        footer_layout.setContentsMargins(10, 5, 10, 10)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        copyright_label = QLabel("© 2026 BudgetWise AI. All Rights Reserved to Oak Technologies. High school capstone project.")
        copyright_label.setFont(QFont("Segoe UI", 8))
        copyright_label.setStyleSheet("color: #64748B; font-weight: bold; background: transparent;")

        footer_layout.addWidget(copyright_label)

        self.content_container = QWidget()
        self.content_container.setStyleSheet("background: transparent;")
        self.content_layout = QHBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_layout.addWidget(self.stacked_widget, 1)

        self.affordability_sidebar = AffordabilityChatPanel(self)
        self.affordability_sidebar.hide()
        self.content_layout.addWidget(self.affordability_sidebar)

        self.main_layout.addWidget(self.header_container)
        self.main_layout.addWidget(self.content_container, 1)
        self.main_layout.addWidget(self.footer_container)

        self.setLayout(self.main_layout)
        self.setup_affordability_sidebar_button()
        self.switch_page(0)

    def setup_affordability_sidebar_button(self):
        if not isinstance(self.home_page, QWidget):
            return

        sig = getattr(self.home_page, "open_affordability_signal", None)
        if sig is not None and hasattr(sig, "connect"):
            try:
                sig.disconnect()
            except Exception:
                pass
            sig.connect(self.toggle_affordability_chat)

        if self.afford_btn is not None:
            return

        all_buttons = self.home_page.findChildren(QPushButton)
        for btn in all_buttons:
            text = btn.text().lower()
            if "calc" in text or "upgrade" in text or "report" in text:
                all_layouts = self.home_page.findChildren(QVBoxLayout)
                for layout in all_layouts:
                    if layout.indexOf(btn) != -1:
                        self.afford_btn = QPushButton("Can I Afford This? 💬")
                        self.afford_btn.setFont(btn.font())
                        self.afford_btn.setStyleSheet(btn.styleSheet())
                        self.afford_btn.clicked.connect(self.toggle_affordability_chat)
                        layout.insertWidget(layout.indexOf(btn) + 1, self.afford_btn)
                        return

    def toggle_affordability_chat(self):
        if hasattr(self, "affordability_sidebar"):
            if self.affordability_sidebar.isVisible():
                self.affordability_sidebar.hide()
            else:
                self.affordability_sidebar.show()
                self.affordability_sidebar.input_field.setFocus()

    def apply_window_background(self, is_logged_in):
        palette = self.palette()
        if is_logged_in:
            palette.setColor(QPalette.Window, QColor("#0F172A"))
        else:
            image_path = get_resource_path(os.path.join("assets", "background.png"))
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
            else:
                palette.setColor(QPalette.Window, QColor("#0F172A"))

        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def resizeEvent(self, a0):
        current_idx = self.stacked_widget.currentIndex()
        self.apply_window_background(current_idx in [1, 4, 5])
        super().resizeEvent(a0)

    def switch_page(self, index):
        is_dashboard_view = index in [1, 4, 5]
        if is_dashboard_view:
            self.header_container.hide()
            self.footer_container.hide()
        else:
            self.header_container.show()
            self.footer_container.show()

        self.apply_window_background(is_dashboard_view)
        self.stacked_widget.setCurrentIndex(index)
        if hasattr(self, "affordability_sidebar") and not is_dashboard_view:
            self.affordability_sidebar.hide()

    def on_login_success(self, username):
        self.home_page.set_username(username)
        self.setup_affordability_sidebar_button()
        self.switch_page(1)

    def show_report_page(self):
        self.report_page.set_user_context(self.home_page.username)
        budget, transactions = self.home_page.get_report_data()
        self.report_page.update_report(budget, transactions)
        self.switch_page(4)

    def handle_logout(self):
        if hasattr(self.login_widget, "reset_fields"):
            self.login_widget.reset_fields()
        if hasattr(self, "affordability_sidebar"):
            self.affordability_sidebar.hide()
        self.switch_page(0)


def main():
    app = QApplication(sys.argv)
    
    if len(sys.argv) > 1 and sys.argv[1].lower().endswith(".rcd"):
        try:
            from tools.rcd_complier import RCDViewerWindow
        except ImportError:
            from tools.rcd_complier import RCDViewerWindow
        viewer = RCDViewerWindow(target_filepath=sys.argv[1])
        viewer.show()
        sys.exit(app.exec_())

    window = BudgetWiseApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()