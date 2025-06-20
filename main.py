"""
# Para el estándar de inicialización robusto y el flujo recomendado de arranque, ver:
# docs/decisiones_main.md y docs/estandares_seguridad.md
#
# Para los principios de diseño UI/UX y buenas prácticas visuales, ver:
# docs/estandares_visuales.md
#
# Para detalles de logging, feedback y manejo de errores críticos, ver:
# docs/estandares_feedback.md y docs/estandares_logging.md
#
# Para reglas de seguridad y manejo de variables sensibles, ver:
# docs/estandares_seguridad.md
"""

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
#    - Sombra visual: NO usar box-shadow en QSS (no es soportado por Qt y genera warnings). Para sombras en botones, tarjetas y widgets usar SIEMPRE QGraphicsDropShadowEffect desde Python. Ejemplo estándar:
#        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
#        from PyQt6.QtGui import QColor
#        sombra = QGraphicsDropShadowEffect()
#        sombra.setBlurRadius(15)
#        sombra.setXOffset(0)
#        sombra.setYOffset(4)
#        sombra.setColor(QColor(0, 0, 0, 160))
#        widget.setGraphicsEffect(sombra)
#    - Documentar cualquier excepción visual en docs/estandares_visuales.md
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

import codecs
import sys
import subprocess
import os
import platform
import importlib.metadata as importlib_metadata  # Sustituye pkg_resources (deprecado)
from core.event_bus import event_bus

# Forzar la codificación de salida estándar a UTF-8 para evitar errores con caracteres Unicode.
# Solución compatible con Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Definir constantes para literales duplicados
MODULO_CONFIGURACION = "Configuración"
DB_DRIVER_SQL_SERVER = "ODBC Driver 17 for SQL Server"

# --- UTILIDAD PARA COMPARAR VERSIONES ---
def version_mayor_igual(version_actual, version_requerida):
    from packaging import version
    return version.parse(version_actual) >= version.parse(version_requerida)

# --- INSTALACIÓN AUTOMÁTICA DE DEPENDENCIAS CRÍTICAS (WHEELS) PARA TODA LA APP ---

def _ejecutar_comando_pip(args):
    try:
        subprocess.check_call([sys.executable, "-m", "pip"] + args)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR PIP] {e}")
        return False

def _instalar_wheel_local(paquete, wheel_url, wheel_filename):
    import urllib.request
    local_path = os.path.join(os.getcwd(), wheel_filename)
    try:
        print(f"[LOG 1.1.1] Descargando wheel para {paquete} desde {wheel_url}...")
        urllib.request.urlretrieve(wheel_url, local_path)
        if _ejecutar_comando_pip(["install", "--user", local_path]):
            print(f"[LOG 1.1.2] ✅ {paquete} instalado desde wheel.")
            return True
        return False
    except Exception as e:
        print(f"[LOG 1.1.3] ❌ Error descargando/instalando {paquete} desde wheel: {e}")
        return False
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

def _instalar_paquete_pip(paquete, version=None):
    target = f"{paquete}=={version}" if version else paquete
    print(f"[LOG 1.2.1] Instalando {target} con pip...")
    if _ejecutar_comando_pip(["install", "--user", target, "--prefer-binary"]):
        print(f"[LOG 1.2.2] ✅ {paquete} instalado.")
        return True
    print(f"[LOG 1.2.3] ❌ Error instalando {paquete}.")
    return False

def _instalar_dependencia_si_necesario(paquete, version, wheel_info=None):
    print(f"[LOG 1.3.1] Chequeando {paquete} {'>= ' + version if version else ''}...")
    try:
        actual = importlib_metadata.version(paquete)
        if version and not version_mayor_igual(actual, version):
            raise ValueError(f"Versión instalada {actual} < requerida {version}")
        print(f"[LOG 1.3.2] ✅ {paquete} ya está instalado y cumple versión.")
        return True
    except Exception:
        print(f"[LOG 1.3.3] ❌ {paquete} no está instalado o la versión es incorrecta. Intentando instalar...")
        if not _instalar_paquete_pip(paquete, version) and wheel_info:
            print(f"[LOG 1.3.4] Falló la instalación normal de {paquete}. Intentando con wheel...")
            return _instalar_wheel_local(paquete, wheel_info['url'], wheel_info['filename'])
        elif not wheel_info:
             return _instalar_paquete_pip(paquete, version) # Reintentar sin wheel si no hay info de wheel
    return False # Si llega aquí, algo falló

def _instalar_desde_requirements():
    print("[LOG 1.4.1] Instalando dependencias desde requirements.txt (excluyendo pandas y pyodbc)...")
    req_path = os.path.join(os.getcwd(), "requirements.txt")
    req_tmp_path = os.path.join(os.getcwd(), "requirements_tmp.txt")
    try:
        with open(req_path, "r", encoding="utf-8") as fin, open(req_tmp_path, "w", encoding="utf-8") as fout:
            for line in fin:
                if not (line.strip().startswith("pandas") or line.strip().startswith("pyodbc")):
                    fout.write(line)
        
        with open(req_tmp_path, "r", encoding="utf-8") as f:
            for line in f:
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith("#"): 
                    continue
                pkg_name_parts = line_stripped.split("==")
                pkg = pkg_name_parts[0]
                version_req = pkg_name_parts[1] if len(pkg_name_parts) > 1 else None
                _instalar_dependencia_si_necesario(pkg, version_req) # No usa wheel para estos
        print("[LOG 1.4.5] ✅ Verificación de dependencias de requirements.txt completada.")
    except Exception as e:
        print(f"[LOG 1.4.6] ❌ Error procesando requirements.txt: {e}")
    finally:
        if os.path.exists(req_tmp_path):
            os.remove(req_tmp_path)

def instalar_dependencias_criticas():
    print("[LOG 1.1] === INICIO DE CHEQUEO DE DEPENDENCIAS CRÍTICAS ===")
    py_version_short = f"{sys.version_info.major}{sys.version_info.minor}"
    arch = platform.architecture()[0]
    py_tag = f"cp{py_version_short}"
    win_tag = "win_amd64" if arch == "64bit" else "win32"
    
    url_base_wheels = "https://download.lfd.uci.edu/pythonlibs/archive/"
    
    dependencias_con_wheels = {
        "pandas": {"version": "2.2.2", "wheel_filename_template": "pandas-{version}-{py_tag}-{py_tag}-{win_tag}.whl"},
        "pyodbc": {"version": "5.0.1", "wheel_filename_template": "pyodbc-{version}-{py_tag}-{py_tag}-{win_tag}.whl"}
    }

    for paquete, info in dependencias_con_wheels.items():
        version = info["version"]
        wheel_filename = info["wheel_filename_template"].format(version=version, py_tag=py_tag, win_tag=win_tag)
        wheel_url = url_base_wheels + wheel_filename
        wheel_info = {"url": wheel_url, "filename": wheel_filename}
        _instalar_dependencia_si_necesario(paquete, version, wheel_info)

    _instalar_desde_requirements()
    print("[LOG 1.5] === FIN DE CHEQUEO DE DEPENDENCIAS CRÍTICAS ===")
        

# Ejecutar instalación automática antes de cualquier importación pesada o arranque de la app
def _verificar_e_instalar_dependencias():
    try:
        import pandas
        import pyodbc
    except ImportError:
        print("Instalando dependencias críticas automáticamente...")
        instalar_dependencias_criticas()

def chequear_dependencias(lista, tipo_log):
    faltantes = []
    for paquete, version in lista:
        try:
            actual = importlib_metadata.version(paquete)
            if version and not version_mayor_igual(actual, version):
                raise ValueError(f"Versión instalada {actual} < requerida {version}")
            print(f"{tipo_log} ✅ {paquete} presente y versión >= {version if version else ''}.", flush=True)
        except Exception:
            print(f"{tipo_log} ❌ {paquete} faltante o versión menor a la requerida.", flush=True)
            faltantes.append(f"{paquete}{' >= ' + version if version else ''}")
    return faltantes

def mostrar_mensaje_dependencias(titulo, mensaje, detalles, tipo="info"):
    from PyQt6.QtWidgets import QApplication
    import sys
    from core.feedback_dialog import FeedbackDialog
    app = QApplication.instance()
    app_creado = False
    if app is None:
        app = QApplication(sys.argv)
        app_creado = True
    dlg = FeedbackDialog(titulo, mensaje, detalles, tipo)
    dlg.exec()
    if app_creado:
        app.quit()

def manejar_dependencias_faltantes(faltantes_criticos, faltantes_secundarios):
    if faltantes_criticos or faltantes_secundarios:
        print("[LOG 2.3] Dependencias faltantes detectadas. Mostrando mensaje.", flush=True)
        mensaje = "No se puede iniciar la aplicación. Instala las siguientes dependencias críticas:" if faltantes_criticos else "La aplicación se iniciará, pero faltan dependencias secundarias. Algunas funciones pueden estar limitadas (exportar PDF, QR, gráficos, etc.):"
        detalles = "\n".join(faltantes_criticos + faltantes_secundarios)
        tipo = "error" if faltantes_criticos else "warning"
        mostrar_mensaje_dependencias(
            "Dependencias faltantes",
            mensaje,
            detalles,
            tipo
        )
        if faltantes_criticos:
            sys.exit(1)
    else:
        print("[LOG 2.5] ✅ Todas las dependencias críticas y secundarias están instaladas correctamente.", flush=True)

def verificar_dependencias():
    """
    Verifica si las dependencias críticas y secundarias están instaladas.
    Si falta una CRÍTICA (PyQt6, pandas, pyodbc), muestra un error y cierra.
    Si faltan secundarias, muestra advertencia visual pero permite iniciar la app.
    Ahora acepta versiones IGUALES O SUPERIORES a las requeridas.
    """
    requeridos_criticos = [
        ("PyQt6", "6.9.0"), ("pandas", "2.2.2"), ("pyodbc", "5.0.1")
    ]
    requeridos_secundarios = [
        ("reportlab", "4.4.0"), ("qrcode", "7.4.2"), ("matplotlib", "3.8.4"),
        ("pytest", "8.2.0"), ("pillow", "10.3.0"), ("python-dateutil", "2.9.0"),
        ("pytz", "2024.1"), ("tzdata", "2024.1"), ("openpyxl", "3.1.2"),
        ("colorama", "0.4.6"), ("ttkthemes", "3.2.2"), ("fpdf", None)
    ]
    print("[LOG 2.1] Chequeando dependencias críticas...", flush=True)
    faltantes_criticos = chequear_dependencias(requeridos_criticos, "[LOG 2.1.1]")
    print("[LOG 2.2] Chequeando dependencias secundarias...", flush=True)
    faltantes_secundarios = chequear_dependencias(requeridos_secundarios, "[LOG 2.2.1]")
    manejar_dependencias_faltantes(faltantes_criticos, faltantes_secundarios)
# Verificar e instalar dependencias críticas
_verificar_e_instalar_dependencias()
# Ahora verificar dependencias instaladas y requeridas
verificar_dependencias()
import os
# Refuerzo para evitar errores de OpenGL/Skia/Chromium en Windows
os.environ['QT_OPENGL'] = 'software'
os.environ['QT_QUICK_BACKEND'] = 'software'
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu --disable-software-rasterizer'

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, 
    QPushButton, QStackedWidget, QMessageBox
)
from PyQt6.QtGui import QPalette, QColor, QIcon
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize, QEvent
from utils.icon_loader import get_icon
from mps.ui.components.sidebar_moderno import Sidebar
from utils.theme_manager import aplicar_tema, cargar_modo_tema, set_theme
from core.config import DEFAULT_THEME
from functools import partial
import ctypes
import sys, os

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

# --- ORDEN LÓGICO DE MÓDULOS SEGÚN FLUJO DE NEGOCIO ---
svg_dir = os.path.join(os.path.dirname(__file__), 'resources', 'icons')
sidebar_sections = [
    ("Obras", os.path.join(svg_dir, 'obras.svg')),
    ("Inventario", os.path.join(svg_dir, 'inventario.svg')),
    ("Herrajes", os.path.join(svg_dir, 'herrajes.svg')),
    ("Vidrios", os.path.join(svg_dir, 'vidrios.svg')),
    ("Producción", os.path.join(svg_dir, 'produccion.svg')),
    ("Logística", os.path.join(svg_dir, 'logistica.svg')),
    ("Compras / Pedidos", os.path.join(svg_dir, 'compras.svg')),
    ("Contabilidad", os.path.join(svg_dir, 'contabilidad.svg')),
    ("Auditoría", os.path.join(svg_dir, 'auditoria.svg')),
    ("Mantenimiento", os.path.join(svg_dir, 'mantenimiento.svg')),
    ("Usuarios", os.path.join(svg_dir, 'users.svg')),
    (MODULO_CONFIGURACION, os.path.join(svg_dir, 'configuracion.svg'))
]
icon_map = {
    "Obras": "obras",
    "Inventario": "inventario",
    "Herrajes": "herrajes",
    "Vidrios": "vidrios",
    "Producción": "produccion",
    "Logística": "logistica",
    "Compras / Pedidos": "compras",
    "Contabilidad": "contabilidad",
    "Auditoría": "auditoria",
    "Mantenimiento": "mantenimiento",
    "Usuarios": "users",
    MODULO_CONFIGURACION: "configuracion"
}

# Clase principal
class MainWindow(QMainWindow):
    def __init__(self, usuario, modulos_permitidos):
        super().__init__()
        self._db_connections = {}
        self._models = {}
        self._views = {}
        self._controllers = {}
        # Inicializar modelos, vistas, controladores y layout principal
        self.logger = Logger()
        self._init_models()
        self._init_views_and_controllers(usuario)
        self._setup_main_layout()
        self._filter_modules_and_setup_sidebar(usuario, modulos_permitidos)
        self._connect_module_signals()
        self._integrate_order_status_in_works()
        self._setup_conexion_checker()

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=4000):
        """
        Muestra un mensaje temporal en la ventana principal.
        tipo: "info", "warning", "error", "success"
        duracion: milisegundos (por defecto 4000)
        """
        from PyQt6.QtWidgets import QMessageBox
        if tipo == "info":
            icon = QMessageBox.Icon.Information
        elif tipo == "warning":
            icon = QMessageBox.Icon.Warning
        elif tipo == "error":
            icon = QMessageBox.Icon.Critical
        elif tipo == "success":
            icon = QMessageBox.Icon.Information
        else:
            icon = QMessageBox.Icon.NoIcon
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setText(mensaje)
        msg_box.setWindowTitle("Mensaje")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        # Cerrar automáticamente después de 'duracion' ms
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(duracion, msg_box.accept)
        msg_box.exec()

    def actualizar_usuario_label(self, usuario):
        """
        Actualiza el label de usuario actual en la interfaz, si existe.
        """
        # Si tienes un label específico para mostrar el usuario, actualízalo aquí.
        # Por ejemplo, si tienes self.usuario_label:
        if hasattr(self, "usuario_label"):
            if isinstance(usuario, dict) and "usuario" in usuario and "rol" in usuario:
                self.usuario_label.setText(f"Usuario: {usuario['usuario']} ({usuario['rol']})")
            else:
                self.usuario_label.setText(f"Usuario: {str(usuario)}")

    def get_inventario_connection(self):
        if 'inventario' not in self._db_connections:
            db = DatabaseConnection()
            db.conectar_a_base("inventario")
            self._db_connections['inventario'] = db
        return self._db_connections['inventario']

    def get_usuarios_connection(self):
        if 'users' not in self._db_connections:
            db = DatabaseConnection()
            db.conectar_a_base("users")
            self._db_connections['users'] = db
        return self._db_connections['users']

    def get_auditoria_connection(self):
        if 'auditoria' not in self._db_connections:
            db = DatabaseConnection()
            db.conectar_a_base("auditoria")
            self._db_connections['auditoria'] = db
        return self._db_connections['auditoria']

    def get_configuracion_connection(self):
        # Si configuracion está en inventario, se reutiliza
        return self.get_inventario_connection()

    def get_pedidos_connection(self):
        # Si pedidos está en inventario, se reutiliza
        return self.get_inventario_connection()

    def get_produccion_connection(self):
        # Si producción está en inventario, se reutiliza
        return self.get_inventario_connection()

    def _init_models(self):
        self._models['inventario'] = InventarioModel(db_connection=self.get_inventario_connection())
        self._models['obras'] = ObrasModel(db_connection=self.get_inventario_connection())
        self._models['produccion'] = ProduccionModel(db_connection=self.get_produccion_connection())
        self._models['logistica'] = LogisticaModel(db_connection=self.get_inventario_connection())
        self._models['pedidos'] = PedidosModel(db_connection=self.get_pedidos_connection())
        self._models['configuracion'] = ConfiguracionModel(db_connection=self.get_configuracion_connection())
        self._models['herrajes'] = HerrajesModel(self.get_inventario_connection())
        self._models['usuarios'] = UsuariosModel(db_connection=self.get_usuarios_connection())
        self._models['auditoria'] = AuditoriaModel(db_connection=self.get_auditoria_connection())

    def _init_views_and_controllers(self, usuario):
        usuario_str = usuario['usuario'] if isinstance(usuario, dict) and 'usuario' in usuario else str(usuario)
        self._views['inventario'] = InventarioView(db_connection=self.get_inventario_connection(), usuario_actual=usuario_str)
        self._controllers['inventario'] = InventarioController(
            model=self._models['inventario'],
            view=self._views['inventario'],
            db_connection=self.get_inventario_connection(),
            usuario_actual=usuario
        )
        self._views['obras'] = ObrasView()
        self._controllers['obras'] = ObrasController(
            model=self._models['obras'], view=self._views['obras'], db_connection=self.get_inventario_connection(), usuarios_model=self._models['usuarios'], logistica_controller=None
        )
        self.obras_controller = self._controllers['obras']
        self._views['produccion'] = ProduccionView()
        self._controllers['produccion'] = ProduccionController(
            model=self._models['produccion'], view=self._views['produccion'], db_connection=self.get_produccion_connection()
        )
        self._views['logistica'] = LogisticaView()
        self._controllers['logistica'] = LogisticaController(
            model=self._models['logistica'], view=self._views['logistica'], db_connection=self.get_inventario_connection(), usuarios_model=self._models['usuarios']
        )
        self._controllers['obras'].logistica_controller = self._controllers['logistica']
        self._views['compras_pedidos'] = ComprasPedidosView()
        self._controllers['compras_pedidos'] = ComprasPedidosController(
            self._models['pedidos'], self._views['compras_pedidos'], self.get_pedidos_connection(), self._models['usuarios']
        )
        self._controllers['compras_pedidos'].cargar_pedidos()
        self._views['pedidos'] = PedidosIndependienteView()
        self._controllers['pedidos'] = PedidosController(self._views['pedidos'], self.get_pedidos_connection())
        self._views['usuarios'] = UsuariosView()
        self._controllers['usuarios'] = UsuariosController(
            model=self._models['usuarios'], view=self._views['usuarios'], db_connection=self.get_usuarios_connection()
        )
        self._views['auditoria'] = AuditoriaView()
        self._controllers['auditoria'] = AuditoriaController(
            model=self._models['auditoria'], view=self._views['auditoria'], db_connection=self.get_auditoria_connection()
        )
        self._views['configuracion'] = ConfiguracionView()
        self._controllers['configuracion'] = ConfiguracionController(
            model=self._models['configuracion'], view=self._views['configuracion'], db_connection=self.get_configuracion_connection(), usuarios_model=self._models['usuarios']
        )
        
        self.mantenimiento_view = MantenimientoView()
        from modules.mantenimiento.controller import MantenimientoController
        self.mantenimiento_controller = MantenimientoController(
            model=self.mantenimiento_view, view=self.mantenimiento_view, db_connection=self.get_inventario_connection(), usuarios_model=self._models['usuarios']
        )
        
        self.contabilidad_view = ContabilidadView()
        from modules.contabilidad.controller import ContabilidadController
        self.contabilidad_controller = ContabilidadController(
            model=self.contabilidad_view, view=self.contabilidad_view, db_connection=self.get_inventario_connection(), usuarios_model=self._models['usuarios']
        )
        
        self.herrajes_view = HerrajesView()
        self.herrajes_controller = HerrajesController(
            self._models['herrajes'], self.herrajes_view, db_connection=self.get_inventario_connection(), usuarios_model=self._models['usuarios']
        )
        
        from modules.vidrios.view import VidriosView
        from modules.vidrios.controller import VidriosController
        self.vidrios_view = VidriosView()
        self.vidrios_controller = VidriosController(
            model=self.vidrios_view, view=self.vidrios_view, db_connection=self.get_inventario_connection()
        )

    def _setup_main_layout(self):
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Crear un layout vertical para el área principal (usuario_label + module_stack)
        main_area_layout = QVBoxLayout()
        # Crear y agregar el label de usuario
        self.usuario_label = QLabel("Usuario: -")
        self.usuario_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.usuario_label.setStyleSheet("font-weight: 500; font-size: 13px; margin: 8px 0 8px 16px; color: #1e293b;")
        main_area_layout.addWidget(self.usuario_label)

        self.module_stack = QStackedWidget()
        
        # Agregar vistas al stack en el MISMO orden que sidebar_sections
        self.module_stack.addWidget(self._views['obras'])            # 0 Obras
        self.module_stack.addWidget(self._views['inventario'])       # 1 Inventario
        self.module_stack.addWidget(self._views['herrajes'])         # 2 Herrajes
        self.module_stack.addWidget(self._views['vidrios'])          # 3 Vidrios
        self.module_stack.addWidget(self._views['produccion'])       # 4 Producción
        self.module_stack.addWidget(self._views['logistica'])        # 5 Logística
        self.module_stack.addWidget(self._views['compras_pedidos'])  # 6 Compras / Pedidos
        self.module_stack.addWidget(self._views['contabilidad'])     # 7 Contabilidad
        self.module_stack.addWidget(self._views['auditoria'])        # 8 Auditoría
        self.module_stack.addWidget(self._views['mantenimiento'])    # 9 Mantenimiento
        self.module_stack.addWidget(self._views['usuarios'])         # 10 Usuarios
        self.module_stack.addWidget(self._views['configuracion'])    # 11 Configuración
        main_area_layout.addWidget(self.module_stack)

        main_layout.addLayout(main_area_layout)
        self._ajustar_sidebar() # Llamada inicial para ajustar el sidebar

    def _filter_modules_and_setup_sidebar(self, usuario, modulos_permitidos_param):
        modulos_a_usar = self._obtener_modulos_a_usar(usuario, modulos_permitidos_param)
        modulos_sidebar_originales = [nombre for nombre, _ in sidebar_sections]
        secciones_filtradas_sidebar, self.map_sidebar_idx_to_stack_idx = self._construir_secciones_sidebar(
            modulos_a_usar, modulos_sidebar_originales
        )

        if not secciones_filtradas_sidebar:
            secciones_filtradas_sidebar, self.map_sidebar_idx_to_stack_idx = self._manejar_sidebar_vacio(
                modulos_sidebar_originales
            )

        self._setup_sidebar_widget(secciones_filtradas_sidebar)

        initial_sidebar_idx_to_select, initial_stack_idx_to_select = self._determinar_indices_iniciales(
            modulos_a_usar, secciones_filtradas_sidebar, modulos_sidebar_originales
        )

        if secciones_filtradas_sidebar:
            self.sidebar.select_button_visually(initial_sidebar_idx_to_select)
            self.module_stack.setCurrentIndex(initial_stack_idx_to_select)
        else:
            self._mostrar_widget_error_stack()

        self.sidebar.setFocus()
        self.logger.info(f"[PERMISOS] Sidebar filtrado: {[n for n, _ in secciones_filtradas_sidebar]}")
        self.logger.info(f"[PERMISOS] Mapeo sidebar->stack: {self.map_sidebar_idx_to_stack_idx}")

    def _obtener_modulos_a_usar(self, usuario, modulos_permitidos_param):
        try:
            modulos_permitidos_obtenidos = self._models['usuarios'].obtener_modulos_permitidos(usuario)
            if not modulos_permitidos_obtenidos:
                self.logger.error(f"[PERMISOS] No se encontraron módulos permitidos para el usuario: {usuario}")
        except Exception as e:
            import traceback
            self.logger.error(f"[ERROR] Excepción al inicializar la UI: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Error crítico", f"Error al cargar la interfaz: {e}")
            self.close()
            return []
        modulos_a_usar = modulos_permitidos_param if isinstance(modulos_permitidos_param, list) else modulos_permitidos_obtenidos
        if not isinstance(modulos_a_usar, list):
            modulos_a_usar = []
        return modulos_a_usar

    def _construir_secciones_sidebar(self, modulos_a_usar, modulos_sidebar_originales):
        secciones_filtradas_sidebar = []
        map_sidebar_idx_to_stack_idx = []
        for i, nombre_modulo_sidebar in enumerate(modulos_sidebar_originales):
            if nombre_modulo_sidebar in modulos_a_usar:
                icon_name = icon_map.get(nombre_modulo_sidebar, "default_icon")
                if icon_name == "default_icon" and nombre_modulo_sidebar.lower().replace(" / ", "_").replace(" ", "_") != "default_icon":
                    generated_icon_name = nombre_modulo_sidebar.lower().replace(" / ", "_").replace(" ", "_")
                    icon_name = generated_icon_name
                secciones_filtradas_sidebar.append((nombre_modulo_sidebar, get_icon(icon_name)))
                map_sidebar_idx_to_stack_idx.append(i)
        return secciones_filtradas_sidebar, map_sidebar_idx_to_stack_idx

    def _manejar_sidebar_vacio(self, modulos_sidebar_originales):
        self.logger.warning("[PERMISOS] Usuario sin módulos permitidos. Mostrando solo Configuración.")
        secciones_filtradas_sidebar = [(MODULO_CONFIGURACION, get_icon(icon_map[MODULO_CONFIGURACION]))]
        try:
            idx_config = modulos_sidebar_originales.index(MODULO_CONFIGURACION)
            map_sidebar_idx_to_stack_idx = [idx_config]
        except ValueError:
            idx_fallback = len(modulos_sidebar_originales) - 1
            map_sidebar_idx_to_stack_idx = [idx_fallback]
            self.logger.error(f"[PERMISOS] Módulo '{MODULO_CONFIGURACION}' no encontrado en sidebar_sections para fallback.")
        return secciones_filtradas_sidebar, map_sidebar_idx_to_stack_idx

    def _setup_sidebar_widget(self, secciones_filtradas_sidebar):
        if hasattr(self, "sidebar"):
            self.sidebar.setParent(None)
            del self.sidebar
        central_widget = self.centralWidget()
        main_layout = central_widget.layout() # type: ignore
        if not main_layout:
            self.logger.error("[CRITICAL] main_layout no encontrado al configurar sidebar.")
            main_layout = QHBoxLayout()
            if central_widget:
                central_widget.setLayout(main_layout) # type: ignore
            main_layout.addWidget(self.module_stack)
        self.sidebar = Sidebar(sections=secciones_filtradas_sidebar, mostrar_nombres=True)
        main_layout.insertWidget(0, self.sidebar) # type: ignore

    def _determinar_indices_iniciales(self, modulos_a_usar, secciones_filtradas_sidebar, modulos_sidebar_originales):
        initial_sidebar_idx_to_select = 0
        initial_stack_idx_to_select = self.map_sidebar_idx_to_stack_idx[0] if self.map_sidebar_idx_to_stack_idx else 0
        if "Obras" in modulos_a_usar:
            try:
                obras_sidebar_idx = [s[0] for s in secciones_filtradas_sidebar].index("Obras")
                obras_stack_idx = modulos_sidebar_originales.index("Obras")
                if obras_stack_idx in self.map_sidebar_idx_to_stack_idx:
                    initial_sidebar_idx_to_select = obras_sidebar_idx
                    initial_stack_idx_to_select = obras_stack_idx
            except ValueError:
                self.logger.warning("[PERMISOS] Módulo 'Obras' permitido pero no encontrado en secciones filtradas/originales para selección inicial.")
        return initial_sidebar_idx_to_select, initial_stack_idx_to_select

    def _mostrar_widget_error_stack(self):
        self.logger.error("[PERMISOS] No hay módulos para mostrar después del filtrado.")
        error_label = QLabel("Error: No tiene módulos asignados o no se pudieron cargar.")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.module_stack.addWidget(error_label)
        self.module_stack.setCurrentIndex(self.module_stack.count() - 1)

    def _update_controllers_with_user(self, usuario):
        self._controllers['inventario'].usuario_actual = usuario
        self._controllers['obras'].usuario_actual = usuario
        self._controllers['produccion'].usuario_actual = usuario
        self._controllers['logistica'].usuario_actual = usuario
        self._controllers['compras_pedidos'].usuario_actual = usuario
        self._controllers['pedidos'].usuario_actual = usuario
        self._controllers['usuarios'].usuario_actual = usuario
        self._controllers['auditoria'].usuario_actual = usuario
        self._controllers['configuracion'].usuario_actual = usuario
        self.herrajes_controller.usuario_actual = usuario
        # self.vidrios_controller no tiene usuario_actual actualmente, si se necesita, añadirlo.

    def _connect_module_signals(self):
        if hasattr(self._views['obras'], 'obra_agregada'):
            if hasattr(self._controllers['inventario'], 'actualizar_por_obra'):
                self._views['obras'].obra_agregada.connect(self._controllers['inventario'].actualizar_por_obra)
            if hasattr(self.vidrios_controller, 'actualizar_por_obra'):
                self._views['obras'].obra_agregada.connect(self.vidrios_controller.actualizar_por_obra)
        
        if hasattr(self._controllers['inventario'], 'actualizar_por_pedido'):
            event_bus.pedido_actualizado.connect(self._controllers['inventario'].actualizar_por_pedido)
        if hasattr(self._controllers['obras'], 'actualizar_por_pedido'):
            event_bus.pedido_actualizado.connect(self._controllers['obras'].actualizar_por_pedido)
        
        if hasattr(self._controllers['inventario'], 'actualizar_por_pedido_cancelado'):
            event_bus.pedido_cancelado.connect(self._controllers['inventario'].actualizar_por_pedido_cancelado)
        if hasattr(self._controllers['obras'], 'actualizar_por_pedido_cancelado'):
            event_bus.pedido_cancelado.connect(self._controllers['obras'].actualizar_por_pedido_cancelado)
        
        if hasattr(self, 'sidebar'): # Asegurarse que el sidebar existe
            self.sidebar.pageChanged.connect(self._on_sidebar_page_changed)

    def _integrate_order_status_in_works(self):
        try:
            self.obras_controller.mostrar_estado_pedidos_en_tabla(
                inventario_controller=self._controllers['inventario'],
                vidrios_controller=self.vidrios_controller,
                herrajes_controller=self.herrajes_controller
            )
        except Exception as e:
            self.logger.error(f"[INTEGRACIÓN] Error al poblar estado de pedidos en Obras: {e}")

    def _on_sidebar_page_changed(self, sidebar_idx):
        # sidebar_idx es el índice dentro de las secciones_filtradas del sidebar.
        # Usar el mapeo para obtener el índice correcto en el module_stack original.
        if hasattr(self, 'map_sidebar_idx_to_stack_idx') and 0 <= sidebar_idx < len(self.map_sidebar_idx_to_stack_idx):
            stack_idx = self.map_sidebar_idx_to_stack_idx[sidebar_idx]
            if 0 <= stack_idx < self.module_stack.count():
                self.module_stack.setCurrentIndex(stack_idx)
                # Asegurar que el botón del sidebar también se actualice visualmente si el cambio no vino de un clic directo
                if hasattr(self, 'sidebar') and hasattr(self.sidebar, 'select_button_visually'):
                    self.sidebar.select_button_visually(sidebar_idx) # type: ignore
            else:
                self.logger.error(f"[NAV] Error: Índice de stack mapeado {stack_idx} fuera de rango.")
        else:
            self.logger.error(f"[NAV] Error: Índice de sidebar {sidebar_idx} fuera de rango en mapeo o mapeo no inicializado.")

    def showEvent(self, event):
        super().showEvent(event)
        self._ajustar_sidebar()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self._ajustar_sidebar()

    def _ajustar_sidebar(self):
        if hasattr(self, "sidebar"):
            if self.isMaximized() or self.isFullScreen():
                self.sidebar.setFixedWidth(160)
            else:
                self.sidebar.setFixedWidth(200)

    def _setup_conexion_checker(self):
        """
        Inicializa un QTimer que verifica el estado de la conexión a la base de datos periódicamente
        y actualiza el indicador visual del Sidebar.
        """
        self._estado_bd_online = True  # Estado inicial asumido
        self._timer_conexion = QTimer(self)
        self._timer_conexion.setInterval(15000)  # 15 segundos (ajustable)
        self._timer_conexion.timeout.connect(self.verificar_estado_conexion_bd)
        self._timer_conexion.start()
        # Chequeo inicial inmediato
        QTimer.singleShot(1000, self.verificar_estado_conexion_bd)

    def verificar_estado_conexion_bd(self):
        """
        Intenta una conexión rápida a la base de datos y actualiza el Sidebar.
        No bloquea la UI ni cierra la app si falla, solo actualiza el estado visual.
        """
        import pyodbc
        from core.config import DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_DEFAULT_DATABASE
        # La constante DB_DRIVER_SQL_SERVER ya está definida globalmente
        try:
            connection_string = (
                f"DRIVER={{{DB_DRIVER_SQL_SERVER}}};"
                f"SERVER={DB_SERVER};"
                f"DATABASE={DB_DEFAULT_DATABASE};"
                f"UID={DB_USERNAME};"
                f"PWD={DB_PASSWORD};"
                f"TrustServerCertificate=yes;"
            )
            # No se usa la variable conn, se puede quitar el with y el as conn
            pyodbc.connect(connection_string, timeout=3).close() # Cerrar conexión inmediatamente
            if not self._estado_bd_online:
                self.sidebar.set_estado_online(True)
                self._estado_bd_online = True
            return
        except Exception:
            if self._estado_bd_online:
                self.sidebar.set_estado_online(False)
                self._estado_bd_online = False
            # Aquí termina el manejo de excepción, no hay que concatenar ni repetir código
            return

def chequear_conexion_bd():
    import pyodbc
    # Puedes ajustar estos valores según tu configuración realonn, se puede quitar el with y el as conn
    # DB_DRIVER = os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server') # Usar constante global_string, timeout=5).close() # Cerrar conexión inmediatamente
    db_driver_local = os.environ.get('DB_DRIVER', DB_DRIVER_SQL_SERVER)
    DB_SERVER = os.environ.get('DB_SERVER', '')
    DB_DATABASE = os.environ.get('DB_DATABASE', 'inventario')
    DB_USERNAME = os.environ.get('DB_USERNAME', 'sa')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'tu_contraseña_aqui')
    try:
        connection_string = (
            f"DRIVER={{{db_driver_local}}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_DATABASE};"
            f"UID={DB_USERNAME};"
            f"PWD={DB_PASSWORD};"
            f"TrustServerCertificate=yes;"
        )
        # No se usa la variable conn, se puede quitar el with y el as conn
        pyodbc.connect(connection_string, timeout=5).close() # Cerrar conexión inmediatamente
        print("✅ Conexión exitosa a la base de datos.")
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        print("Verifica usuario, contraseña, servidor y que SQL Server acepte autenticación SQL.")
        sys.exit(1)

def chequear_conexion_bd_gui():
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from core.config import DB_SERVER, DB_SERVER_ALTERNATE, DB_USERNAME, DB_PASSWORD, DB_DEFAULT_DATABASE, DB_TIMEOUT
    import traceback
    servidores = [DB_SERVER, DB_SERVER_ALTERNATE]
    # print(f"[LOG 3.2] ✅ Conexión exitosa a la base de datos: {db_server_actual}")  # Esta línea se debe mover al lugar correcto si es necesario
    # Renombrar variable para cumplir convención
    for db_server_actual in servidores:
        try:
            print(f"[LOG 3.1] Intentando conexión a BD: {db_server_actual} ...")
            connection_string = (
                f"DRIVER={{{DB_DRIVER_SQL_SERVER}}};"
                f"SERVER={db_server_actual};"
                f"DATABASE={DB_DEFAULT_DATABASE};"
                f"UID={DB_USERNAME};"
                f"PWD={DB_PASSWORD};"
                f"TrustServerCertificate=yes;"
            )
            import pyodbc
            # No se usa la variable conn, se puede quitar el with y el as conn
            pyodbc.connect(connection_string, timeout=DB_TIMEOUT).close() # Cerrar conexión inmediatamente
            print(f"[LOG 3.2] ✅ Conexión exitosa a la base de datos: {db_server_actual}")
            return
        except Exception as e:
            print(f"[LOG 3.3] ❌ Error de conexión a la base de datos ({db_server_actual}): {e}\n{traceback.format_exc()}")
    print("[LOG 3.4] ❌ No se pudo conectar a ninguna base de datos. Mostrando error GUI.")
    # No es necesario crear una nueva instancia de QApplication si ya existe
    # app = QApplication.instance() or QApplication(sys.argv)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Error de conexión a la base de datos")
    msg.setText("❌ No se pudo conectar a la base de datos.")
    msg.setInformativeText(f"Verifica usuario, contraseña, servidor (puede ser IP o nombre) y que SQL Server acepte autenticación SQL.\n\nIntentado con: {DB_SERVER} y {DB_SERVER_ALTERNATE}")
    # El estilo visual de QMessageBox puede personalizarse con setStyleSheet SOLO aquí, si se requiere una excepción visual.
    msg.exec()
    sys.exit(1)

# --- DIAGNÓSTICO ROBUSTO DE ENTORNO Y DEPENDENCIAS ---amente. Versión: {pandas.__version__}")
def diagnostico_entorno_dependencias():
    import sys
    import os
    import traceback
    import datetime
    log_path = os.path.join(os.getcwd(), 'logs', 'diagnostico_dependencias.txt')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    def log(msg):
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.datetime.now().isoformat()} | {msg}\n")
    try:
        log("[DIAG 0] === INICIO DIAGNÓSTICO DE ENTORNO Y DEPENDENCIAS ===")
        log(f"[DIAG 1] sys.executable: {sys.executable}")
        log(f"[DIAG 2] sys.version: {sys.version}")
        log(f"[DIAG 3] sys.path: {sys.path}")
        try:
            import pandas
            log(f"[DIAG 4] pandas importado correctamente. Versión: {pandas.__version__}")
        except Exception as e:
            log(f"[DIAG 4] ❌ Error importando pandas: {e}\n{traceback.format_exc()}")
        try:
            import reportlab
            log("[DIAG 5] reportlab importado correctamente.")
        except Exception as e:
            log(f"[DIAG 5] ❌ Error importando reportlab: {e}\n{traceback.format_exc()}")
    except Exception as e:
        log(f"[DIAG ERROR] Excepción en diagnóstico: {e}\n{traceback.format_exc()}")
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
# 12. Siempre usar setStyleSheet para personalizar QMessageBox y otros diálogos (justificado y documentado).
# 13. Los errores críticos deben mostrarse en ventana modal, nunca solo en consola.
# 14. Los formularios y tablas deben tener suficiente espacio y no estar saturados.
# 15. El diseño debe ser minimalista, sin recargar de información ni colores innecesarios.
# --- FIN DE BASE DE MEJORES PRÁCTICAS ---

# === [AUDITORÍA UI/UX Y FEEDBACK MODAL ROBUSTO] ===
# [editado 07/06/2025]
# Se deja constancia de que TODOS los módulos principales (Obras, Inventario, Logística, Pedidos, Contabilidad, Usuarios/Roles, Auditoría, etc.)
# cumplen con los estándares de UI/UX, feedback modal robusto, accesibilidad, consistencia visual y cierre modal solo en éxito,
# según lo definido en docs/estandares_visuales.md, docs/estandares_feedback.md y los checklists:
#   - checklist_botones_accion.txt
#   - checklist_formularios_botones_ui.txt
# Cada formulario y botón principal ha sido validado, documentado y marcado como COMPLETO en los checklists.
# Se mantiene trazabilidad en README.md y docstrings de cada módulo.
# Cualquier excepción o personalización está justificada y documentada en los archivos de estándares.
# Esta sección se actualizará ante cualquier cambio relevante en la UI/UX o feedback de los módulos principales.
# === [FIN AUDITORÍA UI/UX Y FEEDBACK MODAL ROBUSTO] ===

# --- FLUJO ROBUSTO DE INICIALIZACIÓN DE LA APP ---
# 1. Diagnóstico de entorno y dependencias
from core.config import DEBUG_MODE, DEFAULT_THEME
from core.logger import Logger
from core.database import DatabaseConnection
from core.splash_screen import SplashScreen
from utils.theme_manager import set_theme
from PyQt6.QtWidgets import QApplication
import sys
import os

# 2. Inicialización de QApplication y SplashScreen
if __name__ == "__main__":
    print("[LOG 4.1] Iniciando QApplication...")
    app = QApplication(sys.argv)
    print("[LOG 4.2] Aplicando stylesheet global desde configuración...")
    set_theme(app, DEFAULT_THEME)
    print("[LOG 4.3] Mostrando SplashScreen...")
    splash = SplashScreen(message="Cargando módulos y base de datos...", duration=2200)
    # --- APLICAR TEMA AL SPLASHSCREEN ---
    # Detectar modo de tema desde config o theme_manager
    from utils.theme_manager import cargar_modo_tema
    modo_tema = cargar_modo_tema()  # 'light' o 'dark'
    qss_file = 'resources/qss/theme_dark.qss' if modo_tema == 'dark' else 'resources/qss/theme_light.qss'
    try:
        with open(qss_file, 'r', encoding='utf-8') as f:
            splash.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo QSS: {qss_file}")
    # --- MOSTRAR IMAGEN PERSONALIZADA EN SPLASHSCREEN ---
    # Si SplashScreen permite set_image, usarlo. Si no, modificar el widget para mostrar la imagen.
    try:
        splash.set_image('resources/icons/pantalla-carga.jpg')  # Imagen de carga actualizada
    except Exception:
        pass  # Si no existe el método, ignora
    splash.show()
    splash.fade_in.start()

    # 3. Verificar dependencias críticas y abortar si falta alguna
    chequear_conexion_bd_gui()

    # 4. Importar y mostrar LoginView solo si todo lo anterior fue exitoso
    from modules.usuarios.login_view import LoginView
    from modules.usuarios.login_controller import LoginController
    from modules.usuarios.model import UsuariosModel
    db_connection_usuarios = DatabaseConnection()
    db_connection_usuarios.conectar_a_base("users")
    usuarios_model = UsuariosModel(db_connection=db_connection_usuarios)
    login_view = LoginView()
    login_controller = LoginController(login_view, usuarios_model)

    def on_login_success():
        global main_window  # Mantener referencia global para evitar cierre inmediato
        user = login_controller.usuario_autenticado
        if not user:
            login_view.mostrar_error("Usuario o contraseña incorrectos.")
            return
        login_view.close()
        modulos_permitidos = usuarios_model.obtener_modulos_permitidos(user)
        main_window = MainWindow(user, modulos_permitidos)
        main_window.actualizar_usuario_label(user)
        main_window.mostrar_mensaje(f"Usuario actual: {user['usuario']} ({user['rol']})", tipo="info", duracion=4000)
        main_window.show()

    login_view.boton_login.clicked.connect(on_login_success)
    from PyQt6.QtCore import QTimer
    def cerrar_splash_y_mostrar_login():
        splash.close()
        QTimer.singleShot(0, login_view.show)
    splash.fade_out.finished.connect(cerrar_splash_y_mostrar_login)
    splash.fade_out.start()
    print("[LOG 4.10] QApplication loop iniciado.")
    sys.exit(app.exec())