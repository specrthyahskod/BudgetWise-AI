import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QStackedWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QBrush, QPalette, QIcon

from pages.login import Login
from pages.home import home
from pages.remember_pass import remember_pass
from pages.signup import Signup

def get_asset_path(filename):
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'assets', filename)

class BudgetWiseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("BudgetWise AI")
        self.resize(950, 650)

        icon_path = get_asset_path("BudgetWise_AI_logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.apply_global_background()

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 15)
        self.main_layout.setSpacing(10)

        self.title = QLabel("💰 BudgetWise AI")
        self.title.setFont(QFont("Arial", 26, QFont.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: #111827;")

        self.subtitle = QLabel("Your AI-powered student finance companion")
        self.subtitle.setFont(QFont("Arial", 11))
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setStyleSheet("color: #4B5563;")

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")

        self.login_widget = Login()
        self.home_page = home()
        self.reset_page = remember_pass()
        self.signup_page = Signup()

        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.reset_page)
        self.stacked_widget.addWidget(self.signup_page) 

        self.login_widget.login_successful.connect(self.on_login_success)

        self.login_widget.forgot_password_requested.connect(
            lambda: self.stacked_widget.setCurrentIndex(2)
        )

        self.login_widget.signup_requested.connect(
            lambda: self.stacked_widget.setCurrentIndex(3)
        )

        self.reset_page.back_to_login_requested.connect(
            lambda: self.stacked_widget.setCurrentIndex(0)
        )

        self.signup_page.back_to_login_requested.connect(
            lambda: self.stacked_widget.setCurrentIndex(0)
        )

        self.signup_page.signup_successful.connect(self.on_login_success)

        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(3)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        copyright_label = QLabel("© 2026 BudgetWise AI. All Rights Reserved.")
        copyright_label.setFont(QFont("Arial", 9))
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("color: #4B5563; font-weight: bold;")

        legal_label = QLabel("This is an educational project, we'll add some ToS and Privacy n Policy later.")
        legal_label.setFont(QFont("Arial", 8))
        legal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        legal_label.setStyleSheet("color: #6B7280;")

        footer_layout.addWidget(copyright_label)
        footer_layout.addWidget(legal_label)

        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.subtitle)
        self.main_layout.addWidget(self.stacked_widget, 1)
        self.main_layout.addLayout(footer_layout)

        self.setLayout(self.main_layout)

    def apply_global_background(self):
        image_path = get_asset_path("background.png")

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
        else:
            print(f"Warning: Background image not found at {image_path}")

    def resizeEvent(self, a0):
        self.apply_global_background()
        super().resizeEvent(a0)

    def on_login_success(self, username):
        self.home_page.set_username(username)
        self.stacked_widget.setCurrentIndex(1)


def main():
    app = QApplication(sys.argv)

    icon_path = get_asset_path("BudgetWise_AI_logo.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = BudgetWiseApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()