class ThemeManager:
    IS_DARK = False

    LIGHT_THEME = """
        QWidget {
            color: #0F172A;
            font-family: Arial;
        }
        QFrame {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
        }
        QTableWidget {
            background-color: transparent;
            color: #0F172A;
            gridline-color: #E2E8F0;
        }
        QHeaderView::section {
            background-color: #F1F5F9;
            color: #1E293B;
            font-weight: bold;
            border: none;
            padding: 4px;
        }
    """

    DARK_THEME = """
        QWidget {
            color: #F8FAFC;
            font-family: Arial;
        }
        QFrame {
            background-color: rgba(30, 41, 59, 0.95);
            border-radius: 12px;
        }
        QTableWidget {
            background-color: transparent;
            color: #F8FAFC;
            gridline-color: #334155;
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