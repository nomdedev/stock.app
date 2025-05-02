from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QMessageBox
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from utils.icon_loader import get_icon
from functools import partial
import ctypes

# Dependencias principales
import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from core.database import DatabaseConnection, DataAccessLayer, InventarioDatabaseConnection
from core.logger import Logger

# Importar vistas reales
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

        # Obtener el tamaño de la pantalla
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)

        # Calcular el tamaño de la ventana (80% del tamaño de la pantalla)
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)

        # Calcular la posición para centrar la ventana
        pos_x = (screen_width - window_width) // 2
        pos_y = (screen_height - window_height) // 2

        # Establecer geometría de la ventana
        self.setGeometry(pos_x, pos_y, window_width, window_height)

        self.initUI()

    def initUI(self):
        # Crear instancia de conexión a la base de datos
        self.db_connection = DatabaseConnection()
        self.db_connection.conectar_a_base("inventario")  # Cambiado a "inventario"

        # Crear instancias de modelos
        self.inventario_db_connection = InventarioDatabaseConnection()
        self.inventario_model = InventarioModel(db_connection=self.inventario_db_connection)
        self.obras_model = ObrasModel(db_connection=self.db_connection)
        self.produccion_model = ProduccionModel(db_connection=self.db_connection)
        self.logistica_model = LogisticaModel(db_connection=self.db_connection)
        self.pedidos_model = PedidosModel(db_connection=self.db_connection)
        self.usuarios_model = UsuariosModel(db_connection=self.db_connection)
        self.auditoria_model = AuditoriaModel(db_connection=self.db_connection)
        self.configuracion_model = ConfiguracionModel(db_connection=self.db_connection)

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
            model=self.pedidos_model, view=self.pedidos_view, db_connection=self.db_connection
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
            btn.setFixedHeight(44)
            btn.setIcon(get_icon(f"{icon_name}.svg"))
            btn.setIconSize(QSize(20, 20))
            btn.setStyleSheet("""
                QPushButton#botonMenu {
                    background-color: #2563eb; /* Azul */
                    color: white;
                    text-align: left;
                    padding-left: 20px;
                    border: none;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 8px;
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())