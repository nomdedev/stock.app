from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt6 import QtGui
from PyQt6.QtCore import QSize

class LogisticaView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        # Cargar el stylesheet visual moderno para Logística
        try:
            with open("styles/inventario_styles.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar inventario_styles.qss: {e}")
        # Botones principales como iconos
        botones_layout = QHBoxLayout()
        botones = [
            QPushButton(),  # Nueva Entrega
            QPushButton(),  # Ver Hoja de Ruta
            QPushButton(),  # Exportar a Excel
        ]
        iconos = [
            ("plus_icon.svg", "Agregar nueva entrega"),
            ("proceso.png", "Ver hoja de ruta"),
            ("excel_icon.svg", "Exportar entregas a Excel"),
        ]
        for boton, (icono, tooltip) in zip(botones, iconos):
            boton.setIcon(QtGui.QIcon(f"img/{icono}"))
            boton.setIconSize(QSize(32, 32))
            boton.setToolTip(tooltip)
            boton.setText("")
            boton.setFixedSize(48, 48)
            boton.setStyleSheet("""
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
            botones_layout.addWidget(boton)
        self.layout.addLayout(botones_layout)

    @property
    def label(self):
        if not hasattr(self, '_label_estado'):
            self._label_estado = QLabel()
        return self._label_estado

    @property
    def buscar_input(self):
        if not hasattr(self, '_buscar_input'):
            self._buscar_input = QLineEdit()
        return self._buscar_input

    @property
    def id_item_input(self):
        if not hasattr(self, '_id_item_input'):
            self._id_item_input = QLineEdit()
        return self._id_item_input
