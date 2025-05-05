from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, 
    QPushButton, QStackedWidget, QMessageBox
)
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from utils.icon_loader import get_icon
from functools import partial
import ctypes
import sys, os

# Configurar el path para importar módulos locales
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importar utilidades principales
from core.logger import Logger
from core.database import DatabaseConnection, InventarioDatabaseConnection

# Importar vistas
from modules.inventario.view import InventarioView
from modules.obras.view import ObrasView
from modules.produccion.view import ProduccionView
from modules.logistica.view import LogisticaView
from modules.pedidos.view import PedidosView
from modules.usuarios.view import UsuariosView
from modules.auditoria.view import AuditoriaView
from modules.configuracion.view import ConfiguracionView

# Importar controladores
from modules.inventario.controller import InventarioController
from modules.obras.controller import ObrasController
from modules.produccion.controller import ProduccionController
from modules.logistica.controller import LogisticaController
from modules.pedidos.controller import PedidosController
from modules.usuarios.controller import UsuariosController
from modules.auditoria.controller import AuditoriaController
from modules.configuracion.controller import ConfiguracionController

# Importar modelos
from modules.inventario.model import InventarioModel
from modules.obras.model import ObrasModel
from modules.produccion.model import ProduccionModel
from modules.logistica.model import LogisticaModel
from modules.pedidos.model import PedidosModel
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from modules.configuracion.model import ConfiguracionModel

# Clase principal
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = Logger()  # Inicializar el logger
        self.logger.info("Aplicación iniciada")
        self.setWindowTitle("MPS Inventario App")

        # Configurar tamaño inicial de la ventana
        self.resize(1280, 720)  # Tamaño inicial razonable
        self.setMinimumSize(1024, 600)  # Tamaño mínimo para evitar errores

        # Aplicar estilo global para tablas con encabezados azul crema y letras en negrita
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e3a8a; /* Azul oscuro */
                color: #FFFFFF; /* Texto blanco */
            }
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: #FFFFFF; /* Texto blanco */
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #14274e; /* Azul aún más oscuro */
            }
            QLabel {
                color: #d1d5db; /* Texto gris claro */
            }
            QFrame {
                border: 1px solid #14274e; /* Bordes azul más oscuro */
            }
            QTableWidget {
                background-color: #f0f0f0; /* Gris claro */
                color: #000000; /* Texto negro */
                border: 1px solid #000000; /* Bordes negros */
                font-size: 12px;
                gridline-color: #000000; /* Color de las líneas de la cuadrícula */
            }
            QTableWidget::item {
                background-color: #f0f0f0; /* Gris claro */
            }
            QTableWidget::item:selected {
                background-color: #d1d5db; /* Gris más oscuro */
                color: #000000; /* Texto negro */
            }
            QHeaderView::section {
                background-color: #dbeafe; /* Azul crema */
                color: #000000; /* Texto negro */
                font-weight: bold; /* Letras en negrita */
                border: 1px solid #000000; /* Bordes negros */
            }
        """)

        self.initUI()

    def initUI(self):
        # Crear conexiones persistentes a las bases de datos
        self.db_connection_inventario = DatabaseConnection()
        self.db_connection_inventario.conectar_a_base("inventario")

        self.db_connection_usuarios = DatabaseConnection()
        self.db_connection_usuarios.conectar_a_base("users")

        self.db_connection_auditoria = DatabaseConnection()
        self.db_connection_auditoria.conectar_a_base("auditoria")

        # Crear instancias de modelos con la conexión correspondiente
        self.inventario_model = InventarioModel(db_connection=self.db_connection_inventario)
        self.obras_model = ObrasModel(db_connection=self.db_connection_inventario)
        self.produccion_model = ProduccionModel(db_connection=self.db_connection_inventario)
        self.logistica_model = LogisticaModel(db_connection=self.db_connection_inventario)
        self.pedidos_model = PedidosModel(db_connection=self.db_connection_inventario)
        self.usuarios_model = UsuariosModel(db_connection=self.db_connection_usuarios)
        self.auditoria_model = AuditoriaModel(db_connection=self.db_connection_auditoria)
        self.configuracion_model = ConfiguracionModel(db_connection=self.db_connection_inventario)

        # Crear instancias de vistas y controladores
        self.inventario_view = InventarioView()
        self.inventario_controller = InventarioController(
            model=self.inventario_model, view=self.inventario_view
        )

        self.obras_view = ObrasView()
        self.obras_controller = ObrasController(
            model=self.obras_model, view=self.obras_view
        )

        self.produccion_view = ProduccionView()
        self.produccion_controller = ProduccionController(
            model=self.produccion_model, view=self.produccion_view
        )

        self.logistica_view = LogisticaView()
        self.logistica_controller = LogisticaController(
            model=self.logistica_model, view=self.logistica_view
        )

        self.pedidos_view = PedidosView()
        self.pedidos_controller = PedidosController(
            model=self.pedidos_model, view=self.pedidos_view, db_connection=self.db_connection_inventario
        )

        # Crear instancias de controladores antes de las vistas
        self.usuarios_controller = UsuariosController(
            model=self.usuarios_model, view=None
        )
        self.usuarios_view = UsuariosView(controller=self.usuarios_controller)
        self.usuarios_controller.view = self.usuarios_view

        self.auditoria_view = AuditoriaView()
        self.auditoria_controller = AuditoriaController(
            model=self.auditoria_model, view=self.auditoria_view
        )

        self.configuracion_view = ConfiguracionView()
        self.configuracion_controller = ConfiguracionController(
            model=self.configuracion_model, view=self.configuracion_view
        )

        # Layout principal
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Crear QStackedWidget para la navegación entre secciones
        self.module_stack = QStackedWidget()
        self.module_stack.addWidget(self.inventario_view)   # index 0
        self.module_stack.addWidget(self.obras_view)        # index 1
        self.module_stack.addWidget(self.produccion_view)   # index 2
        self.module_stack.addWidget(self.logistica_view)    # index 3
        self.module_stack.addWidget(self.pedidos_view)      # index 4
        self.module_stack.addWidget(self.usuarios_view)     # index 5
        self.module_stack.addWidget(self.auditoria_view)    # index 6
        self.module_stack.addWidget(self.configuracion_view)# index 7

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.section_selected.connect(self.navigate_to_section)

        # Agregar al layout principal
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.module_stack)

    def navigate_to_section(self, index):
        """Actualizar la sección activa en el QStackedWidget."""
        if 0 <= index < self.module_stack.count():
            self.module_stack.setCurrentIndex(index)
            self.logger.info(f"Navegando a la sección con índice {index}")
        else:
            self.logger.warning(f"Índice fuera de rango: {index}")

class Sidebar(QWidget):
    section_selected = pyqtSignal(int)  # Señal para emitir el índice seleccionado

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 20, 10, 10)
        self.layout.setSpacing(8)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)
        self.create_buttons()

    def create_buttons(self):
        sections = [
            ("Inventario", "inventario", 0),
            ("Obras", "obras", 1),
            ("Producción", "produccion", 2),
            ("Logística", "logistica", 3),
            ("Pedidos", "pedidos", 4),
            ("Usuarios", "usuarios", 5),
            ("Auditoría", "auditoria", 6),
            ("Configuración", "configuracion", 7),
        ]

        for name, icon_name, index in sections:
            btn = QPushButton(name)
            btn.setObjectName("botonMenu")
            btn.setFixedHeight(40)  # Altura fija
            btn.setFixedWidth(150)  # Ancho fijo
            btn.setIcon(get_icon(f"{icon_name}.svg"))
            btn.setIconSize(QSize(20, 20))
            btn.setStyleSheet("""
                QPushButton#botonMenu {
                    background-color: #2563eb; /* Azul */
                    color: white; /* Texto blanco */
                    text-align: center; /* Centrar texto */
                    border: none;
                    font-size: 14px; /* Tamaño de letra */
                    font-weight: bold; /* Negrita */
                    border-radius: 8px; /* Bordes redondeados */
                }
                QPushButton#botonMenu:hover {
                    background-color: #1e40af; /* Azul más oscuro */
                }
                QPushButton#botonMenu:pressed {
                    background-color: #1e3a8a; /* Azul aún más oscuro */
                }
            """)
            btn.clicked.connect(partial(self.section_selected.emit, index))
            self.layout.addWidget(btn)

class PedidosView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Crear contenedor para los botones
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)  # Espaciado entre botones
        botones_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrar botones

        # Botón "Crear Pedido"
        self.boton_crear = QPushButton("Crear Pedido")
        self.boton_crear.setFixedSize(150, 30)
        self.boton_crear.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                border: none;
                border-radius: 15px; /* Bordes redondeados */
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        botones_layout.addWidget(self.boton_crear)

        # Botón "Ver Detalles del Pedido"
        self.boton_ver_detalles = QPushButton("Ver Detalles del Pedido")
        self.boton_ver_detalles.setFixedSize(150, 30)
        self.boton_ver_detalles.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                border: none;
                border-radius: 15px; /* Bordes redondeados */
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        botones_layout.addWidget(self.boton_ver_detalles)

        # Botón "Cargar Presupuesto"
        self.boton_cargar_presupuesto = QPushButton("Cargar Presupuesto")
        self.boton_cargar_presupuesto.setFixedSize(150, 30)
        self.boton_cargar_presupuesto.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                border: none;
                border-radius: 15px; /* Bordes redondeados */
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        botones_layout.addWidget(self.boton_cargar_presupuesto)

        # Agregar el layout de botones al layout principal
        self.layout.addLayout(botones_layout)

class AuditoriaView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Crear contenedor para los botones
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)  # Espaciado entre botones
        botones_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrar botones

        # Botón "Ver Logs"
        self.boton_ver_logs = QPushButton("Ver Logs")
        self.boton_ver_logs.setFixedSize(150, 30)
        self.boton_ver_logs.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                border: none;
                border-radius: 15px; /* Bordes redondeados */
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        botones_layout.addWidget(self.boton_ver_logs)

        # Botón "Exportar Logs"
        self.boton_exportar_logs = QPushButton("Exportar Logs")
        self.boton_exportar_logs.setFixedSize(150, 30)
        self.boton_exportar_logs.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                border: none;
                border-radius: 15px; /* Bordes redondeados */
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        botones_layout.addWidget(self.boton_exportar_logs)

        # Botón "Filtrar Logs"
        self.boton_filtrar_logs = QPushButton("Filtrar Logs")
        self.boton_filtrar_logs.setFixedSize(150, 30)
        self.boton_filtrar_logs.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                border: none;
                border-radius: 15px; /* Bordes redondeados */
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        botones_layout.addWidget(self.boton_filtrar_logs)

        # Agregar el layout de botones al layout principal
        self.layout.addLayout(botones_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())