class ThemeManager:
    IS_DARK = False

    LIGHT_THEME = """
        QWidget {
            background-color: transparent;
            color: #0F172A;
            font-family: Arial;
        }
        QFrame {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            border: 1px solid #E2E8F0;
        }
        QLabel {
            color: #0F172A;
            background: transparent;
            border: none;
        }
        QTableWidget {
            background-color: transparent;
            color: #0F172A;
            gridline-color: #E2E8F0;
            border: none;
        }
        QHeaderView::section {
            background-color: #F1F5F9;
            color: #1E293B;
            font-weight: bold;
            border: none;
            padding: 4px;
        }
        QLineEdit, QComboBox, QDateEdit {
            background-color: #FFFFFF;
            color: #0F172A;
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 4px;
        }
    """

    DARK_THEME = """
        QWidget {
            background-color: #0F172A;
            color: #F8FAFC;
            font-family: Arial;
        }
        QFrame {
            background-color: #1E293B;
            border-radius: 12px;
            border: 1px solid #334155;
        }
        QLabel {
            color: #F8FAFC;
            background: transparent;
            border: none;
        }
        QTableWidget {
            background-color: #1E293B;
            color: #F8FAFC;
            gridline-color: #334155;
            border: none;
        }
        QTableWidget::item {
            color: #F8FAFC;
        }
        QHeaderView::section {
            background-color: #0F172A;
            color: #F8FAFC;
            font-weight: bold;
            border: none;
            padding: 4px;
        }
        QLineEdit, QComboBox, QDateEdit {
            background-color: #334155;
            color: #F8FAFC;
            border: 1px solid #475569;
            border-radius: 6px;
            padding: 4px;
        }
    """

    @classmethod
    def toggle_theme(cls, widget):
        cls.IS_DARK = not cls.IS_DARK
        if cls.IS_DARK:
            widget.setStyleSheet(cls.DARK_THEME)
        else:
            widget.setStyleSheet(cls.LIGHT_THEME)
        return cls.IS_DARK