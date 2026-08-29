import os
import json
import base64
import urllib.request
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QSpinBox, QComboBox, QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont


class AIRoutineAnalyzer(QThread):
    parsed_signal = pyqtSignal(list, str)

    def __init__(self, image_path, api_key=""):
        super().__init__()
        self.image_path = image_path
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")

    def run(self):
        extracted_units = []
        raw_summary = ""

        if self.api_key:
            try:
                with open(self.image_path, "rb") as img_f:
                    b64_image = base64.b64encode(img_f.read()).decode("utf-8")

                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                
                prompt_text = (
                    "Look closely at this student routine/timetable image. "
                    "Extract all unique subjects, modules, and course names/codes exactly as shown in the schedule. "
                    "Determine the academic intensity based on class frequency and subject type into one of: "
                    "'Core STEM (High)', 'STEM Analytics', 'Theory / Standard', 'Elective / Light'. "
                    "Return ONLY a pure JSON array of objects with keys: "
                    "'code' (string subject/course title), 'type' (string classification), "
                    "'credits' (integer, default 6), and 'exam_soon' (boolean). "
                    "Do not return markdown fences, explanation, or placeholder codes like INFO101 unless explicitly in the image."
                )

                payload = {
                    "contents": [{
                        "parts": [
                            {"text": prompt_text},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": b64_image
                                }
                            }
                        ]
                    }]
                }

                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )

                with urllib.request.urlopen(req, timeout=20) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    text_resp = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if text_resp.startswith("```"):
                        text_resp = text_resp.split("```")[1]
                        if text_resp.startswith("json"):
                            text_resp = text_resp[4:]
                    extracted_units = json.loads(text_resp.strip())
                    raw_summary = "AI Vision Successfully Extracted Dynamic Timetable"
            except Exception:
                extracted_units = []

        if not extracted_units:
            raw_summary = "No subjects detected. Please upload an image or add subjects manually."

        self.parsed_signal.emit(extracted_units, raw_summary)


class StudyShiftMatrixDialog(QDialog):
    def __init__(self, work_days_count, hours_per_shift, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dynamic Timetable & Workload Optimizer")
        self.setFixedSize(680, 640)
        self.setStyleSheet("background-color: #0F172A; color: #F8FAFC;")
        
        self.work_days_count = work_days_count
        self.hours_per_shift = hours_per_shift
        self.timetable_image_path = ""
        
        self.type_combos = []
        self.credit_spins = []
        self.exam_combos = []
        self.units_data = []
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("🤖 Timetable & Workload Routine Management")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Upload your class routine to auto-extract enrolled subjects and balance study-work stress.")
        subtitle.setFont(QFont("Segoe UI", 9))
        subtitle.setStyleSheet("color: #94A3B8;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        upload_frame = QFrame()
        upload_frame.setStyleSheet("background-color: #1E293B; border: 1px dashed #3B82F6; border-radius: 10px;")
        up_layout = QHBoxLayout(upload_frame)
        up_layout.setContentsMargins(15, 10, 15, 10)

        self.lbl_upload_status = QLabel("📷 No Timetable Image Uploaded")
        self.lbl_upload_status.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_upload_status.setStyleSheet("color: #94A3B8; border: none;")

        self.btn_upload = QPushButton("Upload Schedule Routine")
        self.btn_upload.setFixedHeight(34)
        self.btn_upload.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border-radius: 6px; border: none; padding: 0 14px;")
        self.btn_upload.clicked.connect(self.choose_and_process_image)

        up_layout.addWidget(self.lbl_upload_status, 1)
        up_layout.addWidget(self.btn_upload)

        self.ocr_progress = QProgressBar()
        self.ocr_progress.setRange(0, 0)
        self.ocr_progress.setFixedHeight(4)
        self.ocr_progress.setTextVisible(False)
        self.ocr_progress.setStyleSheet("QProgressBar { background-color: #1E293B; border: none; } QProgressBar::chunk { background-color: #3B82F6; }")
        self.ocr_progress.hide()

        self.metric_card = QFrame()
        self.metric_card.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; border-radius: 10px;")
        m_layout = QHBoxLayout(self.metric_card)
        m_layout.setContentsMargins(15, 10, 15, 10)

        self.lbl_work_hrs = QLabel(f"Work: {self.work_days_count * self.hours_per_shift:.1f} hrs/fn")
        self.lbl_work_hrs.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_work_hrs.setStyleSheet("color: #60A5FA; border: none;")

        self.lbl_study_hrs = QLabel("Study Required: 0.0 hrs/fn")
        self.lbl_study_hrs.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_study_hrs.setStyleSheet("color: #38BDF8; border: none;")

        self.lbl_burnout = QLabel("Risk: Normal")
        self.lbl_burnout.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_burnout.setStyleSheet("color: #4ADE80; border: none;")

        m_layout.addWidget(self.lbl_work_hrs)
        m_layout.addStretch()
        m_layout.addWidget(self.lbl_study_hrs)
        m_layout.addStretch()
        m_layout.addWidget(self.lbl_burnout)

        table_header_layout = QHBoxLayout()
        tbl_lbl = QLabel("Enrolled Course Workload Breakdown")
        tbl_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        btn_add_row = QPushButton("+ Add Course")
        btn_add_row.setFixedHeight(28)
        btn_add_row.setStyleSheet("background-color: #334155; color: #F8FAFC; border-radius: 4px; padding: 0 10px; font-weight: bold;")
        btn_add_row.clicked.connect(self.add_manual_row)

        table_header_layout.addWidget(tbl_lbl)
        table_header_layout.addStretch()
        table_header_layout.addWidget(btn_add_row)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Extracted Subject / Unit", "Difficulty Type", "Credits", "Major Exam/Due?"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1E293B;
                color: #F8FAFC;
                gridline-color: #334155;
                border: 1px solid #334155;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #0F172A;
                color: #94A3B8;
                font-weight: bold;
                border: none;
                padding: 6px;
            }
        """)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)

        self.banner = QLabel("Upload a routine image above to extract subjects and analyze fatigue risk.")
        self.banner.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.banner.setWordWrap(True)
        self.banner.setStyleSheet("padding: 10px; border-radius: 8px; background-color: #1E293B; border: 1px solid #334155; color: #94A3B8;")

        btn_analyze = QPushButton("⚡ Re-Calculate Workload Risk")
        btn_analyze.setFixedHeight(38)
        btn_analyze.setStyleSheet("background-color: #2563EB; color: white; font-weight: bold; border-radius: 6px; border: none;")
        btn_analyze.clicked.connect(self.calculate_matrix)

        btn_close = QPushButton("Done")
        btn_close.setFixedHeight(34)
        btn_close.setStyleSheet("background-color: #334155; color: #F8FAFC; font-weight: bold; border-radius: 6px; border: none;")
        btn_close.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(upload_frame)
        layout.addWidget(self.ocr_progress)
        layout.addWidget(self.metric_card)
        layout.addLayout(table_header_layout)
        layout.addWidget(self.table, 1)
        layout.addWidget(self.banner)
        layout.addWidget(btn_analyze)
        layout.addWidget(btn_close)

        self.setLayout(layout)

    def choose_and_process_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Timetable Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if not file_path:
            return

        self.timetable_image_path = file_path
        filename = os.path.basename(file_path)
        self.lbl_upload_status.setText(f"Scanning: {filename}...")
        self.lbl_upload_status.setStyleSheet("color: #60A5FA; border: none;")
        self.btn_upload.setEnabled(False)
        self.ocr_progress.show()

        self.analyzer_thread = AIRoutineAnalyzer(file_path)
        self.analyzer_thread.parsed_signal.connect(self.on_timetable_analyzed)
        self.analyzer_thread.start()

    def on_timetable_analyzed(self, units_list, raw_text):
        self.ocr_progress.hide()
        self.btn_upload.setEnabled(True)
        filename = os.path.basename(self.timetable_image_path)

        if not units_list:
            self.lbl_upload_status.setText(f"⚠️ No subjects detected in {filename}")
            self.lbl_upload_status.setStyleSheet("color: #EF4444; border: none;")
            QMessageBox.warning(
                self,
                "No Subjects Extracted",
                "Could not automatically read subjects from the routine image.\nPlease add them using the '+ Add Course' button."
            )
            return

        self.lbl_upload_status.setText(f"✓ Detected: {filename} ({len(units_list)} Subjects Found)")
        self.lbl_upload_status.setStyleSheet("color: #4ADE80; border: none;")

        self.units_data = units_list
        self.populate_table()
        self.calculate_matrix()

    def add_manual_row(self):
        self.units_data.append({
            "code": f"Subject {len(self.units_data) + 1}",
            "type": "Theory / Standard",
            "credits": 6,
            "exam_soon": False
        })
        self.populate_table()
        self.calculate_matrix()

    def populate_table(self):
        self.type_combos.clear()
        self.credit_spins.clear()
        self.exam_combos.clear()
        self.table.setRowCount(len(self.units_data))

        for row, unit in enumerate(self.units_data):
            self.table.setItem(row, 0, QTableWidgetItem(str(unit.get("code", ""))))
            
            combo_type = QComboBox()
            combo_type.addItems(["Core STEM (High)", "STEM Analytics", "Theory / Standard", "Elective / Light"])
            combo_type.setCurrentText(str(unit.get("type", "Theory / Standard")))
            self.table.setCellWidget(row, 1, combo_type)
            self.type_combos.append(combo_type)

            spin_cr = QSpinBox()
            spin_cr.setRange(1, 24)
            spin_cr.setValue(int(unit.get("credits", 6)))
            self.table.setCellWidget(row, 2, spin_cr)
            self.credit_spins.append(spin_cr)

            combo_exam = QComboBox()
            combo_exam.addItems(["Yes (Heavy)", "No (Standard)"])
            combo_exam.setCurrentText("Yes (Heavy)" if unit.get("exam_soon", False) else "No (Standard)")
            self.table.setCellWidget(row, 3, combo_exam)
            self.exam_combos.append(combo_exam)

    def calculate_matrix(self):
        if not self.type_combos:
            self.lbl_study_hrs.setText("Study Required: 0.0 hrs/fn")
            self.lbl_burnout.setText("Risk: No Courses")
            self.lbl_burnout.setStyleSheet("color: #94A3B8; border: none;")
            return

        total_study_hours = 0.0
        heavy_units_count = 0

        for row in range(len(self.type_combos)):
            u_type = self.type_combos[row].currentText()
            credits_val = self.credit_spins[row].value()
            is_heavy = self.exam_combos[row].currentText() == "Yes (Heavy)"

            multiplier = 1.0
            if u_type == "Core STEM (High)":
                multiplier = 1.6
            elif u_type == "STEM Analytics":
                multiplier = 1.4
            elif u_type == "Elective / Light":
                multiplier = 0.75

            base_hours = credits_val * 1.5 * 2.0
            adjusted = base_hours * multiplier
            
            if is_heavy:
                adjusted = adjusted * 1.35
                heavy_units_count += 1
                
            total_study_hours += adjusted

        total_work_hours = self.work_days_count * self.hours_per_shift
        total_committed_hours = total_study_hours + total_work_hours
        
        capacity = 140.0
        load_pct = (total_committed_hours / capacity) * 100.0

        self.lbl_study_hrs.setText(f"Study: {total_study_hours:.1f} hrs/fn")

        if load_pct > 95.0 or (total_work_hours >= 40 and heavy_units_count >= 2):
            self.lbl_burnout.setText("Risk: HIGH BURNOUT 🚨")
            self.lbl_burnout.setStyleSheet("color: #EF4444; font-weight: bold; border: none;")
            shifts_to_cut = max((total_committed_hours - capacity) / max(self.hours_per_shift, 1.0), 1.0)
            self.banner.setText(
                f"⚠️ Academic Overload Detected!\n"
                f"You have {heavy_units_count} high-intensity modules alongside {total_work_hours:.0f} work hours.\n"
                f"Total fortnightly demand ({total_committed_hours:.1f} hrs) exceeds healthy capacity. "
                f"Recommendation: Reduce work shifts by ~{shifts_to_cut:.0f} shift(s) this cycle."
            )
            self.banner.setStyleSheet("background-color: rgba(239, 68, 68, 0.15); color: #FCA5A5; border: 1px solid #EF4444; border-radius: 8px; padding: 10px;")
        elif load_pct > 75.0:
            self.lbl_burnout.setText("Risk: Moderate ⚠️")
            self.lbl_burnout.setStyleSheet("color: #F59E0B; font-weight: bold; border: none;")
            self.banner.setText(
                f"⚖️ Schedule Tight: Combined work & study load ({total_committed_hours:.1f} hrs/fn) is manageable but has minimal buffer for unexpected assignments."
            )
            self.banner.setStyleSheet("background-color: rgba(245, 158, 11, 0.15); color: #FCD34D; border: 1px solid #F59E0B; border-radius: 8px; padding: 10px;")
        else:
            self.lbl_burnout.setText("Risk: Optimal ✅")
            self.lbl_burnout.setStyleSheet("color: #22C55E; font-weight: bold; border: none;")
            self.banner.setText(
                f"✅ Balanced Workload: {total_work_hours:.0f} work hours and {total_study_hours:.1f} study hours fit comfortably within your 14-day schedule."
            )
            self.banner.setStyleSheet("background-color: rgba(34, 197, 94, 0.15); color: #86EFAC; border: 1px solid #22C55E; border-radius: 8px; padding: 10px;")