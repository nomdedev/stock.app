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

import sys
import subprocess
import os
import platform
import importlib.metadata as importlib_metadata  # Sustituye pkg_resources (deprecado)
from core.event_bus import event_bus

# --- UTILIDAD PARA COMPARAR VERSIONES ---
def version_mayor_igual(version_actual, version_requerida):
    from packaging import version
    return version.parse(version_actual) >= version.parse(version_requerida)

# --- INSTALACIÓN AUTOMÁTICA DE DEPENDENCIAS CRÍTICAS (WHEELS) PARA TODA LA APP ---
def instalar_dependencias_criticas():
    import urllib.request
    print("[LOG 1.1] === INICIO DE CHEQUEO DE DEPENDENCIAS CRÍTICAS ===")
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"  # Ej: 311 para Python 3.11
    arch = platform.architecture()[0]
    py_tag = f"cp{py_version}"
    win_tag = "win_amd64" if arch == "64bit" else "win32"
    wheels = {
        "pandas": f"pandas-2.2.2-{py_tag}-{py_tag}-{win_tag}.whl",
        "pyodbc": f"pyodbc-5.0.1-{py_tag}-{py_tag}-{win_tag}.whl"
    }
    url_base = "https://download.lfd.uci.edu/pythonlibs/archive/"
    def instalar_wheel(paquete, wheel_file):
        url = url_base + wheel_file
        local_path = os.path.join(os.getcwd(), wheel_file)
        try:
            print(f"[LOG 1.1.1] Descargando e instalando wheel para {paquete} desde {url}...")
            urllib.request.urlretrieve(url, local_path)
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", local_path])
            os.remove(local_path)
            print(f"[LOG 1.1.2] ✅ {paquete} instalado desde wheel.")
            return True
        except Exception as e:
            print(f"[LOG 1.1.3] ❌ Error instalando {paquete} desde wheel: {e}")
            return False
    def instalar_dependencia(paquete, version):
        try:
            print(f"[LOG 1.2.1] Instalando {paquete}=={version} con pip...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", f"{paquete}=={version}", "--prefer-binary"])
            print(f"[LOG 1.2.2] ✅ {paquete} instalado normalmente.")
            return True
        except Exception as e:
            print(f"[LOG 1.2.3] ❌ Error instalando {paquete} normalmente: {e}")
            if paquete in wheels:
                return instalar_wheel(paquete, wheels[paquete])
            return False
    def instalar_dependencia_si_falta(paquete, version):
        print(f"[LOG 1.3.1] Chequeando {paquete} >= {version if version else ''}...")
        try:
            actual = importlib_metadata.version(paquete)
            if version and not version_mayor_igual(actual, version):
                raise Exception(f"Versión instalada {actual} < requerida {version}")
            print(f"[LOG 1.3.2] ✅ {paquete} ya está instalado y cumple versión.")
            return True
        except Exception:
            print(f"[LOG 1.3.3] ❌ {paquete} no está instalado o la versión es incorrecta. Intentando instalar...")
            return instalar_dependencia(paquete, version)
    requeridos = [("pandas", "2.2.2"), ("pyodbc", "5.0.1")]
    for paquete, version in requeridos:
        instalar_dependencia_si_falta(paquete, version)
    # Instalar el resto de requirements.txt, excluyendo pandas y pyodbc
    try:
        print("[LOG 1.4.1] Instalando el resto de dependencias desde requirements.txt (sin pandas ni pyodbc)...")
        req_path = os.path.join(os.getcwd(), "requirements.txt")
        req_tmp_path = os.path.join(os.getcwd(), "requirements_tmp.txt")
        with open(req_path, "r", encoding="utf-8") as fin, open(req_tmp_path, "w", encoding="utf-8") as fout:
            for line in fin:
                if not (line.strip().startswith("pandas") or line.strip().startswith("pyodbc")):
                    fout.write(line)
        # Leer requirements_tmp.txt y chequear cada paquete antes de instalar
        with open(req_tmp_path, "r", encoding="utf-8") as f:
            for line in f:
                pkg = line.strip().split("==")[0] if "==" in line else line.strip()
                if not pkg or pkg.startswith("#"): continue
                try:
                    actual = importlib_metadata.version(pkg)
                    print(f"[LOG 1.4.2] Chequeando {pkg}... versión instalada: {actual}")
                except Exception:
                    print(f"[LOG 1.4.4] ❌ {pkg} no está instalado. Instalando...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", line.strip()])
        os.remove(req_tmp_path)
        print("[LOG 1.4.5] ✅ Todas las dependencias instaladas correctamente.")
    except Exception as e:
        print(f"[LOG 1.4.6] ❌ Error instalando requirements.txt: {e}")
        print("Por favor, revisa los logs y ejecuta manualmente si es necesario.")
    print("[LOG 1.5] === FIN DE CHEQUEO DE DEPENDENCIAS CRÍTICAS ===")
        

# Ejecutar instalación automática antes de cualquier importación pesada o arranque de la app
def _verificar_e_instalar_dependencias():
    try:
        import pandas
        import pyodbc
    except ImportError:
        print("Instalando dependencias críticas automáticamente...")
        instalar_dependencias_criticas()

_verificar_e_instalar_dependencias()
verificar_dependencias()

def mostrar_mensaje_dependencias(titulo, texto, detalles, tipo="error"):
    from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QPushButton
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtCore import Qt
    app = QApplication.instance() or QApplication(sys.argv)
    dialog = QDialog()
    dialog.setWindowTitle(titulo)
    dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
    dialog.setFixedWidth(420)
    # Solo se permite setStyleSheet aquí para personalizar el diálogo de dependencias.
    # No usar setStyleSheet embebido en widgets individuales fuera de diálogos personalizadas o theme global.
    dialog.setStyleSheet(f"""
        QDialog {{
            background: #fff9f3;
            border-radius: 18px;
            border: 2px solid #e3e3e3;
        }}
        QLabel#titulo {{
            color: #2563eb;
            font-size: 18px;
            font-weight: bold;
            padding: 12px 0 0 0;
            qproperty-alignment: AlignCenter;
        }}
        QLabel#mensaje {{
            color: #1e293b;
            font-size: 14px;
            font-weight: 500;
            padding: 8px 0 0 0;
            qproperty-alignment: AlignCenter;
        }}
        QLabel#detalles {{
            color: {'#ef4444' if tipo=='error' else '#fbbf24'};
            font-size: 13px;
            font-weight: 500;
            background: {'#ffe5e5' if tipo=='error' else '#fef9c3'};
            border-radius: 10px;
            padding: 10px 16px;
            margin: 12px 0 0 0;
            qproperty-alignment: AlignCenter;
        }}
        QPushButton {{
            background: #2563eb;
            color: white;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            min-width: 100px;
            min-height: 32px;
            padding: 8px 24px;
            margin-top: 18px;
        }}
        QPushButton:hover {{
            background: #1e40af;
        }}
    """)
    layout = QVBoxLayout()
    # Ícono grande
    icon_label = QLabel()
    if tipo == "error":
        icon_label.setPixmap(QPixmap("resources/icons/reject.svg").scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    else:
        icon_label.setPixmap(QPixmap("resources/icons/warning.svg").scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(icon_label)
    # Título
    titulo_label = QLabel(titulo)
    titulo_label.setObjectName("titulo")
    layout.addWidget(titulo_label)
    # Mensaje principal
    mensaje_label = QLabel(texto)
    mensaje_label.setObjectName("mensaje")
    mensaje_label.setWordWrap(True)
    layout.addWidget(mensaje_label)
    # Detalles (lista de dependencias)
    detalles_label = QLabel(detalles)
    detalles_label.setObjectName("detalles")
    detalles_label.setWordWrap(True)
    layout.addWidget(detalles_label)
    # Botón de cierre
    btn = QPushButton("Cerrar")
    btn.clicked.connect(dialog.accept)
    layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
    dialog.setLayout(layout)
    dialog.exec()

def verificar_dependencias():
    """
    Verifica si las dependencias críticas y secundarias están instaladas.
    Si falta una CRÍTICA (PyQt6, pandas, pyodbc), muestra un error y cierra.
    Si faltan secundarias, muestra advertencia visual pero permite iniciar la app.
    Ahora acepta versiones IGUALES O SUPERIORES a las requeridas.
    """
    from PyQt6.QtWidgets import QApplication
    requeridos_criticos = [
        ("PyQt6", "6.9.0"), ("pandas", "2.2.2"), ("pyodbc", "5.0.1")
    ]
    requeridos_secundarios = [
        ("reportlab", "4.4.0"), ("qrcode", "7.4.2"), ("matplotlib", "3.8.4"),
        ("pytest", "8.2.0"), ("pillow", "10.3.0"), ("python-dateutil", "2.9.0"),
        ("pytz", "2024.1"), ("tzdata", "2024.1"), ("openpyxl", "3.1.2"),
        ("colorama", "0.4.6"), ("ttkthemes", "3.2.2"), ("fpdf", None)
    ]
    faltantes_criticos = []
    faltantes_secundarios = []
    print("[LOG 2.1] Chequeando dependencias críticas...", flush=True)
    for paquete, version in requeridos_criticos:
        try:
            actual = importlib_metadata.version(paquete)
            if version and not version_mayor_igual(actual, version):
                raise Exception(f"Versión instalada {actual} < requerida {version}")
            print(f"[LOG 2.1.1] ✅ {paquete} presente y versión >= {version if version else ''}.", flush=True)
        except Exception:
            print(f"[LOG 2.1.2] ❌ {paquete} faltante o versión menor a la requerida.", flush=True)
            faltantes_criticos.append(f"{paquete}{' >= ' + version if version else ''}")
    print("[LOG 2.2] Chequeando dependencias secundarias...", flush=True)
    for paquete, version in requeridos_secundarios:
        try:
            actual = importlib_metadata.version(paquete)
            if version and not version_mayor_igual(actual, version):
                raise Exception(f"Versión instalada {actual} < requerida {version}")
            print(f"[LOG 2.2.1] ✅ {paquete} presente.", flush=True)
        except Exception:
            print(f"[LOG 2.2.2] ❌ {paquete} faltante.", flush=True)
            faltantes_secundarios.append(f"{paquete}{' >= ' + version if version else ''}")
    if faltantes_criticos:
        print("[LOG 2.3] Dependencias críticas faltantes. Mostrando mensaje y abortando.", flush=True)
        mostrar_mensaje_dependencias(
            "Faltan dependencias críticas",
            "No se puede iniciar la aplicación. Instala las siguientes dependencias críticas:",
            "\n".join(faltantes_criticos),
            tipo="error"
        )
        sys.exit(1)
    elif faltantes_secundarios:
        print("[LOG 2.4] Dependencias secundarias faltantes. Mostrando advertencia.", flush=True)
        mostrar_mensaje_dependencias(
            "Dependencias opcionales faltantes",
            "La aplicación se iniciará, pero faltan dependencias secundarias. Algunas funciones pueden estar limitadas (exportar PDF, QR, gráficos, etc.):",
            "\n".join(faltantes_secundarios),
            tipo="warning"
        )
    else:
        print("[LOG 2.5] ✅ Todas las dependencias críticas y secundarias están instaladas correctamente.", flush=True)

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
    ("Configuración", os.path.join(svg_dir, 'configuracion.svg'))
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
    "Configuración": "configuracion"
}

# Clase principal
class MainWindow(QMainWindow):
    def __init__(self, usuario, modulos_permitidos):
        super().__init__()
        from PyQt6.QtWidgets import QStatusBar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self.logger = Logger()
        self.logger.info("Aplicación iniciada")
        self.setWindowTitle("MPS Inventario App")
        self.resize(1280, 720)
        self.setMinimumSize(1024, 600)
        self.usuario_actual = usuario
        self.modulos_permitidos = modulos_permitidos
        self.usuario_label = QLabel()
        self.usuario_label.setObjectName("usuarioActualLabel")
        # El estilo visual de usuario_label se gestiona por QSS de theme global. No usar setStyleSheet aquí.
        self.usuario_label.setText("")
        self._status_bar.addPermanentWidget(self.usuario_label, 1)
        self.initUI(usuario, modulos_permitidos)

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=4000):
        colores = {
            "info": "#2563eb",
            "exito": "#22c55e",
            "advertencia": "#fbbf24",
            "error": "#ef4444"
        }
        color = colores.get(tipo, "#2563eb")
        # El estilo visual del status bar se gestiona por QSS de theme global. No usar setStyleSheet aquí.
        self._status_bar.showMessage(mensaje, duracion)
        if tipo == "error":
            QMessageBox.critical(self, "Error", mensaje)
        elif tipo == "advertencia":
            QMessageBox.warning(self, "Advertencia", mensaje)
        elif tipo == "exito":
            QMessageBox.information(self, "Éxito", mensaje)

    def actualizar_usuario_label(self, usuario):
        rol = usuario.get('rol', '').lower()
        colores = {
            'admin': '#2563eb',
            'supervisor': '#fbbf24',
            'usuario': '#22c55e'
        }
        color = colores.get(rol, '#1e293b')
        # El estilo visual de usuario_label se gestiona por QSS de theme global. No usar setStyleSheet aquí.
        self.usuario_label.setText(f"Usuario: {usuario['usuario']} ({usuario['rol']})")

    def initUI(self, usuario=None, modulos_permitidos=None):
        # Crear conexiones persistentes a las bases de datos (una sola instancia por base)
        self.db_connection_inventario = DatabaseConnection()
        self.db_connection_inventario.conectar_a_base("inventario")
        self.db_connection_usuarios = DatabaseConnection()
        self.db_connection_usuarios.conectar_a_base("users")
        self.db_connection_auditoria = DatabaseConnection()
        self.db_connection_auditoria.conectar_a_base("auditoria")
        self.db_connection_pedidos = self.db_connection_inventario
        self.db_connection_configuracion = self.db_connection_inventario
        self.db_connection_produccion = self.db_connection_inventario

        # Crear instancias de modelos
        self.inventario_model = InventarioModel(db_connection=self.db_connection_inventario)
        self.inventario_model.actualizar_qr_y_campos_por_descripcion()
        self.obras_model = ObrasModel(db_connection=self.db_connection_inventario)
        self.produccion_model = ProduccionModel(db_connection=self.db_connection_produccion)
        self.logistica_model = LogisticaModel(db_connection=self.db_connection_inventario)
        self.pedidos_model = PedidosModel(db_connection=self.db_connection_pedidos)
        self.configuracion_model = ConfiguracionModel(db_connection=self.db_connection_configuracion)
        self.herrajes_model = HerrajesModel(self.db_connection_inventario)
        self.usuarios_model = UsuariosModel(db_connection=self.db_connection_usuarios)
        self.usuarios_model.crear_usuarios_iniciales()

        # Crear vistas y controladores principales
        usuario_str = usuario['usuario'] if isinstance(usuario, dict) and 'usuario' in usuario else str(usuario)
        self.inventario_view = InventarioView(db_connection=self.db_connection_inventario, usuario_actual=usuario_str)
        self.inventario_controller = InventarioController(
            model=self.inventario_model,
            view=self.inventario_view,
            db_connection=self.db_connection_inventario,
            usuario_actual=usuario  # Asegura que usuario_actual se propague correctamente
        )
        self.obras_view = ObrasView()
        # Inyectar el controller en la vista para acceso robusto desde el botón de alta
        self.obras_controller = ObrasController(
            model=self.obras_model, view=self.obras_view, db_connection=self.db_connection_inventario, usuarios_model=self.usuarios_model, logistica_controller=None
        )
        self.obras_view.set_controller(self.obras_controller)
        self.produccion_view = ProduccionView()
        self.produccion_controller = ProduccionController(
            model=self.produccion_model, view=self.produccion_view, db_connection=self.db_connection_produccion
        )
        self.logistica_view = LogisticaView()
        self.logistica_controller = LogisticaController(
            model=self.logistica_model, view=self.logistica_view, db_connection=self.db_connection_inventario, usuarios_model=self.usuarios_model
        )
        self.obras_controller.logistica_controller = self.logistica_controller
        self.compras_pedidos_view = ComprasPedidosView()
        self.compras_pedidos_controller = ComprasPedidosController(
            self.pedidos_model, self.compras_pedidos_view, self.db_connection_pedidos, self.usuarios_model
        )
        self.compras_pedidos_controller.cargar_pedidos()
        self.pedidos_view = PedidosIndependienteView()
        self.pedidos_controller = PedidosController(self.pedidos_view, self.db_connection_pedidos)
        self.usuarios_controller = UsuariosController(
            model=self.usuarios_model, view=None, db_connection=self.db_connection_usuarios
        )
        self.usuarios_view = UsuariosView()
        self.usuarios_controller.view = self.usuarios_view
        self.auditoria_view = AuditoriaView()
        self.auditoria_model = AuditoriaModel(db_connection=self.db_connection_auditoria)
        self.auditoria_controller = AuditoriaController(
            model=self.auditoria_model, view=self.auditoria_view, db_connection=self.db_connection_auditoria
        )
        self.configuracion_view = ConfiguracionView()
        self.configuracion_controller = ConfiguracionController(
            model=self.configuracion_model, view=self.configuracion_view, db_connection=self.db_connection_configuracion, usuarios_model=self.usuarios_model
        )
        self.mantenimiento_view = MantenimientoView()
        from modules.mantenimiento.controller import MantenimientoController
        self.mantenimiento_controller = MantenimientoController(
            model=self.mantenimiento_view, view=self.mantenimiento_view, db_connection=self.db_connection_inventario, usuarios_model=self.usuarios_model
        )
        self.contabilidad_view = ContabilidadView()
        from modules.contabilidad.controller import ContabilidadController
        self.contabilidad_controller = ContabilidadController(
            model=self.contabilidad_view, view=self.contabilidad_view, db_connection=self.db_connection_inventario, usuarios_model=self.usuarios_model
        )
        self.herrajes_view = HerrajesView()
        self.herrajes_controller = HerrajesController(
            self.herrajes_model, self.herrajes_view, db_connection=self.db_connection_inventario, usuarios_model=self.usuarios_model
        )
        from modules.vidrios.view import VidriosView
        from modules.vidrios.controller import VidriosController
        self.vidrios_view = VidriosView()
        self.vidrios_controller = VidriosController(
            model=self.vidrios_view, view=self.vidrios_view, db_connection=self.db_connection_inventario
        )

        # Layout principal
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.module_stack = QStackedWidget()
        # Agregar vistas al stack en el MISMO orden que sidebar_sections
        self.module_stack.addWidget(self.obras_view)            # 0 Obras
        self.module_stack.addWidget(self.inventario_view)       # 1 Inventario
        self.module_stack.addWidget(self.herrajes_view)         # 2 Herrajes
        self.module_stack.addWidget(self.vidrios_view)          # 3 Vidrios
        self.module_stack.addWidget(self.produccion_view)       # 4 Producción
        self.module_stack.addWidget(self.logistica_view)        # 5 Logística
        self.module_stack.addWidget(self.compras_pedidos_view)  # 6 Compras / Pedidos
        self.module_stack.addWidget(self.contabilidad_view)     # 7 Contabilidad
        self.module_stack.addWidget(self.auditoria_view)        # 8 Auditoría
        self.module_stack.addWidget(self.mantenimiento_view)    # 9 Mantenimiento
        self.module_stack.addWidget(self.usuarios_view)         # 10 Usuarios
        self.module_stack.addWidget(self.configuracion_view)    # 11 Configuración
        main_layout.addWidget(self.module_stack)
        self._ajustar_sidebar()

        # --- FILTRADO ROBUSTO Y DOCUMENTADO DE MÓDULOS EN SIDEBAR Y STACK PRINCIPAL ---
        # 1. Obtener módulos permitidos para el usuario actual (según permisos_modulos)
        # ATENCIÓN: obtener_modulos_permitidos debe estar implementado y accesible en UsuariosModel
        try:
            modulos_permitidos = self.usuarios_model.obtener_modulos_permitidos(usuario)
            if not modulos_permitidos:
                self.logger.error(f"[PERMISOS] No se encontraron módulos permitidos para el usuario: {usuario}")
        except Exception as e:
            import traceback
            self.logger.error(f"[ERROR] Excepción al inicializar la UI: {e}\n{traceback.format_exc()}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error crítico", f"Error al cargar la interfaz: {e}")
            self.close()
        # 2. Filtrar secciones del sidebar y widgets del stack según permisos
        if not isinstance(modulos_permitidos, list):
            modulos_permitidos = []
        secciones_filtradas = []
        indices_permitidos = []
        modulos_sidebar = [nombre for nombre, _ in sidebar_sections]
        for i, nombre in enumerate(modulos_sidebar):
            if nombre in modulos_permitidos:
                icon_name = icon_map.get(nombre, nombre.lower().replace(" / ", "_").replace(" ", "_"))
                secciones_filtradas.append((nombre, get_icon(icon_name)))
                indices_permitidos.append(i)
        # 3. Filtrar secciones y sincronizar con el stack
        # 4. Si no hay módulos permitidos, mostrar mensaje y fallback seguro
        if not secciones_filtradas:
            self.logger.warning(f"[PERMISOS] Usuario sin módulos permitidos. Mostrando solo Configuración.")
            secciones_filtradas = [("Configuración", get_icon(icon_map["Configuración"]))]
            indices_permitidos = [0]
        # 5. Recrear el sidebar con los módulos filtrados
        # Eliminar sidebar anterior si existe antes de agregar el nuevo
        if hasattr(self, "sidebar"):
            self.sidebar.setParent(None)
            del self.sidebar
        self.sidebar = Sidebar(sections=secciones_filtradas, mostrar_nombres=True)
        main_layout.insertWidget(0, self.sidebar)
        # 6. Seleccionar el primer módulo permitido como vista inicial (priorizando 'Obras' si está permitido)
        index_obras = None
        if modulos_permitidos and isinstance(modulos_permitidos, list) and "Obras" in modulos_permitidos:
            # Buscar el índice de 'Obras' en el sidebar filtrado
            for idx, (nombre, _) in enumerate(secciones_filtradas):
                if nombre == "Obras":
                    index_obras = idx
                    break
        if index_obras is not None:
            self.module_stack.setCurrentIndex(index_obras)
        elif indices_permitidos:
            self.module_stack.setCurrentIndex(indices_permitidos[0])
        else:
            self.module_stack.setCurrentIndex(0)
        # 7. Accesibilidad: enfocar el sidebar tras el filtrado
        self.sidebar.setFocus()
        # 8. Documentación y log para diagnóstico
        self.logger.info(f"[PERMISOS] Sidebar filtrado: {[n for n, _ in secciones_filtradas]}")
        # --- FIN FILTRADO ROBUSTO DE MÓDULOS ---

        # Pasar usuario_actual a los controladores
        self.inventario_controller.usuario_actual = usuario
        self.obras_controller.usuario_actual = usuario
        self.produccion_controller.usuario_actual = usuario
        self.logistica_controller.usuario_actual = usuario
        self.compras_pedidos_controller.usuario_actual = usuario
        self.pedidos_controller.usuario_actual = usuario
        self.usuarios_controller.usuario_actual = usuario
        self.auditoria_controller.usuario_actual = usuario
        self.configuracion_controller.usuario_actual = usuario
        self.herrajes_controller.usuario_actual = usuario

        # INTEGRACIÓN EN TIEMPO REAL ENTRE MÓDULOS (Obras, Inventario, Vidrios, Pedidos)
        # Conectar la señal obra_agregada de ObrasView a los controladores de Inventario y Vidrios
        if hasattr(self.obras_view, 'obra_agregada'):
            if hasattr(self.inventario_controller, 'actualizar_por_obra'):
                self.obras_view.obra_agregada.connect(self.inventario_controller.actualizar_por_obra)
            if hasattr(self.vidrios_controller, 'actualizar_por_obra'):
                self.obras_view.obra_agregada.connect(self.vidrios_controller.actualizar_por_obra)
        # Conectar la señal pedido_actualizado del event_bus a los controladores de Obras e Inventario
        if hasattr(self.inventario_controller, 'actualizar_por_pedido'):
            event_bus.pedido_actualizado.connect(self.inventario_controller.actualizar_por_pedido)
        if hasattr(self.obras_controller, 'actualizar_por_pedido'):
            event_bus.pedido_actualizado.connect(self.obras_controller.actualizar_por_pedido)
        # Conectar la señal pedido_cancelado del event_bus a los controladores de Obras e Inventario
        if hasattr(self.inventario_controller, 'actualizar_por_pedido_cancelado'):
            event_bus.pedido_cancelado.connect(self.inventario_controller.actualizar_por_pedido_cancelado)
        if hasattr(self.obras_controller, 'actualizar_por_pedido_cancelado'):
            event_bus.pedido_cancelado.connect(self.obras_controller.actualizar_por_pedido_cancelado)
        # Conectar la señal pageChanged del sidebar al cambio de vista en el stack
        self.sidebar.pageChanged.connect(self._on_sidebar_page_changed)

        # --- INTEGRACIÓN VISUAL DE ESTADO DE PEDIDOS EN OBRAS ---
        # Al inicializar la UI, poblar la tabla de obras con el estado de pedidos de Inventario, Vidrios y Herrajes
        try:
            self.obras_controller.mostrar_estado_pedidos_en_tabla(
                inventario_controller=self.inventario_controller,
                vidrios_controller=self.vidrios_controller,
                herrajes_controller=self.herrajes_controller
            )
        except Exception as e:
            self.logger.error(f"[INTEGRACIÓN] Error al poblar estado de pedidos en Obras: {e}")

    def _on_sidebar_page_changed(self, idx):
        self.module_stack.setCurrentIndex(idx)

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
        DB_DRIVER = 'ODBC Driver 17 for SQL Server'
        try:
            connection_string = (
                f"DRIVER={{{DB_DRIVER}}};"
                f"SERVER={DB_SERVER};"
                f"DATABASE={DB_DEFAULT_DATABASE};"
                f"UID={DB_USERNAME};"
                f"PWD={DB_PASSWORD};"
                f"TrustServerCertificate=yes;"
            )
            with pyodbc.connect(connection_string, timeout=3):
                if not self._estado_bd_online:
                    self.sidebar.set_estado_online(True)
                    self._estado_bd_online = True
                return
        except Exception:
            if self._estado_bd_online:
                self.sidebar.set_estado_online(False)
                self._estado_bd_online = False
        # No mostrar mensajes ni cerrar la app aquí, solo actualizar el círculo visual

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
    from core.config import DB_SERVER, DB_SERVER_ALTERNATE, DB_USERNAME, DB_PASSWORD, DB_DEFAULT_DATABASE, DB_TIMEOUT
    DB_DRIVER = 'ODBC Driver 17 for SQL Server'
    servidores = [DB_SERVER, DB_SERVER_ALTERNATE]
    for DB_SERVER_ACTUAL in servidores:
        try:
            print(f"[LOG 3.1] Intentando conexión a BD: {DB_SERVER_ACTUAL} ...")
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
                print(f"[LOG 3.2] ✅ Conexión exitosa a la base de datos: {DB_SERVER_ACTUAL}")
                return
        except Exception as e:
            print(f"[LOG 3.3] ❌ Error de conexión a la base de datos ({DB_SERVER_ACTUAL}): {e}")
    print("[LOG 3.4] ❌ No se pudo conectar a ninguna base de datos. Mostrando error GUI.")
    app = QApplication.instance() or QApplication(sys.argv)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Error de conexión a la base de datos")
    msg.setText("❌ No se pudo conectar a la base de datos.")
    msg.setInformativeText(f"Verifica usuario, contraseña, servidor (puede ser IP o nombre) y que SQL Server acepte autenticación SQL.\n\nIntentado con: {DB_SERVER} y {DB_SERVER_ALTERNATE}")
    # El estilo visual de QMessageBox puede personalizarse con setStyleSheet SOLO aquí, si se requiere una excepción visual.
    msg.exec()
    sys.exit(1)

# --- DIAGNÓSTICO ROBUSTO DE ENTORNO Y DEPENDENCIAS ---
def diagnostico_entorno_dependencias():
    import sys, os, traceback
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
            log(f"[DIAG 5] reportlab importado correctamente. Versión: {reportlab.__version__}")
        except Exception as e:
            log(f"[DIAG 5] ❌ Error importando reportlab: {e}\n{traceback.format_exc()}")
        log("[DIAG 6] === FIN DIAGNÓSTICO ===")
    except Exception as e:
        print("Ocurrió un error crítico. Consulta logs/diagnostico_dependencias.txt para más detalles y pasos de diagnóstico.")
        log(f"[DIAG 7] ❌ Error inesperado en diagnóstico: {e}\n{traceback.format_exc()}")
        sys.exit(1)

# Solo ejecutar diagnóstico si falla la importación de dependencias críticas
try:
    import pandas
    import reportlab
except ImportError:
    diagnostico_entorno_dependencias()

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
    if modo_tema == 'dark':
        splash.setStyleSheet(open('resources/qss/theme_dark.qss', encoding='utf-8').read())
    else:
        splash.setStyleSheet(open('resources/qss/theme_light.qss', encoding='utf-8').read())
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