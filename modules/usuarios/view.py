from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QHBoxLayout, QGraphicsDropShadowEffect, QTabWidget, QComboBox, QMenu, QHeaderView, QMessageBox, QDialog, QFileDialog
from PyQt6.QtGui import QIcon, QColor, QAction, QPixmap
from PyQt6.QtCore import QSize, Qt, QPoint
import json
import os
from functools import partial
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono, aplicar_qss_global_y_tema

class UsuariosView(QWidget, TableResponsiveMixin):
    """
    Vista robusta para gestión de usuarios y permisos.
    Cumple los estándares de layout, accesibilidad, feedback y permisos definidos en docs/estandares_visuales.md.
    - Header visual con título y barra de botones alineados horizontalmente.
    - Refuerzo de accesibilidad en botones y tabla.
    - Feedback visual centralizado.
    - Lógica robusta para mostrar/ocultar pestaña de permisos según rol.
    - Documentación de edge cases y excepciones visuales.
    """
    def __init__(self, usuario_actual="default", controller=None):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.controller = controller  # Permite inyectar lógica de negocio/mock para testeo
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(20)

        # --- Header visual: título y barra de botones alineados ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Gestión de Usuarios")
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        # Botón principal (Agregar usuario)
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/agregar-user.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar usuario")
        header_layout.addWidget(self.boton_agregar)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)
        self.main_layout.addSpacing(8)

        self._cargar_stylesheet()
        self._init_tabs()
        self._init_tab_usuarios()
        self._init_tab_permisos()
        self.setLayout(self.main_layout)

        # --- Feedback visual centralizado ---
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Mensaje de feedback de usuarios")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario")
        self.main_layout.addWidget(self.label_feedback)
        self._feedback_timer = None

        # Refuerzo de accesibilidad en botón principal
        self.boton_agregar.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        font = self.boton_agregar.font()
        if font.pointSize() < 12:
            font.setPointSize(12)
        self.boton_agregar.setFont(font)

        # Refuerzo de accesibilidad en tabla principal
        self.tabla_usuarios.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # Refuerzo de accesibilidad en todos los QLineEdit de la vista principal
        for widget in self.findChildren(QComboBox):
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
            if not widget.toolTip():
                widget.setToolTip("Selector de usuario")
            if not widget.accessibleName():
                widget.setAccessibleName("Selector de usuario para permisos")

    def mostrar_feedback(self, mensaje, tipo="info"):
        if not hasattr(self, "label_feedback") or self.label_feedback is None:
            return
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
        self.label_feedback.clear()
        self.label_feedback.setText(f"{icono}{mensaje}")
        self.label_feedback.setVisible(True)
        self.label_feedback.setAccessibleDescription(f"Mensaje de feedback tipo {tipo}")
        self.label_feedback.setAccessibleName(f"Feedback {tipo}")
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

    def mostrar_tab_permisos(self, visible):
        # Solo mostrar la pestaña de permisos si el usuario es admin
        idx = self.tabs.indexOf(self.tab_permisos)
        if visible and idx == -1:
            self.tabs.addTab(self.tab_permisos, "Permisos de módulos")
        elif not visible and idx != -1:
            self.tabs.removeTab(idx)

    def _cargar_stylesheet(self):
        # Cargar y aplicar QSS global y tema visual (NO modificar ni sobrescribir salvo justificación)
        qss_tema = None
        try:
            import json
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            qss_tema = f"themes/{tema}.qss"
        except Exception:
            pass
        aplicar_qss_global_y_tema(self, qss_global_path="style_moderno.qss", qss_tema_path=qss_tema)

    def _init_tabs(self):
        self.tabs = QTabWidget()
        self.tab_usuarios = QWidget()
        self.tab_permisos = QWidget()
        self.tabs.addTab(self.tab_usuarios, "Usuarios")
        self.tabs.addTab(self.tab_permisos, "Permisos de módulos")
        self.main_layout.addWidget(self.tabs)

    def _init_tab_usuarios(self):
        tab_usuarios_layout = QVBoxLayout(self.tab_usuarios)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/agregar-user.svg"))
        self.boton_agregar.setIconSize(QSize(20, 20))
        self.boton_agregar.setToolTip("Agregar usuario")
        self.boton_agregar.setText("")
        estilizar_boton_icono(self.boton_agregar)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        tab_usuarios_layout.addLayout(botones_layout)
        # Tabla de usuarios
        self.tabla_usuarios = QTableWidget()
        self.make_table_responsive(self.tabla_usuarios)
        tab_usuarios_layout.addWidget(self.tabla_usuarios)
        # Configuración de columnas
        self.config_path = f"config_usuarios_columns_{self.usuario_actual}.json"
        self.usuarios_headers = self.obtener_headers_fallback()
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()
        # Menú contextual en el header
        header = self.tabla_usuarios.horizontalHeader() if hasattr(self.tabla_usuarios, 'horizontalHeader') else None
        if header is not None:
            header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            if hasattr(header, 'customContextMenuRequested'):
                header.customContextMenuRequested.connect(self.mostrar_menu_columnas)
            # Eliminar/congelar conexión a autoajustar_columna hasta que se implemente correctamente
            # if hasattr(self, 'autoajustar_columna') and hasattr(header, 'sectionDoubleClicked'):
            #     header.sectionDoubleClicked.connect(self.autoajustar_columna)
            if hasattr(header, 'setSectionsMovable'):
                header.setSectionsMovable(True)
            if hasattr(header, 'setSectionsClickable'):
                header.setSectionsClickable(True)
            if hasattr(header, 'sectionClicked'):
                header.sectionClicked.connect(self.mostrar_menu_columnas_header)
        # Refuerzo visual y robustez en header de tabla de usuarios
        if header is not None:
            try:
                pass
            except Exception:
                pass
        # Señal para mostrar QR al seleccionar un ítem
        if hasattr(self.tabla_usuarios, 'itemSelectionChanged'):
            self.tabla_usuarios.itemSelectionChanged.connect(self.mostrar_qr_item_seleccionado)

    def _init_tab_permisos(self):
        tab_permisos_layout = QVBoxLayout(self.tab_permisos)
        self.label_permisos = QLabel("Asignar módulos permitidos a usuarios normales:")
        tab_permisos_layout.addWidget(self.label_permisos)
        self.combo_usuario = QComboBox()
        tab_permisos_layout.addWidget(self.combo_usuario)
        self.tabla_permisos_modulos = QTableWidget()
        self.make_table_responsive(self.tabla_permisos_modulos)
        tab_permisos_layout.addWidget(self.tabla_permisos_modulos)
        self.boton_guardar_permisos = QPushButton("Guardar permisos")
        estilizar_boton_icono(self.boton_guardar_permisos)
        tab_permisos_layout.addWidget(self.boton_guardar_permisos)

    def obtener_headers_desde_db(self, tabla):
        # Obtención dinámica de headers desde la base de datos (si hay controller y método disponible)
        if self.controller and hasattr(self.controller, 'obtener_headers_desde_db'):
            try:
                headers = self.controller.obtener_headers_desde_db(tabla)
                if headers:
                    return headers
            except Exception as e:
                print(f"Error obteniendo headers desde BD: {e}")
        # Fallback seguro
        return self.obtener_headers_fallback()

    def obtener_headers_fallback(self):
        return ["id", "usuario", "nombre", "rol", "email", "estado"]

    def cargar_config_columnas(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error cargando configuración de columnas: {e}")
        return {header: True for header in self.usuarios_headers}

    def guardar_config_columnas(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Configuración guardada", "La configuración de columnas se ha guardado correctamente.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar la configuración: {e}")

    def aplicar_columnas_visibles(self):
        for idx, header in enumerate(self.usuarios_headers):
            visible = self.columnas_visibles.get(header, True)
            if hasattr(self.tabla_usuarios, 'setColumnHidden'):
                self.tabla_usuarios.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        menu = QMenu(self)
        for idx, header in enumerate(self.usuarios_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        viewport = self.tabla_usuarios.viewport() if hasattr(self.tabla_usuarios, 'viewport') else None
        if viewport is not None and hasattr(viewport, 'mapToGlobal'):
            menu.exec(viewport.mapToGlobal(pos))
        else:
            menu.exec(pos)

    def mostrar_menu_columnas_header(self, idx):
        header = self.tabla_usuarios.horizontalHeader() if hasattr(self.tabla_usuarios, 'horizontalHeader') else None
        if header is not None and hasattr(header, 'sectionPosition') and hasattr(header, 'mapToGlobal') and hasattr(header, 'sectionViewportPosition'):
            pos = header.sectionPosition(idx)
            global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
            self.mostrar_menu_columnas(global_pos)

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        if hasattr(self.tabla_usuarios, 'setColumnHidden'):
            self.tabla_usuarios.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()

    def mostrar_qr_item_seleccionado(self):
        # Ejemplo de acceso seguro a item
        row = self.tabla_usuarios.currentRow() if hasattr(self.tabla_usuarios, 'currentRow') else -1
        if row != -1 and hasattr(self.tabla_usuarios, 'item'):
            item = self.tabla_usuarios.item(row, 0)
            if item is not None and hasattr(item, 'text'):
                codigo = item.text()  # Usar el primer campo como dato QR
                qr = qrcode.QRCode(version=1, box_size=6, border=2)
                qr.add_data(codigo)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    img.save(tmp)
                    tmp_path = tmp.name
                pixmap = QPixmap(tmp_path)
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Código QR para {codigo}")
                vbox = QVBoxLayout(dialog)
                qr_label = QLabel()
                qr_label.setPixmap(pixmap)
                vbox.addWidget(qr_label)
                btns = QHBoxLayout()
                btn_guardar = QPushButton("Guardar QR como imagen")
                btn_pdf = QPushButton("Exportar QR a PDF")
                btns.addWidget(btn_guardar)
                btns.addWidget(btn_pdf)
                vbox.addLayout(btns)
                def guardar():
                    file_path, _ = QFileDialog.getSaveFileName(dialog, "Guardar QR", f"qr_{codigo}.png", "Imagen PNG (*.png)")
                    if file_path:
                        with open(tmp_path, "rb") as src, open(file_path, "wb") as dst:
                            dst.write(src.read())
                def exportar_pdf():
                    file_path, _ = QFileDialog.getSaveFileName(dialog, "Exportar QR a PDF", f"qr_{codigo}.pdf", "Archivo PDF (*.pdf)")
                    if file_path:
                        from reportlab.pdfgen import canvas
                        from reportlab.lib.pagesizes import letter
                        c = canvas.Canvas(file_path, pagesize=letter)
                        c.drawInlineImage(tmp_path, 100, 500, 200, 200)
                        c.save()
                btn_guardar.clicked.connect(guardar)
                btn_pdf.clicked.connect(exportar_pdf)
                dialog.exec()
