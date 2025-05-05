import json
import os

CONFIG_PATH = "config/theme_config.json"

def aplicar_tema(app, modo="oscuro"):
    """Aplica el tema oscuro o claro a la aplicación."""
    ruta = f"assets/style_{modo}.qss"
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

def guardar_modo_tema(modo):
    """Guarda el modo de tema (oscuro o claro) de manera persistente."""
    os.makedirs("config", exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump({"tema": modo}, f)

def cargar_modo_tema():
    """Carga el modo de tema guardado, por defecto 'oscuro'."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f).get("tema", "oscuro")
    return "oscuro"
