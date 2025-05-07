from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, 
    QPushButton, QStackedWidget, QMessageBox
)
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from utils.icon_loader import get_icon
from utils.theme_manager import aplicar_tema, cargar_modo_tema
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
from modules.obras.produccion.view import ProduccionView  # Importar desde el módulo correcto
from modules.logistica.view import LogisticaView
from modules.compras.view import PedidosView
from modules.usuarios.view import UsuariosView
from modules.auditoria.view import AuditoriaView
from modules.configuracion.view import ConfiguracionView
from modules.mantenimiento.view import MantenimientoView
from modules.contabilidad.view import ContabilidadView
from modules.herrajes.view import HerrajesView

# Importar controladores
from modules.inventario.controller import InventarioController
from modules.obras.controller import ObrasController
from modules.obras.produccion.controller import ProduccionController  # Importar desde el módulo correcto
from modules.logistica.controller import LogisticaController
from modules.compras.pedidos.controller import PedidosController  # Importar desde el módulo correcto
from modules.usuarios.controller import UsuariosController
from modules.auditoria.controller import AuditoriaController
from modules.configuracion.controller import ConfiguracionController
from modules.herrajes.controller import HerrajesController

# Importar modelos
from modules.inventario.model import InventarioModel
from modules.obras.model import ObrasModel
from modules.obras.produccion.model import ProduccionModel  # Importar desde el módulo correcto
from modules.logistica.model import LogisticaModel
from modules.compras.pedidos.model import PedidosModel  # Importar desde el módulo correcto
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from modules.configuracion.model import ConfiguracionModel
from modules.herrajes.model import HerrajesModel

# Importar componentes
from components.sidebar_button import SidebarButton
from widgets.sidebar import Sidebar

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

        # Inicializar el módulo Pedidos dentro de Compras
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

        try:
            # Inicializar el módulo Auditoría
            self.auditoria_view = AuditoriaView()  # Crear instancia de AuditoriaView
            self.auditoria_model = AuditoriaModel()  # Crear instancia de AuditoriaModel
            self.auditoria_controller = AuditoriaController(
                model=self.auditoria_model, view=self.auditoria_view
            )
        except Exception as e:
            print(f"Error al inicializar el módulo Auditoría: {e}")
            # Mostrar un mensaje de advertencia en la interfaz
            self.statusBar().showMessage("El módulo Auditoría está deshabilitado temporalmente.")

        try:
            # Inicializar el módulo Configuración
            self.configuracion_view = ConfiguracionView()
            self.configuracion_controller = ConfiguracionController(
                model=self.configuracion_model, view=self.configuracion_view
            )
        except Exception as e:
            print(f"Error al inicializar el módulo Configuración: {e}")
            self.statusBar().showMessage("El módulo Configuración está deshabilitado temporalmente.")

        # Inicializar el módulo Mantenimiento
        self.mantenimiento_view = MantenimientoView()

        # Inicializar el módulo Contabilidad
        self.contabilidad_view = ContabilidadView()

        # Inicializar el módulo Herrajes
        self.herrajes_model = HerrajesModel(self.db_connection_inventario)
        self.herrajes_view = HerrajesView()
        self.herrajes_controller = HerrajesController(self.herrajes_model, self.herrajes_view)

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
        self.module_stack.addWidget(self.mantenimiento_view)  # index 5
        self.module_stack.addWidget(self.contabilidad_view)  # index 6
        self.module_stack.addWidget(self.herrajes_view)      # index 7
        self.module_stack.addWidget(self.auditoria_view)    # index 8
        self.module_stack.addWidget(self.usuarios_view)     # index 9
        self.module_stack.addWidget(self.configuracion_view)# index 10

        # Crear el sidebar con los módulos
        sections = [
            ("Inventario", "img/inventario.svg"),
            ("Obras", "img/obras.svg"),
            ("Producción", "img/produccion.svg"),
            ("Logística", "img/logistica.svg"),
            ("Compras", "img/compras.svg"),
            ("Usuarios", "img/users.svg"),
            ("Auditoría", "img/auditoria.svg"),
            ("Configuración", "img/configuracion.svg"),
            ("Mantenimiento", "img/mantenimiento.svg"),
            ("Contabilidad", "img/contabilidad.svg"),
            ("Vidrios", "img/vidrios.svg")
        ]
        self.sidebar = Sidebar("img", sections)
        self.sidebar.pageChanged.connect(self.module_stack.setCurrentIndex)
        main_layout.addWidget(self.sidebar)

        main_layout.addWidget(self.module_stack)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())