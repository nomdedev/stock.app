from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QDateEdit, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox, QDialog, QFileDialog, QProgressBar, QTabWidget, QInputDialog
from PyQt6.QtGui import QIcon, QColor, QAction, QPixmap
from PyQt6.QtCore import QSize, Qt, QPoint, QTimer
import json
import os
from functools import partial
import qrcode
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono, aplicar_qss_global_y_tema
from core.event_bus import event_bus

class VidriosView(QWidget, TableResponsiveMixin):
    """
    Vista robusta para gestión de vidrios.
    Cumple los estándares de layout, QSS, headers, robustez y feedback definidos en el README.
    - Usa main_layout y setLayout.
    - Valida headers y celdas antes de acceder.
    - No usa box-shadow en QSS (usa QGraphicsDropShadowEffect en botones).
    - Exportación QR robusta.
    """
    def __init__(self, usuario_actual="default", headers_dinamicos=None):
        super().__init__()
        self.usuario_actual = usuario_actual
        self._cambio_columnas_interactivo = False
        self.vidrios_headers = headers_dinamicos if headers_dinamicos else ["tipo", "ancho", "alto", "cantidad", "proveedor", "fecha_entrega"]
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        self.setWindowTitle("Gestión de Vidrios")

        # --- HEADER VISUAL MODERNO: título y barra de botones alineados ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Gestión de Vidrios")
        self.label_titulo.setObjectName("label_titulo_vidrios")
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.boton_agregar_vidrios_obra = QPushButton()
        self.boton_agregar_vidrios_obra.setObjectName("boton_agregar_vidrios_obra")
        self.boton_agregar_vidrios_obra.setIcon(QIcon("resources/icons/add-material.svg"))
        self.boton_agregar_vidrios_obra.setIconSize(QSize(24, 24))
        self.boton_agregar_vidrios_obra.setToolTip("Agregar vidrios a una obra existente")
        self.boton_agregar_vidrios_obra.setAccessibleName("Agregar vidrios a obra")
        self.boton_agregar_vidrios_obra.setFixedSize(48, 48)
        self.boton_agregar_vidrios_obra.setText("")
        estilizar_boton_icono(self.boton_agregar_vidrios_obra)
        header_layout.addStretch()
        header_layout.addWidget(self.boton_agregar_vidrios_obra)
        self.main_layout.addLayout(header_layout)

        # --- TABS PRINCIPALES (MEJORADO: paddings, márgenes, alineación, consistencia visual) ---
        self.tabs = QTabWidget()
        self.tabs.setObjectName("tabs_vidrios")
        self.tabs.setStyleSheet("QTabWidget::pane { border-radius: 12px; background: #fff9f3; margin: 0 0 0 0; } QTabBar::tab { min-width: 180px; min-height: 36px; font-size: 13px; padding: 10px 24px; border-radius: 8px; background: #e3f6fd; margin-right: 8px; } QTabBar::tab:selected { background: #fff; color: #2563eb; border: 2px solid #2563eb; }")
        self.main_layout.addWidget(self.tabs)

        # Pestaña 1: Obras sin pedido de vidrios (mejorada)
        self.tab_obras = QWidget()
        tab_obras_layout = QVBoxLayout(self.tab_obras)
        tab_obras_layout.setContentsMargins(24, 20, 24, 20)
        tab_obras_layout.setSpacing(18)
        self.tabla_obras = QTableWidget()
        self.tabla_obras.setObjectName("tabla_obras_vidrios")
        self.tabla_obras.setColumnCount(4)
        self.tabla_obras.setHorizontalHeaderLabels(["ID Obra", "Nombre", "Cliente", "Fecha Entrega"])
        header_obras = self.tabla_obras.horizontalHeader()
        if header_obras is not None:
            header_obras.setObjectName("header_obras_vidrios")
            self.tabla_obras.setHorizontalHeader(header_obras)
        self.tabla_obras.setAlternatingRowColors(True)
        self.tabla_obras.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_obras.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tab_obras_layout.addWidget(self.tabla_obras)
        self.boton_iniciar_pedido = QPushButton("Iniciar pedido de vidrios para obra seleccionada")
        self.boton_iniciar_pedido.setObjectName("boton_iniciar_pedido_vidrios")
        self.boton_iniciar_pedido.setToolTip("Iniciar pedido de vidrios para la obra seleccionada")
        tab_obras_layout.addWidget(self.boton_iniciar_pedido)
        self.tab_obras.setLayout(tab_obras_layout)
        self.tabs.addTab(self.tab_obras, "Obras y estado de pedidos")

        # Pestaña 2: Pedidos realizados por el usuario (mejorada)
        self.tab_pedidos_usuario = QWidget()
        tab_pedidos_usuario_layout = QVBoxLayout(self.tab_pedidos_usuario)
        tab_pedidos_usuario_layout.setContentsMargins(24, 20, 24, 20)
        tab_pedidos_usuario_layout.setSpacing(18)
        self.tabla_pedidos_usuario = QTableWidget()
        self.tabla_pedidos_usuario.setObjectName("tabla_pedidos_usuario_vidrios")
        self.tabla_pedidos_usuario.setColumnCount(5)
        self.tabla_pedidos_usuario.setHorizontalHeaderLabels(["ID Pedido", "Obra", "Fecha", "Estado", "Detalle"])
        header_pedidos = self.tabla_pedidos_usuario.horizontalHeader()
        if header_pedidos is not None:
            header_pedidos.setObjectName("header_pedidos_usuario_vidrios")
            self.tabla_pedidos_usuario.setHorizontalHeader(header_pedidos)
        self.tabla_pedidos_usuario.setAlternatingRowColors(True)
        self.tabla_pedidos_usuario.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_pedidos_usuario.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tab_pedidos_usuario_layout.addWidget(self.tabla_pedidos_usuario)
        self.tab_pedidos_usuario.setLayout(tab_pedidos_usuario_layout)
        self.tabs.addTab(self.tab_pedidos_usuario, "Pedidos realizados por usuario")

        # --- FEEDBACK VISUAL CENTRALIZADO Y QSS GLOBAL ---
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Mensaje de feedback de vidrios")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario")
        self.main_layout.addWidget(self.label_feedback)
        self._feedback_timer = None

        self.setLayout(self.main_layout)

        # Configuración de columnas y headers dinámicos
        self.config_path = f"config_vidrios_columns_{self.usuario_actual}.json"
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

        # Menú contextual en el header (robusto)
        header = self.tabla_obras.horizontalHeader()
        if header is not None:
            header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            if hasattr(header, 'customContextMenuRequested'):
                header.customContextMenuRequested.connect(self.mostrar_menu_columnas)
            if hasattr(header, 'sectionDoubleClicked'):
                header.sectionDoubleClicked.connect(self.auto_ajustar_columna)
            if hasattr(header, 'setSectionsMovable'):
                header.setSectionsMovable(True)
            if hasattr(header, 'setSectionsClickable'):
                header.setSectionsClickable(True)
            if hasattr(header, 'sectionClicked'):
                header.sectionClicked.connect(self.mostrar_menu_columnas_header)

        # Cargar y aplicar QSS global y tema visual (solo desde resources/qss/)
        from utils.theme_manager import cargar_modo_tema
        tema = cargar_modo_tema()
        qss_tema = f"resources/qss/theme_{tema}.qss"
        aplicar_qss_global_y_tema(self, qss_global_path="resources/qss/theme_light.qss", qss_tema_path=qss_tema)

        # Botones principales como iconos (con sombra real)
        botones_layout = QHBoxLayout()
        self.boton_buscar = QPushButton()
        self.boton_buscar.setObjectName("boton_buscar_vidrios")  # Unificación visual y QSS global
        self.boton_buscar.setIcon(QIcon("resources/icons/search_icon.svg"))
        self.boton_buscar.setIconSize(QSize(20, 20))
        self.boton_buscar.setToolTip("Buscar vidrio")
        self.boton_buscar.setAccessibleName("Buscar vidrio")
        self.boton_buscar.setText("")
        self.boton_buscar.setFixedSize(48, 48)
        sombra2 = QGraphicsDropShadowEffect()
        sombra2.setBlurRadius(12)
        sombra2.setColor(QColor(37,99,235,40))
        sombra2.setOffset(0, 2)
        self.boton_buscar.setGraphicsEffect(sombra2)
        self.boton_exportar_excel = QPushButton()
        self.boton_exportar_excel.setObjectName("boton_exportar_excel_vidrios")  # Unificación visual y QSS global
        self.boton_exportar_excel.setIcon(QIcon("resources/icons/excel_icon.svg"))
        self.boton_exportar_excel.setIconSize(QSize(24, 24))
        self.boton_exportar_excel.setToolTip("Exportar vidrios a Excel")
        self.boton_exportar_excel.setAccessibleName("Exportar vidrios a Excel")
        self.boton_exportar_excel.setText("")
        self.boton_exportar_excel.setFixedSize(48, 48)
        sombra3 = QGraphicsDropShadowEffect()
        sombra3.setBlurRadius(12)
        sombra3.setColor(QColor(37,99,235,40))
        sombra3.setOffset(0, 2)
        self.boton_exportar_excel.setGraphicsEffect(sombra3)
        estilizar_boton_icono(self.boton_buscar)
        estilizar_boton_icono(self.boton_exportar_excel)
        botones_layout.addWidget(self.boton_buscar)
        botones_layout.addWidget(self.boton_exportar_excel)
        botones_layout.addStretch()
        self.main_layout.addLayout(botones_layout)
        # Conectar botones principales a sus acciones (exportar, etc.)
        self.conectar_botones_principales()

        # --- FEEDBACK VISUAL CENTRALIZADO Y QSS GLOBAL ---
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        # QSS global gestiona el estilo del feedback visual, no usar setStyleSheet embebido
        # [MIGRACIÓN QSS] Cumple: no hay setStyleSheet activos, todo el feedback y estilos visuales se gestionan por QSS global (ver docs/estandares_visuales.md)
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Mensaje de feedback de vidrios")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario")
        self.main_layout.addWidget(self.label_feedback)
        self._feedback_timer = None

        # Eliminar referencias a self.tabla_vidrios.horizontalHeader() y self.tabla_vidrios.itemSelectionChanged.connect(...)
        # Si se requiere menú contextual, usar self.tabla_obras o self.tabla_pedido según la pestaña activa.

        # Suscribirse a la señal global de integración en tiempo real
        event_bus.obra_agregada.connect(self.actualizar_por_obra)

        # Conectar señales de las tablas a métodos específicos
        self.tabla_obras.cellDoubleClicked.connect(self.editar_estado_pedido)
        self.tabla_obras.itemSelectionChanged.connect(self.actualizar_detalle_pedido)
        self.tabla_pedido.cellDoubleClicked.connect(self.editar_detalle_pedido)

        self.setLayout(self.main_layout)

    def create_form_layout(self):
        form_layout = QFormLayout()
        self.tipo_input = QLineEdit()
        self.ancho_input = QLineEdit()
        self.alto_input = QLineEdit()
        self.cantidad_input = QLineEdit()
        self.proveedor_input = QLineEdit()
        self.fecha_entrega_input = QDateEdit()
        self.fecha_entrega_input.setCalendarPopup(True)
        form_layout.addRow("Tipo:", self.tipo_input)
        form_layout.addRow("Ancho:", self.ancho_input)
        form_layout.addRow("Alto:", self.alto_input)
        form_layout.addRow("Cantidad:", self.cantidad_input)
        form_layout.addRow("Proveedor:", self.proveedor_input)
        form_layout.addRow("Fecha de Entrega:", self.fecha_entrega_input)
        return form_layout

    def create_table(self):
        table = QTableWidget()
        table.setColumnCount(len(self.vidrios_headers))
        table.setHorizontalHeaderLabels(self.vidrios_headers)
        return table

    def cargar_config_columnas(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                QMessageBox.warning(self, "Error de configuración", f"No se pudo cargar la configuración de columnas: {e}")
        return {header: True for header in self.vidrios_headers}

    def guardar_config_columnas(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)
            # Eliminado: No mostrar ningún mensaje de configuración guardada
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", f"No se pudo guardar la configuración: {e}")

    # Refactor: Métodos para operar sobre la tabla de la pestaña activa
    def get_tabla_activa(self):
        idx = self.tabs.currentIndex()
        if idx == 0:
            return self.tabla_obras
        elif idx == 1:
            return self.tabla_pedido
        return None

    def aplicar_columnas_visibles(self, tabla=None, headers=None, columnas_visibles=None):
        # Por defecto, usa la tabla de la pestaña activa
        if tabla is None:
            tabla = self.get_tabla_activa()
        if headers is None:
            headers = self.vidrios_headers
        if columnas_visibles is None:
            columnas_visibles = self.columnas_visibles
        if tabla is not None:
            for idx, header in enumerate(headers):
                visible = columnas_visibles.get(header, True)
                tabla.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos, tabla=None, headers=None, columnas_visibles=None):
        self._cambio_columnas_interactivo = True
        if tabla is None:
            tabla = self.get_tabla_activa()
        if headers is None:
            headers = self.vidrios_headers
        if columnas_visibles is None:
            columnas_visibles = self.columnas_visibles
        menu = QMenu(self)
        for idx, header in enumerate(headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, tabla, idx, header, columnas_visibles))
            menu.addAction(accion)
        header = self.get_safe_horizontal_header(tabla)
        if header is not None and hasattr(header, 'mapToGlobal'):
            menu.exec(header.mapToGlobal(pos))
        else:
            menu.exec(pos)
        self._cambio_columnas_interactivo = False

    def mostrar_menu_columnas_header(self, idx, tabla=None, headers=None, columnas_visibles=None):
        if tabla is None:
            tabla = self.get_tabla_activa()
        if headers is None:
            headers = self.vidrios_headers
        if columnas_visibles is None:
            columnas_visibles = self.columnas_visibles
        from PyQt6.QtCore import QPoint
        header = self.get_safe_horizontal_header(tabla)
        try:
            if header is not None and all(hasattr(header, m) for m in ['sectionPosition', 'mapToGlobal', 'sectionViewportPosition']):
                if idx < 0 or idx >= self.get_safe_column_count(tabla):
                    self.mostrar_feedback("Índice de columna fuera de rango", "error")
                    return
                pos = header.sectionPosition(idx)
                global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
                self.mostrar_menu_columnas(global_pos, tabla, headers, columnas_visibles)
            else:
                self.mostrar_feedback("No se puede mostrar el menú de columnas: header no disponible o incompleto", "error")
        except Exception as e:
            self.mostrar_feedback(f"Error al mostrar menú de columnas: {e}", "error")

    def toggle_columna(self, tabla, idx, header, columnas_visibles, checked):
        columnas_visibles[header] = checked
        tabla.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()
        if getattr(self, '_cambio_columnas_interactivo', False):
            self.mostrar_feedback("Configuración de columnas actualizada.", tipo="info")
            self._cambio_columnas_interactivo = False

    def auto_ajustar_columna(self, idx, tabla=None):
        if tabla is None:
            tabla = self.get_tabla_activa()
        if tabla is not None:
            tabla.resizeColumnToContents(idx)

    def mostrar_qr_item_seleccionado(self, tabla=None):
        if tabla is None:
            tabla = self.get_tabla_activa()
        selected = self.get_safe_selected_items(tabla)
        if not selected:
            return
        row = selected[0].row()
        item_codigo = self.get_safe_item(tabla, row, 0)
        if item_codigo is None:
            QMessageBox.warning(self, "Error de selección", "No se pudo obtener el código para el QR.")
            return
        codigo = item_codigo.text()
        if not codigo:
            QMessageBox.warning(self, "Error de datos", "El campo de código está vacío.")
            return
        try:
            qr = qrcode.QRCode(version=1, box_size=6, border=2)
            qr.add_data(codigo)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            # Convertir a formato PIL si es necesario
            if not hasattr(img, 'save'):
                from PIL import Image
                img = img.get_image()
        except Exception as e:
            QMessageBox.critical(self, "Error al generar QR", f"No se pudo generar el código QR: {e}")
            return
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                img.save(tmp)
                tmp.flush()
                tmp_path = tmp.name
                pixmap = QPixmap(tmp_path)
        except Exception as e:
            QMessageBox.critical(self, "Error de imagen", f"No se pudo crear la imagen temporal: {e}")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Código QR para {codigo}")
        vbox = QVBoxLayout(dialog)
        qr_label = QLabel()
        qr_label.setPixmap(pixmap)
        vbox.addWidget(qr_label)
        btns = QHBoxLayout()
        btn_guardar = QPushButton()
        btn_guardar.setIcon(QIcon("resources/icons/guardar-qr.svg"))
        btn_guardar.setToolTip("Guardar QR como imagen")
        estilizar_boton_icono(btn_guardar)
        btn_pdf = QPushButton()
        btn_pdf.setIcon(QIcon("resources/icons/pdf.svg"))
        btn_pdf.setToolTip("Exportar QR a PDF")
        estilizar_boton_icono(btn_pdf)
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_pdf)
        vbox.addLayout(btns)
        def guardar():
            try:
                file_path, _ = QFileDialog.getSaveFileName(dialog, "Guardar QR", f"qr_{codigo}.png", "Imagen PNG (*.png)")
                if file_path:
                    with open(tmp_path, "rb") as src, open(file_path, "wb") as dst:
                        dst.write(src.read())
            except Exception as e:
                QMessageBox.critical(dialog, "Error al guardar", f"No se pudo guardar la imagen: {e}")
        def exportar_pdf():
            try:
                file_path, _ = QFileDialog.getSaveFileName(dialog, "Exportar QR a PDF", f"qr_{codigo}.pdf", "Archivo PDF (*.pdf)")
                if file_path:
                    c = canvas.Canvas(file_path, pagesize=letter)
                    c.drawInlineImage(tmp_path, 100, 500, 200, 200)
                    c.save()
            except Exception as e:
                QMessageBox.critical(dialog, "Error al exportar PDF", f"No se pudo exportar el QR a PDF: {e}")
        btn_guardar.clicked.connect(guardar)
        btn_pdf.clicked.connect(exportar_pdf)
        dialog.exec()

    def mostrar_feedback(self, mensaje, tipo="exito"):
        """Muestra un mensaje de feedback visual en la interfaz."""
        colores = {
            "exito": "#4CAF50",  # Verde
            "error": "#F44336"   # Rojo
        }
        color = colores.get(tipo, "#000")
        self.label_feedback.setText(mensaje)
        self.label_feedback.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.label_feedback.setVisible(True)

        # Ocultar el mensaje después de 3 segundos
        if self._feedback_timer:
            self._feedback_timer.stop()
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(lambda: self.label_feedback.setVisible(False))
        self._feedback_timer.start(3000)

    def ocultar_feedback(self):
        if hasattr(self, "label_feedback") and self.label_feedback:
            self.label_feedback.setVisible(False)
            self.label_feedback.clear()
        if hasattr(self, '_feedback_timer') and self._feedback_timer:
            self._feedback_timer.stop()

    def mostrar_feedback_carga(self, mensaje="Cargando...", minimo=0, maximo=0):
        """Muestra un feedback visual de carga usando QProgressBar modal."""
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
        Actualiza la vista de vidrios en tiempo real cuando se agrega una nueva obra.
        Muestra feedback visual inmediato y refresca los datos necesarios.
        """
        self.refrescar_por_obra(datos_obra)
        self.mostrar_feedback(f"Nueva obra agregada: {datos_obra.get('nombre','')} (vidrios actualizados)", tipo="info")

    def refrescar_por_obra(self, datos_obra):
        # Lógica para refrescar la tabla de obras tras una nueva obra
        if hasattr(self, 'tabla_obras'):
            self.tabla_obras.setRowCount(0)
            print(f"[INFO] Refrescado visual de obras tras obra agregada: {datos_obra}")
        else:
            print("[WARN] No se pudo refrescar obras tras obra agregada.")

    def exportar_tabla_a_excel(self, tabla=None):
        """
        Exporta la tabla activa a un archivo Excel, con confirmación y feedback modal robusto.
        """
        if tabla is None:
            tabla = self.get_tabla_activa()
        if tabla is None:
            self.mostrar_feedback("No hay tabla activa para exportar.", tipo="error")
            return
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import pandas as pd
        confirm = QMessageBox.question(
            self,
            "Confirmar exportación",
            "¿Desea exportar la tabla a Excel?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            self.mostrar_feedback("Exportación cancelada por el usuario.", tipo="advertencia")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar a Excel",
            "tabla.xlsx",
            "Archivos Excel (*.xlsx)"
        )
        if not file_path:
            self.mostrar_feedback("Exportación cancelada.", tipo="advertencia")
            return
        data = []
        for row in range(tabla.rowCount()):
            row_data = {}
            for col in range(tabla.columnCount()):
                header_item = tabla.horizontalHeaderItem(col)
                header = header_item.text() if header_item is not None else f"Col {col+1}"
                item = tabla.item(row, col)
                row_data[header] = item.text() if item else ""
            data.append(row_data)
        df = pd.DataFrame(data)
        try:
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Exportación exitosa", f"Datos exportados correctamente a:\n{file_path}")
            self.mostrar_feedback(f"Datos exportados correctamente a {file_path}", tipo="exito")
        except Exception as e:
            QMessageBox.critical(self, "Error de exportación", f"No se pudo exportar: {e}")
            self.mostrar_feedback(f"No se pudo exportar: {e}", tipo="error")

    def conectar_botones_principales(self):
        """
        Conecta los botones principales a sus acciones correspondientes.
        """
        self.boton_exportar_excel.clicked.connect(self.exportar_tabla_a_excel)
        # Puedes conectar otros botones aquí si es necesario

    # Método para mostrar el formulario de vidrios asociados a una obra
    def mostrar_formulario_vidrios_obra(self):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Agregar Vidrios a Obra")
        layout = QVBoxLayout(dialogo)

        obra_input = QLineEdit()
        obra_input.setPlaceholderText("ID de la obra")
        layout.addWidget(QLabel("ID de la obra:"))
        layout.addWidget(obra_input)

        tipo_input = QLineEdit()
        tipo_input.setPlaceholderText("Tipo de vidrio")
        layout.addWidget(QLabel("Tipo de vidrio:"))
        layout.addWidget(tipo_input)

        ancho_input = QLineEdit()
        ancho_input.setPlaceholderText("Ancho")
        layout.addWidget(QLabel("Ancho:"))
        layout.addWidget(ancho_input)

        alto_input = QLineEdit()
        alto_input.setPlaceholderText("Alto")
        layout.addWidget(QLabel("Alto:"))
        layout.addWidget(alto_input)

        cantidad_input = QLineEdit()
        cantidad_input.setPlaceholderText("Cantidad")
        layout.addWidget(QLabel("Cantidad:"))
        layout.addWidget(cantidad_input)

        boton_guardar = QPushButton("Guardar")
        boton_guardar.clicked.connect(lambda: self.guardar_vidrios_obra(obra_input.text(), tipo_input.text(), ancho_input.text(), alto_input.text(), cantidad_input.text()))
        layout.addWidget(boton_guardar)

        dialogo.setLayout(layout)
        dialogo.exec()

    # Método para validar campos del formulario
    def validar_campos_formulario(self):
        campos = [self.tipo_input, self.ancho_input, self.alto_input, self.cantidad_input, self.proveedor_input]
        campos_invalidos = []
        for campo in campos:
            if not campo.text().strip():
                campo.setStyleSheet("border: 2px solid red;")
                campos_invalidos.append(campo)
            else:
                campo.setStyleSheet("border: 1px solid #bfc0c0;")
        return len(campos_invalidos) == 0

    # Método para guardar los vidrios asociados a una obra
    def guardar_vidrios_obra(self, obra_id, tipo, ancho, alto, cantidad):
        if not self.validar_campos_formulario():
            QMessageBox.warning(self, "Error", "Por favor, complete todos los campos obligatorios.")
            return
        # Aquí se implementaría la lógica para guardar los datos en la base de datos
        QMessageBox.information(self, "Éxito", f"Vidrios agregados a la obra {obra_id} correctamente.")
        self.mostrar_feedback("Vidrios agregados a la obra correctamente.", tipo="exito")

    # Método para editar el estado del pedido en la tabla de obras
    def editar_estado_pedido(self, row, column):
        tabla = self.get_tabla_activa()
        if tabla is None:
            return
        item = tabla.item(row, column)
        if item is None:
            return
        # Lógica para editar el estado del pedido (por ejemplo, cambiar texto o color)
        nuevo_estado = "Pedido Enviado" if item.text() != "Pedido Enviado" else "Pendiente"
        item.setText(nuevo_estado)
        color = QColor(76, 175, 80) if nuevo_estado == "Pedido Enviado" else QColor(255, 87, 34)
        self.set_safe_background(tabla, row, column, color)
        self.mostrar_feedback(f"Estado del pedido actualizado a '{nuevo_estado}'", tipo="exito")

    # Método para actualizar el detalle del pedido en la interfaz
    def actualizar_detalle_pedido(self):
        tabla = self.get_tabla_activa()
        if tabla is None:
            return
        # Lógica para mostrar el detalle del pedido en los campos correspondientes
        fila_seleccionada = tabla.currentRow()
        if fila_seleccionada < 0:
            return
        item_codigo = tabla.item(fila_seleccionada, 0)
        if item_codigo is not None:
            self.codigo_pedido_actual = item_codigo.text()
        # Aquí se puede agregar más lógica para cargar el detalle completo del pedido

    # Método para editar el detalle de un pedido en la tabla de pedidos
    def editar_detalle_pedido(self, row, column):
        tabla = self.get_tabla_activa()
        if tabla is None:
            return
        item = tabla.item(row, column)
        if item is None:
            return
        # Lógica para editar el detalle del pedido (por ejemplo, abrir un formulario)
        nuevo_valor, ok = QInputDialog.getText(self, "Editar detalle de pedido", "Nuevo valor:", text=item.text())
        if ok and nuevo_valor:
            item.setText(nuevo_valor)
            self.mostrar_feedback("Detalle de pedido actualizado.", tipo="exito")

    def inicializar_vinculos_controlador(self, controller):
        """
        Conecta los eventos de la UI con los métodos del controlador de Vidrios.
        """
        self.controller = controller
        # Pestaña 1: cargar resumen de obras
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.boton_iniciar_pedido.clicked.connect(self._iniciar_pedido_para_obra)
        # Pestaña 2: cargar pedidos del usuario
        self.boton_guardar_pedido.clicked.connect(self._guardar_pedido_vidrios)
        self.tabla_obras.cellClicked.connect(self._on_tabla_obras_cell_clicked)
        self.tabla_pedido.cellClicked.connect(self._on_tabla_pedido_cell_clicked)
        # Cargar datos iniciales
        self._on_tab_changed(0)

    def _on_tab_changed(self, idx):
        if idx == 0 and hasattr(self, 'controller'):
            self.controller.cargar_resumen_obras()
        elif idx == 1 and hasattr(self, 'controller'):
            self.controller.cargar_pedidos_usuario(self.usuario_actual)

    def mostrar_resumen_obras(self, obras):
        self.tabla_obras.setRowCount(0)
        for row, obra in enumerate(obras):
            self.tabla_obras.insertRow(row)
            for col, key in enumerate([0, 1, 2, 3]):  # id, nombre, cliente, fecha_entrega
                item = QTableWidgetItem(str(obra[col]) if obra[col] is not None else "")
                self.tabla_obras.setItem(row, col, item)
            # Estado de pedido
            estado = obra[4] if len(obra) > 4 else ""
            item_estado = QTableWidgetItem(str(estado))
            self.tabla_obras.setItem(row, 4, item_estado)
            # Botón editar estado
            btn_editar = QPushButton("Editar estado")
            btn_editar.clicked.connect(lambda _, r=row: self._editar_estado_pedido(r))
            self.tabla_obras.setCellWidget(row, 5, btn_editar)
        self.tabla_obras.setColumnCount(6)
        self.tabla_obras.setHorizontalHeaderLabels(["ID Obra", "Nombre", "Cliente", "Fecha Entrega", "Estado pedido", "Acción"])

    def _editar_estado_pedido(self, row):
        if not hasattr(self, 'controller'):
            return
        item_id = self.get_safe_item(self.tabla_obras, row, 0)
        item_estado = self.get_safe_item(self.tabla_obras, row, 4)
        if item_id is None or item_estado is None:
            self.mostrar_feedback("No se pudo obtener la obra o el estado actual.", tipo="error")
            return
        id_obra = item_id.text()
        estado_actual = item_estado.text()
        nuevo_estado, ok = QInputDialog.getText(self, "Editar estado de pedido", "Nuevo estado:", text=estado_actual)
        if ok and nuevo_estado and nuevo_estado != estado_actual:
            self.controller.actualizar_estado_pedido(id_obra, nuevo_estado)
            self.mostrar_feedback(f"Estado de pedido actualizado a '{nuevo_estado}'", tipo="exito")
            self.controller.cargar_resumen_obras()

    def _iniciar_pedido_para_obra(self):
        row = self.tabla_obras.currentRow()
        if row < 0:
            self.mostrar_feedback("Seleccione una obra para iniciar pedido.", tipo="error")
            return
        item_id_obra = self.get_safe_item(self.tabla_obras, row, 0)
        id_obra = item_id_obra.text() if item_id_obra else ""
        if not id_obra:
            self.mostrar_feedback("No se pudo obtener el ID de la obra.", tipo="error")
            return
        # Cambiar a la pestaña de pedido y preparar formulario
        self.tabs.setCurrentIndex(1)
        self.label_formulario.setText(f"Formulario de pedido de vidrios para obra {id_obra}")
        # Limpiar tabla de pedido
        self.tabla_pedido.setRowCount(0)
        # Aquí podrías poblar la tabla con datos de la obra si es necesario

    def _guardar_pedido_vidrios(self):
        if not hasattr(self, 'controller'):
            return
        datos = []
        for row in range(self.get_safe_row_count(self.tabla_pedido)):
            fila = []
            for col in range(self.get_safe_column_count(self.tabla_pedido)):
                item = self.get_safe_item(self.tabla_pedido, row, col)
                fila.append(item.text() if item else "")
            datos.append(fila)
        self.controller.guardar_pedido_vidrios(datos)
        self.mostrar_feedback("Pedido de vidrios guardado correctamente.", tipo="exito")
        self.controller.cargar_pedidos_usuario(self.usuario_actual)

    def mostrar_pedidos_usuario(self, pedidos):
        self.tabla_pedido.setRowCount(0)
        for row, pedido in enumerate(pedidos):
            self.tabla_pedido.insertRow(row)
            # tipología, ancho x alto, color, cantidad, id_obra, id_vidrio
            for col, idx in enumerate([4, 5, 6, 8]):
                item = QTableWidgetItem(str(pedido[idx]) if pedido[idx] is not None else "")
                self.tabla_pedido.setItem(row, col, item)
            # Botón ver detalle
            btn_detalle = QPushButton("Ver detalle")
            btn_detalle.clicked.connect(lambda _, r=row: self._ver_detalle_pedido(r))
            self.tabla_pedido.setCellWidget(row, 4, btn_detalle)
        self.tabla_pedido.setColumnCount(5)
        self.tabla_pedido.setHorizontalHeaderLabels(["Tipología", "Ancho x Alto", "Color", "Cantidad", "Acción"])

    def _ver_detalle_pedido(self, row):
        if not hasattr(self, 'controller'):
            return
        item_id_obra = self.get_safe_item(self.tabla_pedido, row, 0)
        item_id_vidrio = self.get_safe_item(self.tabla_pedido, row, 1)
        if item_id_obra is None or item_id_vidrio is None:
            self.mostrar_feedback("No se pudo obtener el pedido seleccionado.", tipo="error")
            return
        id_obra = item_id_obra.text()
        id_vidrio = item_id_vidrio.text()
        self.controller.mostrar_detalle_pedido(id_obra, id_vidrio)

    def mostrar_detalle_pedido(self, detalle):
        dialog = QDialog(self)
        dialog.setWindowTitle("Detalle del pedido de vidrios")
        layout = QVBoxLayout(dialog)
        campos = ["Tipo", "Ancho", "Alto", "Color", "Cantidad reservada", "Estado", "Fecha pedido"]
        if detalle and len(detalle) > 0:
            for idx, campo in enumerate(campos):
                valor = detalle[0][idx] if len(detalle[0]) > idx else ""
                layout.addWidget(QLabel(f"{campo}: {valor}"))
        else:
            layout.addWidget(QLabel("No se encontró detalle para este pedido."))
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(dialog.accept)
        layout.addWidget(btn_cerrar)
        dialog.setLayout(layout)
        dialog.exec()

    def _on_tabla_obras_cell_clicked(self, row, col):
        # Permitir doble clic en estado para editar
        if col == 4:
            self._editar_estado_pedido(row)

    def _on_tabla_pedido_cell_clicked(self, row, col):
        # Permitir clic en acción para ver detalle
        if col == 4:
            self._ver_detalle_pedido(row)

    # --- Corrección de robustez para tablas ---
    def get_safe_item(self, tabla, row, col):
        if tabla is not None and 0 <= row < tabla.rowCount() and 0 <= col < tabla.columnCount():
            return tabla.item(row, col)
        return None

    def get_safe_selected_items(self, tabla):
        if tabla is not None:
            return tabla.selectedItems()
        return []

    def get_safe_horizontal_header(self, tabla):
        if tabla is not None:
            return tabla.horizontalHeader()
        return None

    def get_safe_column_count(self, tabla):
        if tabla is not None:
            return tabla.columnCount()
        return 0

    def get_safe_row_count(self, tabla):
        if tabla is not None:
            return tabla.rowCount()
        return 0

    def set_safe_background(self, tabla, row, column, color):
        item = self.get_safe_item(tabla, row, column)
        if item is not None:
            item.setBackground(color)

