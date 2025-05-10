from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QTableWidget, QTabWidget, QCalendarWidget, QPushButton, QHBoxLayout, QComboBox, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QColor
from modules.obras.produccion.view import ProduccionView  # Importar ProduccionView desde el módulo correcto
from themes import theme_manager  # Importar el gestor de temas

class ObrasView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Aplicar el tema global según la preferencia
        try:
            tema = theme_manager.cargar_preferencia_tema()
            theme_manager.aplicar_tema(tema)
        except Exception as e:
            print(f"No se pudo aplicar el tema global: {e}")

        self.label_titulo = QLabel("Gestión de Obras")
        self.layout.addWidget(self.label_titulo)

        # Formulario de entrada
        self.form_layout = QFormLayout()
        self.nombre_input = QLineEdit()
        self.nombre_input.setFixedWidth(150)
        self.cliente_input = QLineEdit()
        self.cliente_input.setFixedWidth(150)
        self.estado_input = QComboBox()  # Cambiar a QComboBox para seleccionar estados
        self.estado_input.addItems(["Medición", "Fabricación", "Entrega"])  # Estados predeterminados
        self.estado_input.setFixedWidth(150)
        self.form_layout.addRow("Nombre:", self.nombre_input)
        self.form_layout.addRow("Cliente:", self.cliente_input)
        self.form_layout.addRow("Estado:", self.estado_input)
        self.layout.addLayout(self.form_layout)

        # Tabla principal de obras
        self.tabla_obras = QTableWidget()
        self.tabla_obras.setColumnCount(6)
        self.tabla_obras.setHorizontalHeaderLabels(["ID", "Nombre", "Cliente", "Estado", "Fecha", "Acciones"])
        self.tabla_obras.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_obras.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_obras.verticalHeader().setVisible(False)
        self.tabla_obras.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.tabla_obras)

        # Botón de cambiar estado por fila
        from PyQt6.QtWidgets import QWidget, QHBoxLayout
        for row in range(self.tabla_obras.rowCount()):
            btn = QPushButton()
            btn.setIcon(QIcon("img/settings_icon.svg"))
            btn.setToolTip("Cambiar estado")
            btn.setFixedSize(32, 32)
            def handler(r=row):
                self.tabla_obras.selectRow(r)
                self.parent().controller.cambiar_estado_obra()
            btn.clicked.connect(handler)
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(btn)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0,0,0,0)
            widget.setLayout(layout)
            self.tabla_obras.setCellWidget(row, 5, widget)

        # Crear pestañas
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Pestaña de Cronograma
        self.tab_cronograma = QWidget()
        self.tab_cronograma_layout = QVBoxLayout()

        self.tabla_cronograma = QTableWidget()
        self.tabla_cronograma.setColumnCount(6)
        self.tabla_cronograma.setHorizontalHeaderLabels(["Etapa", "Fecha Programada", "Fecha Realizada", "Observaciones", "Responsable", "Estado"])
        self.tabla_cronograma.horizontalHeader().setStretchLastSection(True)
        self.tab_cronograma_layout.addWidget(self.tabla_cronograma)

        # Kanban visual para cronograma
        self.kanban_layout = QHBoxLayout()
        self.kanban_frame = QWidget()
        self.kanban_frame.setLayout(self.kanban_layout)
        self.tab_cronograma_layout.addWidget(self.kanban_frame)

        self.tab_cronograma.setLayout(self.tab_cronograma_layout)
        self.tabs.addTab(self.tab_cronograma, "Cronograma")

        # Pestaña de Calendario
        self.tab_calendario = QWidget()
        self.tab_calendario_layout = QVBoxLayout()

        self.calendario = QCalendarWidget()
        self.calendario.setGridVisible(True)
        self.tab_calendario_layout.addWidget(self.calendario)

        self.tab_calendario.setLayout(self.tab_calendario_layout)
        self.tabs.addTab(self.tab_calendario, "Calendario")

        # Pestaña de Producción
        self.tab_produccion = ProduccionView()
        self.tabs.addTab(self.tab_produccion, "Producción")

        # Botones principales como iconos
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-etapa.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar obra")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_buscar = QPushButton()
        self.boton_buscar.setIcon(QIcon("img/search_icon.svg"))
        self.boton_buscar.setIconSize(QSize(24, 24))
        self.boton_buscar.setToolTip("Buscar obra")
        self.boton_buscar.setText("")
        self.boton_buscar.setFixedSize(48, 48)
        self.boton_exportar_excel = QPushButton()
        self.boton_exportar_excel.setIcon(QIcon("img/excel_icon.svg"))
        self.boton_exportar_excel.setIconSize(QSize(24, 24))
        self.boton_exportar_excel.setToolTip("Exportar obras a Excel")
        self.boton_exportar_excel.setText("")
        self.boton_exportar_excel.setFixedSize(48, 48)
        self.boton_ver_cronograma = QPushButton()
        self.boton_ver_cronograma.setIcon(QIcon("img/calendar_icon.svg"))
        self.boton_ver_cronograma.setIconSize(QSize(32, 32))
        self.boton_ver_cronograma.setToolTip("Ver cronograma global")
        self.boton_ver_cronograma.setText("")
        self.boton_ver_cronograma.setFixedSize(48, 48)
        self.boton_asignar_material = QPushButton()
        self.boton_asignar_material.setIcon(QIcon("img/add-material.svg"))
        self.boton_asignar_material.setIconSize(QSize(24, 24))
        self.boton_asignar_material.setToolTip("Asignar materiales a la obra seleccionada")
        self.boton_asignar_material.setText("")
        self.boton_asignar_material.setFixedSize(48, 48)
        self.boton_cambiar_estado = QPushButton()
        self.boton_cambiar_estado.setIcon(QIcon("img/finish-check.svg"))
        self.boton_cambiar_estado.setIconSize(QSize(24, 24))
        self.boton_cambiar_estado.setToolTip("Cambiar estado de la obra seleccionada")
        self.boton_cambiar_estado.setText("")
        self.boton_cambiar_estado.setFixedSize(48, 48)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addWidget(self.boton_buscar)
        botones_layout.addWidget(self.boton_exportar_excel)
        botones_layout.addWidget(self.boton_ver_cronograma)
        botones_layout.addWidget(self.boton_asignar_material)
        botones_layout.addWidget(self.boton_cambiar_estado)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        self.setLayout(self.layout)

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
