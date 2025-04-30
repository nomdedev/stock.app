from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget
from PyQt6.QtCore import QTimer

class ContabilidadView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label = QLabel("Gestión de Contabilidad y Recibos")
        self.layout.addWidget(self.label)

        # Formulario para agregar recibo
        self.form_layout = QFormLayout()
        self.fecha_emision_input = QLineEdit()
        self.fecha_emision_input.setFixedWidth(500)
        self.obra_id_input = QLineEdit()
        self.obra_id_input.setFixedWidth(500)
        self.monto_total_input = QLineEdit()
        self.monto_total_input.setFixedWidth(500)
        self.concepto_input = QLineEdit()
        self.concepto_input.setFixedWidth(500)
        self.destinatario_input = QLineEdit()
        self.destinatario_input.setFixedWidth(500)
        self.form_layout.addRow("Fecha de Emisión:", self.fecha_emision_input)
        self.form_layout.addRow("ID de Obra:", self.obra_id_input)
        self.form_layout.addRow("Monto Total:", self.monto_total_input)
        self.form_layout.addRow("Concepto:", self.concepto_input)
        self.form_layout.addRow("Destinatario:", self.destinatario_input)
        self.layout.addLayout(self.form_layout)

        self.boton_agregar_recibo = QPushButton("Agregar Recibo")
        self.layout.addWidget(self.boton_agregar_recibo)

        # Tabla de recibos
        self.tabla_recibos = QTableWidget()
        self.tabla_recibos.setColumnCount(6)
        self.tabla_recibos.setHorizontalHeaderLabels(["ID", "Fecha", "Obra", "Monto", "Concepto", "Estado"])
        self.layout.addWidget(self.tabla_recibos)

        # Timer para refrescar la tabla de recibos cada 3 segundos
        self.timer_refresco = QTimer(self)
        self.timer_refresco.timeout.connect(self.refrescar_tabla_recibos)
        self.timer_refresco.start(3000)

        # Tabla de movimientos contables
        self.tabla_movimientos = QTableWidget()
        self.tabla_movimientos.setColumnCount(5)
        self.tabla_movimientos.setHorizontalHeaderLabels(["Fecha", "Tipo", "Monto", "Concepto", "Observaciones"])
        self.layout.addWidget(self.tabla_movimientos)

        self.setLayout(self.layout)
        self.controller = None

    def inicializar_botones(self):
        self.boton_generar_pdf = QPushButton("Generar Recibo en PDF")
        self.layout.addWidget(self.boton_generar_pdf)

        self.boton_exportar_excel = QPushButton("Exportar Balance a Excel")
        self.layout.addWidget(self.boton_exportar_excel)

        self.boton_exportar_pdf = QPushButton("Exportar Balance a PDF")
        self.layout.addWidget(self.boton_exportar_pdf)

        self.boton_generar_firma = QPushButton("Generar Firma Digital")
        self.layout.addWidget(self.boton_generar_firma)

        self.boton_verificar_firma = QPushButton("Verificar Firma Digital")
        self.layout.addWidget(self.boton_verificar_firma)

    def refrescar_tabla_recibos(self):
        if self.controller:
            self.controller.actualizar_tabla_recibos()
