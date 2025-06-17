import pytest
from PyQt6.QtWidgets import QApplication
from main import MainWindow

class DummyUser:
    def __getitem__(self, key):
        if key == 'usuario':
            return 'testuser'
        if key == 'rol':
            return 'admin'
        raise KeyError(key)
    def get(self, key, default=None):
        if key == 'rol':
            return 'admin'
        if key == 'usuario':
            return 'testuser'
        return default

def test_module_stack_and_sidebar_mapping(qtbot):
    # Simula todos los módulos permitidos
    usuario = DummyUser()
    modulos_permitidos = [
        "Obras", "Inventario", "Herrajes", "Vidrios", "Producción", "Logística",
        "Compras / Pedidos", "Contabilidad", "Auditoría", "Mantenimiento", "Usuarios", "Configuración"
    ]
    window = MainWindow(usuario, modulos_permitidos)
    qtbot.addWidget(window)
    # El orden esperado de vistas en el stack debe coincidir con el orden del sidebar
    for idx, (nombre, _) in enumerate(window.sidebar.sections):
        window.sidebar.pageChanged.emit(idx)
        # El widget actual del stack debe tener el mismo objectName o clase que el módulo
        widget = window.module_stack.currentWidget()
        # Validación robusta: el nombre de la clase del widget debe contener el nombre del módulo (ignorando acentos y mayúsculas)
        clase = widget.__class__.__name__.lower()
        nombre_mod = nombre.lower().replace(' / ', '').replace('í', 'i').replace('ó', 'o').replace('á', 'a').replace('é', 'e').replace('ú', 'u')
        assert nombre_mod[:5] in clase or nombre_mod.replace(' ', '')[:5] in clase, \
            f"El módulo '{nombre}' no carga la vista correcta: stack muestra {clase}"
