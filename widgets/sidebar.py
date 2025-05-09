from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import QSize, pyqtSignal, Qt
from PyQt6.QtGui import QIcon
import os

class Sidebar(QWidget):
    pageChanged = pyqtSignal(int)  # Señal para cambiar página del stackedWidget

    def __init__(self, icons_path, sections, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 20, 10, 10)
        self.layout.setSpacing(8)

        # Fondo blanco para el modo claro
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QPushButton#botonMenu {
                background-color: white;
                color: #1f2937;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                text-align: center;
            }
            QPushButton#botonMenu:hover {
                background-color: #f3f4f6;
            }
            QPushButton#botonMenuActivo {
                background-color: #2563eb;
                color: white;
            }
        """)

        # Estado Online/Offline
        self.estado_label = QLabel("Online")
        self.estado_label.setObjectName("estadoOnline")
        self.estado_label.setFixedHeight(28)
        self.estado_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.estado_label.setStyleSheet("""
            QLabel#estadoOnline {
                background-color: #dcfce7;
                color: #065f46;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: bold;
                border-radius: 8px;
                padding: 0 10px;
            }
            QLabel#estadoOffline {
                background-color: #fee2e2;
                color: #991b1b;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: bold;
                border-radius: 8px;
            }
        """)
        self.layout.addWidget(self.estado_label)

        # Botones de navegación
        for index, section in enumerate(sections):
            # Permitir que section sea str o tuple (nombre, ...)
            if isinstance(section, tuple):
                section_name = section[0]
                icon_file = section[1] if len(section) > 1 else None
            else:
                section_name = section
                icon_file = None
            button = QPushButton()
            button.setObjectName("botonMenu")
            button.setFixedHeight(25)
            button.setFixedSize(44, 25)
            button.setStyleSheet("""
                QPushButton#botonMenu {
                    background-color: white;
                    color: #1f2937;
                    border-radius: 8px;
                    padding: 4px 4px;
                    font-size: 10px;
                    font-weight: 500;
                    text-align: center;
                }
                QPushButton#botonMenu:hover {
                    background-color: #f3f4f6;
                }
                QPushButton#botonMenuActivo {
                    background-color: #2563eb;
                    color: white;
                }
            """)
            # Usar SVG de utils si existe
            icon_path = os.path.join('utils', f"{section_name.lower()}.svg")
            if not os.path.exists(icon_path):
                # Fallback: buscar en img/
                icon_path = os.path.join('img', f"{section_name.lower()}.svg")
            if os.path.exists(icon_path):
                button.setIcon(QIcon(icon_path))
                button.setIconSize(QSize(20, 20))
            button.clicked.connect(lambda _, idx=index: self.pageChanged.emit(idx))
            self.layout.addWidget(button)
