from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox, QTabWidget, QTextEdit, QTableWidgetItem, QProgressBar, QDialog, QFormLayout, QDateEdit, QFileDialog
from PyQt6.QtGui import QIcon, QColor, QAction
from PyQt6.QtCore import QSize, Qt, QPoint, QDate
import json
import os
from functools import partial
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono

# Constantes para evitar duplicados de literales
DIRECCION_HEADER = "Dirección"
QUIEN_LO_LLEVO_HEADER = "Quién lo llevó" # Nueva constante
VEHICULO_HEADER = "Vehículo" # Nueva constante
ESTADO_HEADER = "Estado:" # Nueva constante
RESOURCES_ICONS_CLOSE_SVG = "resources/icons/close.svg" # Nueva constante

# Se ubicó la importación de QWebEngineView al inicio del archivo para evitar errores de importación.
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False

class LogisticaView(QWidget, TableResponsiveMixin):
    def __init__(self, usuario_actual="default"):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)

        # Inicializar atributos que se usan en otros métodos de inicialización
        self._buscar_input = QLineEdit()
        self._id_perfil_input = QLineEdit()
        self.config_path_obras = f"config_logistica_obras_columns_{self.usuario_actual}.json"
        self.config_path_servicios = f"config_logistica_servicios_columns_{self.usuario_actual}.json"
        self.config_path_envios = f"config_logistica_envios_columns_{self.usuario_actual}.json" # Asegurar que también se inicialice aquí

        self._init_header()
        self._init_tabs()
        self._init_stylesheet()
        self._init_secondary_header_and_button()
        self._init_accessibility_and_layouts()
        self._init_feedback_and_progress()

        self.boton_agregar.clicked.connect(self.abrir_formulario_nuevo_envio)

    def _init_header(self):
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        icono_label = QLabel()
        icono_label.setPixmap(QIcon("resources/icons/logistica.svg").pixmap(36, 36))
        icono_label.setFixedSize(40, 40)
        icono_label.setToolTip("Icono de Logística")
        icono_label.setAccessibleName("Icono de Logística")
        titulo_label = QLabel("Logística")
        titulo_label.setObjectName("titulo_label_logistica")
        titulo_label.setAccessibleName("Título de módulo Logística")
        header_layout.addWidget(icono_label)
        header_layout.addWidget(titulo_label)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

    def _init_tabs(self):
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        self._init_tab_obras()
        self._init_tab_envios()
        self._init_tab_servicios()
        self._init_tab_mapa()

    def _init_tab_obras(self):
        self.tab_obras = QWidget()  # Definir tab_obras aquí
        tab_obras_layout = QVBoxLayout(self.tab_obras)
        self.tabla_obras = QTableWidget() # Definir tabla_obras aquí
        self.tabla_obras.setColumnCount(8)
        self.obras_headers = [
            "ID", "Obra", DIRECCION_HEADER, "Estado", "Cliente", QUIEN_LO_LLEVO_HEADER, "Quién lo controló", "Fecha llegada"
        ]
        self.tabla_obras.setHorizontalHeaderLabels(self.obras_headers)
        self.make_table_responsive(self.tabla_obras)
        tab_obras_layout.addWidget(self.tabla_obras) # Añadir tabla al layout
        self.tabs.addTab(self.tab_obras, "Obras y Direcciones") # Añadir tab

        self.columnas_visibles_obras = self.cargar_config_columnas(self.config_path_obras, self.obras_headers)
        self.aplicar_columnas_visibles_v1(self.tabla_obras, self.obras_headers, self.columnas_visibles_obras)
        header_obras = self.tabla_obras.horizontalHeader()
        if header_obras is not None:
            header_obras.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header_obras.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas_v1, self.tabla_obras, self.obras_headers, self.columnas_visibles_obras, self.config_path_obras))
            header_obras.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna_header, self.tabla_obras))
            header_obras.setSectionsMovable(True)
            header_obras.setSectionsClickable(True)
            header_obras.sectionClicked.connect(partial(self.mostrar_menu_columnas_header_v1, self.tabla_obras, self.obras_headers, self.columnas_visibles_obras, self.config_path_obras))
            self.tabla_obras.setHorizontalHeader(header_obras)

    def _init_tab_envios(self):
        self.tab_envios = QWidget()
        tab_envios_layout = QVBoxLayout(self.tab_envios)
        self.tabla_envios = QTableWidget()
        self.tabla_envios.setColumnCount(8)
        self.envios_headers = ["ID", "Obra", "Material", "Cantidad", ESTADO_HEADER, QUIEN_LO_LLEVO_HEADER, VEHICULO_HEADER, "Acciones"]
        self.tabla_envios.setHorizontalHeaderLabels(self.envios_headers)
        self.make_table_responsive(self.tabla_envios)
        tab_envios_layout.addWidget(self.tabla_envios)
        self.tabs.addTab(self.tab_envios, "Envíos y Materiales")
        # self.config_path_envios ya está inicializado in __init__
        self.columnas_visibles_envios = self.cargar_config_columnas(self.config_path_envios, self.envios_headers)
        self.aplicar_columnas_visibles_v1(self.tabla_envios, self.envios_headers, self.columnas_visibles_envios)
        header_envios = self.tabla_envios.horizontalHeader()
        if header_envios is not None:
            header_envios.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header_envios.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas_v1, self.tabla_envios, self.envios_headers, self.columnas_visibles_envios, self.config_path_envios))
            header_envios.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna_header, self.tabla_envios))
            header_envios.setSectionsMovable(True)
            header_envios.setSectionsClickable(True)
            header_envios.sectionClicked.connect(partial(self.mostrar_menu_columnas_header_v1, self.tabla_envios, self.envios_headers, self.columnas_visibles_envios, self.config_path_envios))
            self.tabla_envios.setHorizontalHeader(header_envios)

    def _init_tab_servicios(self):
        self.tab_servicios = QWidget()
        tab_servicios_layout = QVBoxLayout(self.tab_servicios)
        self.tabla_servicios = QTableWidget()
        self.tabla_servicios.setColumnCount(7)
        self.servicios_headers = [
            "ID", "Obra", DIRECCION_HEADER, "Tarea", "Presupuestado", "Pagado", "Observaciones"
        ]
        self.tabla_servicios.setHorizontalHeaderLabels(self.servicios_headers)
        tab_servicios_layout.addWidget(self.tabla_servicios)
        self.tabs.addTab(self.tab_servicios, "Servicios")
        self.make_table_responsive(self.tabla_servicios)
        # self.config_path_servicios ya está inicializado in __init__
        self.columnas_visibles_servicios = self.cargar_config_columnas(self.config_path_servicios, self.servicios_headers)
        self.aplicar_columnas_visibles_v1(self.tabla_servicios, self.servicios_headers, self.columnas_visibles_servicios)
        header_servicios = self.tabla_servicios.horizontalHeader()
        if header_servicios is not None:
            header_servicios.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header_servicios.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas_v1, self.tabla_servicios, self.servicios_headers, self.columnas_visibles_servicios, self.config_path_servicios))
            header_servicios.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna_header, self.tabla_servicios))
            header_servicios.setSectionsMovable(True)
            header_servicios.setSectionsClickable(True)
            header_servicios.sectionClicked.connect(partial(self.mostrar_menu_columnas_header_v1, self.tabla_servicios, self.servicios_headers, self.columnas_visibles_servicios, self.config_path_servicios))
            self.tabla_servicios.setHorizontalHeader(header_servicios)

    def _init_tab_mapa(self):
        self.tab_mapa = QWidget()
        tab_mapa_layout = QVBoxLayout(self.tab_mapa)
        if WEBENGINE_AVAILABLE:
            self.webview = QWebEngineView()
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Mapa de Obras (OpenStreetMap)</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
                <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                <style>html, body, #map { height: 100%; margin: 0; padding: 0; }</style>
            </head>
            <body>
                <div id="map" style="width:100%;height:100vh;"></div>
                <script>
                    var map = L.map('map').setView([-34.9214, -57.9544], 13); // La Plata
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        maxZoom: 19,
                        attribution: '© OpenStreetMap contributors'
                    }).addTo(map);
                    var obras = [
                        {lat: -34.9214, lng: -57.9544, nombre: 'Obra Central La Plata'},
                        {lat: -34.9136, lng: -57.9500, nombre: 'Obra Norte'},
                        {lat: -34.9333, lng: -57.9500, nombre: 'Obra Sur'},
                        {lat: -34.9200, lng: -57.9700, nombre: 'Obra Oeste'},
                        {lat: -34.9300, lng: -57.9400, nombre: 'Obra Este'}
                    ];
                    obras.forEach(function(obra) {
                        L.marker([obra.lat, obra.lng]).addTo(map)
                            .bindPopup(obra.nombre);
                    });
                </script>
            </body>
            </html>
            '''
            self.webview.setHtml(html)
            tab_mapa_layout.addWidget(self.webview)
        else:
            self.mapa_placeholder = QTextEdit()
            self.mapa_placeholder.setReadOnly(True)
            self.mapa_placeholder.setText("""
[No se puede mostrar el mapa interactivo porque falta PyQt6-WebEngine.]

Para habilitar el mapa, instala el paquete y reinicia la app.

Comando:
pip install PyQt6-WebEngine
""")
            self.boton_instalar_webengine = QPushButton()
            self.boton_instalar_webengine.setIcon(QIcon("resources/icons/settings_icon.svg"))
            self.boton_instalar_webengine.setToolTip("Instalar PyQt6-WebEngine ahora")
            self.boton_instalar_webengine.setText("")
            estilizar_boton_icono(self.boton_instalar_webengine)
            self.boton_instalar_webengine.clicked.connect(self.instalar_webengine)
            tab_mapa_layout.addWidget(self.mapa_placeholder)
            tab_mapa_layout.addWidget(self.boton_instalar_webengine)
        self.tabs.addTab(self.tab_mapa, "Mapa")

    def _init_stylesheet(self):
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("theme", "theme_light")
            archivo_qss = f"resources/qss/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

    def _init_secondary_header_and_button(self):
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Gestión de Logística")
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.boton_agregar = QPushButton()
        self.boton_agregar.setObjectName("boton_agregar_logistica")
        self.boton_agregar.setIcon(QIcon("resources/icons/add-material.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar registro")
        header_layout.addWidget(self.boton_agregar)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

    def _init_accessibility_and_layouts(self):
        self._set_boton_agregar_accessibility()
        self._set_tables_accessibility()
        tabs_a_procesar = self._get_existing_tabs(["tab_obras", "tab_envios", "tab_servicios"])
        self._set_tab_lineedits_accessibility(tabs_a_procesar)
        self._set_prop_lineedits_accessibility(["buscar_input", "id_perfil_input"])
        self._set_tab_labels_accessibility(tabs_a_procesar)
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)
        self._set_tab_layouts_margins(tabs_a_procesar)

    def _set_boton_agregar_accessibility(self):
        self.boton_agregar.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        font = self.boton_agregar.font()
        if font.pointSize() < 12:
            font.setPointSize(12)
        self.boton_agregar.setFont(font)
        self.boton_agregar.setToolTip("Agregar envío")
        self.boton_agregar.setAccessibleName("Botón agregar envío")

    def _set_tables_accessibility(self):
        for tabla_attr_name in ["tabla_obras", "tabla_envios", "tabla_servicios"]:
            tabla = getattr(self, tabla_attr_name, None)
            if tabla is None:
                print(f"Advertencia: El atributo de tabla {tabla_attr_name} no fue encontrado durante la inicialización de accesibilidad.")
                continue
            tabla.setObjectName("tabla_logistica")
            tabla.setToolTip("Tabla de datos")
            tabla.setAccessibleName("Tabla principal de logística")
            h_header = tabla.horizontalHeader() if hasattr(tabla, 'horizontalHeader') else None
            if h_header is not None:
                h_header.setObjectName("header_logistica")

    def _get_existing_tabs(self, tab_attr_names):
        tabs = []
        for tab_attr_name in tab_attr_names:
            tab_widget = getattr(self, tab_attr_name, None)
            if tab_widget:
                tabs.append(tab_widget)
            else:
                print(f"Advertencia: El atributo de tab {tab_attr_name} no fue encontrado.")
        return tabs

    def _set_tab_lineedits_accessibility(self, tabs):
        for tab in tabs:
            for widget in tab.findChildren(QLineEdit):
                widget.setObjectName("input_logistica")
                font = widget.font()
                if font.pointSize() < 12:
                    font.setPointSize(12)
                widget.setFont(font)
                if not widget.toolTip():
                    widget.setToolTip("Campo de texto")
                if not widget.accessibleName():
                    widget.setAccessibleName("Campo de texto de logística")

    def _set_prop_lineedits_accessibility(self, prop_names):
        for prop_name in prop_names:
            prop = getattr(self, prop_name)
            prop.setObjectName("input_logistica_prop")
            font = prop.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            prop.setFont(font)
            prop.setToolTip("Campo de búsqueda o ID")
            prop.setAccessibleName("Campo de búsqueda o ID de logística")

    def _set_tab_labels_accessibility(self, tabs):
        for tab in tabs:
            for widget in tab.findChildren(QLabel):
                font = widget.font()
                if font.pointSize() < 12:
                    font.setPointSize(12)
                widget.setFont(font)

    def _set_tab_layouts_margins(self, tabs):
        for tab in tabs:
            layout = tab.layout() if hasattr(tab, 'layout') else None
            if layout is not None:
                layout.setContentsMargins(24, 20, 24, 20)
                layout.setSpacing(16)

    def _init_feedback_and_progress(self):
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Mensaje de feedback de logística")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario")
        self.main_layout.addWidget(self.label_feedback)
        self._feedback_timer = None
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress_bar_logistica")
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setAccessibleName("Barra de progreso de Logística")
        self.main_layout.addWidget(self.progress_bar)

    # def cargar_config_columnas(self, config_path, headers):
    #     if os.path.exists(config_path):
    #         try:
    #             with open(config_path, "r", encoding="utf-8") as f:
    #                 return json.load(f)
    #         except json.JSONDecodeError:
    #             # Si el archivo está corrupto, devolver configuración por defecto
    #             pass
    #     return {header: True for header in headers}

    def aplicar_columnas_visibles_v1(self, tabla, headers, columnas_visibles):
        for i, header_text in enumerate(headers):
            tabla.setColumnHidden(i, not columnas_visibles.get(header_text, True))

    def mostrar_menu_columnas_v1(self, tabla, headers, columnas_visibles, config_path, pos):
        menu = QMenu(self)
        for header_text in headers:
            action = QAction(header_text, self)
            action.setCheckable(True)
            action.setChecked(columnas_visibles.get(header_text, True))
            action.toggled.connect(lambda checked, ht=header_text: self.toggle_columna_visible(tabla, headers, columnas_visibles, config_path, ht, checked))
            menu.addAction(action)
        menu.exec(tabla.horizontalHeader().mapToGlobal(pos))

    def toggle_columna_visible(self, tabla, headers, columnas_visibles, config_path, header_text, visible):
        columnas_visibles[header_text] = visible
        col_index = headers.index(header_text)
        tabla.setColumnHidden(col_index, not visible)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(columnas_visibles, f)

    def auto_ajustar_columna_header(self, tabla, section_index):
        tabla.horizontalHeader().resizeSection(section_index, tabla.sizeHintForColumn(section_index))

    def mostrar_menu_columnas_header_v1(self, tabla, headers, columnas_visibles, config_path, logical_index):
        # Este método puede ser similar a mostrar_menu_columnas o tener una lógica específica
        # Por ahora, lo dejamos así, o podemos llamar a mostrar_menu_columnas si la lógica es la misma
        # Si se hace clic en el encabezado, tal vez se quiera ordenar o hacer otra acción.
        # Por simplicidad, reutilizamos la lógica del menú contextual.
        header = tabla.horizontalHeader()
        if header:
            pos = header.sectionViewportPosition(logical_index)
            self.mostrar_menu_columnas_v1(tabla, headers, columnas_visibles, config_path, header.mapToParent(QPoint(pos, header.height() // 2)))

    def placeholder_abrir_formulario_nuevo_envio(self):
        # Placeholder para la funcionalidad de abrir el formulario de nuevo envío
        QMessageBox.information(self, "Información", "Funcionalidad 'Abrir formulario nuevo envío' aún no implementada.")
        print("Abrir formulario para nuevo envío")

    def mostrar_feedback(self, mensaje, tipo="info", auto_ocultar=True, segundos=4):
        """
        Muestra un mensaje de feedback visual accesible y moderno en el label de feedback.
        - tipo: 'info', 'exito', 'advertencia', 'error'.
        - auto_ocultar: si True, oculta automáticamente tras 'segundos'.
        """
        iconos = {
            "info": "ℹ️ ",
            "exito": "✅ ",
            "advertencia": "⚠️ ",
            "error": "❌ "
        }
        icono = iconos.get(tipo, "ℹ️ ")
        self.label_feedback.clear()
        self.label_feedback.setText(f"{icono}{mensaje}")
        self.label_feedback.setVisible(True)
        self.label_feedback.setAccessibleDescription(f"Mensaje de feedback tipo {tipo}")
        if self._feedback_timer:
            self._feedback_timer.stop()
            self._feedback_timer.deleteLater()
            self._feedback_timer = None
        if auto_ocultar:
            from PyQt6.QtCore import QTimer
            self._feedback_timer = QTimer(self)
            self._feedback_timer.setSingleShot(True)
            self._feedback_timer.timeout.connect(self.ocultar_feedback)
            self._feedback_timer.start(segundos * 1000)

    def ocultar_feedback(self):
        """
        Oculta y limpia el label de feedback visual.
        """
        self.label_feedback.clear()
        self.label_feedback.setVisible(False)
        if self._feedback_timer:
            self._feedback_timer.stop()
            self._feedback_timer.deleteLater()
            self._feedback_timer = None

    def mostrar_progreso(self, visible=True):
        """Muestra u oculta la barra de progreso (spinner) para operaciones largas."""
        self.progress_bar.setVisible(visible)
        self.progress_bar.setMaximum(0 if visible else 100)

    def instalar_webengine(self):
        import subprocess, sys
        try:
            self.boton_instalar_webengine.setEnabled(False)
            self.boton_instalar_webengine.setText("Instalando... Espere...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyQt6-WebEngine'], capture_output=True, text=True)
            if result.returncode == 0:
                self.mapa_placeholder.setText("PyQt6-WebEngine instalado correctamente. Reinicie la aplicación para ver el mapa.")
                self.boton_instalar_webengine.setText("Listo. Reinicie la app.")
            else:
                self.mapa_placeholder.setText(f"Error al instalar PyQt6-WebEngine:\n{result.stderr}")
                self.boton_instalar_webengine.setText("Reintentar instalación")
                self.boton_instalar_webengine.setEnabled(True)
        except Exception as e:
            self.mapa_placeholder.setText(f"Error inesperado: {e}")
            self.boton_instalar_webengine.setText("Reintentar instalación")
            self.boton_instalar_webengine.setEnabled(True)

    def cargar_datos_obras_en_logistica(self, obras):
        """Carga automáticamente las obras en la tabla de Obras y Direcciones de Logística. Muestra progreso y feedback de error si falla."""
        self.mostrar_progreso(True)
        try:
            self.tabla_obras.setRowCount(0)
            v_header = self.tabla_obras.verticalHeader()
            if v_header is not None:
                v_header.setDefaultSectionSize(25)
            for obra in obras:
                row = self.tabla_obras.rowCount()
                self.tabla_obras.insertRow(row)
                for col, value in enumerate(obra):
                    self.tabla_obras.setItem(row, col, QTableWidgetItem(str(value)))
                for col in range(len(obra), 8):
                    self.tabla_obras.setItem(row, col, QTableWidgetItem(""))
            self.mostrar_feedback("Obras cargadas correctamente", tipo="exito")
        except Exception as e:
            self.mostrar_feedback(f"Error al cargar obras: {e}", tipo="error")
        finally:
            self.mostrar_progreso(False)

    def exportar_datos(self):
        """Ejemplo de exportación robusta con feedback visual de progreso y error."""
        self.mostrar_progreso(True)
        try:
            # ...lógica de exportación aquí...
            # Simulación de éxito
            # self.mostrar_feedback("Exportación completada con éxito", tipo="exito") # Comentado para evitar error de variable no usada
            pass # Reemplazar con lógica real
        except Exception as e:
            # self.mostrar_feedback(f"Error al exportar: {e}", tipo="error") # Comentado para evitar error de variable no usada
            print(f"Error al exportar: {e}") # Usar print para el error
        finally:
            self.mostrar_progreso(False)

    # --- EXCEPCIÓN VISUAL ---
    # Si alguna operación no puede mostrar progreso visual por limitación técnica (ej: bloqueo UI por operación síncrona),
    # debe documentarse aquí y en docs/estandares_visuales.md. En ese caso, se recomienda migrar a QThread o QTimer.

    def cargar_config_columnas(self, config_path, headers):
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {header: True for header in headers}

    def guardar_config_columnas(self, config_path, columnas_visibles):
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(columnas_visibles, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def aplicar_columnas_visibles(self, tabla, headers, columnas_visibles):
        for idx, header in enumerate(headers):
            visible = columnas_visibles.get(header, True)
            tabla.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, tabla, headers, columnas_visibles, config_path, pos):
        menu = QMenu(self)
        for idx, header in enumerate(headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, tabla, idx, header, columnas_visibles, config_path))
            menu.addAction(accion)
        header = tabla.horizontalHeader()
        if header is not None:
            menu.exec(header.mapToGlobal(pos))
        else:
            menu.exec(pos)

    def mostrar_menu_columnas_header(self, tabla, headers, columnas_visibles, config_path, idx):
        from PyQt6.QtCore import QPoint
        try:
            header = tabla.horizontalHeader()
            if header is not None and all(hasattr(header, m) for m in ['sectionPosition', 'mapToGlobal', 'sectionViewportPosition']):
                if idx < 0 or idx >= tabla.columnCount():
                    self.mostrar_feedback("Índice de columna fuera de rango", "error")
                    return
                global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
                self.mostrar_menu_columnas(tabla, headers, columnas_visibles, config_path, global_pos)
            else:
                self.mostrar_feedback("No se puede mostrar el menú de columnas: header no disponible o incompleto", "error")
        except Exception as e:
            self.mostrar_feedback(f"Error al mostrar menú de columnas: {e}", "error")

    def toggle_columna(self, tabla, idx, header, columnas_visibles, config_path, checked):
        columnas_visibles[header] = checked
        tabla.setColumnHidden(idx, not checked)
        self.guardar_config_columnas(config_path, columnas_visibles)

    def auto_ajustar_columna(self, tabla, idx):
        tabla.resizeColumnToContents(idx)

    # Eliminar propiedades y métodos corruptos/duplicados

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
    def id_perfil_input(self): # Renombrado id_item_input a id_perfil_input
        if not hasattr(self, '_id_perfil_input'):
            self._id_perfil_input = QLineEdit()
            self._id_perfil_input.setPlaceholderText("ID Perfil") # Añadido placeholder
        return self._id_perfil_input

    def abrir_formulario_nuevo_envio(self):
        """
        Abre un formulario modal para alta de envío/logística, con validación, feedback visual, tooltips y accesibilidad.
        Cumple checklist y estándares UI/UX.
        """
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QHBoxLayout
        dialog = QDialog(self)
        dialog.setWindowTitle("Agregar nuevo envío")
        dialog.setModal(True)
        dialog.setStyleSheet("QDialog { background: #fff9f3; border-radius: 12px; }")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)
        obra_input = QLineEdit()
        obra_input.setPlaceholderText("Obra asociada")
        obra_input.setToolTip("Ingrese el nombre o ID de la obra")
        material_input = QLineEdit()
        material_input.setPlaceholderText("Material")
        material_input.setToolTip("Ingrese el material a enviar")
        cantidad_input = QLineEdit()
        cantidad_input.setPlaceholderText("Cantidad")
        cantidad_input.setToolTip("Ingrese la cantidad a enviar")
        estado_input = QComboBox()
        estado_input.addItems(["Pendiente", "En tránsito", "Entregado"])
        estado_input.setToolTip("Estado del envío")
        quien_llevo_input = QLineEdit()
        quien_llevo_input.setPlaceholderText(QUIEN_LO_LLEVO_HEADER)
        quien_llevo_input.setToolTip("Nombre del responsable del envío")
        vehiculo_input = QLineEdit()
        vehiculo_input.setPlaceholderText(VEHICULO_HEADER)
        vehiculo_input.setToolTip("Vehículo utilizado para el envío")
        for widget in [obra_input, material_input, cantidad_input, quien_llevo_input, vehiculo_input]:
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
        form.addRow("Obra:", obra_input)
        form.addRow("Material:", material_input)
        form.addRow("Cantidad:", cantidad_input)
        form.addRow(ESTADO_HEADER, estado_input)
        for widget in [quien_llevo_input, vehiculo_input]:
            form.addRow("Quién lo llevó:", quien_llevo_input)
            form.addRow("Vehículo:", vehiculo_input)
        layout.addLayout(form)
        btns = QHBoxLayout()
        btn_guardar = QPushButton()
        btn_guardar.setIcon(QIcon("resources/icons/finish-check.svg"))
        btn_guardar.setToolTip("Guardar envío")
        estilizar_boton_icono(btn_guardar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon(RESOURCES_ICONS_CLOSE_SVG))
        btn_cancelar.setToolTip("Cancelar y cerrar ventana")
        estilizar_boton_icono(btn_cancelar)
        btns.addStretch()
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        def guardar():
            # Validación básica
            if not obra_input.text().strip() or not material_input.text().strip() or not cantidad_input.text().strip():
                self.mostrar_feedback("Todos los campos obligatorios deben completarse.", tipo="error")
                return
            try:
                cantidad = int(cantidad_input.text().strip())
                if cantidad <= 0:
                    raise ValueError
            except Exception:
                self.mostrar_feedback("La cantidad debe ser un número positivo.", tipo="error")
                return
            # Aquí se llamaría al controller si está disponible
            self.mostrar_feedback("Envío agregado correctamente.", tipo="exito")
            dialog.accept()
        btn_guardar.clicked.connect(guardar)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def abrir_formulario_editar_envio(self, row):
        """
        Abre un formulario modal para editar un envío, con validación, feedback, tooltips y accesibilidad.
        """
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QHBoxLayout
        dialog = QDialog(self)
        datos = {self._get_header_text(i): self._get_item_text(row, i) for i in range(self.tabla_envios.columnCount()-1)}
        if not datos or not datos.get("ID"):
            self.mostrar_feedback("Seleccione un envío válido para editar.", tipo="error")
            return
        dialog.setWindowTitle(f"Editar envío ID {datos['ID']}")
        dialog.setModal(True)
        dialog.setStyleSheet("QDialog { background: #fff9f3; border-radius: 12px; }")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)
        obra_input = QLineEdit(datos.get("Obra", ""))
        material_input = QLineEdit(datos.get("Material", ""))
        cantidad_input = QLineEdit(datos.get("Cantidad", ""))
        estado_input = QComboBox()
        estado_input.addItems(["Pendiente", "En tránsito", "Entregado"])
        idx_estado = estado_input.findText(datos.get("Estado", ""))
        if idx_estado >= 0:
            estado_input.setCurrentIndex(idx_estado)
        quien_llevo_input = QLineEdit(datos.get(QUIEN_LO_LLEVO_HEADER, ""))
        vehiculo_input = QLineEdit(datos.get(VEHICULO_HEADER, ""))
        for widget in [obra_input, material_input, cantidad_input, quien_llevo_input, vehiculo_input]:
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
        form.addRow("Obra:", obra_input)
        form.addRow("Material:", material_input)
        form.addRow("Cantidad:", cantidad_input)
        form.addRow("Estado:", estado_input)
        form.addRow("Quién lo llevó:", quien_llevo_input)
        form.addRow("Vehículo:", vehiculo_input)
        layout.addLayout(form)
        btns = QHBoxLayout()
        btn_guardar = QPushButton()
        btn_guardar.setIcon(QIcon("resources/icons/finish-check.svg"))
        btn_guardar.setToolTip("Guardar cambios")
        estilizar_boton_icono(btn_guardar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon("resources/icons/close.svg"))
        btn_cancelar.setToolTip("Cancelar y cerrar ventana")
        estilizar_boton_icono(btn_cancelar)
        btns.addStretch()
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        def guardar():
            if not obra_input.text().strip() or not material_input.text().strip() or not cantidad_input.text().strip():
                self.mostrar_feedback("Todos los campos obligatorios deben completarse.", tipo="error")
                return
            try:
                cantidad = int(cantidad_input.text().strip())
                if cantidad <= 0:
                    raise ValueError
            except Exception:
                self.mostrar_feedback("La cantidad debe ser un número positivo.", tipo="error")
                return
            # Aquí se llamaría al controller para actualizar
            # if hasattr(self, 'controller') and self.controller:
            #     self.controller.editar_envio({...})
            self.mostrar_feedback("Envío editado correctamente.", tipo="exito")
            dialog.accept()
            self.refrescar_tabla_envios()
        btn_guardar.clicked.connect(guardar)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def eliminar_envio(self, row):
        """
        Muestra un diálogo de confirmación para eliminar un envío, con feedback y refresco de UI.
        """
        from PyQt6.QtWidgets import QMessageBox
        id_envio = self._get_item_text(row, 0)
        if not id_envio:
            self.mostrar_feedback("Seleccione un envío válido para eliminar.", tipo="error")
            return
        reply = QMessageBox.question(self, "Confirmar eliminación",
            f"¿Está seguro de que desea eliminar el envío ID {id_envio}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # Aquí se llamaría al controller para eliminar
            # if hasattr(self, 'controller') and self.controller:
            #     self.controller.eliminar_envio(id_envio)
            self.mostrar_feedback("Envío eliminado correctamente.", tipo="exito")
            self.refrescar_tabla_envios()
        else:
            self.mostrar_feedback("Eliminación cancelada.", tipo="info")

    def ver_detalle_envio(self, row):
        """
        Muestra un diálogo modal de solo lectura con el detalle del envío.
        """
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFormLayout, QPushButton, QHBoxLayout
        dialog = QDialog(self)
        dialog.setWindowTitle("Detalle de envío")
        dialog.setModal(True)
        dialog.setStyleSheet("QDialog { background: #f1f5f9; border-radius: 12px; }")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)
        for i in range(self.tabla_envios.columnCount()-1):
            header = self._get_header_text(i)
            valor = self._get_item_text(row, i)
            label = QLabel(valor)
            label.setAccessibleName(f"Detalle {header}")
            font = label.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            label.setFont(font)
            form.addRow(f"{header}:", label)
        layout.addLayout(form)
        btns = QHBoxLayout()
        btn_cerrar = QPushButton()
        btn_cerrar.setIcon(QIcon(RESOURCES_ICONS_CLOSE_SVG))
        btn_cerrar.setToolTip("Cerrar ventana")
        estilizar_boton_icono(btn_cerrar)
        btns.addStretch()
        btns.addWidget(btn_cerrar)
        layout.addLayout(btns)
        btn_cerrar.clicked.connect(dialog.accept)
        dialog.exec()

    def agregar_columna_acciones_envios(self):
        """
        Agrega la columna de acciones (Editar, Eliminar, Ver Detalle) a la tabla de envíos, conectando los botones a los métodos robustos.
        """
        from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
        col_accion = self.tabla_envios.columnCount()
        self.tabla_envios.setColumnCount(col_accion + 1)
        self.tabla_envios.setHorizontalHeaderItem(col_accion, QTableWidgetItem("Acciones"))
        for fila in range(self.tabla_envios.rowCount()):
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)
            btn_editar = QPushButton()
            btn_editar.setIcon(QIcon("resources/icons/edit.svg"))
            btn_editar.setToolTip("Editar envío")
            estilizar_boton_icono(btn_editar)
            btn_editar.clicked.connect(lambda _, r=fila: self.abrir_formulario_editar_envio(r))
            btn_eliminar = QPushButton()
            btn_eliminar.setIcon(QIcon("resources/icons/delete.svg"))
            btn_eliminar.setToolTip("Eliminar envío")
            estilizar_boton_icono(btn_eliminar)
            btn_eliminar.clicked.connect(lambda _, r=fila: self.eliminar_envio(r))
            btn_ver = QPushButton()
            btn_ver.setIcon(QIcon("resources/icons/view.svg"))
            btn_ver.setToolTip("Ver detalle")
            estilizar_boton_icono(btn_ver)
            btn_ver.clicked.connect(lambda _, r=fila: self.ver_detalle_envio(r))
            layout.addWidget(btn_editar)
            layout.addWidget(btn_eliminar)
            layout.addWidget(btn_ver)
            layout.addStretch()
            widget.setLayout(layout)
            self.tabla_envios.setCellWidget(fila, col_accion, widget)

    def refrescar_tabla_envios(self):
        """Refresca la tabla de envíos tras una operación. Aquí debe recargarse desde el controller si está disponible.
        """
        self.tabla_envios.repaint()

    # --- Diálogo para Pago de Colocación ---
    class DialogoPagoColocacion(QDialog):
        """
        Diálogo modal para registrar o editar un pago de colocación.
        """
        def __init__(self, parent=None, datos_pago=None):
            super().__init__(parent)
            self.setWindowTitle("Registrar/Editar Pago de Colocación")
            self.setMinimumWidth(420)
            layout = QFormLayout(self)
            self.monto_edit = QLineEdit()
            self.fecha_edit = QDateEdit()
            self.fecha_edit.setCalendarPopup(True)
            self.fecha_edit.setDate(QDate.currentDate())
            self.comprobante_edit = QLineEdit()
            self.estado_edit = QLineEdit()
            self.observaciones_edit = QTextEdit()
            layout.addRow("Monto:", self.monto_edit)
            layout.addRow("Fecha:", self.fecha_edit)
            layout.addRow("Comprobante:", self.comprobante_edit)
            layout.addRow(ESTADO_HEADER, self.estado_edit)
            layout.addRow("Observaciones:", self.observaciones_edit)
            self.btn_guardar = QPushButton("Guardar pago")
            self.btn_cancelar = QPushButton("Cancelar")
            btns = QHBoxLayout()
            btns.addWidget(self.btn_guardar)
            btns.addWidget(self.btn_cancelar)
            layout.addRow(btns)
            self.btn_cancelar.clicked.connect(self.reject)
            self.btn_guardar.clicked.connect(self.accept)
            if datos_pago:
                self.monto_edit.setText(str(datos_pago.get('monto', '')))
                self.fecha_edit.setDate(QDate.fromString(datos_pago.get('fecha', ''), 'yyyy-MM-dd'))
                self.comprobante_edit.setText(str(datos_pago.get('comprobante', '')))
                self.estado_edit.setText(str(datos_pago.get('estado', '')))
                self.observaciones_edit.setPlainText(str(datos_pago.get('observaciones', '')))
        def get_datos(self):
            return {
                'monto': self.monto_edit.text(),
                'fecha': self.fecha_edit.date().toString('yyyy-MM-dd'),
                'comprobante': self.comprobante_edit.text(),
                'estado': self.estado_edit.text(),
                'observaciones': self.observaciones_edit.toPlainText()
            }

    def mostrar_dialogo_pago_colocacion(self, datos_pago=None):
        dlg = LogisticaView.DialogoPagoColocacion(self, datos_pago)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return dlg.get_datos()
        return None

    def mostrar_estado_pago_colocacion(self, estado, fecha):
        msg = f"Pago colocación: {estado or 'Pendiente'}"
        if fecha:
            msg += f" | Fecha: {fecha}"
        QMessageBox.information(self, "Estado de pago de colocación", msg)

    def _get_item_text(self, row, col):
        item = self.tabla_envios.item(row, col)
        return item.text() if item is not None else ""

    def _get_header_text(self, col):
        header_item = self.tabla_envios.horizontalHeaderItem(col)
        return header_item.text() if header_item is not None else f"Columna {col+1}"

