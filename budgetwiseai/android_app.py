import os
import sys

def is_android():
    try:
        import android
        return True
    except ImportError:
        return False


if is_android():
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.core.window import Window
    
    Window.size = (400, 600)
    
    class BudgetWiseAndroidApp(App):
        def build(self):
            layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            
            title = Label(
                text='💰 BudgetWise AI',
                size_hint_y=0.2,
                font_size='28sp'
            )
            
            subtitle = Label(
                text='Your AI-powered student finance companion',
                size_hint_y=0.1,
                font_size='14sp'
            )
            
            info = Label(
                text='Mobile version coming soon!\n\nCore features:\n• Budget Tracking\n• AI Finance Advice\n• Expense Management',
                size_hint_y=0.6,
                font_size='12sp'
            )
            
            layout.add_widget(title)
            layout.add_widget(subtitle)
            layout.add_widget(info)
            
            return layout
    
    def main():
        app = BudgetWiseAndroidApp()
        app.run()
    
    if __name__ == '__main__':
        main()

else:
    from budgetwiseai.main import main
    
    if __name__ == '__main__':
        main()