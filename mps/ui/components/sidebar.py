from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QStackedWidget
from components.sidebar_button import SidebarButton
from PyQt6.QtCore import Qt, pyqtSignal
import os

class Sidebar(QWidget):
    pageChanged = pyqtSignal(int)  # Señal para navegación segura
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

        self._visible_indices = list(range(len(self.buttons)))

    def set_main_stack(self, main_stack: QStackedWidget):
        self.main_stack = main_stack
        self.btn_inventario.clicked.connect(lambda: self._emit_page_changed(0))
        self.btn_obras.clicked.connect(lambda: self._emit_page_changed(1))
        self.btn_logistica.clicked.connect(lambda: self._emit_page_changed(2))
        self.btn_usuarios.clicked.connect(lambda: self._emit_page_changed(3))
        self.btn_configuracion.clicked.connect(lambda: self._emit_page_changed(4))

    def _emit_page_changed(self, idx):
        # idx es el índice real, pero solo emitir si está visible
        if idx in self._visible_indices:
            self.pageChanged.emit(self._visible_indices.index(idx))
        else:
            # Si el botón no está visible, no emitir
            pass

    def set_active(self, index):
        if self.main_stack is not None and index < len(self._visible_indices):
            real_idx = self._visible_indices[index]
            self.main_stack.setCurrentIndex(real_idx)
            for i, btn in enumerate(self.buttons):
                btn.set_activo(i == real_idx)

    def set_visible_modules(self, indices):
        """
        Recibe una lista de índices de módulos visibles (según permisos).
        Oculta o muestra los botones y actualiza la navegación.
        """
        self._visible_indices = indices
        for i, btn in enumerate(self.buttons):
            btn.setVisible(i in indices)
        # Seleccionar el primero visible por defecto
        if indices:
            self.set_active(0)
