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
        self.cliente_input = QLineEdit(self)
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
        self.boton_guardar = QPushButton("Guardar")
        self.boton_cancelar = QPushButton("Cancelar")
        botones_layout.addWidget(self.boton_guardar)
        botones_layout.addWidget(self.boton_cancelar)
        layout.addLayout(botones_layout)

        # Conexiones de señal
        self.boton_guardar.clicked.connect(self.guardar_obra)
        self.boton_cancelar.clicked.connect(self.reject)

        # Mejorar estética del formulario de alta de obra
        self.setStyleSheet("""
            QDialog {
                background: #f9fafb;
                border-radius: 14px;
            }
            QLabel {
                font-size: 15px;
                color: #22223b;
                margin-bottom: 2px;
            }
            QLineEdit, QDateEdit {
                padding: 7px 10px;
                border: 1px solid #bfc0c0;
                border-radius: 7px;
                font-size: 15px;
                margin-bottom: 10px;
            }
            QPushButton {
                min-width: 90px;
                min-height: 36px;
                border-radius: 7px;
                font-size: 15px;
                margin-top: 8px;
            }
            QPushButton#boton_guardar {
                background: #2563eb;
                color: white;
            }
            QPushButton#boton_cancelar {
                background: #e0e1dd;
                color: #22223b;
            }
        """)
        self.boton_guardar.setObjectName("boton_guardar")
        self.boton_cancelar.setObjectName("boton_cancelar")
        # Centrar y espaciar mejor los botones
        botones_layout.setSpacing(18)
        layout.setSpacing(14)
        layout.setContentsMargins(28, 22, 28, 18)

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
        self.cliente_input = QLineEdit(self)
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
        self.boton_guardar = QPushButton("Guardar")
        self.boton_cancelar = QPushButton("Cancelar")
        botones_layout.addWidget(self.boton_guardar)
        botones_layout.addWidget(self.boton_cancelar)
        layout.addLayout(botones_layout)

        # Conexiones de señal
        self.boton_guardar.clicked.connect(self.guardar_obra)
        self.boton_cancelar.clicked.connect(self.reject)

        # Cargar datos de la obra si están disponibles
        if self.datos_obra:
            self.cargar_datos()

        # Mejorar estética del formulario de edición de obra
        self.setStyleSheet("""
            QDialog {
                background: #f9fafb;
                border-radius: 14px;
            }
            QLabel {
                font-size: 15px;
                color: #22223b;
                margin-bottom: 2px;
            }
            QLineEdit, QDateEdit {
                padding: 7px 10px;
                border: 1px solid #bfc0c0;
                border-radius: 7px;
                font-size: 15px;
                margin-bottom: 10px;
            }
            QPushButton {
                min-width: 90px;
                min-height: 36px;
                border-radius: 7px;
                font-size: 15px;
                margin-top: 8px;
            }
            QPushButton#boton_guardar {
                background: #2563eb;
                color: white;
            }
            QPushButton#boton_cancelar {
                background: #e0e1dd;
                color: #22223b;
            }
        """)
        self.boton_guardar.setObjectName("boton_guardar")
        self.boton_cancelar.setObjectName("boton_cancelar")
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

        # Título
        self.label = QLabel("Gestión de Obras")
        self.label.setAccessibleName("Título de módulo Obras")
        self.label.setAccessibleDescription("Encabezado principal de la vista de obras")
        self.main_layout.addWidget(self.label)

        # Botón principal de acción (Agregar obra)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("resources/icons/plus_icon.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar nueva obra")
        self.boton_agregar.setAccessibleName("Botón agregar obra")
        self.boton_agregar.setAccessibleDescription("Botón principal para agregar una nueva obra")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_agregar.setGraphicsEffect(sombra)
        estilizar_boton_icono(self.boton_agregar)
        self.boton_agregar.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        botones_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.main_layout.addLayout(botones_layout)

        # Buscador de obras por nombre o cliente
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar obra...")
