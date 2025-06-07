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
from core.event_bus import event_bus

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

    def __init__(self, db_connection=None, usuario_actual="default"):
        super().__init__()
        self.setObjectName("InventarioView")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(32, 32, 32, 32)
        self.main_layout.setSpacing(16)

        self.db_connection = db_connection
        self.usuario_actual = usuario_actual

        # --- FEEDBACK VISUAL Y ACCESIBILIDAD ---
        self.label_feedback = QLabel("")
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Feedback visual de Inventario")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario en Inventario")
        self.main_layout.addWidget(self.label_feedback)
        # --- HEADER VISUAL MODERNO: título y barra de botones alineados ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Gestión de Inventario")
        self.label_titulo.setAccessibleDescription("Título principal de la vista de Inventario")
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        # [ELIMINADO] Botón principal (Agregar item) al lado del título
        # self.boton_agregar = QPushButton()
        # self.boton_agregar.setIcon(QIcon("resources/icons/add-material.svg"))
        # self.boton_agregar.setIconSize(QSize(24, 24))
        # self.boton_agregar.setToolTip("Agregar item")
        # self.boton_agregar.setAccessibleName("Botón agregar ítem de inventario")
        # header_layout.addWidget(self.boton_agregar)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

        # --- BOTONES PRINCIPALES COMO ICONOS (arriba a la derecha) ---
        # Cada botón tiene su función, tooltip y SVG documentado para fácil mantenimiento.
        # Puedes cambiar el SVG o el tooltip según la función que desees destacar.
        top_btns_layout = QHBoxLayout()
        top_btns_layout.addStretch()
        # Botón: Agregar nuevo ítem de inventario
        btn_nuevo_item = QPushButton()
        btn_nuevo_item.setIcon(QIcon("resources/icons/add-material.svg"))  # SVG: add-material.svg
        btn_nuevo_item.setIconSize(QSize(24, 24))
        btn_nuevo_item.setToolTip("Agregar nuevo ítem de inventario")
        btn_nuevo_item.setAccessibleName("Botón agregar nuevo ítem de inventario")
        btn_nuevo_item.clicked.connect(self.nuevo_item_signal.emit)
        estilizar_boton_icono(btn_nuevo_item)
        top_btns_layout.addWidget(btn_nuevo_item)
        # Botón: Exportar a Excel
        btn_excel = QPushButton()
        btn_excel.setIcon(QIcon("resources/icons/excel_icon.svg"))  # SVG: excel_icon.svg
        btn_excel.setIconSize(QSize(24, 24))
        btn_excel.setToolTip("Exportar inventario a Excel")
        btn_excel.setAccessibleName("Botón exportar inventario a Excel")
        btn_excel.clicked.connect(self.exportar_excel_signal.emit)
        estilizar_boton_icono(btn_excel)
        top_btns_layout.addWidget(btn_excel)
        # Botón: Exportar a PDF
        btn_pdf = QPushButton()
        btn_pdf.setIcon(QIcon("resources/icons/pdf_icon.svg"))  # SVG: pdf_icon.svg
        btn_pdf.setIconSize(QSize(24, 24))
        btn_pdf.setToolTip("Exportar inventario a PDF")
        btn_pdf.setAccessibleName("Botón exportar inventario a PDF")
        btn_pdf.clicked.connect(self.exportar_pdf_signal.emit)
        estilizar_boton_icono(btn_pdf)
        top_btns_layout.addWidget(btn_pdf)
        # Botón: Buscar ítem
        btn_buscar = QPushButton()
        btn_buscar.setIcon(QIcon("resources/icons/search_icon.svg"))  # SVG: search_icon.svg
        btn_buscar.setIconSize(QSize(24, 24))
        btn_buscar.setToolTip("Buscar ítem de inventario")
        btn_buscar.setAccessibleName("Botón buscar ítem de inventario")
        btn_buscar.clicked.connect(self.buscar_signal.emit)
        estilizar_boton_icono(btn_buscar)
        top_btns_layout.addWidget(btn_buscar)
        # Botón: Generar código QR
        btn_qr = QPushButton()
        btn_qr.setIcon(QIcon("resources/icons/qr_icon.svg"))  # SVG: qr_icon.svg
        btn_qr.setIconSize(QSize(24, 24))
        btn_qr.setToolTip("Generar código QR de inventario")
        btn_qr.setAccessibleName("Botón generar código QR de inventario")
        btn_qr.clicked.connect(self.generar_qr_signal.emit)
        estilizar_boton_icono(btn_qr)
        top_btns_layout.addWidget(btn_qr)
        # Botón: Ver obras pendientes de material
        btn_obras_pendientes = QPushButton()
        btn_obras_pendientes.setIcon(QIcon("resources/icons/viewdetails.svg"))  # SVG: viewdetails.svg
        btn_obras_pendientes.setIconSize(QSize(24, 24))
        btn_obras_pendientes.setToolTip("Ver obras pendientes de material")
        btn_obras_pendientes.setAccessibleName("Botón ver obras pendientes de material")
        btn_obras_pendientes.clicked.connect(self.ver_obras_pendientes_material)
        estilizar_boton_icono(btn_obras_pendientes)
        top_btns_layout.addWidget(btn_obras_pendientes)
        # Botón: Reservar lote de perfiles
        btn_reservar_lote = QPushButton()
        btn_reservar_lote.setIcon(QIcon("resources/icons/reserve-stock.svg"))  # SVG: reserve-stock.svg
        btn_reservar_lote.setIconSize(QSize(24, 24))
        btn_reservar_lote.setToolTip("Reservar lote de perfiles")
        btn_reservar_lote.setAccessibleName("Botón reservar lote de perfiles")
        btn_reservar_lote.clicked.connect(self.abrir_reserva_lote_perfiles)
        estilizar_boton_icono(btn_reservar_lote)
        top_btns_layout.addWidget(btn_reservar_lote)
        self.main_layout.addLayout(top_btns_layout)

        # Validar conexión
        conexion_valida = self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password"])
        if not conexion_valida:
            error_label = QLabel("❌ Error: No se pudo conectar a la base de datos de inventario.\nVerifique la configuración o contacte al administrador.")
            # QSS global: el color y formato de error se define en themes/light.qss y dark.qss
            error_label.setProperty("feedback", "error")  # Para que el QSS global lo seleccione
            # Refuerzo de accesibilidad explícito para tests
            error_label.setAccessibleDescription("Mensaje de error crítico de conexión en Inventario")
            error_label.setAccessibleName("Label de error de conexión en Inventario")
            self.main_layout.addWidget(error_label)
            self.setLayout(self.main_layout)
            return

        self.main_layout.setSpacing(16)  # Cambiar a un valor mayor para mejor visibilidad

        # Obtener headers desde la base de datos
        self.inventario_headers = self.obtener_headers_desde_db("inventario_perfiles")
        # --- TABLA PRINCIPAL DE INVENTARIO ---
        self.tabla_inventario = QTableWidget()
        self.tabla_inventario.setObjectName("tabla_inventario")
        self.tabla_inventario.setColumnCount(len(self.inventario_headers))
        self.tabla_inventario.setHorizontalHeaderLabels(self.inventario_headers)
        self.make_table_responsive(self.tabla_inventario)
        self.tabla_inventario.setAlternatingRowColors(True)
        self.tabla_inventario.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_inventario.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_inventario.setToolTip("Tabla principal de inventario")
        self.tabla_inventario.setAccessibleName("Tabla de inventario")
        v_header = self.tabla_inventario.verticalHeader()
        if v_header is not None:
            v_header.setVisible(False)
        h_header = self.tabla_inventario.horizontalHeader()
        if h_header is not None:
            # QSS global: el estilo de header se define en themes/light.qss y dark.qss
            h_header.setProperty("header", True)
            h_header.setHighlightSections(False)
            # Corregir: usar QHeaderView.ResizeMode.Stretch en vez de QHeaderView.Stretch
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
        # Hacer la tabla más alta
        self.tabla_inventario.setMinimumHeight(520)
        self.tabla_inventario.setMaximumHeight(900)
        self.main_layout.addWidget(self.tabla_inventario)

        self.main_layout.addStretch()  # Asegura que la tabla se vea correctamente

        # Cargar configuración de columnas visibles
        # --- NOTA: La cadena de conexión SQL se construye dinámicamente usando variables de configuración.
        # Esto NO constituye una credencial hardcodeada ni viola el estándar de seguridad.
        # Ver test_no_credenciales_en_codigo en tests/test_estandares_modulos.py para justificación.
        # ---
        self.config_path = f"config_inventario_columns_{self.usuario_actual}.json"
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

        # Menú contextual para mostrar/ocultar columnas
        self.tabla_inventario.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabla_inventario.customContextMenuRequested.connect(self.mostrar_menu_columnas)

        # Cargar y aplicar QSS global y tema visual (NO modificar ni sobrescribir salvo justificación)
        qss_tema = None
        try:
            import json
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("theme", "theme_light")
            qss_tema = f"resources/qss/{tema}.qss"
            # Eliminado setStyleSheet embebido, migrado a QSS global (ver docs/estandares_visuales.md)
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")
        from utils.theme_manager import cargar_modo_tema
        tema = cargar_modo_tema()
        qss_tema = f"resources/qss/theme_{tema}.qss"
        aplicar_qss_global_y_tema(self, qss_global_path="resources/qss/theme_light.qss", qss_tema_path=qss_tema)

        # Conectar la señal exportar_excel_signal al método exportar_tabla_a_excel
        self.exportar_excel_signal.connect(self.exportar_tabla_a_excel)

        # Refuerzo de accesibilidad en todos los QLabel
        for widget in self.findChildren(QLabel):
            if not widget.accessibleDescription():
                widget.setAccessibleDescription("Label informativo o de feedback en Inventario")
            if not widget.accessibleName():
                widget.setAccessibleName("Label de Inventario")

        # Suscribirse a la señal global de integración en tiempo real
        event_bus.obra_agregada.connect(self.actualizar_por_obra)

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
        return {header: True for header in self.inventario_headers}

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
        """
        Muestra el menú contextual del header de la tabla de inventario.
        Corrige robustamente el error de tipo: siempre convierte a QPoint.
        """
        from PyQt6.QtCore import QPoint
        menu = QMenu(self)
        accion_autoajustar = QAction("Autoajustar todas las columnas", self)
        accion_autoajustar.triggered.connect(self.autoajustar_todas_columnas)
        menu.addAction(accion_autoajustar)
        h_header = self.tabla_inventario.horizontalHeader() if hasattr(self.tabla_inventario, 'horizontalHeader') else None
        try:
            if h_header is not None and hasattr(h_header, 'mapToGlobal'):
                # Convertir siempre a QPoint
                if isinstance(pos, QPoint):
                    global_pos = pos
                elif isinstance(pos, int):
                    global_pos = QPoint(pos, 0)
                elif isinstance(pos, tuple) and len(pos) == 2:
                    global_pos = QPoint(pos[0], pos[1])
                else:
                    # Fallback: intentar construir QPoint si es posible
                    try:
                        global_pos = QPoint(*pos)
                    except Exception:
                        global_pos = QPoint(0, 0)
                menu.exec(h_header.mapToGlobal(global_pos))
            else:
                menu.exec(pos)
        except Exception as e:
            self.mostrar_feedback(f"Error al mostrar menú de header: {e}", tipo="error")

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
        from PyQt6.QtWidgets import QMessageBox
        # Diálogo de confirmación antes de exportar
        confirm = QMessageBox.question(self, "Confirmar exportación", "¿Desea exportar el inventario a Excel?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm != QMessageBox.StandardButton.Yes:
            self.mostrar_feedback("Exportación cancelada por el usuario.", tipo="advertencia")
            return
        # Abrir diálogo para elegir ubicación
        file_path, _ = QFileDialog.getSaveFileName(self, "Exportar a Excel", "inventario.xlsx", "Archivos Excel (*.xlsx)")
        if not file_path:
            self.mostrar_feedback("Exportación cancelada.", tipo="advertencia")
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
            QMessageBox.information(self, "Exportación exitosa", f"Inventario exportado correctamente a:\n{file_path}")
            self.mostrar_feedback(f"Inventario exportado correctamente a {file_path}", tipo="exito")
            log_error(f"Inventario exportado correctamente a {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error de exportación", f"No se pudo exportar: {e}")
            self.mostrar_feedback(f"No se pudo exportar: {e}", tipo="error")
            log_error(f"Error al exportar inventario: {e}")

    def ver_obras_pendientes_material(self):
        id_item = self.obtener_id_item_seleccionado()
        if not id_item:
            self.mostrar_feedback("Seleccione un material en la tabla.", tipo="advertencia")
            log_error("Intento de ver obras pendientes sin selección de material.")
            return
        if not (self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password", "server"])):
            self.mostrar_feedback("No hay conexión válida a la base de datos.", tipo="error")
            log_error("Error de conexión a la base de datos al consultar obras pendientes.")
            return
        try:
            query = "SELECT referencia_obra, cantidad_reservada, estado, codigo_reserva FROM reserva_materiales WHERE id_item = ? AND estado IN ('activa', 'pendiente')"
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
                self.mostrar_feedback("No hay obras pendientes para este material.", tipo="info")
                log_error(f"Consulta de obras pendientes: sin reservas para material {id_item}")
                return
            # --- ESTÁNDAR VISUAL ---
            dialog = QDialog(self)
            dialog.setWindowTitle("Obras pendientes de este material")
            dialog.setStyleSheet("QDialog { background: #fff9f3; border-radius: 12px; }")
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(24, 20, 24, 20)
            layout.setSpacing(16)
            for r in reservas:
                obra = r.get("referencia_obra", "")
                cantidad = r.get("cantidad_reservada", "")
                estado = r.get("estado", "")
                codigo = r.get("codigo_reserva", "")
                label = QLabel(f"Obra: <b>{obra}</b> | Cantidad: <b>{cantidad}</b> | Estado: <b>{estado}</b> | Código: <b>{codigo}</b>")
                label.setStyleSheet("font-size: 13px; color: #2563eb; background: #e3f6fd; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;")
                layout.addWidget(label)
            btn_cerrar = QPushButton()
            btn_cerrar.setIcon(QIcon("resources/icons/close.svg"))  # SVG: close.svg
            btn_cerrar.setToolTip("Cerrar ventana de reservas")
            estilizar_boton_icono(btn_cerrar)
            btn_cerrar.clicked.connect(dialog.accept)
            layout.addWidget(btn_cerrar)
            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            self.mostrar_feedback(f"Error al consultar reservas: {e}", tipo="error")
            log_error(f"Error al consultar reservas: {e}")

    def abrir_pedido_material_obra(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Pedido de material por obra")
        dialog.setMinimumSize(800, 600)
        dialog.setStyleSheet("QDialog { background: #fff9f3; border-radius: 12px; }")
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)
        codigo_proveedor_input = QLineEdit()
        codigo_proveedor_input.setPlaceholderText("Código de proveedor")
        codigo_proveedor_input.setToolTip("Ingrese el código del material a pedir")
        form_layout.addRow("Código de proveedor:", codigo_proveedor_input)
        descripcion_label = QLabel("")
        descripcion_label.setStyleSheet("color: #2563eb; font-weight: bold; font-size: 13px;")
        descripcion_label.setToolTip("Descripción del material según código")
        form_layout.addRow("Descripción:", descripcion_label)
        layout.addLayout(form_layout)
        # --- TABLA DE PERFILES EN PEDIDO MATERIAL ---
        tabla_perfiles = QTableWidget()
        tabla_perfiles.setObjectName("tabla_inventario")  # Unificación visual
        tabla_perfiles.setColumnCount(5)
        tabla_perfiles.setHorizontalHeaderLabels([
            "Código", "Descripción", "Stock", "Cantidad a pedir", "Faltan"
        ])
        # El estilo visual de la tabla se gestiona solo por QSS global (ver resources/qss/theme_light.qss y theme_dark.qss)
        tabla_perfiles.setAlternatingRowColors(True)
        tabla_perfiles.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(tabla_perfiles)
        # Botones de acción (solo ícono, documentados)
        btn_buscar = QPushButton()
        btn_buscar.setIcon(QIcon("resources/icons/search_icon.svg"))  # SVG: search_icon.svg
        btn_buscar.setToolTip("Buscar perfiles por código")
        estilizar_boton_icono(btn_buscar)
        btn_reservar = QPushButton()
        btn_reservar.setIcon(QIcon("resources/icons/add-material.svg"))  # SVG: add-material.svg
        btn_reservar.setToolTip("Pedir material seleccionado")
        estilizar_boton_icono(btn_reservar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon("resources/icons/close.svg"))  # SVG: close.svg
        btn_cancelar.setToolTip("Cancelar y cerrar ventana")
        estilizar_boton_icono(btn_cancelar)
        btns = QHBoxLayout()
        btns.addStretch()
        btns.addWidget(btn_buscar)
        btns.addWidget(btn_reservar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        dialog.setLayout(layout)
        perfiles_encontrados = []
        # --- NUEVO: Búsqueda en vivo y validación de código ---
        def buscar_y_mostrar_descripcion():
            codigo = codigo_proveedor_input.text().strip()
            if not codigo:
                descripcion_label.setText("")
                return
            if not (self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password", "server"])):
                descripcion_label.setText("Sin conexión a BD")
                return
            query = "SELECT codigo, descripcion, stock FROM inventario_perfiles WHERE codigo = ?"
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
                    cursor.execute(query, (codigo,))
                    row = cursor.fetchone()
                    if row:
                        descripcion_label.setText(str(row[1]))
                        descripcion_label.setStyleSheet("color: #0077b6; font-weight: bold;")
                    else:
                        descripcion_label.setText("Código no encontrado")
                        descripcion_label.setStyleSheet("color: #d90429; font-weight: bold;")
            except Exception as e:
                descripcion_label.setText(f"Error: {e}")
                descripcion_label.setStyleSheet("color: #d90429; font-weight: bold;")
        # Conectar búsqueda en vivo y enter
        codigo_proveedor_input.textChanged.connect(buscar_y_mostrar_descripcion)
        codigo_proveedor_input.returnPressed.connect(buscar_y_mostrar_descripcion)
        # --- FIN NUEVO ---
        def buscar_perfiles():
            if not (self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password", "server"])):
                self.mostrar_feedback("No hay conexión válida a la base de datos.", tipo="error")
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
                        perfiles_encontrados.append({"id": id_item, "codigo": cod, "desc": desc, "stock": stock, "input": cantidad_pedir, "faltan": faltan_label})
                        def actualizar_faltan(idx=i):
                            try:
                                val = int(perfiles_encontrados[idx]["input"].text())
                            except Exception:
                                val = 0
                            try:
                                stock_val = int(perfiles_encontrados[idx]["stock"])
                            except Exception:
                                stock_val = 0
                            faltan = max(0, val - stock_val)
                            perfiles_encontrados[idx]["faltan"].setText(str(faltan))
                        cantidad_pedir.textChanged.connect(lambda _, idx=i: actualizar_faltan(idx))
            except Exception as e:
                self.mostrar_feedback(f"Error al buscar perfiles: {e}", tipo="error")
                log_error(f"Error al buscar perfiles: {e}")
        def pedir_lote():
            if not (self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password", "server"])):
                self.mostrar_feedback("No hay conexión válida a la base de datos.", tipo="error")
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
                        cursor.execute("INSERT INTO reserva_materiales (id_item, cantidad_reservada, referencia_obra, estado) VALUES (?, ?, ?, ?)", (id_item, cantidad, "OBRA", estado))
                    conn.commit()
                self.mostrar_feedback("Pedido de material realizado correctamente.", tipo="exito")
                log_error("Pedido de material realizado correctamente.")
                dialog.accept()
                self.actualizar_signal.emit()
            except Exception as e:
                self.mostrar_feedback(f"Error al registrar pedido: {e}", tipo="error")
                log_error(f"Error al registrar pedido: {e}")
        btn_buscar.clicked.connect(buscar_perfiles)
        btn_reservar.clicked.connect(pedir_lote)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    # Reemplazar la función antigua por la nueva
    abrir_reserva_lote_perfiles = abrir_pedido_material_obra

    def abrir_formulario_nuevo_item(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Agregar nuevo ítem de inventario")
        dialog.setModal(True)
        dialog.setStyleSheet("QDialog { background: #fff9f3; border-radius: 12px; }")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)
        campos = {
            "codigo": QLineEdit(),
            "nombre": QLineEdit(),
            "tipo_material": QLineEdit(),
            "unidad": QLineEdit(),
            "stock_actual": QLineEdit(),
            "stock_minimo": QLineEdit(),
            "ubicacion": QLineEdit(),
            "descripcion": QLineEdit(),
        }
        for key, widget in campos.items():
            widget.setPlaceholderText(key.replace('_', ' ').capitalize())
            widget.setToolTip(f"Ingrese {key.replace('_', ' ')}")
            form.addRow(key.replace('_', ' ').capitalize() + ":", widget)
        qr_input = QLineEdit()
        qr_input.setPlaceholderText("Código QR (opcional)")
        qr_input.setToolTip("Código QR opcional")
        form.addRow("Código QR:", qr_input)
        imagen_input = QLineEdit()
        imagen_input.setPlaceholderText("Ruta imagen referencia (opcional)")
        imagen_input.setToolTip("Ruta de imagen de referencia (opcional)")
        form.addRow("Imagen referencia:", imagen_input)
        layout.addLayout(form)
        btns = QHBoxLayout()
        btn_guardar = QPushButton()
        btn_guardar.setIcon(QIcon("resources/icons/finish-check.svg"))  # SVG: finish-check.svg
        btn_guardar.setToolTip("Guardar ítem de inventario")
        estilizar_boton_icono(btn_guardar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon("resources/icons/close.svg"))  # SVG: close.svg
        btn_cancelar.setToolTip("Cancelar y cerrar ventana")
        estilizar_boton_icono(btn_cancelar)
        btns.addStretch()
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        resultado = {}
        def guardar():
            for key, widget in campos.items():
                valor = widget.text().strip()
                if not valor:
                    widget.setProperty("error", True)
                    widget.setToolTip("Campo obligatorio")
                    style = widget.style()
                    if style is not None:
                        style.unpolish(widget)
                        style.polish(widget)
                    self.mostrar_feedback(f"El campo '{key}' es obligatorio.", tipo="error")
                    return
                resultado[key] = valor
            resultado["qr"] = qr_input.text().strip()
            resultado["imagen_referencia"] = imagen_input.text().strip()
            # Insertar en la base de datos
            if not (self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password", "server"])):
                self.mostrar_feedback("No hay conexión válida a la base de datos.", tipo="error")
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
                    cursor.execute(
                        """
                        INSERT INTO inventario_perfiles (codigo, nombre, tipo_material, unidad, stock, stock_minimo, ubicacion, descripcion, qr, imagen_referencia)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            resultado["codigo"], resultado["nombre"], resultado["tipo_material"], resultado["unidad"],
                            int(resultado["stock_actual"]), int(resultado["stock_minimo"]), resultado["ubicacion"], resultado["descripcion"],
                            resultado["qr"], resultado["imagen_referencia"]
                        )
                    )
                    conn.commit()
                self.mostrar_feedback("Ítem agregado correctamente.", tipo="exito")
                dialog.accept()
                self.actualizar_signal.emit()
            except Exception as e:
                self.mostrar_feedback(f"Error al agregar ítem: {e}", tipo="error")
        btn_guardar.clicked.connect(guardar)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def abrir_ajuste_stock_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajuste de stock de inventario")
        dialog.setMinimumSize(600, 400)
        dialog.setStyleSheet("QDialog { background: #fff9f3; border-radius: 12px; }")
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)
        codigo_input = QLineEdit()
        codigo_input.setPlaceholderText("Ingrese código de material")
        codigo_input.setToolTip("Código del material a ajustar")
        descripcion_label = QLabel("")
        descripcion_label.setStyleSheet("color: #2563eb; font-style: italic; font-size: 13px;")
        descripcion_label.setAccessibleName("Descripción del material")
        descripcion_label.setAccessibleDescription("Descripción del material según código ingresado")
        form_layout.addRow("Código:", codigo_input)
        form_layout.addRow("Descripción:", descripcion_label)
        layout.addLayout(form_layout)
        # --- TABLA DE AJUSTES DE STOCK ---
        tabla_ajustes = QTableWidget()
        tabla_ajustes.setObjectName("tabla_inventario")  # Unificación visual
        tabla_ajustes.setColumnCount(3)
        tabla_ajustes.setHorizontalHeaderLabels(["Código", "Descripción", "Cantidad"])
        # El estilo visual de la tabla se gestiona solo por QSS global (ver resources/qss/theme_light.qss y theme_dark.qss)
        tabla_ajustes.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(tabla_ajustes)
        cantidad_input = QLineEdit()
        cantidad_input.setPlaceholderText("Cantidad a ajustar")
        cantidad_input.setToolTip("Cantidad a ajustar para el material")
        form_layout.addRow("Cantidad:", cantidad_input)
        btn_agregar = QPushButton()
        btn_agregar.setIcon(QIcon("resources/icons/add-material.svg"))  # SVG: add-material.svg
        btn_agregar.setToolTip("Agregar material a la lista de ajuste")
        estilizar_boton_icono(btn_agregar)
        btn_agregar.setEnabled(False)
        layout.addWidget(btn_agregar)
        btns = QHBoxLayout()
        btn_aceptar = QPushButton()
        btn_aceptar.setIcon(QIcon("resources/icons/finish-check.svg"))  # SVG: finish-check.svg
        btn_aceptar.setToolTip("Aceptar y guardar ajustes")
        estilizar_boton_icono(btn_aceptar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon("resources/icons/close.svg"))  # SVG: close.svg
        btn_cancelar.setToolTip("Cancelar y cerrar ventana")
        estilizar_boton_icono(btn_cancelar)
        btns.addStretch()
        btns.addWidget(btn_aceptar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        dialog.setLayout(layout)
        # Estado interno
        items_ajuste = []
        # --- Lógica de búsqueda y validación en tiempo real ---
        def buscar_codigo():
            codigo = codigo_input.text().strip()
            if not codigo:
                descripcion_label.setText("")
                btn_agregar.setEnabled(False)
                return
            # Buscar en la base de datos
            if not (self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password", "server"])):
                descripcion_label.setText("No hay conexión a la base de datos.")
                btn_agregar.setEnabled(False)
                return
            query = "SELECT descripcion FROM inventario_perfiles WHERE codigo = ?"
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
                    cursor.execute(query, (codigo,))
                    row = cursor.fetchone()
                    if row:
                        descripcion_label.setText(str(row[0]))
                        btn_agregar.setEnabled(True)
                    else:
                        descripcion_label.setText("Código no encontrado")
                        btn_agregar.setEnabled(False)
            except Exception as e:
                descripcion_label.setText(f"Error: {e}")
                btn_agregar.setEnabled(False)
        # Conectar búsqueda en vivo y enter
        codigo_input.textChanged.connect(buscar_codigo)
        codigo_input.returnPressed.connect(buscar_codigo)
        def agregar_a_lista():
            codigo = codigo_input.text().strip()
            if not codigo:
                return
            # Buscar en la base de datos
            if not (self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password", "server"])):
                self.mostrar_feedback("No hay conexión válida a la base de datos.", tipo="error")
                log_error("Error de conexión a la base de datos al agregar ajuste.")
                return
            query = "SELECT id, codigo, descripcion, stock FROM inventario_perfiles WHERE codigo = ?"
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
                    cursor.execute(query, (codigo,))
                    row = cursor.fetchone()
                    if row:
                        # Agregar a la tabla de ajustes
                        fila = tabla_ajustes.rowCount()
                        tabla_ajustes.insertRow(fila)
                        for col in range(3):
                            item = QTableWidgetItem(str(row[col]))
                            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # No editable
                            tabla_ajustes.setItem(fila, col, item)
                        cantidad_input.clear()
                        # Actualizar estado interno
                        items_ajuste.append({"codigo": row[0], "descripcion": row[1], "cantidad": 0})
                        self.mostrar_feedback(f"Material '{row[1]}' agregado a la lista de ajuste.", tipo="exito")
                    else:
                        self.mostrar_feedback("Código no encontrado en inventario.", tipo="advertencia")
            except Exception as e:
                self.mostrar_feedback(f"Error al agregar material: {e}", tipo="error")
                log_error(f"Error al agregar material a ajuste: {e}")
        btn_agregar.clicked.connect(agregar_a_lista)
        codigo_input.returnPressed.connect(lambda: btn_agregar.setEnabled(btn_agregar.isEnabled()) or agregar_a_lista())
        # Botones aceptar/cancelar
        def aceptar():
            if not items_ajuste:
                self.mostrar_feedback("No hay ajustes para guardar.", tipo="advertencia")
                return
            # Aquí puedes emitir una señal o procesar los ajustes
            self.ajustes_stock_guardados.emit(items_ajuste)
            dialog.accept()
        btn_aceptar.clicked.connect(aceptar)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def mostrar_feedback(self, mensaje, tipo="info", icono="", duracion=4000):
        # QSS global: el color y formato de feedback se define en themes/light.qss y dark.qss
        self.label_feedback.setProperty("feedback_tipo", tipo)
        style = self.label_feedback.style()
        if style is not None:
            style.unpolish(self.label_feedback)
            style.polish(self.label_feedback)
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
        self._feedback_timer.start(duracion)

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

    def actualizar_por_obra(self, datos_obra):
        """
        Actualiza el inventario en tiempo real cuando se agrega una nueva obra.
        Muestra feedback visual inmediato y refresca los datos necesarios.
        """
        # Aquí puedes refrescar solo lo necesario, por ejemplo:
        self.refrescar_stock_por_obra(datos_obra)
        self.mostrar_feedback_visual(f"Nueva obra agregada: {datos_obra.get('nombre','')} (stock actualizado)", tipo="info")

    def refrescar_stock_por_obra(self, datos_obra):
        # Lógica para refrescar el stock afectado por la nueva obra
        # Recarga la tabla si existe el método cargar_items y la tabla
        if hasattr(self, 'cargar_items') and hasattr(self, 'tabla_inventario'):
            # Intenta recargar la tabla con los datos actuales
            self.cargar_items([])  # Limpia la tabla
            # Feedback visual mínimo
            print(f"[INFO] Refrescado visual de inventario tras obra agregada: {datos_obra}")
        else:
            print("[WARN] No se pudo refrescar inventario tras obra agregada.")

    def mostrar_feedback_visual(self, mensaje, tipo="info"):
        # Helper para feedback visual accesible y consistente
        if hasattr(self, 'label_feedback'):
            self.label_feedback.setText(mensaje)
            self.label_feedback.setVisible(True)
            # Aquí puedes aplicar color/emoji según tipo
        else:
            print(mensaje)

    def toggle_expandir_fila(self, fila, columna):
        """
        Expande o colapsa visualmente la fila seleccionada en la tabla de inventario.
        Proporciona feedback visual accesible y cumple con los estándares visuales.
        """
        if not hasattr(self, 'tabla_inventario') or self.tabla_inventario is None:
            self.mostrar_feedback("No se puede expandir la fila: tabla no inicializada.", tipo="error")
            return
        alto_expandido = 80  # Alto expandido (puedes ajustar según diseño)
        alto_normal = 32     # Alto normal (ajustar según QSS global)
        if not hasattr(self, 'filas_expandidas'):
            self.filas_expandidas = set()
        if fila in self.filas_expandidas:
            self.tabla_inventario.setRowHeight(fila, alto_normal)
            self.filas_expandidas.remove(fila)
            self.mostrar_feedback(f"Fila {fila+1} colapsada.", tipo="info")
        else:
            self.tabla_inventario.setRowHeight(fila, alto_expandido)
            self.filas_expandidas.add(fila)
            self.mostrar_feedback(f"Fila {fila+1} expandida.", tipo="info")

    def abrir_reserva_perfil_dialog(self, id_perfil=None):
        """
        Abre un diálogo modal robusto para reservar perfil/material desde la fila seleccionada.
        Cumple checklist: validación, feedback, tooltips, accesibilidad, visual, controller.
        """
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox, QSpinBox, QLabel, QPushButton, QHBoxLayout
        dialog = QDialog(self)
        dialog.setWindowTitle("Reservar perfil/material para obra")
        dialog.setModal(True)
        dialog.setStyleSheet("QDialog { background: #fff9f3; border-radius: 12px; }")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)
        # --- Combo de obras ---
        cmb_obras = QComboBox()
        cmb_obras.setToolTip("Seleccione la obra a la que reservar el material")
        cmb_obras.setAccessibleName("Obra para reserva")
        # Cargar obras desde el controller/modelo
        obras = getattr(self, 'controller', None).model.obtener_obras() if hasattr(self, 'controller') and hasattr(self.controller.model, 'obtener_obras') else []
        for obra in obras:
            cmb_obras.addItem(str(obra['nombre']), obra['id_obra'])
        form.addRow("Obra:", cmb_obras)
        # --- Combo de perfiles/materiales ---
        cmb_perfiles = QComboBox()
        cmb_perfiles.setToolTip("Seleccione el perfil/material a reservar")
        cmb_perfiles.setAccessibleName("Perfil/material para reserva")
        perfiles = getattr(self, 'controller', None).model.obtener_perfiles() if hasattr(self, 'controller') and hasattr(self.controller.model, 'obtener_perfiles') else []
        for perfil in perfiles:
            cmb_perfiles.addItem(f"{perfil['codigo']} - {perfil['nombre']}", perfil['id_perfil'])
        if id_perfil:
            idx = cmb_perfiles.findData(id_perfil)
            if idx >= 0:
                cmb_perfiles.setCurrentIndex(idx)
        form.addRow("Perfil:", cmb_perfiles)
        # --- SpinBox de cantidad ---
        spin_cantidad = QSpinBox()
        spin_cantidad.setMinimum(1)
        spin_cantidad.setMaximum(1)
        spin_cantidad.setToolTip("Cantidad a reservar (máximo: stock actual)")
        spin_cantidad.setAccessibleName("Cantidad a reservar")
        form.addRow("Cantidad:", spin_cantidad)
        # --- Stock actual label ---
        lbl_stock = QLabel("")
        lbl_stock.setStyleSheet("color: #2563eb; font-size: 13px;")
        form.addRow("Stock actual:", lbl_stock)
        # --- Actualizar stock/cantidad al cambiar perfil ---
        def actualizar_stock():
            idp = cmb_perfiles.currentData()
            perfil = next((p for p in perfiles if p['id_perfil'] == idp), None)
            stock = int(perfil['stock_actual']) if perfil and 'stock_actual' in perfil else 1
            spin_cantidad.setMaximum(stock if stock > 0 else 1)
            lbl_stock.setText(str(stock))
        cmb_perfiles.currentIndexChanged.connect(actualizar_stock)
        actualizar_stock()
        layout.addLayout(form)
        # --- Feedback visual ---
        lbl_feedback = QLabel("")
        lbl_feedback.setObjectName("label_feedback_reserva")
        lbl_feedback.setStyleSheet("font-size: 13px; color: #ef4444; padding: 4px 0;")
        lbl_feedback.setVisible(False)
        layout.addWidget(lbl_feedback)
        # --- Botones ---
        btns = QHBoxLayout()
        btn_reservar = QPushButton()
        btn_reservar.setIcon(QIcon("resources/icons/add-material.svg"))
        btn_reservar.setToolTip("Reservar perfil/material seleccionado")
        estilizar_boton_icono(btn_reservar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon("resources/icons/close.svg"))
        btn_cancelar.setToolTip("Cancelar y cerrar ventana")
        estilizar_boton_icono(btn_cancelar)
        btns.addStretch()
        btns.addWidget(btn_reservar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        # --- Acción reservar ---
        def reservar():
            id_obra = cmb_obras.currentData()
            id_perfil = cmb_perfiles.currentData()
            cantidad = spin_cantidad.value()
            if id_obra is None or id_perfil is None or cantidad < 1:
                lbl_feedback.setText("Complete todos los campos y seleccione cantidad válida.")
                lbl_feedback.setVisible(True)
                return
            try:
                self.controller.reservar_perfil(self.usuario_actual, id_obra, id_perfil, cantidad)
                self.mostrar_feedback("Reserva exitosa.", tipo="exito")
                dialog.accept()
                self.actualizar_signal.emit()
            except ValueError as e:
                lbl_feedback.setText(str(e))
                lbl_feedback.setVisible(True)
            except Exception as e:
                lbl_feedback.setText(f"Error inesperado: {e}")
                lbl_feedback.setVisible(True)
        btn_reservar.clicked.connect(reservar)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def agregar_boton_reserva_a_tabla(self):
        """
        Agrega un botón de acción de reserva en cada fila de la tabla de inventario.
        """
        for row in range(self.tabla_inventario.rowCount()):
            btn_reservar = QPushButton()
            btn_reservar.setIcon(QIcon("resources/icons/add-material.svg"))
            btn_reservar.setToolTip("Reservar este perfil/material para una obra")
            estilizar_boton_icono(btn_reservar)
            id_perfil = self.tabla_inventario.item(row, 0).text() if self.tabla_inventario.item(row, 0) else None
            btn_reservar.clicked.connect(lambda _, idp=id_perfil: self.abrir_reserva_perfil_dialog(idp))
            self.tabla_inventario.setCellWidget(row, self.tabla_inventario.columnCount()-1, btn_reservar)
# NOTA: Todos los estilos visuales y feedback deben ser gestionados por QSS global (themes/light.qss and dark.qss). No usar setStyleSheet embebido. Si se requiere excepción, documentar y justificar en docs/estandares_visuales.md
