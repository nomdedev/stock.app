from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QSizePolicy, QMessageBox

class LogisticaView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label = QLabel("Gestión de Logística")
        self.label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(self.label)

        # Formulario de entrada
        self.form_layout = QFormLayout()
        self.destino_input = QLineEdit()
        self.fecha_programada_input = QLineEdit()
        self.estado_input = QLineEdit()
        self.vehiculo_input = QLineEdit()
        self.chofer_input = QLineEdit()
        self.form_layout.addRow("Destino:", self.destino_input)
        self.form_layout.addRow("Fecha Programada:", self.fecha_programada_input)
        self.form_layout.addRow("Estado:", self.estado_input)
        self.form_layout.addRow("Vehículo:", self.vehiculo_input)
        self.form_layout.addRow("Chofer:", self.chofer_input)
        self.layout.addLayout(self.form_layout)

        # Botón estilizado para agregar entrega
        self.boton_agregar = QPushButton("Agregar Entrega")
        self.boton_agregar.setStyleSheet("background-color: #2563eb; color: white; padding: 10px; border-radius: 5px;")
        self.boton_agregar.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_agregar)

        # Tabla de entregas
        self.tabla_entregas = QTableWidget()
        self.tabla_entregas.setColumnCount(5)
        self.tabla_entregas.setHorizontalHeaderLabels(["Destino", "Fecha", "Estado", "Vehículo", "Chofer"])
        self.layout.addWidget(self.tabla_entregas)

        # Botón para actualizar estado
        self.boton_actualizar_estado = QPushButton("Actualizar Estado")
        self.boton_actualizar_estado.setStyleSheet("background-color: #2563eb; color: white; padding: 10px; border-radius: 5px;")
        self.boton_actualizar_estado.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_actualizar_estado)

        # Tabla de checklist
        self.tabla_checklist = QTableWidget()
        self.tabla_checklist.setColumnCount(4)
        self.tabla_checklist.setHorizontalHeaderLabels(["Ítem", "Estado", "Observaciones", "Acción"])
        self.layout.addWidget(self.tabla_checklist)

        # Botones adicionales
        self.botones_layout = QVBoxLayout()
        self.boton_agregar_checklist = QPushButton("Agregar Ítem al Checklist")
        self.boton_agregar_checklist.setStyleSheet("background-color: #2563eb; color: white; padding: 10px; border-radius: 5px;")
        self.boton_agregar_checklist.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.botones_layout.addWidget(self.boton_agregar_checklist)

        self.boton_exportar_excel = QPushButton("Exportar Historial a Excel")
        self.boton_exportar_excel.setStyleSheet("background-color: #2563eb; color: white; padding: 10px; border-radius: 5px;")
        self.boton_exportar_excel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.botones_layout.addWidget(self.boton_exportar_excel)

        self.boton_exportar_pdf = QPushButton("Exportar Historial a PDF")
        self.boton_exportar_pdf.setStyleSheet("background-color: #2563eb; color: white; padding: 10px; border-radius: 5px;")
        self.boton_exportar_pdf.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.botones_layout.addWidget(self.boton_exportar_pdf)

        self.boton_exportar_acta = QPushButton("Exportar Acta de Entrega")
        self.boton_exportar_acta.setStyleSheet("background-color: #2563eb; color: white; padding: 10px; border-radius: 5px;")
        self.boton_exportar_acta.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.botones_layout.addWidget(self.boton_exportar_acta)

        self.boton_generar_hoja_ruta = QPushButton("Generar Hoja de Ruta")
        self.boton_generar_hoja_ruta.setStyleSheet("background-color: #2563eb; color: white; padding: 10px; border-radius: 5px;")
        self.boton_generar_hoja_ruta.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.botones_layout.addWidget(self.boton_generar_hoja_ruta)

        self.boton_exportar_acta.clicked.connect(self.exportar_acta_placeholder)
        self.boton_generar_hoja_ruta.clicked.connect(self.generar_hoja_ruta_placeholder)

    def exportar_acta_placeholder(self):
        QMessageBox.information(self, "En desarrollo", "La función 'Exportar Acta de Entrega' está en desarrollo.")

    def generar_hoja_ruta_placeholder(self):
        QMessageBox.information(self, "En desarrollo", "La función 'Generar Hoja de Ruta' está en desarrollo.")
