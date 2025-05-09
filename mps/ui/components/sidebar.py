from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QStackedWidget
from components.sidebar_button import SidebarButton
from PyQt6.QtCore import Qt
import os

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(10)

        # Ruta base de íconos (puedes ajustar según tu estructura)
        icon_dir = os.path.join(os.path.dirname(__file__), '../../../utils')

        self.btn_inventario = SidebarButton("Inventario", os.path.join(icon_dir, "box.svg"))
        self.btn_obras = SidebarButton("Obras", os.path.join(icon_dir, "building.svg"))
        self.btn_logistica = SidebarButton("Logística", os.path.join(icon_dir, "truck.svg"))
        self.btn_usuarios = SidebarButton("Usuarios", os.path.join(icon_dir, "user.svg"))
        self.btn_configuracion = SidebarButton("Configuración", os.path.join(icon_dir, "settings.svg"))

        self.buttons = [
            self.btn_inventario,
            self.btn_obras,
            self.btn_logistica,
            self.btn_usuarios,
            self.btn_configuracion
        ]

        for btn in self.buttons:
            self.layout.addWidget(btn)

        # Spacer para empujar los botones hacia arriba
        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.main_stack = None
        self.set_active(0)  # Selección visual inicial

    def set_main_stack(self, main_stack: QStackedWidget):
        self.main_stack = main_stack
        self.btn_inventario.clicked.connect(lambda: self.set_active(0))
        self.btn_obras.clicked.connect(lambda: self.set_active(1))
        self.btn_logistica.clicked.connect(lambda: self.set_active(2))
        self.btn_usuarios.clicked.connect(lambda: self.set_active(3))
        self.btn_configuracion.clicked.connect(lambda: self.set_active(4))

    def set_active(self, index):
        if self.main_stack is not None:
            self.main_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.buttons):
            btn.setSelected(i == index)
