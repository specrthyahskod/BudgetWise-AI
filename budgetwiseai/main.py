import os
import sys

# Platform detection - use Kivy for Android, PyQt5 for desktop
try:
    import android
    PLATFORM = "android"
except ImportError:
    PLATFORM = "desktop"

if PLATFORM == "android":
    # ============================================
    # ANDROID VERSION (Kivy)
    # ============================================
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.textinput import TextInput
    from kivy.uix.image import Image
    from kivy.core.window import Window
    from kivy.uix.stacklayout import StackLayout
    from kivy.uix.scrollview import ScrollView
    from kivy.graphics import Color, Rectangle
    
    Window.size = (400, 700)
    
    class BudgetWiseApp(App):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.title = "BudgetWise AI"
            self.current_user = None
            self.screens = {}
        
        def build(self):
            self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            self.main_layout.canvas.before.clear()
            with self.main_layout.canvas.before:
                Color(0.067, 0.11, 0.16, 1)  # Dark background
                Rectangle(size=Window.size, pos=self.main_layout.pos)
            
            # Title
            title = Label(
                text='💰 BudgetWise AI',
                size_hint_y=0.12,
                font_size='28sp',
                color=(0.98, 0.98, 0.98, 1)
            )
            
            # Subtitle
            subtitle = Label(
                text='Your AI-powered student finance companion',
                size_hint_y=0.08,
                font_size='14sp',
                color=(0.29, 0.33, 0.35, 1)
            )
            
            # Content area
            content_layout = BoxLayout(orientation='vertical', size_hint_y=0.7, spacing=10, padding=10)
            content_layout.canvas.before.clear()
            with content_layout.canvas.before:
                Color(0.12, 0.18, 0.22, 1)
                Rectangle(size=content_layout.size, pos=content_layout.pos)
            
            welcome_label = Label(
                text='Welcome to BudgetWise!',
                font_size='20sp',
                size_hint_y=0.15,
                color=(0.98, 0.98, 0.98, 1)
            )
            
            info_label = Label(
                text='Features:\n'
                     '• 💳 Budget Tracking\n'
                     '• 🤖 AI Finance Advice\n'
                     '• 📊 Expense Management\n'
                     '• 💰 Savings Goals\n'
                     '• 📈 Financial Analytics',
                font_size='13sp',
                size_hint_y=0.6,
                color=(0.98, 0.98, 0.98, 1),
                markup=True
            )
            
            login_btn = Button(
                text='Login',
                size_hint_y=0.15,
                background_color=(0.2, 0.6, 0.8, 1)
            )
            login_btn.bind(on_press=self.show_login)
            
            signup_btn = Button(
                text='Sign Up',
                size_hint_y=0.15,
                background_color=(0.3, 0.7, 0.4, 1)
            )
            signup_btn.bind(on_press=self.show_signup)
            
            content_layout.add_widget(welcome_label)
            content_layout.add_widget(info_label)
            content_layout.add_widget(login_btn)
            content_layout.add_widget(signup_btn)
            
            # Footer
            footer = Label(
                text='© 2026 BudgetWise AI. All Rights Reserved.',
                size_hint_y=0.1,
                font_size='9sp',
                color=(0.42, 0.45, 0.5, 1)
            )
            
            self.main_layout.add_widget(title)
            self.main_layout.add_widget(subtitle)
            self.main_layout.add_widget(content_layout)
            self.main_layout.add_widget(footer)
            
            return self.main_layout
        
        def show_login(self, instance):
            # Placeholder for login screen
            print("Login button pressed")
        
        def show_signup(self, instance):
            # Placeholder for signup screen
            print("Signup button pressed")
    
    def main():
        app = BudgetWiseApp()
        app.run()
    
    if __name__ == "__main__":
        main()

else:
    # ============================================
    # DESKTOP VERSION (PyQt5) - Original Code
    # ============================================
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QLabel, QStackedWidget, QSizePolicy
    )
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QBrush
    from pages.login import Login
    from pages.home import home
    from pages.remember_pass import remember_pass
    from pages.signup import Signup

    def get_asset_path(filename):
        """Resolves absolute path to assets for local running and packaged builds."""
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'assets', filename)


    class BudgetWiseApp(QWidget):
        def __init__(self):
            super().__init__()
            self.init_ui()

        def init_ui(self):
            self.setWindowTitle("BudgetWise AI")
            self.resize(950, 650)

            icon_path = get_asset_path("BudgetWise_AI_logo.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))

            self.main_layout = QVBoxLayout()
            self.main_layout.setContentsMargins(20, 20, 20, 15)
            self.main_layout.setSpacing(10)

            self.title = QLabel("💰 BudgetWise AI")
            self.title.setFont(QFont("Arial", 26, QFont.Bold))
            self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.subtitle = QLabel("Your AI-powered student finance companion")
            self.subtitle.setFont(QFont("Arial", 11))
            self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.stacked_widget = QStackedWidget()
            self.stacked_widget.setStyleSheet("background: transparent;")
            self.stacked_widget.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )

            self.login_widget = Login()
            self.home_page = home()
            self.reset_page = remember_pass()
            self.signup_page = Signup()

            self.stacked_widget.addWidget(self.login_widget)
            self.stacked_widget.addWidget(self.home_page)
            self.stacked_widget.addWidget(self.reset_page)
            self.stacked_widget.addWidget(self.signup_page)

            self.login_widget.login_successful.connect(self.on_login_success)

            self.login_widget.forgot_password_requested.connect(
                lambda: self.stacked_widget.setCurrentIndex(2)
            )

            self.login_widget.signup_requested.connect(
                lambda: self.stacked_widget.setCurrentIndex(3)
            )

            self.reset_page.back_to_login_requested.connect(
                lambda: self.stacked_widget.setCurrentIndex(0)
            )

            self.signup_page.back_to_login_requested.connect(
                lambda: self.stacked_widget.setCurrentIndex(0)
            )

            self.signup_page.signup_successful.connect(self.on_login_success)

            self.footer_widget = QWidget()
            footer_layout = QVBoxLayout(self.footer_widget)
            footer_layout.setContentsMargins(0, 5, 0, 0)
            footer_layout.setSpacing(3)
            footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.copyright_label = QLabel("© 2026 BudgetWise AI. All Rights Reserved.")
            self.copyright_label.setFont(QFont("Arial", 9))
            self.copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.legal_label = QLabel("Privacy Policy  |  Terms of Service  |  Educational Purpose Only  |  Contact Support")
            self.legal_label.setFont(QFont("Arial", 8))
            self.legal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            footer_layout.addWidget(self.copyright_label)
            footer_layout.addWidget(self.legal_label)

            self.main_layout.addWidget(self.title)
            self.main_layout.addWidget(self.subtitle)
            self.main_layout.addWidget(self.stacked_widget, 1)
            self.main_layout.addWidget(self.footer_widget)

            self.setLayout(self.main_layout)

            self.stacked_widget.currentChanged.connect(self.on_page_changed)
            self.on_page_changed(0)

        def apply_background_image(self):
            image_path = get_asset_path("background.png")

            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                palette = self.palette()
                palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
                self.setPalette(palette)
                self.setAutoFillBackground(True)

            self.main_layout.setContentsMargins(20, 20, 20, 15)
            self.main_layout.setSpacing(10)
            self.title.show()
            self.subtitle.show()
            self.footer_widget.show()

            self.title.setStyleSheet("color: #111827;")
            self.subtitle.setStyleSheet("color: #4B5563;")
            self.copyright_label.setStyleSheet("color: #4B5563; font-weight: bold;")
            self.legal_label.setStyleSheet("color: #6B7280;")

        def apply_maximized_dark_dashboard(self):
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor("#111827"))
            palette.setColor(QPalette.WindowText, QColor("#F9FAFB"))
            palette.setColor(QPalette.Base, QColor("#1F2937"))
            palette.setColor(QPalette.Text, QColor("#F9FAFB"))
            
            self.setPalette(palette)
            self.setAutoFillBackground(True)

            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)
            
            self.title.hide()
            self.subtitle.hide()
            self.footer_widget.hide()

            self.showMaximized()

        def on_page_changed(self, index):
            if index == 1:  
                self.apply_maximized_dark_dashboard()
            else:        
                self.apply_background_image()

        def resizeEvent(self, a0):
            if self.stacked_widget.currentIndex() != 1:
                self.apply_background_image()
            super().resizeEvent(a0)

        def on_login_success(self, username):
            self.home_page.set_username(username)
            self.stacked_widget.setCurrentIndex(1)


    def main():
        app = QApplication(sys.argv)

        icon_path = get_asset_path("BudgetWise_AI_logo.png")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))

        window = BudgetWiseApp()
        window.show()
        sys.exit(app.exec_())


    if __name__ == "__main__":
        main()
