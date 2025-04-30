from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QSizePolicy

class AuditoriaView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label = QLabel("Gestión de Auditorías")
        self.label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(self.label)

        # Tabla de auditorías
        self.tabla_auditorias = QTableWidget()
        self.tabla_auditorias.setColumnCount(6)
        self.tabla_auditorias.setHorizontalHeaderLabels(["ID", "Fecha y Hora", "Usuario", "Módulo", "Tipo de Evento", "Detalle"])
        self.layout.addWidget(self.tabla_auditorias)

        # Botón para filtrar auditorías
        self.boton_filtrar = QPushButton("Filtrar Auditorías")
        self.boton_filtrar.setStyleSheet("background-color: #4caf50; color: white; padding: 10px; border-radius: 5px;")
        self.boton_filtrar.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_filtrar)

        # Botón para exportar auditorías
        self.boton_exportar = QPushButton("Exportar Auditorías")
        self.boton_exportar.setStyleSheet("background-color: #2563eb; color: white; padding: 10px; border-radius: 5px;")
        self.boton_exportar.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_exportar)

        # Botón para exportar auditorías a Excel
        self.boton_exportar_excel = QPushButton("Exportar a Excel")
        self.boton_exportar_excel.setStyleSheet("background-color: #4caf50; color: white; padding: 10px; border-radius: 5px;")
        self.boton_exportar_excel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_exportar_excel)

        # Botón para exportar auditorías a PDF
        self.boton_exportar_pdf = QPushButton("Exportar a PDF")
        self.boton_exportar_pdf.setStyleSheet("background-color: #f44336; color: white; padding: 10px; border-radius: 5px;")
        self.boton_exportar_pdf.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_exportar_pdf)

        self.setLayout(self.layout)

class Auditoria(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel("Vista de Auditoría")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
