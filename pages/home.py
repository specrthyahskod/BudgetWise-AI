from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont

class home(QWidget):
    def __init__(self):
        super().__init__()
        self.username = ""
        self.init_ui()  

    def init_ui(self):
        layout = QVBoxLayout()

        self.welcome_label = QLabel("Welcome!")
        self.welcome_label.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(self.welcome_label)
        self.setLayout(layout)

    def set_username(self, name):
        self.username = name
        self.welcome_label.setText(f" 🏠 Welcome back, {self.username}! 👋")