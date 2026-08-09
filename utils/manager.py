class ThemeManager:
    IS_DARK = True

    DARK_THEME = """
        QWidget {
            background-color: #0F172A;
            color: #F8FAFC;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QFrame {
            background-color: #1E293B;
            border-radius: 10px;
            border: 1px solid #334155;
        }
        QLabel {
            color: #F8FAFC;
            background: transparent;
            border: none;
        }
        QPushButton {
            background-color: #334155;
            color: #F8FAFC;
            border: 1px solid #475569;
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #475569;
        }
        QTableWidget {
            background-color: #1E293B;
            color: #F8FAFC;
            gridline-color: #334155;
            border: none;
            border-radius: 8px;
        }
        QTableWidget::item {
            color: #F8FAFC;
            padding: 5px;
        }
        QHeaderView::section {
            background-color: #0F172A;
            color: #94A3B8;
            font-weight: 700;
            border: none;
            border-bottom: 2px solid #334155;
            padding: 6px;
        }
        QLineEdit, QComboBox, QDateEdit {
            background-color: #0F172A;
            color: #F8FAFC;
            border: 1px solid #475569;
            border-radius: 6px;
            padding: 6px;
        }
        QCalendarWidget QWidget {
            background-color: #1E293B;
            color: #F8FAFC;
        }
        QCalendarWidget QAbstractItemView:enabled {
            background-color: #0F172A;
            color: #F8FAFC;
            selection-background-color: #16A34A;
            selection-color: #FFFFFF;
        }
    """

    @classmethod
    def apply_dark_theme(cls, widget):
        widget.setStyleSheet(cls.DARK_THEME)