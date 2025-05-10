from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import QSize
import json

class UsuariosView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Cargar el stylesheet visual moderno para Usuarios según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        # Botón principal de acción (Agregar)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/agregar-user.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar usuario")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_agregar.setStyleSheet("")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_agregar.setGraphicsEffect(sombra)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        # Tabla de usuarios (placeholder)
        self.tabla_usuarios = QTableWidget()
        self.layout.addWidget(self.tabla_usuarios)

        self.setLayout(self.layout)

class Usuarios(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label_titulo = QLabel("Vista de Usuarios")
        self.layout.addWidget(self.label_titulo)
        self.setLayout(self.layout)
