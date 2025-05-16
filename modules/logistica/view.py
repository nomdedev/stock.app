from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox, QTabWidget, QTextEdit, QTableWidgetItem
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
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

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
        header_obras.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header_obras.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_obras, self.obras_headers, self.columnas_visibles_obras, self.config_path_obras))
        header_obras.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_obras))
        header_obras.setSectionsMovable(True)
        header_obras.setSectionsClickable(True)
        header_obras.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_obras, self.obras_headers, self.columnas_visibles_obras, self.config_path_obras))
        self.tabla_obras.setHorizontalHeader(header_obras)

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
        header_envios.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header_envios.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_envios, self.envios_headers, self.columnas_visibles_envios, self.config_path_envios))
        header_envios.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_envios))
        header_envios.setSectionsMovable(True)
        header_envios.setSectionsClickable(True)
        header_envios.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_envios, self.envios_headers, self.columnas_visibles_envios, self.config_path_envios))
        self.tabla_envios.setHorizontalHeader(header_envios)

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
        header_servicios.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header_servicios.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_servicios, self.servicios_headers, self.columnas_visibles_servicios, self.config_path_servicios))
        header_servicios.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_servicios))
        header_servicios.setSectionsMovable(True)
        header_servicios.setSectionsClickable(True)
        header_servicios.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_servicios, self.servicios_headers, self.columnas_visibles_servicios, self.config_path_servicios))
        self.tabla_servicios.setHorizontalHeader(header_servicios)

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
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        self.main_layout.addLayout(botones_layout)

        self.setLayout(self.main_layout)

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
        """Carga automáticamente las obras en la tabla de Obras y Direcciones de Logística."""
        self.tabla_obras.setRowCount(0)
        for obra in obras:
            row = self.tabla_obras.rowCount()
            self.tabla_obras.insertRow(row)
            for col, value in enumerate(obra):
                self.tabla_obras.setItem(row, col, QTableWidgetItem(str(value)))
            # Si faltan columnas (por ejemplo, control/logística), rellenar con vacío
            for col in range(len(obra), 8):
                self.tabla_obras.setItem(row, col, QTableWidgetItem(""))

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
        menu.exec(tabla.horizontalHeader().mapToGlobal(pos))

    def mostrar_menu_columnas_header(self, tabla, headers, columnas_visibles, config_path, idx):
        header = tabla.horizontalHeader()
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
