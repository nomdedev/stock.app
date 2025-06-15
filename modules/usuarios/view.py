from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QHBoxLayout, QGraphicsDropShadowEffect, QTabWidget, QComboBox, QMenu, QHeaderView, QMessageBox, QDialog, QFileDialog, QTableWidgetItem
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

guardar_permisos_text = "Guardar permisos"
dialog_style = "QDialog { background: #fff9f3; border-radius: 12px; }"
cancelar_tooltip = "Cancelar y cerrar ventana"

# --- Definición de constantes globales para literales y tooltips ---
tooltip_agregar_usuario = "Agregar usuario"
tooltip_guardar = "Guardar cambios"
tooltip_eliminar = "Eliminar usuario"
eliminar_usuario_text = "Eliminar usuario"
tooltip_refrescar = "Refrescar resumen de permisos"
tooltip_permisos = "Permitir acceso a módulo"
tooltip_tabla_usuarios = "Muestra la lista de usuarios registrados"
tooltip_tabla_permisos = "Tabla de permisos por módulo"
tooltip_tabla_resumen = "Visualización de permisos por usuario y módulo. Solo lectura."

# Literales y estilos adicionales para evitar duplicados y advertencias
refrescar_resumen_text = "Refrescar resumen de permisos"
nombre_usuario_text = "Nombre de usuario"
usuario_label = "Usuario:"
permisos_label = "Permisos:"
feedback_label_style = "color: #b91c1c; font-size: 12px;"
finish_check_icon = "resources/icons/finish-check.svg"
close_icon = "resources/icons/close.svg"

class UsuariosView(QWidget, TableResponsiveMixin):
    """
    Vista robusta para gestión de usuarios y permisos.
    Cumple los estándares de layout, accesibilidad, feedback y permisos definidos en docs/estandards_visuales.md.
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

        # Inicializar tabs y tabla antes de cualquier uso
        self._init_tabs()
        self._init_tab_usuarios()
        self._connect_tab_change_signal()
        self._setup_header()
        self._setup_feedback()
        self._setup_accessibility()
        self._apply_qss_theme()
        if hasattr(self, 'actualizar_tabla_usuarios'):
            self.actualizar_tabla_usuarios()

    def _connect_tab_change_signal(self):
        if hasattr(self, 'tabs') and self.tabs is not None:
            self.tabs.currentChanged.connect(self._on_tab_changed)

    def _setup_header(self):
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Gestión de Usuarios")
        self.label_titulo.setObjectName("label_titulo_usuarios")  # Para QSS global
        self.label_titulo.setAccessibleName("Título de módulo Usuarios")
        self.label_titulo.setAccessibleDescription("Encabezado principal de la vista de usuarios")
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        # Botón principal (Agregar usuario)
        self.boton_agregar = QPushButton()
        self.boton_agregar.setObjectName("boton_agregar_usuarios")
        self.boton_agregar.setIcon(QIcon("resources/icons/agregar-user.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip(tooltip_agregar_usuario)
        self.boton_agregar.setAccessibleName("Botón agregar usuario")
        self.boton_agregar.setAccessibleDescription("Agrega un nuevo usuario al sistema")
        estilizar_boton_icono(self.boton_agregar)
        # Aplicar sombra visual al botón principal
        sombra_agregar = QGraphicsDropShadowEffect()
        sombra_agregar.setBlurRadius(12)
        sombra_agregar.setXOffset(0)
        sombra_agregar.setYOffset(2)
        sombra_agregar.setColor(QColor(0, 0, 0, 40))
        self.boton_agregar.setGraphicsEffect(sombra_agregar)
        header_layout.addWidget(self.boton_agregar)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)
        self.main_layout.addSpacing(8)

    def _setup_feedback(self):
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")  # Para QSS global
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Mensaje de feedback de usuarios")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario")
        self.label_feedback.setStyleSheet("")  # Eliminar estilos embebidos
        self.main_layout.addWidget(self.label_feedback)
        self._feedback_timer = None

    def _setup_accessibility(self):
        # Refuerzo de accesibilidad en botón principal
        self._setup_boton_agregar_accessibility()
        # Refuerzo de accesibilidad en tabla principal
        self._setup_tabla_usuarios_accessibility()
        # Refuerzo de accesibilidad en todos los QComboBox de la vista principal
        self._setup_comboboxes_accessibility()

    def _setup_boton_agregar_accessibility(self):
        if hasattr(self, 'boton_agregar') and self.boton_agregar:
            self.boton_agregar.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            font = self.boton_agregar.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            self.boton_agregar.setFont(font)

    def _setup_tabla_usuarios_accessibility(self):
        if hasattr(self, 'tabla_usuarios') and self.tabla_usuarios:
            self.tabla_usuarios.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.tabla_usuarios.setObjectName("tabla_usuarios")

    def _setup_comboboxes_accessibility(self):
        for widget in self.findChildren(QComboBox):
            if widget:
                self._setup_single_combobox_accessibility(widget)

    def _setup_single_combobox_accessibility(self, widget):
        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        font = widget.font()
        if font.pointSize() < 12:
            font.setPointSize(12)
        widget.setFont(font)
        if not widget.toolTip():
            widget.setToolTip("Selector de usuario")
        if not widget.accessibleName():
            widget.setAccessibleName("Selector de usuario para permisos")

    def _apply_qss_theme(self):
        # Aplicar QSS global y tema visual (solo desde resources/qss/)
        try:
            from utils.theme_manager import cargar_modo_tema
            tema = cargar_modo_tema()
            qss_tema = f"resources/qss/theme_{tema}.qss"
            aplicar_qss_global_y_tema(self, qss_global_path="resources/qss/theme_light.qss", qss_tema_path=qss_tema)
        except Exception as e:
            print(f"Error aplicando QSS global: {e}")

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
        if not hasattr(self, "label_feedback") or self.label_feedback is None:
            return
        self.label_feedback.setVisible(False)
        self.label_feedback.clear()
        if hasattr(self, '_feedback_timer') and self._feedback_timer:
            self._feedback_timer.stop()

    def mostrar_tab_permisos(self, visible):
        # Robustecer acceso a tabs y tab_permisos
        if not hasattr(self, 'tabs') or self.tabs is None or not hasattr(self, 'tab_permisos') or self.tab_permisos is None:
            self.mostrar_feedback("No se puede mostrar/ocultar la pestaña de permisos: tabs o tab_permisos no inicializados", "error")
            return
        idx = self.tabs.indexOf(self.tab_permisos) if self.tabs and self.tab_permisos else -1
        if visible and idx == -1:
            self.tabs.addTab(self.tab_permisos, "Permisos de módulos")
        elif not visible and idx != -1:
            self.tabs.removeTab(idx)

    def _cargar_stylesheet(self):
        try:
            from utils.theme_manager import cargar_modo_tema
            tema = cargar_modo_tema()
            qss_tema = f"resources/qss/theme_{tema}.qss"
            aplicar_qss_global_y_tema(self, qss_global_path="resources/qss/theme_light.qss", qss_tema_path=qss_tema)
        except Exception as e:
            self.mostrar_feedback(f"Error cargando tema: {e}", "error")

    def _init_tabs(self):
        self.tabs = QTabWidget()
        self.tab_usuarios = QWidget()
        self.tab_permisos = QWidget()
        self.tab_resumen_permisos = QWidget()
        self.tabs.addTab(self.tab_usuarios, "Usuarios")
        self.tabs.addTab(self.tab_permisos, "Permisos de módulos")
        self.tabs.addTab(self.tab_resumen_permisos, "Resumen de permisos")
        self.main_layout.addWidget(self.tabs)
        self._init_tab_resumen_permisos()
        # --- Refresco automático al cambiar de pestaña ---
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        """
        Refresca automáticamente las tablas de usuarios, permisos y resumen al cambiar de pestaña.
        """
        if not hasattr(self, 'tabs') or self.tabs is None:
            return
        current_widget = self.tabs.currentWidget()
        if self._is_tab(current_widget, 'tab_usuarios'):
            self._refresh_tab_usuarios()
        elif self._is_tab(current_widget, 'tab_permisos'):
            self._refresh_tab_permisos()
        elif self._is_tab(current_widget, 'tab_resumen_permisos'):
            self._refresh_tab_resumen_permisos()

    def _is_tab(self, widget, tab_attr):
        return hasattr(self, tab_attr) and getattr(self, tab_attr) is widget

    def _refresh_tab_usuarios(self):
        if hasattr(self, 'actualizar_tabla_usuarios'):
            self.actualizar_tabla_usuarios()

    def _refresh_tab_permisos(self):
        if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'cargar_permisos_modulos'):
            self.controller.cargar_permisos_modulos()

    def _refresh_tab_resumen_permisos(self):
        if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'cargar_resumen_permisos'):
            self.controller.cargar_resumen_permisos()

    def _init_tab_usuarios(self):
        tab_usuarios_layout = QVBoxLayout(self.tab_usuarios)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setObjectName("boton_agregar_usuarios")
        self.boton_agregar.setIcon(QIcon("resources/icons/agregar-user.svg"))
        self.boton_agregar.setIconSize(QSize(20, 20))
        self.boton_agregar.setToolTip(tooltip_agregar_usuario)
        self.boton_agregar.setAccessibleName("Botón agregar usuario")
        self.boton_agregar.setAccessibleDescription("Agrega un nuevo usuario al sistema")
        self.boton_agregar.setText("")
        estilizar_boton_icono(self.boton_agregar)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        tab_usuarios_layout.addLayout(botones_layout)
        # Tabla de usuarios
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setObjectName("tabla_usuarios")
        self.tabla_usuarios.setAccessibleName("Tabla de usuarios")
        self.tabla_usuarios.setAccessibleDescription(tooltip_tabla_usuarios)
        self.tabla_usuarios.setToolTip(tooltip_tabla_usuarios)
        self.make_table_responsive(self.tabla_usuarios)
        tab_usuarios_layout.addWidget(self.tabla_usuarios)
        # Configuración de columnas
        self.config_path = f"config_usuarios_columns_{self.usuario_actual}.json"
        self.usuarios_headers = self.obtener_headers_fallback()
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()
        # Menú contextual en el header
        header = self.tabla_usuarios.horizontalHeader() if hasattr(self, 'tabla_usuarios') and self.tabla_usuarios else None
        if header is not None:
            header.setObjectName("header_inventario")
            header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            if hasattr(header, 'customContextMenuRequested'):
                header.customContextMenuRequested.connect(self.mostrar_menu_columnas)
            if hasattr(header, 'setSectionsMovable'):
                header.setSectionsMovable(True)
            if hasattr(header, 'setSectionsClickable'):
                header.setSectionsClickable(True)
            if hasattr(header, 'sectionClicked'):
                header.sectionClicked.connect(self.mostrar_menu_columnas_header)
        # Refuerzo visual y robustez en header de tabla de usuarios
        if header is not None:
            # No es necesario un try vacío aquí, ya que no hay código que pueda lanzar excepción
            pass
        # Señal para mostrar QR al seleccionar un ítem
        if hasattr(self, 'tabla_usuarios') and self.tabla_usuarios and hasattr(self.tabla_usuarios, 'itemSelectionChanged'):
            self.tabla_usuarios.itemSelectionChanged.connect(self.mostrar_qr_item_seleccionado)

    def _init_tab_permisos(self):
        tab_permisos_layout = QVBoxLayout(self.tab_permisos)
        self.label_permisos = QLabel("Asignar módulos permitidos a usuarios normales:")
        tab_permisos_layout.addWidget(self.label_permisos)
        self.combo_usuario = QComboBox()
        self.combo_usuario.setToolTip("Seleccionar usuario para asignar permisos")
        self.combo_usuario.setAccessibleName("Selector de usuario para permisos")
        tab_permisos_layout.addWidget(self.combo_usuario)
        self.tabla_permisos_modulos = QTableWidget()
        self.tabla_permisos_modulos.setToolTip(tooltip_tabla_permisos)
        self.tabla_permisos_modulos.setAccessibleName("Tabla de permisos de módulos")
        tab_permisos_layout.addWidget(self.tabla_permisos_modulos)
        self.boton_guardar_permisos = QPushButton(guardar_permisos_text)
        self.boton_guardar_permisos.setIcon(QIcon("resources/icons/guardar.svg"))
        self.boton_guardar_permisos.setIconSize(QSize(20, 20))
        self.boton_guardar_permisos.setToolTip(tooltip_guardar)
        estilizar_boton_icono(self.boton_guardar_permisos)
        self.boton_refrescar_resumen = QPushButton(refrescar_resumen_text)
        self.boton_refrescar_resumen.setIcon(QIcon("resources/icons/actualizar.svg"))
        self.boton_refrescar_resumen.setIconSize(QSize(20, 20))
        self.boton_refrescar_resumen.setToolTip(tooltip_refrescar)
        estilizar_boton_icono(self.boton_refrescar_resumen)
        tab_permisos_layout.addWidget(self.boton_guardar_permisos)
        tab_permisos_layout.addWidget(self.boton_refrescar_resumen)

    def _init_tab_resumen_permisos(self):
        layout = QVBoxLayout(self.tab_resumen_permisos)
        self.boton_refrescar_resumen = QPushButton(refrescar_resumen_text)
        self.boton_refrescar_resumen.setObjectName("boton_refrescar_resumen_permisos")
        self.boton_refrescar_resumen.setIcon(QIcon("resources/icons/refresh-cw.svg"))
        self.boton_refrescar_resumen.setIconSize(QSize(20, 20))
        self.boton_refrescar_resumen.setToolTip(tooltip_refrescar)
        estilizar_boton_icono(self.boton_refrescar_resumen)
        layout.addWidget(self.boton_refrescar_resumen)
        self.tabla_resumen_permisos = QTableWidget()
        self.tabla_resumen_permisos.setObjectName("tabla_resumen_permisos")
        self.tabla_resumen_permisos.setToolTip(tooltip_tabla_resumen)
        self.tabla_resumen_permisos.setAccessibleName("Tabla de resumen de permisos")
        self.make_table_responsive(self.tabla_resumen_permisos)
        layout.addWidget(self.tabla_resumen_permisos)
        self.label_resumen_info = QLabel(tooltip_tabla_resumen)
        layout.addWidget(self.label_resumen_info)

    def obtener_headers_desde_db(self, tabla):
        if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'obtener_headers_desde_db'):
            try:
                headers = self.controller.obtener_headers_desde_db(tabla)
                if headers:
                    return headers
            except Exception as e:
                self.mostrar_feedback(f"Error obteniendo headers desde BD: {e}", "error")
        return self.obtener_headers_fallback()

    def obtener_headers_fallback(self):
        return ["id", "usuario", "nombre", "rol", "email", "estado"]

    def cargar_config_columnas(self):
        try:
            if hasattr(self, 'config_path') and self.config_path and os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            self.mostrar_feedback(f"Error cargando configuración de columnas: {e}", "error")
        return {header: True for header in self.usuarios_headers}

    def guardar_config_columnas(self):
        try:
            if not hasattr(self, 'config_path') or not self.config_path:
                return
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)
            # Eliminado feedback modal innecesario
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar la configuración: {e}")

    def aplicar_columnas_visibles(self):
        # Sincronizar columnas_visibles con usuarios_headers
        if not hasattr(self, 'tabla_usuarios') or self.tabla_usuarios is None:
            self.mostrar_feedback("Tabla de usuarios no inicializada para aplicar columnas visibles", "error")
            return
        if not hasattr(self, 'usuarios_headers') or not self.usuarios_headers:
            self.mostrar_feedback("Headers de usuarios no definidos para aplicar columnas visibles", "error")
            return
        # Reparar claves faltantes o sobrantes en columnas_visibles
        headers_set = set(self.usuarios_headers)
        visibles_set = set(self.columnas_visibles.keys())
        # Agregar headers nuevos
        for h in headers_set - visibles_set:
            self.columnas_visibles[h] = True
        # Eliminar claves huérfanas
        for h in visibles_set - headers_set:
            del self.columnas_visibles[h]
        self.guardar_config_columnas()
        # Aplicar visibilidad
        for idx, header in enumerate(self.usuarios_headers):
            visible = self.columnas_visibles.get(header, True)
            if hasattr(self.tabla_usuarios, 'setColumnHidden'):
                self.tabla_usuarios.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        # Robustez: sincronizar antes de mostrar menú
        if not self._tabla_usuarios_disponible():
            self.mostrar_feedback("Tabla de usuarios no disponible para menú de columnas.", "error")
            return
        if not self._usuarios_headers_disponibles():
            self.mostrar_feedback("Headers de usuarios no definidos.", "error")
            return
        self._sincronizar_columnas_visibles()
        if not self.usuarios_headers:
            self.mostrar_feedback("No hay columnas configurables para mostrar en el menú.", "error")
            return
        menu, any_action = self._construir_menu_columnas()
        if not any_action:
            self.mostrar_feedback("No hay columnas configurables para mostrar en el menú.", "error")
            return
        self._mostrar_menu_en_posicion(menu, pos)

    def _tabla_usuarios_disponible(self):
        return hasattr(self, 'tabla_usuarios') and self.tabla_usuarios is not None

    def _usuarios_headers_disponibles(self):
        return hasattr(self, 'usuarios_headers') and self.usuarios_headers

    def _sincronizar_columnas_visibles(self):
        headers_set = set(self.usuarios_headers)
        visibles_set = set(self.columnas_visibles.keys())
        if headers_set != visibles_set:
            self.mostrar_feedback("Detectada desincronización de columnas. Reparando...", "advertencia")
            for h in headers_set - visibles_set:
                self.columnas_visibles[h] = True
            for h in visibles_set - headers_set:
                del self.columnas_visibles[h]
            self.guardar_config_columnas()

    def _construir_menu_columnas(self):
        menu = QMenu(self)
        any_action = False
        for idx, header in enumerate(self.usuarios_headers):
            if header is None or header == "":
                continue
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
            any_action = True
        return menu, any_action

    def _mostrar_menu_en_posicion(self, menu, pos):
        viewport = self.tabla_usuarios.viewport() if hasattr(self.tabla_usuarios, 'viewport') else None
        if viewport is not None and hasattr(viewport, 'mapToGlobal'):
            menu.exec(viewport.mapToGlobal(pos))
        else:
            menu.exec(pos)

    def toggle_columna(self, idx, header, checked):
        # Robustez: asegurar que header existe en usuarios_headers
        if not hasattr(self, 'usuarios_headers') or header not in self.usuarios_headers:
            self.mostrar_feedback(f"Header '{header}' no válido para toggle_columna", "error")
            return
        self.columnas_visibles[header] = checked
        if hasattr(self, 'tabla_usuarios') and self.tabla_usuarios and hasattr(self.tabla_usuarios, 'setColumnHidden'):
            self.tabla_usuarios.setColumnHidden(idx, not checked)
        else:
            self.mostrar_feedback("No se pudo ocultar/mostrar columna: tabla_usuarios no inicializada", "error")
        self.guardar_config_columnas()

    def mostrar_qr_item_seleccionado(self):
        if not hasattr(self, 'tabla_usuarios') or self.tabla_usuarios is None or not hasattr(self.tabla_usuarios, 'currentRow'):
            self.mostrar_feedback("Tabla de usuarios no inicializada para mostrar QR", "error")
            return
        row = self.tabla_usuarios.currentRow()
        if row == -1 or not hasattr(self.tabla_usuarios, 'item'):
            return
        item = self.tabla_usuarios.item(row, 0)
        if item is None or not hasattr(item, 'text'):
            return
        codigo = item.text()
        try:
            tmp_path = self._generar_qr_tempfile(codigo)
            pixmap = QPixmap(tmp_path)
            self._mostrar_qr_dialogo(codigo, pixmap, tmp_path)
        except Exception as e:
            self.mostrar_feedback(f"Error generando QR: {e}", "error")

    def _generar_qr_tempfile(self, codigo):
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(codigo)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            img.save(tmp)
            return tmp.name

    def _mostrar_qr_dialogo(self, codigo, pixmap, tmp_path):
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
        btn_guardar.clicked.connect(lambda: self._guardar_qr_imagen(dialog, tmp_path, codigo))
        btn_pdf.clicked.connect(lambda: self._exportar_qr_pdf(dialog, tmp_path, codigo))
        dialog.exec()

    def _guardar_qr_imagen(self, dialog, tmp_path, codigo):
        file_path, _ = QFileDialog.getSaveFileName(dialog, "Guardar QR", f"qr_{codigo}.png", "Imagen PNG (*.png)")
        if file_path:
            with open(tmp_path, "rb") as src, open(file_path, "wb") as dst:
                dst.write(src.read())

    def _exportar_qr_pdf(self, dialog, tmp_path, codigo):
        file_path, _ = QFileDialog.getSaveFileName(dialog, "Exportar QR a PDF", f"qr_{codigo}.pdf", "Archivo PDF (*.pdf)")
        if file_path:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            c = canvas.Canvas(file_path, pagesize=letter)
            c.drawInlineImage(tmp_path, 100, 500, 200, 200)
            c.save()

    def cargar_resumen_permisos(self, usuarios, modulos, permisos_dict):
        """
        Carga la tabla de resumen de permisos de forma robusta y defensiva.
        Edge cases cubiertos:
        - Si la tabla no está inicializada, muestra feedback y no lanza excepción.
        - Si los datos de entrada no son del tipo esperado, muestra feedback y no lanza excepción.
        - Si algún usuario no tiene los campos esperados, se maneja de forma segura.
        Cumple checklist de robustez, feedback y accesibilidad (ver docs/estandares_feedback.md y checklist_formularios_botones_ui.txt).
        """
        if not hasattr(self, 'tabla_resumen_permisos') or self.tabla_resumen_permisos is None:
            self.mostrar_feedback("Tabla de resumen de permisos no inicializada", "error")
            return
        if not isinstance(usuarios, (list, tuple)) or not isinstance(modulos, (list, tuple)) or not isinstance(permisos_dict, dict):
            self.mostrar_feedback("Datos inválidos para cargar resumen de permisos", "error")
            return
        self.tabla_resumen_permisos.clear()
        headers = ["Usuario", "Rol", "Módulo", "Ver", "Modificar", "Aprobar"]
        self.tabla_resumen_permisos.setColumnCount(len(headers))
        self.tabla_resumen_permisos.setHorizontalHeaderLabels(headers)
        rows = 0
        for usuario in usuarios:
            usuario_id, usuario_nombre, rol = self._extraer_campos_usuario(usuario)
            for modulo in modulos:
                permisos = self._obtener_permisos_usuario_modulo(permisos_dict, usuario_id, modulo)
                self._agregar_fila_resumen_permisos(rows, usuario_nombre, rol, modulo, permisos)
                rows += 1
        self.tabla_resumen_permisos.resizeColumnsToContents()

    def _extraer_campos_usuario(self, usuario):
        usuario_id = None
        usuario_nombre = ""
        rol = ""
        if isinstance(usuario, dict):
            usuario_id = usuario.get('id')
            usuario_nombre = usuario.get('usuario', str(usuario_id))
            rol = usuario.get('rol', '')
        elif isinstance(usuario, (list, tuple)):
            usuario_id = usuario[0] if len(usuario) > 0 else None
            usuario_nombre = usuario[4] if len(usuario) > 4 else str(usuario_id)
            rol = usuario[6] if len(usuario) > 6 else ''
        else:
            usuario_nombre = str(usuario)
        return usuario_id, usuario_nombre, rol

    def _obtener_permisos_usuario_modulo(self, permisos_dict, usuario_id, modulo):
        return permisos_dict.get((usuario_id, modulo), {'ver': False, 'modificar': False, 'aprobar': False})

    def _agregar_fila_resumen_permisos(self, row, usuario_nombre, rol, modulo, permisos):
        self.tabla_resumen_permisos.insertRow(row)
        self.tabla_resumen_permisos.setItem(row, 0, QTableWidgetItem(str(usuario_nombre)))
        self.tabla_resumen_permisos.setItem(row, 1, QTableWidgetItem(str(rol)))
        self.tabla_resumen_permisos.setItem(row, 2, QTableWidgetItem(str(modulo)))
        for i, key in enumerate(['ver', 'modificar', 'aprobar']):
            item = QTableWidgetItem("✅" if permisos.get(key, False) else "❌")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_resumen_permisos.setItem(row, 3 + i, item)

    def abrir_dialogo_crear_usuario(self):
        """
        Abre un diálogo modal robusto para crear un nuevo usuario.
        Cumple checklist: validación visual/backend, feedback, accesibilidad, tooltips, cierre solo en éxito, validación de contraseña fuerte.
        """
        if not hasattr(self, 'controller') or self.controller is None:
            self.mostrar_feedback("Controlador no disponible para crear usuario.", "error")
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QHBoxLayout, QLabel, QCheckBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Crear Usuario")
        dialog.setStyleSheet(dialog_style)
        dialog.setStyleSheet(dialog_style)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)

        username_input = self._crear_input_usuario(form)
        password_input = self._crear_input_contrasena(form)
        combo_rol = self._crear_combo_rol(form)
        checkboxes = self._crear_checkboxes_permisos(form)
        lbl_feedback = self._crear_label_feedback_crear(form)

        layout.addLayout(form)
        btn_guardar, btn_cancelar = self._crear_botones_guardar_cancelar(layout)

        btn_guardar.clicked.connect(
            lambda: self._accion_guardar_usuario(
                dialog, username_input, password_input, combo_rol, checkboxes, lbl_feedback
            )
        )
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def _crear_input_usuario(self, form):
        from PyQt6.QtWidgets import QLineEdit
        username_input = QLineEdit()
        username_input.setPlaceholderText(nombre_usuario_text)
        username_input.setToolTip("Ingrese el nombre de usuario")
        username_input.setAccessibleName(nombre_usuario_text)
        form.addRow(usuario_label, username_input)
        return username_input

    def _crear_input_contrasena(self, form):
        from PyQt6.QtWidgets import QLineEdit
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_input.setPlaceholderText("Contraseña fuerte")
        password_input.setToolTip("Ingrese una contraseña fuerte (mín. 8 caracteres, mayúscula, minúscula, número y símbolo)")
        password_input.setAccessibleName("Contraseña")
        form.addRow("Contraseña:", password_input)
        return password_input

    def _crear_combo_rol(self, form):
        from PyQt6.QtWidgets import QComboBox
        combo_rol = QComboBox()
        combo_rol.setToolTip("Seleccionar rol del usuario")
        combo_rol.setAccessibleName("Rol de usuario")
        roles = []
        if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'obtener_roles'):
            try:
                roles = self.controller.obtener_roles()
            except Exception as e:
                self.mostrar_feedback(f"Error obteniendo roles: {e}", "error")
        for rol in roles:
            combo_rol.addItem(rol)
        form.addRow("Rol:", combo_rol)
        return combo_rol

    def _crear_checkboxes_permisos(self, form):
        from PyQt6.QtWidgets import QVBoxLayout, QCheckBox
        permisos_layout = QVBoxLayout()
        permisos = []
        if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'obtener_permisos_modulos'):
            try:
                permisos = self.controller.obtener_permisos_modulos()
            except Exception as e:
                self.mostrar_feedback(f"Error obteniendo permisos: {e}", "error")
        checkboxes = []
        for permiso in permisos:
            cb = QCheckBox(permiso)
            cb.setToolTip(f"Permitir acceso a {permiso}")
            cb.setAccessibleName(f"Permiso {permiso}")
            permisos_layout.addWidget(cb)
            checkboxes.append(cb)
        form.addRow(permisos_label, permisos_layout)
        return checkboxes

    def _crear_label_feedback_crear(self, form):
        from PyQt6.QtWidgets import QLabel
        lbl_feedback = QLabel()
        lbl_feedback.setStyleSheet(feedback_label_style)
        lbl_feedback.setVisible(False)
        form.addRow("", lbl_feedback)
        return lbl_feedback

    def _crear_botones_guardar_cancelar(self, layout):
        from PyQt6.QtWidgets import QPushButton, QHBoxLayout
        btns = QHBoxLayout()
        btn_guardar = QPushButton()
        btn_guardar.setIcon(QIcon(finish_check_icon))
        btn_guardar.setToolTip("Crear usuario")
        btn_guardar.setAccessibleName("Crear usuario")
        estilizar_boton_icono(btn_guardar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon(close_icon))
        btn_cancelar.setToolTip(cancelar_tooltip)
        btn_cancelar.setAccessibleName("Cancelar")
        estilizar_boton_icono(btn_cancelar)
        btns.addStretch()
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        return btn_guardar, btn_cancelar

    def _es_contrasena_fuerte(self, pw):
        import re
        return (
            len(pw) >= 8 and
            re.search(r"[A-Z]", pw) and
            re.search(r"[a-z]", pw) and
            re.search(r"\d", pw) and
            re.search(r"[^A-Za-z0-9]", pw)
        )

    def _accion_guardar_usuario(self, dialog, username_input, password_input, combo_rol, checkboxes, lbl_feedback):
        username = username_input.text().strip()
        password = password_input.text()
        rol = combo_rol.currentText()
        permisos_seleccionados = [cb.text() for cb in checkboxes if cb.isChecked()]
        if not username or not password or not rol:
            lbl_feedback.setText("Complete todos los campos obligatorios.")
            lbl_feedback.setVisible(True)
            return
        if not self._es_contrasena_fuerte(password):
            lbl_feedback.setText("La contraseña debe tener al menos 8 caracteres, mayúscula, minúscula, número y símbolo.")
            lbl_feedback.setVisible(True)
            return
        try:
            if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'crear_usuario'):
                self.controller.crear_usuario(username, password, rol, permisos_seleccionados)
                self.mostrar_feedback("Usuario creado correctamente.", tipo="exito")
                dialog.accept()
                if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'actualizar_tabla_usuarios'):
                    self.controller.actualizar_tabla_usuarios()
            else:
                self.mostrar_feedback("No se implementó la lógica de crear usuario.", tipo="error")
        except Exception as e:
            lbl_feedback.setText(f"Error: {e}")
            lbl_feedback.setVisible(True)

    def abrir_dialogo_editar_usuario(self, usuario):
        """
        Abre un diálogo modal robusto para editar un usuario existente.
        Cumple checklist: validación visual/backend, feedback, accesibilidad, tooltips, cierre solo en éxito, validación de contraseña fuerte si se cambia.
        usuario: dict con claves 'username', 'rol', 'permisos' (lista de str)
        """
        if not hasattr(self, 'controller') or self.controller is None:
            self.mostrar_feedback("Controlador no disponible para editar usuario.", "error")
            return
        if not usuario or not isinstance(usuario, dict):
            self.mostrar_feedback("Datos de usuario inválidos para edición.", "error")
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Editar Usuario: {usuario.get('username','')}")
        dialog.setModal(True)
        dialog.setStyleSheet(dialog_style)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)

        username_input = self._crear_input_editar_usuario(form, usuario)
        password_input = self._crear_input_editar_contrasena(form)
        combo_rol = self._crear_combo_rol_editar(form, usuario)
        checkboxes = self._crear_checkboxes_permisos_editar(form, usuario)
        lbl_feedback = self._crear_label_feedback(form)

        layout.addLayout(form)
        btn_guardar, btn_cancelar = self._crear_botones_guardar_cancelar_editar(layout)

        btn_guardar.clicked.connect(
            lambda: self._accion_guardar_edicion_usuario(
                dialog, username_input, password_input, combo_rol, checkboxes, lbl_feedback
            )
        )
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def _crear_input_editar_usuario(self, form, usuario):
        from PyQt6.QtWidgets import QLineEdit
        username_input = QLineEdit(usuario.get('username',''))
        username_input.setReadOnly(True)
        username_input.setToolTip(nombre_usuario_text + " (no editable)")
        username_input.setAccessibleName(nombre_usuario_text)
        form.addRow(usuario_label, username_input)
        return username_input

    def _crear_input_editar_contrasena(self, form):
        from PyQt6.QtWidgets import QLineEdit
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_input.setPlaceholderText("Nueva contraseña (opcional)")
        password_input.setToolTip("Ingrese una nueva contraseña fuerte si desea cambiarla")
        password_input.setAccessibleName("Contraseña")
        form.addRow("Contraseña:", password_input)
        return password_input

    def _crear_combo_rol_editar(self, form, usuario):
        from PyQt6.QtWidgets import QComboBox
        combo_rol = QComboBox()
        combo_rol.setToolTip("Seleccionar rol del usuario")
        combo_rol.setAccessibleName("Rol de usuario")
        roles = []
        if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'obtener_roles'):
            try:
                roles = self.controller.obtener_roles()
            except Exception as e:
                self.mostrar_feedback(f"Error obteniendo roles: {e}", "error")
        for rol in roles:
            combo_rol.addItem(rol)
        if usuario.get('rol') and usuario.get('rol') in roles:
            combo_rol.setCurrentText(usuario['rol'])
        form.addRow("Rol:", combo_rol)
        return combo_rol

    def _crear_checkboxes_permisos_editar(self, form, usuario):
        from PyQt6.QtWidgets import QVBoxLayout, QCheckBox
        permisos_layout = QVBoxLayout()
        permisos = []
        if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'obtener_permisos_modulos'):
            try:
                permisos = self.controller.obtener_permisos_modulos()
            except Exception as e:
                self.mostrar_feedback(f"Error obteniendo permisos: {e}", "error")
        checkboxes = []
        permisos_usuario = set(usuario.get('permisos', []))
        for permiso in permisos:
            cb = QCheckBox(permiso)
            cb.setToolTip(f"Permitir acceso a {permiso}")
            cb.setAccessibleName(f"Permiso {permiso}")
            if permiso in permisos_usuario:
                cb.setChecked(True)
            permisos_layout.addWidget(cb)
            checkboxes.append(cb)
        form.addRow(permisos_label, permisos_layout)
        return checkboxes

    def _crear_label_feedback(self, form):
        from PyQt6.QtWidgets import QLabel
        lbl_feedback = QLabel("Realice los cambios necesarios y guarde para actualizar el usuario.")
        lbl_feedback.setStyleSheet("color: #2563eb; font-size: 12px;")
        lbl_feedback.setVisible(False)
        lbl_feedback.setObjectName("label_feedback_edicion_usuario")
        form.addRow("", lbl_feedback)
        return lbl_feedback

    def _crear_botones_guardar_cancelar_editar(self, layout):
        from PyQt6.QtWidgets import QPushButton, QHBoxLayout
        btns = QHBoxLayout()
        btn_guardar = QPushButton()
        btn_guardar.setIcon(QIcon(finish_check_icon))
        btn_guardar.setToolTip(tooltip_guardar)
        btn_guardar.setAccessibleName(tooltip_guardar)
        estilizar_boton_icono(btn_guardar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon(close_icon))
        btn_cancelar.setToolTip(cancelar_tooltip)
        btn_cancelar.setAccessibleName("Cancelar")
        estilizar_boton_icono(btn_cancelar)
        btns.addStretch()
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        return btn_guardar, btn_cancelar

    def _es_contrasena_fuerte_editar(self, pw):
        import re
        # For editing, require password not to contain the username as a substring (if available)
        if hasattr(self, 'usuario_actual') and self.usuario_actual and self.usuario_actual.lower() in pw.lower():
            return False
        return (
            len(pw) >= 8 and
            re.search(r"[A-Z]", pw) and
            re.search(r"[a-z]", pw) and
            re.search(r"\d", pw) and
            re.search(r"[^A-Za-z0-9]", pw)
        )

    def _accion_guardar_edicion_usuario(self, dialog, username_input, password_input, combo_rol, checkboxes, lbl_feedback):
        rol = combo_rol.currentText()
        permisos_seleccionados = [cb.text() for cb in checkboxes if cb.isChecked()]
        nueva_contrasena = password_input.text()
        if not rol:
            lbl_feedback.setText("Seleccione un rol.")
            lbl_feedback.setVisible(True)
            return
        if nueva_contrasena and not self._es_contrasena_fuerte_editar(nueva_contrasena):
            lbl_feedback.setText("La nueva contraseña debe tener al menos 8 caracteres, mayúscula, minúscula, número y símbolo.")
            lbl_feedback.setVisible(True)
            return
        try:
            if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'editar_usuario'):
                self.controller.editar_usuario(
                    username_input.text(),
                    nueva_contrasena if nueva_contrasena else None,
                    rol,
                    permisos_seleccionados
                )
                self.mostrar_feedback("Usuario editado correctamente.", tipo="exito")
                dialog.accept()
                if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'actualizar_tabla_usuarios'):
                    self.controller.actualizar_tabla_usuarios()
            else:
                self.mostrar_feedback("No se implementó la lógica de editar usuario.", tipo="error")
        except Exception as e:
            lbl_feedback.setText(f"Error: {e}")
            lbl_feedback.setVisible(True)

    def abrir_dialogo_editar_permisos(self, usuario):
        """
        Abre un diálogo modal robusto para editar los permisos de un usuario.
        Cumple checklist: validación visual/backend, feedback, accesibilidad, tooltips, cierre solo en éxito.
        usuario: dict con claves 'username', 'rol', 'permisos' (lista de str)
        """
        if not self._puede_editar_permisos(usuario):
            return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLabel, QPushButton, QHBoxLayout
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Editar Permisos: {usuario.get('username','')}")
        dialog.setModal(True)
        dialog.setStyleSheet(dialog_style)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)

        self._agregar_usuario_readonly(form, usuario)
        checkboxes = self._crear_checkboxes_permisos_editar(form, usuario)
        lbl_feedback = self._crear_label_feedback_crear(form)
        layout.addLayout(form)

        btn_guardar, btn_cancelar = self._crear_botones_guardar_cancelar(layout)
        btn_guardar.clicked.connect(
            lambda: self._accion_guardar_permisos(dialog, usuario, checkboxes, lbl_feedback)
        )
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def _puede_editar_permisos(self, usuario):
        if not hasattr(self, 'controller') or self.controller is None:
            self.mostrar_feedback("Controlador no disponible para editar permisos.", "error")
            return False
        if not usuario or not isinstance(usuario, dict):
            self.mostrar_feedback("Datos de usuario inválidos para edición de permisos.", "error")
            return False
        return True

    def _agregar_usuario_readonly(self, form, usuario):
        from PyQt6.QtWidgets import QLabel
        lbl_usuario = QLabel(usuario.get('username',''))
        lbl_usuario.setToolTip("Usuario al que se le asignan permisos")
        lbl_usuario.setAccessibleName("Usuario")
        form.addRow("Usuario:", lbl_usuario)

    def _accion_guardar_permisos(self, dialog, usuario, checkboxes, lbl_feedback):
        permisos_seleccionados = [cb.text() for cb in checkboxes if cb.isChecked()]
        if not permisos_seleccionados:
            lbl_feedback.setText("Seleccione al menos un permiso.")
            lbl_feedback.setVisible(True)
            return
        try:
            if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'editar_permisos_usuario'):
                self.controller.editar_permisos_usuario(
                    usuario.get('username',''),
                    permisos_seleccionados
                )
                self.mostrar_feedback("Permisos actualizados correctamente.", tipo="exito")
                dialog.accept()
                if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'actualizar_tabla_usuarios'):
                    self.controller.actualizar_tabla_usuarios()
            else:
                self.mostrar_feedback("No se implementó la lógica de editar permisos.", tipo="error")
        except Exception as e:
            lbl_feedback.setText(f"Error: {e}")
            lbl_feedback.setVisible(True)

    def abrir_dialogo_eliminar_usuario(self, usuario):
        """
        Abre un diálogo modal robusto para eliminar un usuario existente.
        Cumple checklist: confirmación modal, feedback visual/accesible, cierre solo en éxito, tooltips, logging/auditoría, refresco de UI.
        usuario: dict con claves 'id', 'username', 'rol', ...
        """
        if not hasattr(self, 'controller') or self.controller is None:
            self.mostrar_feedback("Controlador no disponible para eliminar usuario.", "error")
            return
        if not usuario or not isinstance(usuario, dict) or 'id' not in usuario:
            self.mostrar_feedback("Datos de usuario inválidos para eliminación.", "error")
            return
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Eliminar Usuario: {usuario.get('username','')}")
        dialog.setModal(True)
        dialog.setStyleSheet("QDialog { background: #fff9f3; border-radius: 12px; }")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        # Mensaje de confirmación
        lbl_confirm = QLabel(f"¿Está seguro que desea eliminar el usuario <b>{usuario.get('username','')}</b>? Esta acción no se puede deshacer.")
        lbl_confirm.setAccessibleName("Mensaje de confirmación de eliminación de usuario")
        lbl_confirm.setWordWrap(True)
        layout.addWidget(lbl_confirm)
        # Feedback
        lbl_feedback = QLabel()
        lbl_feedback.setStyleSheet("color: #b91c1c; font-size: 12px;")
        lbl_feedback.setVisible(False)
        layout.addWidget(lbl_feedback)
        # Botones
        btn_eliminar = QPushButton()
        btn_eliminar.setIcon(QIcon("resources/icons/delete.svg"))
        btn_eliminar.setToolTip(eliminar_usuario_text)
        btn_eliminar.setAccessibleName(eliminar_usuario_text)
        estilizar_boton_icono(btn_eliminar)
        estilizar_boton_icono(btn_eliminar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon("resources/icons/close.svg"))
        btn_cancelar.setToolTip(cancelar_tooltip)
        btn_cancelar.setAccessibleName("Cancelar")
        estilizar_boton_icono(btn_cancelar)
        btns = QHBoxLayout()
        btns.addStretch()
        btns.addWidget(btn_eliminar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        # Acción eliminar
        def eliminar():
            try:
                if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'eliminar_usuario'):
                    self.controller.eliminar_usuario(usuario.get('id'))
                    self.mostrar_feedback("Usuario eliminado correctamente.", tipo="exito")
                    dialog.accept()
                    if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'actualizar_tabla_usuarios'):
                        self.controller.actualizar_tabla_usuarios()
                else:
                    self.mostrar_feedback("No se implementó la lógica de eliminar usuario.", tipo="error")
            except Exception as e:
                lbl_feedback.setText(f"Error: {e}")
                lbl_feedback.setVisible(True)
        btn_eliminar.clicked.connect(eliminar)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def actualizar_tabla_usuarios(self):
        """
        Refresca la tabla de usuarios de forma robusta.
        Valida existencia y tipo de tabla, y muestra feedback si no es posible refrescar.
        """
        if not hasattr(self, 'tabla_usuarios') or self.tabla_usuarios is None:
            self.mostrar_feedback("Tabla de usuarios no inicializada.", "error")
            return
        if not (hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'cargar_usuarios')):
            self.mostrar_feedback("Controlador no disponible para cargar usuarios.", "error")
            return
        try:
            self.controller.cargar_usuarios()
        except Exception as e:
            self.mostrar_feedback(f"Error actualizando tabla de usuarios: {e}", "error")

    # Refuerzo defensivo en métodos de menú contextual y columnas
    def mostrar_menu_columnas_header(self, idx):
        from PyQt6.QtCore import QPoint
        header = self.tabla_usuarios.horizontalHeader() if hasattr(self, 'tabla_usuarios') and self.tabla_usuarios and hasattr(self.tabla_usuarios, 'horizontalHeader') else None
        try:
            if header is not None and all(hasattr(header, m) for m in ['sectionPosition', 'mapToGlobal', 'sectionViewportPosition']):
                if idx < 0 or idx >= self.tabla_usuarios.columnCount():
                    self.mostrar_feedback("Índice de columna fuera de rango", "error")
                    return
                global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
                self.mostrar_menu_columnas(global_pos)
            else:
                self.mostrar_feedback("No se puede mostrar el menú de columnas: header no disponible o incompleto", "error")
        except Exception as e:
            self.mostrar_feedback(f"Error al mostrar menú de columnas: {e}", "error")
