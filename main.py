import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QStackedWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QBrush, QPalette, QColor

from pages.login import Login
from pages.home import home
from pages.remember_pass import remember_pass
from pages.signup import Signup
from pages.reports import FinancialReportPage
from pages.calculator import CalculatorPage


class BudgetWiseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("BudgetWise AI")
        self.resize(1100, 750)

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

        self.footer_container = QWidget()
        footer_layout = QVBoxLayout(self.footer_container)
        footer_layout.setContentsMargins(10, 5, 10, 10)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        copyright_label = QLabel("© 2026 BudgetWise AI. All Rights Reserved.")
        copyright_label.setFont(QFont("Segoe UI", 8))
        copyright_label.setStyleSheet("color: #64748B; font-weight: bold; background: transparent;")

        footer_layout.addWidget(copyright_label)

        self.main_layout.addWidget(self.header_container)
        self.main_layout.addWidget(self.stacked_widget, 1)
        self.main_layout.addWidget(self.footer_container)

        self.setLayout(self.main_layout)
        self.switch_page(0)

    def apply_window_background(self, is_logged_in):
        """Shows background image during login/signup, and dark theme when logged in."""
        palette = self.palette()
        if is_logged_in:
            palette.setColor(QPalette.Window, QColor("#0F172A"))
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(base_dir, "assets", "background.png")
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

    def on_login_success(self, username):
        self.home_page.set_username(username)
        self.switch_page(1)

    def show_report_page(self):
        budget, transactions = self.home_page.get_report_data()
        self.report_page.update_report(budget, transactions)
        self.switch_page(4)


def main():
    app = QApplication(sys.argv)
    window = BudgetWiseApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()