from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import QSize, Qt
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
                # self.setStyleSheet(f.read())
                pass
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

        # Refuerzo de accesibilidad en botones principales
        for btn in [self.boton_agregar, self.boton_marcar_leido]:
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            # btn.setStyleSheet(btn.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
            font = btn.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            btn.setFont(font)
            if not btn.toolTip():
                btn.setToolTip("Botón de acción")
            if not btn.accessibleName():
                btn.setAccessibleName("Botón de acción de notificaciones")
        # Refuerzo de accesibilidad en tabla principal
        self.tabla_notificaciones.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # self.tabla_notificaciones.setStyleSheet(self.tabla_notificaciones.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")
        self.tabla_notificaciones.setToolTip("Tabla de notificaciones")
        self.tabla_notificaciones.setAccessibleName("Tabla principal de notificaciones")
        # Refuerzo visual y robustez en header de tabla principal
        h_header = self.tabla_notificaciones.horizontalHeader() if hasattr(self.tabla_notificaciones, 'horizontalHeader') else None
        if h_header is not None:
            try:
                h_header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; border-radius: 8px; font-size: 10px; padding: 8px 12px; border: 1px solid #e3e3e3;")
            except Exception:
                pass
        else:
            # EXCEPCIÓN VISUAL: No se puede aplicar refuerzo visual porque el header es None
            pass
        # Refuerzo de accesibilidad en QLabel
        for widget in self.findChildren(QLabel):
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
        # Márgenes y padding en layouts según estándar
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)
        # EXCEPCIÓN: Este módulo no usa QLineEdit ni QComboBox en la vista principal, por lo que no aplica refuerzo en inputs ni selectores.

        # Establecer el layout solo una vez al final
        self.setLayout(self.main_layout)
