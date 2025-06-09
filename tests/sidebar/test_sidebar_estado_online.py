import pytest
from PyQt6.QtWidgets import QApplication
from mps.ui.components.sidebar_moderno import Sidebar

def get_estado_label(sidebar):
    # Busca el QLabel del estado online/offline
    for child in sidebar.findChildren(type(sidebar.estado_label)):
        if child.objectName() in ("estadoOnline", "estadoOffline"):
            return child
    return None

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    return app

def test_sidebar_estado_online_offline(app):
    sidebar = Sidebar(sections=[], online=True)
    label = get_estado_label(sidebar)
    assert label is not None
    # Estado online
    sidebar.set_estado_online(True)
    assert label.objectName() == "estadoOnline"
    assert "Conectado" in label.toolTip()
    # El color de fondo debe ser verde (#22c55e)
    assert "#22c55e" in label.styleSheet() or "background" in label.styleSheet()
    # Estado offline
    sidebar.set_estado_online(False)
    assert label.objectName() == "estadoOffline"
    assert "Sin conexión" in label.toolTip()
    # El color de fondo debe ser rojo (#ef4444)
    assert "#ef4444" in label.styleSheet() or "background" in label.styleSheet()
