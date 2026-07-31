from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from utils.excel_manager import save_user_to_excel

class Signup(QWidget):
    back_to_login_requested = pyqtSignal()
    signup_successful = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        heading = QLabel("Create Account")
        heading.setFont(QFont("Arial", 20, QFont.Bold))
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet("color: #111827;")

        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Full Name")
        self.fullname_input.setFixedWidth(280)
        self.fullname_input.setFixedHeight(38)
        self.fullname_input.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px;")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        self.email_input.setFixedWidth(280)
        self.email_input.setFixedHeight(38)
        self.email_input.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px;")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(280)
        self.password_input.setFixedHeight(38)
        self.password_input.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px;")

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setFixedWidth(280)
        self.confirm_password_input.setFixedHeight(38)
        self.confirm_password_input.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px;")

        self.register_btn = QPushButton("Register")
        self.register_btn.setFixedWidth(280)
        self.register_btn.setFixedHeight(40)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        self.register_btn.clicked.connect(self.handle_signup)

        self.back_btn = QPushButton("Already have an account? Sign In")
        self.back_btn.setFixedWidth(280)
        self.back_btn.setFlat(True)
        self.back_btn.setStyleSheet("""
            QPushButton {
                color: #2563EB;
                border: none;
                font-size: 12px;
                background: transparent;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.back_btn.clicked.connect(self.back_to_login_requested.emit)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #DC2626; font-weight: bold;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(heading)
        layout.addWidget(self.fullname_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(self.register_btn)
        layout.addWidget(self.back_btn)
        layout.addWidget(self.error_label)

        self.setLayout(layout)

    def handle_signup(self):
        fullname = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        if not fullname or not email or not password or not confirm_password:
            self.error_label.setText("Please fill in all fields.")
            return

        if password != confirm_password:
            self.error_label.setText("Passwords do not match.")
            return

        try:
            save_user_to_excel(fullname, email, password)
            self.error_label.setText("")
            self.signup_successful.emit(fullname)
        except Exception as e:
            self.error_label.setText("Failed to save registration data.")
            print(f"Error saving to Excel: {e}")