from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QHBoxLayout

class HerrajesView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label = QLabel("Gestión de Herrajes")
        self.layout.addWidget(self.label)

        self.form_layout = QFormLayout()
        self.nombre_input = QLineEdit()
        self.cantidad_input = QLineEdit()
        self.proveedor_input = QLineEdit()
        self.form_layout.addRow("Nombre:", self.nombre_input)
        self.form_layout.addRow("Cantidad:", self.cantidad_input)
        self.form_layout.addRow("Proveedor:", self.proveedor_input)
        self.layout.addLayout(self.form_layout)

        self.boton_agregar = QPushButton("Agregar Material")
        self.layout.addWidget(self.boton_agregar)

        self.setLayout(self.layout)

class MaterialesView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Tabla de materiales
        self.tabla_materiales = QTableWidget()
        self.tabla_materiales.setColumnCount(7)
        self.tabla_materiales.setHorizontalHeaderLabels([
            "ID", "Código", "Descripción", "Cantidad", "Ubicación", "Fecha Ingreso", "Observaciones"
        ])
        self.layout.addWidget(self.tabla_materiales)

        # Barra de botones
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton("Agregar Herraje")
        self.boton_modificar = QPushButton("Modificar")
        self.boton_eliminar = QPushButton("Eliminar")
        self.boton_buscar = QPushButton("Buscar")
        self.boton_exportar_excel = QPushButton("Exportar Excel")
        self.boton_exportar_pdf = QPushButton("Exportar PDF")
        self.boton_ver_movimientos = QPushButton("Ver Movimientos")

        botones = [
            self.boton_agregar, self.boton_modificar, self.boton_eliminar,
            self.boton_buscar, self.boton_exportar_excel, self.boton_exportar_pdf,
            self.boton_ver_movimientos
        ]

        for boton in botones:
            botones_layout.addWidget(boton)

        self.layout.addLayout(botones_layout)
        self.setLayout(self.layout)
