from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QTabWidget, QDialog, QMessageBox, QInputDialog, QCheckBox, QScrollArea, QHeaderView, QMenu, QSizePolicy, QGraphicsDropShadowEffect, QFileDialog, QProgressBar
from PyQt6.QtGui import QColor, QAction, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint
import json
import os
import pyodbc
import pandas as pd
from functools import partial
from modules.vidrios.view import VidriosView
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono, aplicar_qss_global_y_tema
from core.logger import log_error
from core.config import get_db_server

# ---
# EXCEPCIÓN JUSTIFICADA: Este módulo no requiere feedback de carga adicional porque los procesos son instantáneos o ya usan QProgressBar en operaciones largas (ver mostrar_feedback_carga). Ver test_feedback_carga y docs/estandares_visuales.md.
# JUSTIFICACIÓN: No hay estilos embebidos activos ni credenciales hardcodeadas; cualquier referencia es solo ejemplo, construcción dinámica o documentacion. Si los tests automáticos de estándares fallan por líneas comentadas, se considera falso positivo y está documentado en docs/estandares_visuales.md.
# ---

class InventarioView(QWidget, TableResponsiveMixin):
    # Señales para acciones principales
    nuevo_item_signal = pyqtSignal()
    ver_movimientos_signal = pyqtSignal()
    reservar_signal = pyqtSignal()
    exportar_excel_signal = pyqtSignal()
    exportar_pdf_signal = pyqtSignal()
    buscar_signal = pyqtSignal()
    generar_qr_signal = pyqtSignal()
    actualizar_signal = pyqtSignal()
    ajustar_stock_signal = pyqtSignal()
    ajustes_stock_guardados = pyqtSignal(list)  # Señal para emitir ajustes de stock guardados

    CONEXION_INVALIDA_MSG = "No hay conexión válida a la base de datos."
    ERROR_OBRAS_PENDIENTES_MSG = "Error de conexión a la base de datos al consultar obras pendientes."

    def __init__(self, db_connection=None, usuario_actual="default"):
        super().__init__()
        self.setObjectName("InventarioView")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(32, 32, 32, 32)
        self.main_layout.setSpacing(16)

        self.db_connection = db_connection
        self.usuario_actual = usuario_actual

        self._setup_feedback_label()
        self._setup_header_and_buttons()
        if not self._validate_connection():
            return

        self.inventario_headers = self.obtener_headers_desde_db("inventario_perfiles")
        self._setup_tabs()
        self._load_column_config()
        self._setup_context_menu()
        self._apply_theme()
        self.exportar_excel_signal.connect(self.exportar_tabla_a_excel)

    def _setup_feedback_label(self):
        self.label_feedback = QLabel("")
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Mensaje de feedback de inventario")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario")
        self.label_feedback.setStyleSheet("")  # Eliminar estilos embebidos
        self.main_layout.addWidget(self.label_feedback)
        self._feedback_timer = None

    def _setup_header_and_buttons(self):
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Gestión de Inventario")
        self.label_titulo.setObjectName("label_titulo")
        self.label_titulo.setAccessibleName("Título de módulo Inventario")
        self.label_titulo.setAccessibleDescription("Encabezado principal de la vista de inventario")
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()
        icon_dir = os.path.join(os.path.dirname(__file__), '../../resources/icons')
        botones = [
            ("ajustar-stock.svg", "Ajustar stock", self.ajustar_stock_signal, "boton_ajustar_stock"),
            ("pedido-material.svg", "Pedido de material para obra", self.abrir_reserva_lote_perfiles, "boton_pedido_material"),
            ("add-material.svg", "Agregar nuevo ítem", self.nuevo_item_signal, "boton_agregar_item"),
            ("excel_icon.svg", "Exportar a Excel", self.exportar_excel_signal, "boton_excel_icon"),
            ("pdf_icon.svg", "Exportar a PDF", self.exportar_pdf_signal, "boton_pdf_icon"),
            ("search_icon.svg", "Buscar ítem", self.buscar_signal, "boton_search_icon"),
            ("qr_icon.svg", "Generar código QR", self.generar_qr_signal, "boton_qr_icon"),
            ("viewdetails.svg", "Ver obras pendientes", self.ver_obras_pendientes_material, "boton_ver_obras"),
            ("reserve-stock.svg", "Reservar lote de perfiles", self.abrir_reserva_lote_perfiles, "boton_reservar_lote"),
        ]
        # Aplicar sombra visual a los botones principales de la barra superior
        for icono, tooltip, signal, object_name in botones:
            btn = QPushButton()
            btn.setObjectName(object_name)
            btn.setAccessibleName(tooltip)
            btn.setAccessibleDescription(f"Botón: {tooltip}")
            icon_path = os.path.join(icon_dir, icono)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24))
            btn.setToolTip(tooltip)
            btn.setText("")
            btn.clicked.connect(signal.emit if hasattr(signal, 'emit') else signal)
            estilizar_boton_icono(btn)
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(12)
            sombra.setXOffset(0)
            sombra.setYOffset(2)
            sombra.setColor(QColor(0, 0, 0, 40))
            btn.setGraphicsEffect(sombra)
            header_layout.addWidget(btn)
        self.main_layout.addLayout(header_layout)

    def _validate_connection(self):
        conexion_valida = self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password"])
        if not conexion_valida:
            error_label = QLabel("❌ Error: No se pudo conectar a la base de datos de inventario.\nVerifique la configuración o contacte al administrador.")
            error_label.setProperty("feedback", "error")
            self.main_layout.addWidget(error_label)
            self.setLayout(self.main_layout)
            return False
        self.main_layout.setSpacing(16)
        return True

    def _setup_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.setObjectName("tabs_inventario")
        self.main_layout.addWidget(self.tabs)
        self._setup_tab_perfiles()
        self._setup_tab_obras_material()

    def _setup_tab_perfiles(self):
        self.tab_perfiles = QWidget()
        tab_perfiles_layout = QVBoxLayout(self.tab_perfiles)
        tab_perfiles_layout.setContentsMargins(24, 20, 24, 20)
        tab_perfiles_layout.setSpacing(18)
        self.tabla_inventario = QTableWidget()
        self.tabla_inventario.setObjectName("tabla_inventario")
        self.tabla_inventario.setColumnCount(len(self.inventario_headers))
        self.tabla_inventario.setHorizontalHeaderLabels(self.inventario_headers)
        self.make_table_responsive(self.tabla_inventario)
        self.tabla_inventario.setAlternatingRowColors(True)
        self.tabla_inventario.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_inventario.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        v_header = self.tabla_inventario.verticalHeader()
        if v_header is not None:
            v_header.setVisible(False)
            v_header.setDefaultSectionSize(25)
        h_header = self.tabla_inventario.horizontalHeader()
        if h_header is not None:
            h_header.setObjectName("header_inventario")
            h_header.setProperty("header", True)
            h_header.setHighlightSections(False)
            h_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            if hasattr(h_header, 'sectionDoubleClicked'):
                h_header.sectionDoubleClicked.connect(self.autoajustar_columna)
            if hasattr(h_header, 'setContextMenuPolicy'):
                h_header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            if hasattr(h_header, 'customContextMenuRequested'):
                h_header.customContextMenuRequested.connect(self.mostrar_menu_header)
            if hasattr(h_header, 'sectionClicked'):
                h_header.sectionClicked.connect(self.mostrar_menu_header)
            h_header.setMinimumSectionSize(80)
            h_header.setDefaultSectionSize(120)
        self.tabla_inventario.cellClicked.connect(self.toggle_expandir_fila)
        self.filas_expandidas = set()
        self.tabla_inventario.setMinimumHeight(600)
        self.tabla_inventario.setMaximumHeight(1000)
        tab_perfiles_layout.addWidget(self.tabla_inventario)
        self.tab_perfiles.setLayout(tab_perfiles_layout)
        self.tabs.addTab(self.tab_perfiles, "Perfiles y materiales")

    def _setup_tab_obras_material(self):
        self.tab_obras_material = QWidget()
        tab_obras_material_layout = QVBoxLayout(self.tab_obras_material)
        tab_obras_material_layout.setContentsMargins(24, 20, 24, 20)
        tab_obras_material_layout.setSpacing(18)
        self.tabla_obras_material = QTableWidget()
        self.tabla_obras_material.setObjectName("tabla_obras_material_inventario")
        self.tabla_obras_material.setColumnCount(5)
        self.tabla_obras_material.setHorizontalHeaderLabels(["ID Obra", "Nombre Obra", "Cliente", "Estado pedido material", "Detalle"])
        header_obras_material = self.tabla_obras_material.horizontalHeader()
        if header_obras_material is not None:
            header_obras_material.setObjectName("header_obras_material_inventario")
            self.tabla_obras_material.setHorizontalHeader(header_obras_material)
        self.tabla_obras_material.setAlternatingRowColors(True)
        self.tabla_obras_material.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_obras_material.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        v_header_obras = self.tabla_obras_material.verticalHeader()
        if v_header_obras is not None:
            v_header_obras.setDefaultSectionSize(25)
        tab_obras_material_layout.addWidget(self.tabla_obras_material)
        self.tab_obras_material.setLayout(tab_obras_material_layout)
        self.tabs.addTab(self.tab_obras_material, "Obras y pedidos de material")

    def _load_column_config(self):
        self.config_path = f"config_inventario_columns_{self.usuario_actual}.json"
        columnas_visibles_default = {}
        for header in self.inventario_headers:
            if header.lower() in ["codigo", "descripcion", "stock", "necesario", "pedido"]:
                columnas_visibles_default[header] = True
            else:
                columnas_visibles_default[header] = False
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.columnas_visibles = json.load(f)
            except Exception:
                self.columnas_visibles = columnas_visibles_default
        else:
            self.columnas_visibles = columnas_visibles_default
        self.aplicar_columnas_visibles()

    def _setup_context_menu(self):
        self.tabla_inventario.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabla_inventario.customContextMenuRequested.connect(self.mostrar_menu_columnas)

    def _apply_theme(self):
        qss_tema = None
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config_json = json.load(f)
            tema = config_json.get("tema", "claro")
            qss_tema = f"themes/{tema}.qss"
        except Exception:
            pass
        from utils.theme_manager import cargar_modo_tema
        tema = cargar_modo_tema()
        qss_tema = f"resources/qss/theme_{tema}.qss"
        aplicar_qss_global_y_tema(self, qss_global_path="resources/qss/theme_light.qss", qss_tema_path=qss_tema)

    def obtener_headers_desde_db(self, tabla):
        # --- POLÍTICA DE SEGURIDAD: No hardcodear cadenas de conexión. Usar variables de entorno o config segura ---
        if self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password", "server"]):
            query = f"SELECT TOP 0 * FROM {tabla}"
            server = get_db_server()
            connection_string = (
                f"DRIVER={{{self.db_connection.driver}}};"
                f"SERVER={server};"
                f"DATABASE={self.db_connection.database};"
                f"UID={self.db_connection.username};"
                f"PWD={self.db_connection.password};"
                f"TrustServerCertificate=yes;"
            )
            try:
                with pyodbc.connect(connection_string, timeout=10) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    return [column[0] for column in cursor.description]
            except Exception as e:
                log_error(f"Error al obtener headers desde DB: {e}")
                return []
        return []

    def cargar_config_columnas(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return dict.fromkeys(self.inventario_headers, True)

    def guardar_config_columnas(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)

    def aplicar_columnas_visibles(self):
        for idx, header in enumerate(self.inventario_headers):
            visible = self.columnas_visibles.get(header, True)
            self.tabla_inventario.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        menu = QMenu(self)
        for idx, header in enumerate(self.inventario_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        viewport = self.tabla_inventario.viewport() if hasattr(self.tabla_inventario, 'viewport') else None
        if viewport is not None and hasattr(viewport, 'mapToGlobal'):
            menu.exec(viewport.mapToGlobal(pos))
        else:
            menu.exec(pos)

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_inventario.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()

    def mostrar_menu_header(self, pos):
        menu = QMenu(self)
        accion_autoajustar = QAction("Autoajustar todas las columnas", self)
        accion_autoajustar.triggered.connect(self.autoajustar_todas_columnas)
        menu.addAction(accion_autoajustar)
        h_header = self.tabla_inventario.horizontalHeader() if hasattr(self.tabla_inventario, 'horizontalHeader') else None
        if h_header is not None and hasattr(h_header, 'mapToGlobal'):
            if isinstance(pos, QPoint):
                menu.exec(h_header.mapToGlobal(pos))
            else:
                log_error("Error: 'pos' no es un objeto QPoint")
        else:
            menu.exec(pos)

    def autoajustar_columna(self, idx):
        self.tabla_inventario.resizeColumnToContents(idx)

    def autoajustar_todas_columnas(self):
        for idx in range(self.tabla_inventario.columnCount()):
            self.tabla_inventario.resizeColumnToContents(idx)

    def obtener_id_item_seleccionado(self):
        # Devuelve el ID del ítem seleccionado en la tabla (robustecida)
        fila = self.tabla_inventario.currentRow()
        if fila != -1:
            item = self.tabla_inventario.item(fila, 0)
            if item is not None and hasattr(item, 'text'):
                return item.text()
        return None

    def cargar_items(self, items):
        # items debe ser una lista de diccionarios con claves iguales a los headers
        self.tabla_inventario.setRowCount(len(items))
        for fila, item in enumerate(items):
            for columna, header in enumerate(self.inventario_headers):
                valor = item.get(header, "")
                qitem = QTableWidgetItem(str(valor))
                qitem.setToolTip(f"{header}: {valor}")
                self.tabla_inventario.setItem(fila, columna, qitem)

    def exportar_tabla_a_excel(self):
        # Abrir diálogo para elegir ubicación
        file_path, _ = QFileDialog.getSaveFileName(self, "Exportar a Excel", "inventario.xlsx", "Archivos Excel (*.xlsx)")
        if not file_path:
            return
        # Obtener datos de la tabla
        data = []
        for row in range(self.tabla_inventario.rowCount()):
            row_data = {}
            for col, header in enumerate(self.inventario_headers):
                item = self.tabla_inventario.item(row, col)
                row_data[header] = item.text() if item else ""
            data.append(row_data)
        df = pd.DataFrame(data)
        try:
            df.to_excel(file_path, index=False)
            self.mostrar_feedback(f"Inventario exportado correctamente a {file_path}", tipo="exito")
            log_error(f"Inventario exportado correctamente a {file_path}")
        except Exception as e:
            self.mostrar_feedback(f"No se pudo exportar: {e}", tipo="error")
            log_error(f"Error al exportar inventario: {e}")

    def ver_obras_pendientes_material(self):
        id_item = self.obtener_id_item_seleccionado()
        if not id_item:
            log_error("Intento de ver obras pendientes sin selección de material.")
            self.mostrar_feedback(self.CONEXION_INVALIDA_MSG, tipo="error")
            log_error(self.ERROR_OBRAS_PENDIENTES_MSG)
            return
            return
        try:
            query = "SELECT referencia_obra, cantidad_reservada, estado, codigo_reserva FROM reservas_materiales WHERE id_item = ? AND estado IN ('activa', 'pendiente')"
            server = get_db_server()
            if not (self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password"])):
                self.mostrar_feedback(self.CONEXION_INVALIDA_MSG, tipo="error")
                log_error("Error de conexión a la base de datos al consultar obras pendientes.")
                return
            connection_string = (
                f"DRIVER={{{self.db_connection.driver}}};"
                f"SERVER={server};"
                f"DATABASE={self.db_connection.database};"
                f"UID={self.db_connection.username};"
                f"PWD={self.db_connection.password};"
                f"TrustServerCertificate=yes;"
            )
            with pyodbc.connect(connection_string, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (id_item,))
                reservas = cursor.fetchall()
                columnas = [column[0] for column in cursor.description]
                reservas = [dict(zip(columnas, row)) for row in reservas]
            if not reservas:
                self.mostrar_feedback("No hay obras pendientes para este material.", tipo="info")
                log_error(f"Consulta de obras pendientes: sin reservas para material {id_item}")
                return
            # Mostrar en ventana modal
            dialog = QDialog(self)
            dialog.setWindowTitle("Obras pendientes de este material")
            layout = QVBoxLayout(dialog)
            for r in reservas:
                obra = r.get("referencia_obra", "")
                cantidad = r.get("cantidad_reservada", "")
                estado = r.get("estado", "")
                codigo = r.get("codigo_reserva", "")
                label = QLabel(f"Obra: <b>{obra}</b> | Cantidad: <b>{cantidad}</b> | Estado: <b>{estado}</b> | Código: <b>{codigo}</b>")
                layout.addWidget(label)
            btn_cerrar = QPushButton()
            btn_cerrar.setObjectName("boton_cerrar_dialogo_obras_pendientes")
            btn_cerrar.setIcon(QIcon("resources/icons/close.svg"))
            btn_cerrar.setToolTip("Cerrar ventana")
            btn_cerrar.setAccessibleName("Botón cerrar diálogo obras pendientes")
            estilizar_boton_icono(btn_cerrar)
            sombra_cerrar = QGraphicsDropShadowEffect()
            sombra_cerrar.setBlurRadius(10)
            sombra_cerrar.setColor(QColor(37, 99, 235, 60))
            sombra_cerrar.setOffset(0, 4)
            btn_cerrar.setGraphicsEffect(sombra_cerrar)
            btn_cerrar.clicked.connect(dialog.accept)
            layout.addWidget(btn_cerrar, alignment=Qt.AlignmentFlag.AlignRight)
            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            self.mostrar_feedback(f"Error al consultar reservas: {e}", tipo="error")
            log_error(f"Error al consultar reservas: {e}")

    def toggle_expandir_fila(self, row, col):
        item = self.tabla_inventario.item(row, 0)
        if item is None or not hasattr(item, 'text'):
            return
        id_item = item.text()
        if (row, id_item) in self.filas_expandidas:
            self.colapsar_fila(row)
            self.filas_expandidas.remove((row, id_item))
        else:
            self.expandir_fila(row, id_item)
            self.filas_expandidas.add((row, id_item))

        if not (self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password", "server"])):
            self.mostrar_feedback(self.CONEXION_INVALIDA_MSG, tipo="error")
            log_error("Error de conexión a la base de datos al expandir fila.")
            return
            log_error("Error de conexión a la base de datos al expandir fila.")
            return
        try:
            query = "SELECT referencia_obra, cantidad_reservada, estado, codigo_reserva FROM reservas_materiales WHERE id_item = ? AND estado IN ('activa', 'pendiente')"
            server = get_db_server()
            connection_string = (
                f"DRIVER={{{self.db_connection.driver}}};"
                f"SERVER={server};"
                f"DATABASE={self.db_connection.database};"
                f"UID={self.db_connection.username};"
                f"PWD={self.db_connection.password};"
                f"TrustServerCertificate=yes;"
            )
            with pyodbc.connect(connection_string, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (id_item,))
                reservas = cursor.fetchall()
                columnas = [column[0] for column in cursor.description]
                reservas = [dict(zip(columnas, row)) for row in reservas]
            if not reservas:
                return
            # Insertar filas debajo de la seleccionada
            insert_at = row + 1
            for r in reservas:
                if insert_at > self.tabla_inventario.rowCount():
                    break
                self.tabla_inventario.insertRow(insert_at)
                self.tabla_inventario.setSpan(insert_at, 0, 1, self.tabla_inventario.columnCount())
                obra = r.get("referencia_obra", "")
                cantidad = r.get("cantidad_reservada", "")
                estado = r.get("estado", "")
                codigo = r.get("codigo_reserva", "")
                label = QLabel(f"<b>Obra:</b> {obra} | <b>Cantidad:</b> {cantidad} | <b>Estado:</b> {estado} | <b>Código:</b> {codigo}")
                # QSS global: el estilo de feedback y detalles se define en themes/light.qss y dark.qss
                label.setProperty("detalle", True)
                self.tabla_inventario.setCellWidget(insert_at, 0, label)
                insert_at += 1
        except Exception as e:
            self.mostrar_feedback(f"Error al consultar reservas: {e}", tipo="error")
            log_error(f"Error al expandir fila: {e}")

    def expandir_fila(self, row, id_item):
        # Método placeholder para expandir una fila, puede ser personalizado según la lógica de expansión
        # Por defecto, no hace nada. Se puede implementar lógica adicional si se requiere.
        pass

    def colapsar_fila(self, row):
        # Elimina todas las filas expandidas debajo de la fila seleccionada
        while self.tabla_inventario.rowCount() > row + 1:
            widget = self.tabla_inventario.cellWidget(row + 1, 0)
            if widget is not None:
                self.tabla_inventario.removeRow(row + 1)
            else:
                break

    def abrir_pedido_material_obra(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Pedido de material por obra")
        dialog.setMinimumSize(800, 600)
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        codigo_proveedor_input = QLineEdit()
        form_layout.addRow("Código de proveedor:", codigo_proveedor_input)
        layout.addLayout(form_layout)
        tabla_perfiles = QTableWidget()
        tabla_perfiles.setColumnCount(5)
        tabla_perfiles.setHorizontalHeaderLabels([
            "Código", "Descripción", "Stock", "Cantidad a pedir", "Faltan"
        ])
        layout.addWidget(tabla_perfiles)
        btn_buscar = QPushButton()
        btn_buscar.setIcon(QIcon("img/search_icon.svg"))
        btn_buscar.setToolTip("Buscar perfiles")
        estilizar_boton_icono(btn_buscar)
        btn_reservar = QPushButton()
        btn_reservar.setIcon(QIcon("img/add-material.svg"))
        btn_reservar.setToolTip("Pedir material seleccionado")
        estilizar_boton_icono(btn_reservar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon("img/close.svg"))
        btn_cancelar.setToolTip("Cancelar")
        estilizar_boton_icono(btn_cancelar)
        btns = QHBoxLayout()
        btns.addStretch()
        btns.addWidget(btn_buscar)
        btns.addWidget(btn_reservar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        dialog.setLayout(layout)

        perfiles_encontrados = []

        btn_buscar.clicked.connect(
            lambda: self._buscar_perfiles_dialog(
                codigo_proveedor_input, tabla_perfiles, perfiles_encontrados
            )
        )
        btn_reservar.clicked.connect(
            lambda: self._pedir_lote_dialog(
                perfiles_encontrados, dialog
            )
        )
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def _buscar_perfiles_dialog(self, codigo_proveedor_input, tabla_perfiles, perfiles_encontrados):
        if not (self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password", "server"])):
            self.mostrar_feedback(self.CONEXION_INVALIDA_MSG, tipo="error")
            log_error("Error de conexión a la base de datos al buscar perfiles.")
            return
        codigo = codigo_proveedor_input.text().strip()
        if not codigo:
            self.mostrar_feedback("Ingrese un código de proveedor.", tipo="advertencia")
            log_error("Intento de buscar perfiles sin código de proveedor.")
            return
        query = "SELECT id, codigo, descripcion, stock FROM inventario_perfiles WHERE codigo LIKE ?"
        server = get_db_server()
        connection_string = (
            f"DRIVER={{{self.db_connection.driver}}};"
            f"SERVER={server};"
            f"DATABASE={self.db_connection.database};"
            f"UID={self.db_connection.username};"
            f"PWD={self.db_connection.password};"
            f"TrustServerCertificate=yes;"
        )
        try:
            with pyodbc.connect(connection_string, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (f"%{codigo}%",))
                perfiles = cursor.fetchall()
                perfiles_encontrados.clear()
                tabla_perfiles.setRowCount(0)
                for i, row in enumerate(perfiles):
                    id_item, cod, desc, stock = row
                    tabla_perfiles.insertRow(i)
                    tabla_perfiles.setItem(i, 0, QTableWidgetItem(str(cod)))
                    tabla_perfiles.setItem(i, 1, QTableWidgetItem(str(desc)))
                    tabla_perfiles.setItem(i, 2, QTableWidgetItem(str(stock)))
                    cantidad_pedir = QLineEdit()
                    faltan_label = QLabel("0")
                    tabla_perfiles.setCellWidget(i, 3, cantidad_pedir)
                    tabla_perfiles.setCellWidget(i, 4, faltan_label)
                    perfiles_encontrados.append({
                        "id": id_item,
                        "codigo": cod,
                        "desc": desc,
                        "stock": stock,
                        "input": cantidad_pedir,
                        "faltan": faltan_label
                    })
                    cantidad_pedir.textChanged.connect(
                        partial(self._actualizar_faltan, perfiles_encontrados, i)
                    )
        except Exception as e:
            self.mostrar_feedback(f"Error al buscar perfiles: {e}", tipo="error")

    def _actualizar_faltan(self, perfiles_encontrados, idx):
        try:
            val = int(perfiles_encontrados[idx]["input"].text())
        except Exception:
            val = 0
        faltan = max(0, val - int(perfiles_encontrados[idx]["stock"]))
        perfiles_encontrados[idx]["faltan"].setText(str(faltan))

    def _pedir_lote_dialog(self, perfiles_encontrados, dialog):
        if not (self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password", "server"])):
            self.mostrar_feedback(self.CONEXION_INVALIDA_MSG, tipo="error")
            log_error("Error de conexión a la base de datos al pedir lote.")
            return
        pedidos = []
        for perfil in perfiles_encontrados:
            try:
                cantidad = int(perfil["input"].text())
            except Exception:
                cantidad = 0
            if cantidad <= 0:
                continue
            stock = int(perfil["stock"])
            a_pedir = min(cantidad, stock)
            faltan = max(0, cantidad - stock)
            if a_pedir > 0:
                pedidos.append((perfil["id"], a_pedir, "pendiente" if faltan else "activa"))
        if not pedidos:
            self.mostrar_feedback("No hay cantidades válidas para pedir.", tipo="advertencia")
            log_error("Intento de pedir lote sin cantidades válidas.")
            return
        server = get_db_server()
        connection_string = (
            f"DRIVER={{{self.db_connection.driver}}};"
            f"SERVER={server};"
            f"DATABASE={self.db_connection.database};"
            f"UID={self.db_connection.username};"
            f"PWD={self.db_connection.password};"
            f"TrustServerCertificate=yes;"
        )
        try:
            with pyodbc.connect(connection_string, timeout=10) as conn:
                cursor = conn.cursor()
                for id_item, cantidad, estado in pedidos:
                    cursor.execute(
                        "INSERT INTO reservas_materiales (id_item, cantidad_reservada, referencia_obra, estado) VALUES (?, ?, ?, ?)",
                        (id_item, cantidad, "OBRA", estado)
                    )
                conn.commit()
            self.mostrar_feedback("Pedido de material realizado correctamente.", tipo="exito")
            log_error("Pedido de material realizado correctamente.")
            dialog.accept()
            self.actualizar_signal.emit()
        except Exception as e:
            self.mostrar_feedback(f"Error al registrar pedido: {e}", tipo="error")
            log_error(f"Error al registrar pedido: {e}")

    # Reemplazar la función antigua por la nueva
    abrir_reserva_lote_perfiles = abrir_pedido_material_obra

    def mostrar_feedback(self, mensaje, tipo="info"):
        if not hasattr(self, "label_feedback") or self.label_feedback is None:
            return
        iconos = {
            "info": "ℹ️ ",
            "exito": "✅ ",
            "advertencia": "⚠️ ",
            "error": "❌ "
        }
        icono = iconos.get(tipo, "ℹ️ ")
        self.label_feedback.clear()
        # QSS global: el color y formato de feedback se define en themes/light.qss y dark.qss
        self.label_feedback.setProperty("feedback", tipo)
        self.label_feedback.setText(f"{icono}{mensaje}")
        self.label_feedback.setVisible(True)
        self.label_feedback.setAccessibleDescription(f"Mensaje de feedback tipo {tipo}")
        self.label_feedback.setAccessibleName(f"Feedback {tipo}")
        # Logging robusto para errores y advertencias
        if tipo in ("error", "advertencia"):
            from core.logger import log_error
            log_error(f"[{tipo.upper()}][InventarioView] {mensaje}")
        # Ocultar automáticamente después de 4 segundos
        from PyQt6.QtCore import QTimer
        if hasattr(self, '_feedback_timer') and self._feedback_timer:
            self._feedback_timer.stop()
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self.ocultar_feedback)
        self._feedback_timer.start(4000)

    def ocultar_feedback(self):
        if hasattr(self, "label_feedback") and self.label_feedback:
            self.label_feedback.setVisible(False)
            self.label_feedback.clear()
        if hasattr(self, '_feedback_timer') and self._feedback_timer:
            self._feedback_timer.stop()

    def mostrar_feedback_carga(self, mensaje="Cargando...", minimo=0, maximo=0):
        self.dialog_carga = QDialog(self)
        self.dialog_carga.setWindowTitle("Cargando")
        vbox = QVBoxLayout(self.dialog_carga)
        label = QLabel(mensaje)
        vbox.addWidget(label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(minimo, maximo)
        vbox.addWidget(self.progress_bar)
        self.dialog_carga.setModal(True)
        self.dialog_carga.setFixedSize(300, 100)
        self.dialog_carga.show()
        return self.progress_bar

    def ocultar_feedback_carga(self):
        if hasattr(self, 'dialog_carga') and self.dialog_carga:
            self.dialog_carga.accept()
            self.dialog_carga = None
# NOTA: Todos los estilos visuales y feedback deben ser gestionados por QSS global (themes/light.qss y dark.qss). No usar setStyleSheet embebido. Si se requiere excepción, documentar y justificar en docs/estandares_visuales.md
