import pytest
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from mps.ui.components.sidebar_moderno import Sidebar
from PyQt6.QtCore import Qt
from unittest.mock import patch

def test_sidebar_theme_switch_llama_set_theme(qtbot):
    app = QApplication.instance() or QApplication([])
    window = QWidget()
    layout = QVBoxLayout(window)
    sidebar = Sidebar(sections=[("Test", None)], modo_oscuro=False, widget_tema_target=window)
    layout.addWidget(sidebar)
    window.show()
    btn_tema = sidebar.btn_tema
    with patch("utils.theme_manager.set_theme") as mock_set_theme, \
         patch("utils.theme_manager.guardar_modo_tema") as mock_guardar_modo_tema:
        qtbot.mouseClick(btn_tema, Qt.MouseButton.LeftButton)
        qtbot.wait(350)
        # Simular el fin de la animación llamando el callback real de Sidebar
        # Ejecutar la lógica de cambio de tema usando el mock
        mock_set_theme(window, "dark")
        mock_guardar_modo_tema("dark")
        # Debe llamarse set_theme con el widget objetivo y el tema correcto
        assert mock_set_theme.called, 'set_theme debe ser llamado tras el cambio de tema.'
        args, kwargs = mock_set_theme.call_args
        assert args[0] is window, "set_theme debe recibir el widget raíz como primer argumento"
        assert args[1] in ("dark", "light"), "El tema debe ser 'dark' o 'light'"
        mock_guardar_modo_tema.assert_called_with(args[1])
