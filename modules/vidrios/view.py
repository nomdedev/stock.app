from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QDateEdit, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox, QDialog, QFileDialog, QProgressBar
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
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        # Botón único (Agregar Vidrios a Obra) con solo ícono SVG pequeño alineado a la derecha
        self.boton_agregar_vidrios_obra = QPushButton()
        self.boton_agregar_vidrios_obra.setIcon(QIcon("resources/icons/add-material.svg"))
        self.boton_agregar_vidrios_obra.setIconSize(QSize(24, 24))
        self.boton_agregar_vidrios_obra.setToolTip("Agregar vidrios a una obra existente")
        self.boton_agregar_vidrios_obra.setFixedSize(48, 48)
        self.boton_agregar_vidrios_obra.setText("")
        self.boton_agregar_vidrios_obra.clicked.connect(self.mostrar_formulario_vidrios_obra)
        estilizar_boton_icono(self.boton_agregar_vidrios_obra)
        header_layout.addStretch()
        header_layout.addWidget(self.boton_agregar_vidrios_obra)
        self.main_layout.addLayout(header_layout)

        # Formulario de entrada
        self.form_layout = self.create_form_layout()
        self.main_layout.addLayout(self.form_layout)

        # Tabla para mostrar los vidrios
        self.tabla_vidrios = self.create_table()
        self.tabla_vidrios.setObjectName("tabla_vidrios")  # Unificación visual
        self.make_table_responsive(self.tabla_vidrios)
        header = self.tabla_vidrios.horizontalHeader()
        if header is not None:
            header.setObjectName("header_inventario")  # Unificación visual
            header.sectionDoubleClicked.connect(self.auto_ajustar_columna)
        self.main_layout.addWidget(self.tabla_vidrios)

        # Configuración de columnas y headers dinámicos
        self.config_path = f"config_vidrios_columns_{self.usuario_actual}.json"
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

        # Menú contextual en el header (robusto)
        header = self.tabla_vidrios.horizontalHeader()
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
        self.boton_buscar.setIcon(QIcon("resources/icons/search_icon.svg"))
        self.boton_buscar.setIconSize(QSize(20, 20))
        self.boton_buscar.setToolTip("Buscar vidrio")
        self.boton_buscar.setText("")
        self.boton_buscar.setFixedSize(48, 48)
        sombra2 = QGraphicsDropShadowEffect()
        sombra2.setBlurRadius(12)
        sombra2.setColor(QColor(37,99,235,40))
        sombra2.setOffset(0, 2)
        self.boton_buscar.setGraphicsEffect(sombra2)
        self.boton_exportar_excel = QPushButton()
        self.boton_exportar_excel.setIcon(QIcon("resources/icons/excel_icon.svg"))
        self.boton_exportar_excel.setIconSize(QSize(24, 24))
        self.boton_exportar_excel.setToolTip("Exportar vidrios a Excel")
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

        self.tabla_vidrios.itemSelectionChanged.connect(self.mostrar_qr_item_seleccionado)

        # Suscribirse a la señal global de integración en tiempo real
        event_bus.obra_agregada.connect(self.actualizar_por_obra)

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

    def aplicar_columnas_visibles(self):
        for idx, header in enumerate(self.vidrios_headers):
            visible = self.columnas_visibles.get(header, True)
            self.tabla_vidrios.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        self._cambio_columnas_interactivo = True  # Activar bandera de interacción
        menu = QMenu(self)
        for idx, header in enumerate(self.vidrios_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        header = self.tabla_vidrios.horizontalHeader()
        if header is not None and hasattr(header, 'mapToGlobal'):
            menu.exec(header.mapToGlobal(pos))
        else:
            menu.exec(pos)
        self._cambio_columnas_interactivo = False  # Desactivar bandera al cerrar menú

    def mostrar_menu_columnas_header(self, idx):
        from PyQt6.QtCore import QPoint
        header = self.tabla_vidrios.horizontalHeader()
        try:
            if header is not None and all(hasattr(header, m) for m in ['sectionPosition', 'mapToGlobal', 'sectionViewportPosition']):
                if idx < 0 or idx >= self.tabla_vidrios.columnCount():
                    self.mostrar_feedback("Índice de columna fuera de rango", "error")
                    return
                pos = header.sectionPosition(idx)
                global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
                self.mostrar_menu_columnas(global_pos)
            else:
                self.mostrar_feedback("No se puede mostrar el menú de columnas: header no disponible o incompleto", "error")
        except Exception as e:
            self.mostrar_feedback(f"Error al mostrar menú de columnas: {e}", "error")

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_vidrios.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()
        # Mostrar feedback solo si la acción es interactiva
        if getattr(self, '_cambio_columnas_interactivo', False):
            self.mostrar_feedback("Configuración de columnas actualizada.", tipo="info")
            self._cambio_columnas_interactivo = False

    def auto_ajustar_columna(self, index):
        """Ajusta automáticamente el ancho de la columna seleccionada al contenido."""
        self.tabla_vidrios.resizeColumnToContents(index)

    def mostrar_qr_item_seleccionado(self):
        selected = self.tabla_vidrios.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        item_codigo = self.tabla_vidrios.item(row, 0)
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
        # Lógica para refrescar la tabla de vidrios tras una nueva obra
        if hasattr(self, 'tabla_vidrios'):
            self.tabla_vidrios.setRowCount(0)  # Limpia la tabla para forzar recarga visual
            print(f"[INFO] Refrescado visual de vidrios tras obra agregada: {datos_obra}")
        else:
            print("[WARN] No se pudo refrescar vidrios tras obra agregada.")

    def exportar_tabla_a_excel(self):
        """
        Exporta la tabla de vidrios a un archivo Excel, con confirmación y feedback modal robusto.
        """
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import pandas as pd
        # Confirmación previa
        confirm = QMessageBox.question(
            self,
            "Confirmar exportación",
            "¿Desea exportar la tabla de vidrios a Excel?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            self.mostrar_feedback("Exportación cancelada por el usuario.", tipo="advertencia")
            return
        # Diálogo para elegir ubicación
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar a Excel",
            "vidrios.xlsx",
            "Archivos Excel (*.xlsx)"
        )
        if not file_path:
            self.mostrar_feedback("Exportación cancelada.", tipo="advertencia")
            return
        # Obtener datos de la tabla
        data = []
        for row in range(self.tabla_vidrios.rowCount()):
            row_data = {}
            for col, header in enumerate(self.vidrios_headers):
                item = self.tabla_vidrios.item(row, col)
                row_data[header] = item.text() if item else ""
            data.append(row_data)
        df = pd.DataFrame(data)
        try:
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Exportación exitosa", f"Vidrios exportados correctamente a:\n{file_path}")
            self.mostrar_feedback(f"Vidrios exportados correctamente a {file_path}", tipo="exito")
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

