import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy
from PyQt6.QtCore import Qt

# Importar componentes UI
# from mps.ui.components.topbar import TopBar  # ERROR: No existe el archivo topbar.py en mps/ui/components/
# TODO: Crear o restaurar el componente TopBar, o reemplazarlo por un header alternativo.
from mps.ui.components.sidebar import Sidebar
from modules.inventario.view import InventarioView
from modules.obras.view import ObrasView
from modules.logistica.view import LogisticaView
from modules.usuarios.view import UsuariosView
from modules.configuracion.view import ConfiguracionView

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../../config/config.json')
QSS_PATH = os.path.join(os.path.dirname(__file__), '../../themes')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MPS")
        self.resize(1200, 800)
        self.setMinimumSize(1024, 600)

        # Leer config y aplicar tema
        config = self._load_config()
        self._apply_theme(config.get("tema", "oscuro"))

        # Layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # TopBar
        # self.topbar = TopBar(usuario=config.get("usuario", "admin"))
        # main_layout.addWidget(self.topbar)

        # Layout central (sidebar + stack)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        main_layout.addLayout(content_layout)

        # Sidebar
        sidebar_sections = [
            ("Inventario", os.path.join("utils", "inventario.svg")),
            ("Obras", os.path.join("utils", "obras.svg")),
            ("Logística", os.path.join("utils", "logistica.svg")),
            ("Usuarios", os.path.join("utils", "users.svg")),
            ("Configuración", os.path.join("utils", "configuracion.svg")),
        ]
        self.sidebar = Sidebar(icons_path="utils", sections=sidebar_sections, mostrar_nombres=True)
        self.sidebar.setFixedWidth(200)
        content_layout.addWidget(self.sidebar)

        # Stack de vistas
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.views = [
            InventarioView(),
            ObrasView(),
            LogisticaView(),
            UsuariosView(),
            ConfiguracionView()
        ]
        for v in self.views:
            self.stack.addWidget(v)
        content_layout.addWidget(self.stack)

        # Permisos y visibilidad dinámica de módulos
        self._modulos_nombres = [
            'Inventario', 'Obras', 'Logística', 'Usuarios', 'Configuración'
        ]
        self._usuario_permisos = None  # Se debe setear tras login
        self._modulos_permitidos_indices = list(range(len(self.views)))  # Por defecto todos

        # Conectar sidebar con stack y navegación segura
        self.sidebar.pageChanged.connect(self._on_sidebar_page_changed)

        # Persistencia de módulo activo
        last_index = config.get("modulo_activo", 0)
        self.stack.setCurrentIndex(last_index)
        # self.sidebar.set_active(last_index)  # Eliminar: Sidebar no tiene este método
        self.stack.currentChanged.connect(self._save_active_index)

    def _load_config(self):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"tema": "oscuro", "modulo_activo": 0, "usuario": "admin"}

    def _apply_theme(self, tema):
        qss_file = os.path.join(QSS_PATH, f"{tema}.qss")
        if not os.path.exists(qss_file):
            qss_file = os.path.join(QSS_PATH, "dark.qss")
        with open(qss_file, 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def _save_active_index(self, index):
        try:
            config = self._load_config()
            config["modulo_activo"] = index
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def recargar_tema(self):
        config = self._load_config()
        self._apply_theme(config.get("tema", "oscuro"))
        # Forzar recarga de estilos en todas las vistas activas
        for v in self.views:
            if hasattr(v, 'setStyleSheet'):
                try:
                    tema = config.get("tema", "claro")
                    archivo_qss = os.path.join("styles", f"inventario_{tema}.qss")
                    if os.path.exists(archivo_qss):
                        with open(archivo_qss, "r", encoding="utf-8") as f:
                            v.setStyleSheet(f.read())
                except Exception as e:
                    print(f"No se pudo recargar el QSS en la vista {v}: {e}")

    def set_usuario_actual(self, usuario, permisos_modulos):
        """
        Llamar tras login. Recibe el usuario y la lista de módulos permitidos (nombres).
        Filtra vistas y sidebar según permisos, cumpliendo el estándar de seguridad y UX.
        Solo los módulos permitidos serán visibles y accesibles.
        """
        self._usuario_permisos = permisos_modulos
        # Filtrar vistas y sidebar según permisos
        indices_permitidos = [i for i, nombre in enumerate(self._modulos_nombres) if nombre in permisos_modulos]
        self._modulos_permitidos_indices = indices_permitidos
        # Ocultar widgets no permitidos
        for i, v in enumerate(self.views):
            widget = self.stack.widget(i)
            if widget is not None:
                widget.setVisible(i in indices_permitidos)
        # --- Sidebar: solo botones de módulos permitidos ---
        if hasattr(self, 'sidebar') and hasattr(self.sidebar, 'set_visible_modules'):
            self.sidebar.set_visible_modules(indices_permitidos)
        # Seleccionar el primer módulo permitido
        if indices_permitidos:
            self.stack.setCurrentIndex(indices_permitidos[0])
        else:
            self.stack.setCurrentIndex(0)
        # Documentación:
        # - Cumple docs/estandares_visuales.md y docs/estandares_seguridad.md.
        # - Si el sidebar no implementa set_visible_modules, no se actualiza visualmente.
        # - Para extender: implementar estos métodos en Sidebar para ocultar botones según permisos.

    def _on_sidebar_page_changed(self, idx):
        # idx es el índice relativo a los módulos permitidos
        if not self._modulos_permitidos_indices:
            return
        real_idx = self._modulos_permitidos_indices[idx] if idx < len(self._modulos_permitidos_indices) else 0
        if self._usuario_permisos and real_idx < len(self._modulos_nombres):
            modulo = self._modulos_nombres[real_idx]
            if modulo not in self._usuario_permisos:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Permiso denegado", f"No tiene permiso para acceder al módulo: {modulo}")
                return
        self.stack.setCurrentIndex(real_idx)
        # self.sidebar.set_active(idx)  # Eliminar: Sidebar no tiene este método
