WINDOW_STYLE = """
QWidget {
    border-radius: 12px;
    background-color: #f8f9fc;
    color: #000000;
}

QPushButton {
    background-color: #2563eb;
    color: #FFFFFF;
    border-radius: 8px;
    padding: 8px 16px;
}

QPushButton:hover {
    background-color: #1e40af;
}

QPushButton:pressed {
    background-color: #1e3a8a;
}

QLineEdit {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 8px;
    background-color: #ffffff;
    color: #000000;
}

QLineEdit:focus {
    border: 1px solid #2563eb;
}

/* Modo oscuro */
QWidget[mode="dark"] {
    background-color: #000000;
    color: #FFFFFF;
}

QPushButton[mode="dark"] {
    background-color: #2563eb;
    color: #FFFFFF;
}

QPushButton[mode="dark"]:hover {
    background-color: #1e40af;
}

QPushButton[mode="dark"]:pressed {
    background-color: #1e3a8a;
}

QLineEdit[mode="dark"] {
    border: 1px solid #2d2d2d;
    background-color: #1a1a1a;
    color: #FFFFFF;
}

QLineEdit[mode="dark"]:focus {
    border: 1px solid #2563eb;
}

QLabel {
    color: #000000;
    font-size: 14px;
}

QLabel[mode="dark"] {
    color: #d1d5db; /* Texto gris claro */
}

QTableWidget {
    border: 1px solid #e5e7eb;
    background-color: #ffffff;
    color: #000000;
    border-radius: 8px;
}

QTableWidget[mode="dark"] {
    border: 1px solid #2d2d2d;
    background-color: #1a1a1a;
    color: #FFFFFF;
}

QTableWidget::item:selected {
    background-color: #2563eb;
    color: #FFFFFF;
}

QTableWidget[mode="dark"]::item:selected {
    background-color: #1e40af;
    color: #FFFFFF;
}

QComboBox {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 6px;
    background-color: #ffffff;
    color: #000000;
}

QComboBox:focus {
    border: 1px solid #2563eb;
}

QComboBox[mode="dark"] {
    border: 1px solid #2d2d2d;
    background-color: #1a1a1a;
    color: #FFFFFF;
}

QComboBox[mode="dark"]:focus {
    border: 1px solid #2563eb;
}

QComboBox QAbstractItemView {
    border: 1px solid #e5e7eb;
    background-color: #ffffff;
    color: #000000;
}

QComboBox[mode="dark"] QAbstractItemView {
    border: 1px solid #2d2d2d;
    background-color: #1a1a1a;
    color: #FFFFFF;
}

QScrollBar:vertical {
    border: none;
    background: #f1f5f9;
    width: 12px;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background: #2563eb;
    min-height: 20px;
    border-radius: 6px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: none;
    height: 0px;
}

QScrollBar[mode="dark"]:vertical {
    background: #1a1a1a;
}

QScrollBar[mode="dark"]::handle:vertical {
    background: #1e40af;
}

QFrame {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    background-color: #ffffff;
}

QFrame[mode="dark"] {
    border: 1px solid #2d2d2d;
    background-color: #1a1a1a;
}
"""
