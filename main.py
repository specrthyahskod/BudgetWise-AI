import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QStackedWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QBrush, QPalette

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
        self.resize(1000, 700)

        self.apply_global_background()

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(15, 10, 15, 10)
        self.main_layout.setSpacing(5)

        self.title = QLabel("💰 BudgetWise AI")
        self.title.setFont(QFont("Arial", 24, QFont.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: #111827; background: transparent;")

        self.subtitle = QLabel("Your AI-powered student finance companion")
        self.subtitle.setFont(QFont("Arial", 11))
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setStyleSheet("color: #4B5563; background: transparent;")

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

        self.login_widget.forgot_password_requested.connect(
            lambda: self.switch_page(2)
        )

        self.login_widget.signup_requested.connect(
            lambda: self.switch_page(3)
        )

        self.reset_page.back_to_login_requested.connect(
            lambda: self.switch_page(0)
        )

        self.signup_page.back_to_login_requested.connect(
            lambda: self.switch_page(0)
        )

        self.signup_page.signup_successful.connect(self.on_login_success)

        self.home_page.open_report_signal.connect(self.show_report_page)
        self.report_page.back_btn.clicked.connect(
            lambda: self.switch_page(1)
        )

        self.home_page.open_calculator_signal.connect(
            lambda: self.switch_page(5)
        )
        self.calc_page.back_btn.clicked.connect(
            lambda: self.switch_page(1)
        )

        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(2)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        copyright_label = QLabel("© 2026 BudgetWise AI. All Rights Reserved.")
        copyright_label.setFont(QFont("Arial", 8))
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("color: #4B5563; font-weight: bold; background: transparent;")

        legal_label = QLabel("Privacy Policy  |  Terms of Service  |  Educational Purpose Only  |  Contact Support")
        legal_label.setFont(QFont("Arial", 8))
        legal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        legal_label.setStyleSheet("color: #6B7280; background: transparent;")

        footer_layout.addWidget(copyright_label)
        footer_layout.addWidget(legal_label)

        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.subtitle)
        self.main_layout.addWidget(self.stacked_widget, 1)
        self.main_layout.addLayout(footer_layout)

        self.setLayout(self.main_layout)

    def apply_global_background(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, "assets", "background.png")

        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            palette = self.palette()
            palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
            self.setPalette(palette)
            self.setAutoFillBackground(True)

    def resizeEvent(self, a0):
        self.apply_global_background()
        super().resizeEvent(a0)

    def switch_page(self, index):
        if index in [1, 4, 5]:
            self.title.hide()
            self.subtitle.hide()
        else:
            self.title.show()
            self.subtitle.show()

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