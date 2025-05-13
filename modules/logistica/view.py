from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox, QTabWidget, QTextEdit
from PyQt6.QtGui import QIcon, QColor, QAction
from PyQt6.QtCore import QSize, Qt, QPoint
import json
import os
from functools import partial
from core.table_responsive_mixin import TableResponsiveMixin

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False

class LogisticaView(QWidget, TableResponsiveMixin):
    def __init__(self, usuario_actual="default"):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Tabs principales
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # --- Pestaña 1: Obras y Direcciones ---
        self.tab_obras = QWidget()
        tab_obras_layout = QVBoxLayout(self.tab_obras)
        self.tabla_obras = QTableWidget()
        self.tabla_obras.setColumnCount(5)
        self.tabla_obras.setHorizontalHeaderLabels(["ID", "Obra", "Dirección", "Estado", "Cliente"])
        self.make_table_responsive(self.tabla_obras)
        tab_obras_layout.addWidget(self.tabla_obras)
        self.tabs.addTab(self.tab_obras, "Obras y Direcciones")

        # --- Pestaña 2: Envíos y Materiales ---
        self.tab_envios = QWidget()
        tab_envios_layout = QVBoxLayout(self.tab_envios)
        self.tabla_envios = QTableWidget()
        self.tabla_envios.setColumnCount(5)
        self.tabla_envios.setHorizontalHeaderLabels(["ID", "Obra", "Material", "Cantidad", "Estado"])
        self.make_table_responsive(self.tabla_envios)
        tab_envios_layout.addWidget(self.tabla_envios)
        self.tabs.addTab(self.tab_envios, "Envíos y Materiales")

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

        # --- Pestaña 4: Mapa (Google Maps) ---
        self.tab_mapa = QWidget()
        tab_mapa_layout = QVBoxLayout(self.tab_mapa)
        if WEBENGINE_AVAILABLE:
            self.webview = QWebEngineView()
            # HTML básico con Google Maps y pines de ejemplo (requiere API key real para producción)
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Mapa de Obras</title>
                <style>html, body, #map {{ height: 100%; margin: 0; padding: 0; }}</style>
                <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY"></script>
                <script>
                function initMap() {{
                    var map = new google.maps.Map(document.getElementById('map'), {{
                        zoom: 10,
                        center: {{lat: -34.6037, lng: -58.3816}} // Buenos Aires ejemplo
                    }});
                    var obras = [
                        {{lat: -34.6037, lng: -58.3816, nombre: 'Obra 1'}},
                        {{lat: -34.6090, lng: -58.3840, nombre: 'Obra 2'}}
                    ];
                    obras.forEach(function(obra) {{
                        var marker = new google.maps.Marker({{
                            position: {{lat: obra.lat, lng: obra.lng}},
                            map: map,
                            title: obra.nombre
                        }});
                    }});
                }}
                </script>
            </head>
            <body onload="initMap()">
                <div id="map" style="width:100%;height:100vh;"></div>
            </body>
            </html>
            '''
            self.webview.setHtml(html)
            tab_mapa_layout.addWidget(self.webview)
        else:
            self.mapa_placeholder = QTextEdit()
            self.mapa_placeholder.setReadOnly(True)
            self.mapa_placeholder.setText("[Aquí se mostrará el mapa con los pines de cada obra. Instala PyQt6-WebEngine para habilitar Google Maps]")
            tab_mapa_layout.addWidget(self.mapa_placeholder)
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
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        self.setLayout(self.layout)

    def cargar_config_columnas(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {header: True for header in self.envios_headers}

    def guardar_config_columnas(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "Configuración guardada", "La configuración de columnas se ha guardado correctamente.")

    def aplicar_columnas_visibles(self):
        for idx, header in enumerate(self.envios_headers):
            visible = self.columnas_visibles.get(header, True)
            self.tabla_envios.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        menu = QMenu(self)
        for idx, header in enumerate(self.envios_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        menu.exec(self.tabla_envios.horizontalHeader().mapToGlobal(pos))

    def mostrar_menu_columnas_header(self, idx):
        pos = self.tabla_envios.horizontalHeader().sectionPosition(idx)
        header = self.tabla_envios.horizontalHeader()
        global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
        self.mostrar_menu_columnas(global_pos)

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_envios.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()

    def auto_ajustar_columna(self, idx):
        self.tabla_envios.resizeColumnToContents(idx)

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
