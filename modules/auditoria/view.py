from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QSizePolicy, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QColor

class AuditoriaView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Cargar el stylesheet visual moderno para Auditoría según el tema activo
        try:
            with open("themes/light.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        # Botones principales como iconos
        botones_layout = QHBoxLayout()
        botones = [
            QPushButton(),  # Ver Logs
            QPushButton(),  # Exportar Logs
            QPushButton(),  # Filtrar Logs
        ]
        iconos = [
            ("search_icon.svg", "Ver logs de auditoría"),
            ("excel_icon.svg", "Exportar logs a Excel"),
            ("pdf_icon.svg", "Exportar logs a PDF"),
        ]
        for boton, (icono, tooltip) in zip(botones, iconos):
            boton.setIcon(QIcon(f"img/{icono}"))
            boton.setIconSize(QSize(32, 32))
            boton.setToolTip(tooltip)
            boton.setText("")
            boton.setFixedSize(48, 48)
            botones_layout.addWidget(boton)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        # Botón principal de acción estándar (para compatibilidad con el controlador)
        self.boton_accion = QPushButton()
        self.boton_accion.setIcon(QIcon("utils/auditoria.svg"))
        self.boton_accion.setToolTip("Ver logs de auditoría")
        self.boton_accion.setFixedSize(48, 48)
        self.boton_accion.setIconSize(QSize(32, 32))
        self.boton_accion.setObjectName("boton_accion")
        self.layout.addWidget(self.boton_accion)

        # Sombra visual profesional para el botón principal
        def aplicar_sombra(widget):
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(15)
            sombra.setXOffset(0)
            sombra.setYOffset(4)
            sombra.setColor(QColor(0, 0, 0, 160))
            widget.setGraphicsEffect(sombra)
        aplicar_sombra(self.boton_accion)

        # Tabla de logs (placeholder)
        self.tabla_logs = QTableWidget()
        self.layout.addWidget(self.tabla_logs)

        self.setLayout(self.layout)

class Auditoria(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label_titulo = QLabel("Vista de Auditoría")
        self.layout.addWidget(self.label_titulo)
        self.setLayout(self.layout)
