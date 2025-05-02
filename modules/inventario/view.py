from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QTabWidget, QDialog, QMessageBox, QInputDialog, QCheckBox, QScrollArea, QHeaderView, QMenu
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt
import json

class AjustarStockDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajustar Stock")
        self.setFixedSize(600, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Campo para ingresar el código del material
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Ingrese el código del material")
        layout.addWidget(QLabel("Código del Material:"))
        layout.addWidget(self.codigo_input)

        # Botón para buscar el material
        self.buscar_button = QPushButton("Buscar")
        self.buscar_button.clicked.connect(self.buscar_material)
        layout.addWidget(self.buscar_button)

        # Tabla para mostrar los materiales a ajustar
        self.tabla_ajustes = QTableWidget()
        self.tabla_ajustes.setColumnCount(3)
        self.tabla_ajustes.setHorizontalHeaderLabels(["Código", "Descripción", "Cantidad"])
        layout.addWidget(self.tabla_ajustes)

        # Botones para agregar y aceptar ajustes
        botones_layout = QHBoxLayout()
        self.agregar_button = QPushButton("Agregar a la Lista")
        self.agregar_button.clicked.connect(self.agregar_a_lista)
        self.cargar_button = QPushButton("Cargar Stock")
        self.cargar_button.clicked.connect(self.cargar_stock)
        botones_layout.addWidget(self.agregar_button)
        botones_layout.addWidget(self.cargar_button)
        layout.addLayout(botones_layout)

        self.lista_ajustes = []  # Lista para almacenar los ajustes temporales

    def buscar_material(self):
        codigo = self.codigo_input.text()
        if not codigo:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingrese un código de material.")
            return

        # Buscar el material en la tabla de inventario
        for row in range(self.parent().tabla_inventario.rowCount()):
            item_codigo = self.parent().tabla_inventario.item(row, 1)  # Columna de código
            item_descripcion = self.parent().tabla_inventario.item(row, 2)  # Columna de descripción
            if item_codigo and item_codigo.text() == codigo:
                descripcion = item_descripcion.text() if item_descripcion else ""
                QMessageBox.information(self, "Material Encontrado", f"Descripción: {descripcion}")
                return

        QMessageBox.warning(self, "No Encontrado", "El código ingresado no existe en el inventario.")

    def agregar_a_lista(self):
        codigo = self.codigo_input.text()
        if not codigo:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingrese un código de material.")
            return

        cantidad, ok = QInputDialog.getInt(self, "Cantidad", "Ingrese la cantidad a ajustar:")
        if not ok or cantidad <= 0:
            QMessageBox.warning(self, "Advertencia", "Cantidad inválida.")
            return

        # Buscar el material en la tabla de inventario
        for row in range(self.parent().tabla_inventario.rowCount()):
            item_codigo = self.parent().tabla_inventario.item(row, 1)  # Columna de código
            item_descripcion = self.parent().tabla_inventario.item(row, 2)  # Columna de descripción
            if item_codigo and item_codigo.text() == codigo:
                descripcion = item_descripcion.text() if item_descripcion else ""
                self.lista_ajustes.append((codigo, descripcion, cantidad))

                # Agregar a la tabla de ajustes
                row_position = self.tabla_ajustes.rowCount()
                self.tabla_ajustes.insertRow(row_position)
                self.tabla_ajustes.setItem(row_position, 0, QTableWidgetItem(codigo))
                self.tabla_ajustes.setItem(row_position, 1, QTableWidgetItem(descripcion))
                self.tabla_ajustes.setItem(row_position, 2, QTableWidgetItem(str(cantidad)))
                QMessageBox.information(self, "Agregado", "El material ha sido agregado a la lista de ajustes.")
                return

        QMessageBox.warning(self, "No Encontrado", "El código ingresado no existe en el inventario.")

    def cargar_stock(self):
        if not self.lista_ajustes:
            QMessageBox.warning(self, "Advertencia", "No hay ajustes para cargar.")
            return

        # Actualizar la tabla de inventario
        for codigo, descripcion, cantidad in self.lista_ajustes:
            for row in range(self.parent().tabla_inventario.rowCount()):
                item_codigo = self.parent().tabla_inventario.item(row, 1)  # Columna de código
                item_stock = self.parent().tabla_inventario.item(row, 11)  # Columna de stock
                if item_codigo and item_codigo.text() == codigo:
                    nuevo_stock = int(item_stock.text()) + cantidad
                    self.parent().tabla_inventario.setItem(row, 11, QTableWidgetItem(str(nuevo_stock)))

        QMessageBox.information(self, "Éxito", "El stock ha sido actualizado correctamente.")
        self.lista_ajustes.clear()
        self.tabla_ajustes.setRowCount(0)  # Limpiar la tabla de ajustes

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

        # Eliminar la primera columna automática
        self.tabla_inventario.setColumnHidden(0, True)

        # Conectar clic en los encabezados para mostrar menú
        self.tabla_inventario.horizontalHeader().sectionClicked.connect(self.mostrar_menu_columnas)

        general_layout.addWidget(self.tabla_inventario)

        # Botones
        botones_layout = QHBoxLayout()
        botones = [
            QPushButton("Nuevo Ítem"),
            QPushButton("Ver Movimientos"),
            QPushButton("Reservar"),
            QPushButton("Ajustar Stock"),
            QPushButton("Exportar a Excel"),
            QPushButton("Exportar a PDF"),
            QPushButton("Buscar"),
            QPushButton("Generar QR"),
            QPushButton("Actualizar Inventario")
        ]

        for boton in botones:
            boton.setFixedSize(200, 30)
            boton.setStyleSheet("""
                QPushButton {
                    font-size: 10px;
                    border-radius: 15px;
                    background-color: #0078d7;
                    color: white;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #005a9e;
                }
            """)
            botones_layout.addWidget(boton)

        # Conectar el botón "Ajustar Stock" al diálogo
        for boton in self.findChildren(QPushButton):
            if boton.text() == "Ajustar Stock":
                boton.clicked.connect(self.abrir_ajustar_stock_dialog)

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

        # Agregar QTabWidget al layout principal
        layout.addWidget(self.tab_widget)

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
        columnas = [
            "ID", "Código", "Descripción", "Acabado", "Documento", "Proveedor",
            "Dimensiones", "Unidades", "Pedido", "Importe", "Ubicación", "Stock", "Stock Mínimo", "Estado"
        ]

        for i, columna in enumerate(columnas):
            accion = menu.addAction(columna)
            accion.setCheckable(True)
            accion.setChecked(not self.tabla_inventario.isColumnHidden(i))
            accion.triggered.connect(lambda checked, col=i: self.tabla_inventario.setColumnHidden(col, not checked))

        menu.exec(QtGui.QCursor.pos())

    def abrir_ajustar_stock_dialog(self):
        dialog = AjustarStockDialog(self)
        dialog.exec()

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
            for col in range(self.tabla_inventario.columnCount()):
                item = self.tabla_inventario.item(row, col)
                if item and item.text() == "Bajo Stock":  # Suponiendo que hay una columna que indica el estado
                    item.setBackground(QtGui.QColor("red"))

    def set_modo_lectura(self, activar):
        # Deshabilitar botones
        for boton in self.findChildren(QPushButton):
            boton.setDisabled(activar)

        # Deshabilitar campos de entrada
        for campo in self.findChildren(QLineEdit):
            campo.setDisabled(activar)

    def obtener_datos_nuevo_item(self):
        """Obtiene los datos del nuevo ítem desde los campos de entrada."""
        # Aquí puedes agregar los campos necesarios para el nuevo ítem
        codigo = self.buscar_input.text()
        descripcion = "Descripción de ejemplo"  # Reemplazar con el campo real
        cantidad = 10  # Reemplazar con el campo real

        if codigo and descripcion and cantidad:
            return {
                "codigo": codigo,
                "descripcion": descripcion,
                "cantidad": cantidad
            }
        else:
            return None

    def obtener_id_item_seleccionado(self):
        """Obtiene el ID del ítem seleccionado en la tabla de inventario."""
        fila_seleccionada = self.tabla_inventario.currentRow()
        if fila_seleccionada != -1:
            id_item = self.tabla_inventario.item(fila_seleccionada, 0).text()
            return id_item
        else:
            return None

class Inventario(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel("Vista de Inventario")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    ventana_inventario = InventarioView()
    ventana_inventario.setWindowTitle("Inventario - Vista Independiente")
    ventana_inventario.resize(1200, 800)
    ventana_inventario.show()
    sys.exit(app.exec())
