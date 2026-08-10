from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class remember_pass(QWidget):
    back_to_login_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()  

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        heading = QLabel("Reset Your Password")
        heading.setFont(QFont("Arial", 18, QFont.Bold))
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your new password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(280)
        self.password_input.setFixedHeight(35)

        self.reset_btn = QPushButton("Reset Password")
        self.reset_btn.setFixedWidth(280)
        self.reset_btn.setFixedHeight(38)

        self.back_btn = QPushButton("Back to Login")
        self.back_btn.setFixedWidth(280)
        self.back_btn.setFlat(True)
        self.back_btn.clicked.connect(self.back_to_login_requested.emit)

        layout.addWidget(heading)
        layout.addWidget(self.password_input)
        layout.addWidget(self.reset_btn)
        layout.addWidget(self.back_btn)

        self.setLayout(layout) 