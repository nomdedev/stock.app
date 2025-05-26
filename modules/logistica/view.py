from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox, QTabWidget, QTextEdit, QTableWidgetItem, QProgressBar
from PyQt6.QtGui import QIcon, QColor, QAction
from PyQt6.QtCore import QSize, Qt, QPoint
import json
import os
from functools import partial
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono

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

        # --- HEADER VISUAL MODERNO ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        icono_label = QLabel()
        icono_label.setPixmap(QIcon("img/logistica.svg").pixmap(36, 36))
        icono_label.setFixedSize(40, 40)
        icono_label.setToolTip("Icono de Logística")
        icono_label.setAccessibleName("Icono de Logística")
        titulo_label = QLabel("Logística")
        titulo_label.setStyleSheet("color: #2563eb; font-size: 22px; font-weight: 600; padding-left: 4px;")
        titulo_label.setAccessibleName("Título de módulo Logística")
        header_layout.addWidget(icono_label)
        header_layout.addWidget(titulo_label)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

        # Tabs principales
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # --- Pestaña 1: Obras y Direcciones ---
        self.tab_obras = QWidget()
        tab_obras_layout = QVBoxLayout(self.tab_obras)
        self.tabla_obras = QTableWidget()
        self.tabla_obras.setColumnCount(8)
        self.tabla_obras.setHorizontalHeaderLabels([
            "ID", "Obra", "Dirección", "Estado", "Cliente", "Quién lo llevó", "Quién lo controló", "Fecha llegada"
        ])
        self.make_table_responsive(self.tabla_obras)
        tab_obras_layout.addWidget(self.tabla_obras)
        self.tabs.addTab(self.tab_obras, "Obras y Direcciones")

        # Configuración de columnas para Obras y Direcciones
        self.config_path_obras = f"config_logistica_obras_columns.json"
        self.obras_headers = [
            "ID", "Obra", "Dirección", "Estado", "Cliente", "Quién lo llevó", "Quién lo controló", "Fecha llegada"
        ]
        self.columnas_visibles_obras = self.cargar_config_columnas(self.config_path_obras, self.obras_headers)
        self.aplicar_columnas_visibles(self.tabla_obras, self.obras_headers, self.columnas_visibles_obras)
        header_obras = self.tabla_obras.horizontalHeader()
        if header_obras is not None:
            header_obras.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header_obras.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_obras, self.obras_headers, self.columnas_visibles_obras, self.config_path_obras))
            header_obras.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_obras))
            header_obras.setSectionsMovable(True)
            header_obras.setSectionsClickable(True)
            header_obras.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_obras, self.obras_headers, self.columnas_visibles_obras, self.config_path_obras))
            self.tabla_obras.setHorizontalHeader(header_obras)
        else:
            # EXCEPCIÓN VISUAL: Si el header es None, no se puede aplicar menú contextual ni acciones de header.
            # Documentar en docs/estandares_visuales.md si ocurre en producción.
            pass

        # --- Pestaña 2: Envíos y Materiales ---
        self.tab_envios = QWidget()
        tab_envios_layout = QVBoxLayout(self.tab_envios)
        self.tabla_envios = QTableWidget()
        self.tabla_envios.setColumnCount(7)
        self.tabla_envios.setHorizontalHeaderLabels([
            "ID", "Obra", "Material", "Cantidad", "Estado", "Quién lo llevó", "Vehículo"
        ])
        self.make_table_responsive(self.tabla_envios)
        tab_envios_layout.addWidget(self.tabla_envios)
        self.tabs.addTab(self.tab_envios, "Envíos y Materiales")

        # Configuración de columnas para Envíos y Materiales
        self.config_path_envios = f"config_logistica_envios_columns.json"
        self.envios_headers = ["ID", "Obra", "Material", "Cantidad", "Estado", "Quién lo llevó", "Vehículo"]
        self.columnas_visibles_envios = self.cargar_config_columnas(self.config_path_envios, self.envios_headers)
        self.aplicar_columnas_visibles(self.tabla_envios, self.envios_headers, self.columnas_visibles_envios)
        header_envios = self.tabla_envios.horizontalHeader()
        if header_envios is not None:
            header_envios.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header_envios.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_envios, self.envios_headers, self.columnas_visibles_envios, self.config_path_envios))
            header_envios.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_envios))
            header_envios.setSectionsMovable(True)
            header_envios.setSectionsClickable(True)
            header_envios.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_envios, self.envios_headers, self.columnas_visibles_envios, self.config_path_envios))
            self.tabla_envios.setHorizontalHeader(header_envios)
        else:
            # EXCEPCIÓN VISUAL: Si el header es None, no se puede aplicar menú contextual ni acciones de header.
            # Documentar en docs/estandares_visuales.md si ocurre en producción.
            pass

        # --- Pestaña 3: Servicios (Service) ---
        self.tab_servicios = QWidget()
        tab_servicios_layout = QVBoxLayout(self.tab_servicios)
        self.tabla_servicios = QTableWidget()
        self.tabla_servicios.setColumnCount(7)
        self.tabla_servicios.setHorizontalHeaderLabels([
            "ID", "Obra", "Dirección", "Tarea", "Presupuestado", "Pagado", "Observaciones"
        ])
        self.make_table_responsive(self.tabla_servicios)
        tab_servicios_layout.addWidget(self.tabla_servicios)
        self.tabs.addTab(self.tab_servicios, "Servicios")

        # Configuración de columnas para Servicios
        self.config_path_servicios = f"config_logistica_servicios_columns.json"
        self.servicios_headers = [
            "ID", "Obra", "Dirección", "Tarea", "Presupuestado", "Pagado", "Observaciones"
        ]
        self.columnas_visibles_servicios = self.cargar_config_columnas(self.config_path_servicios, self.servicios_headers)
        self.aplicar_columnas_visibles(self.tabla_servicios, self.servicios_headers, self.columnas_visibles_servicios)
        header_servicios = self.tabla_servicios.horizontalHeader()
        if header_servicios is not None:
            header_servicios.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header_servicios.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_servicios, self.servicios_headers, self.columnas_visibles_servicios, self.config_path_servicios))
            header_servicios.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_servicios))
            header_servicios.setSectionsMovable(True)
            header_servicios.setSectionsClickable(True)
            header_servicios.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_servicios, self.servicios_headers, self.columnas_visibles_servicios, self.config_path_servicios))
            self.tabla_servicios.setHorizontalHeader(header_servicios)
        else:
            # EXCEPCIÓN VISUAL: Si el header es None, no se puede aplicar menú contextual ni acciones de header.
            # Documentar en docs/estandares_visuales.md si ocurre en producción.
            pass

        # --- Pestaña 4: Mapa (OpenStreetMap + Leaflet) ---
        self.tab_mapa = QWidget()
        tab_mapa_layout = QVBoxLayout(self.tab_mapa)
        if WEBENGINE_AVAILABLE:
            self.webview = QWebEngineView()
            # HTML con OpenStreetMap y Leaflet.js (sin API key), centrado en La Plata
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
            self.boton_instalar_webengine.setIcon(QIcon("img/settings_icon.svg"))
            self.boton_instalar_webengine.setToolTip("Instalar PyQt6-WebEngine ahora")
            self.boton_instalar_webengine.setText("")
            estilizar_boton_icono(self.boton_instalar_webengine)
            self.boton_instalar_webengine.clicked.connect(self.instalar_webengine)
            tab_mapa_layout.addWidget(self.mapa_placeholder)
            tab_mapa_layout.addWidget(self.boton_instalar_webengine)

        # Configuración de columnas para Mapa (si se usa tabla en el futuro)
        # (No aplica por ahora, pero se deja el patrón preparado)

        self.tabs.addTab(self.tab_mapa, "Mapa")

        # Cargar el stylesheet visual moderno para Logística según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        # Botón principal de acción (Agregar)
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/hoja-de-ruta.svg"))  # Icono específico de logística
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar envío")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_agregar.setStyleSheet("")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 160))
        self.boton_agregar.setGraphicsEffect(sombra)
        estilizar_boton_icono(self.boton_agregar)
        self.boton_agregar.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.boton_agregar.setStyleSheet(self.boton_agregar.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
        font = self.boton_agregar.font()
        if font.pointSize() < 12:
            font.setPointSize(12)
        self.boton_agregar.setFont(font)
        self.boton_agregar.setAccessibleName("Botón agregar envío")
        botones_layout.addWidget(self.boton_agregar)
        self.main_layout.addLayout(botones_layout)

        # Refuerzo de accesibilidad en botón principal
        self.boton_agregar.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.boton_agregar.setStyleSheet(self.boton_agregar.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
        font = self.boton_agregar.font()
        if font.pointSize() < 12:
            font.setPointSize(12)
        self.boton_agregar.setFont(font)
        self.boton_agregar.setToolTip("Agregar envío")  # Unificado, siempre presente
        self.boton_agregar.setAccessibleName("Botón agregar envío")
        # Refuerzo de accesibilidad en tablas principales
        for tabla in [self.tabla_obras, self.tabla_envios, self.tabla_servicios]:
            tabla.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            tabla.setStyleSheet(tabla.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")
            tabla.setToolTip("Tabla de datos")
            tabla.setAccessibleName("Tabla principal de logística")
            h_header = tabla.horizontalHeader() if hasattr(tabla, 'horizontalHeader') else None
            if h_header is not None:
                h_header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; font-weight: bold; border-radius: 8px; font-size: 13px; padding: 8px 12px; border: 1px solid #e3e3e3;")
        # Refuerzo de accesibilidad en todos los QLineEdit de la vista
        for tab in [self.tab_obras, self.tab_envios, self.tab_servicios]:
            for widget in tab.findChildren(QLineEdit):
                widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                widget.setStyleSheet(widget.styleSheet() + "\nQLineEdit:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQLineEdit { font-size: 12px; }")
                font = widget.font()
                if font.pointSize() < 12:
                    font.setPointSize(12)
                widget.setFont(font)
                if not widget.toolTip():
                    widget.setToolTip("Campo de texto")
                if not widget.accessibleName():
                    widget.setAccessibleName("Campo de texto de logística")
        # Refuerzo en propiedades QLineEdit
        for prop in [self.buscar_input, self.id_item_input]:
            prop.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            prop.setStyleSheet(prop.styleSheet() + "\nQLineEdit:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQLineEdit { font-size: 12px; }")
            font = prop.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            prop.setFont(font)
            prop.setToolTip("Campo de búsqueda o ID")
            prop.setAccessibleName("Campo de búsqueda o ID de logística")
        # Refuerzo de accesibilidad en todos los QLabel de la vista
        for tab in [self.tab_obras, self.tab_envios, self.tab_servicios]:
            for widget in tab.findChildren(QLabel):
                font = widget.font()
                if font.pointSize() < 12:
                    font.setPointSize(12)
                widget.setFont(font)
        # Márgenes y padding en layouts según estándar
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)
        for tab in [self.tab_obras, self.tab_envios, self.tab_servicios]:
            layout = tab.layout() if hasattr(tab, 'layout') else None
            if layout is not None:
                layout.setContentsMargins(24, 20, 24, 20)
                layout.setSpacing(16)
        # EXCEPCIÓN: Si algún input requiere estilo especial por UX, debe estar documentado aquí y en docs/estandares_visuales.md
        # --- FIN DE BLOQUE DE ESTÁNDAR ---

        # --- FEEDBACK VISUAL INMEDIATO (QLabel) ---
        # Estándar: único label de feedback visual, accesible, con estilos modernos y oculto por defecto.
        # Usar siempre self.feedback_label para feedback visual inmediato.
        self.feedback_label = QLabel()
        self.feedback_label.setVisible(False)
        self.feedback_label.setStyleSheet("QLabel { font-size: 13px; border-radius: 8px; padding: 8px; font-weight: 500; background: #f1f5f9; }")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.feedback_label.setAccessibleName("Feedback visual de Logística")
        self.main_layout.addWidget(self.feedback_label)
        self._feedback_timer = None  # Temporizador para ocultar feedback automáticamente

        # --- FEEDBACK DE PROGRESO (QProgressBar) ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Modo indeterminado (spinner)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar { border-radius: 8px; height: 18px; background: #e3f6fd; } QProgressBar::chunk { background: #2563eb; border-radius: 8px; }")
        self.progress_bar.setAccessibleName("Barra de progreso de Logística")
        self.main_layout.addWidget(self.progress_bar)

    def mostrar_feedback(self, mensaje, tipo="info", auto_ocultar=True, segundos=4):
        """
        Muestra un mensaje de feedback visual accesible y moderno en el label de feedback.
        - tipo: 'info', 'exito', 'advertencia', 'error'.
        - auto_ocultar: si True, oculta automáticamente tras 'segundos'.
        """
        colores = {
            "info": "#2563eb",
            "exito": "#22c55e",
            "advertencia": "#fbbf24",
            "error": "#ef4444"
        }
        color = colores.get(tipo, "#2563eb")
        iconos = {
            "info": "ℹ️ ",
            "exito": "✅ ",
            "advertencia": "⚠️ ",
            "error": "❌ "
        }
        icono = iconos.get(tipo, "ℹ️ ")
        # Limpiar mensaje anterior y estilos
        self.feedback_label.clear()
        self.feedback_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px; border-radius: 8px; padding: 8px; background: #f1f5f9;")
        self.feedback_label.setText(f"{icono}{mensaje}")
        self.feedback_label.setVisible(True)
        self.feedback_label.setAccessibleDescription(f"Mensaje de feedback tipo {tipo}")
        # Ocultado automático con temporizador
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
        self.feedback_label.clear()
        self.feedback_label.setVisible(False)
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
            self.mostrar_feedback("Exportación completada con éxito", tipo="exito")
        except Exception as e:
            self.mostrar_feedback(f"Error al exportar: {e}", tipo="error")
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
        header = tabla.horizontalHeader()
        if header is not None:
            pos = header.sectionPosition(idx)
            global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
            self.mostrar_menu_columnas(tabla, headers, columnas_visibles, config_path, global_pos)

    def toggle_columna(self, tabla, idx, header, columnas_visibles, config_path, checked):
        columnas_visibles[header] = checked
        tabla.setColumnHidden(idx, not checked)
        self.guardar_config_columnas(config_path, columnas_visibles)

    def auto_ajustar_columna(self, tabla, idx):
        tabla.resizeColumnToContents(idx)

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
