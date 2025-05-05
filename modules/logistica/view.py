from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QSizePolicy

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
        self.boton_agregar.setStyleSheet("""
            QPushButton {
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
        self.boton_agregar.setFixedHeight(40)  # Altura fija
        self.boton_agregar.setFixedWidth(150)  # Ancho fijo
        self.layout.addWidget(self.boton_agregar)

        # Tabla de entregas
        self.tabla_entregas = QTableWidget()
        self.tabla_entregas.setColumnCount(5)
        self.tabla_entregas.setHorizontalHeaderLabels(["Destino", "Fecha", "Estado", "Vehículo", "Chofer"])
        self.tabla_entregas.horizontalHeader().setStretchLastSection(True)  # Ajustar última columna
        self.layout.addWidget(self.tabla_entregas)

        # Botón para actualizar estado
        self.boton_actualizar_estado = QPushButton("Actualizar Estado")
        self.boton_actualizar_estado.setStyleSheet("""
            QPushButton {
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
        self.boton_actualizar_estado.setFixedHeight(40)  # Altura fija
        self.boton_actualizar_estado.setFixedWidth(150)  # Ancho fijo
        self.layout.addWidget(self.boton_actualizar_estado)

        # Tabla de checklist
        self.tabla_checklist = QTableWidget()
        self.tabla_checklist.setColumnCount(4)
        self.tabla_checklist.setHorizontalHeaderLabels(["Ítem", "Estado", "Observaciones", "Acción"])
        self.layout.addWidget(self.tabla_checklist)

        # Botones adicionales
        self.botones_layout = QVBoxLayout()
        self.boton_agregar_checklist = QPushButton("Agregar Ítem al Checklist")
        self.boton_agregar_checklist.setStyleSheet("""
            QPushButton {
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
        self.boton_agregar_checklist.setFixedHeight(40)  # Altura fija
        self.boton_agregar_checklist.setFixedWidth(150)  # Ancho fijo
        self.botones_layout.addWidget(self.boton_agregar_checklist)

        self.boton_exportar_excel = QPushButton("Exportar Historial a Excel")
        self.boton_exportar_excel.setStyleSheet("""
            QPushButton {
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
        self.boton_exportar_excel.setFixedHeight(40)  # Altura fija
        self.boton_exportar_excel.setFixedWidth(150)  # Ancho fijo
        self.botones_layout.addWidget(self.boton_exportar_excel)

        self.boton_exportar_pdf = QPushButton("Exportar Historial a PDF")
        self.boton_exportar_pdf.setStyleSheet("""
            QPushButton {
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
        self.boton_exportar_pdf.setFixedHeight(40)  # Altura fija
        self.boton_exportar_pdf.setFixedWidth(150)  # Ancho fijo
        self.botones_layout.addWidget(self.boton_exportar_pdf)

        self.boton_exportar_acta = QPushButton("Exportar Acta de Entrega")
        self.boton_exportar_acta.setStyleSheet("""
            QPushButton {
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
        self.boton_exportar_acta.setFixedHeight(40)  # Altura fija
        self.boton_exportar_acta.setFixedWidth(150)  # Ancho fijo
        self.botones_layout.addWidget(self.boton_exportar_acta)

        self.boton_generar_hoja_ruta = QPushButton("Generar Hoja de Ruta")
        self.boton_generar_hoja_ruta.setStyleSheet("""
            QPushButton {
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
        self.boton_generar_hoja_ruta.setFixedHeight(40)  # Altura fija
        self.boton_generar_hoja_ruta.setFixedWidth(150)  # Ancho fijo
        self.botones_layout.addWidget(self.boton_generar_hoja_ruta)

        self.layout.addLayout(self.botones_layout)
        self.setLayout(self.layout)

    def mostrar_hoja_de_ruta(self, hoja_de_ruta):
        self.tabla_hoja_ruta = QTableWidget()
        self.tabla_hoja_ruta.setRowCount(len(hoja_de_ruta))
        self.tabla_hoja_ruta.setColumnCount(5)
        self.tabla_hoja_ruta.setHorizontalHeaderLabels(["ID Entrega", "ID Obra", "Fecha Programada", "Estado", "Chofer Asignado"])

        for row_idx, entrega in enumerate(hoja_de_ruta):
            self.tabla_hoja_ruta.setItem(row_idx, 0, QTableWidgetItem(str(entrega["ID Entrega"])))
            self.tabla_hoja_ruta.setItem(row_idx, 1, QTableWidgetItem(str(entrega["ID Obra"])))
            self.tabla_hoja_ruta.setItem(row_idx, 2, QTableWidgetItem(str(entrega["Fecha Programada"])))
            self.tabla_hoja_ruta.setItem(row_idx, 3, QTableWidgetItem(str(entrega["Estado"])))
            self.tabla_hoja_ruta.setItem(row_idx, 4, QTableWidgetItem(str(entrega["Chofer Asignado"])))

        self.layout.addWidget(self.tabla_hoja_ruta)

class Logistica(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel("Vista de Logística")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
