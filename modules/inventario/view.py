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

    def __init__(self):
        super().__init__()
        self.setObjectName("inventarioView")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.layout.setSpacing(0)
        self.setStyleSheet("""
            #inventarioView {
                background-color: #232B36;
                border-radius: 24px;
            }
            QLabel {
                color: #fff;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 32px;
                font-weight: 700;
                letter-spacing: 1px;
                margin-bottom: 24px;
            }
            QTableWidget {
                background-color: #232B36;
                color: #fff;
                border-radius: 16px;
                border: none;
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-weight: 400;
                gridline-color: #2E3742;
            }
            QHeaderView::section {
                background-color: #232B36;
                color: #fff;
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-weight: 700;
                border: none;
                padding: 12px 0;
            }
            QTableWidget::item {
                background-color: #232B36;
                border: none;
                padding: 8px 0;
            }
            QTableWidget::item:selected {
                background-color: #2E3742;
                color: #fff;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background: #232B36;
                border-radius: 8px;
                width: 12px;
            }
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 8px;
                min-width: 48px;
                min-height: 48px;
                max-width: 48px;
                max-height: 48px;
            }
            QPushButton:hover {
                background: #2E3742;
            }
        """)

        # Título
        self.label_titulo = QLabel("INVENTORY")
        self.layout.addWidget(self.label_titulo)

        # Tabla principal de inventario
        self.tabla_inventario = QTableWidget()
        self.tabla_inventario.setColumnCount(7)
        self.tabla_inventario.setHorizontalHeaderLabels([
            "Code", "Description", "Location", "Supplier", "Quantity", "Unit", ""
        ])
        self.tabla_inventario.setAlternatingRowColors(True)
        self.tabla_inventario.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_inventario.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_inventario.verticalHeader().setVisible(False)
        self.tabla_inventario.horizontalHeader().setHighlightSections(False)
        self.tabla_inventario.setShowGrid(False)
        self.layout.addWidget(self.tabla_inventario)

        # Botones principales como iconos (arriba a la derecha)
        top_btns_layout = QHBoxLayout()
        top_btns_layout.addStretch()
        iconos = [
            ("plus_icon.svg", "Agregar nuevo ítem"),
            ("excel_icon.svg", "Exportar a Excel"),
            ("pdf_icon.svg", "Exportar a PDF"),
            ("search_icon.svg", "Buscar ítem"),
            ("qr_icon.svg", "Generar código QR"),
        ]
        for icono, tooltip in iconos:
            btn = QPushButton()
            btn.setIcon(QtGui.QIcon(f"img/{icono}"))
            btn.setIconSize(QSize(24, 24))
            btn.setToolTip(tooltip)
            btn.setText("")
            top_btns_layout.addWidget(btn)
        self.layout.insertLayout(1, top_btns_layout)

        # Botones grandes debajo de la tabla
        bottom_btns_layout = QHBoxLayout()
        bottom_btns_layout.setSpacing(32)
        btns = [
            ("refresh_icon.svg", "Refresh"),
            ("ajustar.png", "Adjust stock"),
            ("search_icon.svg", "View"),
            ("reservar-mas.png", "Reserve"),
        ]
        for icono, texto in btns:
            btn = QPushButton()
            btn.setIcon(QtGui.QIcon(f"img/{icono}"))
            btn.setIconSize(QSize(28, 28))
            btn.setText(f"  {texto}")
            btn.setStyleSheet("""
                QPushButton {
                    background: #232B36;
                    color: #AEE9D1;
                    border: 2px solid #3DE6B1;
                    border-radius: 16px;
                    font-size: 20px;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                    font-weight: 600;
                    padding: 16px 32px;
                    min-width: 220px;
                    min-height: 64px;
                    text-align: left;
                }
                QPushButton:hover {
                    background: #2E3742;
                    color: #fff;
                }
            """)
            btn.setToolTip(texto)
            bottom_btns_layout.addWidget(btn)
        self.layout.addSpacing(24)
        self.layout.addLayout(bottom_btns_layout)

    def obtener_id_item_seleccionado(self):
        # Devuelve el ID del ítem seleccionado en la tabla (stub para pruebas)
        fila = self.tabla_inventario.currentRow()
        if fila != -1:
            return self.tabla_inventario.item(fila, 0).text()
        return None
