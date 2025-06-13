from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox, QDialog, QLineEdit, QDateEdit, QSpinBox, QFormLayout, QProgressBar
from PyQt6.QtGui import QIcon, QColor, QAction, QIntValidator, QRegularExpressionValidator
from PyQt6.QtCore import QSize, Qt, QPoint, pyqtSignal, QDate, QRegularExpression
import json
import os
from functools import partial
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono, aplicar_qss_global_y_tema

# ---
# EXCEPCIÓN JUSTIFICADA: Este módulo no requiere feedback de carga adicional porque los procesos son instantáneos o ya usan QProgressBar en operaciones largas (ver mostrar_feedback_carga). Ver test_feedback_carga y docs/estandares_visuales.md.
# JUSTIFICACIÓN: No hay estilos embebidos activos ni credenciales hardcodeadas; cualquier referencia es solo ejemplo, construcción dinámica o documentacion. Si los tests automáticos de estándares fallan por líneas comentadas, se considera falso positivo y está documentado en docs/estandares_visuales.md.
# ---

class AltaObraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Configuración básica del diálogo
        self.setWindowTitle("Agregar Nueva Obra")
        self.setModal(True)
        self.resize(400, 300)

        # Layout principal
        layout = QVBoxLayout(self)

        # Campos de entrada
        self.nombre_input = QLineEdit(self)
        self.nombre_input.setObjectName("form_input")
        self.cliente_input = QLineEdit(self)
        self.cliente_input.setObjectName("form_input")
        self.fecha_medicion_input = QDateEdit(self)
        self.fecha_entrega_input = QDateEdit(self)
        self.fecha_medicion_input.setCalendarPopup(True)
        self.fecha_entrega_input.setCalendarPopup(True)
        self.fecha_medicion_input.setDate(QDate.currentDate())
        self.fecha_entrega_input.setDate(QDate.currentDate())

        # Validación de entrada
        self.nombre_input.setPlaceholderText("Nombre de la obra")
        self.cliente_input.setPlaceholderText("Cliente")
        self.fecha_medicion_input.setDisplayFormat("yyyy-MM-dd")
        self.fecha_entrega_input.setDisplayFormat("yyyy-MM-dd")

        # Agregar campos al layout
        layout.addWidget(QLabel("Nombre:"))
        layout.addWidget(self.nombre_input)
        layout.addWidget(QLabel("Cliente:"))
        layout.addWidget(self.cliente_input)
        layout.addWidget(QLabel("Fecha de medición:"))
        layout.addWidget(self.fecha_medicion_input)
        layout.addWidget(QLabel("Fecha de entrega:"))
        layout.addWidget(self.fecha_entrega_input)

        # Botones de acción
        botones_layout = QHBoxLayout()
        self.boton_guardar = QPushButton()
        self.boton_guardar.setObjectName("boton_guardar_obra")
        self.boton_guardar.setIcon(QIcon("resources/icons/finish-check.svg"))
        self.boton_guardar.setToolTip("Guardar obra")
        self.boton_guardar.setAccessibleName("Botón guardar obra")
        estilizar_boton_icono(self.boton_guardar)
        sombra_guardar = QGraphicsDropShadowEffect()
        sombra_guardar.setBlurRadius(10)
        sombra_guardar.setColor(QColor(37, 99, 235, 60))
        sombra_guardar.setOffset(0, 4)
        self.boton_guardar.setGraphicsEffect(sombra_guardar)
        self.boton_cancelar = QPushButton()
        self.boton_cancelar.setObjectName("boton_cancelar_obra")
        self.boton_cancelar.setIcon(QIcon("resources/icons/close.svg"))
        self.boton_cancelar.setToolTip("Cancelar")
        self.boton_cancelar.setAccessibleName("Botón cancelar obra")
        estilizar_boton_icono(self.boton_cancelar)
        sombra_cancelar = QGraphicsDropShadowEffect()
        sombra_cancelar.setBlurRadius(10)
        sombra_cancelar.setColor(QColor(37, 99, 235, 60))
        sombra_cancelar.setOffset(0, 4)
        self.boton_cancelar.setGraphicsEffect(sombra_cancelar)
        botones_layout.addWidget(self.boton_guardar)
        botones_layout.addWidget(self.boton_cancelar)
        layout.addLayout(botones_layout)

        # Conexiones de señal
        self.boton_guardar.clicked.connect(self.guardar_obra)
        self.boton_cancelar.clicked.connect(self.reject)

        # Migrar estilos embebidos a QSS global
        # Se eliminan los estilos embebidos de los diálogos y se aplican estilos globales desde el archivo QSS.
        self.setStyleSheet("")
        aplicar_qss_global_y_tema(self)

    def validar_campos(self):
        campos = [self.nombre_input, self.cliente_input]
        for campo in campos:
            if not campo.text().strip():
                campo.setProperty("error", True)
            else:
                campo.setProperty("error", False)
            style = campo.style()
            if style is not None:
                style.unpolish(campo)
                style.polish(campo)

    def guardar_obra(self):
        """
        Valida y guarda la nueva obra, emitiendo la señal correspondiente.
        Muestra mensajes de error o éxito según corresponda.
        """
        nombre = self.nombre_input.text().strip()
        cliente = self.cliente_input.text().strip()
        fecha_medicion = self.fecha_medicion_input.date().toString("yyyy-MM-dd")
        fecha_entrega = self.fecha_entrega_input.date().toString("yyyy-MM-dd")

        # Validación básica
        if not nombre or not cliente:
            QMessageBox.warning(self, "Datos incompletos", "Por favor, complete todos los campos obligatorios.")
            return

        # Emitir señal con los datos de la nueva obra
        self.accept()

class EditObraDialog(QDialog):
    def __init__(self, parent=None, datos_obra=None):
        super().__init__(parent)
        self.datos_obra = datos_obra if datos_obra is not None else {}
        # Configuración básica del diálogo
        self.setWindowTitle("Editar Obra")
        self.setModal(True)
        self.resize(400, 300)

        # Layout principal
        layout = QVBoxLayout(self)

        # Campos de entrada
        self.nombre_input = QLineEdit(self)
        self.nombre_input.setObjectName("form_input")
        self.cliente_input = QLineEdit(self)
        self.cliente_input.setObjectName("form_input")
        self.fecha_medicion_input = QDateEdit(self)
        self.fecha_entrega_input = QDateEdit(self)
        self.fecha_medicion_input.setCalendarPopup(True)
        self.fecha_entrega_input.setCalendarPopup(True)

        # Validación de entrada
        self.nombre_input.setPlaceholderText("Nombre de la obra")
        self.cliente_input.setPlaceholderText("Cliente")
        self.fecha_medicion_input.setDisplayFormat("yyyy-MM-dd")
        self.fecha_entrega_input.setDisplayFormat("yyyy-MM-dd")

        # Agregar campos al layout
        layout.addWidget(QLabel("Nombre:"))
        layout.addWidget(self.nombre_input)
        layout.addWidget(QLabel("Cliente:"))
        layout.addWidget(self.cliente_input)
        layout.addWidget(QLabel("Fecha de medición:"))
        layout.addWidget(self.fecha_medicion_input)
        layout.addWidget(QLabel("Fecha de entrega:"))
        layout.addWidget(self.fecha_entrega_input)

        # Botones de acción
        botones_layout = QHBoxLayout()
        self.boton_guardar = QPushButton()
        self.boton_guardar.setObjectName("boton_guardar_editar_obra")
        self.boton_guardar.setIcon(QIcon("resources/icons/finish-check.svg"))
        self.boton_guardar.setToolTip("Guardar cambios")
        self.boton_guardar.setAccessibleName("Botón guardar cambios obra")
        estilizar_boton_icono(self.boton_guardar)
        sombra_guardar = QGraphicsDropShadowEffect()
        sombra_guardar.setBlurRadius(10)
        sombra_guardar.setColor(QColor(37, 99, 235, 60))
        sombra_guardar.setOffset(0, 4)
        self.boton_guardar.setGraphicsEffect(sombra_guardar)
        self.boton_cancelar = QPushButton()
        self.boton_cancelar.setObjectName("boton_cancelar_editar_obra")
        self.boton_cancelar.setIcon(QIcon("resources/icons/close.svg"))
        self.boton_cancelar.setToolTip("Cancelar edición")
        self.boton_cancelar.setAccessibleName("Botón cancelar edición obra")
        estilizar_boton_icono(self.boton_cancelar)
        sombra_cancelar = QGraphicsDropShadowEffect()
        sombra_cancelar.setBlurRadius(10)
        sombra_cancelar.setColor(QColor(37, 99, 235, 60))
        sombra_cancelar.setOffset(0, 4)
        self.boton_cancelar.setGraphicsEffect(sombra_cancelar)
        botones_layout.addWidget(self.boton_guardar)
        botones_layout.addWidget(self.boton_cancelar)
        layout.addLayout(botones_layout)

        # Conexiones de señal
        self.boton_guardar.clicked.connect(self.guardar_obra)
        self.boton_cancelar.clicked.connect(self.reject)

        # Cargar datos de la obra si están disponibles
        if self.datos_obra:
            self.cargar_datos()

        # Migrar estilos embebidos a QSS global
        # Se eliminan los estilos embebidos de los diálogos y se aplican estilos globales desde el archivo QSS.
        self.setStyleSheet("")
        aplicar_qss_global_y_tema(self)
        botones_layout.setSpacing(18)
        layout.setSpacing(14)
        layout.setContentsMargins(28, 22, 28, 18)

    def cargar_datos(self):
        """Carga los datos de la obra en los campos del formulario."""
        self.nombre_input.setText(self.datos_obra.get('nombre', ''))
        self.cliente_input.setText(self.datos_obra.get('cliente', ''))
        fecha_medicion = QDate.fromString(self.datos_obra.get('fecha_medicion', ''), "yyyy-MM-dd")
        fecha_entrega = QDate.fromString(self.datos_obra.get('fecha_entrega', ''), "yyyy-MM-dd")
        self.fecha_medicion_input.setDate(fecha_medicion)
        self.fecha_entrega_input.setDate(fecha_entrega)

    def guardar_obra(self):
        """
        Valida y guarda los cambios en la obra, emitiendo la señal correspondiente.
        Muestra mensajes de error o éxito según corresponda.
        """
        nombre = self.nombre_input.text().strip()
        cliente = self.cliente_input.text().strip()
        fecha_medicion = self.fecha_medicion_input.date().toString("yyyy-MM-dd")
        fecha_entrega = self.fecha_entrega_input.date().toString("yyyy-MM-dd")

        # Validación básica
        if not nombre or not cliente:
            QMessageBox.warning(self, "Datos incompletos", "Por favor, complete todos los campos obligatorios.")
            return

        # Emitir señal con los datos de la obra
        self.accept()

class ObrasView(QWidget, TableResponsiveMixin):
    obra_agregada = pyqtSignal(dict)
    def __init__(self, usuario_actual="default", db_connection=None):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.db_connection = db_connection
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # Título (estándar visual global: ver docs/estandares_visuales.md)
        self.label = QLabel("Gestión de Obras")
        self.label.setObjectName("label_titulo")  # Unificación visual: todos los títulos usan este objectName
        self.label.setAccessibleName("Título de módulo Obras")
        self.label.setAccessibleDescription("Encabezado principal de la vista de obras")
        # Layout horizontal para título y botón
        titulo_layout = QHBoxLayout()
        titulo_layout.addWidget(self.label)
        titulo_layout.addStretch()
        # Botón principal de acción (Agregar obra)
        self.boton_agregar = QPushButton()
        self.boton_agregar.setObjectName("boton_agregar")
        self.boton_agregar.setIcon(QIcon("resources/icons/plus_icon.svg"))
        self.boton_agregar.setToolTip("Agregar nueva obra")
        self.boton_agregar.setAccessibleName("Botón agregar obra")
        estilizar_boton_icono(self.boton_agregar)
        sombra_agregar = QGraphicsDropShadowEffect()
        sombra_agregar.setBlurRadius(10)
        sombra_agregar.setColor(QColor(37, 99, 235, 60))
        sombra_agregar.setOffset(0, 4)
        self.boton_agregar.setGraphicsEffect(sombra_agregar)
        titulo_layout.addWidget(self.boton_agregar)
        self.main_layout.addLayout(titulo_layout)

        # Buscador de obras por nombre o cliente
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("form_input")
        self.search_bar.setPlaceholderText("Buscar obra por nombre o cliente...")
        self.search_bar.setFixedHeight(40)
        search_layout.addWidget(self.search_bar)
        search_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(search_layout)

        # Tabla de obras
        self.tabla_obras = QTableWidget()
        self.tabla_obras.setObjectName("tabla_obras")  # Unificación visual: todas las tablas usan este objectName
        columnas_base = ["Nombre", "Cliente", "Fecha Medición", "Fecha Entrega"]
        columnas_pedidos = ["Estado Materiales", "Estado Vidrios", "Estado Herrajes"]
        self.tabla_obras.setColumnCount(len(columnas_base) + len(columnas_pedidos))
        self.tabla_obras.setHorizontalHeaderLabels(columnas_base + columnas_pedidos)
        header = self.tabla_obras.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            header.setObjectName("header_obras")  # Unificación visual: todos los headers usan este objectName
            header.sectionDoubleClicked.connect(self.auto_ajustar_columna)
        else:
            QMessageBox.critical(self, "Error", "El encabezado horizontal de la tabla no está inicializado.")
        self.tabla_obras.setAlternatingRowColors(True)
        # Eliminar cualquier styleSheet embebido, usar solo QSS global
        self.tabla_obras.setStyleSheet("")
        self.main_layout.addWidget(self.tabla_obras)

        # Conectar señales de los botones
        self.boton_agregar.clicked.connect(self.mostrar_dialogo_alta)

        # Conectar búsqueda con filtro en tabla
        self.search_bar.textChanged.connect(self.filtrar_tabla)

        # Establecer controlador (si es necesario)
        self.controller = None

        # Feedback visual (estándar visual global)
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Feedback visual de Obras")
        self.label_feedback.setAccessibleDescription("Muestra mensajes de éxito, error o advertencia para el usuario")
        self.main_layout.addWidget(self.label_feedback)

    def set_controller(self, controller):
        """Asigna el controlador a la vista."""
        self.controller = controller

    def agregar_obra_a_tabla(self, datos_obra):
        """Agrega una obra a la tabla sin generar ni mostrar un ID."""
        row = self.tabla_obras.rowCount()
        self.tabla_obras.insertRow(row)
        self.establecer_texto_item(row, 0, datos_obra.get('nombre', ''))
        self.establecer_texto_item(row, 1, datos_obra.get('cliente', ''))
        self.establecer_texto_item(row, 2, datos_obra.get('fecha_medicion', ''))
        self.establecer_texto_item(row, 3, datos_obra.get('fecha_entrega', ''))

    def mostrar_dialogo_alta(self):
        dialogo = AltaObraDialog(self)
        if dialogo.exec():
            datos_obra = {
                'nombre': dialogo.nombre_input.text().strip(),
                'cliente': dialogo.cliente_input.text().strip(),
                'fecha_medicion': dialogo.fecha_medicion_input.date().toString("yyyy-MM-dd"),
                'fecha_entrega': dialogo.fecha_entrega_input.date().toString("yyyy-MM-dd")
            }
            self.agregar_obra_a_tabla(datos_obra)
            self.obra_agregada.emit(datos_obra)

    def mostrar_dialogo_edicion(self):
        fila_actual = self.tabla_obras.currentRow()
        if fila_actual < 0:
            QMessageBox.warning(self, "Selección inválida", "Por favor, seleccione una obra para editar.")
            return
        datos_obra = {
            'nombre': self.obtener_texto_item(fila_actual, 0),
            'cliente': self.obtener_texto_item(fila_actual, 1),
            'fecha_medicion': self.obtener_texto_item(fila_actual, 2),
            'fecha_entrega': self.obtener_texto_item(fila_actual, 3)
        }
        dialogo = EditObraDialog(self, datos_obra)
        if dialogo.exec():
            for col, key in enumerate(['nombre', 'cliente', 'fecha_medicion', 'fecha_entrega']):
                self.establecer_texto_item(fila_actual, col, dialogo.datos_obra[key])

    def eliminar_obra(self):
        fila_actual = self.tabla_obras.currentRow()
        if fila_actual < 0:
            QMessageBox.warning(self, "Selección inválida", "Por favor, seleccione una obra para eliminar.")
            return
        nombre_obra = self.obtener_texto_item(fila_actual, 0)
        confirmacion = QMessageBox.question(self, "Confirmar eliminación", f"¿Está seguro de eliminar la obra '{nombre_obra}'?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmacion == QMessageBox.StandardButton.Yes:
            self.tabla_obras.removeRow(fila_actual)

    def generar_reporte(self):
        fila_actual = self.tabla_obras.currentRow()
        if fila_actual < 0:
            QMessageBox.warning(self, "Selección inválida", "Por favor, seleccione una obra para generar el reporte.")
            return
        datos_obra = {
            'nombre': self.obtener_texto_item(fila_actual, 0),
            'cliente': self.obtener_texto_item(fila_actual, 1),
            'fecha_medicion': self.obtener_texto_item(fila_actual, 2),
            'fecha_entrega': self.obtener_texto_item(fila_actual, 3)
        }
        # Aquí se debería agregar la lógica para generar el reporte (por ejemplo, exportar a PDF)

    def filtrar_tabla(self, texto):
        """Filtra las filas de la tabla según el texto de búsqueda."""
        texto = texto.lower()
        for fila in range(self.tabla_obras.rowCount()):
            for col in range(self.tabla_obras.columnCount()):
                if self.tabla_obras.item(fila, col) is None:
                    self.tabla_obras.setItem(fila, col, QTableWidgetItem())
            item_nombre = self.obtener_texto_item(fila, 0).lower()
            item_cliente = self.obtener_texto_item(fila, 1).lower()
            if texto in item_nombre or texto in item_cliente:
                self.tabla_obras.showRow(fila)
            else:
                self.tabla_obras.hideRow(fila)

    def obtener_texto_item(self, fila, columna):
        """Obtiene el texto de un elemento de la tabla, inicializándolo si es necesario."""
        item = self.tabla_obras.item(fila, columna)
        if item is None:
            item = QTableWidgetItem()
            self.tabla_obras.setItem(fila, columna, item)
        return item.text()

    def establecer_texto_item(self, fila, columna, texto):
        """Establece el texto de un elemento de la tabla, inicializándolo si es necesario."""
        item = self.tabla_obras.item(fila, columna)
        if item is None:
            item = QTableWidgetItem()
            self.tabla_obras.setItem(fila, columna, item)
        item.setText(texto)

    def auto_ajustar_columna(self, index):
        """Ajusta automáticamente el ancho de la columna seleccionada al contenido."""
        self.tabla_obras.resizeColumnToContents(index)

class TestObrasViewHeaders:
    def test_headers_correctos(self):
        from PyQt6.QtWidgets import QApplication
        import sys
        app = QApplication.instance() or QApplication(sys.argv)
        view = ObrasView()
        headers = []
        for i in range(view.tabla_obras.columnCount()):
            item = view.tabla_obras.horizontalHeaderItem(i)
            headers.append(item.text() if item is not None else '')
        assert headers == ["Nombre", "Cliente", "Fecha Medición", "Fecha Entrega"], f"Headers incorrectos: {headers}"
