import os
import sys
import re
from datetime import datetime
from typing import Any, Optional

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QStackedWidget, QTextEdit, QLineEdit, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QBrush, QPalette, QColor, QIcon

from pages.login import Login
from pages.home import home
from pages.remember_pass import remember_pass
from pages.signup import Signup
from pages.reports import FinancialReportPage
from pages.calculator import CalculatorPage

# Import FinREST SDK if available in local environment, else set to None
try:
    from finrest import FinREST, UserFinancialContext, FinolaResponse
except ImportError:
    FinREST = None
    UserFinancialContext = None
    FinolaResponse = None

try:
    import session_manager
except ImportError:
    session_manager = None


def get_resource_path(relative_path: str) -> str:
    """Resolves asset paths for local development and PyInstaller onefile bundles."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class FinolaInferenceWorker(QThread):
    """Background worker thread executing FinREST requests to keep PyQt5 responsive."""
    response_ready = pyqtSignal(object)
    inference_failed = pyqtSignal(str)

    def __init__(self, endpoint_url: str, message: str, context: Any, user_id: str):
        super().__init__()
        self.endpoint_url = endpoint_url
        self.message = message
        self.context = context
        self.user_id = user_id

    def run(self):
        try:
            if not FinREST:
                raise ImportError("The 'finrest' SDK is not installed. Run 'pip install finrest==0.1.1'.")
            
            client = FinREST(base_url=self.endpoint_url)
            res = client.chat(
                message=self.message,
                user_id=self.user_id,
                context=self.context
            )
            self.response_ready.emit(res)
        except Exception as e:
            self.inference_failed.emit(str(e))


class AffordabilityChatPanel(QWidget):
    def __init__(self, app_reference):
        super().__init__()
        self.app = app_reference
        self.worker = None
        self.setFixedWidth(420)
        self.setStyleSheet("""
            QWidget {
                background-color: #0F172A;
                color: #F8FAFC;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
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
            QPushButton#SendBtn:disabled {
                background-color: #334155;
                color: #64748B;
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

        # Header Bar
        header = QHBoxLayout()
        
        # Avatar (Cute Mascot if exists, robot emoji fallback)
        avatar_path = get_resource_path(os.path.join("assets", "finola_avatar.png"))
        if os.path.exists(avatar_path):
            avatar_lbl = QLabel()
            pixmap = QPixmap(avatar_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            avatar_lbl.setPixmap(pixmap)
            header.addWidget(avatar_lbl)
        else:
            icon_lbl = QLabel("🤖")
            icon_lbl.setFont(QFont("Segoe UI", 16))
            header.addWidget(icon_lbl)
        
        title_box = QVBoxLayout()
        title = QLabel("Finola AI")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: #F8FAFC; margin: 0;")
        
        subtitle = QLabel("Deterministic Policy & Visa Compliance Core")
        subtitle.setFont(QFont("Segoe UI", 8))
        subtitle.setStyleSheet("color: #38BDF8; margin: 0;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.hide)

        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(close_btn)
        main_layout.addLayout(header)

        # Quick Question Suggestion Chips
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(6)
        chips = [
            ("iPad $400", "Can I buy an iPad for $400 AUD?"),
            ("Groceries $120", "Can I spend $120 on groceries?"),
            ("OCR Bug", "Receipt OCR failed to parse my supermarket bill."),
        ]
        for label, text in chips:
            chip_btn = QPushButton(label)
            chip_btn.setObjectName("SuggestionChip")
            chip_btn.clicked.connect(lambda _, q=text: self.submit_quick_query(q))
            chips_layout.addWidget(chip_btn)
        main_layout.addLayout(chips_layout)

        # Transcript Area
        self.chat_history = QTextEdit()
        self.chat_history.setObjectName("ChatTranscript")
        self.chat_history.setReadOnly(True)
        self.display_welcome_banner()
        main_layout.addWidget(self.chat_history, 1)

        # Bottom Input Field
        input_box = QHBoxLayout()
        input_box.setSpacing(8)
        self.input_field = QLineEdit()
        self.input_field.setObjectName("QueryInput")
        self.input_field.setPlaceholderText("Ask Finola e.g. 'Can I buy an iPad for $400?'...")
        self.input_field.returnPressed.connect(self.process_query)

        self.send_btn = QPushButton("Ask")
        self.send_btn.setObjectName("SendBtn")
        self.send_btn.clicked.connect(self.process_query)

        input_box.addWidget(self.input_field, 1)
        input_box.addWidget(self.send_btn)
        main_layout.addLayout(input_box)

    def display_welcome_banner(self):
        self.chat_history.setHtml("""
        <div style='background-color: #131B2E; border: 1px solid #1E293B; border-radius: 8px; padding: 12px; margin-bottom: 8px;'>
            <div style='color: #38BDF8; font-weight: bold; font-size: 12px; margin-bottom: 4px;'>🛡️ Finola Core Active</div>
            <div style='color: #94A3B8; font-size: 11px; line-height: 1.45;'>
                I verify financial transactions against deterministic bounds &amp; student visa limits:
                <br>&bull; <b>Subclass 500 Compliance:</b> Flags purchases that demand excess work shifts (&gt; 48h/fortnight).
                <br>&bull; <b>Liquidity Engine:</b> Validates against your emergency reserve &amp; daily SafeSpend.
                <br>&bull; <b>Auto Triage:</b> Unhandled OCR or database crashes are automatically dispatched to engineering.
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

        # Render user message bubble
        user_bubble = f"""
        <div style='display: flex; justify-content: flex-end; margin: 8px 0;'>
            <div style='background-color: #0284C7; color: #FFFFFF; padding: 8px 14px; border-radius: 14px 14px 2px 14px; font-size: 12px; max-width: 85%;'>
                <b>You:</b> {query}
            </div>
        </div>
        """
        self.chat_history.append(user_bubble)
        self.input_field.clear()

        # Build dynamic context from dashboard state
        current_balance = 1200.0
        bal_attr = getattr(self.app.home_page, "total_budget", None)
        if bal_attr is not None:
            try:
                current_balance = float(bal_attr)
            except Exception:
                pass

        now = datetime.now()
        days_left_in_cycle = max(1, 7 - now.weekday())

        context = UserFinancialContext(
            current_balance=current_balance,
            emergency_vault=500.0,
            hourly_wage=25.0,
            hours_worked_this_fortnight=34.0,
            days_left_in_cycle=days_left_in_cycle
        ) if UserFinancialContext else None

        # Lock UI during inference
        self.send_btn.setEnabled(False)
        self.send_btn.setText("Thinking...")
        self.input_field.setEnabled(False)

        # Launch background worker
        user_id = getattr(self.app.home_page, "username", "Student_User")
        self.worker = FinolaInferenceWorker(
            endpoint_url="http://127.0.0.1:8000",
            message=query,
            context=context,
            user_id=user_id
        )
        self.worker.response_ready.connect(self.handle_finola_response)
        self.worker.inference_failed.connect(self.handle_inference_error)
        self.worker.start()

    def handle_finola_response(self, response):
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Ask")
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

        calc = response.diagnostics.get("calculus") if response.diagnostics else None
        
        # Color coding & badge mapping
        badge_color = "#38BDF8"
        badge_text = "ADVISORY"
        
        if calc:
            verdict = calc.get("verdict", "APPROVED")
            if verdict == "APPROVED":
                badge_color = "#10B981"
                badge_text = "APPROVED ✅"
            elif verdict == "VISA_HOURS_RISK":
                badge_color = "#EF4444"
                badge_text = "VISA WORK CAP RISK ⚠️"
            elif verdict == "CRITICAL_BUFFER_WARNING":
                badge_color = "#F59E0B"
                badge_text = "BUFFER BREACH 🟡"
            elif verdict == "DENIED":
                badge_color = "#EF4444"
                badge_text = "OVERDRAFT REJECTED ⛔"

        # Math telemetry table
        telemetry_html = ""
        if calc:
            telemetry_html = f"""
            <div style='background-color: #0A0F1D; border-radius: 6px; padding: 8px; margin-top: 8px;'>
                <table width='100%' style='font-size: 11px; color: #94A3B8;'>
                    <tr>
                        <td width='50%' style='padding: 2px 0;'>⏱ <b>Shift Requirement:</b></td>
                        <td width='50%' style='color: #F8FAFC; text-align: right;'><b>{calc.get('hours_needed', 0.0):.1f} hrs</b> work</td>
                    </tr>
                    <tr>
                        <td style='padding: 2px 0;'>🛡 <b>Visa Fortnight Left:</b></td>
                        <td style='color: #F8FAFC; text-align: right;'>{calc.get('remaining_visa_hours', 0.0):.1f} / 48 hrs</td>
                    </tr>
                    <tr>
                        <td style='padding: 2px 0;'>💰 <b>Projected Balance:</b></td>
                        <td style='color: #38BDF8; text-align: right;'>${calc.get('post_balance', 0.0):,.2f} AUD</td>
                    </tr>
                    <tr>
                        <td style='padding: 2px 0;'>📅 <b>Daily SafeSpend:</b></td>
                        <td style='color: #F8FAFC; text-align: right;'>${calc.get('daily_safespend', 0.0):,.2f}/day</td>
                    </tr>
                </table>
            </div>
            """

        # System issue badge if Finola caught a bug report
        triage_html = ""
        if response.issue_detected:
            triage_html = """
            <div style='background-color: #2D1515; border: 1px solid #7F1D1D; border-radius: 6px; padding: 6px 10px; margin-top: 6px; font-size: 11px; color: #FCA5A5;'>
                🚨 <b>Incident Logged:</b> Diagnostic report dispatched to the administrator inbox.
            </div>
            """

        ai_card = f"""
        <div style='background-color: #131D31; border: 1px solid #1E293B; border-left: 4px solid {badge_color}; border-radius: 8px; padding: 12px; margin: 8px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size: 12px; font-weight: bold; color: {badge_color};'>{badge_text}</span>
                <span style='font-size: 10px; color: #64748B;'>Finola SLM</span>
            </div>
            <div style='font-size: 12px; color: #E2E8F0; margin: 8px 0; line-height: 1.45;'>{response.reply}</div>
            {telemetry_html}
            {triage_html}
        </div>
        """
        self.chat_history.append(ai_card)

    def handle_inference_error(self, err_msg):
        self.send_btn.setEnabled(True)
        self.send_btn.setText("Ask")
        self.input_field.setEnabled(True)
        
        fallback_bubble = f"""
        <div style='background-color: #26171E; border-left: 3px solid #EF4444; padding: 8px 10px; border-radius: 4px; margin: 6px 0; font-size: 11px; color: #FCA5A5;'>
            ⚠️ <b>FinREST Offline:</b> Could not reach backend at <code>http://127.0.0.1:8000</code>.<br>
            <i>{err_msg}</i>
        </div>
        """
        self.chat_history.append(fallback_bubble)


class BudgetWiseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.afford_btn = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("BudgetWise AI")
        self.resize(1150, 750)

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

        # Attach Finola Sidebar
        self.affordability_sidebar = AffordabilityChatPanel(self)
        self.affordability_sidebar.hide()
        self.content_layout.addWidget(self.affordability_sidebar)

        self.main_layout.addWidget(self.header_container)
        self.main_layout.addWidget(self.content_container, 1)
        self.main_layout.addWidget(self.footer_container)

        self.setLayout(self.main_layout)
        self.setup_affordability_sidebar_button()

        # Session-aware boot router
        has_active_session = False
        if session_manager:
            sess = session_manager.load_session()
            username = sess.get("username", "")
            if sess.get("logged_in") and username:
                has_active_session = True
                self.home_page.set_username(username)
                self.setup_affordability_sidebar_button()
                self.switch_page(1)

        if not has_active_session:
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
                        self.afford_btn = QPushButton("Talk to Finola 💬")
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
        if session_manager:
            session_manager.save_session(username=username, onboarding_completed=True)

        self.home_page.set_username(username)
        self.setup_affordability_sidebar_button()
        self.switch_page(1)

    def show_report_page(self):
        self.report_page.set_user_context(self.home_page.username)
        budget, transactions = self.home_page.get_report_data()
        self.report_page.update_report(budget, transactions)
        self.switch_page(4)

    def handle_logout(self):
        if session_manager:
            session_manager.clear_session()

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