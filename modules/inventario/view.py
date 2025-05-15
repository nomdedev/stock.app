from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QTabWidget, QDialog, QMessageBox, QInputDialog, QCheckBox, QScrollArea, QHeaderView, QMenu, QSizePolicy, QGraphicsDropShadowEffect, QFileDialog
from PyQt6.QtGui import QColor, QAction, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint
import json
import os
import pyodbc
import pandas as pd
from functools import partial
from modules.vidrios.view import VidriosView
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono

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

    def __init__(self, db_connection=None, usuario_actual="default"):
        super().__init__()
        self.setObjectName("InventarioView")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.layout.setSpacing(16)  # Cambiar a un valor mayor para mejor visibilidad

        self.db_connection = db_connection
        self.usuario_actual = usuario_actual

        # Título
        self.label_titulo = QLabel("INVENTORY")
        self.layout.addWidget(self.label_titulo)

        # Botones principales como iconos (arriba a la derecha)
        top_btns_layout = QHBoxLayout()
        top_btns_layout.addStretch()
        iconos = [
            ("add-material.svg", "Agregar nuevo ítem", self.nuevo_item_signal),
            ("excel_icon.svg", "Exportar a Excel", self.exportar_excel_signal),
            ("pdf_icon.svg", "Exportar a PDF", self.exportar_pdf_signal),
            ("search_icon.svg", "Buscar ítem", self.buscar_signal),
            ("qr_icon.svg", "Generar código QR", self.generar_qr_signal),
        ]
        for icono, tooltip, signal in iconos:
            btn = QPushButton()
            btn.setIcon(QIcon(f"img/{icono}"))
            btn.setIconSize(QSize(24, 24))
            btn.setToolTip(tooltip)
            btn.setText("")
            btn.clicked.connect(signal.emit)
            estilizar_boton_icono(btn)
            top_btns_layout.addWidget(btn)
        self.layout.addLayout(top_btns_layout)  # Cambiar insertLayout por addLayout para asegurar el orden

        # Botón para ver obras pendientes de este material
        self.btn_ver_obras_pendientes = QPushButton("Ver obras pendientes de este material")
        self.btn_ver_obras_pendientes.setIcon(QIcon("img/viewdetails.svg"))
        self.btn_ver_obras_pendientes.setIconSize(QSize(20, 20))
        self.btn_ver_obras_pendientes.setToolTip("Mostrar obras a las que les falta este material")
        self.btn_ver_obras_pendientes.clicked.connect(self.ver_obras_pendientes_material)
        self.layout.addWidget(self.btn_ver_obras_pendientes)

        # Botón para abrir reserva avanzada por lote
        self.btn_reserva_lote = QPushButton("Reserva avanzada por lote")
        self.btn_reserva_lote.setIcon(QIcon("img/batchreserve.svg"))
        self.btn_reserva_lote.setIconSize(QSize(20, 20))
        self.btn_reserva_lote.setToolTip("Abrir ventana de reserva avanzada por lote")
        self.btn_reserva_lote.clicked.connect(self.abrir_reserva_lote_perfiles)
        self.layout.addWidget(self.btn_reserva_lote)

        # Obtener headers desde la base de datos
        self.inventario_headers = self.obtener_headers_desde_db("inventario_perfiles")
        self.tabla_inventario = QTableWidget()
        self.tabla_inventario.setColumnCount(len(self.inventario_headers))
        self.tabla_inventario.setHorizontalHeaderLabels(self.inventario_headers)
        self.make_table_responsive(self.tabla_inventario)
        self.tabla_inventario.setAlternatingRowColors(True)
        self.tabla_inventario.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_inventario.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_inventario.verticalHeader().setVisible(False)
        self.tabla_inventario.horizontalHeader().setHighlightSections(False)
        self.tabla_inventario.setShowGrid(False)
        self.tabla_inventario.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabla_inventario.setMinimumHeight(500)  # <-- Aumenta la altura mínima de la tabla
        self.tabla_inventario.setMinimumWidth(1200)  # <-- Aumenta el ancho mínimo de la tabla
        self.tabla_inventario.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tabla_inventario.horizontalHeader().sectionDoubleClicked.connect(self.autoajustar_columna)
        self.tabla_inventario.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabla_inventario.horizontalHeader().customContextMenuRequested.connect(self.mostrar_menu_header)
        self.tabla_inventario.horizontalHeader().sectionClicked.connect(self.mostrar_menu_columnas_header)
        self.tabla_inventario.cellClicked.connect(self.toggle_expandir_fila)
        self.filas_expandidas = set()
        self.layout.addWidget(self.tabla_inventario)

        self.layout.addStretch()  # Asegura que la tabla se vea correctamente

        # Cargar configuración de columnas visibles
        self.config_path = f"config_inventario_columns_{self.usuario_actual}.json"
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

        # Menú contextual para mostrar/ocultar columnas
        self.tabla_inventario.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabla_inventario.customContextMenuRequested.connect(self.mostrar_menu_columnas)

        # Cargar el stylesheet visual moderno para Inventario según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        # Conectar la señal exportar_excel_signal al método exportar_tabla_a_excel
        self.exportar_excel_signal.connect(self.exportar_tabla_a_excel)

    def obtener_headers_desde_db(self, tabla):
        if self.db_connection:
            query = f"SELECT TOP 0 * FROM {tabla}"
            connection_string = (
                f"DRIVER={{{self.db_connection.driver}}};"
                f"SERVER=localhost\\SQLEXPRESS;"
                f"DATABASE={self.db_connection.database};"
                f"UID={self.db_connection.username};"
                f"PWD={self.db_connection.password};"
                f"TrustServerCertificate=yes;"
            )
            with pyodbc.connect(connection_string, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                return [column[0] for column in cursor.description]
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
        menu.exec(self.tabla_inventario.viewport().mapToGlobal(pos))

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_inventario.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()

    def mostrar_menu_header(self, pos):
        menu = QMenu(self)
        accion_autoajustar = QAction("Autoajustar todas las columnas", self)
        accion_autoajustar.triggered.connect(self.autoajustar_todas_columnas)
        menu.addAction(accion_autoajustar)
        menu.exec(self.tabla_inventario.horizontalHeader().mapToGlobal(pos))

    def autoajustar_columna(self, idx):
        self.tabla_inventario.resizeColumnToContents(idx)

    def autoajustar_todas_columnas(self):
        for idx in range(self.tabla_inventario.columnCount()):
            self.tabla_inventario.resizeColumnToContents(idx)

    def obtener_id_item_seleccionado(self):
        # Devuelve el ID del ítem seleccionado en la tabla (stub para pruebas)
        fila = self.tabla_inventario.currentRow()
        if fila != -1:
            return self.tabla_inventario.item(fila, 0).text()
        return None

    def cargar_items(self, items):
        # items debe ser una lista de diccionarios con claves iguales a los headers
        self.tabla_inventario.setRowCount(len(items))
        for fila, item in enumerate(items):
            for columna, header in enumerate(self.inventario_headers):
                valor = item.get(header, "")
                self.tabla_inventario.setItem(fila, columna, QTableWidgetItem(str(valor)))

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
            QMessageBox.information(self, "Éxito", f"Inventario exportado correctamente a {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar: {e}")

    def mostrar_menu_columnas_header(self, idx):
        header = self.tabla_inventario.horizontalHeader()
        pos = header.sectionPosition(idx)
        global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
        self.mostrar_menu_columnas(global_pos)

    def ver_obras_pendientes_material(self):
        id_item = self.obtener_id_item_seleccionado()
        if not id_item:
            QMessageBox.warning(self, "Sin selección", "Seleccione un material en la tabla.")
            return
        # Buscar reservas activas o pendientes para este material
        try:
            # Conexión directa a la base (usa el mismo método que cargar_headers)
            query = "SELECT referencia_obra, cantidad_reservada, estado, codigo_reserva FROM reservas_materiales WHERE id_item = ? AND estado IN ('activa', 'pendiente')"
            connection_string = (
                f"DRIVER={{{self.db_connection.driver}}};"
                f"SERVER=localhost\\SQLEXPRESS;"
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
                QMessageBox.information(self, "Sin reservas", "No hay obras pendientes para este material.")
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
            btn_cerrar = QPushButton("Cerrar")
            btn_cerrar.clicked.connect(dialog.accept)
            layout.addWidget(btn_cerrar)
            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al consultar reservas: {e}")

    def toggle_expandir_fila(self, row, col):
        id_item = self.tabla_inventario.item(row, 0).text()
        if (row, id_item) in self.filas_expandidas:
            self.colapsar_fila(row)
            self.filas_expandidas.remove((row, id_item))
        else:
            self.expandir_fila(row, id_item)
            self.filas_expandidas.add((row, id_item))

    def expandir_fila(self, row, id_item):
        # Consultar reservas activas/pendientes para este material
        try:
            query = "SELECT referencia_obra, cantidad_reservada, estado, codigo_reserva FROM reservas_materiales WHERE id_item = ? AND estado IN ('activa', 'pendiente')"
            connection_string = (
                f"DRIVER={{{self.db_connection.driver}}};"
                f"SERVER=localhost\\SQLEXPRESS;"
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
                self.tabla_inventario.insertRow(insert_at)
                self.tabla_inventario.setSpan(insert_at, 0, 1, self.tabla_inventario.columnCount())
                obra = r.get("referencia_obra", "")
                cantidad = r.get("cantidad_reservada", "")
                estado = r.get("estado", "")
                codigo = r.get("codigo_reserva", "")
                label = QLabel(f"<b>Obra:</b> {obra} | <b>Cantidad:</b> {cantidad} | <b>Estado:</b> {estado} | <b>Código:</b> {codigo}")
                label.setStyleSheet("background:#f1f5f9; color:#222; padding:6px; border-radius:8px; font-size:13px;")
                self.tabla_inventario.setCellWidget(insert_at, 0, label)
                insert_at += 1
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al consultar reservas: {e}")

    def colapsar_fila(self, row):
        # Elimina todas las filas expandidas debajo de la fila seleccionada
        while self.tabla_inventario.rowCount() > row + 1:
            widget = self.tabla_inventario.cellWidget(row + 1, 0)
            if widget:
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
        tabla_perfiles.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
        def buscar_perfiles():
            codigo = codigo_proveedor_input.text().strip()
            if not codigo:
                QMessageBox.warning(dialog, "Falta código", "Ingrese un código de proveedor.")
                return
            query = "SELECT id, codigo, descripcion, stock_actual FROM inventario_perfiles WHERE codigo LIKE ?"
            connection_string = (
                f"DRIVER={{{self.db_connection.driver}}};"
                f"SERVER=localhost\\SQLEXPRESS;"
                f"DATABASE={self.db_connection.database};"
                f"UID={self.db_connection.username};"
                f"PWD={self.db_connection.password};"
                f"TrustServerCertificate=yes;"
            )
            import pyodbc
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
                        faltan = max(0, val - int(perfiles_encontrados[idx]["stock"]))
                        perfiles_encontrados[idx]["faltan"].setText(str(faltan))
                    cantidad_pedir.textChanged.connect(actualizar_faltan)
        def pedir_lote():
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
                QMessageBox.warning(dialog, "Nada para pedir", "No hay cantidades válidas para pedir.")
                return
            connection_string = (
                f"DRIVER={{{self.db_connection.driver}}};"
                f"SERVER=localhost\\SQLEXPRESS;"
                f"DATABASE={self.db_connection.database};"
                f"UID={self.db_connection.username};"
                f"PWD={self.db_connection.password};"
                f"TrustServerCertificate=yes;"
            )
            import pyodbc
            with pyodbc.connect(connection_string, timeout=10) as conn:
                cursor = conn.cursor()
                for id_item, cantidad, estado in pedidos:
                    cursor.execute("INSERT INTO reservas_materiales (id_item, cantidad_reservada, referencia_obra, estado) VALUES (?, ?, ?, ?)", (id_item, cantidad, "OBRA", estado))
                conn.commit()
            QMessageBox.information(dialog, "Pedido registrado", "Pedido de material realizado correctamente.")
            dialog.accept()
            self.actualizar_signal.emit()
        btn_buscar.clicked.connect(buscar_perfiles)
        btn_reservar.clicked.connect(pedir_lote)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    # Reemplazar la función antigua por la nueva
    abrir_reserva_lote_perfiles = abrir_pedido_material_obra
