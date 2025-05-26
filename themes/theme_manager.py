import os
from PyQt6.QtWidgets import QApplication

# Ruta base para los temas
theme_base_path = os.path.join(os.path.dirname(__file__))

def aplicar_tema(nombre_tema):
    """Aplica el tema especificado a la aplicación."""
    qss_path = os.path.join(theme_base_path, f"{nombre_tema}.qss")
    if not os.path.exists(qss_path):
        raise FileNotFoundError(f"El archivo de tema {qss_path} no existe.")

    with open(qss_path, "r") as file:
        qss = file.read()

    app = QApplication.instance()
    if app is not None and isinstance(app, QApplication):
        app.setStyleSheet(qss)
    else:
        raise RuntimeError("No hay una instancia válida de QApplication para aplicar el tema.")

# Función para guardar la preferencia del tema
def guardar_preferencia_tema(nombre_tema):
    config_path = os.path.join(theme_base_path, "config.json")
    with open(config_path, "w") as file:
        file.write(f'{{"tema": "{nombre_tema}"}}')

# Función para cargar la preferencia del tema
def cargar_preferencia_tema():
    config_path = os.path.join(theme_base_path, "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            import json
            config = json.load(file)
            return config.get("tema", "light")
    return "light"