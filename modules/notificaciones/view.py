from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class NotificacionesView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label_titulo = QLabel("Gestión de Notificaciones")
        self.layout.addWidget(self.label_titulo)

        self.form_layout = QFormLayout()
        self.mensaje_input = QLineEdit()
        self.fecha_input = QLineEdit()
        self.tipo_input = QLineEdit()
        self.form_layout.addRow("Mensaje:", self.mensaje_input)
        self.form_layout.addRow("Fecha:", self.fecha_input)
        self.form_layout.addRow("Tipo:", self.tipo_input)
        self.layout.addLayout(self.form_layout)

        # Botón principal como icono
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/plus_icon.svg"))
        self.boton_agregar.setIconSize(QSize(32, 32))
        self.boton_agregar.setToolTip("Agregar nueva notificación")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_agregar.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                border-radius: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1e40af;
            }
            QPushButton:pressed {
                background-color: #1e3a8a;
            }
        """)
        self.layout.addWidget(self.boton_agregar)

        # Cargar el stylesheet visual moderno para Notificaciones
        try:
            with open("styles/inventario_styles.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar inventario_styles.qss: {e}")

        self.setLayout(self.layout)
