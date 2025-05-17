from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import QSize
import json
from core.ui_components import estilizar_boton_icono

class NotificacionesView(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        self.label_titulo = QLabel("Gestión de Notificaciones")
        self.main_layout.addWidget(self.label_titulo)

        # Cargar el stylesheet visual moderno para Notificaciones según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        # Botón principal de acción (Agregar notificación)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/plus_icon.svg"))
        self.boton_agregar.setIconSize(QSize(20, 20))
        self.boton_agregar.setToolTip("Agregar notificación")
        self.boton_agregar.setText("")
        estilizar_boton_icono(self.boton_agregar, tam_icono=20, tam_boton=48)
        botones_layout.addWidget(self.boton_agregar)

        # Botón principal de acción (Marcar como leído)
        self.boton_marcar_leido = QPushButton()
        self.boton_marcar_leido.setIcon(QIcon("img/finish-check.svg"))
        self.boton_marcar_leido.setIconSize(QSize(20, 20))
        self.boton_marcar_leido.setToolTip("Marcar como leído")
        self.boton_marcar_leido.setText("")
        estilizar_boton_icono(self.boton_marcar_leido, tam_icono=20, tam_boton=48)
        botones_layout.addWidget(self.boton_marcar_leido)
        botones_layout.addStretch()
        self.main_layout.addLayout(botones_layout)

        # Tabla de notificaciones (placeholder)
        self.tabla_notificaciones = QTableWidget()
        self.main_layout.addWidget(self.tabla_notificaciones)

        # Establecer el layout solo una vez al final
        self.setLayout(self.main_layout)
