from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QTabWidget, QDialog, QMessageBox, QInputDialog, QCheckBox, QScrollArea, QHeaderView, QMenu
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt
import json
from modules.materiales.view import MaterialesView
from modules.vidrios.view import VidriosView

class AjustarStockDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajustar Stock")
        self.setFixedSize(700, 400)  # Hacer la ventana más ancha
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Aplicar estilo general a la ventana
        self.setStyleSheet("""
            QDialog {
                background-color: #f9f9f9;
                border-radius: 10px;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 12px;
                color: #333333;
                font-weight: bold;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-size: 12px;
                border-radius: 5px;
                padding: 5px 10px;
                width: 200px;
                height: 25px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QTableWidget {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                font-weight: bold;
                border: 1px solid #cccccc;
            }
        """)

        # Campo para ingresar el código del material y mostrar la descripción
        input_layout = QHBoxLayout()
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Ingrese el código del material")
        self.codigo_input.textChanged.connect(self.mostrar_descripcion)
        input_layout.addWidget(QLabel("Código del Material:"))
        input_layout.addWidget(self.codigo_input)

        self.descripcion_label = QLabel("Descripción: -")
        input_layout.addWidget(self.descripcion_label)

        layout.addLayout(input_layout)

        # Botón para agregar el material a la lista
        self.agregar_button = QPushButton("Agregar a la Lista")
        self.agregar_button.setFixedSize(200, 25)
        self.agregar_button.clicked.connect(self.agregar_a_lista)
        layout.addWidget(self.agregar_button)

        # Tabla para mostrar los materiales a ajustar
        self.tabla_ajustes = QTableWidget()
        self.tabla_ajustes.setColumnCount(3)
        self.tabla_ajustes.setHorizontalHeaderLabels(["Código", "Descripción", "Cantidad"])
        layout.addWidget(self.tabla_ajustes)

        # Botón para cargar el stock
        self.cargar_button = QPushButton("Cargar Stock")
        self.cargar_button.setFixedSize(200, 25)
        self.cargar_button.clicked.connect(self.cargar_stock)
        layout.addWidget(self.cargar_button)

        self.lista_ajustes = []  # Lista para almacenar los ajustes temporales

    def mostrar_descripcion(self):
        codigo = self.codigo_input.text()
        descripcion = next(
            (
                self.parent().tabla_inventario.item(row, 2).text()
                for row in range(self.parent().tabla_inventario.rowCount())
                if self.parent().tabla_inventario.item(row, 1) and self.parent().tabla_inventario.item(row, 1).text() == codigo
            ),
            "-"
        )
        self.descripcion_label.setText(f"Descripción: {descripcion}")

    def agregar_a_lista(self):
        codigo = self.codigo_input.text()
        descripcion = self.descripcion_label.text().replace("Descripción: ", "")

        if not codigo or descripcion == "-":
            QMessageBox.warning(self, "Advertencia", "Por favor, ingrese un código válido.")
            return

        cantidad, ok = QInputDialog.getInt(self, "Cantidad", "Ingrese la cantidad a ajustar:")
        if not ok or cantidad <= 0:
            QMessageBox.warning(self, "Advertencia", "Cantidad inválida.")
            return

        self.lista_ajustes.append((codigo, descripcion, cantidad))

        # Agregar a la tabla de ajustes
        row_position = self.tabla_ajustes.rowCount()
        self.tabla_ajustes.insertRow(row_position)
        for col, value in enumerate([codigo, descripcion, str(cantidad)]):
            self.tabla_ajustes.setItem(row_position, col, QTableWidgetItem(value))

    def cargar_stock(self):
        if not self.lista_ajustes:
            QMessageBox.warning(self, "Advertencia", "No hay ajustes para cargar.")
            return

        inventario_items = {
            self.parent().tabla_inventario.item(row, 1).text(): row
            for row in range(self.parent().tabla_inventario.rowCount())
            if self.parent().tabla_inventario.item(row, 1)
        }

        for codigo, _, cantidad in self.lista_ajustes:
            if codigo in inventario_items:
                row = inventario_items[codigo]
                item_stock = self.parent().tabla_inventario.item(row, 11)
                stock_actual = int(item_stock.text()) if item_stock and item_stock.text().isdigit() else 0
                nuevo_stock = stock_actual + cantidad
                self.parent().tabla_inventario.setItem(row, 11, QTableWidgetItem(str(nuevo_stock)))

        QMessageBox.information(self, "Éxito", "El stock ha sido actualizado correctamente.")
        self.lista_ajustes.clear()
        self.tabla_ajustes.setRowCount(0)

class InventarioView(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Crear QTabWidget
        self.tab_widget = QTabWidget()

        # Crear pestañas
        self.tab_general = QWidget()
        self.tab_detalles = QWidget()

        # Configurar contenido de la pestaña "General"
        general_layout = QVBoxLayout(self.tab_general)

        # Identificar la tabla
        general_layout.addWidget(QLabel("Tabla de Inventario", alignment=Qt.AlignmentFlag.AlignCenter))

        # Tabla de inventario
        self.tabla_inventario = QTableWidget()
        columnas = [
            "ID", "Código", "Descripción", "Acabado", "Documento", "Proveedor",
            "Dimensiones", "Unidades", "Pedido", "Importe", "Ubicación", "Stock", "Stock Mínimo", "Estado"
        ]
        self.tabla_inventario.setColumnCount(len(columnas))
        self.tabla_inventario.setHorizontalHeaderLabels(columnas)
        self.tabla_inventario.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_inventario.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdcdc;
                background-color: #f9f9f9;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                font-weight: bold;
                border: 1px solid #dcdcdc;
            }
        """)

        # Configurar columnas visibles por defecto
        columnas_visibles = ["Código", "Descripción", "Tiras Necesarias", "Stock", "Pedido"]
        for i, columna in enumerate(columnas):
            if columna not in columnas_visibles:
                self.tabla_inventario.setColumnHidden(i, True)

        # Agregar opción para mostrar/ocultar columnas
        self.tabla_inventario.horizontalHeader().sectionClicked.connect(self.mostrar_menu_columnas)

        general_layout.addWidget(self.tabla_inventario)

        # Botones
        botones_layout = QHBoxLayout()
        botones = [
            QPushButton("Nuevo Ítem"),
            QPushButton("Ver Movimientos"),
            QPushButton("Reservar"),
            QPushButton("Exportar a Excel"),
            QPushButton("Exportar a PDF"),
            QPushButton("Buscar"),
            QPushButton("Generar QR"),
            QPushButton("Actualizar Inventario")
        ]

        # Asignar íconos y tooltips
        botones[0].setIcon(QtGui.QIcon("img/plus_icon.png"))  # Ícono de '+'
        botones[0].setToolTip("<b>Nuevo Ítem</b>: Agregar un nuevo ítem al inventario")
        botones[0].setStyleSheet(botones[0].styleSheet() + """
            QToolTip {
                background-color: #f0f0f0;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 10px;
            }
        """)

        botones[3].setIcon(QtGui.QIcon("img/excel_icon.png"))  # Ícono de Excel
        botones[3].setToolTip("<b>Exportar a Excel</b>: Exportar el inventario a un archivo Excel")

        botones[4].setIcon(QtGui.QIcon("img/pdf_icon.png"))  # Ícono de PDF
        botones[4].setToolTip("<b>Exportar a PDF</b>: Exportar el inventario a un archivo PDF")

        # Ajustar los botones para que solo muestren íconos
        botones[0].setText("")  # Eliminar texto del botón
        botones[3].setText("")
        botones[4].setText("")
        botones[5].setText("")
        botones[6].setText("")
        botones[7].setText("")

        # Ajustar el tamaño de los botones
        for boton in botones:
            boton.setFixedSize(100, 23)

        # Ajustar el tamaño de la fuente de los botones
        for boton in botones:
            boton.setStyleSheet("""
                QPushButton {
                    font-size: 8px; /* Tamaño de letra */
                    border-radius: 15px;
                    background-color: #2563eb; /* Azul */
                    color: white; /* Texto blanco */
                    text-align: center; /* Centrar texto */
                    border: none;
                    font-weight: bold; /* Negrita */
                    border-radius: 8px; /* Bordes redondeados */
                }
                QPushButton:hover {
                    background-color: #1e40af; /* Azul más oscuro */
                }
                QPushButton:pressed {
                    background-color: #1e3a8a; /* Azul aún más oscuro */
                }
            """)
            botones_layout.addWidget(boton)

        # Conectar el botón "Ajustar Stock" directamente
        self.boton_ajustar_stock = QPushButton("Ajustar Stock")
        self.boton_ajustar_stock.setFixedSize(200, 30)
        self.boton_ajustar_stock.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                border-radius: 15px;
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                text-align: center; /* Centrar texto */
                border: none;
                font-size: 14px; /* Tamaño de letra */
                font-weight: bold; /* Negrita */
                border-radius: 8px; /* Bordes redondeados */
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        self.boton_ajustar_stock.setText("")
        self.boton_ajustar_stock.setIcon(QtGui.QIcon("img/refresh_icon.png"))
        self.boton_ajustar_stock.clicked.connect(self.abrir_ajustar_stock_dialog)
        botones_layout.addWidget(self.boton_ajustar_stock)

        general_layout.addLayout(botones_layout)

        # Configurar contenido de la pestaña "Detalles"
        detalles_layout = QVBoxLayout(self.tab_detalles)

        # Tabla en la pestaña "Detalles"
        self.tabla_detalles = QTableWidget()
        self.tabla_detalles.setColumnCount(len(columnas))
        self.tabla_detalles.setHorizontalHeaderLabels(columnas)
        self.tabla_detalles.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_detalles.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdcdc;
                background-color: #f9f9f9;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                font-weight: bold;
                border: 1px solid #dcdcdc;
            }
        """)
        detalles_layout.addWidget(QLabel("Detalles del Inventario", alignment=Qt.AlignmentFlag.AlignCenter))
        detalles_layout.addWidget(self.tabla_detalles)

        # Agregar pestañas al QTabWidget
        self.tab_widget.addTab(self.tab_general, "General")
        self.tab_widget.addTab(self.tab_detalles, "Detalles")

        # Crear pestañas adicionales para Materiales y Vidrios
        self.tab_materiales = MaterialesView()
        self.tab_vidrios = VidriosView()

        # Agregar las pestañas al QTabWidget
        self.tab_widget.addTab(self.tab_materiales, "Materiales")
        self.tab_widget.addTab(self.tab_vidrios, "Vidrios")

        # Agregar QTabWidget al layout principal
        layout.addWidget(self.tab_widget)

        # Agregar un QLabel para mostrar mensajes de estado o error
        self.label_estado = QLabel()
        self.label_estado.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.label_estado)

        # Ajustar el layout principal
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)

    def mostrar_menu_columnas(self, index):
        menu = QMenu(self)
        for i, columna in enumerate(self.tabla_inventario.horizontalHeaderLabels()):
            accion = menu.addAction(columna)
            accion.setCheckable(True)
            accion.setChecked(not self.tabla_inventario.isColumnHidden(i))
            accion.triggered.connect(lambda checked, col=i: self.tabla_inventario.setColumnHidden(col, not checked))

        menu.exec(QtGui.QCursor.pos())

    def abrir_ajustar_stock_dialog(self):
        dialog = AjustarStockDialog(self)
        dialog.exec()
        return dialog

    def abrir_formulario_nuevo_item(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nuevo Ítem")

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.codigo_input = QLineEdit()
        self.nombre_input = QLineEdit()
        self.cantidad_input = QLineEdit()
        self.ubicacion_input = QLineEdit()
        self.tipo_input = QLineEdit()
        self.proveedor_input = QLineEdit()
        self.observaciones_input = QLineEdit()

        form_layout.addRow("Código:", self.codigo_input)
        form_layout.addRow("Nombre:", self.nombre_input)
        form_layout.addRow("Cantidad:", self.cantidad_input)
        form_layout.addRow("Ubicación:", self.ubicacion_input)
        form_layout.addRow("Tipo:", self.tipo_input)
        form_layout.addRow("Proveedor:", self.proveedor_input)
        form_layout.addRow("Observaciones:", self.observaciones_input)

        layout.addLayout(form_layout)

        botones_layout = QHBoxLayout()
        guardar_button = QPushButton("Guardar")
        cancelar_button = QPushButton("Cancelar")
        botones_layout.addWidget(guardar_button)
        botones_layout.addWidget(cancelar_button)

        layout.addLayout(botones_layout)
        dialog.setLayout(layout)

        guardar_button.clicked.connect(lambda: self.guardar_nuevo_item(dialog))
        cancelar_button.clicked.connect(dialog.reject)

        dialog.exec()

    def guardar_nuevo_item(self, dialog):
        datos = {
            "codigo": self.codigo_input.text(),
            "nombre": self.nombre_input.text(),
            "cantidad": self.cantidad_input.text(),
            "ubicacion": self.ubicacion_input.text(),
            "tipo": self.tipo_input.text(),
            "proveedor": self.proveedor_input.text(),
            "observaciones": self.observaciones_input.text()
        }
        dialog.accept()
        return datos

    def abrir_configuracion_columnas(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Configurar Columnas")
        dialog.setFixedSize(400, 300)

        layout = QVBoxLayout(dialog)
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.checkboxes = []
        columnas = [
            "ID", "Código", "Descripción", "Acabado", "Documento", "Proveedor",
            "Dimensiones", "Unidades", "Pedido", "Importe", "Ubicación", "Stock", "Stock Mínimo", "Estado"
        ]

        for i, columna in enumerate(columnas):
            checkbox = QCheckBox(columna)
            checkbox.setChecked(self.columnas_visibles[i])
            self.checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        guardar_button = QPushButton("Guardar")
        guardar_button.clicked.connect(lambda: self.guardar_configuracion_columnas(dialog))
        layout.addWidget(guardar_button)

        dialog.setLayout(layout)
        dialog.exec()

    def guardar_configuracion_columnas(self, dialog):
        self.columnas_visibles = [checkbox.isChecked() for checkbox in self.checkboxes]
        for i, visible in enumerate(self.columnas_visibles):
            self.tabla_inventario.setColumnHidden(i, not visible)

        # Guardar configuración en un archivo JSON
        with open("config_columnas.json", "w") as file:
            json.dump(self.columnas_visibles, file)

        dialog.accept()

    def cargar_configuracion_columnas(self):
        try:
            with open("config_columnas.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return [True] * 14  # Todas las columnas visibles por defecto

    def resaltar_items_bajo_stock(self):
        for row in range(self.tabla_inventario.rowCount()):
            stock_item = self.tabla_inventario.item(row, 11)  # Assuming column 11 is "Stock"
            stock_min_item = self.tabla_inventario.item(row, 12)  # Assuming column 12 is "Stock Mínimo"

            if stock_item and stock_min_item:
                try:
                    stock = int(stock_item.text())
                    stock_min = int(stock_min_item.text())
                    if stock < stock_min:
                        for col in range(self.tabla_inventario.columnCount()):
                            self.tabla_inventario.item(row, col).setBackground(QtGui.QColor("#ffcccc"))  # Light red
                except ValueError:
                    continue

    def llenar_tabla(self, datos):
        """Llena la tabla de inventario con los datos proporcionados."""
        self.tabla_inventario.setRowCount(0)  # Limpiar la tabla
        for row_idx, row_data in enumerate(datos):
            self.tabla_inventario.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                self.tabla_inventario.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
