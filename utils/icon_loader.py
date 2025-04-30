import os
from PyQt6.QtGui import QIcon

def get_icon(filename: str) -> QIcon:
    icons_path = os.path.join(os.path.dirname(__file__), "../icons")
    icon_path = os.path.join(icons_path, filename)
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    print(f"Advertencia: El ícono '{filename}' no existe en la ruta '{icons_path}'.")
    return QIcon()  # Ícono vacío si no se encuentra el archivo
