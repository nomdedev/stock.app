import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy
from PyQt6.QtCore import Qt
import os, json

from mps.ui.components.topbar import TopBar
from mps.ui.components.sidebar import Sidebar
from mps.modules.inventario.view import InventarioView
from mps.modules.obras.view import ObrasView
from mps.modules.logistica.view import LogisticaView
from mps.modules.usuarios.view import UsuariosView
from mps.modules.configuracion.view import ConfiguracionView

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
        self.topbar = TopBar(usuario=config.get("usuario", "admin"))
        main_layout.addWidget(self.topbar)

        # Layout central (sidebar + stack)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        main_layout.addLayout(content_layout)

        # Sidebar
        self.sidebar = Sidebar()
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

        # Conectar sidebar con stack
        self.sidebar.set_main_stack(self.stack)

        # Persistencia de módulo activo
        last_index = config.get("modulo_activo", 0)
        self.stack.setCurrentIndex(last_index)
        self.sidebar.set_active(last_index)
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
