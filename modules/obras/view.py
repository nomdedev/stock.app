from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QCalendarWidget, QPushButton, QHBoxLayout, QFrame, QTableWidget, QTableWidgetItem, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QColor
from themes import theme_manager
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from modules.obras.cronograma.view import CronogramaView
from modules.obras.cronograma.controller import CronogramaController
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono

class ObrasView(QWidget, TableResponsiveMixin):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 10, 20, 10)  # Reducir margen superior
        self.layout.setSpacing(8)  # Menor separación vertical
        try:
            tema = theme_manager.cargar_preferencia_tema()
            theme_manager.aplicar_tema(tema)
        except Exception as e:
            print(f"No se pudo aplicar el tema global: {e}")
        # Título estilizado
        self.label_titulo = QLabel("Gestión de Obras")
        self.label_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_titulo)
        # Área de estado
        self.label_estado = QLabel("Estado: Listo")
        self.label_estado.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_estado)
        # Pestañas: Obras, Cronograma (Gantt) y Calendario
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        # --- NUEVA PESTAÑA: Tabla de Obras ---
        self.tab_tabla_obras = QWidget()
        self.tab_tabla_obras_layout = QVBoxLayout()
        self.tab_tabla_obras.setLayout(self.tab_tabla_obras_layout)
        self.tabs.addTab(self.tab_tabla_obras, "Listado de Obras")
        # --- Botones superiores derechos estilo Inventario ---
        top_btns_layout = QHBoxLayout()
        top_btns_layout.addStretch()
        self.boton_agregar_obra = QPushButton()
        self.boton_agregar_obra.setIcon(QIcon("img/add-etapa.svg"))
        self.boton_agregar_obra.setIconSize(QSize(24, 24))
        self.boton_agregar_obra.setToolTip("Agregar nueva obra")
        self.boton_agregar_obra.setText("")
        self.boton_agregar_obra.setFixedSize(48, 48)
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_agregar_obra.setGraphicsEffect(sombra)
        estilizar_boton_icono(self.boton_agregar_obra)
        top_btns_layout.addWidget(self.boton_agregar_obra)
        self.tab_tabla_obras_layout.addLayout(top_btns_layout)
        # --- Tabla principal de obras (estilo Inventario) ---
        self.tabla_obras = QTableWidget()
        self.tabla_obras.setObjectName("tabla_obras")
        TableResponsiveMixin.make_table_responsive(self, self.tabla_obras)
        self.tabla_obras.setAlternatingRowColors(True)
        self.tabla_obras.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_obras.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_obras.verticalHeader().setVisible(False)
        self.tabla_obras.horizontalHeader().setHighlightSections(False)
        self.tabla_obras.setShowGrid(False)
        self.tabla_obras.setMinimumHeight(400)
        self.tabla_obras.setMinimumWidth(1200)
        self.tabla_obras.setStyleSheet("")
        self.tab_tabla_obras_layout.addWidget(self.tabla_obras)
        # Método para cargar datos en la tabla
        def cargar_tabla_obras(obras):
            self.tabla_obras.setRowCount(0)
            for idx, obra in enumerate(obras):
                row = self.tabla_obras.rowCount()
                self.tabla_obras.insertRow(row)
                self.tabla_obras.setItem(row, 0, QTableWidgetItem(str(obra.get('nombre',''))))
                self.tabla_obras.setItem(row, 1, QTableWidgetItem(str(obra.get('cliente',''))))
                self.tabla_obras.setItem(row, 2, QTableWidgetItem(str(obra.get('estado',''))))
                self.tabla_obras.setItem(row, 3, QTableWidgetItem(str(obra.get('fecha_medicion',''))))
                self.tabla_obras.setItem(row, 4, QTableWidgetItem(str(obra.get('fecha_entrega',''))))
                self.tabla_obras.setItem(row, 5, QTableWidgetItem(str(obra.get('dias_entrega',''))))
                self.tabla_obras.setItem(row, 6, QTableWidgetItem(str(obra.get('monto_ars',''))))
                self.tabla_obras.setItem(row, 7, QTableWidgetItem(str(obra.get('pago_porcentaje',''))))
                # Botón de edición
                btn_editar = QPushButton()
                btn_editar.setIcon(QIcon("img/plus_icon.svg"))
                btn_editar.setToolTip("Editar obra")
                btn_editar.setFixedSize(32, 32)
                estilizar_boton_icono(btn_editar)
                btn_editar.clicked.connect(lambda _, r=row: self.accion_editar_obra(r))
                self.tabla_obras.setCellWidget(row, 8, btn_editar)
        self.cargar_tabla_obras = cargar_tabla_obras
        # Acción de edición
        def accion_editar_obra(row):
            if hasattr(self, 'obras_controller'):
                self.obras_controller.editar_obra(row+1)
        self.accion_editar_obra = accion_editar_obra
        # Pestaña de Cronograma (Gantt visual)
        self.tab_cronograma = QWidget()
        self.tab_cronograma_layout = QVBoxLayout()
        self.tab_cronograma.setLayout(self.tab_cronograma_layout)
        self.tabs.addTab(self.tab_cronograma, "Cronograma")
        # --- INTEGRACIÓN DEL NUEVO GANTT ---
        self.cronograma_view = CronogramaView()
        self.cronograma_controller = CronogramaController(self.cronograma_view)
        # Contenedor horizontal para botones de zoom
        zoom_layout = QHBoxLayout()
        self.boton_zoom_in = QPushButton("+")
        self.boton_zoom_in.setFixedSize(32, 32)
        self.boton_zoom_in.setToolTip("Acercar cronograma")
        self.boton_zoom_out = QPushButton("-")
        self.boton_zoom_out.setFixedSize(32, 32)
        self.boton_zoom_out.setToolTip("Alejar cronograma")
        zoom_layout.addWidget(self.boton_zoom_in)
        zoom_layout.addWidget(self.boton_zoom_out)
        zoom_layout.addStretch()
        self.tab_cronograma_layout.addLayout(zoom_layout)
        self.tab_cronograma_layout.addWidget(self.cronograma_view)
        self.boton_zoom_in.clicked.connect(self.cronograma_view.zoom_in)
        self.boton_zoom_out.clicked.connect(self.cronograma_view.zoom_out)
        # --- Botones de acción debajo del cronograma ---
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-etapa.svg"))
        self.boton_agregar.setIconSize(QSize(20, 20))
        self.boton_agregar.setToolTip("Agregar obra")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_agregar.setStyleSheet("")
        botones_layout.addWidget(self.boton_agregar)
        self.boton_verificar_obra = QPushButton()
        self.boton_verificar_obra.setIcon(QIcon("img/search_icon.svg"))
        self.boton_verificar_obra.setIconSize(QSize(24, 24))
        self.boton_verificar_obra.setToolTip("Verificar obra en SQL")
        self.boton_verificar_obra.setText("")
        self.boton_verificar_obra.setFixedSize(48, 48)
        self.boton_verificar_obra.setStyleSheet("")
        botones_layout.addWidget(self.boton_verificar_obra)
        botones_layout.addStretch()
        self.tab_cronograma_layout.addLayout(botones_layout)
        estilizar_boton_icono(self.boton_agregar)
        estilizar_boton_icono(self.boton_verificar_obra)
        self.boton_agregar.clicked.connect(self.accion_agregar_obra)
        self.boton_verificar_obra.clicked.connect(self.accion_verificar_obra)
        # Pestaña de Calendario
        self.tab_calendario = QWidget()
        self.tab_calendario_layout = QVBoxLayout()
        self.calendario = QCalendarWidget()
        self.calendario.setGridVisible(True)
        self.tab_calendario_layout.addWidget(self.calendario)
        self.tab_calendario.setLayout(self.tab_calendario_layout)
        self.tabs.addTab(self.tab_calendario, "Calendario")
        self.setLayout(self.layout)
        # NOTA: Este módulo no tiene QTableWidget principal, por lo que no aplica make_table_responsive aquí.

    @property
    def label(self):
        return self.label_estado

    def accion_agregar_obra(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Agregar Obra", "Acción de agregar obra ejecutada.")

    def accion_verificar_obra(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Verificar Obra", "Acción de verificar obra ejecutada.")
