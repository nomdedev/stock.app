from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QTabWidget, QDialog, QMessageBox, QInputDialog, QCheckBox, QScrollArea, QHeaderView, QMenu, QSizePolicy, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor, QAction, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize
import json
import os
import pyodbc
from functools import partial
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

    def __init__(self, db_connection=None, usuario_actual="default"):
        super().__init__()
        self.setObjectName("InventarioView")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.layout.setSpacing(16)  # Cambiar a un valor mayor para mejor visibilidad

        self.db_connection = db_connection
        self.usuario_actual = usuario_actual

        # Título
        self.label_titulo = QLabel("INVENTORY")
        self.layout.addWidget(self.label_titulo)

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
            btn.setIcon(QIcon(f"img/{icono}"))
            btn.setIconSize(QSize(24, 24))
            btn.setToolTip(tooltip)
            btn.setText("")
            btn.clicked.connect(signal.emit)
            top_btns_layout.addWidget(btn)
        self.layout.addLayout(top_btns_layout)  # Cambiar insertLayout por addLayout para asegurar el orden

        # Obtener headers desde la base de datos
        self.inventario_headers = self.obtener_headers_desde_db("inventario_perfiles")
        self.tabla_inventario = QTableWidget()
        self.tabla_inventario.setColumnCount(len(self.inventario_headers))
        self.tabla_inventario.setHorizontalHeaderLabels(self.inventario_headers)
        self.tabla_inventario.setAlternatingRowColors(True)
        self.tabla_inventario.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_inventario.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_inventario.verticalHeader().setVisible(False)
        self.tabla_inventario.horizontalHeader().setHighlightSections(False)
        self.tabla_inventario.setShowGrid(False)
        self.tabla_inventario.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabla_inventario.setMinimumHeight(500)  # <-- Aumenta la altura mínima de la tabla
        self.tabla_inventario.setMinimumWidth(1200)  # <-- Aumenta el ancho mínimo de la tabla
        self.tabla_inventario.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # <-- Hace que las columnas ocupen todo el ancho
        self.layout.addWidget(self.tabla_inventario)

        self.layout.addStretch()  # Asegura que la tabla se vea correctamente

        # Cargar configuración de columnas visibles
        self.config_path = f"config_inventario_columns_{self.usuario_actual}.json"
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

        # Menú contextual para mostrar/ocultar columnas
        self.tabla_inventario.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabla_inventario.customContextMenuRequested.connect(self.mostrar_menu_columnas)

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

    def obtener_headers_desde_db(self, tabla):
        if self.db_connection:
            query = f"SELECT TOP 0 * FROM {tabla}"
            connection_string = (
                f"DRIVER={{{self.db_connection.driver}}};"
                f"SERVER=localhost\\SQLEXPRESS;"
                f"DATABASE={self.db_connection.database};"
                f"UID={self.db_connection.username};"
                f"PWD={self.db_connection.password};"
                f"TrustServerCertificate=yes;"
            )
            with pyodbc.connect(connection_string, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                return [column[0] for column in cursor.description]
        return []

    def cargar_config_columnas(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {header: True for header in self.inventario_headers}

    def guardar_config_columnas(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)

    def aplicar_columnas_visibles(self):
        for idx, header in enumerate(self.inventario_headers):
            visible = self.columnas_visibles.get(header, True)
            self.tabla_inventario.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        menu = QMenu(self)
        for idx, header in enumerate(self.inventario_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        menu.exec(self.tabla_inventario.viewport().mapToGlobal(pos))

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_inventario.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()

    def obtener_id_item_seleccionado(self):
        # Devuelve el ID del ítem seleccionado en la tabla (stub para pruebas)
        fila = self.tabla_inventario.currentRow()
        if fila != -1:
            return self.tabla_inventario.item(fila, 0).text()
        return None

    def cargar_items(self, items):
        # items debe ser una lista de diccionarios con claves iguales a los headers
        self.tabla_inventario.setRowCount(len(items))
        for fila, item in enumerate(items):
            for columna, header in enumerate(self.inventario_headers):
                valor = item.get(header, "")
                self.tabla_inventario.setItem(fila, columna, QTableWidgetItem(str(valor)))
