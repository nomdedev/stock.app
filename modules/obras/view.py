from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QCalendarWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from themes import theme_manager
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ObrasView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        try:
            tema = theme_manager.cargar_preferencia_tema()
            theme_manager.aplicar_tema(tema)
        except Exception as e:
            print(f"No se pudo aplicar el tema global: {e}")
        self.label_titulo = QLabel("Gestión de Obras")
        self.layout.addWidget(self.label_titulo)
        # Pestañas: solo Cronograma (Gantt) y Calendario
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        # Pestaña de Cronograma (Gantt visual)
        self.tab_cronograma = QWidget()
        self.tab_cronograma_layout = QVBoxLayout()
        self.tab_cronograma.setLayout(self.tab_cronograma_layout)
        self.tabs.addTab(self.tab_cronograma, "Cronograma")
        self.gantt_canvas = None
        self.gantt_bar_info = []  # Guardar info de cada barra para identificar la obra
        self.gantt_on_bar_clicked = None  # Callback externo (el controlador lo setea)
        # Layout para el Gantt
        self.gantt_layout = QVBoxLayout()
        self.tab_cronograma_layout.addLayout(self.gantt_layout)
        # --- Botones de acción debajo del cronograma ---
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-etapa.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar obra")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        botones_layout.addWidget(self.boton_agregar)
        self.boton_verificar_obra = QPushButton()
        self.boton_verificar_obra.setIcon(QIcon("img/search_icon.svg"))
        self.boton_verificar_obra.setIconSize(QSize(24, 24))
        self.boton_verificar_obra.setToolTip("Verificar obra en SQL")
        self.boton_verificar_obra.setText("")
        self.boton_verificar_obra.setFixedSize(48, 48)
        botones_layout.addWidget(self.boton_verificar_obra)
        botones_layout.addStretch()
        self.tab_cronograma_layout.addLayout(botones_layout)
        # Pestaña de Calendario
        self.tab_calendario = QWidget()
        self.tab_calendario_layout = QVBoxLayout()
        self.calendario = QCalendarWidget()
        self.calendario.setGridVisible(True)
        self.tab_calendario_layout.addWidget(self.calendario)
        self.tab_calendario.setLayout(self.tab_calendario_layout)
        self.tabs.addTab(self.tab_calendario, "Calendario")
        self.setLayout(self.layout)

    def mostrar_gantt(self, obras):
        import datetime
        from matplotlib.backend_bases import PickEvent
        # Limpiar el layout del Gantt
        while self.gantt_layout.count():
            item = self.gantt_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        if self.gantt_canvas:
            self.gantt_canvas.setParent(None)
            self.gantt_canvas = None
        self.gantt_bar_info = []
        if not obras:
            label_vacio = QLabel("No hay obras con fechas válidas para mostrar en el Gantt.")
            self.gantt_layout.addWidget(label_vacio)
            return
        # Filtrar solo obras con fechas válidas
        obras_validas = []
        for idx, obra in enumerate(obras):
            try:
                fecha_ini = datetime.datetime.strptime(str(obra[4]), "%Y-%m-%d") if obra[4] else None
                fecha_fin = datetime.datetime.strptime(str(obra[5]), "%Y-%m-%d") if obra[5] else None
            except Exception:
                continue
            if fecha_ini and fecha_fin:
                obras_validas.append((obra, fecha_ini, fecha_fin))
        if not obras_validas:
            label_vacio = QLabel("No hay obras con fechas válidas para mostrar en el Gantt.")
            self.gantt_layout.addWidget(label_vacio)
            return
        nombres = [f"{o[0][1][:18]} ({o[0][2][:12]})" for o in obras_validas]
        fechas_inicio = [o[1] for o in obras_validas]
        fechas_fin = [o[2] for o in obras_validas]
        # --- BORDES REDONDEADOS Y COLORES POR ESTADO ---
        # Colores minimalistas: medición (gris), fabricación (amarillo), entrega (verde)
        colores = []
        for o in obras_validas:
            estado = o[0][3].lower() if o[0][3] else ""
            if estado == "medición":
                colores.append("#bdbdbd")  # Gris minimalista
            elif estado == "fabricación":
                colores.append("#ffe066")  # Amarillo suave
            elif estado == "entrega":
                colores.append("#7ed957")  # Verde
            else:
                colores.append("#e0e0e0")
        y_pos = range(len(nombres))
        duraciones = [(fin - ini).days for ini, fin in zip(fechas_inicio, fechas_fin)]
        import matplotlib.dates as mdates
        fig = Figure(figsize=(min(12, 2+len(nombres)*1.5), 1.5+0.7*len(nombres)))
        ax = fig.add_subplot(111)
        fechas_inicio_num = mdates.date2num(fechas_inicio)
        bars = ax.barh(y_pos, duraciones, left=fechas_inicio_num, color=colores, height=0.45, edgecolor='none', linewidth=0, picker=True)
        # Bordes redondeados en las barras
        for bar, color in zip(bars, colores):
            bar.set_zorder(3)
            bar.set_alpha(0.95)
            bar.set_linewidth(0)
            bar.set_edgecolor('none')
            bar.set_capstyle('round')
            bar.set_joinstyle('round')
            # Redondear extremos
            bar.set_clip_path(None)
            bar.set_path_effects([])
            try:
                bar.set_radius(8)  # matplotlib >=3.4
            except Exception:
                pass
        ax.set_facecolor('#f8fafc')
        fig.patch.set_facecolor('#f8fafc')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#e5e7eb')
        ax.tick_params(axis='x', colors='#444')
        ax.tick_params(axis='y', colors='#444')
        ax.set_yticks(list(y_pos))
        ax.set_yticklabels(nombres, fontsize=10)
        ax.set_xlabel("Fecha", fontsize=11)
        ax.set_title("Diagrama de Gantt de Obras", fontsize=13, fontweight='bold', pad=15)
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%Y'))
        fig.autofmt_xdate(rotation=25)
        ax.grid(True, which='major', axis='x', linestyle='--', color='#cccccc')
        for i, (ini, fin) in enumerate(zip(fechas_inicio, fechas_fin)):
            ax.text(mdates.date2num(ini), i, ini.strftime('%d-%b-%Y'), va='center', ha='right', fontsize=8, color='#333', alpha=0.8)
            ax.text(mdates.date2num(fin), i, fin.strftime('%d-%b-%Y'), va='center', ha='left', fontsize=8, color='#333', alpha=0.8)
        fig.subplots_adjust(left=0.25, right=0.98, top=0.85, bottom=0.18)
        self.gantt_canvas = FigureCanvas(fig)
        self.gantt_layout.addWidget(self.gantt_canvas, alignment=Qt.AlignmentFlag.AlignCenter)
        # Guardar info de cada barra para identificar la obra al hacer clic
        self.gantt_bar_info = [(obras_validas[i][0][0], obras_validas[i][2].strftime('%Y-%m-%d')) for i in range(len(obras_validas))]  # (id_obra, fecha_entrega)
        # Conectar evento de clic en barra
        def on_bar_pick(event):
            if hasattr(event, 'ind') and event.ind:
                idx = event.ind[0]
                if 0 <= idx < len(self.gantt_bar_info):
                    id_obra, fecha_entrega = self.gantt_bar_info[idx]
                    if self.gantt_on_bar_clicked:
                        self.gantt_on_bar_clicked(id_obra, fecha_entrega)
        self.gantt_canvas.mpl_connect('pick_event', on_bar_pick)

    @property
    def label(self):
        if not hasattr(self, '_label_estado'):
            self._label_estado = QLabel()
        return self._label_estado
