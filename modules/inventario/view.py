from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QTabWidget, QDialog, QMessageBox, QInputDialog, QCheckBox, QScrollArea, QHeaderView, QMenu, QSizePolicy, QGraphicsDropShadowEffect
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor
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
        self.setObjectName("InventarioView")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.layout.setSpacing(0)

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
            ("add-material.svg", "Agregar nuevo ítem", self.nuevo_item_signal),
            ("excel_icon.svg", "Exportar a Excel", self.exportar_excel_signal),
            ("pdf_icon.svg", "Exportar a PDF", self.exportar_pdf_signal),
            ("search_icon.svg", "Buscar ítem", self.buscar_signal),
            ("qr_icon.svg", "Generar código QR", self.generar_qr_signal),
        ]
        for icono, tooltip, signal in iconos:
            btn = QPushButton()
            btn.setIcon(QtGui.QIcon(f"img/{icono}"))
            btn.setIconSize(QSize(24, 24))
            btn.setToolTip(tooltip)
            btn.setText("")
            btn.clicked.connect(signal.emit)
            top_btns_layout.addWidget(btn)
        self.layout.insertLayout(1, top_btns_layout)

        # Cargar el stylesheet visual moderno para Inventario según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

    def obtener_id_item_seleccionado(self):
        # Devuelve el ID del ítem seleccionado en la tabla (stub para pruebas)
        fila = self.tabla_inventario.currentRow()
        if fila != -1:
            return self.tabla_inventario.item(fila, 0).text()
        return None
