from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem
from PyQt6 import QtGui
from PyQt6.QtCore import Qt

class InventarioView(QWidget):
    def __init__(self):
        super().__init__()

        self.label = QLabel("Inventario General")

        # Tabla de inventario
        self.tabla_inventario = QTableWidget()
        columnas = [
            "Tipo", "Código", "Descripción", "Acabado", "Documento", "Proveedor",
            "Dimensiones", "Unidades", "Pedido", "Importe", "Ubicación", "Stock", "Stock Mínimo", "Estado"
        ]
        self.tabla_inventario.setColumnCount(len(columnas))
        self.tabla_inventario.setHorizontalHeaderLabels(columnas)
        # Ajustar anchos de columna para parecerse a la imagen
        anchos = [80, 90, 200, 90, 100, 120, 120, 80, 80, 90, 120, 80, 90, 80]
        for i, ancho in enumerate(anchos):
            self.tabla_inventario.setColumnWidth(i, ancho)
        self.tabla_inventario.horizontalHeader().setStyleSheet("")  # Restablecer estilo predeterminado
        self.tabla_inventario.setFixedSize(800, 400)

        # Botones
        self.boton_nuevo_item = QPushButton("Nuevo Ítem")
        self.boton_nuevo_item.setFixedSize(180, 36)
        self.boton_nuevo_item.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 12px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1e40af;
            }
            QPushButton:pressed {
                background-color: #1e3a8a;
            }
        """)

        self.boton_ver_movimientos = QPushButton("Ver Movimientos")
        self.boton_ver_movimientos.setFixedSize(180, 36)
        self.boton_ver_movimientos.setStyleSheet(self.boton_nuevo_item.styleSheet())

        self.boton_reservar = QPushButton("Reservar")
        self.boton_reservar.setFixedSize(180, 36)
        self.boton_reservar.setStyleSheet(self.boton_nuevo_item.styleSheet())

        self.boton_ajustar_stock = QPushButton("Ajustar Stock")
        self.boton_ajustar_stock.setFixedSize(180, 36)
        self.boton_ajustar_stock.setStyleSheet(self.boton_nuevo_item.styleSheet())

        # Botón para exportar inventario a Excel
        self.boton_exportar_excel = QPushButton("Exportar a Excel")
        self.boton_exportar_excel.setFixedSize(180, 36)
        self.boton_exportar_excel.setStyleSheet(self.boton_nuevo_item.styleSheet())

        # Botón para exportar inventario a PDF
        self.boton_exportar_pdf = QPushButton("Exportar a PDF")
        self.boton_exportar_pdf.setFixedSize(180, 36)
        self.boton_exportar_pdf.setStyleSheet(self.boton_nuevo_item.styleSheet())

        # Campo de búsqueda
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar por código...")
        self.buscar_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 8px;
                font-size: 14px;
                background-color: #f8f9fc;
            }
            QLineEdit:focus {
                border: 1px solid #2563eb;
                background-color: #ffffff;
            }
        """)
        self.buscar_input.setFixedSize(400, 40)

        self.boton_buscar = QPushButton("Buscar")
        self.boton_buscar.setFixedSize(180, 36)
        self.boton_buscar.setStyleSheet(self.boton_nuevo_item.styleSheet())

        # Botón para generar QR
        self.boton_generar_qr = QPushButton("Generar QR")
        self.boton_generar_qr.setFixedSize(180, 36)
        self.boton_generar_qr.setStyleSheet(self.boton_nuevo_item.styleSheet())
        self.id_item_input = QLineEdit()
        self.id_item_input.setFixedSize(300, 30)

        self.boton_actualizar = QPushButton("Actualizar Inventario")
        self.boton_actualizar.setFixedSize(180, 36)

        # Tabla de movimientos
        self.tabla_movimientos = QTableWidget()
        self.tabla_movimientos.setColumnCount(4)
        self.tabla_movimientos.setHorizontalHeaderLabels(["Fecha", "Tipo", "Cantidad", "Observaciones"])
        self.tabla_movimientos.setFixedSize(800, 200)

        # Tabla de reservas
        self.tabla_reservas = QTableWidget()
        self.tabla_reservas.setColumnCount(4)
        self.tabla_reservas.setHorizontalHeaderLabels(["Fecha", "Cantidad", "Estado", "Referencia"])
        self.tabla_reservas.setFixedSize(800, 200)

        # Ajustar el diseño para que los elementos se distribuyan horizontalmente y se adapten al ancho de la pantalla
        self.layout = QVBoxLayout()

        # Crear un layout horizontal para la tabla principal y los botones
        contenido_layout = QHBoxLayout()

        # Tabla principal
        tabla_layout = QVBoxLayout()
        tabla_layout.addWidget(self.tabla_inventario)
        contenido_layout.addLayout(tabla_layout)

        # Botones
        botones_layout = QVBoxLayout()
        botones_layout.addWidget(self.boton_nuevo_item)
        botones_layout.addWidget(self.boton_ver_movimientos)
        botones_layout.addWidget(self.boton_reservar)
        botones_layout.addWidget(self.boton_ajustar_stock)
        botones_layout.addWidget(self.boton_exportar_excel)
        botones_layout.addWidget(self.boton_exportar_pdf)
        botones_layout.addWidget(self.buscar_input)
        botones_layout.addWidget(self.boton_buscar)
        botones_layout.addWidget(self.boton_generar_qr)
        contenido_layout.addLayout(botones_layout)

        # Agregar el layout horizontal al layout principal
        self.layout.addLayout(contenido_layout)

        # Tablas adicionales
        self.layout.addWidget(self.tabla_movimientos)
        self.layout.addWidget(self.tabla_reservas)

        self.setLayout(self.layout)
        self.controller = None

    def resaltar_items_bajo_stock(self):
        for row in range(self.tabla_inventario.rowCount()):
            for col in range(self.tabla_inventario.columnCount()):
                item = self.tabla_inventario.item(row, col)
                if item and item.text() == "Bajo Stock":  # Suponiendo que hay una columna que indica el estado
                    item.setBackground(QtGui.QColor("red"))

    def set_modo_lectura(self, activar):
        # Deshabilitar botones
        self.boton_nuevo_item.setDisabled(activar)
        self.boton_ver_movimientos.setDisabled(activar)
        self.boton_reservar.setDisabled(activar)
        self.boton_ajustar_stock.setDisabled(activar)
        self.boton_exportar_excel.setDisabled(activar)
        self.boton_exportar_pdf.setDisabled(activar)
        self.boton_buscar.setDisabled(activar)
        self.boton_generar_qr.setDisabled(activar)

        # Deshabilitar campos de entrada
        self.buscar_input.setDisabled(activar)
        self.id_item_input.setDisabled(activar)

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

    def obtener_datos_reserva(self):
        """Obtiene los datos necesarios para registrar una reserva desde los campos de entrada."""
        fila_seleccionada = self.tabla_inventario.currentRow()
        if fila_seleccionada != -1:
            id_item = self.tabla_inventario.item(fila_seleccionada, 0).text()
            cantidad_reservada = 5  # Reemplazar con el campo real para ingresar la cantidad
            referencia_obra = "Obra de ejemplo"  # Reemplazar con el campo real para ingresar la referencia

            if id_item and cantidad_reservada and referencia_obra:
                return {
                    "id_item": id_item,
                    "cantidad_reservada": cantidad_reservada,
                    "referencia_obra": referencia_obra
                }
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
