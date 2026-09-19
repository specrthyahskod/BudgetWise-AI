"""Financial report page with weekly .rcd export and PyQt5 compatibility."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFileDialog, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from models.rcd_format import RCDFileManager


class FinancialReportPage(QWidget):
    """Displays financial reports and supports weekly ledger export to .rcd."""

    def __init__(
        self,
        username: str = "user",
        transactions: list[dict] | None = None,
        currency: str = "AUD",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.username = username
        self.transactions = transactions or []
        self.currency = currency
        self.budget = 0.0

        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet("""
            QWidget {
                background-color: #0F172A;
                color: #F8FAFC;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #334155;
                border-color: #38BDF8;
            }
            QPushButton#ExportBtn {
                background-color: #0284C7;
                color: #FFFFFF;
                border: none;
            }
            QPushButton#ExportBtn:hover {
                background-color: #0369A1;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("← Back to Dashboard")
        self.back_btn.setFixedWidth(160)
        
        self.title_lbl = QLabel("Financial Reports & Archives")
        self.title_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.title_lbl.setStyleSheet("color: #38BDF8; background: transparent;")

        header_layout.addWidget(self.back_btn)
        header_layout.addSpacing(12)
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Report Card
        self.status_card = QFrame()
        self.status_card.setStyleSheet("background-color: #1E293B; border-radius: 12px; padding: 16px;")
        status_layout = QVBoxLayout(self.status_card)

        self.info_lbl = QLabel("Export your weekly financial ledger into a verified BudgetWise .rcd archive.")
        self.info_lbl.setFont(QFont("Segoe UI", 11))
        self.info_lbl.setStyleSheet("color: #94A3B8; background: transparent;")

        self.summary_lbl = QLabel("Ready to export current week.")
        self.summary_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.summary_lbl.setStyleSheet("color: #F8FAFC; background: transparent; margin-top: 6px;")

        status_layout.addWidget(self.info_lbl)
        status_layout.addWidget(self.summary_lbl)
        layout.addWidget(self.status_card)

        # 3. Action Download Button
        self.download_week_btn = QPushButton("Download Week (.rcd)")
        self.download_week_btn.setObjectName("ExportBtn")
        self.download_week_btn.setMinimumHeight(44)
        self.download_week_btn.clicked.connect(self._download_week)
        layout.addWidget(self.download_week_btn)

        layout.addStretch()

    def set_user_context(self, username: str) -> None:
        """Sets active user context called from main.py."""
        self.username = username or "student_user"

    def update_report(self, budget: float | dict, transactions: list[dict] | None) -> None:
        """Receives live transactions and budget from home.py."""
        self.budget = float(budget) if isinstance(budget, (int, float)) else 2500.0
        self.transactions = transactions or []
        
        week_start, week_end = self._current_week_range()
        records = self._filter_week_transactions(week_start, week_end)
        total_spent = sum(r["amount"] for r in records)
        
        self.summary_lbl.setText(
            f"Active Week ({week_start.strftime('%b %d')} – {week_end.strftime('%b %d')}): "
            f"{len(records)} transactions | ${total_spent:,.2f} {self.currency} spent"
        )

    @staticmethod
    def _current_week_range(reference: date | None = None) -> tuple[date, date]:
        today = reference or date.today()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        return monday, sunday

    @staticmethod
    def _parse_transaction_date(value: object) -> date | None:
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return date.fromisoformat(value[:10])
            except ValueError:
                return None
        return None

    def _filter_week_transactions(
        self, week_start: date, week_end: date
    ) -> list[dict]:
        filtered: list[dict] = []

        for txn in self.transactions:
            if not isinstance(txn, dict):
                continue
            txn_date = self._parse_transaction_date(txn.get("date"))
            if txn_date is None or not (week_start <= txn_date <= week_end):
                continue

            filtered.append(
                {
                    "date": txn_date.isoformat(),
                    "category": str(txn.get("category", "General")),
                    "description": str(txn.get("description", txn.get("name", ""))),
                    "amount": float(txn.get("amount", txn.get("price", 0.0))),
                }
            )

        filtered.sort(key=lambda item: item["date"])
        return filtered

    @staticmethod
    def _compute_summary_metrics(
        records: list[dict], currency: str, week_start: date, week_end: date
    ) -> dict:
        total_expenses = round(sum(record["amount"] for record in records), 2)
        record_count = len(records)
        day_span = (week_end - week_start).days + 1
        daily_average = round(total_expenses / day_span, 2) if day_span else 0.0

        return {
            "total_expenses": total_expenses,
            "record_count": record_count,
            "daily_average": daily_average,
            "currency": currency,
        }

    def _download_week(self) -> None:
        week_start, week_end = self._current_week_range()
        week_records = self._filter_week_transactions(week_start, week_end)
        summary = self._compute_summary_metrics(
            week_records, self.currency, week_start, week_end
        )

        default_name = f"BW_Week_{week_end.strftime('%Y%m%d')}.rcd"
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Weekly Record",
            default_name,
            "BudgetWise Records (*.rcd)",
        )

        if not filepath:
            return

        try:
            rcd_bytes = RCDFileManager.pack_weekly_data(
                username=self.username,
                week_start=week_start.isoformat(),
                week_end=week_end.isoformat(),
                transactions=week_records,
                summary_metrics=summary,
            )

            saved_path = RCDFileManager.save_file(filepath, rcd_bytes)

            QMessageBox.information(
                self,
                "Export Complete",
                f"Weekly financial record exported successfully to:\n{saved_path}",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export .rcd file:\n{e}"
            )