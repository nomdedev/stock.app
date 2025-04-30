from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QTableWidget, QSizePolicy
from core.ui_components import CustomButton

class ObrasView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label = QLabel("Gestión de Obras")
        self.layout.addWidget(self.label)

        self.form_layout = QFormLayout()
        self.nombre_input = QLineEdit()
        self.nombre_input.setFixedWidth(500)
        self.cliente_input = QLineEdit()
        self.cliente_input.setFixedWidth(500)
        self.estado_input = QLineEdit()
        self.estado_input.setFixedWidth(500)
        self.form_layout.addRow("Nombre:", self.nombre_input)
        self.form_layout.addRow("Cliente:", self.cliente_input)
        self.form_layout.addRow("Estado:", self.estado_input)
        self.layout.addLayout(self.form_layout)

        self.boton_agregar = CustomButton("Agregar Obra")
        self.boton_agregar.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_agregar)

        # Botón para ver cronograma
        self.boton_ver_cronograma = CustomButton("Ver Cronograma")
        self.boton_ver_cronograma.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_ver_cronograma)

        # Botón para asignar materiales
        self.boton_asignar_materiales = CustomButton("Asignar Materiales")
        self.boton_asignar_materiales.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_asignar_materiales)

        # Botón para exportar cronograma a Excel
        self.boton_exportar_excel = CustomButton("Exportar Cronograma a Excel")
        self.boton_exportar_excel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_exportar_excel)

        # Botón para exportar cronograma a PDF
        self.boton_exportar_pdf = CustomButton("Exportar Cronograma a PDF")
        self.boton_exportar_pdf.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_exportar_pdf)

        # Tabla de obras (para seleccionar y ver cronograma)
        self.tabla_obras = QTableWidget()
        self.tabla_obras.setColumnCount(5)
        self.tabla_obras.setHorizontalHeaderLabels(["ID", "Nombre", "Cliente", "Estado", "Acción"])
        self.tabla_obras.horizontalHeader().setStyleSheet("")
        self.layout.addWidget(self.tabla_obras)

        # Tabla de cronograma
        self.tabla_cronograma = QTableWidget()
        self.tabla_cronograma.setColumnCount(6)
        self.tabla_cronograma.setHorizontalHeaderLabels(["Etapa", "Fecha Programada", "Fecha Realizada", "Observaciones", "Responsable", "Estado"])
        self.tabla_cronograma.horizontalHeader().setStyleSheet("")
        self.layout.addWidget(self.tabla_cronograma)

        # Tabla de materiales asignados
        self.tabla_materiales = QTableWidget()
        self.tabla_materiales.setColumnCount(5)
        self.tabla_materiales.setHorizontalHeaderLabels(["Material", "Cantidad Necesaria", "Cantidad Reservada", "Estado", "Acción"])
        self.tabla_materiales.horizontalHeader().setStyleSheet("")
        self.layout.addWidget(self.tabla_materiales)

        self.setLayout(self.layout)

class Obras(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel("Vista de Obras")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
