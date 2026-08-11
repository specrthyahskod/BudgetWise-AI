import socket
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class remember_pass(QWidget):
    back_to_login_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        heading = QLabel("Reset Password")
        heading.setFont(QFont("Segoe UI", 20, QFont.Bold))
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet("color: #111827;")

        sub_heading = QLabel("Enter your registered email address to receive a secure 5-minute session link.")
        sub_heading.setFont(QFont("Segoe UI", 10))
        sub_heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_heading.setStyleSheet("color: #4B5563;")
        sub_heading.setWordWrap(True)
        sub_heading.setFixedWidth(280)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Registered Email Address")
        self.email_input.setFixedWidth(280)
        self.email_input.setFixedHeight(38)
        self.email_input.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px; border: 1px solid #D1D5DB;")

        self.send_btn = QPushButton("Send Security Link")
        self.send_btn.setFixedWidth(280)
        self.send_btn.setFixedHeight(40)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        self.send_btn.clicked.connect(self.handle_send_request)

        self.back_btn = QPushButton("← Back to Login")
        self.back_btn.setFixedWidth(280)
        self.back_btn.setFlat(True)
        self.back_btn.setStyleSheet("""
            QPushButton {
                color: #2563EB;
                border: none;
                font-size: 12px;
                background: transparent;
                font-weight: 600;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.back_btn.clicked.connect(self.on_back_clicked)

        self.status_label = QLabel("")
        self.status_label.setFixedWidth(280)
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(heading)
        layout.addWidget(sub_heading)
        layout.addWidget(self.email_input)
        layout.addWidget(self.send_btn)
        layout.addWidget(self.status_label)
        layout.addWidget(self.back_btn)

        self.setLayout(layout)

    def handle_send_request(self):
        email = self.email_input.text().strip()

        if not email or "@" not in email:
            self.status_label.setText("Please enter a valid email address.")
            self.status_label.setStyleSheet("color: #DC2626; font-weight: bold;")
            return

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(3.0)
            client.connect(("127.0.0.1", 9999))

            payload = {
                "action": "REQUEST_IDI_LINK",
                "email": email
            }
            client.send(json.dumps(payload).encode("utf-8"))

            raw_res = client.recv(4096).decode("utf-8")
            response = json.loads(raw_res)
            client.close()

            if response.get("status") == "SUCCESS":
                self.status_label.setText(
                    f"An encrypted 256-bit IDI security link was dispatched to {email}.\nValid for 5 minutes."
                )
                self.status_label.setStyleSheet("color: #16A34A; font-weight: bold;")
                self.email_input.clear()
            else:
                self.status_label.setText(response.get("message", "Request failed."))
                self.status_label.setStyleSheet("color: #DC2626; font-weight: bold;")

        except Exception:
            self.status_label.setText("Intranet Socket IDI Server Offline.")
            self.status_label.setStyleSheet("color: #DC2626; font-weight: bold;")

    def on_back_clicked(self):
        self.email_input.clear()
        self.status_label.setText("")
        self.back_to_login_requested.emit()