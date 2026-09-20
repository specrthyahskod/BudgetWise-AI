import os
import sys
import json
import csv
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

ROOT_DIR = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "tools" else Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from models.rcd_format import RCDFileManager, InvalidRCDFileError


class RCDViewerWindow(QMainWindow):
    def __init__(self, target_filepath: str | None = None):
        super().__init__()
        self.current_filepath: str | None = target_filepath
        self.unpacked_data = None

        self.setWindowTitle("BudgetWise Record Viewer (.rcd)")
        self.resize(850, 620)
        self.init_ui()

        if self.current_filepath and os.path.exists(self.current_filepath):
            self.load_rcd_file(self.current_filepath)

    def init_ui(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0F172A;
            }
            QWidget {
                color: #F8FAFC;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #334155;
                border-color: #38BDF8;
            }
            QPushButton#PrimaryBtn {
                background-color: #0284C7;
                border: none;
            }
            QPushButton#PrimaryBtn:hover {
                background-color: #0369A1;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        top_bar = QHBoxLayout()
        title_box = QVBoxLayout()

        self.title_lbl = QLabel("📁 BudgetWise Complier")
        self.title_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.title_lbl.setStyleSheet("color: #38BDF8;")

        self.file_path_lbl = QLabel("No file loaded. Click 'Open .rcd File' to inspect.")
        self.file_path_lbl.setFont(QFont("Segoe UI", 9))
        self.file_path_lbl.setStyleSheet("color: #94A3B8;")

        title_box.addWidget(self.title_lbl)
        title_box.addWidget(self.file_path_lbl)
        top_bar.addLayout(title_box)
        top_bar.addStretch()

        open_btn = QPushButton("Open Other .rcd")
        open_btn.clicked.connect(self.browse_file)
        top_bar.addWidget(open_btn)

        self.export_btn = QPushButton("Export to JSON / CSV")
        self.export_btn.setObjectName("PrimaryBtn")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.decompile_current_archive)
        top_bar.addWidget(self.export_btn)

        main_layout.addLayout(top_bar)

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(12)

        self.card_status, self.lbl_status = self._create_metric_card("INTEGRITY STATUS", "UNCHECKED", "#94A3B8")
        self.card_user, self.lbl_user = self._create_metric_card("RECORD OWNER", "—", "#38BDF8")
        self.card_period, self.lbl_period = self._create_metric_card("STATEMENT WINDOW", "—", "#F8FAFC")
        self.card_spent, self.lbl_spent = self._create_metric_card("TOTAL RECORD SPEND", "$0.00", "#F87171")

        metrics_layout.addWidget(self.card_status)
        metrics_layout.addWidget(self.card_user)
        metrics_layout.addWidget(self.card_period)
        metrics_layout.addWidget(self.card_spent)
        main_layout.addLayout(metrics_layout)

        table_frame = QFrame()
        table_frame.setStyleSheet("background-color: #1E293B; border-radius: 10px; border: 1px solid #334155;")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(12, 12, 12, 12)

        table_heading = QLabel("Decrypted Ledger Entries")
        table_heading.setFont(QFont("Segoe UI", 11, QFont.Bold))
        table_heading.setStyleSheet("color: #E2E8F0; border: none; background: transparent;")
        table_layout.addWidget(table_heading)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Category", "Description", "Amount"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0F172A;
                color: #F8FAFC;
                gridline-color: #334155;
                border: 1px solid #334155;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #1E293B;
                color: #94A3B8;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)

        table_layout.addWidget(self.table)
        main_layout.addWidget(table_frame, 1)

    def _create_metric_card(self, title: str, initial_val: str, text_color: str):
        card = QFrame()
        card.setFixedHeight(75)
        card.setStyleSheet("background-color: #1E293B; border-radius: 8px; border: 1px solid #334155;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_t = QLabel(title)
        lbl_t.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lbl_t.setStyleSheet("color: #94A3B8; border: none; background: transparent;")

        lbl_v = QLabel(initial_val)
        lbl_v.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl_v.setStyleSheet(f"color: {text_color}; border: none; background: transparent;")

        layout.addWidget(lbl_t)
        layout.addWidget(lbl_v)
        return card, lbl_v

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open BudgetWise Record", "", "BudgetWise Records (*.rcd);;All Files (*)"
        )
        if path:
            self.load_rcd_file(path)

    def load_rcd_file(self, filepath: str):
        self.current_filepath = filepath
        self.file_path_lbl.setText(filepath)

        try:
            data = RCDFileManager.unpack_file(filepath)
            self.unpacked_data = data

            self.lbl_status.setText("VERIFIED ✅")
            self.lbl_status.setStyleSheet("color: #10B981; border: none; background: transparent;")

            self.lbl_user.setText(data.get("user", "Unknown"))
            
            period = data.get("period", {})
            self.lbl_period.setText(f"{period.get('start', '?')} → {period.get('end', '?')}")

            summary = data.get("summary", {})
            total_spent = summary.get("total_expenses", summary.get("weekly_expenses", 0.0))
            currency = summary.get("currency", "AUD")
            self.lbl_spent.setText(f"${float(total_spent):,.2f} {currency}")

            records = data.get("records", [])
            self.table.setRowCount(len(records))
            for idx, r in enumerate(records):
                date_item = QTableWidgetItem(str(r.get("date", "")))
                cat_item = QTableWidgetItem(str(r.get("category", "")))
                desc_item = QTableWidgetItem(str(r.get("description", "")))
                
                amt = float(r.get("amount", 0.0))
                amt_item = QTableWidgetItem(f"${amt:,.2f}")
                amt_item.setForeground(QColor("#F87171") if cat_item.text().lower() != "income" else QColor("#4ADE80"))

                self.table.setItem(idx, 0, date_item)
                self.table.setItem(idx, 1, cat_item)
                self.table.setItem(idx, 2, desc_item)
                self.table.setItem(idx, 3, amt_item)

            self.export_btn.setEnabled(True)

        except InvalidRCDFileError as e:
            self.lbl_status.setText("TAMPERED ❌")
            self.lbl_status.setStyleSheet("color: #EF4444; border: none; background: transparent;")
            self.table.setRowCount(0)
            self.export_btn.setEnabled(False)
            QMessageBox.critical(
                self,
                "Archive Security Error",
                f"The selected file failed cryptographic integrity checks:\n\n{e}\n\n"
                "This file may have been modified or corrupted outside BudgetWise AI."
            )
        except Exception as e:
            QMessageBox.critical(self, "Read Error", f"Unable to open .rcd archive:\n{e}")

    def decompile_current_archive(self):
        """Allows non-technical users to decompile the archive back to JSON or CSV."""
        if not self.unpacked_data:
            return

        default_base = self.current_filepath if self.current_filepath else "export_record.rcd"
        suggested_path = str(Path(default_base).with_suffix(".json"))

        save_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Decompile Financial Archive",
            suggested_path,
            "JSON Format (*.json);;CSV Format (*.csv)"
        )
        if not save_path:
            return

        try:
            if save_path.lower().endswith(".csv") or "CSV" in selected_filter:
                with open(save_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["date", "category", "description", "amount"])
                    for r in self.unpacked_data.get("records", []):
                        writer.writerow([r.get("date"), r.get("category"), r.get("description"), r.get("amount")])
            else:
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(self.unpacked_data, f, indent=2, ensure_ascii=False)

            QMessageBox.information(self, "Decompile Successful", f"File saved as:\n{save_path}")
        except Exception as e:
            QMessageBox.warning(self, "Export Failed", f"Could not save file:\n{e}")


def main():
    app = QApplication(sys.argv)
    file_to_open = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].lower().endswith(".rcd") else None
    window = RCDViewerWindow(file_to_open)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()