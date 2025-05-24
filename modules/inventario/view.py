from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QTabWidget, QDialog, QMessageBox, QMenu, QHeaderView, QGraphicsDropShadowEffect, QFileDialog
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
from core.logger import Logger, log_error
from core.database import get_connection_string

# --- GUÍA PARA FORMULARIOS Y DIÁLOGOS SECUNDARIOS (accesibilidad y visuales) ---
# Si se agregan QDialog o formularios secundarios en este módulo:
# - Usar padding mínimo de 20px vertical y 24px horizontal (ver main.py y docs/estandares_visuales.md)
# - Bordes redondeados (8-12px), fuente sans-serif, tooltips descriptivos en todos los campos y botones.
# - Botones principales con icono y feedback visual (hover, disabled, etc.) usando 'estilizar_boton_icono'.
# - Feedback inmediato con QLabel y colores estándar (verde, rojo, naranja, azul pastel) y emojis (✅❌⚠️ℹ️).
# - Si el proceso es largo, usar QProgressDialog o spinner.
# - Documentar cualquier excepción visual o lógica en el código y en docs/estandares_visuales.md.
#
# Ejemplo de feedback visual en formularios:
# label_feedback = QLabel()
# label_feedback.setStyleSheet("font-size: 13px; padding: 8px 0;")
# label_feedback.setText("<span style='color:#22c55e;'>✅ Acción realizada con éxito</span>")
#
# Ver ejemplos en modules/obras/controller.py y modules/contabilidad/view.py

# --- VALIDACIÓN DE TESTS AUTOMÁTICOS Y EXCEPCIONES VISUALES ---
# Recomendación: Validar cobertura de tests automáticos para flujos críticos (carga, exportación, feedback de error).
# Si se detecta una excepción visual nueva, documentarla en el código y en docs/estandares_visuales.md.
#
# Ejemplo de excepción documentada:
# # EXCEPCIÓN: El feedback visual de progreso puede ser breve si la tabla es pequeña. Documentado en docs/estandares_feedback.md.

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
    ajustes_stock_guardados = pyqtSignal(list)  # Señal para emitir los ajustes de stock guardados

    def _conexion_valida(self):
        return self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password"])

    def _feedback_error(self, mensaje, log_msg=None):
        if log_msg:
            self.logger.log_error_popup(log_msg)
            log_error(log_msg)
        QMessageBox.critical(self, "Error", mensaje)

    def ver_obras_pendientes_material(self):
        # Implementación de ver_obras_pendientes_material
        pass

    def toggle_expandir_fila(self, row, col):
        # Implementación de toggle_expandir_fila
        pass

    def __init__(self, db_connection=None, usuario_actual="default"):
        super().__init__()
        self.logger = Logger()
        self.setObjectName("InventarioView")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 20, 24, 20)  # Padding global reforzado
        self.main_layout.setSpacing(20)  # Espaciado vertical estándar

        self.db_connection = db_connection
        self.usuario_actual = usuario_actual

        # Título
        self.label_titulo = QLabel("INVENTORY")
        self.main_layout.addWidget(self.label_titulo)

        # Validar conexión
        if not self._conexion_valida():
            error_label = QLabel("❌ Error: No se pudo conectar a la base de datos de inventario.\nVerifique la configuración o contacte al administrador.")
            error_label.setStyleSheet("color: #ef4444; font-size: 13px; font-weight: bold; padding: 16px;")
            error_label.setToolTip("Error de conexión a la base de datos. Consulte al administrador.")
            self.main_layout.addWidget(error_label)
            self._feedback_error(
                "No se pudo conectar a la base de datos de inventario.",
                f"InventarioView: No se pudo conectar a la base de datos de inventario para usuario {self.usuario_actual}"
            )
            self.setLayout(self.main_layout)
            return

        # --- Barra de botones principal (arriba a la derecha, unificada y estilizada) ---
        top_btns_layout = QHBoxLayout()
        top_btns_layout.setSpacing(16)  # Espaciado estándar entre botones
        top_btns_layout.setContentsMargins(0, 0, 0, 0)
        top_btns_layout.addStretch()
        # Definir botones principales (todos con el mismo estilo y tamaño)
        iconos = [
            ("add-material.svg", "Agregar nuevo ítem", self.nuevo_item_signal),
            ("excel_icon.svg", "Exportar a Excel", self.exportar_excel_signal),
            ("pdf_icon.svg", "Exportar a PDF", self.exportar_pdf_signal),
            ("search_icon.svg", "Buscar ítem", self.buscar_signal),
            ("qr_icon.svg", "Generar código QR", self.generar_qr_signal),
            ("ajustar-stock.svg", "Ajustar stock de perfiles", None),  # Botón de ajuste de stock
            ("obras-pendientes.svg", "Mostrar obras a las que les falta este material", None),
            ("lote.svg", "Abrir ventana de reserva avanzada por lote", None),
        ]
        self.barra_botones = []
        for icono, tooltip, signal in iconos:
            btn = QPushButton()
            btn.setIcon(QIcon(f"img/{icono}"))
            btn.setIconSize(QSize(24, 24))
            # Refuerzo: tooltip descriptivo y accesible
            btn.setToolTip(tooltip)
            btn.setText("")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(38, 38)
            estilizar_boton_icono(btn)
            if signal is not None:
                btn.clicked.connect(signal.emit)
            elif icono == "ajustar-stock.svg":
                btn.clicked.connect(self._stub_ajuste_stock)
            elif icono == "obras-pendientes.svg":
                btn.clicked.connect(self.ver_obras_pendientes_material)
            elif icono == "lote.svg":
                btn.clicked.connect(self._stub_reserva_lote_perfiles)
            self.barra_botones.append(btn)
            top_btns_layout.addWidget(btn)
        self.main_layout.addLayout(top_btns_layout)

        # --- Tabla de inventario (mejorada visualmente) ---
        self.inventario_headers = self.obtener_headers_desde_db("inventario_perfiles")
        if not self.inventario_headers:
            # Fallback a headers estándar si la consulta falla o la tabla está vacía
            self.inventario_headers = [
                "id_item", "descripcion", "tipo", "linea", "color_acabado", "color_real", "longitud", "stock", "pedidos"
            ]
        self.tabla_inventario = QTableWidget()
        self.tabla_inventario.setColumnCount(len(self.inventario_headers))
        self.tabla_inventario.setHorizontalHeaderLabels(self.inventario_headers)
        self.make_table_responsive(self.tabla_inventario)
        self.tabla_inventario.setAlternatingRowColors(True)
        self.tabla_inventario.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_inventario.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_inventario.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                alternate-background-color: #f8fafc;
                background: #fff;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
                padding: 12px;
            }
            QTableWidget::item {
                padding: 8px 12px;
            }
            QTableWidget::item:selected {
                background: #dbeafe;
                color: #1e293b;
            }
            QHeaderView::section {
                background-color: #e3f6fd;
                color: #2563eb;
                font-weight: bold;
                border-radius: 8px;
                font-size: 13px;
                padding: 8px 12px;
                border: 1px solid #e3e3e3;
            }
        """)
        # Refuerzo: asegurar headers visuales estándar aunque el QSS global cambie
        h_header = self.tabla_inventario.horizontalHeader()
        if h_header is not None:
            h_header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; font-weight: bold; border-radius: 8px; font-size: 13px; padding: 8px 12px; border: 1px solid #e3e3e3;")
            h_header.setHighlightSections(False)
            h_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            h_header.sectionDoubleClicked.connect(self.autoajustar_columna)
            h_header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            h_header.customContextMenuRequested.connect(self.mostrar_menu_header)
            h_header.sectionClicked.connect(self.mostrar_menu_columnas_header)
        self.tabla_inventario.cellClicked.connect(self.toggle_expandir_fila)
        self.filas_expandidas = set()
        self.main_layout.addWidget(self.tabla_inventario)

        self.main_layout.addStretch()

        # Cargar configuración de columnas visibles
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
            tema = config.get("tema", "claro")
            qss_tema = f"themes/{tema}.qss"
        except Exception as e:
            self.logger.warning(f"No se pudo cargar el tema visual: {e}")
        aplicar_qss_global_y_tema(self, qss_global_path="style_moderno.qss", qss_tema_path=qss_tema)

        # Conectar la señal exportar_excel_signal al método exportar_tabla_a_excel
        self.exportar_excel_signal.connect(self.exportar_tabla_a_excel)

        # NOTA: Mantener la práctica de tooltips claros en todo botón/campo nuevo para accesibilidad y usabilidad.

        # Refuerzo de accesibilidad en todos los botones principales
        for btn in self.barra_botones:
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setStyleSheet(btn.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
            font = btn.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            btn.setFont(font)
            # Tooltip ya presente, pero reforzamos claridad
            if not btn.toolTip():
                btn.setToolTip("Botón de acción")
        # Refuerzo de accesibilidad en la tabla principal
        self.tabla_inventario.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.tabla_inventario.setStyleSheet(self.tabla_inventario.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")
        # Refuerzo de accesibilidad en todos los QLineEdit de la vista principal
        for widget in self.findChildren(QLineEdit):
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            widget.setStyleSheet(widget.styleSheet() + "\nQLineEdit:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQLineEdit { font-size: 12px; }")
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
            if not widget.toolTip():
                widget.setToolTip("Campo de texto")
            if not widget.accessibleName():
                widget.setAccessibleName("Campo de texto de inventario")
        # Documentar excepción visual si algún widget no cumple estándar
        # EXCEPCIÓN: Si algún botón requiere texto visible por UX, debe estar documentado aquí y en docs/estandares_visuales.md

    def _stub_ajuste_stock(self):
        # Stub temporal para botón de ajuste de stock
        # EXCEPCIÓN: Este botón existe por requerimiento de UX, pero la funcionalidad aún no está implementada.
        # Documentado aquí y en docs/estandares_visuales.md
        self.logger.warning("Funcionalidad de ajuste de stock no implementada.")
        QMessageBox.information(self, "No implementado", "La funcionalidad de ajuste de stock aún no está disponible.")

    def _stub_reserva_lote_perfiles(self):
        # Stub temporal para botón de reserva avanzada por lote
        # EXCEPCIÓN: Este botón existe por requerimiento de UX, pero la funcionalidad aún no está implementada.
        # Documentado aquí y en docs/estandares_visuales.md
        self.logger.warning("Funcionalidad de reserva avanzada por lote no implementada.")
        QMessageBox.information(self, "No implementado", "La funcionalidad de reserva avanzada por lote aún no está disponible.")

    def _get_db_attr(self, attr, default=None):
        # Helper robusto para obtener atributos de la conexión
        if self.db_connection and hasattr(self.db_connection, attr):
            return getattr(self.db_connection, attr)
        return default

    def obtener_headers_desde_db(self, tabla):
        try:
            if self._conexion_valida():
                driver = self._get_db_attr("driver", "")
                database = self._get_db_attr("database", "")
                query = f"SELECT TOP 0 * FROM {tabla}"
                connection_string = get_connection_string(driver, database)
                with pyodbc.connect(connection_string, timeout=10) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    return [column[0] for column in cursor.description]
        except Exception as e:
            # EXCEPCIÓN: Si la consulta de headers falla, se usa fallback visual estándar.
            # Documentado aquí y en docs/estandares_visuales.md
            self._feedback_error(
                f"Error al obtener headers de la tabla {tabla}: {e}",
                f"Error al obtener headers de la tabla {tabla}: {e}"
            )
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
        header = self.tabla_inventario.horizontalHeader()
        if header is not None:
            menu.exec(header.mapToGlobal(pos))
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
        h_header = self.tabla_inventario.horizontalHeader()
        if h_header is not None:
            menu.exec(h_header.mapToGlobal(pos))
        else:
            menu.exec(pos)

    def autoajustar_columna(self, idx):
        self.tabla_inventario.resizeColumnToContents(idx)

    def autoajustar_todas_columnas(self):
        for idx in range(self.tabla_inventario.columnCount()):
            self.tabla_inventario.resizeColumnToContents(idx)

    def mostrar_menu_columnas_header(self, idx):
        header = self.tabla_inventario.horizontalHeader()
        if header is not None:
            pos = header.sectionPosition(idx)
            global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
            self.mostrar_menu_columnas(global_pos)

    def obtener_id_item_seleccionado(self):
        # Devuelve el ID del ítem seleccionado en la tabla (robustecida)
        fila = self.tabla_inventario.currentRow()
        if fila != -1:
            item = self.tabla_inventario.item(fila, 0)
            if item is not None and hasattr(item, 'text'):
                return item.text()
        return None

    def cargar_items(self, items):
        from PyQt6.QtWidgets import QProgressDialog
        progress = QProgressDialog("Cargando inventario...", None, 0, len(items), self)
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setMinimumDuration(300)
        progress.setValue(0)
        self.tabla_inventario.setRowCount(len(items))
        for fila, item in enumerate(items):
            for columna, header in enumerate(self.inventario_headers):
                valor = item.get(header, "")
                qitem = QTableWidgetItem(str(valor))
                # Mejora: agregar tooltip descriptivo a cada celda
                qitem.setToolTip(f"{header}: {valor}")
                self.tabla_inventario.setItem(fila, columna, qitem)
            progress.setValue(fila + 1)
        progress.close()
        # EXCEPCIÓN: Si hay muchos ítems, el feedback visual puede ser breve. Documentado aquí y en docs/estandares_feedback.md

    def exportar_tabla_a_excel(self):
        from PyQt6.QtWidgets import QProgressDialog
        # Abrir diálogo para elegir ubicación
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar inventario a Excel",
            "inventario.xlsx",
            "Archivos de Excel (*.xlsx);;Todos los archivos (*)"
        )
        if not file_path:
            return  # El usuario canceló
        try:
            row_count = self.tabla_inventario.rowCount()
            progress = QProgressDialog("Exportando a Excel...", None, 0, row_count, self)
            progress.setWindowModality(Qt.WindowModality.ApplicationModal)
            progress.setMinimumDuration(300)
            progress.setValue(0)
            # Recolectar datos de la tabla
            data = []
            for row in range(row_count):
                fila = []
                for col in range(self.tabla_inventario.columnCount()):
                    item = self.tabla_inventario.item(row, col)
                    fila.append(item.text() if item else "")
                data.append(fila)
                if row % 10 == 0 or row == row_count - 1:
                    progress.setValue(row + 1)
            progress.setValue(row_count)
            df = pd.DataFrame(data, columns=self.inventario_headers)
            df.to_excel(file_path, index=False)
            progress.close()
            QMessageBox.information(self, "Exportación exitosa", f"Inventario exportado correctamente a:\n{file_path}")
        except Exception as e:
            progress.close()
            self._feedback_error(
                f"Error al exportar a Excel: {e}",
                f"InventarioView.exportar_tabla_a_excel: {e}"
            )
        # EXCEPCIÓN: Si la tabla está vacía o hay error de escritura, se muestra feedback visual y se documenta en logs.
        # EXCEPCIÓN: El feedback visual de progreso puede ser breve si la tabla es pequeña. Documentado en docs/estandares_feedback.md.

        header = self.tabla_inventario.horizontalHeader() if hasattr(self.tabla_inventario, 'horizontalHeader') else None
        if header is not None:
            if hasattr(header, 'setContextMenuPolicy'):
                header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            if hasattr(header, 'customContextMenuRequested'):
                header.customContextMenuRequested.connect(self.mostrar_menu_columnas)
            if hasattr(header, 'setSectionsMovable'):
                header.setSectionsMovable(True)
            if hasattr(header, 'setSectionsClickable'):
                header.setSectionsClickable(True)
            if hasattr(header, 'sectionClicked'):
                header.sectionClicked.connect(self.mostrar_menu_columnas_header)
        else:
            # EXCEPCIÓN VISUAL: Si el header es None, no se puede aplicar menú contextual ni acciones de header.
            # Documentar en docs/estandares_visuales.md si ocurre en producción.
            pass