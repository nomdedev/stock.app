from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QTabWidget, QDialog, QMessageBox, QInputDialog, QCheckBox, QScrollArea, QHeaderView, QMenu
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal, QSize
import json
from modules.vidrios.view import VidriosView

class InventarioView(QWidget):
    # Señales para acciones principales
    nuevo_item_signal = pyqtSignal()
    ver_movimientos_signal = pyqtSignal()
    reservar_signal = pyqtSignal()
    exportar_excel_signal = pyqtSignal()
    exportar_pdf_signal = pyqtSignal()
    buscar_signal = pyqtSignal()
    generar_qr_signal = pyqtSignal()
    actualizar_signal = pyqtSignal()
    ajustar_stock_signal = pyqtSignal()

    def obtener_id_item_seleccionado(self):
        # Devuelve el ID del ítem seleccionado en la tabla (stub para pruebas)
        fila = self

        # Botones principales como iconos
        botones_layout = QHBoxLayout()
        botones = [
            QPushButton(),  # Nuevo ítem
            QPushButton(),  # Ver movimientos
            QPushButton(),  # Reservar
            QPushButton(),  # Exportar a Excel
            QPushButton(),  # Exportar a PDF
            QPushButton(),  # Buscar
            QPushButton(),  # Generar QR
            QPushButton(),  # Actualizar
            QPushButton(),  # Ajustar stock
        ]
        iconos = [
            ("plus_icon.svg", "Agregar nuevo ítem"),
            ("search_icon.svg", "Ver movimientos"),
            ("reservar-mas.png", "Reservar ítem"),
            ("excel_icon.svg", "Exportar a Excel"),
            ("pdf_icon.svg", "Exportar a PDF"),
            ("buscar.png", "Buscar ítem"),
            ("qr_icon.svg", "Generar código QR"),
            ("refresh_icon.svg", "Actualizar tabla"),
            ("ajustar.png", "Ajustar stock"),
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
