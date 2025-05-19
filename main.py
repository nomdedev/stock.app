# --- PRINCIPIOS Y PARÁMETROS DE DISEÑO UI/UX PARA TODA LA APP ---
# Estos lineamientos deben aplicarse SIEMPRE al crear cualquier ventana, diálogo, botón, label, input, tabla, etc.
# Si se requiere una excepción, debe justificarse y documentarse.
#
# 1. Padding y márgenes:
#    - Padding mínimo en diálogos y widgets: 20px vertical, 24px horizontal.
#    - Márgenes entre elementos: mínimo 16px.
#    - Los cuadros de diálogo deben estar perfectamente centrados y con el mismo espacio a ambos lados.
# 2. Bordes y esquinas:
#    - Bordes redondeados: 8-12px en todos los diálogos, botones y campos de entrada.
# 3. Tipografía:
#    - Fuente: Segoe UI, Roboto, o similar sans-serif.
#    - Tamaño base: 11px para mensajes secundarios, 13px para principales, 14px para títulos.
#    - Peso: 500-600 para títulos y botones, 400-500 para textos normales.
#    - Color de texto: #1e293b para texto principal, #ef4444 para errores, #2563eb para info, #22c55e para éxito, #fbbf24 para advertencia.
#    - El texto debe estar centrado vertical y horizontalmente en diálogos y botones.
# 4. Botones:
#    - Ancho mínimo: 80px, alto mínimo: 28px.
#    - Padding horizontal: 16px.
#    - Bordes redondeados: 8px.
#    - Color de fondo: #2563eb para acción principal, #f1f5f9 para secundarios.
#    - Color de texto: blanco en botones primarios, #1e293b en secundarios.
#    - Espaciado entre botones: 16px.
# 5. Colores y fondo:
#    - Fondo general: #f1f5f9.
#    - Los diálogos de error usan #ef4444 para el texto y fondo claro.
#    - Los mensajes de éxito usan #22c55e, advertencia #fbbf24, info #2563eb.
# 6. Íconos:
#    - Siempre SVG o PNG de alta resolución.
#    - Alineados con el texto y con padding de al menos 8px respecto al texto.
# 7. Tablas y formularios:
#    - Espaciado entre filas: mínimo 8px.
#    - Padding en celdas: 12px.
#    - Bordes redondeados en headers y celdas: 8px.
#    - No saturar de información, usar scroll y paginación si es necesario.
# 8. Feedback visual:
#    - Mensajes breves, claros y con color adecuado.
#    - Siempre usar QMessageBox o widgets personalizados con los estilos definidos.
#    - El feedback debe ser inmediato tras la acción del usuario.
# 9. Accesibilidad:
#    - Contraste alto entre texto y fondo.
#    - No usar solo color para indicar estado (agregar íconos o texto).
#    - Tamaños de fuente nunca menores a 10px.
# 10. Código:
#     - Centralizar estilos en QSS global o helpers.
#     - No hardcodear estilos en cada widget, salvo casos justificados.
#     - Reutilizar componentes visuales y helpers para mantener coherencia.
#     - Documentar cualquier excepción a estas reglas.
# --- FIN DE PRINCIPIOS DE DISEÑO ---

import sys
import subprocess
import os

def verificar_e_instalar_dependencias():
    requeridos = [
        "PyQt6", "pyodbc", "reportlab", "qrcode", "pandas"
    ]
    faltantes = []
    for paquete in requeridos:
        try:
            __import__(paquete)
        except ImportError:
            faltantes.append(paquete)
    if faltantes:
        print(f"Instalando paquetes faltantes: {', '.join(faltantes)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *faltantes])
        print("Dependencias instaladas. Reiniciando la aplicación...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

def test_dependencias():
    try:
        import PyQt6
        import pyodbc
        import reportlab
        import qrcode
        import pandas
        print("✅ Todas las dependencias críticas están instaladas correctamente.")
    except Exception as e:
        print(f"❌ Error en la verificación de dependencias: {e}")
        sys.exit(1)

verificar_e_instalar_dependencias()
test_dependencias()

import os
# Refuerzo para evitar errores de OpenGL/Skia/Chromium en Windows
os.environ['QT_OPENGL'] = 'software'
os.environ['QT_QUICK_BACKEND'] = 'software'
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu --disable-software-rasterizer'

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

# Forzar aceleración por software de Qt/OpenGL
os.environ['QT_OPENGL'] = 'software'

# Configurar el path para importar módulos locales
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importar utilidades principales
from core.logger import Logger
from core.database import DatabaseConnection, InventarioDatabaseConnection
from core.startup_update_checker import check_and_update_critical_packages
from core.splash_screen import SplashScreen

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
        from PyQt6.QtWidgets import QStatusBar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
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
        self._status_bar.addPermanentWidget(self.usuario_label, 1)

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=4000):
        """Muestra un mensaje visual en la barra de estado y, si es error, también un QMessageBox."""
        colores = {
            "info": "#2563eb",
            "exito": "#22c55e",
            "advertencia": "#fbbf24",
            "error": "#ef4444"
        }
        color = colores.get(tipo, "#2563eb")
        # Fondo sutil y texto destacado para feedback moderno
        self._status_bar.setStyleSheet(f"background: #f1f5f9; color: {color}; font-weight: bold; font-size: 13px; border-radius: 8px; padding: 4px 12px;")
        self._status_bar.showMessage(mensaje, duracion)
        if tipo == "error":
            QMessageBox.critical(self, "Error", mensaje)
        elif tipo == "advertencia":
            QMessageBox.warning(self, "Advertencia", mensaje)
        elif tipo == "exito":
            QMessageBox.information(self, "Éxito", mensaje)

    def actualizar_usuario_label(self, usuario):
        """Actualiza el label de usuario actual con color según el rol y estilo moderno."""
        rol = usuario.get('rol', '').lower()
        colores = {
            'admin': '#2563eb',
            'supervisor': '#fbbf24',
            'usuario': '#22c55e'
        }
        color = colores.get(rol, '#1e293b')
        # Fondo sutil, borde y color de texto por rol, consistente con feedback
        self.usuario_label.setStyleSheet(
            f"background: #e0e7ef; color: {color}; font-size: 13px; font-weight: bold; border-radius: 8px; padding: 4px 12px; margin-right: 8px; border: 1.5px solid {color};"
        )
        self.usuario_label.setText(f"Usuario: {usuario['username']} ({usuario['rol']})")

    def on_modulo_cambiado(self, index):
        nombre_modulo = self.sidebar.sections[index][0] if index < len(self.sidebar.sections) else ""
        self.mostrar_mensaje(f"Módulo activo: {nombre_modulo}", tipo="info", duracion=2500)

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
            model=self.obras_model, view=self.obras_view, db_connection=self.db_connection_inventario, usuarios_model=self.usuarios_model, logistica_controller=None  # Se setea después
        )

        self.produccion_view = ProduccionView()
        self.produccion_controller = ProduccionController(
            model=self.produccion_model, view=self.produccion_view, db_connection=self.db_connection_produccion
        )

        self.logistica_view = LogisticaView()
        self.logistica_controller = LogisticaController(
            model=self.logistica_model, view=self.logistica_view, db_connection=self.db_connection_inventario, usuarios_model=self.usuarios_model
        )
        # Enlazar referencia cruzada para sincronización
        self.obras_controller.logistica_controller = self.logistica_controller

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
            self._status_bar.showMessage("El módulo Auditoría está deshabilitado temporalmente.")

        try:
            # Inicializar el módulo Configuración
            self.configuracion_view = ConfiguracionView()
            self.configuracion_controller = ConfiguracionController(
                model=self.configuracion_model, view=self.configuracion_view, db_connection=self.db_connection_configuracion, usuarios_model=self.usuarios_model
            )
        except Exception as e:
            print(f"Error al inicializar el módulo Configuración: {e}")
            self._status_bar.showMessage("El módulo Configuración está deshabilitado temporalmente.")

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
            from modules.notificaciones.view import NotificacionesView
            from modules.notificaciones.controller import NotificacionesController
            self.notificaciones_view = NotificacionesView()
            self.notificaciones_controller = NotificacionesController(
                model=self.notificaciones_view, view=self.notificaciones_view, db_connection=self.db_connection_inventario, usuarios_model=self.usuarios_model
            )
        except Exception as e:
            print(f"Error al inicializar el módulo Notificaciones: {e}")

        # Layout principal
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Crear QStackedWidget para la navegación entre secciones
        self.module_stack = QStackedWidget()
        self.module_stack.addWidget(self.obras_view)            # index 0
        inventario_valido = self.db_connection_inventario and all(hasattr(self.db_connection_inventario, attr) for attr in ["driver", "database", "username", "password"])
        if inventario_valido:
            self.module_stack.addWidget(self.inventario_view)   # index 1
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
            # Solo mostrar Inventario si la conexión es válida
            *([("Inventario", os.path.join(svg_dir, 'inventario.svg'))] if inventario_valido else []),
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
        self.sidebar.pageChanged.connect(self.on_modulo_cambiado)
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
        # Usar el usuario real autenticado (no hardcodear admin)
        self.usuario_actual = usuario
        self.mostrar_modulos_permitidos(usuario)
        # Pasar usuario_actual a los controladores
        self.inventario_controller.usuario_actual = usuario
        self.obras_controller.usuario_actual = usuario
        self.produccion_controller.usuario_actual = usuario
        self.logistica_controller.usuario_actual = usuario
        self.compras_pedidos_controller.usuario_actual = usuario
        self.pedidos_controller.usuario_actual = usuario
        self.usuarios_controller.usuario_actual = usuario
        if hasattr(self, 'auditoria_controller'):
            self.auditoria_controller.usuario_actual = usuario
        if hasattr(self, 'configuracion_controller'):
            self.configuracion_controller.usuario_actual = usuario
        if hasattr(self, 'herrajes_controller'):
            self.herrajes_controller.usuario_actual = usuario
        # Mostrar el usuario actual de forma visualmente destacado en la barra de estado
        self.actualizar_usuario_label(usuario)
        self.mostrar_mensaje(f"Usuario actual: {usuario['username']} ({usuario['rol']})", tipo="info", duracion=4000)

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

def chequear_conexion_bd():
    import pyodbc
    # Puedes ajustar estos valores según tu configuración real
    DB_DRIVER = os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    DB_SERVER = os.environ.get('DB_SERVER', 'localhost\\SQLEXPRESS')
    DB_DATABASE = os.environ.get('DB_DATABASE', 'inventario')
    DB_USERNAME = os.environ.get('DB_USERNAME', 'sa')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'tu_contraseña_aqui')
    try:
        connection_string = (
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_DATABASE};"
            f"UID={DB_USERNAME};"
            f"PWD={DB_PASSWORD};"
            f"TrustServerCertificate=yes;"
        )
        with pyodbc.connect(connection_string, timeout=5) as conn:
            print("✅ Conexión exitosa a la base de datos.")
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        print("Verifica usuario, contraseña, servidor y que SQL Server acepte autenticación SQL.")
        sys.exit(1)

def chequear_conexion_bd_gui():
    from PyQt6.QtWidgets import QApplication, QMessageBox
    # Usar SIEMPRE los parámetros centralizados de core.config
    from core.config import DB_SERVER, DB_SERVER_ALTERNATE, DB_USERNAME, DB_PASSWORD, DB_DEFAULT_DATABASE, DB_TIMEOUT
    DB_DRIVER = 'ODBC Driver 17 for SQL Server'
    # Intentar primero con la IP, luego con el nombre de instancia alternativo
    servidores = [DB_SERVER, DB_SERVER_ALTERNATE]
    for DB_SERVER_ACTUAL in servidores:
        try:
            connection_string = (
                f"DRIVER={{{DB_DRIVER}}};"
                f"SERVER={DB_SERVER_ACTUAL};"
                f"DATABASE={DB_DEFAULT_DATABASE};"
                f"UID={DB_USERNAME};"
                f"PWD={DB_PASSWORD};"
                f"TrustServerCertificate=yes;"
            )
            import pyodbc
            with pyodbc.connect(connection_string, timeout=DB_TIMEOUT) as conn:
                print(f"✅ Conexión exitosa a la base de datos: {DB_SERVER_ACTUAL}")
                return
        except Exception as e:
            print(f"❌ Error de conexión a la base de datos ({DB_SERVER_ACTUAL}): {e}")
    # Si falla todo, mostrar error GUI
    app = QApplication.instance() or QApplication(sys.argv)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Error de conexión a la base de datos")
    msg.setText("❌ No se pudo conectar a la base de datos.")
    msg.setInformativeText(f"Verifica usuario, contraseña, servidor (puede ser IP o nombre) y que SQL Server acepte autenticación SQL.\n\nIntentado con: {DB_SERVER} y {DB_SERVER_ALTERNATE}")
    # Estilo minimalista, letra pequeña, padding simétrico, centrado, bordes redondeados, fondo claro
    msg.setStyleSheet("""
        QMessageBox {
            background: #f1f5f9;
            color: #ef4444;
            font-size: 10px;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            font-weight: 500;
            border-radius: 12px;
            padding: 20px 24px 20px 24px;
        }
        QLabel {
            qproperty-alignment: 'AlignCenter';
            font-size: 10px;
        }
        QPushButton {
            min-width: 80px;
            min-height: 28px;
            border-radius: 8px;
            font-size: 10px;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            padding: 4px 16px;
        }
    """)
    msg.exec()
    sys.exit(1)

# --- BASE DE MEJORES PRÁCTICAS DE DISEÑO PARA TODA LA APP ---
# 1. Todos los diálogos y mensajes deben tener padding simétrico, bordes redondeados y fondo claro.
# 2. El texto debe estar centrado y usar fuente moderna, tamaño 11-13px, peso 500-600.
# 3. Los botones deben tener mínimo 80px de ancho, padding horizontal generoso y bordes redondeados.
# 4. Los colores deben ser consistentes con la paleta principal (#f1f5f9 fondo, #2563eb info, #ef4444 error, #22c55e éxito, #fbbf24 advertencia).
# 5. Los íconos deben ser SVG o PNG de alta resolución, alineados con el texto.
# 6. Los layouts deben tener márgenes y espaciados uniformes (mínimo 16px), y los elementos bien alineados.
# 7. El feedback visual debe ser inmediato y claro, usando colores y mensajes breves.
# 8. Los cuadros de diálogo deben estar bien encuadrados, con el mismo espacio a ambos lados.
# 9. El diseño debe ser responsivo y accesible, evitando textos demasiado pequeños o contrastes bajos.
# 10. El código debe centralizar estilos y reutilizar componentes visuales para mantener coherencia.
# 11. Evitar hardcodear estilos en cada widget: usar QSS global o helpers.
# 12. Siempre usar setStyleSheet para personalizar QMessageBox y otros diálogos.
# 13. Los errores críticos deben mostrarse en ventana modal, nunca solo en consola.
# 14. Los formularios y tablas deben tener suficiente espacio y no estar saturados.
# 15. El diseño debe ser minimalista, sin recargar de información ni colores innecesarios.
# --- FIN DE BASE DE MEJORES PRÁCTICAS ---

chequear_conexion_bd_gui()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Aplicar el stylesheet neumórfico global
    with open("mps/ui/assets/stylesheet.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    
    def start_main_window():
        main_window = MainWindow()
        main_window.show()
    
    splash = SplashScreen(message="Cargando módulos y base de datos...", duration=2200)
    splash.show_and_finish(start_main_window)
    sys.exit(app.exec())