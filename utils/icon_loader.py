import os
from PyQt6.QtGui import QIcon

_icon_cache = {}

def get_icon(name: str) -> QIcon:
    """
    Busca en resources/icons/<name>.svg o <name>.png.
    Devuelve un QIcon válido o un QIcon() vacío si no se encuentra.
    Usa caché interna para que cada nombre devuelva siempre la misma instancia.
    """
    if name in _icon_cache:
        return _icon_cache[name]
    base_dir = os.path.join(os.path.dirname(__file__), "../resources/icons")
    svg_path = os.path.join(base_dir, f"{name}.svg")
    if os.path.isfile(svg_path):
        icon = QIcon(svg_path)
        _icon_cache[name] = icon
        return icon
    png_path = os.path.join(base_dir, f"{name}.png")
    if os.path.isfile(png_path):
        icon = QIcon(png_path)
        _icon_cache[name] = icon
        return icon
    icon = QIcon()
    _icon_cache[name] = icon
    return icon
