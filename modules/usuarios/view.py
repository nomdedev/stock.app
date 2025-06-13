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
        # Conexión para refresco automático al cambiar de pestaña
        if hasattr(self, 'tabs') and self.tabs is not None:
            self.tabs.currentChanged.connect(self._on_tab_changed)

        # --- Header visual: título y barra de botones alineados ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Gestión de Usuarios")
        self.label_titulo.setObjectName("label_titulo_usuarios")  # Para QSS global
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        # Botón principal (Agregar usuario)
        self.boton_agregar = QPushButton()
        self.boton_agregar.setObjectName("boton_agregar_usuarios")  # Para QSS global
        self.boton_agregar.setIcon(QIcon("resources/icons/agregar-user.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar usuario")
        header_layout.addWidget(self.boton_agregar)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)
        self.main_layout.addSpacing(8)

        # --- FEEDBACK VISUAL CENTRALIZADO Y QSS GLOBAL ---
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")  # Para QSS global
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Mensaje de feedback de usuarios")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario")
        self.main_layout.addWidget(self.label_feedback)
        self._feedback_timer = None

        # Refuerzo de accesibilidad en botón principal
        if hasattr(self, 'boton_agregar') and self.boton_agregar:
            self.boton_agregar.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            font = self.boton_agregar.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            self.boton_agregar.setFont(font)

        # Refuerzo de accesibilidad en tabla principal
        if hasattr(self, 'tabla_usuarios') and self.tabla_usuarios:
            self.tabla_usuarios.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.tabla_usuarios.setObjectName("tabla_usuarios")

        # Refuerzo de accesibilidad en todos los QComboBox de la vista principal
        for widget in self.findChildren(QComboBox):
            if widget:
                widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                font = widget.font()
                if font.pointSize() < 12:
                    font.setPointSize(12)
                widget.setFont(font)
                if not widget.toolTip():
                    widget.setToolTip("Selector de usuario")
                if not widget.accessibleName():
                    widget.setAccessibleName("Selector de usuario para permisos")

        # Aplicar QSS global y tema visual (solo desde resources/qss/)
        try:
            from utils.theme_manager import cargar_modo_tema
            tema = cargar_modo_tema()
            qss_tema = f"resources/qss/theme_{tema}.qss"
            aplicar_qss_global_y_tema(self, qss_global_path="resources/qss/theme_light.qss", qss_tema_path=qss_tema)
        except Exception as e:
            print(f"Error aplicando QSS global: {e}")

        if hasattr(self, 'actualizar_tabla_usuarios'):
            self.actualizar_tabla_usuarios()

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
        if hasattr(self, 'tabs') and self.tabs is not None:
            # Refrescar tabla de usuarios
            if hasattr(self, 'tab_usuarios') and self.tabs.currentWidget() == self.tab_usuarios:
                if hasattr(self, 'actualizar_tabla_usuarios'):
                    self.actualizar_tabla_usuarios()
            # Refrescar tabla de permisos
            elif hasattr(self, 'tab_permisos') and self.tabs.currentWidget() == self.tab_permisos:
                if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'cargar_permisos_modulos'):
                    self.controller.cargar_permisos_modulos()
            # Refrescar resumen de permisos
            elif hasattr(self, 'tab_resumen_permisos') and self.tabs.currentWidget() == self.tab_resumen_permisos:
                if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'cargar_resumen_permisos'):
                    self.controller.cargar_resumen_permisos()

    def _init_tab_usuarios(self):
        tab_usuarios_layout = QVBoxLayout(self.tab_usuarios)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setObjectName("boton_agregar_usuarios")
        self.boton_agregar.setIcon(QIcon("resources/icons/agregar-user.svg"))
        self.boton_agregar.setIconSize(QSize(20, 20))
        self.boton_agregar.setToolTip("Agregar usuario")
        self.boton_agregar.setText("")
        estilizar_boton_icono(self.boton_agregar)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        tab_usuarios_layout.addLayout(botones_layout)
        # Tabla de usuarios
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setObjectName("tabla_usuarios")
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
        tab_permisos_layout.addWidget(self.combo_usuario)
        self.tabla_permisos_modulos = QTableWidget()
        self.make_table_responsive(self.tabla_permisos_modulos)
        tab_permisos_layout.addWidget(self.tabla_permisos_modulos)
        self.boton_guardar_permisos = QPushButton("Guardar permisos")
        self.boton_guardar_permisos.setIcon(QIcon("resources/icons/guardar.svg"))
        self.boton_guardar_permisos.setIconSize(QSize(20, 20))
        estilizar_boton_icono(self.boton_guardar_permisos)
        self.boton_refrescar_resumen = QPushButton("Refrescar resumen de permisos")
        self.boton_refrescar_resumen.setIcon(QIcon("resources/icons/actualizar.svg"))
        self.boton_refrescar_resumen.setIconSize(QSize(20, 20))
        estilizar_boton_icono(self.boton_refrescar_resumen)
        tab_permisos_layout.addWidget(self.boton_guardar_permisos)
        tab_permisos_layout.addWidget(self.boton_refrescar_resumen)

    def _init_tab_resumen_permisos(self):
        layout = QVBoxLayout(self.tab_resumen_permisos)
        self.boton_refrescar_resumen = QPushButton("Refrescar resumen de permisos")
        self.boton_refrescar_resumen.setObjectName("boton_refrescar_resumen_permisos")
        self.boton_refrescar_resumen.setIcon(QIcon("resources/icons/refresh-cw.svg"))
        self.boton_refrescar_resumen.setIconSize(QSize(20, 20))
        estilizar_boton_icono(self.boton_refrescar_resumen)
        layout.addWidget(self.boton_refrescar_resumen)
        self.tabla_resumen_permisos = QTableWidget()
        self.tabla_resumen_permisos.setObjectName("tabla_resumen_permisos")
        self.make_table_responsive(self.tabla_resumen_permisos)
        layout.addWidget(self.tabla_resumen_permisos)
        self.label_resumen_info = QLabel("Visualización de permisos por usuario y módulo. Solo lectura.")
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
        if not hasattr(self, 'tabla_usuarios') or self.tabla_usuarios is None:
            self.mostrar_feedback("Tabla de usuarios no disponible para menú de columnas.", "error")
            return
        if not hasattr(self, 'usuarios_headers') or not self.usuarios_headers:
            self.mostrar_feedback("Headers de usuarios no definidos.", "error")
            return
        # Reparar desincronización si la hay
        headers_set = set(self.usuarios_headers)
        visibles_set = set(self.columnas_visibles.keys())
        if headers_set != visibles_set:
            self.mostrar_feedback("Detectada desincronización de columnas. Reparando...", "advertencia")
            for h in headers_set - visibles_set:
                self.columnas_visibles[h] = True
            for h in visibles_set - headers_set:
                del self.columnas_visibles[h]
            self.guardar_config_columnas()
        # Si después de reparar no hay headers válidos, no mostrar menú
        if not self.usuarios_headers:
            self.mostrar_feedback("No hay columnas configurables para mostrar en el menú.", "error")
            return
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
        if not any_action:
            self.mostrar_feedback("No hay columnas configurables para mostrar en el menú.", "error")
            return
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
        if row != -1 and hasattr(self.tabla_usuarios, 'item'):
            item = self.tabla_usuarios.item(row, 0)
            if item is not None and hasattr(item, 'text'):
                codigo = item.text()  # Usar el primer campo como dato QR
                try:
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
                except Exception as e:
                    self.mostrar_feedback(f"Error generando QR: {e}", "error")

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
            usuario_id = usuario['id'] if isinstance(usuario, dict) and 'id' in usuario else usuario[0] if isinstance(usuario, (list, tuple)) and len(usuario) > 0 else None
            usuario_nombre = usuario['usuario'] if isinstance(usuario, dict) and 'usuario' in usuario else usuario[4] if isinstance(usuario, (list, tuple)) and len(usuario) > 4 else str(usuario_id)
            rol = usuario['rol'] if isinstance(usuario, dict) and 'rol' in usuario else usuario[6] if isinstance(usuario, (list, tuple)) and len(usuario) > 6 else ''
            for modulo in modulos:
                permisos = permisos_dict.get((usuario_id, modulo), {'ver': False, 'modificar': False, 'aprobar': False})
                self.tabla_resumen_permisos.insertRow(rows)
                self.tabla_resumen_permisos.setItem(rows, 0, QTableWidgetItem(str(usuario_nombre)))
                self.tabla_resumen_permisos.setItem(rows, 1, QTableWidgetItem(str(rol)))
                self.tabla_resumen_permisos.setItem(rows, 2, QTableWidgetItem(str(modulo)))
                for i, key in enumerate(['ver', 'modificar', 'aprobar']):
                    item = QTableWidgetItem("✅" if permisos.get(key, False) else "❌")
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.tabla_resumen_permisos.setItem(rows, 3 + i, item)
                rows += 1
        self.tabla_resumen_permisos.resizeColumnsToContents()

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
        dialog.setModal(True)
        dialog.setStyleSheet("QDialog { background: #fff9f3; border-radius: 12px; }")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)
        # --- Username ---
        username_input = QLineEdit()
        username_input.setObjectName("form_input")
        username_input.setPlaceholderText("Nombre de usuario")
        username_input.setToolTip("Ingrese el nombre de usuario")
        username_input.setAccessibleName("Nombre de usuario")
        form.addRow("Usuario:", username_input)
        # --- Contraseña ---
        password_input = QLineEdit()
        password_input.setObjectName("form_input")
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_input.setPlaceholderText("Contraseña fuerte")
        password_input.setToolTip("Ingrese una contraseña fuerte (mín. 8 caracteres, mayúscula, minúscula, número y símbolo)")
        password_input.setAccessibleName("Contraseña")
        form.addRow("Contraseña:", password_input)
        # --- Rol ---
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
        # --- Permisos (checkboxes por módulo) ---
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
        form.addRow("Permisos:", permisos_layout)
        # --- Feedback campo ---
        lbl_feedback = QLabel()
        lbl_feedback.setStyleSheet("color: #b91c1c; font-size: 12px;")
        lbl_feedback.setVisible(False)
        form.addRow("", lbl_feedback)
        layout.addLayout(form)
        # --- Botones ---
        btns = QHBoxLayout()
        btn_guardar = QPushButton()
        btn_guardar.setIcon(QIcon("resources/icons/finish-check.svg"))
        btn_guardar.setToolTip("Crear usuario")
        btn_guardar.setAccessibleName("Crear usuario")
        estilizar_boton_icono(btn_guardar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon("resources/icons/close.svg"))
        btn_cancelar.setToolTip("Cancelar y cerrar ventana")
        btn_cancelar.setAccessibleName("Cancelar")
        estilizar_boton_icono(btn_cancelar)
        btns.addStretch()
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        # --- Validación de contraseña fuerte ---
        import re
        def es_contrasena_fuerte(pw):
            return (
                len(pw) >= 8 and
                re.search(r"[A-Z]", pw) and
                re.search(r"[a-z]", pw) and
                re.search(r"[0-9]", pw) and
                re.search(r"[^A-Za-z0-9]", pw)
            )
        # --- Acción guardar ---
        def guardar():
            username = username_input.text().strip()
            password = password_input.text()
            rol = combo_rol.currentText()
            permisos_seleccionados = [cb.text() for cb in checkboxes if cb.isChecked()]
            if not username or not password or not rol:
                lbl_feedback.setText("Complete todos los campos obligatorios.")
                lbl_feedback.setVisible(True)
                return
            if not es_contrasena_fuerte(password):
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
        btn_guardar.clicked.connect(guardar)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

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
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QHBoxLayout, QLabel, QCheckBox
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Editar Usuario: {usuario.get('username','')}")
        dialog.setModal(True)
        dialog.setStyleSheet("QDialog { background: #fff9f3; border-radius: 12px; }")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)
        # --- Username (readonly) ---
        username_input = QLineEdit(usuario.get('username',''))
        username_input.setObjectName("form_input")
        username_input.setReadOnly(True)
        username_input.setToolTip("Nombre de usuario (no editable)")
        username_input.setAccessibleName("Nombre de usuario")
        form.addRow("Usuario:", username_input)
        # --- Contraseña (opcional, solo si se desea cambiar) ---
        password_input = QLineEdit()
        password_input.setObjectName("form_input")
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_input.setPlaceholderText("Nueva contraseña (opcional)")
        password_input.setToolTip("Ingrese una nueva contraseña fuerte si desea cambiarla")
        password_input.setAccessibleName("Contraseña")
        form.addRow("Contraseña:", password_input)
        # --- Rol ---
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
        # --- Permisos (checkboxes por módulo) ---
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
        form.addRow("Permisos:", permisos_layout)
        # --- Feedback campo ---
        lbl_feedback = QLabel()
        lbl_feedback.setStyleSheet("color: #b91c1c; font-size: 12px;")
        lbl_feedback.setVisible(False)
        form.addRow("", lbl_feedback)
        layout.addLayout(form)
        # --- Botones ---
        btns = QHBoxLayout()
        btn_guardar = QPushButton()
        btn_guardar.setIcon(QIcon("resources/icons/finish-check.svg"))
        btn_guardar.setToolTip("Guardar cambios")
        btn_guardar.setAccessibleName("Guardar cambios")
        estilizar_boton_icono(btn_guardar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon("resources/icons/close.svg"))
        btn_cancelar.setToolTip("Cancelar y cerrar ventana")
        btn_cancelar.setAccessibleName("Cancelar")
        estilizar_boton_icono(btn_cancelar)
        btns.addStretch()
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        # --- Validación de contraseña fuerte (si se cambia) ---
        import re
        def es_contrasena_fuerte(pw):
            return (
                len(pw) >= 8 and
                re.search(r"[A-Z]", pw) and
                re.search(r"[a-z]", pw) and
                re.search(r"[0-9]", pw) and
                re.search(r"[^A-Za-z0-9]", pw)
            )
        # --- Acción guardar ---
        def guardar():
            rol = combo_rol.currentText()
            permisos_seleccionados = [cb.text() for cb in checkboxes if cb.isChecked()]
            nueva_contrasena = password_input.text()
            if not rol:
                lbl_feedback.setText("Seleccione un rol.")
                lbl_feedback.setVisible(True)
                return
            if nueva_contrasena and not es_contrasena_fuerte(nueva_contrasena):
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
        btn_guardar.clicked.connect(guardar)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def abrir_dialogo_editar_permisos(self, usuario):
        """
        Abre un diálogo modal robusto para editar los permisos de un usuario.
        Cumple checklist: validación visual/backend, feedback, accesibilidad, tooltips, cierre solo en éxito.
        usuario: dict con claves 'username', 'rol', 'permisos' (lista de str)
        """
        if not hasattr(self, 'controller') or self.controller is None:
            self.mostrar_feedback("Controlador no disponible para editar permisos.", "error")
            return
        if not usuario or not isinstance(usuario, dict):
            self.mostrar_feedback("Datos de usuario inválidos para edición de permisos.", "error")
            return
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLabel, QCheckBox, QPushButton, QHBoxLayout
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Editar Permisos: {usuario.get('username','')}")
        dialog.setModal(True)
        dialog.setStyleSheet("QDialog { background: #fff9f3; border-radius: 12px; }")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)
        # --- Usuario (readonly) ---
        lbl_usuario = QLabel(usuario.get('username',''))
        lbl_usuario.setToolTip("Usuario al que se le asignan permisos")
        lbl_usuario.setAccessibleName("Usuario")
        form.addRow("Usuario:", lbl_usuario)
        # --- Permisos (checkboxes por módulo) ---
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
        form.addRow("Permisos:", permisos_layout)
        # --- Feedback campo ---
        lbl_feedback = QLabel()
        lbl_feedback.setStyleSheet("color: #b91c1c; font-size: 12px;")
        lbl_feedback.setVisible(False)
        form.addRow("", lbl_feedback)
        layout.addLayout(form)
        # --- Botones ---
        btns = QHBoxLayout()
        btn_guardar = QPushButton()
        btn_guardar.setIcon(QIcon("resources/icons/finish-check.svg"))
        btn_guardar.setToolTip("Guardar permisos")
        btn_guardar.setAccessibleName("Guardar permisos")
        estilizar_boton_icono(btn_guardar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon("resources/icons/close.svg"))
        btn_cancelar.setToolTip("Cancelar y cerrar ventana")
        btn_cancelar.setAccessibleName("Cancelar")
        estilizar_boton_icono(btn_cancelar)
        btns.addStretch()
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        # --- Acción guardar ---
        def guardar():
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
        btn_guardar.clicked.connect(guardar)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

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
        btns = QHBoxLayout()
        btn_eliminar = QPushButton()
        btn_eliminar.setIcon(QIcon("resources/icons/delete.svg"))
        btn_eliminar.setToolTip("Eliminar usuario")
        btn_eliminar.setAccessibleName("Eliminar usuario")
        estilizar_boton_icono(btn_eliminar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon("resources/icons/close.svg"))
        btn_cancelar.setToolTip("Cancelar y cerrar ventana")
        btn_cancelar.setAccessibleName("Cancelar")
        estilizar_boton_icono(btn_cancelar)
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
                pos = header.sectionPosition(idx)
                global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
                self.mostrar_menu_columnas(global_pos)
            else:
                self.mostrar_feedback("No se puede mostrar el menú de columnas: header no disponible o incompleto", "error")
        except Exception as e:
            self.mostrar_feedback(f"Error al mostrar menú de columnas: {e}", "error")
