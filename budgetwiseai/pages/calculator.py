from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class CalculatorPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.expression = ""
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        top_bar = QHBoxLayout()

        title = QLabel("🧮 Student Financial Calculator")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #111827;")

        self.back_btn = QPushButton("← Back to Dashboard")
        self.back_btn.setFixedHeight(36)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 0 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)

        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.back_btn)

        calc_container = QFrame()
        calc_container.setFixedWidth(340)
        calc_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }
        """)

        calc_layout = QVBoxLayout(calc_container)
        calc_layout.setContentsMargins(20, 20, 20, 20)
        calc_layout.setSpacing(15)

        self.display = QLabel("0")
        self.display.setFixedHeight(50)
        self.display.setFont(QFont("Arial", 20, QFont.Bold))
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.display.setStyleSheet("""
            background-color: #F8FAFC;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            padding: 8px;
            color: #0F172A;
        """)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        buttons = [
            ("C", 0, 0), ("(", 0, 1), (")", 0, 2), ("/", 0, 3),
            ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("*", 1, 3),
            ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("-", 2, 3),
            ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("+", 3, 3),
            ("0", 4, 0), (".", 4, 1), ("=", 4, 2)
        ]

        for text, row, col in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(60, 50)
            btn.setFont(QFont("Arial", 12, QFont.Bold))

            if text in ["/", "*", "-", "+", "="]:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2563EB;
                        color: white;
                        border-radius: 8px;
                        border: none;
                    }
                    QPushButton:hover { background-color: #1D4ED8; }
                """)
            elif text == "C":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #DC2626;
                        color: white;
                        border-radius: 8px;
                        border: none;
                    }
                    QPushButton:hover { background-color: #B91C1C; }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #F1F5F9;
                        color: #0F172A;
                        border-radius: 8px;
                        border: 1px solid #CBD5E1;
                    }
                    QPushButton:hover { background-color: #E2E8F0; }
                """)

            btn.clicked.connect(lambda _, t=text: self.on_button_click(t))

            if text == "=":
                grid_layout.addWidget(btn, row, col, 1, 2)
                btn.setFixedWidth(130)
            else:
                grid_layout.addWidget(btn, row, col)

        calc_layout.addWidget(self.display)
        calc_layout.addLayout(grid_layout)

        center_wrapper = QHBoxLayout()
        center_wrapper.addStretch()
        center_wrapper.addWidget(calc_container)
        center_wrapper.addStretch()

        main_layout.addLayout(top_bar)
        main_layout.addLayout(center_wrapper)

        self.setLayout(main_layout)

    def on_button_click(self, char):
        if char == "C":
            self.expression = ""
            self.display.setText("0")
        elif char == "=":
            if self.expression != "":
                try:
                    result = eval(self.expression)
                    self.display.setText(str(result))
                    self.expression = str(result)
                except:
                    self.display.setText("Error")
                    self.expression = ""
        else:
            self.expression = self.expression + char
            self.display.setText(self.expression)