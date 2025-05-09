from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import QSize

class ContabilidadView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(0)

        self.label_titulo = QLabel("Gestión de Contabilidad y Recibos")
        self.label_titulo.setProperty("class", "contabilidad-titulo")
        self.layout.addWidget(self.label_titulo)

        # Cargar el stylesheet visual moderno para Contabilidad según el tema activo
        try:
            import json
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos de Contabilidad según el tema: {e}")

        # Aplicar estilos globales desde themes
        try:
            with open("themes/light.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        # Formulario para agregar recibo
        self.form_layout = QFormLayout()
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        self.form_layout.setHorizontalSpacing(16)
        self.form_layout.setVerticalSpacing(10)
        self.fecha_emision_input = QLineEdit()
        self.fecha_emision_input.setFixedWidth(400)
        self.fecha_emision_input.setProperty("class", "contabilidad-input")
        self.obra_id_input = QLineEdit()
        self.obra_id_input.setFixedWidth(400)
        self.obra_id_input.setProperty("class", "contabilidad-input")
        self.monto_total_input = QLineEdit()
        self.monto_total_input.setFixedWidth(400)
        self.monto_total_input.setProperty("class", "contabilidad-input")
        self.concepto_input = QLineEdit()
        self.concepto_input.setFixedWidth(400)
        self.concepto_input.setProperty("class", "contabilidad-input")
        self.destinatario_input = QLineEdit()
        self.destinatario_input.setFixedWidth(400)
        self.destinatario_input.setProperty("class", "contabilidad-input")
        self.form_layout.addRow(QLabel("Fecha de Emisión:"), self.fecha_emision_input)
        self.form_layout.addRow(QLabel("ID de Obra:"), self.obra_id_input)
        self.form_layout.addRow(QLabel("Monto Total:"), self.monto_total_input)
        self.form_layout.addRow(QLabel("Concepto:"), self.concepto_input)
        self.form_layout.addRow(QLabel("Destinatario:"), self.destinatario_input)
        self.layout.addLayout(self.form_layout)

        # Ajustar estilos de QLineEdit
        for input_field in [
            self.fecha_emision_input,
            self.obra_id_input,
            self.monto_total_input,
            self.concepto_input,
            self.destinatario_input
        ]:
            input_field.setStyleSheet(
                """
                QLineEdit {
                    padding: 8px;
                    border-radius: 5px;
                    border: 1px solid #ccc;
                }
                QLineEdit:focus {
                    border-color: #0078d7;
                }
                """
            )

        # Tabla de recibos
        self.tabla_recibos = QTableWidget()
        self.tabla_recibos.setColumnCount(6)
        self.tabla_recibos.setHorizontalHeaderLabels(["ID", "Fecha", "Obra", "Monto", "Concepto", "Estado"])
        self.tabla_recibos.setObjectName("tabla_recibos")
        self.layout.addWidget(self.tabla_recibos)

        # Espaciado entre tablas
        self.layout.addSpacing(20)

        # Tabla de movimientos contables
        self.tabla_movimientos = QTableWidget()
        self.tabla_movimientos.setColumnCount(5)
        self.tabla_movimientos.setHorizontalHeaderLabels(["Fecha", "Tipo", "Monto", "Concepto", "Observaciones"])
        self.tabla_movimientos.setObjectName("tabla_movimientos")
        self.layout.addWidget(self.tabla_movimientos)

        # Botones principales como iconos (abajo a la izquierda)
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(12)
        self.boton_nuevo_recibo = QPushButton()
        self.boton_nuevo_recibo.setIcon(QIcon("img/plus_icon.svg"))
        self.boton_nuevo_recibo.setIconSize(QSize(24, 24))
        self.boton_nuevo_recibo.setToolTip("Agregar recibo")
        self.boton_nuevo_recibo.setText("")
        self.boton_nuevo_recibo.setProperty("class", "inventario-bottom")
        self.boton_exportar_excel = QPushButton()
        self.boton_exportar_excel.setIcon(QIcon("img/excel_icon.svg"))
        self.boton_exportar_excel.setIconSize(QSize(24, 24))
        self.boton_exportar_excel.setToolTip("Exportar a Excel")
        self.boton_exportar_excel.setText("")
        self.boton_exportar_excel.setProperty("class", "inventario-bottom")
        self.boton_exportar_pdf = QPushButton()
        self.boton_exportar_pdf.setIcon(QIcon("img/pdf_icon.svg"))
        self.boton_exportar_pdf.setIconSize(QSize(24, 24))
        self.boton_exportar_pdf.setToolTip("Exportar a PDF")
        self.boton_exportar_pdf.setText("")
        self.boton_exportar_pdf.setProperty("class", "inventario-bottom")
        botones_layout.addWidget(self.boton_nuevo_recibo)
        botones_layout.addWidget(self.boton_exportar_excel)
        botones_layout.addWidget(self.boton_exportar_pdf)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        # Botón principal de acción estándar (para compatibilidad con el controlador)
        self.boton_accion = QPushButton()
        self.boton_accion.setIcon(QIcon("utils/contabilidad.svg"))
        self.boton_accion.setToolTip("Agregar nuevo recibo")
        self.boton_accion.setFixedSize(48, 48)
        self.boton_accion.setIconSize(QSize(32, 32))
        self.boton_accion.setObjectName("boton_accion")
        self.layout.addWidget(self.boton_accion)

        # Sombra visual profesional para el botón principal
        def aplicar_sombra(widget):
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(15)
            sombra.setXOffset(0)
            sombra.setYOffset(4)
            sombra.setColor(QColor(0, 0, 0, 160))
            widget.setGraphicsEffect(sombra)
        aplicar_sombra(self.boton_accion)

        # Asegurar espaciado y alineación
        self.layout.setSpacing(10)
        self.form_layout.setHorizontalSpacing(12)
        self.form_layout.setVerticalSpacing(8)
        botones_layout.setSpacing(10)

        self.setLayout(self.layout)
        self.controller = None

    @property
    def label(self):
        if not hasattr(self, '_label_estado'):
            self._label_estado = QLabel()
        return self._label_estado

    @property
    def buscar_input(self):
        if not hasattr(self, '_buscar_input'):
            self._buscar_input = QLineEdit()
        return self._buscar_input

    @property
    def id_item_input(self):
        if not hasattr(self, '_id_item_input'):
            self._id_item_input = QLineEdit()
        return self._id_item_input

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
