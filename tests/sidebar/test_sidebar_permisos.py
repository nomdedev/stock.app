import pytest
from PyQt6.QtWidgets import QApplication
from mps.ui.components.sidebar_moderno import Sidebar
from utils.icon_loader import get_icon

def _icon_cache_key(qicon):
    return qicon.cacheKey() if hasattr(qicon, 'cacheKey') else str(qicon)

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    return app

def test_sidebar_muestra_modulos_permitidos_admin(app):
    secciones = [
        ("Obras", get_icon("obras")),
        ("Inventario", get_icon("inventario")),
        ("Vidrios", get_icon("vidrios")),
        ("Usuarios", get_icon("usuarios")),
        ("Configuración", get_icon("configuracion")),
    ]
    sidebar = Sidebar(sections=secciones, mostrar_nombres=True)
    titulos_sidebar = [btn.text() for btn in sidebar._sidebar_buttons]
    iconos_sidebar = [btn.icon() for btn in sidebar._sidebar_buttons]
    # 1. Todos los módulos permitidos están
    for nombre, _ in secciones:
        assert nombre in titulos_sidebar
    # 2. No hay duplicados
    assert len(titulos_sidebar) == len(set(titulos_sidebar))
    # 3. Íconos correctos
    for idx, (_, icono) in enumerate(secciones):
        assert _icon_cache_key(iconos_sidebar[idx]) == _icon_cache_key(icono)
    # 4. Accesibilidad
    for btn in sidebar._sidebar_buttons:
        assert btn.accessibleName() is not None or btn.toolTip() != ""
    # 5. Señal pageChanged
    triggered = []
    sidebar.pageChanged.connect(lambda idx: triggered.append(idx))
    sidebar._sidebar_buttons[2].click()
    assert triggered and triggered[0] == 2
    # 6. Botones extra: Configuración, Logs, Ayuda
    extras = ["Configuración", "Logs", "Ayuda"]
    extras_presentes = [w.text() for w in sidebar.findChildren(type(sidebar._sidebar_buttons[0])) if w.text() in extras]
    for extra in extras:
        assert extra in extras_presentes
    # 7. Todos los botones tienen ícono
    for btn in sidebar._sidebar_buttons:
        assert not btn.icon().isNull(), f"El botón '{btn.text()}' no tiene ícono asignado"
    # 8. Íconos de extras correctos
    extras = [
        ("Configuración", get_icon("configuracion")),
        ("Logs", get_icon("logs")),
        ("Ayuda", get_icon("ayuda")),
    ]
    for extra_nombre, extra_icon in extras:
        btns = [w for w in sidebar.findChildren(type(sidebar._sidebar_buttons[0])) if w.text() == extra_nombre]
        assert btns, f"No se encontró el botón '{extra_nombre}'"
        for btn in btns:
            assert _icon_cache_key(btn.icon()) == _icon_cache_key(extra_icon), f"El ícono de '{extra_nombre}' no es el esperado"
    # 9. No hay íconos duplicados
    all_icons = [btn.icon().cacheKey() for btn in sidebar.findChildren(type(sidebar._sidebar_buttons[0]))]
    assert len(all_icons) == len(set(all_icons)), "Hay íconos duplicados en el sidebar"

def test_sidebar_muestra_modulos_permitidos_usuario(app):
    secciones = [
        ("Obras", get_icon("obras")),
        ("Inventario", get_icon("inventario")),
    ]
    sidebar = Sidebar(sections=secciones, mostrar_nombres=True)
    titulos_sidebar = [btn.text() for btn in sidebar._sidebar_buttons]
    assert "Obras" in titulos_sidebar
    assert "Inventario" in titulos_sidebar
    assert "Usuarios" not in titulos_sidebar
    assert "Configuración" in [w.text() for w in sidebar.findChildren(type(sidebar._sidebar_buttons[0]))]
    # No duplicados
    assert len(titulos_sidebar) == len(set(titulos_sidebar))
    # Accesibilidad
    for btn in sidebar._sidebar_buttons:
        assert btn.accessibleName() is not None or btn.toolTip() != ""

def test_sidebar_no_muestra_modulos_no_permitidos(app):
    secciones = []
    sidebar = Sidebar(sections=secciones, mostrar_nombres=True)
    titulos_sidebar = [btn.text() for btn in sidebar._sidebar_buttons]
    assert titulos_sidebar == []
    # No botones extra
    assert len(sidebar._sidebar_buttons) == 0
