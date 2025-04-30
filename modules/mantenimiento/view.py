from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem, QFormLayout, QSizePolicy

class MantenimientoView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Gestión de Mantenimiento")
        self.label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(self.label)

        # Ajustar otros elementos al estilo dashboard
        self.form_layout = QFormLayout()
        self.tipo_objeto_input = QLineEdit()
        self.tipo_objeto_input.setStyleSheet("""
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
        self.tipo_objeto_input.setFixedSize(500, 40)

        self.id_objeto_input = QLineEdit()
        self.id_objeto_input.setStyleSheet(self.tipo_objeto_input.styleSheet())
        self.id_objeto_input.setFixedSize(500, 40)

        self.tipo_mantenimiento_input = QComboBox()
        self.tipo_mantenimiento_input.addItems(["Preventivo", "Correctivo", "Calibración"])
        self.fecha_realizacion_input = QDateEdit()
        self.realizado_por_input = QLineEdit()
        self.realizado_por_input.setStyleSheet(self.tipo_objeto_input.styleSheet())
        self.realizado_por_input.setFixedSize(500, 40)

        self.observaciones_input = QTextEdit()
        self.observaciones_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 8px;
                font-size: 14px;
                background-color: #f8f9fc;
            }
            QTextEdit:focus {
                border: 1px solid #2563eb;
                background-color: #ffffff;
            }
        """)
        self.observaciones_input.setFixedSize(500, 100)

        self.firma_digital_input = QLineEdit()
        self.form_layout.addRow("Tipo de Objeto:", self.tipo_objeto_input)
        self.form_layout.addRow("ID del Objeto:", self.id_objeto_input)
        self.form_layout.addRow("Tipo de Mantenimiento:", self.tipo_mantenimiento_input)
        self.form_layout.addRow("Fecha de Realización:", self.fecha_realizacion_input)
        self.form_layout.addRow("Realizado Por:", self.realizado_por_input)
        self.form_layout.addRow("Observaciones:", self.observaciones_input)
        self.form_layout.addRow("Firma Digital:", self.firma_digital_input)
        self.layout.addLayout(self.form_layout)

        self.boton_agregar_mantenimiento = QPushButton("Agregar Mantenimiento")
        self.boton_agregar_mantenimiento.setStyleSheet("background-color: #2563eb; color: white; padding: 10px; border-radius: 5px;")
        self.boton_agregar_mantenimiento.setFixedWidth(100)
        self.boton_agregar_mantenimiento.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_agregar_mantenimiento)

        # Tabla de herramientas
        self.tabla_herramientas = QTableWidget()
        self.tabla_herramientas.setColumnCount(5)
        self.tabla_herramientas.setHorizontalHeaderLabels(["ID", "Nombre", "Descripción", "Ubicación", "Estado"])
        self.tabla_herramientas.horizontalHeader().setStyleSheet("")
        self.layout.addWidget(self.tabla_herramientas)

        # Tabla de vehículos
        self.tabla_vehiculos = QTableWidget()
        self.tabla_vehiculos.setColumnCount(5)
        self.tabla_vehiculos.setHorizontalHeaderLabels(["ID", "Patente", "Marca", "Modelo", "Estado"])
        self.tabla_vehiculos.horizontalHeader().setStyleSheet("")
        self.layout.addWidget(self.tabla_vehiculos)

        # Tabla de mantenimientos
        self.tabla_mantenimientos = QTableWidget()
        self.tabla_mantenimientos.setColumnCount(6)
        self.tabla_mantenimientos.setHorizontalHeaderLabels(["ID", "Tipo Objeto", "ID Objeto", "Tipo", "Fecha", "Estado"])
        self.tabla_mantenimientos.horizontalHeader().setStyleSheet("")
        self.layout.addWidget(self.tabla_mantenimientos)

        # Tareas recurrentes
        self.boton_ver_tareas_recurrentes = QPushButton("Ver Tareas Recurrentes")
        self.boton_ver_tareas_recurrentes.setFixedWidth(100)
        self.boton_ver_tareas_recurrentes.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_ver_tareas_recurrentes)

        self.tabla_tareas_recurrentes = QTableWidget()
        self.tabla_tareas_recurrentes.setColumnCount(4)
        self.tabla_tareas_recurrentes.setHorizontalHeaderLabels(["ID", "Descripción", "Próxima Fecha", "Responsable"])
        self.tabla_tareas_recurrentes.horizontalHeader().setStyleSheet("")
        self.layout.addWidget(self.tabla_tareas_recurrentes)

        self.inicializar_botones_exportacion()
        self.inicializar_registro_repuestos()

        self.controller = None

    def inicializar_botones_exportacion(self):
        self.boton_exportar_excel = QPushButton("Exportar Historial a Excel")
        self.boton_exportar_excel.setFixedWidth(100)
        self.boton_exportar_excel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_exportar_excel)

        self.boton_exportar_pdf = QPushButton("Exportar Historial a PDF")
        self.boton_exportar_pdf.setFixedWidth(100)
        self.boton_exportar_pdf.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_exportar_pdf)

    def inicializar_registro_repuestos(self):
        self.label_repuestos = QLabel("Registrar Repuestos Utilizados")
        self.layout.addWidget(self.label_repuestos)

        self.id_mantenimiento_input = QLineEdit()
        self.layout.addWidget(QLabel("ID Mantenimiento:"))
        self.layout.addWidget(self.id_mantenimiento_input)

        self.id_item_input = QLineEdit()
        self.layout.addWidget(QLabel("ID Repuesto:"))
        self.layout.addWidget(self.id_item_input)

        self.cantidad_utilizada_input = QLineEdit()
        self.layout.addWidget(QLabel("Cantidad Utilizada:"))
        self.layout.addWidget(self.cantidad_utilizada_input)

        self.boton_registrar_repuesto = QPushButton("Registrar Repuesto")
        self.layout.addWidget(self.boton_registrar_repuesto)

    def mostrar_tareas_recurrentes(self, tareas):
        self.tabla_tareas_recurrentes.setRowCount(len(tareas))
        for row, tarea in enumerate(tareas):
            for col, value in enumerate(tarea):
                self.tabla_tareas_recurrentes.setItem(row, col, QTableWidgetItem(str(value)))
