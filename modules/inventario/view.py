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
        bottom_btns_layout.setSpacing(20)
        bottom_btns_layout.setContentsMargins(40, 10, 40, 40)

        def aplicar_sombra(widget):
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(15)
            sombra.setXOffset(0)
            sombra.setYOffset(4)
            sombra.setColor(QColor(0, 0, 0, 50))
            widget.setGraphicsEffect(sombra)

        # Botón Refresh (solo icono)
        self.boton_refresh = QPushButton()
        self.boton_refresh.setIcon(QtGui.QIcon("img/refresh_icon.svg"))
        self.boton_refresh.setIconSize(QSize(24, 24))
        self.boton_refresh.setToolTip("Recargar la tabla de inventario")
        self.boton_refresh.setText("")
        self.boton_refresh.setFixedSize(48, 48)
        self.boton_refresh.setStyleSheet("")
        aplicar_sombra(self.boton_refresh)
        self.boton_refresh.clicked.connect(self.actualizar_signal.emit)
        bottom_btns_layout.addWidget(self.boton_refresh)

        # Botón Adjust Stock (solo icono)
        self.boton_ajustar_stock = QPushButton()
        self.boton_ajustar_stock.setIcon(QtGui.QIcon("img/settings_icon.svg"))
        self.boton_ajustar_stock.setIconSize(QSize(24, 24))
        self.boton_ajustar_stock.setToolTip("Ajustar stock manualmente")
        self.boton_ajustar_stock.setText("")
        self.boton_ajustar_stock.setFixedSize(48, 48)
        self.boton_ajustar_stock.setStyleSheet("")
        aplicar_sombra(self.boton_ajustar_stock)
        self.boton_ajustar_stock.clicked.connect(self.ajustar_stock_signal.emit)
        bottom_btns_layout.addWidget(self.boton_ajustar_stock)

        # Botón View Details (solo icono)
        self.boton_ver_detalles = QPushButton()
        self.boton_ver_detalles.setIcon(QtGui.QIcon("img/search_icon.svg"))
        self.boton_ver_detalles.setIconSize(QSize(24, 24))
        self.boton_ver_detalles.setToolTip("Ver detalles del ítem seleccionado")
        self.boton_ver_detalles.setText("")
        self.boton_ver_detalles.setFixedSize(48, 48)
        self.boton_ver_detalles.setStyleSheet("")
        aplicar_sombra(self.boton_ver_detalles)
        self.boton_ver_detalles.clicked.connect(self.ver_movimientos_signal.emit)
        bottom_btns_layout.addWidget(self.boton_ver_detalles)

        # Botón Reserve (solo icono)
        self.boton_reservar = QPushButton()
        self.boton_reservar.setIcon(QtGui.QIcon("img/calendar-plus.svg"))
        self.boton_reservar.setIconSize(QSize(24, 24))
        self.boton_reservar.setToolTip("Reservar ítem para obra")
        self.boton_reservar.setText("")
        self.boton_reservar.setFixedSize(48, 48)
        self.boton_reservar.setStyleSheet("")
        aplicar_sombra(self.boton_reservar)
        self.boton_reservar.clicked.connect(self.reservar_signal.emit)
        bottom_btns_layout.addWidget(self.boton_reservar)

        bottom_btns_layout.addStretch()
        self.layout.addSpacing(24)
        self.layout.addLayout(bottom_btns_layout)

        # Cargar el stylesheet visual moderno para Inventario según el tema activo
        try:
            with open("themes/light.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

    def obtener_id_item_seleccionado(self):
        # Devuelve el ID del ítem seleccionado en la tabla (stub para pruebas)
        fila = self.tabla_inventario.currentRow()
        if fila != -1:
            return self.tabla_inventario.item(fila, 0).text()
        return None
