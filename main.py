from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, 
    QPushButton, QStackedWidget, QMessageBox
)
from PyQt6.QtGui import QPalette, QColor, QIcon
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
from core.startup_update_checker import check_and_update_critical_packages

# Verificar y actualizar paquetes críticos antes de continuar
check_and_update_critical_packages()

# Importar vistas
from modules.inventario.view import InventarioView
from modules.obras.view import ObrasView
from modules.obras.produccion.view import ProduccionView  # Importar desde el módulo correcto
from modules.logistica.view import LogisticaView
from modules.compras.pedidos.view import PedidosView as ComprasPedidosView
from modules.pedidos.view import PedidosView as PedidosIndependienteView
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
from modules.compras.pedidos.controller import ComprasPedidosController
from modules.pedidos.controller import PedidosController
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

        self.initUI()
        # QLabel para usuario actual, visualmente destacado
        self.usuario_label = QLabel()
        self.usuario_label.setObjectName("usuarioActualLabel")
        self.usuario_label.setStyleSheet("background: #e0e7ef; color: #1e293b; font-size: 13px; font-weight: bold; border-radius: 8px; padding: 4px 12px; margin-right: 8px;")
        self.usuario_label.setText("")
        self.statusBar().addPermanentWidget(self.usuario_label, 1)

    def initUI(self):
        # Crear conexiones persistentes a las bases de datos (una sola instancia por base)
        self.db_connection_inventario = DatabaseConnection()
        self.db_connection_inventario.conectar_a_base("inventario")

        self.db_connection_usuarios = DatabaseConnection()
        self.db_connection_usuarios.conectar_a_base("users")

        self.db_connection_auditoria = DatabaseConnection()
        self.db_connection_auditoria.conectar_a_base("auditoria")

        self.db_connection_pedidos = self.db_connection_inventario  # Unificar: pedidos usa inventario
        self.db_connection_configuracion = self.db_connection_inventario  # Unificar: configuración usa inventario
        self.db_connection_produccion = self.db_connection_inventario  # Unificar: producción usa inventario

        # Crear instancias de modelos con la conexión correspondiente
        self.inventario_model = InventarioModel(db_connection=self.db_connection_inventario)
        self.inventario_model.actualizar_qr_y_campos_por_descripcion()  # Actualiza QR, tipo, acabado y longitud automáticamente
        self.obras_model = ObrasModel(db_connection=self.db_connection_inventario)
        self.produccion_model = ProduccionModel(db_connection=self.db_connection_produccion)
        self.logistica_model = LogisticaModel(db_connection=self.db_connection_inventario)
        self.pedidos_model = PedidosModel(db_connection=self.db_connection_pedidos)
        self.configuracion_model = ConfiguracionModel(db_connection=self.db_connection_configuracion)
        self.herrajes_model = HerrajesModel(self.db_connection_inventario)
        self.usuarios_model = UsuariosModel(db_connection=self.db_connection_usuarios)
        self._crear_usuarios_iniciales()

        # Crear instancias de vistas y controladores
        self.inventario_view = InventarioView(db_connection=self.db_connection_inventario, usuario_actual="admin")
        self.inventario_controller = InventarioController(
            model=self.inventario_model, view=self.inventario_view, db_connection=self.db_connection_inventario
        )

        self.obras_view = ObrasView()
        self.obras_controller = ObrasController(
            model=self.obras_model, view=self.obras_view, db_connection=self.db_connection_inventario, usuarios_model=self.usuarios_model
        )

        self.produccion_view = ProduccionView()
        self.produccion_controller = ProduccionController(
            model=self.produccion_model, view=self.produccion_view, db_connection=self.db_connection_produccion
        )

        self.logistica_view = LogisticaView()
        self.logistica_controller = LogisticaController(
            model=self.logistica_model, view=self.logistica_view, db_connection=self.db_connection_inventario, usuarios_model=self.usuarios_model
        )

        # Inicializar el módulo Pedidos dentro de Compras
        self.compras_pedidos_view = ComprasPedidosView()
        self.compras_pedidos_controller = ComprasPedidosController(
            self.pedidos_model, self.compras_pedidos_view, self.db_connection_pedidos, self.usuarios_model
        )
        self.compras_pedidos_controller.cargar_pedidos()

        # Inicializar el módulo Pedidos independiente (si aplica)
        self.pedidos_view = PedidosIndependienteView()
        self.pedidos_controller = PedidosController(self.pedidos_view, self.db_connection_pedidos)

        # Crear instancias de controladores antes de las vistas
        self.usuarios_controller = UsuariosController(
            model=self.usuarios_model, view=None, db_connection=self.db_connection_usuarios
        )
        self.usuarios_view = UsuariosView()
        self.usuarios_controller.view = self.usuarios_view

        try:
            # Inicializar el módulo Auditoría
            self.auditoria_view = AuditoriaView()  # Crear instancia de AuditoriaView
            self.auditoria_model = AuditoriaModel(db_connection=self.db_connection_auditoria)  # Pasar conexión unificada
            self.auditoria_controller = AuditoriaController(
                model=self.auditoria_model, view=self.auditoria_view, db_connection=self.db_connection_auditoria
            )
        except Exception as e:
            print(f"Error al inicializar el módulo Auditoría: {e}")
            # Mostrar un mensaje de advertencia en la interfaz
            self.statusBar().showMessage("El módulo Auditoría está deshabilitado temporalmente.")

        try:
            # Inicializar el módulo Configuración
            self.configuracion_view = ConfiguracionView()
            self.configuracion_controller = ConfiguracionController(
                model=self.configuracion_model, view=self.configuracion_view, db_connection=self.db_connection_configuracion, usuarios_model=self.usuarios_model
            )
        except Exception as e:
            print(f"Error al inicializar el módulo Configuración: {e}")
            self.statusBar().showMessage("El módulo Configuración está deshabilitado temporalmente.")

        # Inicializar el módulo Mantenimiento
        self.mantenimiento_view = MantenimientoView()
        self.mantenimiento_controller = None
        try:
            from modules.mantenimiento.controller import MantenimientoController
            self.mantenimiento_controller = MantenimientoController(
                model=self.mantenimiento_view, view=self.mantenimiento_view, db_connection=self.db_connection_inventario, usuarios_model=self.usuarios_model
            )
        except Exception as e:
            print(f"Error al inicializar el módulo Mantenimiento: {e}")

        # Inicializar el módulo Contabilidad
        self.contabilidad_view = ContabilidadView()
        self.contabilidad_controller = None
        try:
            from modules.contabilidad.controller import ContabilidadController
            self.contabilidad_controller = ContabilidadController(
                model=self.contabilidad_view, view=self.contabilidad_view, db_connection=self.db_connection_inventario, usuarios_model=self.usuarios_model
            )
        except Exception as e:
            print(f"Error al inicializar el módulo Contabilidad: {e}")

        # Inicializar el módulo Herrajes
        self.herrajes_view = HerrajesView()
        self.herrajes_controller = HerrajesController(
            self.herrajes_model, self.herrajes_view, db_connection=self.db_connection_inventario, usuarios_model=self.usuarios_model
        )

        try:
            from modules.vidrios.controller import VidriosController
            self.vidrios_controller = VidriosController(
                model=self.vidrios_view, view=self.vidrios_view, db_connection=self.db_connection_inventario
            )
        except Exception:
            pass

        try:
            from modules.notificaciones.controller import NotificacionesController
            self.notificaciones_controller = NotificacionesController(
                model=self.notificaciones_view, view=self.notificaciones_view, db_connection=self.db_connection_inventario, usuarios_model=self.usuarios_model
            )
        except Exception:
            pass

        # Layout principal
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Crear QStackedWidget para la navegación entre secciones
        self.module_stack = QStackedWidget()
        self.module_stack.addWidget(self.obras_view)            # index 0
        self.module_stack.addWidget(self.inventario_view)       # index 1
        self.module_stack.addWidget(self.herrajes_view)         # index 2
        self.module_stack.addWidget(self.compras_pedidos_view)  # index 3
        self.module_stack.addWidget(self.logistica_view)        # index 4
        try:
            from modules.vidrios.view import VidriosView
            self.vidrios_view = VidriosView()
            self.module_stack.addWidget(self.vidrios_view)      # index 5
        except Exception:
            pass
        self.module_stack.addWidget(self.mantenimiento_view)    # index 6
        self.module_stack.addWidget(self.produccion_view)       # index 7
        self.module_stack.addWidget(self.contabilidad_view)     # index 8
        self.module_stack.addWidget(self.auditoria_view)        # index 9
        self.module_stack.addWidget(self.usuarios_view)         # index 10
        self.module_stack.addWidget(self.configuracion_view)    # index 11

        # Crear el sidebar con los íconos SVG y nombres descriptivos de módulos, en orden de flujo real de trabajo
        svg_dir = os.path.join(os.path.dirname(__file__), 'utils')
        sidebar_sections = [
            ("Obras", os.path.join(svg_dir, 'obras.svg')),
            ("Inventario", os.path.join(svg_dir, 'inventario.svg')),
            ("Herrajes", os.path.join(svg_dir, 'herrajes.svg')),
            ("Compras / Pedidos", os.path.join(svg_dir, 'compras.svg')),
            ("Logística", os.path.join(svg_dir, 'logistica.svg')),
            ("Vidrios", os.path.join(svg_dir, 'vidrios.svg')),
            ("Mantenimiento", os.path.join(svg_dir, 'mantenimiento.svg')),
            ("Producción", os.path.join(svg_dir, 'produccion.svg')),
            ("Contabilidad", os.path.join(svg_dir, 'contabilidad.svg')),
            ("Auditoría", os.path.join(svg_dir, 'auditoria.svg')),
            ("Usuarios", os.path.join(svg_dir, 'users.svg')),
            ("Configuración", os.path.join(svg_dir, 'configuracion.svg'))
        ]
        self.sidebar = Sidebar("utils", sidebar_sections, mostrar_nombres=True)
        self.sidebar.pageChanged.connect(self.module_stack.setCurrentIndex)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.module_stack)
        self._ajustar_sidebar()

    def _crear_usuarios_iniciales(self):
        """Crea los usuarios admin, supervisor y comun si no existen."""
        usuarios = self.usuarios_model.obtener_usuarios()
        # pyodbc.Row permite acceso por índice o atributo, pero no por string
        usernames = [getattr(u, 'usuario', u[3]) for u in usuarios] if usuarios else []
        import hashlib
        if 'admin' not in usernames:
            self.usuarios_model.agregar_usuario((
                'Administrador', 'Admin', 'admin@demo.com', 'admin',
                hashlib.sha256('admin'.encode()).hexdigest(), 'admin'
            ))
        if 'supervisor' not in usernames:
            self.usuarios_model.agregar_usuario((
                'Supervisor', 'Supervisor', 'supervisor@demo.com', 'supervisor',
                hashlib.sha256('1234'.encode()).hexdigest(), 'supervisor'
            ))
        if 'usuario' not in usernames:
            self.usuarios_model.agregar_usuario((
                'Usuario', 'Comun', 'usuario@demo.com', 'usuario',
                hashlib.sha256('demo'.encode()).hexdigest(), 'usuario'
            ))

    def mostrar_modulos_permitidos(self, usuario):
        # Obtener módulos permitidos según el usuario
        modulos_permitidos = self.usuarios_model.obtener_modulos_permitidos(usuario)
        # Mapear nombre de módulo a índice en module_stack y sidebar_sections
        modulo_a_indice = {
            "Obras": 0,
            "Inventario": 1,
            "Producción": 2,
            "Compras / Pedidos": 3,
            "Herrajes": 4,
            "Vidrios": 5,
            "Logística": 6,
            "Mantenimiento": 7,
            "Contabilidad": 8,
            "Auditoría": 9,
            "Usuarios": 10,
            "Configuración": 11
        }
        # Filtrar sidebar_sections y module_stack según permisos
        secciones_filtradas = []
        indices_permitidos = []
        for i, (nombre, icono) in enumerate(self.sidebar.sections):
            if nombre in modulos_permitidos:
                secciones_filtradas.append((nombre, icono))
                indices_permitidos.append(i)
        # Actualizar sidebar
        self.sidebar.set_sections(secciones_filtradas)
        # Actualizar module_stack para solo mostrar los permitidos
        # (Opcional: podrías ocultar widgets no permitidos o bloquear acceso)
        self.module_stack.setCurrentIndex(indices_permitidos[0] if indices_permitidos else 0)

    def login_success(self, usuario):
        # Forzar usuario admin para pruebas y experiencia completa
        usuario_admin = {
            'id': 1,
            'username': 'admin',
            'rol': 'admin',
            'email': 'admin@demo.com',
            'nombre': 'Administrador',
            'apellido': 'Demo'
        }
        self.usuario_actual = usuario_admin
        self.mostrar_modulos_permitidos(usuario_admin)
        # Pasar usuario_actual a los controladores
        self.inventario_controller.usuario_actual = usuario_admin
        self.obras_controller.usuario_actual = usuario_admin
        self.produccion_controller.usuario_actual = usuario_admin
        self.logistica_controller.usuario_actual = usuario_admin
        self.compras_pedidos_controller.usuario_actual = usuario_admin
        self.pedidos_controller.usuario_actual = usuario_admin
        self.usuarios_controller.usuario_actual = usuario_admin
        if hasattr(self, 'auditoria_controller'):
            self.auditoria_controller.usuario_actual = usuario_admin
        if hasattr(self, 'configuracion_controller'):
            self.configuracion_controller.usuario_actual = usuario_admin
        if hasattr(self, 'herrajes_controller'):
            self.herrajes_controller.usuario_actual = usuario_admin
        # Mostrar el usuario actual de forma visualmente destacado en la barra de estado
        self.usuario_label.setText(f"Usuario: {usuario_admin['username']} ({usuario_admin['rol']})")
        self.statusBar().showMessage(f"Usuario actual: {usuario_admin['username']} ({usuario_admin['rol']})")

    def showEvent(self, event):
        super().showEvent(event)
        self._ajustar_sidebar()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QtCore.QEvent.Type.WindowStateChange:
            self._ajustar_sidebar()

    def _ajustar_sidebar(self):
        # Si la ventana está maximizada o pantalla completa, expandir sidebar
        expanded = self.isMaximized() or self.isFullScreen() or self.width() > 1400
        self.sidebar.set_expanded(expanded)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Aplicar el stylesheet neumórfico global
    with open("mps/ui/assets/stylesheet.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())