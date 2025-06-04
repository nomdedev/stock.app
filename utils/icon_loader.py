import os
from PyQt6.QtGui import QIcon

def get_icon(name: str) -> QIcon:
    """
    Busca en resources/icons/<name>.svg o <name>.png.
    Devuelve un QIcon válido o un QIcon() vacío si no se encuentra.
    """
    base_dir = os.path.join(os.path.dirname(__file__), "../resources/icons")
    svg_path = os.path.join(base_dir, f"{name}.svg")
    if os.path.isfile(svg_path):
        return QIcon(svg_path)
    png_path = os.path.join(base_dir, f"{name}.png")
    if os.path.isfile(png_path):
        return QIcon(png_path)
    return QIcon()
