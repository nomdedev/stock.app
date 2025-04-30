from PyQt6.QtWidgets import QPushButton
from core.theme import PRIMARY_COLOR, ACCENT_COLOR, FONT_FAMILY

class CustomButton(QPushButton):
    def __init__(self, text, parent=None, style=None):
        super().__init__(text, parent)
        self.setStyleSheet(style or self.default_style())

    def default_style(self):
        return f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                font-family: {FONT_FAMILY};
                font-size: 12px;
                font-weight: bold;
                border-radius: 6px;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_COLOR};
            }}
        """