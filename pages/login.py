from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from utils.excel_manager import authenticate_user


class Login(QWidget):
    login_successful = pyqtSignal(str)
    forgot_password_requested = pyqtSignal()
    signup_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        heading = QLabel("Sign In")
        heading.setFont(QFont("Arial", 20, QFont.Bold))
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet("color: #111827;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username or Email")
        self.username_input.setFixedWidth(280)
        self.username_input.setFixedHeight(38)
        self.username_input.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px;")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(280)
        self.password_input.setFixedHeight(38)
        self.password_input.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px;")

        self.forgot_btn = QPushButton("Forgot Password?")
        self.forgot_btn.setFixedWidth(280)
        self.forgot_btn.setFlat(True)
        self.forgot_btn.setStyleSheet("""
            QPushButton {
                color: #2563EB;
                border: none;
                text-align: right;
                font-size: 12px;
                background: transparent;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.forgot_btn.clicked.connect(self.forgot_password_requested.emit)

        self.login_btn = QPushButton("Log In")
        self.login_btn.setFixedWidth(280)
        self.login_btn.setFixedHeight(40)
        self.login_btn.setStyleSheet("""
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
        self.login_btn.clicked.connect(self.handle_login)

        self.signup_btn = QPushButton("Don't have an account? Sign Up")
        self.signup_btn.setFixedWidth(280)
        self.signup_btn.setFlat(True)
        self.signup_btn.setStyleSheet("""
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
        self.signup_btn.clicked.connect(self.signup_requested.emit)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #DC2626; font-weight: bold;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(heading)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.forgot_btn)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.signup_btn)
        layout.addWidget(self.error_label)

        self.setLayout(layout)

    def handle_login(self):
        username_or_email = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username_or_email or not password:
            self.error_label.setText("Please enter both username and password.")
            return
        
        is_valid, response_data = authenticate_user(username_or_email, password)

        if is_valid:
            self.error_label.setText("")
            self.username_input.clear()
            self.password_input.clear()
            self.login_successful.emit(response_data)
        else:
            self.error_label.setText(response_data)